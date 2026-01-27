"""Tests for Claude provider module.

Tests the ClaudeProvider class.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.gateway.providers.claude import ClaudeProvider
from truth_forge.gateway.types import (
    CompletionRequest,
    CompletionResponse,
    ModelProvider,
    ProviderError,
)


class TestClaudeProviderInit:
    """Tests for ClaudeProvider initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with explicit API key."""
        provider = ClaudeProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.provider == ModelProvider.CLAUDE

    def test_init_with_base_url(self) -> None:
        """Test initialization with base URL."""
        provider = ClaudeProvider(api_key="key", base_url="https://custom.api.com")
        assert provider.base_url == "https://custom.api.com"

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "env-key"})
    def test_init_from_env(self) -> None:
        """Test initialization from environment variable."""
        provider = ClaudeProvider()
        assert provider.api_key == "env-key"

    def test_init_no_api_key(self) -> None:
        """Test initialization without API key."""
        with patch.dict("os.environ", {}, clear=True):
            provider = ClaudeProvider()
            assert provider.api_key is None


class TestClaudeProviderIsAvailable:
    """Tests for ClaudeProvider.is_available method."""

    def test_is_available_with_key(self) -> None:
        """Test is_available returns True when API key is set."""
        provider = ClaudeProvider(api_key="test-key")
        assert provider.is_available() is True

    def test_is_available_without_key(self) -> None:
        """Test is_available returns False when API key is not set."""
        with patch.dict("os.environ", {}, clear=True):
            provider = ClaudeProvider()
            assert provider.is_available() is False


class TestClaudeProviderGetClient:
    """Tests for ClaudeProvider._get_client method."""

    def test_get_client_import_error(self) -> None:
        """Test _get_client raises ProviderError when anthropic not installed."""
        provider = ClaudeProvider(api_key="key")

        with patch.dict("sys.modules", {"anthropic": None}):
            with patch(
                "builtins.__import__",
                side_effect=ImportError("No module named 'anthropic'"),
            ):
                with pytest.raises(ProviderError) as exc_info:
                    provider._get_client()
                assert "anthropic package not installed" in str(exc_info.value)

    @patch("truth_forge.gateway.providers.claude.ClaudeProvider._get_client")
    def test_get_client_cached(self, mock_get_client: MagicMock) -> None:
        """Test _get_client returns cached client."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        provider = ClaudeProvider(api_key="key")
        provider._client = mock_client

        # Direct access should return same client
        assert provider._client is mock_client


class TestClaudeProviderComplete:
    """Tests for ClaudeProvider.complete method."""

    def test_complete_not_available(self) -> None:
        """Test complete raises error when not available."""
        with patch.dict("os.environ", {}, clear=True):
            provider = ClaudeProvider()

            request = CompletionRequest(prompt="test")
            with pytest.raises(ProviderError) as exc_info:
                provider.complete(request)
            assert "Claude API key not configured" in str(exc_info.value)

    @patch.object(ClaudeProvider, "_get_client")
    def test_complete_success(self, mock_get_client: MagicMock) -> None:
        """Test successful completion."""
        # Mock the Anthropic response
        mock_block = MagicMock()
        mock_block.text = "Generated response"

        mock_usage = MagicMock()
        mock_usage.input_tokens = 10
        mock_usage.output_tokens = 20

        mock_response = MagicMock()
        mock_response.content = [mock_block]
        mock_response.usage = mock_usage

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        provider = ClaudeProvider(api_key="test-key")
        request = CompletionRequest(prompt="Hello", model="claude-haiku")

        result = provider.complete(request)

        assert isinstance(result, CompletionResponse)
        assert result.content == "Generated response"
        assert result.input_tokens == 10
        assert result.output_tokens == 20
        assert result.provider == ModelProvider.CLAUDE

    @patch.object(ClaudeProvider, "_get_client")
    def test_complete_with_system_prompt(self, mock_get_client: MagicMock) -> None:
        """Test completion with system prompt."""
        mock_block = MagicMock()
        mock_block.text = "Response"
        mock_usage = MagicMock()
        mock_usage.input_tokens = 5
        mock_usage.output_tokens = 10
        mock_response = MagicMock()
        mock_response.content = [mock_block]
        mock_response.usage = mock_usage

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        provider = ClaudeProvider(api_key="test-key")
        request = CompletionRequest(
            prompt="Hello",
            system="You are a helpful assistant",
            model="claude-haiku",
        )

        provider.complete(request)

        # Verify system prompt was passed
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs["system"] == "You are a helpful assistant"

    @patch.object(ClaudeProvider, "_get_client")
    def test_complete_empty_content(self, mock_get_client: MagicMock) -> None:
        """Test completion with empty content response."""
        mock_usage = MagicMock()
        mock_usage.input_tokens = 5
        mock_usage.output_tokens = 0
        mock_response = MagicMock()
        mock_response.content = []
        mock_response.usage = mock_usage

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        provider = ClaudeProvider(api_key="test-key")
        request = CompletionRequest(prompt="Hello", model="claude-haiku")

        result = provider.complete(request)
        assert result.content == ""

    @patch.object(ClaudeProvider, "_get_client")
    def test_complete_api_error(self, mock_get_client: MagicMock) -> None:
        """Test completion handles API errors."""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        provider = ClaudeProvider(api_key="test-key")
        request = CompletionRequest(prompt="Hello", model="claude-haiku")

        with pytest.raises(ProviderError) as exc_info:
            provider.complete(request)
        assert "Claude API error" in str(exc_info.value)


class TestClaudeProviderStream:
    """Tests for ClaudeProvider.stream method."""

    def test_stream_not_available(self) -> None:
        """Test stream raises error when not available."""
        with patch.dict("os.environ", {}, clear=True):
            provider = ClaudeProvider()

            request = CompletionRequest(prompt="test")
            with pytest.raises(ProviderError) as exc_info:
                list(provider.stream(request))
            assert "Claude API key not configured" in str(exc_info.value)

    @patch.object(ClaudeProvider, "_get_client")
    def test_stream_success(self, mock_get_client: MagicMock) -> None:
        """Test successful streaming."""
        mock_stream = MagicMock()
        mock_stream.text_stream = iter(["Hello", " ", "World"])
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=None)

        mock_client = MagicMock()
        mock_client.messages.stream.return_value = mock_stream
        mock_get_client.return_value = mock_client

        provider = ClaudeProvider(api_key="test-key")
        request = CompletionRequest(prompt="Hello", model="claude-haiku")

        chunks = list(provider.stream(request))
        assert chunks == ["Hello", " ", "World"]

    @patch.object(ClaudeProvider, "_get_client")
    def test_stream_api_error(self, mock_get_client: MagicMock) -> None:
        """Test stream handles API errors."""
        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(side_effect=Exception("Stream Error"))

        mock_client = MagicMock()
        mock_client.messages.stream.return_value = mock_stream
        mock_get_client.return_value = mock_client

        provider = ClaudeProvider(api_key="test-key")
        request = CompletionRequest(prompt="Hello", model="claude-haiku")

        with pytest.raises(ProviderError) as exc_info:
            list(provider.stream(request))
        assert "Claude streaming error" in str(exc_info.value)
