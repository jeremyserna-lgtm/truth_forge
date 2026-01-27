"""Gemini Provider - Google Gemini models.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/gateway/providers/gemini.py
- Version: 2.0.0
- Date: 2026-01-26
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Iterator
from typing import Any

from truth_forge.gateway.providers.base import BaseProvider
from truth_forge.gateway.types import (
    CompletionRequest,
    CompletionResponse,
    ModelProvider,
    ProviderError,
)


logger = logging.getLogger(__name__)


class GeminiProvider(BaseProvider):
    """Provider for Google Gemini models."""

    provider = ModelProvider.GEMINI

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize Gemini provider.

        Args:
            api_key: Google API key. Defaults to GEMINI_API_KEY env var.
            base_url: Override API base URL.
        """
        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        super().__init__(api_key=api_key, base_url=base_url)
        self._client: Any = None

    def _get_client(self) -> Any:
        """Get or create Gemini client."""
        if self._client is None:
            try:
                from google import genai

                self._client = genai.Client(api_key=self.api_key)
            except ImportError as e:
                msg = "google-genai package not installed. Run: pip install google-genai"
                raise ProviderError(msg, provider="gemini") from e
        return self._client

    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return bool(self.api_key)

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Execute completion with Gemini."""
        if not self.is_available():
            msg = "Gemini API key not configured"
            raise ProviderError(msg, provider="gemini")

        config = request.get_config()
        client = self._get_client()

        # Build prompt
        prompt = request.prompt
        if request.content:
            prompt = f"{request.prompt}\n\n{request.content}"

        start_time = time.time()

        try:
            from google.genai import types

            response = client.models.generate_content(
                model=config.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=request.max_tokens or config.max_tokens,
                    temperature=request.temperature or config.temperature,
                ),
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract content
            content = response.text if response.text else ""

            # Estimate tokens (Gemini doesn't always return exact counts)
            input_tokens = len(prompt.split()) * 2  # Rough estimate
            output_tokens = len(content.split()) * 2

            cost = self.estimate_cost(config, input_tokens, output_tokens)

            return CompletionResponse(
                content=content,
                model=config.model,
                provider=self.provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                latency_ms=latency_ms,
            )

        except Exception as e:
            msg = f"Gemini API error: {e}"
            raise ProviderError(msg, provider="gemini") from e

    def stream(self, request: CompletionRequest) -> Iterator[str]:
        """Stream completion from Gemini."""
        if not self.is_available():
            msg = "Gemini API key not configured"
            raise ProviderError(msg, provider="gemini")

        config = request.get_config()
        client = self._get_client()

        prompt = request.prompt
        if request.content:
            prompt = f"{request.prompt}\n\n{request.content}"

        try:
            from google.genai import types

            response = client.models.generate_content_stream(
                model=config.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=request.max_tokens or config.max_tokens,
                    temperature=request.temperature or config.temperature,
                ),
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            msg = f"Gemini streaming error: {e}"
            raise ProviderError(msg, provider="gemini") from e


__all__ = ["GeminiProvider"]
