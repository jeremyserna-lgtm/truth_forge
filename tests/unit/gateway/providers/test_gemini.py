"""Tests for Gemini provider module.

Tests the GeminiProvider class.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.gateway.providers.gemini import GeminiProvider
from truth_forge.gateway.types import (
    CompletionRequest,
    CompletionResponse,
    ModelProvider,
    ProviderError,
)


class TestGeminiProviderInit:
    """Tests for GeminiProvider initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with explicit API key."""
        provider = GeminiProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.provider == ModelProvider.GEMINI

    def test_init_with_base_url(self) -> None:
        """Test initialization with base URL."""
        provider = GeminiProvider(api_key="key", base_url="https://custom.api.com")
        assert provider.base_url == "https://custom.api.com"

    @patch.dict("os.environ", {"GEMINI_API_KEY": "env-key"})
    def test_init_from_env(self) -> None:
        """Test initialization from environment variable."""
        provider = GeminiProvider()
        assert provider.api_key == "env-key"

    def test_init_no_api_key(self) -> None:
        """Test initialization without API key."""
        with patch.dict("os.environ", {}, clear=True):
            provider = GeminiProvider()
            assert provider.api_key is None


class TestGeminiProviderIsAvailable:
    """Tests for GeminiProvider.is_available method."""

    def test_is_available_with_key(self) -> None:
        """Test is_available returns True when API key is set."""
        provider = GeminiProvider(api_key="test-key")
        assert provider.is_available() is True

    def test_is_available_without_key(self) -> None:
        """Test is_available returns False when API key is not set."""
        with patch.dict("os.environ", {}, clear=True):
            provider = GeminiProvider()
            assert provider.is_available() is False


class TestGeminiProviderGetClient:
    """Tests for GeminiProvider._get_client method."""

    def test_get_client_import_error(self) -> None:
        """Test _get_client raises ProviderError when google-genai not installed."""
        provider = GeminiProvider(api_key="key")

        with patch.dict("sys.modules", {"google": None, "google.genai": None}):
            with patch(
                "builtins.__import__",
                side_effect=ImportError("No module named 'google.genai'"),
            ):
                with pytest.raises(ProviderError) as exc_info:
                    provider._get_client()
                assert "google-genai package not installed" in str(exc_info.value)

    def test_get_client_cached(self) -> None:
        """Test _get_client returns cached client."""
        provider = GeminiProvider(api_key="key")
        mock_client = MagicMock()
        provider._client = mock_client

        # Direct access should return same client
        assert provider._client is mock_client


class TestGeminiProviderComplete:
    """Tests for GeminiProvider.complete method."""

    def test_complete_not_available(self) -> None:
        """Test complete raises error when not available."""
        with patch.dict("os.environ", {}, clear=True):
            provider = GeminiProvider()

            request = CompletionRequest(prompt="test")
            with pytest.raises(ProviderError) as exc_info:
                provider.complete(request)
            assert "Gemini API key not configured" in str(exc_info.value)

    @patch.object(GeminiProvider, "_get_client")
    @patch("truth_forge.gateway.providers.gemini.time.time")
    def test_complete_success(
        self, mock_time: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test successful completion."""
        mock_time.side_effect = [0.0, 0.5]  # 500ms latency

        mock_response = MagicMock()
        mock_response.text = "Generated response"

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        # Mock the types import
        with patch("truth_forge.gateway.providers.gemini.genai_types_module", create=True):
            provider = GeminiProvider(api_key="test-key")
            request = CompletionRequest(prompt="Hello", model="gemini-flash")

            result = provider.complete(request)

            assert isinstance(result, CompletionResponse)
            assert result.content == "Generated response"
            assert result.provider == ModelProvider.GEMINI
            assert result.latency_ms == 500.0

    @patch.object(GeminiProvider, "_get_client")
    def test_complete_with_content(self, mock_get_client: MagicMock) -> None:
        """Test completion with additional content."""
        mock_response = MagicMock()
        mock_response.text = "Response"

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        provider = GeminiProvider(api_key="test-key")
        request = CompletionRequest(
            prompt="Summarize this:",
            content="This is the content to summarize.",
            model="gemini-flash",
        )

        provider.complete(request)

        # Verify prompt was combined
        call_args = mock_client.models.generate_content.call_args
        assert "This is the content to summarize" in call_args.kwargs["contents"]

    @patch.object(GeminiProvider, "_get_client")
    def test_complete_empty_response(self, mock_get_client: MagicMock) -> None:
        """Test completion with empty response."""
        mock_response = MagicMock()
        mock_response.text = None

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        provider = GeminiProvider(api_key="test-key")
        request = CompletionRequest(prompt="Hello", model="gemini-flash")

        result = provider.complete(request)
        assert result.content == ""

    @patch.object(GeminiProvider, "_get_client")
    def test_complete_api_error(self, mock_get_client: MagicMock) -> None:
        """Test completion handles API errors."""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        provider = GeminiProvider(api_key="test-key")
        request = CompletionRequest(prompt="Hello", model="gemini-flash")

        with pytest.raises(ProviderError) as exc_info:
            provider.complete(request)
        assert "Gemini API error" in str(exc_info.value)


