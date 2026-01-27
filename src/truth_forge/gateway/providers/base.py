"""Base Provider - Abstract interface for LLM providers.

All providers must implement this interface to work with the gateway.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/gateway/providers/base.py
- Version: 2.0.0
- Date: 2026-01-26
- Changes: Modern type hints, removed async methods for simplicity
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any

from truth_forge.gateway.types import (
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ModelConfig,
    ModelProvider,
)


class BaseProvider(ABC):
    """Abstract base class for LLM providers.

    Implementations must provide:
    - complete(): Synchronous completion
    - embed(): Text embedding (optional)
    - stream(): Streaming completion (optional)
    - is_available(): Check provider availability

    Example:
        class MyProvider(BaseProvider):
            provider = ModelProvider.CLAUDE

            def complete(self, request):
                # Implementation
                return CompletionResponse(...)

            def is_available(self):
                return bool(self.api_key)
    """

    provider: ModelProvider
    """The provider enum value."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize provider.

        Args:
            api_key: API key for authentication (optional for local providers).
            base_url: Override base URL for API calls.
        """
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Execute a completion request.

        Args:
            request: The completion request.

        Returns:
            CompletionResponse with content and metadata.

        Raises:
            ProviderError: If the request fails.
        """

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings for text.

        Args:
            request: The embedding request.

        Returns:
            EmbeddingResponse with vectors.

        Raises:
            NotImplementedError: If provider doesn't support embeddings.
            ProviderError: If the request fails.
        """
        msg = f"{self.provider.value} does not support embeddings"
        raise NotImplementedError(msg)

    def stream(self, request: CompletionRequest) -> Iterator[str]:
        """Stream completion response.

        Args:
            request: The completion request.

        Yields:
            Response chunks as they arrive.

        Raises:
            NotImplementedError: If provider doesn't support streaming.
            ProviderError: If the request fails.
        """
        msg = f"{self.provider.value} does not support streaming"
        raise NotImplementedError(msg)

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available and configured.

        Returns:
            True if provider can accept requests.
        """

    def get_default_model(self) -> str:
        """Get the default model for this provider.

        Returns:
            Default model identifier.
        """
        defaults = {
            ModelProvider.CLAUDE: "claude-3-5-haiku-20241022",
            ModelProvider.GEMINI: "gemini-2.0-flash",
            ModelProvider.OLLAMA: "llama3.2",
        }
        return defaults.get(self.provider, "unknown")

    def estimate_cost(
        self,
        config: ModelConfig,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Estimate cost for a request.

        Args:
            config: Model configuration.
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.

        Returns:
            Estimated cost in USD.
        """
        input_cost = (input_tokens / 1000) * config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * config.cost_per_1k_output
        return input_cost + output_cost

    def _build_messages(
        self,
        request: CompletionRequest,
    ) -> list[dict[str, Any]]:
        """Build messages list from request.

        Args:
            request: The completion request.

        Returns:
            List of message dictionaries.
        """
        messages: list[dict[str, Any]] = []

        if request.system:
            messages.append({"role": "system", "content": request.system})

        user_content = request.prompt
        if request.content:
            user_content = f"{request.prompt}\n\n{request.content}"

        messages.append({"role": "user", "content": user_content})

        return messages


__all__ = ["BaseProvider"]
