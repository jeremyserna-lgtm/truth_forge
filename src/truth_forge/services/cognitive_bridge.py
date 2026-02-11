"""Cognitive Bridge - dynamic model router (Scout/Maverick/R1).

Lightweight implementation aligned with Genesis plan. Uses a JSON config to
select model based on task type and context size, with a fallback chain.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from truth_forge.gateway.providers.maverick import MaverickProvider
from truth_forge.gateway.providers.r1 import R1Provider
from truth_forge.gateway.providers.scout import ScoutProvider
from truth_forge.gateway.types import CompletionRequest, CompletionResponse
from truth_forge.services.exo_inference import ExoInferenceTool
from truth_forge.services.model_readiness import check_readiness


logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(os.environ.get("COGNITIVE_BRIDGE_CONFIG", "")) or (
    Path(__file__).resolve().parents[2] / "config" / "base" / "cognitive_bridge_config.json"
)


@dataclass
class BridgeTarget:
    name: str
    provider: str
    endpoint: str
    max_context: int


class CognitiveBridge:
    """Dynamic router for model selection."""

    def __init__(self, config_path: Path | str = DEFAULT_CONFIG_PATH):
        self.config_path = Path(config_path)
        self.config = self._load_config(self.config_path)
        self.scout = ScoutProvider(base_url=self.config["models"]["scout"]["endpoint"])
        self.maverick = MaverickProvider(base_url=self.config["models"]["maverick"]["endpoint"])
        self.r1 = R1Provider(base_url=self.config["models"]["r1"]["endpoint"])
        self.exo = ExoInferenceTool()
        self._warmup_async()

    @staticmethod
    def _load_config(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _classify_task(self, prompt: str, task_type: str | None = None) -> str:
        if task_type and task_type != "auto":
            return task_type
        lower = prompt.lower()
        if "design" in lower or "architecture" in lower:
            return "architecture_design"
        if "research" in lower or "literature" in lower:
            return "research_synthesis"
        if "code review" in lower or "refactor" in lower:
            return "code_review"
        if "plan" in lower or "strategy" in lower:
            return "complex_reasoning"
        return "simple_chat"

    def route(
        self,
        prompt: str,
        task_type: str = "auto",
        context_tokens: int = 0,
    ) -> BridgeTarget:
        routing = self.config["routing"]
        thresholds = self.config.get("thresholds", {})
        classified = self._classify_task(prompt, task_type)
        model_key = routing.get(classified, routing["fallback_chain"][0])

        # Context-aware override: if very large context, force Scout
        large_ctx = thresholds.get("large_context_tokens", 80_000)
        if context_tokens >= large_ctx:
            model_key = "scout"

        # Availability-aware fallback
        model_key = self._first_available(model_key, routing["fallback_chain"])

        model_cfg = self.config["models"][model_key]
        return BridgeTarget(
            name=model_key,
            provider=model_cfg["provider"],
            endpoint=model_cfg["endpoint"],
            max_context=model_cfg.get("max_context", 0),
        )

    def _first_available(self, preferred: str, fallback_chain: list[str]) -> str:
        order = [preferred] + [m for m in fallback_chain if m != preferred]
        readiness = check_readiness()
        for key in order:
            if key == "maverick":
                ready = readiness.get("maverick")
                if ready is None or ready.ready:  # if readiness unknown, allow
                    if self.maverick.is_available():
                        return key
            if key == "r1":
                ready = readiness.get("r1")
                if ready and ready.ready and self.r1.is_available():
                    return key
            if key == "scout" and self.scout.is_available():
                return key
        # none available: default to preferred (will raise on use)
        return preferred

    # Thin wrapper to perform completion now (Scout only; others pending)
    def complete(self, request: CompletionRequest, task_type: str = "auto") -> CompletionResponse:
        target = self.route(
            request.prompt, task_type=task_type, context_tokens=request.max_tokens or 0
        )
        provider = target.name
        if provider == "maverick":
            # Use EXO if distributed threshold hit
            large_context_threshold = self.config.get("thresholds", {}).get(
                "large_context_tokens", 80_000
            )
            should_distribute = (request.max_tokens or 0) >= large_context_threshold
            if should_distribute and self.exo.can_distribute("maverick", request.max_tokens or 0):
                resp = self.exo.distributed_inference("maverick", self._build_messages(request))
                return CompletionResponse(
                    content=resp["content"],
                    model="maverick-distributed",
                    provider=self.maverick.provider,
                    input_tokens=0,
                    output_tokens=0,
                    cost=0.0,
                    latency_ms=resp.get("latency_ms", 0),
                    tool_calls=None,
                    raw_response=resp,
                )
            return self.maverick.complete(request)
        if provider == "r1":
            return self.r1.complete(request)
        return self.scout.complete(request)

    @staticmethod
    def _build_messages(request: CompletionRequest) -> list[dict[str, str]]:
        """Convert gateway request into chat message payload for EXO/OpenAI APIs."""
        messages: list[dict[str, str]] = []
        if request.system:
            messages.append({"role": "system", "content": request.system})
        user_content = request.content or request.prompt
        messages.append({"role": "user", "content": user_content})
        return messages

    def _warmup_async(self) -> None:
        """Fire-and-forget warmup calls to reduce cold latency."""

        def _run() -> None:
            try:
                if self.scout.is_available():
                    self.scout.complete(
                        CompletionRequest(prompt="ping", max_tokens=4, model="scout-genesis")
                    )
                if self.maverick.is_available():
                    self.maverick.complete(
                        CompletionRequest(prompt="ping", max_tokens=4, model="maverick-genesis")
                    )
                # R1 warmup only if ready
                readiness = check_readiness()
                if readiness.get("r1") and readiness["r1"].ready and self.r1.is_available():
                    self.r1.complete(
                        CompletionRequest(prompt="ping", max_tokens=4, model="r1-genesis")
                    )
            except Exception:
                return

        threading.Thread(target=_run, daemon=True).start()
