"""Unit tests for the KnowledgeService."""

import pytest
from unittest.mock import MagicMock, patch

from truth_forge.services.knowledge.service import KnowledgeService
from truth_forge.services.secret.service import SecretService


@pytest.fixture
def mock_secret_service():
    """Create a mock secret service that passes isinstance checks."""
    return MagicMock(spec=SecretService)


@pytest.fixture
def mock_anthropic_client():
    with patch('anthropic.Anthropic') as mock:
        yield mock


@pytest.fixture
def mock_gemini_client():
    with patch('google.genai.Client') as mock:
        yield mock


@pytest.fixture
def mock_openai_client():
    with patch('openai.OpenAI') as mock:
        yield mock


def test_knowledge_service_initialization():
    """Test that the KnowledgeService initializes correctly."""
    service = KnowledgeService()
    assert service.service_name == "knowledge"
    assert service._default_llm == "claude-sonnet-4-20250514"
    stats = service.get_session_stats()
    assert stats["session_cost"] == 0.0
    assert stats["session_calls"] == 0


def test_knowledge_service_call_claude(mock_secret_service, mock_anthropic_client):
    """Test a successful call to the Claude LLM."""
    mock_secret_service.get_secret.return_value = "fake_claude_key"

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Claude response")]
    mock_response.usage.input_tokens = 10
    mock_response.usage.output_tokens = 20
    mock_anthropic_client.return_value.messages.create.return_value = mock_response

    with patch('truth_forge.services.knowledge.service.get_service', return_value=mock_secret_service):
        service = KnowledgeService(default_llm="claude-sonnet-4-20250514")
        result = service.call_llm("Test prompt")

        assert result["text"] == "Claude response"
        assert result["input_tokens"] == 10
        assert result["output_tokens"] == 20
        assert "cost" in result
        stats = service.get_session_stats()
        assert stats["session_calls"] == 1
        assert stats["session_cost"] > 0


def test_knowledge_service_call_gemini(mock_secret_service, mock_gemini_client):
    """Test a successful call to the Gemini LLM."""
    mock_secret_service.get_secret.return_value = "fake_gemini_key"

    mock_response = MagicMock()
    mock_response.text = "Gemini response"
    # New API: client.models.generate_content()
    mock_gemini_client.return_value.models.generate_content.return_value = mock_response

    with patch('truth_forge.services.knowledge.service.get_service', return_value=mock_secret_service):
        service = KnowledgeService(default_llm="gemini-1.5-pro")
        result = service.call_llm("Test prompt")

        assert result["text"] == "Gemini response"
        assert "cost" in result
        stats = service.get_session_stats()
        assert stats["session_calls"] == 1
        assert stats["session_cost"] > 0


def test_knowledge_service_call_openai(mock_secret_service, mock_openai_client):
    """Test a successful call to the OpenAI LLM."""
    mock_secret_service.get_secret.return_value = "fake_openai_key"

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="OpenAI response"))]
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_openai_client.return_value.chat.completions.create.return_value = mock_response

    with patch('truth_forge.services.knowledge.service.get_service', return_value=mock_secret_service):
        service = KnowledgeService(default_llm="gpt-4-turbo")
        result = service.call_llm("Test prompt")

        assert result["text"] == "OpenAI response"
        assert result["input_tokens"] == 10
        assert result["output_tokens"] == 20
        assert "cost" in result
        stats = service.get_session_stats()
        assert stats["session_calls"] == 1
        assert stats["session_cost"] > 0


def test_process_record_creates_knowledge_atom(mock_secret_service):
    """Test that the process method creates a knowledge atom."""
    mock_secret_service.get_secret.return_value = "fake_claude_key"

    with patch('truth_forge.services.knowledge.service.get_service', return_value=mock_secret_service):
        service = KnowledgeService()
        with patch.object(service, 'call_llm') as mock_call_llm:
            mock_call_llm.return_value = {
                "text": '{"summary": "Test summary"}',
                "input_tokens": 10,
                "output_tokens": 20,
                "cost": 0.00033,
                "llm_model": "claude-sonnet-4-20250514",
            }

            record = {"content": "This is a test."}
            processed_record = service.process(record)

            assert processed_record["knowledge_status"] == "processed"
            assert "extraction" in processed_record
            assert processed_record["extraction"]["summary"] == "Test summary"
            assert "llm_model" in processed_record
            assert "llm_cost" in processed_record
            assert "llm_tokens" in processed_record