class TestGeminiProviderStream:
    """Tests for GeminiProvider.stream method."""

    def test_stream_not_available(self) -> None:
        """Test stream raises error when not available."""
        with patch.dict("os.environ", {}, clear=True):
            provider = GeminiProvider()

            request = CompletionRequest(prompt="test")
            with pytest.raises(ProviderError) as exc_info:
                list(provider.stream(request))
            assert "Gemini API key not configured" in str(exc_info.value)

    @patch.object(GeminiProvider, "_get_client")
    def test_stream_success(self, mock_get_client: MagicMock) -> None:
        """Test successful streaming."""
        chunk1 = MagicMock()
        chunk1.text = "Hello"
        chunk2 = MagicMock()
        chunk2.text = " World"
        chunk3 = MagicMock()
        chunk3.text = None  # Some chunks might have no text

        mock_client = MagicMock()
        mock_client.models.generate_content_stream.return_value = iter(
            [chunk1, chunk2, chunk3]
        )
        mock_get_client.return_value = mock_client

        provider = GeminiProvider(api_key="test-key")
        request = CompletionRequest(prompt="Hello", model="gemini-flash")

        chunks = list(provider.stream(request))
        assert chunks == ["Hello", " World"]

    @patch.object(GeminiProvider, "_get_client")
    def test_stream_with_content(self, mock_get_client: MagicMock) -> None:
        """Test streaming with additional content."""
        chunk = MagicMock()
        chunk.text = "Result"

        mock_client = MagicMock()
        mock_client.models.generate_content_stream.return_value = iter([chunk])
        mock_get_client.return_value = mock_client

        provider = GeminiProvider(api_key="test-key")
        request = CompletionRequest(
            prompt="Summarize:",
            content="Content here",
            model="gemini-flash",
        )

        list(provider.stream(request))

        # Verify prompt was combined
        call_args = mock_client.models.generate_content_stream.call_args
        assert "Content here" in call_args.kwargs["contents"]

    @patch.object(GeminiProvider, "_get_client")
    def test_stream_api_error(self, mock_get_client: MagicMock) -> None:
        """Test stream handles API errors."""
        mock_client = MagicMock()
        mock_client.models.generate_content_stream.side_effect = Exception(
            "Stream Error"
        )
        mock_get_client.return_value = mock_client

        provider = GeminiProvider(api_key="test-key")
        request = CompletionRequest(prompt="Hello", model="gemini-flash")

        with pytest.raises(ProviderError) as exc_info:
            list(provider.stream(request))
        assert "Gemini streaming error" in str(exc_info.value)
