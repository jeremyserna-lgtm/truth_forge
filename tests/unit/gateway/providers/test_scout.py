"""Tests for Scout provider."""

from __future__ import annotations

import json
from unittest.mock import Mock, patch

import pytest

from truth_forge.gateway.providers.scout import (
    THE_CONTEXT,
    THE_MODEL,
    HardwareCapacity,
    ScoutProvider,
    get_hardware_status,
    get_operational_context,
)
from truth_forge.gateway.types import (
    CompletionRequest,
    EmbeddingRequest,
    ModelProvider,
    ProviderError,
)


class TestScoutConstants:
    """Test Scout constants."""

    def test_the_context(self) -> None:
        """Test THE_CONTEXT is 10M."""
        assert THE_CONTEXT == 10_000_000

    def test_the_model(self) -> None:
        """Test THE_MODEL is correct."""
        assert THE_MODEL == "llama4:scout"


class TestHardwareCapacity:
    """Test HardwareCapacity class."""

    @patch("truth_forge.gateway.providers.scout._get_system_memory_gb")
    @patch("truth_forge.gateway.providers.scout._detect_exa_cluster")
    def test_detect_high_memory(self, mock_cluster: Mock, mock_memory: Mock) -> None:
        """Test detection with high memory."""
        mock_memory.return_value = 512
        mock_cluster.return_value = False

        capacity = HardwareCapacity.detect()
        assert capacity.memory_gb == 512
        assert capacity.operational_context <= THE_CONTEXT
        assert "High Memory" in capacity.description

    @patch("truth_forge.gateway.providers.scout._get_system_memory_gb")
    @patch("truth_forge.gateway.providers.scout._detect_exa_cluster")
    def test_detect_cluster(self, mock_cluster: Mock, mock_memory: Mock) -> None:
        """Test detection with EXO cluster."""
        mock_memory.return_value = 128
        mock_cluster.return_value = True

        capacity = HardwareCapacity.detect()
        assert capacity.cluster_available is True
        assert "EXO Cluster" in capacity.description

    @patch("truth_forge.gateway.providers.scout._get_system_memory_gb")
    @patch("truth_forge.gateway.providers.scout._detect_exa_cluster")
    def test_detect_low_memory(self, mock_cluster: Mock, mock_memory: Mock) -> None:
        """Test detection with low memory."""
        mock_memory.return_value = 64
        mock_cluster.return_value = False

        capacity = HardwareCapacity.detect()
        assert capacity.memory_gb == 64
        assert capacity.operational_context <= THE_CONTEXT
        assert "Limited Memory" in capacity.description


class TestGetOperationalContext:
    """Test get_operational_context function."""

    @patch("truth_forge.gateway.providers.scout._hardware_capacity", None)
    @patch("truth_forge.gateway.providers.scout.HardwareCapacity.detect")
    def test_gets_operational_context(self, mock_detect: Mock) -> None:
        """Test gets operational context."""
        mock_capacity = Mock()
        mock_capacity.operational_context = 500_000
        mock_detect.return_value = mock_capacity

        context = get_operational_context()
        assert context == 500_000

    @patch("truth_forge.gateway.providers.scout._hardware_capacity", None)
    @patch("truth_forge.gateway.providers.scout.HardwareCapacity.detect")
    def test_cached(self, mock_detect: Mock) -> None:
        """Test result is cached."""
        mock_capacity = Mock()
        mock_capacity.operational_context = 500_000
        mock_detect.return_value = mock_capacity

        context1 = get_operational_context()
        context2 = get_operational_context()

        assert context1 == context2
        assert mock_detect.call_count == 1  # Only called once


class TestGetHardwareStatus:
    """Test get_hardware_status function."""

    @patch("truth_forge.gateway.providers.scout._hardware_capacity", None)
    @patch("truth_forge.gateway.providers.scout.HardwareCapacity.detect")
    def test_gets_hardware_status(self, mock_detect: Mock) -> None:
        """Test gets hardware status."""
        mock_capacity = Mock()
        mock_capacity.operational_context = 500_000
        mock_capacity.memory_gb = 256
        mock_capacity.cluster_available = False
        mock_capacity.description = "Test description"
        mock_detect.return_value = mock_capacity

        status = get_hardware_status()
        assert status["architecture"] == THE_CONTEXT
        assert status["operational"] == 500_000
        assert status["memory_gb"] == 256
        assert status["cluster_available"] is False
        assert status["description"] == "Test description"
        assert "utilization" in status


