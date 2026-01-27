"""Primitive Model Gateway - Unified LLM orchestration.

The gateway provides:
- Unified interface to all providers
- Automatic provider selection
- Cost tracking and limits
- Response caching
- Fallback on failure

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/gateway/gateway.py
- Version: 2.0.0
- Date: 2026-01-26
- Changes: Modern type hints, simplified caching
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Iterator
from typing import Any

from truth_forge.gateway.providers import (
    BaseProvider,
    ClaudeProvider,
    GeminiProvider,
    OllamaProvider,
)
from truth_forge.gateway.types import (
    CompletionRequest,
    CompletionResponse,
    CostLimitError,
    EmbeddingRequest,
    EmbeddingResponse,
    GatewayError,
    ModelProvider,
    ProviderError,
)


logger = logging.getLogger(__name__)


class ModelGateway:
    """Unified gateway for all LLM operations.

    Features:
    - Provider abstraction (Claude, Gemini, Ollama)
    - Cost tracking and limits
    - Response caching
    - Automatic fallback
    - Metrics collection

    Example:
        gateway = ModelGateway()

        # Simple completion
        response = gateway.complete(CompletionRequest(
            prompt="Explain this code",
            content=code_snippet,
        ))

        # With fallback
        response = gateway.complete_with_fallback(
            request,
            fallback_order=["ollama", "gemini", "claude"],
        )
    """

    def __init__(
        self,
        cost_limit: float | None = None,
        enable_cache: bool = True,
        cache_ttl: int = 3600,
    ) -> None:
        """Initialize the gateway.

        Args:
            cost_limit: Maximum cost in USD before blocking requests.
            enable_cache: Whether to cache responses.
            cache_ttl: Cache time-to-live in seconds.
        """
        self.cost_limit = cost_limit
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl

        # Initialize providers
        self._providers: dict[ModelProvider, BaseProvider] = {
            ModelProvider.CLAUDE: ClaudeProvider(),
            ModelProvider.GEMINI: GeminiProvider(),
            ModelProvider.OLLAMA: OllamaProvider(),
        }

        # Metrics
        self._total_cost = 0.0
        self._request_count = 0
        self._cache: dict[str, tuple[float, CompletionResponse]] = {}

    # =========================================================================
    # CORE OPERATIONS
    # =========================================================================

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Execute a completion request.

        Args:
            request: The completion request.

        Returns:
            CompletionResponse with content and metrics.

        Raises:
            CostLimitError: If cost limit exceeded.
            ProviderError: If provider fails.
        """
        # Check cost limit
        if self.cost_limit and self._total_cost >= self.cost_limit:
            raise CostLimitError(
                f"Cost limit exceeded: ${self._total_cost:.4f} >= ${self.cost_limit:.4f}",
                current_cost=self._total_cost,
                limit=self.cost_limit,
            )

        # Check cache
        if self.enable_cache and request.cache_key:
            cached = self._get_cached(request.cache_key)
            if cached:
                logger.debug("Cache hit for key: %s", request.cache_key)
                return cached

        # Get provider
        config = request.get_config()
        provider = self._providers.get(config.provider)

        if not provider:
            msg = f"Unknown provider: {config.provider}"
            raise GatewayError(msg)

        if not provider.is_available():
            raise ProviderError(
                f"Provider {config.provider.value} is not available",
                provider=config.provider.value,
            )

        # Execute request
        try:
            response = provider.complete(request)
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(
                f"Unexpected error from {config.provider.value}: {e}",
                provider=config.provider.value,
            ) from e

        # Update metrics
        self._total_cost += response.cost
        self._request_count += 1

        # Cache response
        if self.enable_cache and request.cache_key:
            self._set_cached(request.cache_key, response)

        return response

    def complete_with_fallback(
        self,
        request: CompletionRequest,
        fallback_order: list[str] | None = None,
    ) -> CompletionResponse:
        """Complete with automatic fallback to other providers.

        Args:
            request: The completion request.
            fallback_order: Order of providers to try. Defaults to [ollama, gemini, claude].

        Returns:
            CompletionResponse from first successful provider.

        Raises:
            GatewayError: If all providers fail.
        """
        if fallback_order is None:
            # Default: try free first, then cheap, then expensive
            fallback_order = ["ollama", "gemini", "claude"]

        errors = []
        for provider_name in fallback_order:
            try:
                provider_enum = ModelProvider.from_string(provider_name)
                provider = self._providers.get(provider_enum)

                if not provider or not provider.is_available():
                    logger.debug("Provider %s not available, skipping", provider_name)
                    continue

                # Update request to use this provider's default model
                modified_request = CompletionRequest(
                    prompt=request.prompt,
                    content=request.content,
                    model=self._get_default_model_for_provider(provider_enum),
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    as_json=request.as_json,
                    system=request.system,
                    cache_key=request.cache_key,
                    metadata=request.metadata,
                )

                return self.complete(modified_request)

            except Exception as e:
                logger.warning("Provider %s failed: %s", provider_name, e)
                errors.append(f"{provider_name}: {e}")

        msg = f"All providers failed: {'; '.join(errors)}"
        raise GatewayError(msg)

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings.

        Args:
            request: The embedding request.

        Returns:
            EmbeddingResponse with vectors.
        """
        # Currently only Ollama supports embeddings
        provider = self._providers[ModelProvider.OLLAMA]

        if not provider.is_available():
            raise ProviderError(
                "Ollama not available for embeddings",
                provider="ollama",
            )

        return provider.embed(request)

    def stream(self, request: CompletionRequest) -> Iterator[str]:
        """Stream completion response.

        Args:
            request: The completion request.

        Yields:
            Response chunks.
        """
        config = request.get_config()
        provider = self._providers.get(config.provider)

        if not provider:
            msg = f"Unknown provider: {config.provider}"
            raise GatewayError(msg)

        if not provider.is_available():
            raise ProviderError(
                f"Provider {config.provider.value} is not available",
                provider=config.provider.value,
            )

        yield from provider.stream(request)

    # =========================================================================
    # PROVIDER MANAGEMENT
    # =========================================================================

    def get_available_providers(self) -> list[str]:
        """Get list of available providers.

        Returns:
            List of provider names that are currently available.
        """
        return [p.value for p, provider in self._providers.items() if provider.is_available()]

    def get_provider(self, name: str) -> BaseProvider | None:
        """Get a specific provider.

        Args:
            name: Provider name.

        Returns:
            Provider instance or None.
        """
        try:
            provider_enum = ModelProvider.from_string(name)
            return self._providers.get(provider_enum)
        except ValueError:
            return None

    def _get_default_model_for_provider(self, provider: ModelProvider) -> str:
        """Get default model name for a provider."""
        defaults = {
            ModelProvider.CLAUDE: "claude-haiku",
            ModelProvider.GEMINI: "gemini-flash",
            ModelProvider.OLLAMA: "ollama-llama",
        }
        return defaults.get(provider, "claude-haiku")

    # =========================================================================
    # CACHING
    # =========================================================================

    def _get_cached(self, key: str) -> CompletionResponse | None:
        """Get cached response if not expired."""
        if key not in self._cache:
            return None

        timestamp, response = self._cache[key]
        if time.time() - timestamp > self.cache_ttl:
            del self._cache[key]
            return None

        return CompletionResponse(
            content=response.content,
            model=response.model,
            provider=response.provider,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost=0.0,  # Cached responses are free
            latency_ms=0.0,
            cached=True,
            timestamp=response.timestamp,
        )

    def _set_cached(self, key: str, response: CompletionResponse) -> None:
        """Cache a response."""
        self._cache[key] = (time.time(), response)

    def clear_cache(self) -> None:
        """Clear the response cache."""
        self._cache.clear()

    # =========================================================================
    # METRICS
    # =========================================================================

    @property
    def total_cost(self) -> float:
        """Total cost accumulated."""
        return self._total_cost

    @property
    def request_count(self) -> int:
        """Total requests made."""
        return self._request_count

    def get_metrics(self) -> dict[str, Any]:
        """Get gateway metrics.

        Returns:
            Dict with cost, request count, cache stats.
        """
        return {
            "total_cost": self._total_cost,
            "request_count": self._request_count,
            "cache_size": len(self._cache),
            "cost_limit": self.cost_limit,
            "available_providers": self.get_available_providers(),
        }

    def reset_metrics(self) -> None:
        """Reset cost and request counters."""
        self._total_cost = 0.0
        self._request_count = 0


# =============================================================================
# SINGLETON AND CONVENIENCE FUNCTIONS
# =============================================================================

_gateway: ModelGateway | None = None


def get_gateway(cost_limit: float | None = None) -> ModelGateway:
    """Get or create the global gateway instance.

    Args:
        cost_limit: Optional cost limit to set.

    Returns:
        ModelGateway instance.
    """
    global _gateway
    if _gateway is None:
        _gateway = ModelGateway(cost_limit=cost_limit)
    elif cost_limit is not None:
        _gateway.cost_limit = cost_limit
    return _gateway


def prompt(
    task: str,
    content: str | None = None,
    provider: str = "claude",
    model: str | None = None,
    *,
    as_json: bool = False,
    system: str | None = None,
    **kwargs: Any,
) -> str | dict[str, Any]:
    """Convenience function for simple prompts.

    Args:
        task: The prompt/task description.
        content: Content to process.
        provider: Provider to use (claude, gemini, ollama).
        model: Specific model (or uses provider default).
        as_json: Request JSON response.
        system: System prompt.
        **kwargs: Additional request parameters.

    Returns:
        Response content (string or dict if as_json).

    Example:
        result = prompt("Summarize this text", content=my_text)
        entities = prompt("Extract entities as JSON", content=doc, as_json=True)
    """
    gateway = get_gateway()

    # Determine model
    if model is None:
        model_map = {
            "claude": "claude-haiku",
            "gemini": "gemini-flash",
            "ollama": "ollama-llama",
        }
        model = model_map.get(provider, "claude-haiku")

    request = CompletionRequest(
        prompt=task,
        content=content,
        model=model,
        as_json=as_json,
        system=system,
        **kwargs,
    )

    response = gateway.complete(request)

    if as_json:
        try:
            result: dict[str, Any] = json.loads(response.content)
            return result
        except (json.JSONDecodeError, TypeError):
            return response.content

    return response.content


def complete(request: CompletionRequest) -> CompletionResponse:
    """Execute a completion request via the global gateway.

    Args:
        request: The completion request.

    Returns:
        CompletionResponse.
    """
    return get_gateway().complete(request)


def embed(
    text: str | list[str],
    model: str = "ollama-embed",
) -> EmbeddingResponse:
    """Generate embeddings via the global gateway.

    Args:
        text: Text or list of texts to embed.
        model: Embedding model.

    Returns:
        EmbeddingResponse with vectors.
    """
    request = EmbeddingRequest(text=text, model=model)
    return get_gateway().embed(request)


def stream(
    task: str,
    content: str | None = None,
    provider: str = "claude",
    model: str | None = None,
    **kwargs: Any,
) -> Iterator[str]:
    """Stream a completion response.

    Args:
        task: The prompt/task description.
        content: Content to process.
        provider: Provider to use.
        model: Specific model.
        **kwargs: Additional parameters.

    Yields:
        Response chunks.
    """
    gateway = get_gateway()

    if model is None:
        model_map = {
            "claude": "claude-haiku",
            "gemini": "gemini-flash",
            "ollama": "ollama-llama",
        }
        model = model_map.get(provider, "claude-haiku")

    request = CompletionRequest(
        prompt=task,
        content=content,
        model=model,
        **kwargs,
    )

    yield from gateway.stream(request)


__all__ = [
    "ModelGateway",
    "get_gateway",
    "prompt",
    "complete",
    "embed",
    "stream",
]
