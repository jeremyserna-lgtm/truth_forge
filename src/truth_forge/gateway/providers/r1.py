"""R1 Provider - DeepSeek R1 4bit (sovereign synthesis)."""

from __future__ import annotations

import json
import os
import time

from truth_forge.gateway.providers.base import BaseProvider
from truth_forge.gateway.types import (
    CompletionRequest,
    CompletionResponse,
    ModelProvider,
    ProviderError,
)


class R1Provider(BaseProvider):
    provider = ModelProvider.R1
    DEFAULT_ENDPOINT = "http://localhost:8767/v1"

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        base_url = base_url or os.environ.get("R1_BASE_URL", self.DEFAULT_ENDPOINT)
        super().__init__(api_key=api_key, base_url=base_url)
        self._available: bool | None = None

    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            import urllib.request

            url = f"{self.base_url}/models"
            with urllib.request.urlopen(url, timeout=5) as resp:
                self._available = resp.status == 200
        except Exception:
            self._available = False
        return self._available

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        if not self.is_available():
            raise ProviderError(f"R1 not available at {self.base_url}", provider="r1")

        from truth_forge.gateway.types import MODELS

        model = MODELS["r1-genesis"].model
        messages = self._build_messages(request)
        start = time.time()

        try:
            import urllib.request

            payload = {
                "model": model,
                "messages": messages,
                "temperature": request.temperature or 0.6,
                "max_tokens": request.max_tokens or MODELS["r1-genesis"].max_tokens,
                "stream": False,
            }

            url = f"{self.base_url}/chat/completions"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=300) as response:
                data = json.loads(response.read().decode())

            latency_ms = (time.time() - start) * 1000
            choice = data.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")
            usage = data.get("usage", {})
            return CompletionResponse(
                content=content,
                model=model,
                provider=self.provider,
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                cost=0.0,
                latency_ms=latency_ms,
                tool_calls=choice.get("message", {}).get("tool_calls"),
                raw_response=data,
            )
        except Exception as e:
            raise ProviderError(f"R1 completion error: {e}", provider="r1") from e
