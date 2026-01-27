"""Ollama Provider - Local Ollama models.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/gateway/providers/ollama.py
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
    EmbeddingRequest,
    EmbeddingResponse,
    ModelProvider,
    ProviderError,
)


logger = logging.getLogger(__name__)


class OllamaProvider(BaseProvider):
    """Provider for local Ollama models."""

    provider = ModelProvider.OLLAMA

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize Ollama provider.

        Args:
            api_key: Not used for Ollama (local).
            base_url: Ollama server URL. Defaults to OLLAMA_HOST or localhost:11434.
        """
        base_url = base_url or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        super().__init__(api_key=api_key, base_url=base_url)
        self._client: Any = None
        self._available: bool | None = None

    def _get_client(self) -> Any:
        """Get or create Ollama client."""
        if self._client is None:
            try:
                import ollama  # type: ignore[import-not-found]

                self._client = ollama.Client(host=self.base_url)
            except ImportError as e:
                msg = "ollama package not installed. Run: pip install ollama"
                raise ProviderError(msg, provider="ollama") from e
        return self._client

    def is_available(self) -> bool:
        """Check if Ollama server is running."""
        if self._available is not None:
            return self._available

        try:
            client = self._get_client()
            client.list()
            self._available = True
        except Exception:
            self._available = False

        return self._available

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Execute completion with Ollama."""
        if not self.is_available():
            msg = "Ollama server not available"
            raise ProviderError(msg, provider="ollama")

        config = request.get_config()
        client = self._get_client()

        # Build prompt
        prompt = request.prompt
        if request.content:
            prompt = f"{request.prompt}\n\n{request.content}"

        start_time = time.time()

        try:
            response = client.generate(
                model=config.model,
                prompt=prompt,
                options={
                    "temperature": request.temperature or config.temperature,
                    "num_predict": request.max_tokens or config.max_tokens,
                },
            )

            latency_ms = (time.time() - start_time) * 1000

            content = response.get("response", "")

            # Ollama provides token counts
            input_tokens = response.get("prompt_eval_count", 0)
            output_tokens = response.get("eval_count", 0)

            return CompletionResponse(
                content=content,
                model=config.model,
                provider=self.provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=0.0,  # Local = free
                latency_ms=latency_ms,
            )

        except Exception as e:
            msg = f"Ollama error: {e}"
            raise ProviderError(msg, provider="ollama") from e

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings with Ollama."""
        if not self.is_available():
            msg = "Ollama server not available"
            raise ProviderError(msg, provider="ollama")

        client = self._get_client()

        try:
            embeddings: list[list[float]] = []
            total_tokens = 0

            for text in request.texts:
                response = client.embeddings(
                    model=request.model.replace("ollama-", ""),
                    prompt=text,
                )
                embeddings.append(response["embedding"])
                total_tokens += len(text.split())  # Rough estimate

            dimensions = len(embeddings[0]) if embeddings else 0

            return EmbeddingResponse(
                embeddings=embeddings,
                model=request.model,
                dimensions=dimensions,
                total_tokens=total_tokens,
                cost=0.0,
            )

        except Exception as e:
            msg = f"Ollama embedding error: {e}"
            raise ProviderError(msg, provider="ollama") from e

    def stream(self, request: CompletionRequest) -> Iterator[str]:
        """Stream completion from Ollama."""
        if not self.is_available():
            msg = "Ollama server not available"
            raise ProviderError(msg, provider="ollama")

        config = request.get_config()
        client = self._get_client()

        prompt = request.prompt
        if request.content:
            prompt = f"{request.prompt}\n\n{request.content}"

        try:
            stream = client.generate(
                model=config.model,
                prompt=prompt,
                options={
                    "temperature": request.temperature or config.temperature,
                    "num_predict": request.max_tokens or config.max_tokens,
                },
                stream=True,
            )

            for chunk in stream:
                if "response" in chunk:
                    yield chunk["response"]

        except Exception as e:
            msg = f"Ollama streaming error: {e}"
            raise ProviderError(msg, provider="ollama") from e


__all__ = ["OllamaProvider"]
