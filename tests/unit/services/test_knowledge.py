"""Unit tests for knowledge service."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.services.factory import ServiceFactory
from truth_forge.services.knowledge.service import (
    CostLimitError,
    KnowledgeService,
    LLMClientFactory,
    LLMError,
)
from truth_forge.services.secret import SecretService


@pytest.fixture(autouse=True)
def clean_factory() -> Any:
    """Clean factory before and after each test."""
    ServiceFactory.clear()
    yield
    ServiceFactory.clear()


@pytest.fixture
def temp_services_dir(tmp_path: Path) -> Path:
    """Create temporary services directory."""
    services_dir = tmp_path / "services"
    services_dir.mkdir(parents=True)
    return services_dir


@pytest.fixture
def mock_anthropic_response() -> MagicMock:
    """Create mock anthropic response."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"summary": "Test summary", "key_facts": ["fact1"], "entities": ["entity1"], "topics": ["topic1"], "sentiment": "neutral", "confidence": 0.9}')]
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50
    return mock_response


class TestKnowledgeService:
    """Tests for KnowledgeService class."""

    def test_service_name(self) -> None:
        """Test service_name is set correctly."""
        assert KnowledgeService.service_name == "knowledge"

    def test_init_sets_defaults(self, temp_services_dir: Path) -> None:
        """Test initialization sets default values."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService()

            assert service._default_llm == "claude-sonnet-4-20250514"
            assert service._max_cost == 0.50
            assert service._session_cost == 0.0
            assert service._session_calls == 0

    def test_init_custom_model(self, temp_services_dir: Path) -> None:
        """Test initialization with custom model."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService(default_llm="claude-3-haiku-20240307")

            assert service._default_llm == "claude-3-haiku-20240307"

    def test_init_custom_cost_limit(self, temp_services_dir: Path) -> None:
        """Test initialization with custom cost limit."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService(max_cost_per_session=1.0)

            assert service._max_cost == 1.0


class TestKnowledgeServiceCostEstimation:
    """Tests for cost estimation."""

    def test_estimate_cost_sonnet(self, temp_services_dir: Path) -> None:
        """Test cost estimation for Sonnet model."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService()

            # 1000 input + 500 output tokens
            cost = service._estimate_cost(1000, 500)

            # (1000/1M * 3.00) + (500/1M * 15.00) = 0.003 + 0.0075 = 0.0105
            assert abs(cost - 0.0105) < 0.0001

    def test_estimate_cost_haiku(self, temp_services_dir: Path) -> None:
        """Test cost estimation for Haiku model."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService(default_llm="claude-3-haiku-20240307")

            # 1000 input + 500 output tokens
            cost = service._estimate_cost(1000, 500)

            # (1000/1M * 0.25) + (500/1M * 1.25) = 0.00025 + 0.000625 = 0.000875
            assert abs(cost - 0.000875) < 0.0001


class TestKnowledgeServiceCostLimits:
    """Tests for cost limit checking."""

    def test_check_cost_limit_under_limit(self, temp_services_dir: Path) -> None:
        """Test cost check passes when under limit."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService(max_cost_per_session=1.0)

            # Should not raise
            service._check_cost_limit(0.5)

    def test_check_cost_limit_over_limit(self, temp_services_dir: Path) -> None:
        """Test cost check raises when over limit."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService(max_cost_per_session=0.1)
            service._session_cost = 0.08

            with pytest.raises(CostLimitError, match="exceed session cost limit"):
                service._check_cost_limit(0.05)

    def test_check_cost_limit_calls_exceeded(self, temp_services_dir: Path) -> None:
        """Test cost check raises when calls exceeded."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService()
            service._session_calls = 100  # MAX_CALLS_PER_SESSION

            with pytest.raises(CostLimitError, match="call limit reached"):
                service._check_cost_limit(0.001)


