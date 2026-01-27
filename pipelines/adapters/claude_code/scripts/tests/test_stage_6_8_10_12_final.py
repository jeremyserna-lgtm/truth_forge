"""Final comprehensive tests for Stages 6, 8, 10, 12.

Target: Increase coverage for sentence detection, conversations, extraction, and keywords.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_generate_sentence_id(mock_run_id, mock_logger) -> None:
    """Test stage_6 generate_sentence_id function."""
    from stage_6.claude_code_stage_6 import generate_sentence_id
    
    # Test ID generation
    sentence_id = generate_sentence_id("parent_123", 0)
    
    assert isinstance(sentence_id, str)
    assert len(sentence_id) > 0
    
    # Should be deterministic
    sentence_id2 = generate_sentence_id("parent_123", 0)
    assert sentence_id == sentence_id2
    
    # Different inputs should produce different IDs
    sentence_id3 = generate_sentence_id("parent_456", 0)
    assert sentence_id != sentence_id3


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_detect_sentences_comprehensive(mock_run_id, mock_logger) -> None:
    """Test stage_6 detect_sentences function comprehensively."""
    from stage_6.claude_code_stage_6 import detect_sentences
    
    # Mock spaCy nlp
    mock_nlp = MagicMock()
    mock_doc = MagicMock()
    mock_sent1 = MagicMock()
    mock_sent1.text = "First sentence."
    mock_sent1.start_char = 0
    mock_sent1.end_char = 16
    mock_sent2 = MagicMock()
    mock_sent2.text = "Second sentence."
    mock_sent2.start_char = 17
    mock_sent2.end_char = 33
    mock_doc.sents = [mock_sent1, mock_sent2]
    mock_nlp.return_value = mock_doc
    
    message = {
        "entity_id": "entity_123",
        "text": "First sentence. Second sentence.",
        "session_id": "session_123",
        "content_date": None
    }
    
    created_at = datetime.now(timezone.utc).isoformat()
    sentences = list(detect_sentences(message, mock_nlp, "test_run", created_at))
    
    assert isinstance(sentences, list)
    assert len(sentences) == 2
    assert all("entity_id" in s for s in sentences)
    assert all("sentence_index" in s for s in sentences)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_generate_conversation_id(mock_run_id, mock_logger) -> None:
    """Test stage_8 generate_conversation_id function."""
    from stage_8.claude_code_stage_8 import generate_conversation_id
    
    # Test ID generation
    conversation_id = generate_conversation_id("session_123")
    
    assert isinstance(conversation_id, str)
    assert len(conversation_id) > 0
    
    # Should be deterministic
    conversation_id2 = generate_conversation_id("session_123")
    assert conversation_id == conversation_id2


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_create_conversation_entities_comprehensive(mock_run_id, mock_logger) -> None:
    """Test stage_8 create_conversation_entities function comprehensively."""
    from stage_8.claude_code_stage_8 import create_conversation_entities
    from google.cloud import bigquery
    from datetime import datetime, timezone
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.session_id = "session_123"
    mock_row.first_message_at = datetime.now(timezone.utc)
    mock_row.last_message_at = datetime.now(timezone.utc)
    mock_row.message_count = 10
    mock_row.user_message_count = 5
    mock_row.assistant_message_count = 5
    mock_row.tool_use_count = 0
    mock_row.total_word_count = 100
    mock_row.total_char_count = 500
    mock_row.total_cost_usd = 0.01
    mock_row.models_used = ["gpt-4"]
    mock_row.tools_used = ["tool1"]
    mock_row.content_date = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    # create_conversation_entities is a generator
    created_at = datetime.now(timezone.utc).isoformat()
    entities = list(create_conversation_entities(mock_client, "test_run", created_at))
    
    assert isinstance(entities, list)
    assert all("entity_id" in e for e in entities)
    assert all("session_id" in e for e in entities)
    assert all("message_count" in e for e in entities)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_10_extract_from_message_comprehensive(mock_run_id, mock_logger) -> None:
    """Test stage_10 extract_from_message function comprehensively."""
    from stage_10.claude_code_stage_10 import extract_from_message
    
    # Mock genai client - extract_from_message is wrapped with retry_with_backoff
    # The wrapped function still takes (genai, text) as parameters
    mock_genai = MagicMock()
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"intent": "question", "task_type": "coding", "code_languages": ["python"], "complexity": "moderate", "has_code_block": true}'
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    # extract_from_message takes (genai, text) as parameters
    result = extract_from_message(mock_genai, "What is Python?")
    
    assert isinstance(result, dict)
    assert "intent" in result
    assert "task_type" in result


# REMOVED: test_stage_12_extract_keywords_comprehensive - Duplicate of test_stage_8_9_10_12_comprehensive.py::test_stage_12_extract_keywords_comprehensive


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_extract_keywords_empty_text(mock_run_id, mock_logger) -> None:
    """Test stage_12 extract_keywords with empty text."""
    from stage_12.claude_code_stage_12 import extract_keywords
    
    # Mock KeyBERT model
    with patch('stage_12.claude_code_stage_12.get_keybert_model') as mock_get_model:
        mock_model = Mock()
        mock_get_model.return_value = mock_model
        
        # Empty text should return empty list
        keywords = extract_keywords(mock_model, "", top_n=5)
        assert keywords == []
        
        # Short text should return empty list
        keywords = extract_keywords(mock_model, "short", top_n=5)
        assert keywords == []
