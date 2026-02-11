"""LLaMA 4 Scout Provider - Local LLaMA 4 Scout with 10M context.

THE FOUNDATION: 10M Context Window
The 10M context window IS the architecture. Not a feature. Not configurable.
Operational capacity is auto-detected from available hardware.

Architecture: 10M (constant)
Operational capacity: Auto-detected from hardware memory

Technical Specifications:
- Model: LLaMA 4 Scout (109B total, 17B active parameters)
- Context: 10,000,000 tokens (THE ARCHITECTURE)
- Architecture: Mixture of Experts (MoE) with 16 experts
- Multimodality: Native text, image, video via early fusion

MOLT LINEAGE:
- Source: New creation for Not-Me infrastructure
- Version: 2.0.0 (10M Foundation)
- Date: 2026-02-01
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import time
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from truth_forge.gateway.providers.base import BaseProvider
from truth_forge.gateway.types import (
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ModelConfig,
    ModelProvider,
    ProviderError,
)


logger = logging.getLogger(__name__)


# =============================================================================
# THE FOUNDATION: 10M CONTEXT
# =============================================================================

# THE ARCHITECTURE. Not configurable. 10M tokens.
THE_CONTEXT: int = 10_000_000

# The model. One model.
THE_MODEL: str = "llama4:scout"


# =============================================================================
# HARDWARE DETECTION (Auto-calculated operational capacity)
# =============================================================================


def _get_system_memory_gb() -> int:
    """Detect total system memory in GB.

    Works on macOS. Returns conservative estimate on failure.
    """
    try:
        # macOS: use sysctl
        result = subprocess.run(
            ["sysctl", "-n", "hw.memsize"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            bytes_mem = int(result.stdout.strip())
            return bytes_mem // (1024**3)
    except Exception:
        pass

    # Fallback: try /proc/meminfo (Linux)
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return kb // (1024**2)
    except Exception:
        pass

    # Conservative fallback
    return 64


def _detect_exa_cluster() -> bool:
    """Detect if EXO distributed cluster is available.

    Checks for EXO_CLUSTER_NODES environment variable or running exo process.
    """
    # Check environment
    if os.environ.get("EXO_CLUSTER_NODES"):
        return True

    # Check for running exo process
    try:
        result = subprocess.run(
            ["pgrep", "-f", "exo"],
            capture_output=True,
            timeout=2,
        )
        return result.returncode == 0
    except Exception:
        return False


@dataclass
class HardwareCapacity:
    """Auto-detected hardware capacity.

    The architecture is 10M. This reports what's operationally usable NOW.
    """

    memory_gb: int
    operational_context: int
    cluster_available: bool
    description: str

    @classmethod
    def detect(cls) -> HardwareCapacity:
        """Auto-detect current hardware capacity.

        No configuration needed. Hardware determines operational limits.
        """
        memory_gb = _get_system_memory_gb()
        cluster = _detect_exa_cluster()

        # Calculate operational context from memory
        # Rule: ~2KB per token for inference, 50% safety margin
        # With EXO cluster: aggregate memory from all nodes
        if cluster:
            # EXO cluster: check for aggregate memory
            cluster_mem = int(os.environ.get("EXO_TOTAL_MEMORY_GB", memory_gb * 4))
            operational = min(THE_CONTEXT, cluster_mem * 250)  # ~4KB/token for distributed
            description = f"EXO Cluster ({cluster_mem}GB) - Full 10M operational"
        elif memory_gb >= 512:
            operational = min(THE_CONTEXT, 1_000_000)  # 1M safe on 512GB
            description = f"High Memory ({memory_gb}GB) - 1M operational"
        elif memory_gb >= 256:
            operational = min(THE_CONTEXT, 500_000)  # 500K safe on 256GB
            description = f"Medium Memory ({memory_gb}GB) - 500K operational"
        elif memory_gb >= 128:
            operational = min(THE_CONTEXT, 131_072)  # 128K safe on 128GB
            description = f"Standard Memory ({memory_gb}GB) - 128K operational"
        else:
            operational = min(THE_CONTEXT, 32_768)  # 32K safe on <128GB
            description = f"Limited Memory ({memory_gb}GB) - 32K operational"

        return cls(
            memory_gb=memory_gb,
            operational_context=operational,
            cluster_available=cluster,
            description=description,
        )


# Cached hardware detection (computed once)
_hardware_capacity: HardwareCapacity | None = None


def get_operational_context() -> int:
    """Get current operational context capacity.

    Auto-detected from hardware. No configuration needed.
    Architecture is always 10M. This returns what's usable NOW.
    """
    global _hardware_capacity
    if _hardware_capacity is None:
        _hardware_capacity = HardwareCapacity.detect()
    return _hardware_capacity.operational_context


def get_hardware_status() -> dict[str, Any]:
    """Get detailed hardware status.

    Returns architecture (10M) and operational capacity (auto-detected).
    """
    global _hardware_capacity
    if _hardware_capacity is None:
        _hardware_capacity = HardwareCapacity.detect()

    return {
        "architecture": THE_CONTEXT,
        "operational": _hardware_capacity.operational_context,
        "memory_gb": _hardware_capacity.memory_gb,
        "cluster_available": _hardware_capacity.cluster_available,
        "description": _hardware_capacity.description,
        "utilization": _hardware_capacity.operational_context / THE_CONTEXT,
    }


# =============================================================================
# SCOUT MODEL (One model. 10M context. Auto-scaled operations.)
# =============================================================================

# One model configuration. Context is THE_CONTEXT. Always.
SCOUT_MODEL = ModelConfig(
    provider=ModelProvider.SCOUT,
    model=THE_MODEL,
    max_tokens=THE_CONTEXT,  # 10M - THE ARCHITECTURE
    temperature=0.7,
    cost_per_1k_input=0.0,  # Local = free
    cost_per_1k_output=0.0,
    supports_json=True,
    supports_streaming=True,
    supports_tools=True,
)


class ScoutProvider(BaseProvider):
    """Provider for LLaMA 4 Scout via Ollama.

    THE FOUNDATION: 10M context architecture.
    Operational capacity: Auto-detected from hardware.

    The provider implements the Seeing Paradigm - describing what IS,
    not predicting what might be.
    """

    provider = ModelProvider.SCOUT

    # Ollama is the default (Scout runs here)
    DEFAULT_OLLAMA = "http://localhost:11434/v1"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize Scout provider.

        Args:
            api_key: Not required for local inference.
            base_url: Ollama server URL. Defaults to localhost:11434.
        """
        # Ollama is the default
        base_url = base_url or os.environ.get("SCOUT_BASE_URL", self.DEFAULT_OLLAMA)
        super().__init__(api_key=api_key, base_url=base_url)
        self._available: bool | None = None
        self._models_cache: list[str] | None = None

        # Log hardware status on init
        status = get_hardware_status()
        logger.info(
            "Scout provider initialized",
            extra={
                "architecture": status["architecture"],
                "operational": status["operational"],
                "description": status["description"],
            },
        )

    def is_available(self) -> bool:
        """Check if Scout server is running and responsive."""
        if self._available is not None:
            return self._available

        try:
            import urllib.request

            url = f"{self.base_url}/models"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    self._models_cache = [m.get("id", "") for m in data.get("data", [])]
                    self._available = True
                    logger.info(
                        "Scout server available",
                        extra={"endpoint": self.base_url, "models": self._models_cache},
                    )
                else:
                    self._available = False
        except Exception as e:
            logger.warning("Scout server not available", extra={"error": str(e)})
            self._available = False

        return self._available

    def get_available_models(self) -> list[str]:
        """Get list of available models from the server."""
        if self._models_cache is None:
            self.is_available()
        return self._models_cache or []

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Execute completion with LLaMA 4 Scout.

        Implements the Seeing Paradigm: describe what IS, don't predict.
        Architecture: 10M context. Operations: auto-scaled to hardware.
        """
        if not self.is_available():
            msg = f"Scout server not available at {self.base_url}"
            raise ProviderError(msg, provider="scout")

        # One model. THE_MODEL.
        model = THE_MODEL

        # Build messages in OpenAI format
        messages = self._build_messages(request)

        # Operational context (auto-detected from hardware)
        operational = get_operational_context()

        start_time = time.time()

        try:
            import urllib.request

            payload = {
                "model": model,
                "messages": messages,
                "temperature": request.temperature or SCOUT_MODEL.temperature,
                "max_tokens": min(request.max_tokens or operational, operational),
                "stream": False,
            }

            # Add response format if JSON requested
            if request.as_json:
                payload["response_format"] = {"type": "json_object"}

            # Add tools if provided
            if request.tools:
                payload["tools"] = request.tools

            url = f"{self.base_url}/chat/completions"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}),
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=300) as response:
                data = json.loads(response.read().decode())

            latency_ms = (time.time() - start_time) * 1000

            # Extract response
            choice = data.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")
            tool_calls = choice.get("message", {}).get("tool_calls")

            # Token usage
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            return CompletionResponse(
                content=content,
                model=model,
                provider=self.provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=0.0,  # Local = free
                latency_ms=latency_ms,
                tool_calls=tool_calls,
                raw_response=data,
            )

        except Exception as e:
            msg = f"Scout completion error: {e}"
            raise ProviderError(msg, provider="scout") from e

    def stream(self, request: CompletionRequest) -> Iterator[str]:
        """Stream completion from LLaMA 4 Scout.

        Yields chunks as they arrive for real-time display.
        Architecture: 10M context. Operations: auto-scaled to hardware.
        """
        if not self.is_available():
            msg = f"Scout server not available at {self.base_url}"
            raise ProviderError(msg, provider="scout")

        # One model. THE_MODEL.
        model = THE_MODEL
        messages = self._build_messages(request)

        # Operational context (auto-detected from hardware)
        operational = get_operational_context()

        try:
            import urllib.request

            payload = {
                "model": model,
                "messages": messages,
                "temperature": request.temperature or SCOUT_MODEL.temperature,
                "max_tokens": min(request.max_tokens or operational, operational),
                "stream": True,
            }

            url = f"{self.base_url}/chat/completions"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}),
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=300) as response:
                for line in response:
                    line = line.decode("utf-8").strip()
                    if line.startswith("data: "):
                        line = line[6:]
                        if line == "[DONE]":
                            break
                        try:
                            chunk = json.loads(line)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            msg = f"Scout streaming error: {e}"
            raise ProviderError(msg, provider="scout") from e

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings with local embedding model.

        Note: Scout primarily uses generation. For embeddings,
        consider using a dedicated embedding model via Ollama.
        """
        if not self.is_available():
            msg = f"Scout server not available at {self.base_url}"
            raise ProviderError(msg, provider="scout")

        try:
            import urllib.request

            embeddings: list[list[float]] = []
            total_tokens = 0

            for text in request.texts:
                payload = {
                    "model": request.model,
                    "input": text,
                }

                url = f"{self.base_url}/embeddings"
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )

                with urllib.request.urlopen(req, timeout=60) as response:
                    data = json.loads(response.read().decode())
                    embedding = data.get("data", [{}])[0].get("embedding", [])
                    embeddings.append(embedding)
                    total_tokens += data.get("usage", {}).get("total_tokens", len(text.split()))

            dimensions = len(embeddings[0]) if embeddings else 0

            return EmbeddingResponse(
                embeddings=embeddings,
                model=request.model,
                dimensions=dimensions,
                total_tokens=total_tokens,
                cost=0.0,
            )

        except Exception as e:
            msg = f"Scout embedding error: {e}"
            raise ProviderError(msg, provider="scout") from e

    def get_default_model(self) -> str:
        """Get the Scout model. One model."""
        return THE_MODEL

    def health_check(self) -> dict[str, Any]:
        """Detailed health check of Scout server.

        Returns:
            Health status with architecture (10M) and operational capacity.
        """
        hw = get_hardware_status()

        status = {
            "available": self.is_available(),
            "endpoint": self.base_url,
            "models": self.get_available_models(),
            "model": THE_MODEL,
            # THE FOUNDATION
            "architecture": {
                "context": THE_CONTEXT,
                "description": "10M context - THE FOUNDATION",
            },
            # Auto-detected operational capacity
            "operational": {
                "context": hw["operational"],
                "memory_gb": hw["memory_gb"],
                "cluster_available": hw["cluster_available"],
                "description": hw["description"],
                "utilization": hw["utilization"],
            },
        }

        if self._available:
            try:
                import urllib.request

                # Try to get server health
                url = f"{self.base_url.replace('/v1', '')}/health"
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=5) as response:
                    health_data = json.loads(response.read().decode())
                    status["server_health"] = health_data
            except Exception:
                pass  # Health endpoint may not be available

        return status


__all__ = [
    # THE FOUNDATION
    "THE_CONTEXT",
    "THE_MODEL",
    # Hardware auto-detection
    "HardwareCapacity",
    "get_operational_context",
    "get_hardware_status",
    # Model config
    "SCOUT_MODEL",
    # Provider
    "ScoutProvider",
]