class TestKnowledgeServiceProcess:
    """Tests for record processing."""

    def test_process_empty_content(self, temp_services_dir: Path) -> None:
        """Test process handles empty content."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService()
            result = service.process({"content": ""})

            assert result["knowledge_status"] == "skipped"
            assert result["knowledge_reason"] == "empty_content"

    def test_process_no_content(self, temp_services_dir: Path) -> None:
        """Test process handles missing content."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService()
            result = service.process({})

            assert result["knowledge_status"] == "skipped"

    def test_process_generates_content_hash(
        self, temp_services_dir: Path, mock_anthropic_response: MagicMock
    ) -> None:
        """Test process generates content hash."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService()

            # Mock the LLM call
            with patch.object(service, "call_llm") as mock_call:
                mock_call.return_value = {
                    "text": '{"summary": "test", "key_facts": [], "entities": [], "topics": [], "sentiment": "neutral", "confidence": 0.9}',
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "cost": 0.001,
                    "llm_model": "claude-sonnet-4-20250514",
                }

                result = service.process({"content": "Test content"})

                assert "content_hash" in result
                assert len(result["content_hash"]) == 32

    def test_process_handles_cost_limit(self, temp_services_dir: Path) -> None:
        """Test process handles cost limit gracefully."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService()

            # Mock call_llm to raise CostLimitError
            with patch.object(service, "call_llm") as mock_call:
                mock_call.side_effect = CostLimitError("Cost limit exceeded")

                result = service.process({"content": "Test content"})

                assert result["knowledge_status"] == "deferred"

    def test_process_handles_llm_error(self, temp_services_dir: Path) -> None:
        """Test process handles LLM errors gracefully."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService()

            # Mock call_llm to raise LLMError
            with patch.object(service, "call_llm") as mock_call:
                mock_call.side_effect = LLMError("API failed")

                result = service.process({"content": "Test content"})

                assert result["knowledge_status"] == "failed"
                assert "API failed" in result["knowledge_error"]


class TestKnowledgeServiceLLMCall:
    """Tests for LLM calling."""

    def test_call_llm_success(
        self, temp_services_dir: Path, mock_anthropic_response: MagicMock
    ) -> None:
        """Test successful LLM call."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService()

            # Mock the client factory
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_anthropic_response

            with patch.object(
                LLMClientFactory, "get_anthropic_client", return_value=mock_client
            ):
                result = service.call_llm("Test prompt")

                assert "text" in result
                assert result["input_tokens"] == 100
                assert result["output_tokens"] == 50
                assert service._session_calls == 1

    def test_call_llm_tracks_cost(
        self, temp_services_dir: Path, mock_anthropic_response: MagicMock
    ) -> None:
        """Test LLM call tracks session cost."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService()

            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_anthropic_response

            with patch.object(
                LLMClientFactory, "get_anthropic_client", return_value=mock_client
            ):
                service.call_llm("Test prompt")

                assert service._session_cost > 0


class TestKnowledgeServiceSessionStats:
    """Tests for session statistics."""

    def test_get_session_stats(self, temp_services_dir: Path) -> None:
        """Test get_session_stats returns correct data."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService(max_cost_per_session=1.0)
            service._session_cost = 0.25
            service._session_calls = 5

            stats = service.get_session_stats()

            assert stats["session_cost"] == 0.25
            assert stats["session_calls"] == 5
            assert stats["max_cost"] == 1.0
            assert stats["remaining_budget"] == 0.75

    def test_reset_session(self, temp_services_dir: Path) -> None:
        """Test reset_session clears counters."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService()
            service._session_cost = 0.5
            service._session_calls = 10

            service.reset_session()

            assert service._session_cost == 0.0
            assert service._session_calls == 0


class TestKnowledgeServiceSchema:
    """Tests for schema creation."""

    def test_create_schema(self, temp_services_dir: Path) -> None:
        """Test create_schema returns valid SQL."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = KnowledgeService()
            schema = service.create_schema()

            assert "CREATE TABLE IF NOT EXISTS knowledge_records" in schema
            assert "id VARCHAR PRIMARY KEY" in schema
            assert "data JSON NOT NULL" in schema
            assert "content_hash VARCHAR" in schema
            assert "knowledge_status VARCHAR" in schema


class TestKnowledgeServiceClient:
    """Tests for LLM client initialization."""

    def test_get_anthropic_client_no_key(self) -> None:
        """Test client raises when no API key."""
        # Reset cached clients
        LLMClientFactory._anthropic_client = None
        LLMClientFactory._secret_service = None

        # Mock the secret service with spec to pass isinstance check
        mock_secret_service = MagicMock(spec=SecretService)
        mock_secret_service.get_secret.return_value = None

        with patch(
            "truth_forge.services.knowledge.service.get_service",
            return_value=mock_secret_service,
        ):
            with pytest.raises(LLMError, match="ANTHROPIC_API_KEY not configured"):
                LLMClientFactory.get_anthropic_client()

    def test_get_anthropic_client_with_key(self) -> None:
        """Test client initializes with API key."""
        # Reset cached clients
        LLMClientFactory._anthropic_client = None
        LLMClientFactory._secret_service = None

        # Mock the secret service with spec to pass isinstance check
        mock_secret_service = MagicMock(spec=SecretService)
        mock_secret_service.get_secret.return_value = "test-api-key"

        with patch(
            "truth_forge.services.knowledge.service.get_service",
            return_value=mock_secret_service,
        ):
            with patch("anthropic.Anthropic") as mock_anthropic:
                LLMClientFactory.get_anthropic_client()

                mock_anthropic.assert_called_once_with(api_key="test-api-key")


class TestKnowledgeServiceRegistration:
    """Tests for factory registration."""

    def test_knowledge_registered(self) -> None:
        """Test knowledge service can be registered."""
        ServiceFactory.register("knowledge", KnowledgeService)

        assert ServiceFactory.is_registered("knowledge")

    def test_get_knowledge_service(self, temp_services_dir: Path) -> None:
        """Test getting knowledge service via factory."""
        from truth_forge.services.factory import get_service

        ServiceFactory.register("knowledge", KnowledgeService)

        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = get_service("knowledge")

            assert isinstance(service, KnowledgeService)
            assert service.service_name == "knowledge"
