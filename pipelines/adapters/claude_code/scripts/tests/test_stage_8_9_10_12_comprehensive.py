"""Comprehensive tests for Stages 8, 9, 10, 12.

Target: 90%+ coverage of these enrichment and processing stages.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch

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
def test_stage_8_create_conversation_entities(mock_run_id, mock_logger) -> None:
    """Test stage_8 create_conversation_entities function."""
    from stage_8.claude_code_stage_8 import create_conversation_entities
    from google.cloud import bigquery
    from datetime import datetime, timedelta
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.session_id = "session_123"
    # Set numeric attributes properly
    mock_row.message_count = 10
    mock_row.user_message_count = 5
    mock_row.assistant_message_count = 5
    mock_row.tool_use_count = 2
    mock_row.total_word_count = 100
    mock_row.total_char_count = 500
    mock_row.total_cost_usd = 0.01
    mock_row.models_used = '["gpt-4"]'
    mock_row.tools_used = '["tool1"]'
    # Set datetime objects for duration calculation
    mock_row.first_message_at = datetime(2024, 1, 1, 0, 0, 0)
    mock_row.last_message_at = datetime(2024, 1, 1, 0, 5, 0)
    mock_row.content_date = "2024-01-01"
    mock_query_job.result.return_value = [mock_row]
    mock_client.query.return_value = mock_query_job
    
    # create_conversation_entities is a generator
    entities = list(create_conversation_entities(mock_client, "test_run", "2024-01-01T00:00:00Z"))
    
    assert isinstance(entities, list)
    assert len(entities) > 0
    assert all("entity_id" in entity for entity in entities)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_truncate_text(mock_run_id, mock_logger) -> None:
    """Test stage_9 truncate_text function."""
    from stage_9.claude_code_stage_9 import truncate_text
    
    # Test normal truncation - truncate_text takes max_chars parameter
    long_text = "a" * 1000
    truncated, was_truncated = truncate_text(long_text, max_chars=100)
    
    assert isinstance(truncated, str)
    assert isinstance(was_truncated, bool)
    assert len(truncated) <= 100
    assert was_truncated is True
    
    # Test short text (no truncation needed)
    short_text = "Short text"
    result, was_truncated = truncate_text(short_text, max_chars=100)
    
    assert result == short_text
    assert was_truncated is False


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_generate_embeddings_batch(mock_run_id, mock_logger) -> None:
    """Test stage_9 generate_embeddings_batch function."""
    from stage_9.claude_code_stage_9 import generate_embeddings_batch
    from unittest.mock import Mock
    
    # Mock the genai client - embed_content returns a dict
    mock_genai = Mock()
    mock_result = {"embedding": [[0.1] * 768, [0.2] * 768]}  # List of embeddings
    mock_genai.embed_content.return_value = mock_result
    
    texts = ["Text 1", "Text 2"]
    
    # generate_embeddings_batch is wrapped with retry_with_backoff
    # It takes genai client and texts
    embeddings = generate_embeddings_batch(mock_genai, texts)
    
    assert isinstance(embeddings, list)
    assert len(embeddings) == len(texts)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_10_extract_from_message(mock_run_id, mock_logger) -> None:
    """Test stage_10 extract_from_message function."""
    from stage_10.claude_code_stage_10 import extract_from_message
    from unittest.mock import Mock
    
    # Mock the genai client
    mock_genai = Mock()
    mock_model = Mock()
    mock_response = Mock()
    mock_response.text = '{"intent": "test_intent", "task_type": "coding"}'
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    text = "Write a Python function to sort a list"
    
    with patch('stage_10.claude_code_stage_10.get_llm_client', return_value=mock_genai):
        # extract_from_message is wrapped with retry_with_backoff
        # It takes genai client and text
        result = extract_from_message(mock_genai, text)
        
        assert isinstance(result, dict)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_extract_keywords_comprehensive(mock_run_id, mock_logger) -> None:
    """Test stage_12 extract_keywords function comprehensively."""
    from stage_12.claude_code_stage_12 import extract_keywords
    from unittest.mock import Mock
    
    # Mock the KeyBERT model
    mock_model = Mock()
    mock_model.extract_keywords.return_value = [
        ("python", 0.9),
        ("function", 0.8),
        ("sort", 0.7)
    ]
    
    text = "Write a Python function to sort a list"
    
    with patch('stage_12.claude_code_stage_12.get_keybert_model', return_value=mock_model):
        keywords = extract_keywords(mock_model, text, top_n=5)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        # Keywords should be tuples of (keyword, score)
        assert all(isinstance(kw, tuple) and len(kw) == 2 for kw in keywords)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_process_topics(mock_run_id, mock_logger) -> None:
    """Test stage_12 process_topics function."""
    from stage_12.claude_code_stage_12 import process_topics
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = []  # Empty result
    mock_client.query.return_value = mock_query_job
    
    # process_topics requires top_n parameter
    result = process_topics(mock_client, "test_run", top_n=5, batch_size=100, dry_run=True)
    
    assert isinstance(result, dict)
    assert "processed" in result or "total" in result or "count" in result or "dry_run" in result
