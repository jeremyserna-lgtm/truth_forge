"""Tests for Maverick provider."""

from __future__ import annotations

import json
from unittest.mock import Mock, patch

import pytest

from truth_forge.gateway.providers.maverick import MaverickProvider
from truth_forge.gateway.types import CompletionRequest, ModelProvider, ProviderError


class TestMaverickProvider:
    """Test MaverickProvider class."""

    def test_provider_enum(self) -> None:
        """Test provider enum is set correctly."""
        provider = MaverickProvider()
        assert provider.provider == ModelProvider.MAVERICK

    def test_default_endpoint(self) -> None:
        """Test default endpoint."""
        provider = MaverickProvider()
        assert provider.base_url == "http://localhost:8766/v1"

    def test_custom_base_url(self) -> None:
        """Test custom base URL."""
        provider = MaverickProvider(base_url="http://custom:9000/v1")
        assert provider.base_url == "http://custom:9000/v1"

    def test_base_url_from_env(self) -> None:
        """Test base URL from environment variable."""
        with patch.dict("os.environ", {"MAVERICK_BASE_URL": "http://env:8000/v1"}):
            provider = MaverickProvider()
            assert provider.base_url == "http://env:8000/v1"

    @patch("urllib.request.urlopen")
    def test_is_available_success(self, mock_urlopen: Mock) -> None:
        """Test is_available returns True when server responds."""
        mock_response = Mock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        provider = MaverickProvider()
        assert provider.is_available() is True

    @patch("urllib.request.urlopen")
    def test_is_available_failure(self, mock_urlopen: Mock) -> None:
        """Test is_available returns False when server unavailable."""
        mock_urlopen.side_effect = Exception("Connection failed")

        provider = MaverickProvider()
        assert provider.is_available() is False

    @patch("urllib.request.urlopen")
    def test_is_available_cached(self, mock_urlopen: Mock) -> None:
        """Test is_available result is cached."""
        mock_response = Mock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        provider = MaverickProvider()
        result1 = provider.is_available()
        result2 = provider.is_available()

        assert result1 is True
        assert result2 is True
        assert mock_urlopen.call_count == 1  # Only called once

    @patch("urllib.request.urlopen")
    def test_complete_success(self, mock_urlopen: Mock) -> None:
        """Test complete returns successful response."""
        # Mock availability check (context manager returning status 200)
        mock_models_cm = Mock()
        mock_models_cm.__enter__ = Mock(return_value=Mock(status=200))
        mock_models_cm.__exit__ = Mock(return_value=False)

        # Mock completion response (context manager returning JSON body)
        mock_completion_cm = Mock()
        mock_completion_body = Mock()
        mock_completion_body.read.return_value.decode.return_value = json.dumps(
            {
                "choices": [{"message": {"content": "Test response"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            }
        )
        mock_completion_cm.__enter__ = Mock(return_value=mock_completion_body)
        mock_completion_cm.__exit__ = Mock(return_value=False)

        # First call = is_available(), second call = complete()
        mock_urlopen.side_effect = [mock_models_cm, mock_completion_cm]

        provider = MaverickProvider()
        request = CompletionRequest(prompt="Test prompt")
        response = provider.complete(request)

        assert response.content == "Test response"
        assert response.provider == ModelProvider.MAVERICK
        assert response.input_tokens == 10
        assert response.output_tokens == 5
        assert response.cost == 0.0

    @patch("urllib.request.urlopen")
    def test_complete_not_available_raises_error(self, mock_urlopen: Mock) -> None:
        """Test complete raises error when provider not available."""
        mock_urlopen.side_effect = Exception("Connection failed")

        provider = MaverickProvider()
        request = CompletionRequest(prompt="Test prompt")

        with pytest.raises(ProviderError, match="Maverick not available"):
            provider.complete(request)

    @patch("urllib.request.urlopen")
    def test_complete_request_error(self, mock_urlopen: Mock) -> None:
        """Test complete raises ProviderError on request failure."""
        # Mock availability check (context manager returning status 200)
        mock_models_cm = Mock()
        mock_models_cm.__enter__ = Mock(return_value=Mock(status=200))
        mock_models_cm.__exit__ = Mock(return_value=False)

        # First call = is_available() succeeds, second call = complete() fails
        mock_urlopen.side_effect = [
            mock_models_cm,  # Availability check
            Exception("Request failed"),  # Completion request
        ]

        provider = MaverickProvider()
        request = CompletionRequest(prompt="Test prompt")

        with pytest.raises(ProviderError, match="Maverick completion error"):
            provider.complete(request)

    @patch("urllib.request.urlopen")
    def test_complete_with_temperature(self, mock_urlopen: Mock) -> None:
        """Test complete uses custom temperature."""
        # Mock availability check (context manager returning status 200)
        mock_models_cm = Mock()
        mock_models_cm.__enter__ = Mock(return_value=Mock(status=200))
        mock_models_cm.__exit__ = Mock(return_value=False)

        # Mock completion response (context manager returning JSON body)
        mock_completion_cm = Mock()
        mock_completion_body = Mock()
        mock_completion_body.read.return_value.decode.return_value = json.dumps(
            {
                "choices": [{"message": {"content": "Response"}}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 3},
            }
        )
        mock_completion_cm.__enter__ = Mock(return_value=mock_completion_body)
        mock_completion_cm.__exit__ = Mock(return_value=False)

        # First call = is_available(), second call = complete()
        mock_urlopen.side_effect = [mock_models_cm, mock_completion_cm]

        provider = MaverickProvider()
        request = CompletionRequest(prompt="Test", temperature=0.9)
        provider.complete(request)

        # Verify request was made with correct temperature
        call_args = mock_urlopen.call_args_list[-1]
        request_data = json.loads(call_args[0][0].data.decode())
        assert request_data["temperature"] == 0.9

    @patch("urllib.request.urlopen")
    def test_complete_with_max_tokens(self, mock_urlopen: Mock) -> None:
        """Test complete uses custom max_tokens."""
        # Mock availability check (context manager returning status 200)
        mock_models_cm = Mock()
        mock_models_cm.__enter__ = Mock(return_value=Mock(status=200))
        mock_models_cm.__exit__ = Mock(return_value=False)

        # Mock completion response (context manager returning JSON body)
        mock_completion_cm = Mock()
        mock_completion_body = Mock()
        mock_completion_body.read.return_value.decode.return_value = json.dumps(
            {
                "choices": [{"message": {"content": "Response"}}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 3},
            }
        )
        mock_completion_cm.__enter__ = Mock(return_value=mock_completion_body)
        mock_completion_cm.__exit__ = Mock(return_value=False)

        # First call = is_available(), second call = complete()
        mock_urlopen.side_effect = [mock_models_cm, mock_completion_cm]

        provider = MaverickProvider()
        request = CompletionRequest(prompt="Test", max_tokens=100)
        provider.complete(request)

        # Verify request was made with correct max_tokens
        call_args = mock_urlopen.call_args_list[-1]
        request_data = json.loads(call_args[0][0].data.decode())
        assert request_data["max_tokens"] == 100
