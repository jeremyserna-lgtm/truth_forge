"""Tests for gateway types module.

Tests the data structures for LLM operations.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from truth_forge.gateway.types import (
    MODELS,
    CompletionRequest,
    CompletionResponse,
    CostLimitError,
    EmbeddingRequest,
    EmbeddingResponse,
    GatewayError,
    ModelConfig,
    ModelProvider,
    ProviderError,
    RateLimitError,
    get_model_config,
)


class TestModelProvider:
    """Tests for ModelProvider enum."""

    def test_provider_values(self) -> None:
        """Test provider values."""
        assert ModelProvider.CLAUDE.value == "claude"
        assert ModelProvider.GEMINI.value == "gemini"
        assert ModelProvider.OLLAMA.value == "ollama"

    def test_from_string(self) -> None:
        """Test creating from string."""
        assert ModelProvider.from_string("claude") == ModelProvider.CLAUDE
        assert ModelProvider.from_string("CLAUDE") == ModelProvider.CLAUDE
        assert ModelProvider.from_string("gemini") == ModelProvider.GEMINI
        assert ModelProvider.from_string("ollama") == ModelProvider.OLLAMA

    def test_from_string_invalid(self) -> None:
        """Test from_string raises for invalid provider."""
        with pytest.raises(ValueError) as exc_info:
            ModelProvider.from_string("invalid")
        assert "Unknown provider" in str(exc_info.value)


class TestModelConfig:
    """Tests for ModelConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default model config values."""
        config = ModelConfig(
            provider=ModelProvider.CLAUDE,
            model="test-model",
        )
        assert config.max_tokens == 4096
        assert config.temperature == 0.7
        assert config.cost_per_1k_input == 0.0
        assert config.cost_per_1k_output == 0.0
        assert config.supports_json is True
        assert config.supports_streaming is True
        assert config.supports_tools is False

    def test_is_free_property(self) -> None:
        """Test is_free property."""
        free_config = ModelConfig(
            provider=ModelProvider.OLLAMA,
            model="llama",
            cost_per_1k_input=0.0,
            cost_per_1k_output=0.0,
        )
        paid_config = ModelConfig(
            provider=ModelProvider.CLAUDE,
            model="claude",
            cost_per_1k_input=0.003,
            cost_per_1k_output=0.015,
        )

        assert free_config.is_free is True
        assert paid_config.is_free is False


class TestModels:
    """Tests for pre-configured models."""

    def test_models_exist(self) -> None:
        """Test that expected models exist."""
        expected = [
            "claude-opus",
            "claude-sonnet",
            "claude-haiku",
            "gemini-pro",
            "gemini-flash",
            "ollama-llama",
            "ollama-mistral",
            "ollama-embed",
        ]
        for model_name in expected:
            assert model_name in MODELS

    def test_get_model_config(self) -> None:
        """Test get_model_config function."""
        config = get_model_config("claude-haiku")

        assert config.provider == ModelProvider.CLAUDE
        assert "haiku" in config.model

    def test_get_model_config_invalid(self) -> None:
        """Test get_model_config raises for invalid model."""
        with pytest.raises(ValueError) as exc_info:
            get_model_config("nonexistent-model")
        assert "Unknown model" in str(exc_info.value)


class TestCompletionRequest:
    """Tests for CompletionRequest dataclass."""

    def test_default_values(self) -> None:
        """Test default completion request values."""
        request = CompletionRequest(prompt="Test prompt")

        assert request.prompt == "Test prompt"
        assert request.content is None
        assert request.model == "claude-haiku"
        assert request.as_json is False
        assert request.system is None
        assert request.tools is None

    def test_custom_values(self) -> None:
        """Test custom completion request values."""
        request = CompletionRequest(
            prompt="Analyze this",
            content="content to analyze",
            model="claude-sonnet",
            max_tokens=1000,
            temperature=0.5,
            as_json=True,
            system="You are a helpful assistant",
        )

        assert request.prompt == "Analyze this"
        assert request.content == "content to analyze"
        assert request.model == "claude-sonnet"
        assert request.max_tokens == 1000
        assert request.temperature == 0.5
        assert request.as_json is True
        assert request.system == "You are a helpful assistant"

    def test_get_config_with_string(self) -> None:
        """Test get_config with string model."""
        request = CompletionRequest(prompt="Test", model="claude-haiku")
        config = request.get_config()

        assert isinstance(config, ModelConfig)
        assert config.provider == ModelProvider.CLAUDE

    def test_get_config_with_config(self) -> None:
        """Test get_config with ModelConfig model."""
        custom_config = ModelConfig(
            provider=ModelProvider.GEMINI,
            model="custom-model",
        )
        request = CompletionRequest(prompt="Test", model=custom_config)
        config = request.get_config()

        assert config is custom_config


class TestCompletionResponse:
    """Tests for CompletionResponse dataclass."""

    def test_default_values(self) -> None:
        """Test default completion response values."""
        response = CompletionResponse(
            content="Response content",
            model="claude-haiku",
            provider=ModelProvider.CLAUDE,
        )

        assert response.content == "Response content"
        assert response.input_tokens == 0
        assert response.output_tokens == 0
        assert response.cost == 0.0
        assert response.cached is False
        assert response.tool_calls is None

    def test_to_dict(self) -> None:
        """Test converting response to dictionary."""
        response = CompletionResponse(
            content="Test",
            model="claude-haiku",
            provider=ModelProvider.CLAUDE,
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
        )
        data = response.to_dict()

        assert data["content"] == "Test"
        assert data["model"] == "claude-haiku"
        assert data["provider"] == "claude"
        assert data["input_tokens"] == 100
        assert data["output_tokens"] == 50
        assert "timestamp" in data


class TestEmbeddingRequest:
    """Tests for EmbeddingRequest dataclass."""

    def test_default_values(self) -> None:
        """Test default embedding request values."""
        request = EmbeddingRequest(text="Test text")

        assert request.text == "Test text"
        assert request.model == "ollama-embed"
        assert request.dimensions is None

    def test_texts_property_single(self) -> None:
        """Test texts property with single string."""
        request = EmbeddingRequest(text="Single text")
        assert request.texts == ["Single text"]

    def test_texts_property_list(self) -> None:
        """Test texts property with list."""
        request = EmbeddingRequest(text=["Text 1", "Text 2"])
        assert request.texts == ["Text 1", "Text 2"]


class TestEmbeddingResponse:
    """Tests for EmbeddingResponse dataclass."""

    def test_default_values(self) -> None:
        """Test default embedding response values."""
        response = EmbeddingResponse(
            embeddings=[[0.1, 0.2, 0.3]],
            model="ollama-embed",
            dimensions=3,
        )

        assert response.embeddings == [[0.1, 0.2, 0.3]]
        assert response.total_tokens == 0
        assert response.cost == 0.0

    def test_getitem(self) -> None:
        """Test indexing embedding response."""
        response = EmbeddingResponse(
            embeddings=[[0.1, 0.2], [0.3, 0.4]],
            model="test",
            dimensions=2,
        )

        assert response[0] == [0.1, 0.2]
        assert response[1] == [0.3, 0.4]

    def test_len(self) -> None:
        """Test length of embedding response."""
        response = EmbeddingResponse(
            embeddings=[[0.1], [0.2], [0.3]],
            model="test",
            dimensions=1,
        )

        assert len(response) == 3


class TestGatewayError:
    """Tests for GatewayError exception."""

    def test_basic_error(self) -> None:
        """Test basic gateway error."""
        error = GatewayError("Test error")
        assert str(error) == "Test error"
        assert error.provider is None

    def test_error_with_provider(self) -> None:
        """Test gateway error with provider."""
        error = GatewayError("Test error", provider="claude")
        assert error.provider == "claude"


class TestProviderError:
    """Tests for ProviderError exception."""

    def test_provider_error(self) -> None:
        """Test provider error."""
        error = ProviderError(
            "Provider failed",
            provider="claude",
            status_code=500,
            response={"error": "Internal error"},
        )

        assert str(error) == "Provider failed"
        assert error.provider == "claude"
        assert error.status_code == 500
        assert error.response == {"error": "Internal error"}


class TestRateLimitError:
    """Tests for RateLimitError exception."""

    def test_rate_limit_error(self) -> None:
        """Test rate limit error."""
        error = RateLimitError(
            "Rate limited",
            provider="claude",
            retry_after=30.0,
        )

        assert error.provider == "claude"
        assert error.status_code == 429
        assert error.retry_after == 30.0


class TestCostLimitError:
    """Tests for CostLimitError exception."""

    def test_cost_limit_error(self) -> None:
        """Test cost limit error."""
        error = CostLimitError(
            "Cost exceeded",
            current_cost=15.0,
            limit=10.0,
        )

        assert str(error) == "Cost exceeded"
        assert error.current_cost == 15.0
        assert error.limit == 10.0
