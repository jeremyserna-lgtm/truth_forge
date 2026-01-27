"""Claude Provider - Anthropic Claude models.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/gateway/providers/claude.py
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


class ClaudeProvider(BaseProvider):
    """Provider for Anthropic Claude models."""

    provider = ModelProvider.CLAUDE

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize Claude provider.

        Args:
            api_key: Anthropic API key. Defaults to ANTHROPIC_API_KEY env var.
            base_url: Override API base URL.
        """
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        super().__init__(api_key=api_key, base_url=base_url)
        self._client: Any = None

    def _get_client(self) -> Any:
        """Get or create Anthropic client."""
        if self._client is None:
            try:
                import anthropic

                self._client = anthropic.Anthropic(
                    api_key=self.api_key,
                    base_url=self.base_url,
                )
            except ImportError as e:
                msg = "anthropic package not installed. Run: pip install anthropic"
                raise ProviderError(msg, provider="claude") from e
        return self._client

    def is_available(self) -> bool:
        """Check if Claude is available."""
        return bool(self.api_key)

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Execute completion with Claude."""
        if not self.is_available():
            msg = "Claude API key not configured"
            raise ProviderError(msg, provider="claude")

        config = request.get_config()
        client = self._get_client()

        # Build request
        messages = self._build_messages(request)

        start_time = time.time()

        try:
            response = client.messages.create(
                model=config.model,
                max_tokens=request.max_tokens or config.max_tokens,
                messages=messages,
                system=request.system or "",
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract content
            content = ""
            if response.content:
                for block in response.content:
                    if hasattr(block, "text"):
                        content += block.text

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
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
            msg = f"Claude API error: {e}"
            raise ProviderError(msg, provider="claude") from e

    def stream(self, request: CompletionRequest) -> Iterator[str]:
        """Stream completion from Claude."""
        if not self.is_available():
            msg = "Claude API key not configured"
            raise ProviderError(msg, provider="claude")

        config = request.get_config()
        client = self._get_client()
        messages = self._build_messages(request)

        try:
            with client.messages.stream(
                model=config.model,
                max_tokens=request.max_tokens or config.max_tokens,
                messages=messages,
                system=request.system or "",
            ) as stream:
                yield from stream.text_stream

        except Exception as e:
            msg = f"Claude streaming error: {e}"
            raise ProviderError(msg, provider="claude") from e


__all__ = ["ClaudeProvider"]
