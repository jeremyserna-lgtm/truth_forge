"""Tests for Ollama provider module.

Tests the OllamaProvider class.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.gateway.providers.ollama import OllamaProvider
from truth_forge.gateway.types import (
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ModelProvider,
    ProviderError,
)


class TestOllamaProviderInit:
    """Tests for OllamaProvider initialization."""

    def test_init_default_base_url(self) -> None:
        """Test initialization with default base URL."""
        with patch.dict("os.environ", {}, clear=True):
            provider = OllamaProvider()
            assert provider.base_url == "http://localhost:11434"
            assert provider.provider == ModelProvider.OLLAMA

    def test_init_with_custom_base_url(self) -> None:
        """Test initialization with custom base URL."""
        provider = OllamaProvider(base_url="http://custom:8080")
        assert provider.base_url == "http://custom:8080"

    @patch.dict("os.environ", {"OLLAMA_HOST": "http://env-host:11434"})
    def test_init_from_env(self) -> None:
        """Test initialization from environment variable."""
        provider = OllamaProvider()
        assert provider.base_url == "http://env-host:11434"

    def test_init_api_key_ignored(self) -> None:
        """Test that API key is stored but not required."""
        provider = OllamaProvider(api_key="unused")
        assert provider.api_key == "unused"


class TestOllamaProviderIsAvailable:
    """Tests for OllamaProvider.is_available method."""

    @patch.object(OllamaProvider, "_get_client")
    def test_is_available_server_running(self, mock_get_client: MagicMock) -> None:
        """Test is_available returns True when server is running."""
        mock_client = MagicMock()
        mock_client.list.return_value = ["model1", "model2"]
        mock_get_client.return_value = mock_client

        provider = OllamaProvider()
        assert provider.is_available() is True

    @patch.object(OllamaProvider, "_get_client")
    def test_is_available_server_not_running(self, mock_get_client: MagicMock) -> None:
        """Test is_available returns False when server is not running."""
        mock_client = MagicMock()
        mock_client.list.side_effect = Exception("Connection refused")
        mock_get_client.return_value = mock_client

        provider = OllamaProvider()
        assert provider.is_available() is False

    @patch.object(OllamaProvider, "_get_client")
    def test_is_available_cached(self, mock_get_client: MagicMock) -> None:
        """Test is_available caches result."""
        mock_client = MagicMock()
        mock_client.list.return_value = []
        mock_get_client.return_value = mock_client

        provider = OllamaProvider()

        # First call checks server
        result1 = provider.is_available()
        # Second call uses cache
        result2 = provider.is_available()

        assert result1 == result2
        # list() should only be called once
        assert mock_client.list.call_count == 1


class TestOllamaProviderGetClient:
    """Tests for OllamaProvider._get_client method."""

    def test_get_client_import_error(self) -> None:
        """Test _get_client raises ProviderError when ollama not installed."""
        provider = OllamaProvider()

        with patch.dict("sys.modules", {"ollama": None}):
            with patch(
                "builtins.__import__",
                side_effect=ImportError("No module named 'ollama'"),
            ):
                with pytest.raises(ProviderError) as exc_info:
                    provider._get_client()
                assert "ollama package not installed" in str(exc_info.value)

    def test_get_client_cached(self) -> None:
        """Test _get_client returns cached client."""
        provider = OllamaProvider()
        mock_client = MagicMock()
        provider._client = mock_client

        # Direct access should return same client
        assert provider._client is mock_client


class TestOllamaProviderComplete:
    """Tests for OllamaProvider.complete method."""

    @patch.object(OllamaProvider, "is_available", return_value=False)
    def test_complete_not_available(self, mock_available: MagicMock) -> None:
        """Test complete raises error when not available."""
        provider = OllamaProvider()

        request = CompletionRequest(prompt="test")
        with pytest.raises(ProviderError) as exc_info:
            provider.complete(request)
        assert "Ollama server not available" in str(exc_info.value)

    @patch.object(OllamaProvider, "is_available", return_value=True)
    @patch.object(OllamaProvider, "_get_client")
    def test_complete_success(
        self, mock_get_client: MagicMock, mock_available: MagicMock
    ) -> None:
        """Test successful completion."""
        mock_response = {
            "response": "Generated response",
            "prompt_eval_count": 10,
            "eval_count": 20,
        }

        mock_client = MagicMock()
        mock_client.generate.return_value = mock_response
        mock_get_client.return_value = mock_client

        provider = OllamaProvider()
        request = CompletionRequest(prompt="Hello", model="ollama-llama")

        result = provider.complete(request)

        assert isinstance(result, CompletionResponse)
        assert result.content == "Generated response"
        assert result.input_tokens == 10
        assert result.output_tokens == 20
        assert result.provider == ModelProvider.OLLAMA
        assert result.cost == 0.0  # Local = free

    @patch.object(OllamaProvider, "is_available", return_value=True)
    @patch.object(OllamaProvider, "_get_client")
    def test_complete_with_content(
        self, mock_get_client: MagicMock, mock_available: MagicMock
    ) -> None:
        """Test completion with additional content."""
        mock_response = {"response": "Response", "prompt_eval_count": 5, "eval_count": 10}

        mock_client = MagicMock()
        mock_client.generate.return_value = mock_response
        mock_get_client.return_value = mock_client

        provider = OllamaProvider()
        request = CompletionRequest(
            prompt="Summarize:",
            content="Content to summarize",
            model="ollama-llama",
        )

        provider.complete(request)

        # Verify prompt was combined
        call_args = mock_client.generate.call_args
        assert "Content to summarize" in call_args.kwargs["prompt"]

    @patch.object(OllamaProvider, "is_available", return_value=True)
    @patch.object(OllamaProvider, "_get_client")
    def test_complete_missing_token_counts(
        self, mock_get_client: MagicMock, mock_available: MagicMock
    ) -> None:
        """Test completion when token counts are missing."""
        mock_response = {"response": "Response"}  # No token counts

        mock_client = MagicMock()
        mock_client.generate.return_value = mock_response
        mock_get_client.return_value = mock_client

        provider = OllamaProvider()
        request = CompletionRequest(prompt="Hello", model="ollama-llama")

        result = provider.complete(request)
        assert result.input_tokens == 0
        assert result.output_tokens == 0

    @patch.object(OllamaProvider, "is_available", return_value=True)
    @patch.object(OllamaProvider, "_get_client")
    def test_complete_api_error(
        self, mock_get_client: MagicMock, mock_available: MagicMock
    ) -> None:
        """Test completion handles API errors."""
        mock_client = MagicMock()
        mock_client.generate.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        provider = OllamaProvider()
        request = CompletionRequest(prompt="Hello", model="ollama-llama")

        with pytest.raises(ProviderError) as exc_info:
            provider.complete(request)
        assert "Ollama error" in str(exc_info.value)


class TestOllamaProviderEmbed:
    """Tests for OllamaProvider.embed method."""

    @patch.object(OllamaProvider, "is_available", return_value=False)
    def test_embed_not_available(self, mock_available: MagicMock) -> None:
        """Test embed raises error when not available."""
        provider = OllamaProvider()

        request = EmbeddingRequest(text=["test"], model="nomic-embed-text")
        with pytest.raises(ProviderError) as exc_info:
            provider.embed(request)
        assert "Ollama server not available" in str(exc_info.value)

    @patch.object(OllamaProvider, "is_available", return_value=True)
    @patch.object(OllamaProvider, "_get_client")
    def test_embed_success(
        self, mock_get_client: MagicMock, mock_available: MagicMock
    ) -> None:
        """Test successful embedding."""
        mock_client = MagicMock()
        mock_client.embeddings.return_value = {
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        mock_get_client.return_value = mock_client

        provider = OllamaProvider()
        request = EmbeddingRequest(
            text=["Hello world", "Goodbye world"],
            model="ollama-nomic-embed-text",
        )

        result = provider.embed(request)

        assert isinstance(result, EmbeddingResponse)
        assert len(result.embeddings) == 2
        assert result.dimensions == 5
        assert result.cost == 0.0

    @patch.object(OllamaProvider, "is_available", return_value=True)
    @patch.object(OllamaProvider, "_get_client")
    def test_embed_strips_ollama_prefix(
        self, mock_get_client: MagicMock, mock_available: MagicMock
    ) -> None:
        """Test embed strips 'ollama-' prefix from model name."""
        mock_client = MagicMock()
        mock_client.embeddings.return_value = {"embedding": [0.1]}
        mock_get_client.return_value = mock_client

        provider = OllamaProvider()
        request = EmbeddingRequest(
            text=["Test"],
            model="ollama-nomic-embed-text",
        )

        provider.embed(request)

        # Verify model name was stripped
        call_args = mock_client.embeddings.call_args
        assert call_args.kwargs["model"] == "nomic-embed-text"

    @patch.object(OllamaProvider, "is_available", return_value=True)
    @patch.object(OllamaProvider, "_get_client")
    def test_embed_api_error(
        self, mock_get_client: MagicMock, mock_available: MagicMock
    ) -> None:
        """Test embed handles API errors."""
        mock_client = MagicMock()
        mock_client.embeddings.side_effect = Exception("Embedding Error")
        mock_get_client.return_value = mock_client

        provider = OllamaProvider()
        request = EmbeddingRequest(text=["Test"], model="nomic-embed-text")

        with pytest.raises(ProviderError) as exc_info:
            provider.embed(request)
        assert "Ollama embedding error" in str(exc_info.value)


class TestOllamaProviderStream:
    """Tests for OllamaProvider.stream method."""

    @patch.object(OllamaProvider, "is_available", return_value=False)
    def test_stream_not_available(self, mock_available: MagicMock) -> None:
        """Test stream raises error when not available."""
        provider = OllamaProvider()

        request = CompletionRequest(prompt="test")
        with pytest.raises(ProviderError) as exc_info:
            list(provider.stream(request))
        assert "Ollama server not available" in str(exc_info.value)

    @patch.object(OllamaProvider, "is_available", return_value=True)
    @patch.object(OllamaProvider, "_get_client")
    def test_stream_success(
        self, mock_get_client: MagicMock, mock_available: MagicMock
    ) -> None:
        """Test successful streaming."""
        chunks = [
            {"response": "Hello"},
            {"response": " "},
            {"response": "World"},
            {},  # Some chunks might not have response
        ]

        mock_client = MagicMock()
        mock_client.generate.return_value = iter(chunks)
        mock_get_client.return_value = mock_client

        provider = OllamaProvider()
        request = CompletionRequest(prompt="Hello", model="ollama-llama")

        result = list(provider.stream(request))
        assert result == ["Hello", " ", "World"]

    @patch.object(OllamaProvider, "is_available", return_value=True)
    @patch.object(OllamaProvider, "_get_client")
    def test_stream_with_content(
        self, mock_get_client: MagicMock, mock_available: MagicMock
    ) -> None:
        """Test streaming with additional content."""
        mock_client = MagicMock()
        mock_client.generate.return_value = iter([{"response": "Result"}])
        mock_get_client.return_value = mock_client

        provider = OllamaProvider()
        request = CompletionRequest(
            prompt="Summarize:",
            content="Content here",
            model="ollama-llama",
        )

        list(provider.stream(request))

        # Verify prompt was combined and stream=True
        call_args = mock_client.generate.call_args
        assert "Content here" in call_args.kwargs["prompt"]
        assert call_args.kwargs["stream"] is True

    @patch.object(OllamaProvider, "is_available", return_value=True)
    @patch.object(OllamaProvider, "_get_client")
    def test_stream_api_error(
        self, mock_get_client: MagicMock, mock_available: MagicMock
    ) -> None:
        """Test stream handles API errors."""
        mock_client = MagicMock()
        mock_client.generate.side_effect = Exception("Stream Error")
        mock_get_client.return_value = mock_client

        provider = OllamaProvider()
        request = CompletionRequest(prompt="Hello", model="ollama-llama")

        with pytest.raises(ProviderError) as exc_info:
            list(provider.stream(request))
        assert "Ollama streaming error" in str(exc_info.value)
