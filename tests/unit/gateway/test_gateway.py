"""Tests for gateway module.

Tests the unified LLM orchestration.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.gateway.gateway import ModelGateway, get_gateway
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


class TestModelGateway:
    """Tests for ModelGateway class."""

    def test_init_default_values(self) -> None:
        """Test default gateway initialization."""
        gateway = ModelGateway()

        assert gateway.cost_limit is None
        assert gateway.enable_cache is True
        assert gateway.cache_ttl == 3600
        assert gateway.total_cost == 0.0
        assert gateway.request_count == 0

    def test_init_custom_values(self) -> None:
        """Test custom gateway initialization."""
        gateway = ModelGateway(
            cost_limit=10.0,
            enable_cache=False,
            cache_ttl=1800,
        )

        assert gateway.cost_limit == 10.0
        assert gateway.enable_cache is False
        assert gateway.cache_ttl == 1800

    def test_get_available_providers(self) -> None:
        """Test getting available providers."""
        gateway = ModelGateway()
        providers = gateway.get_available_providers()

        # Result depends on which providers are configured
        assert isinstance(providers, list)

    def test_get_provider(self) -> None:
        """Test getting a specific provider."""
        gateway = ModelGateway()
        provider = gateway.get_provider("claude")

        # Provider may or may not be available
        # but the method should not raise

    def test_get_provider_invalid(self) -> None:
        """Test getting invalid provider returns None."""
        gateway = ModelGateway()
        provider = gateway.get_provider("invalid")

        assert provider is None

    def test_get_metrics(self) -> None:
        """Test getting gateway metrics."""
        gateway = ModelGateway(cost_limit=10.0)
        metrics = gateway.get_metrics()

        assert "total_cost" in metrics
        assert "request_count" in metrics
        assert "cache_size" in metrics
        assert "cost_limit" in metrics
        assert "available_providers" in metrics
        assert metrics["cost_limit"] == 10.0

    def test_reset_metrics(self) -> None:
        """Test resetting metrics."""
        gateway = ModelGateway()
        gateway._total_cost = 5.0
        gateway._request_count = 10

        gateway.reset_metrics()

        assert gateway.total_cost == 0.0
        assert gateway.request_count == 0

    def test_clear_cache(self) -> None:
        """Test clearing the cache."""
        gateway = ModelGateway()
        gateway._cache["key"] = (0.0, MagicMock())

        gateway.clear_cache()

        assert len(gateway._cache) == 0

    def test_cost_limit_exceeded(self) -> None:
        """Test that cost limit raises error."""
        gateway = ModelGateway(cost_limit=1.0)

        # Set total cost to exceed limit
        gateway._total_cost = 1.0

        request = CompletionRequest(prompt="Test")

        with pytest.raises(CostLimitError) as exc_info:
            gateway.complete(request)

        assert exc_info.value.limit == 1.0

    def test_cache_hit(self) -> None:
        """Test cache hit returns cached response."""
        gateway = ModelGateway(enable_cache=True)

        # Create a cached response
        cached_response = CompletionResponse(
            content="Cached content",
            model="test-model",
            provider=ModelProvider.CLAUDE,
        )

        # Manually add to cache (simulating a previous request)
        import time

        gateway._cache["test-key"] = (time.time(), cached_response)

        # Create request with same cache key
        request = CompletionRequest(prompt="Test", cache_key="test-key")

        # Get cached response
        result = gateway._get_cached("test-key")

        assert result is not None
        assert result.content == "Cached content"
        assert result.cached is True
        assert result.cost == 0.0  # Cached responses are free

    def test_cache_expired(self) -> None:
        """Test expired cache returns None."""
        gateway = ModelGateway(enable_cache=True, cache_ttl=1)

        # Create an expired cached response
        cached_response = CompletionResponse(
            content="Old content",
            model="test-model",
            provider=ModelProvider.CLAUDE,
        )

        import time

        # Set timestamp to be expired (way in the past)
        gateway._cache["test-key"] = (time.time() - 100, cached_response)

        # Should return None for expired cache
        result = gateway._get_cached("test-key")

        assert result is None

    def test_provider_not_available_raises(self) -> None:
        """Test that unavailable provider raises error."""
        gateway = ModelGateway()

        # Mock all providers as unavailable
        for provider in gateway._providers.values():
            provider.is_available = MagicMock(return_value=False)

        request = CompletionRequest(prompt="Test", model="claude-haiku")

        with pytest.raises(ProviderError) as exc_info:
            gateway.complete(request)

        assert "not available" in str(exc_info.value)

    def test_complete_updates_metrics(self) -> None:
        """Test that complete updates metrics."""
        gateway = ModelGateway()

        # Mock provider
        mock_provider = MagicMock()
        mock_provider.is_available.return_value = True
        mock_provider.complete.return_value = CompletionResponse(
            content="Response",
            model="claude-haiku",
            provider=ModelProvider.CLAUDE,
            cost=0.001,
        )

        gateway._providers[ModelProvider.CLAUDE] = mock_provider

        request = CompletionRequest(prompt="Test", model="claude-haiku")
        response = gateway.complete(request)

        assert gateway.total_cost == 0.001
        assert gateway.request_count == 1

    def test_complete_with_fallback_tries_providers(self) -> None:
        """Test fallback tries multiple providers."""
        gateway = ModelGateway()

        # Mock first provider as unavailable
        mock_ollama = MagicMock()
        mock_ollama.is_available.return_value = False

        # Mock second provider as available
        mock_gemini = MagicMock()
        mock_gemini.is_available.return_value = True
        mock_gemini.complete.return_value = CompletionResponse(
            content="Gemini response",
            model="gemini-flash",
            provider=ModelProvider.GEMINI,
        )

        gateway._providers[ModelProvider.OLLAMA] = mock_ollama
        gateway._providers[ModelProvider.GEMINI] = mock_gemini

        request = CompletionRequest(prompt="Test")
        response = gateway.complete_with_fallback(
            request,
            fallback_order=["ollama", "gemini"],
        )

        assert response.content == "Gemini response"

    def test_complete_with_fallback_all_fail(self) -> None:
        """Test fallback raises when all providers fail."""
        gateway = ModelGateway()

        # Mock all providers as unavailable
        for provider in gateway._providers.values():
            provider.is_available = MagicMock(return_value=False)

        request = CompletionRequest(prompt="Test")

        with pytest.raises(GatewayError) as exc_info:
            gateway.complete_with_fallback(request)

        assert "All providers failed" in str(exc_info.value)


class TestGetGateway:
    """Tests for get_gateway function."""

    def test_get_gateway_creates_singleton(self) -> None:
        """Test get_gateway creates singleton."""
        # Reset global gateway
        import truth_forge.gateway.gateway as gateway_module

        gateway_module._gateway = None

        gw1 = get_gateway()
        gw2 = get_gateway()

        assert gw1 is gw2

    def test_get_gateway_with_cost_limit(self) -> None:
        """Test get_gateway with cost limit."""
        import truth_forge.gateway.gateway as gateway_module

        gateway_module._gateway = None

        gw = get_gateway(cost_limit=5.0)

        assert gw.cost_limit == 5.0

    def test_get_gateway_updates_cost_limit(self) -> None:
        """Test get_gateway updates cost limit on existing."""
        import truth_forge.gateway.gateway as gateway_module

        gateway_module._gateway = None

        gw1 = get_gateway(cost_limit=5.0)
        gw2 = get_gateway(cost_limit=10.0)

        assert gw1 is gw2
        assert gw2.cost_limit == 10.0


class TestModelGatewayComplete:
    """Additional tests for complete method coverage."""

    def test_complete_unknown_provider_raises(self) -> None:
        """Test complete raises for unknown provider."""
        gateway = ModelGateway()

        # Create a mock request that returns unknown provider
        request = MagicMock(spec=CompletionRequest)
        mock_config = MagicMock()
        mock_config.provider = "unknown"
        request.get_config.return_value = mock_config
        request.cache_key = None

        with pytest.raises(GatewayError) as exc_info:
            gateway.complete(request)

        assert "Unknown provider" in str(exc_info.value)

    def test_complete_caches_response(self) -> None:
        """Test that complete caches response when cache_key provided."""
        gateway = ModelGateway(enable_cache=True)

        # Mock provider
        mock_provider = MagicMock()
        mock_provider.is_available.return_value = True
        mock_provider.complete.return_value = CompletionResponse(
            content="Test response",
            model="claude-haiku",
            provider=ModelProvider.CLAUDE,
            cost=0.001,
        )

        gateway._providers[ModelProvider.CLAUDE] = mock_provider

        request = CompletionRequest(prompt="Test", model="claude-haiku", cache_key="test-cache-key")
        response = gateway.complete(request)

        # Should be cached now
        assert "test-cache-key" in gateway._cache
        assert gateway._cache["test-cache-key"][1].content == "Test response"

    def test_complete_provider_error_reraises(self) -> None:
        """Test that provider errors are reraised."""
        gateway = ModelGateway()

        # Mock provider that raises
        mock_provider = MagicMock()
        mock_provider.is_available.return_value = True
        mock_provider.complete.side_effect = ProviderError("API error", provider="claude")

        gateway._providers[ModelProvider.CLAUDE] = mock_provider

        request = CompletionRequest(prompt="Test", model="claude-haiku")

        with pytest.raises(ProviderError) as exc_info:
            gateway.complete(request)

        assert "API error" in str(exc_info.value)

    def test_complete_generic_error_wrapped(self) -> None:
        """Test that generic errors are wrapped in GatewayError."""
        gateway = ModelGateway()

        # Mock provider that raises generic exception
        mock_provider = MagicMock()
        mock_provider.is_available.return_value = True
        mock_provider.complete.side_effect = RuntimeError("Unexpected error")

        gateway._providers[ModelProvider.CLAUDE] = mock_provider

        request = CompletionRequest(prompt="Test", model="claude-haiku")

        with pytest.raises(GatewayError) as exc_info:
            gateway.complete(request)

        assert "Unexpected error" in str(exc_info.value)


class TestModelGatewayStream:
    """Tests for streaming functionality."""

    def test_stream_provider_not_available(self) -> None:
        """Test stream raises when provider not available."""
        gateway = ModelGateway()

        for provider in gateway._providers.values():
            provider.is_available = MagicMock(return_value=False)

        request = CompletionRequest(prompt="Test", model="claude-haiku")

        with pytest.raises(ProviderError):
            list(gateway.stream(request))

    def test_stream_unknown_provider_raises(self) -> None:
        """Test stream raises for unknown provider."""
        gateway = ModelGateway()

        # Create mock request with unknown provider
        request = MagicMock(spec=CompletionRequest)
        mock_config = MagicMock()
        mock_config.provider = "unknown"
        request.get_config.return_value = mock_config

        with pytest.raises(GatewayError) as exc_info:
            list(gateway.stream(request))

        assert "Unknown provider" in str(exc_info.value)


class TestModelGatewayProviderSelection:
    """Tests for provider selection and fallback."""

    def test_complete_with_fallback_raises_if_all_unavailable(self) -> None:
        """Test fallback raises if ALL providers unavailable."""
        gateway = ModelGateway()

        # Make all providers unavailable
        for provider in gateway._providers.values():
            provider.is_available = MagicMock(return_value=False)

        request = CompletionRequest(prompt="Test")

        with pytest.raises(GatewayError) as exc_info:
            gateway.complete_with_fallback(request, fallback_order=["claude", "gemini", "ollama"])

        assert "All providers failed" in str(exc_info.value)