class TestScoutProvider:
    """Test ScoutProvider class."""

    def test_provider_enum(self) -> None:
        """Test provider enum is set correctly."""
        provider = ScoutProvider()
        assert provider.provider == ModelProvider.SCOUT

    def test_default_endpoint(self) -> None:
        """Test default endpoint."""
        provider = ScoutProvider()
        assert provider.base_url == "http://localhost:11434/v1"

    def test_custom_base_url(self) -> None:
        """Test custom base URL."""
        provider = ScoutProvider(base_url="http://custom:9000/v1")
        assert provider.base_url == "http://custom:9000/v1"

    def test_base_url_from_env(self) -> None:
        """Test base URL from environment variable."""
        with patch.dict("os.environ", {"SCOUT_BASE_URL": "http://env:8000/v1"}):
            provider = ScoutProvider()
            assert provider.base_url == "http://env:8000/v1"

    @patch("urllib.request.urlopen")
    def test_is_available_success(self, mock_urlopen: Mock) -> None:
        """Test is_available returns True when server responds."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value.decode.return_value = json.dumps(
            {"data": [{"id": "llama4:scout"}]}
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        provider = ScoutProvider()
        assert provider.is_available() is True

    @patch("urllib.request.urlopen")
    def test_is_available_failure(self, mock_urlopen: Mock) -> None:
        """Test is_available returns False when server unavailable."""
        mock_urlopen.side_effect = Exception("Connection failed")

        provider = ScoutProvider()
        assert provider.is_available() is False

    @patch("urllib.request.urlopen")
    def test_get_available_models(self, mock_urlopen: Mock) -> None:
        """Test get_available_models returns model list."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value.decode.return_value = json.dumps(
            {"data": [{"id": "llama4:scout"}]}
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        provider = ScoutProvider()
        models = provider.get_available_models()
        assert "llama4:scout" in models

    @patch("urllib.request.urlopen")
    @patch("truth_forge.gateway.providers.scout.get_operational_context")
    def test_complete_success(self, mock_context: Mock, mock_urlopen: Mock) -> None:
        """Test complete returns successful response."""
        mock_context.return_value = 1_000_000

        # Mock availability check (context manager returning status 200 + model list)
        mock_models_body = Mock()
        mock_models_body.status = 200
        mock_models_body.read.return_value.decode.return_value = json.dumps(
            {"data": [{"id": "llama4:scout"}]}
        )
        mock_models_cm = Mock()
        mock_models_cm.__enter__ = Mock(return_value=mock_models_body)
        mock_models_cm.__exit__ = Mock(return_value=False)

        # Mock completion response (context manager returning JSON body)
        mock_completion_body = Mock()
        mock_completion_body.read.return_value.decode.return_value = json.dumps(
            {
                "choices": [{"message": {"content": "Test response"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            }
        )
        mock_completion_cm = Mock()
        mock_completion_cm.__enter__ = Mock(return_value=mock_completion_body)
        mock_completion_cm.__exit__ = Mock(return_value=False)

        # First call = is_available(), second call = complete()
        mock_urlopen.side_effect = [mock_models_cm, mock_completion_cm]

        provider = ScoutProvider()
        request = CompletionRequest(prompt="Test prompt")
        response = provider.complete(request)

        assert response.content == "Test response"
        assert response.provider == ModelProvider.SCOUT
        assert response.input_tokens == 10
        assert response.output_tokens == 5
        assert response.cost == 0.0

    @patch("urllib.request.urlopen")
    def test_complete_not_available_raises_error(self, mock_urlopen: Mock) -> None:
        """Test complete raises error when provider not available."""
        mock_urlopen.side_effect = Exception("Connection failed")

        provider = ScoutProvider()
        request = CompletionRequest(prompt="Test prompt")

        with pytest.raises(ProviderError, match="Scout server not available"):
            provider.complete(request)

    @patch("urllib.request.urlopen")
    @patch("truth_forge.gateway.providers.scout.get_operational_context")
    def test_complete_with_json(self, mock_context: Mock, mock_urlopen: Mock) -> None:
        """Test complete with JSON response format."""
        mock_context.return_value = 1_000_000

        # Mock availability check (context manager returning status 200 + model list)
        mock_models_body = Mock()
        mock_models_body.status = 200
        mock_models_body.read.return_value.decode.return_value = json.dumps(
            {"data": [{"id": "llama4:scout"}]}
        )
        mock_models_cm = Mock()
        mock_models_cm.__enter__ = Mock(return_value=mock_models_body)
        mock_models_cm.__exit__ = Mock(return_value=False)

        # Mock completion response (context manager returning JSON body)
        mock_completion_body = Mock()
        mock_completion_body.read.return_value.decode.return_value = json.dumps(
            {
                "choices": [{"message": {"content": '{"key": "value"}'}}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 3},
            }
        )
        mock_completion_cm = Mock()
        mock_completion_cm.__enter__ = Mock(return_value=mock_completion_body)
        mock_completion_cm.__exit__ = Mock(return_value=False)

        # First call = is_available(), second call = complete()
        mock_urlopen.side_effect = [mock_models_cm, mock_completion_cm]

        provider = ScoutProvider()
        request = CompletionRequest(prompt="Test", as_json=True)
        provider.complete(request)

        # Verify request includes JSON format
        call_args = mock_urlopen.call_args_list[-1]
        request_data = json.loads(call_args[0][0].data.decode())
        assert "response_format" in request_data
        assert request_data["response_format"]["type"] == "json_object"

    @patch("urllib.request.urlopen")
    def test_embed_success(self, mock_urlopen: Mock) -> None:
        """Test embed returns successful response."""
        # Mock availability check (context manager returning status 200 + model list)
        mock_models_body = Mock()
        mock_models_body.status = 200
        mock_models_body.read.return_value.decode.return_value = json.dumps(
            {"data": [{"id": "llama4:scout"}]}
        )
        mock_models_cm = Mock()
        mock_models_cm.__enter__ = Mock(return_value=mock_models_body)
        mock_models_cm.__exit__ = Mock(return_value=False)

        # Mock embedding response (context manager returning JSON body)
        mock_embedding_body = Mock()
        mock_embedding_body.read.return_value.decode.return_value = json.dumps(
            {
                "data": [{"embedding": [0.1, 0.2, 0.3]}],
                "usage": {"total_tokens": 5},
            }
        )
        mock_embedding_cm = Mock()
        mock_embedding_cm.__enter__ = Mock(return_value=mock_embedding_body)
        mock_embedding_cm.__exit__ = Mock(return_value=False)

        # First call = is_available(), second call = embed()
        mock_urlopen.side_effect = [mock_models_cm, mock_embedding_cm]

        provider = ScoutProvider()
        request = EmbeddingRequest(text=["test"], model="llama4:scout")
        response = provider.embed(request)

        assert len(response.embeddings) == 1
        assert response.embeddings[0] == [0.1, 0.2, 0.3]
        assert response.dimensions == 3
        assert response.cost == 0.0

    def test_get_default_model(self) -> None:
        """Test get_default_model returns THE_MODEL."""
        provider = ScoutProvider()
        assert provider.get_default_model() == THE_MODEL

    @patch("urllib.request.urlopen")
    def test_health_check(self, mock_urlopen: Mock) -> None:
        """Test health_check returns status."""
        # Mock availability check
        mock_models_response = Mock()
        mock_models_response.status = 200
        mock_models_response.read.return_value.decode.return_value = json.dumps(
            {"data": [{"id": "llama4:scout"}]}
        )
        mock_urlopen.return_value.__enter__.return_value = mock_models_response

        provider = ScoutProvider()
        health = provider.health_check()

        assert "available" in health
        assert "endpoint" in health
        assert "architecture" in health
        assert "operational" in health
        assert health["architecture"]["context"] == THE_CONTEXT
