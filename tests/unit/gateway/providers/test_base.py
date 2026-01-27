"""Tests for base provider module.

Tests the BaseProvider abstract class.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest

from truth_forge.gateway.providers.base import BaseProvider
from truth_forge.gateway.types import (
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    ModelConfig,
    ModelProvider,
)


class ConcreteProvider(BaseProvider):
    """Concrete implementation for testing."""

    provider = ModelProvider.CLAUDE

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Mock completion."""
        return CompletionResponse(
            content="test response",
            model="test-model",
            provider=self.provider,
            input_tokens=10,
            output_tokens=5,
        )

    def is_available(self) -> bool:
        """Mock availability check."""
        return self.api_key is not None


class TestBaseProvider:
    """Tests for BaseProvider class."""

    def test_init_default_values(self) -> None:
        """Test initialization with default values."""
        provider = ConcreteProvider()

        assert provider.api_key is None
        assert provider.base_url is None

    def test_init_with_api_key(self) -> None:
        """Test initialization with API key."""
        provider = ConcreteProvider(api_key="test-key")

        assert provider.api_key == "test-key"

    def test_init_with_base_url(self) -> None:
        """Test initialization with base URL."""
        provider = ConcreteProvider(base_url="http://localhost:8000")

        assert provider.base_url == "http://localhost:8000"

    def test_embed_not_implemented(self) -> None:
        """Test embed raises NotImplementedError by default."""
        provider = ConcreteProvider()
        request = EmbeddingRequest(text="test")

        with pytest.raises(NotImplementedError) as exc_info:
            provider.embed(request)

        assert "does not support embeddings" in str(exc_info.value)

    def test_stream_not_implemented(self) -> None:
        """Test stream raises NotImplementedError by default."""
        provider = ConcreteProvider()
        request = CompletionRequest(prompt="test")

        with pytest.raises(NotImplementedError) as exc_info:
            provider.stream(request)

        assert "does not support streaming" in str(exc_info.value)

    def test_get_default_model_claude(self) -> None:
        """Test get_default_model for Claude provider."""
        provider = ConcreteProvider()

        model = provider.get_default_model()

        assert model == "claude-3-5-haiku-20241022"

    def test_get_default_model_unknown(self) -> None:
        """Test get_default_model for unknown provider."""

        class UnknownProvider(BaseProvider):
            provider = ModelProvider.OLLAMA  # Will test with ollama

            def complete(self, request: CompletionRequest) -> CompletionResponse:
                return CompletionResponse(
                    content="",
                    model="",
                    provider=self.provider,
                    input_tokens=0,
                    output_tokens=0,
                )

            def is_available(self) -> bool:
                return True

        provider = UnknownProvider()
        model = provider.get_default_model()

        assert model == "llama3.2"

    def test_estimate_cost(self) -> None:
        """Test estimate_cost calculates correctly."""
        provider = ConcreteProvider()
        config = ModelConfig(
            model="test",
            provider=ModelProvider.CLAUDE,
            max_tokens=1000,
            cost_per_1k_input=0.001,
            cost_per_1k_output=0.002,
        )

        cost = provider.estimate_cost(config, input_tokens=1000, output_tokens=500)

        # (1000/1000 * 0.001) + (500/1000 * 0.002) = 0.001 + 0.001 = 0.002
        assert cost == 0.002

    def test_estimate_cost_zero_tokens(self) -> None:
        """Test estimate_cost with zero tokens."""
        provider = ConcreteProvider()
        config = ModelConfig(
            model="test",
            provider=ModelProvider.CLAUDE,
            max_tokens=1000,
            cost_per_1k_input=0.001,
            cost_per_1k_output=0.002,
        )

        cost = provider.estimate_cost(config, input_tokens=0, output_tokens=0)

        assert cost == 0.0

    def test_build_messages_with_system(self) -> None:
        """Test _build_messages with system prompt."""
        provider = ConcreteProvider()
        request = CompletionRequest(
            prompt="user message",
            system="system prompt",
        )

        messages = provider._build_messages(request)

        assert len(messages) == 2
        assert messages[0] == {"role": "system", "content": "system prompt"}
        assert messages[1] == {"role": "user", "content": "user message"}

    def test_build_messages_without_system(self) -> None:
        """Test _build_messages without system prompt."""
        provider = ConcreteProvider()
        request = CompletionRequest(prompt="user message")

        messages = provider._build_messages(request)

        assert len(messages) == 1
        assert messages[0] == {"role": "user", "content": "user message"}

    def test_build_messages_with_content(self) -> None:
        """Test _build_messages with additional content."""
        provider = ConcreteProvider()
        request = CompletionRequest(
            prompt="Analyze this:",
            content="some content to analyze",
        )

        messages = provider._build_messages(request)

        assert len(messages) == 1
        assert "Analyze this:" in messages[0]["content"]
        assert "some content to analyze" in messages[0]["content"]

    def test_is_available_abstract(self) -> None:
        """Test is_available works on concrete implementation."""
        provider_with_key = ConcreteProvider(api_key="test-key")
        provider_without_key = ConcreteProvider()

        assert provider_with_key.is_available() is True
        assert provider_without_key.is_available() is False

    def test_complete_abstract(self) -> None:
        """Test complete works on concrete implementation."""
        provider = ConcreteProvider()
        request = CompletionRequest(prompt="test")

        response = provider.complete(request)

        assert response.content == "test response"
        assert response.provider == ModelProvider.CLAUDE
