"""Expanded tests for Stages 6, 10, 12, 16.

Target: Increase coverage for these lower-coverage stages.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

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
def test_stage_6_create_stage_6_table(mock_run_id, mock_logger) -> None:
    """Test stage_6 create_stage_6_table function."""
    from stage_6.claude_code_stage_6 import create_stage_6_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_6_table(mock_client)
    
    assert result is not None


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_detect_sentences_expanded(mock_run_id, mock_logger) -> None:
    """Test stage_6 detect_sentences function with expanded coverage."""
    from stage_6.claude_code_stage_6 import detect_sentences
    from datetime import datetime, timezone
    
    # Mock nlp object
    mock_nlp = MagicMock()
    mock_doc = MagicMock()
    mock_sent = MagicMock()
    mock_sent.text = "Test sentence."
    mock_sent.start_char = 0
    mock_sent.end_char = 15
    mock_doc.sents = [mock_sent]
    mock_nlp.return_value = mock_doc
    
    message = {
        "entity_id": "entity_123",
        "text": "Test sentence.",
        "session_id": "session_123",
        "content_date": "2024-01-01"
    }
    
    # detect_sentences is a generator
    results = list(detect_sentences(message, mock_nlp, "test_run", datetime.now(timezone.utc).isoformat()))
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert all("entity_id" in r for r in results)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_10_create_stage_10_table(mock_run_id, mock_logger) -> None:
    """Test stage_10 create_stage_10_table function."""
    from stage_10.claude_code_stage_10 import create_stage_10_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_10_table(mock_client)
    
    assert result is not None


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_10_process_extractions(mock_run_id, mock_logger) -> None:
    """Test stage_10 process_extractions function."""
    from stage_10.claude_code_stage_10 import process_extractions
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.text = "Test message"
    mock_row.session_id = "session_123"
    mock_row.content_date = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    # Mock genai client
    with patch('stage_10.claude_code_stage_10.get_llm_client') as mock_get_llm:
        mock_genai = MagicMock()
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"intent": "question", "task_type": "coding"}'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_get_llm.return_value = mock_genai
        
        result = process_extractions(mock_client, "test_run", batch_size=50, dry_run=True)
        
        assert isinstance(result, dict)
        assert "input_messages" in result or "extractions_completed" in result or "dry_run" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_create_stage_12_table(mock_run_id, mock_logger) -> None:
    """Test stage_12 create_stage_12_table function."""
    from stage_12.claude_code_stage_12 import create_stage_12_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_12_table(mock_client)
    
    assert result is not None


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_process_topics_expanded(mock_run_id, mock_logger) -> None:
    """Test stage_12 process_topics function with expanded coverage."""
    from stage_12.claude_code_stage_12 import process_topics
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.text = "This is a test message for keyword extraction."
    mock_row.session_id = "session_123"
    mock_row.content_date = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    # Mock KeyBERT model
    with patch('stage_12.claude_code_stage_12.get_keybert_model') as mock_get_model:
        mock_model = Mock()
        mock_model.extract_keywords.return_value = [("keyword1", 0.9), ("keyword2", 0.8)]
        mock_get_model.return_value = mock_model
        
        result = process_topics(mock_client, "test_run", batch_size=50, top_n=5, dry_run=True)
        
        assert isinstance(result, dict)
        assert "input_messages" in result or "topics_extracted" in result or "dry_run" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_ensure_entity_unified_table(mock_run_id, mock_logger) -> None:
    """Test stage_16 ensure_entity_unified_table function."""
    from stage_16.claude_code_stage_16 import ensure_entity_unified_table
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    # First call raises NotFound, second returns table
    mock_client.get_table.side_effect = [NotFound("Table not found"), mock_table]
    mock_client.create_table.return_value = mock_table
    
    result = ensure_entity_unified_table(mock_client)
    
    assert result is not None


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_promote_entities(mock_run_id, mock_logger) -> None:
    """Test stage_16 promote_entities function."""
    from stage_16.claude_code_stage_16 import promote_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.parent_id = None
    mock_row.source_name = "claude_code"
    mock_row.source_pipeline = "claude_code"
    mock_row.level = 1
    mock_row.text = "Test message"
    mock_row.role = "user"
    mock_row.message_type = "message"
    mock_row.message_index = 0
    mock_row.word_count = 2
    mock_row.char_count = 12
    mock_row.model = None
    mock_row.cost_usd = None
    mock_row.tool_name = None
    mock_row.embedding = None
    mock_row.embedding_model = None
    mock_row.embedding_dimension = None
    mock_row.primary_emotion = None
    mock_row.primary_emotion_score = None
    mock_row.emotions_detected = None
    mock_row.all_emotion_scores = None
    mock_row.intent = None
    mock_row.task_type = None
    mock_row.code_languages = None
    mock_row.complexity = None
    mock_row.has_code_block = None
    mock_row.top_keyword = None
    mock_row.top_keyword_score = None
    mock_row.keywords = None
    mock_row.keywords_with_scores = None
    mock_row.session_id = "session_123"
    mock_row.content_date = None
    mock_row.timestamp_utc = None
    mock_row.created_at = "2024-01-01T00:00:00Z"
    mock_row.run_id = "test_run"
    mock_row.validation_status = "PASSED"
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    # Mock get_existing_entity_ids
    with patch('stage_16.claude_code_stage_16.get_existing_entity_ids', return_value=set()):
        result = promote_entities(mock_client, "test_run", include_warnings=True, dry_run=True)
        
        assert isinstance(result, dict)
        assert "eligible_entities" in result or "promoted_entities" in result or "dry_run" in result
