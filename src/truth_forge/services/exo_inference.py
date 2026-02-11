"""EXO distributed inference - route large model inference across cluster.

Distributes inference of large models (Maverick 128E, R1 671B) across
multiple Genesis cluster nodes using EXO's sharded inference protocol.

Architecture:
    ExoInferenceTool
        |
        ├── can_distribute() -> should this request use EXO?
        ├── distributed_inference() -> route through EXO cluster
        ├── _start_exo_workers() -> spawn EXO on soldiers
        ├── _collect_results() -> aggregate distributed inference
        |
        v
    EXO cluster (King coordinates, Soldiers execute shards)
"""

from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass
from typing import Any

import requests


logger = logging.getLogger(__name__)

# EXO default config
EXO_DEFAULT_PORT = 8000
LARGE_CONTEXT_THRESHOLD = 80_000  # tokens


@dataclass
class ExoWorkerState:
    """Track an EXO worker on a soldier node."""

    node: str
    pid: int | None = None
    port: int = EXO_DEFAULT_PORT
    active: bool = False
    last_heartbeat: float = 0.0


class ExoInferenceTool:
    """Distributed inference via EXO across Genesis cluster.

    When a model is too large for a single node or context exceeds
    single-node capacity, EXO shards the inference across soldiers.
    Falls back gracefully to single-node if EXO unavailable.
    """

    def __init__(
        self,
        exo_endpoint: str = "http://localhost:8000",
        soldier_nodes: list[str] | None = None,
        ssh_user: str = "genesis",
    ) -> None:
        self.exo_endpoint = exo_endpoint
        self.soldier_nodes = soldier_nodes or ["soldier1", "soldier2", "soldier3"]
        self.ssh_user = ssh_user
        self._workers: dict[str, ExoWorkerState] = {}

    def can_distribute(self, model: str, prompt_tokens: int) -> bool:
        """Decide if this request should use distributed inference.

        Distribution is warranted when:
        - Model is Maverick (128 experts) or R1 (671B params)
        - Context exceeds single-node threshold (80k tokens)
        - At least one soldier is available

        Args:
            model: Model identifier string.
            prompt_tokens: Number of tokens in the prompt.

        Returns:
            True if distributed inference is recommended.
        """
        # Large models always benefit from distribution
        is_large_model = any(name in model.lower() for name in ["maverick", "r1", "deepseek"])

        # Large context benefits from distribution
        is_large_context = prompt_tokens > LARGE_CONTEXT_THRESHOLD

        if not (is_large_model or is_large_context):
            return False

        # Check if EXO endpoint is reachable
        return self._is_exo_available()

    def distributed_inference(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Route inference through EXO distributed cluster.

        Args:
            model: Model identifier.
            messages: Chat messages in OpenAI format.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.

        Returns:
            Dict with content, latency, and distribution metadata.
        """
        start = time.time()

        if not self._is_exo_available():
            logger.warning("EXO not available, returning placeholder")
            return {
                "model": model,
                "content": "[EXO unavailable - use single-node inference]",
                "latency_ms": 0,
                "distributed": True,
                "fallback": True,
            }

        try:
            # EXO exposes an OpenAI-compatible API
            response = requests.post(
                f"{self.exo_endpoint}/v1/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=300,  # 5 min timeout for large inference
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            latency_ms = (time.time() - start) * 1000

            logger.info(
                "EXO distributed inference complete",
                extra={
                    "model": model,
                    "latency_ms": round(latency_ms, 1),
                    "tokens": data.get("usage", {}).get("total_tokens", 0),
                },
            )

            return {
                "model": model,
                "content": content,
                "latency_ms": round(latency_ms, 1),
                "distributed": True,
                "usage": data.get("usage", {}),
            }

        except requests.RequestException as e:
            latency_ms = (time.time() - start) * 1000
            logger.error(
                "EXO inference failed",
                extra={"error": str(e), "model": model},
            )
            return {
                "model": model,
                "content": f"[EXO error: {e}]",
                "latency_ms": round(latency_ms, 1),
                "distributed": True,
                "fallback": True,
                "error": str(e),
            }

    def _is_exo_available(self) -> bool:
        """Check if EXO endpoint responds."""
        try:
            resp = requests.get(
                f"{self.exo_endpoint}/v1/models",
                timeout=2.0,
            )
            return resp.status_code == 200
        except Exception:
            return False

    def _start_exo_workers(self) -> int:
        """Spawn EXO workers on soldier nodes.

        Returns:
            Number of workers successfully started.
        """
        started = 0
        for node in self.soldier_nodes:
            try:
                # Start EXO in background on soldier via SSH
                result = subprocess.run(
                    [
                        "ssh",
                        "-o",
                        "BatchMode=yes",
                        "-o",
                        "ConnectTimeout=5",
                        f"{self.ssh_user}@{node}",
                        f"nohup exo --port {EXO_DEFAULT_PORT} > /tmp/exo.log 2>&1 & echo $!",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and result.stdout.strip():
                    pid = int(result.stdout.strip())
                    self._workers[node] = ExoWorkerState(
                        node=node,
                        pid=pid,
                        active=True,
                        last_heartbeat=time.time(),
                    )
                    started += 1
                    logger.info(
                        "EXO worker started",
                        extra={"node": node, "pid": pid},
                    )
            except Exception as e:
                logger.error(
                    "Failed to start EXO worker",
                    extra={"node": node, "error": str(e)},
                )
        return started

    def _collect_results(self) -> dict[str, Any]:
        """Get status of all EXO workers."""
        return {
            node: {
                "active": w.active,
                "pid": w.pid,
                "last_heartbeat": w.last_heartbeat,
            }
            for node, w in self._workers.items()
        }

    def get_status(self) -> dict[str, Any]:
        """Return EXO status summary."""
        return {
            "endpoint": self.exo_endpoint,
            "available": self._is_exo_available(),
            "workers": self._collect_results(),
            "soldier_count": len(self.soldier_nodes),
        }
