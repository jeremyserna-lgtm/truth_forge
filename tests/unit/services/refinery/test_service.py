"""Tests for refinery service module."""

from __future__ import annotations

from unittest.mock import Mock, patch

from truth_forge.services.refinery.service import LLMRefineryService, OllamaClient, RefineryConfig


class TestRefineryConfig:
    """Test RefineryConfig dataclass."""

    def test_defaults(self) -> None:
        """Test default configuration values."""
        config = RefineryConfig()
        assert config.ollama_host == "http://localhost:11434"
        assert config.model == "qwen2.5-coder:32b"
        assert config.timeout == 120.0
        assert config.max_retries == 3
        assert config.min_level == 5
        assert config.enable_enrichments is True

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = RefineryConfig(
            ollama_host="http://custom:11434",
            model="custom-model",
            min_level=2,
        )
        assert config.ollama_host == "http://custom:11434"
        assert config.model == "custom-model"
        assert config.min_level == 2


class TestOllamaClient:
    """Test OllamaClient class."""

    def test_init(self) -> None:
        """Test OllamaClient initialization."""
        config = RefineryConfig()
        mock_logger = Mock()
        client = OllamaClient(config, mock_logger)
        assert client.config == config
        assert client.logger == mock_logger
        assert client._client is None

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_ensure_client(self, mock_client_class: Mock) -> None:
        """Test client lazy initialization."""
        config = RefineryConfig()
        mock_logger = Mock()
        client = OllamaClient(config, mock_logger)

        # First call creates client
        client1 = client._ensure_client()
        client2 = client._ensure_client()

        assert client1 is client2  # Same instance
        assert mock_client_class.call_count == 1

    def test_close(self) -> None:
        """Test closing client."""
        config = RefineryConfig()
        mock_logger = Mock()
        client = OllamaClient(config, mock_logger)

        # Create client first
        mock_http_client = Mock()
        client._client = mock_http_client

        client.close()

        mock_http_client.close.assert_called_once()
        assert client._client is None

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_complete_success(self, mock_client_class: Mock) -> None:
        """Test successful completion."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Test response"}
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        config = RefineryConfig()
        mock_logger = Mock()
        client = OllamaClient(config, mock_logger)

        result = client.complete("Test prompt")

        assert result == "Test response"
        mock_client.post.assert_called_once()

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_complete_retries_on_timeout(self, mock_client_class: Mock) -> None:
        """Test completion retries on timeout."""
        import httpx

        mock_client = Mock()
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")
        mock_client_class.return_value = mock_client

        config = RefineryConfig(max_retries=2)
        mock_logger = Mock()
        client = OllamaClient(config, mock_logger)

        result = client.complete("Test prompt")

        # Should return empty string after retries exhausted
        assert result == ""
        assert mock_client.post.call_count == 2

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_extract_json_array(self, mock_client_class: Mock) -> None:
        """Test extracting JSON array."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"response": 'Text before [{"key": "value"}] text after'}
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        config = RefineryConfig()
        mock_logger = Mock()
        client = OllamaClient(config, mock_logger)

        result = client.extract_json("Test prompt")

        assert isinstance(result, list)
        assert result[0]["key"] == "value"

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_extract_json_object(self, mock_client_class: Mock) -> None:
        """Test extracting JSON object."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"response": 'Text before {"key": "value"} text after'}
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        config = RefineryConfig()
        mock_logger = Mock()
        client = OllamaClient(config, mock_logger)

        result = client.extract_json("Test prompt")

        assert isinstance(result, dict)
        assert result["key"] == "value"

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_extract_json_not_found(self, mock_client_class: Mock) -> None:
        """Test extract_json when no JSON found."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"response": "No JSON here"}
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        config = RefineryConfig()
        mock_logger = Mock()
        client = OllamaClient(config, mock_logger)

        result = client.extract_json("Test prompt")

        assert result is None


class TestLLMRefineryService:
    """Test LLMRefineryService class."""

    @patch("truth_forge.services.refinery.service.BaseService.__init__")
    def test_init(self, mock_base_init: Mock) -> None:
        """Test LLMRefineryService initialization."""
        mock_base_init.return_value = None

        config = RefineryConfig()
        service = LLMRefineryService(config)

        assert service._config == config
        assert service._ollama is None
        assert service._identity is None
        assert service.service_name == "refinery"

    @patch("truth_forge.services.refinery.service.BaseService.__init__")
    @patch("truth_forge.services.refinery.service.get_service")
    def test_on_startup(self, mock_get_service: Mock, mock_base_init: Mock) -> None:
        """Test service startup."""
        mock_base_init.return_value = None

        # Mock identity service
        mock_identity = Mock()
        mock_identity.generate_run_id.return_value = "run-123"
        mock_get_service.side_effect = [mock_identity, Mock()]  # identity, mediator

        config = RefineryConfig()
        service = LLMRefineryService(config)
        service._logger = Mock()  # Mock logger
        service.on_startup()

        assert service._identity == mock_identity
        assert service._run_id == "run-123"
        assert service._ollama is not None

    @patch("truth_forge.services.refinery.service.BaseService.__init__")
    def test_on_shutdown(self, mock_base_init: Mock) -> None:
        """Test service shutdown."""
        mock_base_init.return_value = None

        config = RefineryConfig()
        service = LLMRefineryService(config)
        service._logger = Mock()

        # Create mock ollama client
        mock_ollama = Mock()
        service._ollama = mock_ollama

        service.on_shutdown()

        mock_ollama.close.assert_called_once()

    @patch("truth_forge.services.refinery.service.BaseService.__init__")
    def test_process_conversation(self, mock_base_init: Mock) -> None:
        """Test processing a conversation."""
        mock_base_init.return_value = None

        config = RefineryConfig()
        service = LLMRefineryService(config)
        service._logger = Mock()
        service._mediator = Mock()

        # Mock ollama client
        mock_ollama = Mock()
        mock_ollama.extract_json.return_value = []  # No entities extracted
        service._ollama = mock_ollama

        record = {
            "uuid": "conv-123",
            "messages": [{"role": "user", "content": "Test"}],
        }

        result = service.process(record)

        assert result["conversation_id"] == "conv-123"
        assert "status" in result

    @patch("truth_forge.services.refinery.service.BaseService.__init__")
    def test_generate_entity_id_with_identity(self, mock_base_init: Mock) -> None:
        """Test entity ID generation with identity service."""
        mock_base_init.return_value = None

        config = RefineryConfig()
        service = LLMRefineryService(config)
        service._logger = Mock()

        mock_identity = Mock()
        mock_identity.generate_entity_id.return_value = "entity-123"
        service._identity = mock_identity

        entity_id = service._generate_entity_id("msg", "content", "parent-456")

        assert entity_id == "entity-123"
        mock_identity.generate_entity_id.assert_called_once()

    @patch("truth_forge.services.refinery.service.BaseService.__init__")
    def test_generate_entity_id_fallback(self, mock_base_init: Mock) -> None:
        """Test entity ID generation fallback."""
        mock_base_init.return_value = None

        config = RefineryConfig()
        service = LLMRefineryService(config)
        service._logger = Mock()
        service._identity = None  # No identity service

        entity_id = service._generate_entity_id("msg", "content", "parent")

        assert entity_id.startswith("msg:")
        assert len(entity_id) > 0
