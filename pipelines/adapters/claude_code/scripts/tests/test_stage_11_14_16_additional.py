"""Additional comprehensive tests for Stages 11, 14, 16.

Target: Increase coverage for sentiment, aggregation, and promotion stages.
Focus on edge cases, error paths, and uncovered functions.
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


# Stage 11 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_create_stage_11_table(mock_run_id, mock_logger) -> None:
    """Test stage_11 create_stage_11_table function."""
    from stage_11.claude_code_stage_11 import create_stage_11_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_11_table(mock_client)
    
    assert result is not None
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_process_sentiment_batch_edge_cases(mock_run_id, mock_logger) -> None:
    """Test stage_11 process_sentiment_batch with edge cases."""
    from stage_11.claude_code_stage_11 import process_sentiment_batch
    
    # Mock classifier that returns predictions
    mock_classifier = Mock()
    mock_classifier.return_value = [
        [
            {"label": "POSITIVE", "score": 0.9},
            {"label": "NEGATIVE", "score": 0.1}
        ],
        [
            {"label": "NEUTRAL", "score": 0.5},
            {"label": "POSITIVE", "score": 0.3}
        ]
    ]
    
    texts = ["Great!", "Okay"]
    results = process_sentiment_batch(mock_classifier, texts, threshold=0.3)
    
    assert isinstance(results, list)
    assert len(results) == len(texts)
    assert all("primary_emotion" in r for r in results)
    assert all("primary_score" in r for r in results)
    assert all("emotions_detected" in r for r in results)
    assert all("all_scores" in r for r in results)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_process_sentiment_with_data(mock_run_id, mock_logger) -> None:
    """Test stage_11 process_sentiment with actual data processing."""
    from stage_11.claude_code_stage_11 import process_sentiment
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.text = "This is a test sentence with enough content."
    mock_row.session_id = "session_123"
    mock_row.content_date = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    # Mock get_sentiment_pipeline
    with patch('stage_11.claude_code_stage_11.get_sentiment_pipeline') as mock_get_pipeline:
        mock_pipeline = Mock()
        mock_pipeline.return_value = [
            [
                {"label": "POSITIVE", "score": 0.9},
                {"label": "NEGATIVE", "score": 0.1}
            ]
        ]
        mock_get_pipeline.return_value = mock_pipeline
        
        result = process_sentiment(mock_client, "test_run", batch_size=10, threshold=0.3, dry_run=False)
        
        assert isinstance(result, dict)
        assert "input_sentences" in result
        assert "sentiments_analyzed" in result
        assert result["dry_run"] is False


# Stage 14 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_14_create_stage_14_table(mock_run_id, mock_logger) -> None:
    """Test stage_14 create_stage_14_table function."""
    from stage_14.claude_code_stage_14 import create_stage_14_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_14_table(mock_client)
    
    assert result is not None
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_14_aggregate_entities_with_data(mock_run_id, mock_logger) -> None:
    """Test stage_14 aggregate_entities with actual data processing."""
    from stage_14.claude_code_stage_14 import aggregate_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    
    # Mock count query for dry_run=False
    mock_query_job = Mock()
    mock_insert_job = Mock()
    mock_count_job = Mock()
    
    # Count query result
    mock_count_row = Mock()
    mock_count_row.cnt = 5
    mock_count_job.result.return_value = iter([mock_count_row])
    
    # Insert job (for actual aggregation)
    mock_insert_job.result.return_value = None  # Insert completes
    
    # Query returns insert job
    def query_side_effect(query_str):
        if "INSERT INTO" in query_str:
            return mock_insert_job
        elif "COUNT(*)" in query_str:
            return mock_count_job
        return mock_query_job
    
    mock_client.query.side_effect = query_side_effect
    
    result = aggregate_entities(mock_client, "test_run", batch_size=100, dry_run=False)
    
    assert isinstance(result, dict)
    assert "messages_aggregated" in result
    assert result["dry_run"] is False


# Stage 16 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_ensure_entity_unified_table_exists(mock_run_id, mock_logger) -> None:
    """Test stage_16 ensure_entity_unified_table when table already exists."""
    from stage_16.claude_code_stage_16 import ensure_entity_unified_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    # When table exists, get_table returns it, create_table is called with exists_ok=True
    mock_client.get_table.return_value = mock_table
    mock_client.create_table.return_value = mock_table
    
    result = ensure_entity_unified_table(mock_client)
    
    assert result is not None
    # create_table is called with exists_ok=True, so it may be called even if table exists
    # The important thing is that we get a table back
    assert result == mock_table


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_get_existing_entity_ids_empty(mock_run_id, mock_logger) -> None:
    """Test stage_16 get_existing_entity_ids when table is empty."""
    from stage_16.claude_code_stage_16 import get_existing_entity_ids
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])  # Empty result
    mock_client.query.return_value = mock_query_job
    
    existing_ids = get_existing_entity_ids(mock_client)
    
    assert isinstance(existing_ids, set)
    assert len(existing_ids) == 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_get_existing_entity_ids_exception(mock_run_id, mock_logger) -> None:
    """Test stage_16 get_existing_entity_ids when table doesn't exist."""
    from stage_16.claude_code_stage_16 import get_existing_entity_ids
    from google.cloud import bigquery
    from google.api_core.exceptions import NotFound
    
    mock_client = Mock(spec=bigquery.Client)
    mock_client.query.side_effect = NotFound("Table not found")
    
    # Should return empty set on exception
    existing_ids = get_existing_entity_ids(mock_client)
    
    assert isinstance(existing_ids, set)
    assert len(existing_ids) == 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_promote_entities_no_warnings(mock_run_id, mock_logger) -> None:
    """Test stage_16 promote_entities with include_warnings=False."""
    from stage_16.claude_code_stage_16 import promote_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.validation_status = "PASSED"
    # Set all required attributes
    for attr in ["parent_id", "source_name", "source_pipeline", "level", "text", "role",
                 "message_type", "message_index", "word_count", "char_count", "model",
                 "cost_usd", "tool_name", "embedding", "embedding_model", "embedding_dimension",
                 "primary_emotion", "primary_emotion_score", "emotions_detected", "all_emotion_scores",
                 "intent", "task_type", "code_languages", "complexity", "has_code_block",
                 "top_keyword", "top_keyword_score", "keywords", "keywords_with_scores",
                 "session_id", "content_date", "timestamp_utc", "created_at", "run_id",
                 "validation_score", "fingerprint"]:
        setattr(mock_row, attr, None)
    
    # Make mock_row behave like a dict for dict(entity) conversion
    mock_row.keys.return_value = [
        "entity_id", "parent_id", "source_name", "source_pipeline", "level", "text", "role",
        "message_type", "message_index", "word_count", "char_count", "model",
        "cost_usd", "tool_name", "embedding", "embedding_model", "embedding_dimension",
        "primary_emotion", "primary_emotion_score", "emotions_detected", "all_emotion_scores",
        "intent", "task_type", "code_languages", "complexity", "has_code_block",
        "top_keyword", "top_keyword_score", "keywords", "keywords_with_scores",
        "session_id", "content_date", "timestamp_utc", "created_at", "run_id",
        "validation_status", "validation_score", "fingerprint"
    ]
    mock_row.__getitem__ = lambda self, key: getattr(self, key, None)
    
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    with patch('stage_16.claude_code_stage_16.get_existing_entity_ids', return_value=set()):
        result = promote_entities(mock_client, "test_run", include_warnings=False, dry_run=False)
        
        assert isinstance(result, dict)
        assert "eligible_entities" in result
        assert "promoted_entities" in result
        assert "skipped_duplicates" in result
        assert result["dry_run"] is False


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_promote_entities_batch_insert(mock_run_id, mock_logger) -> None:
    """Test stage_16 promote_entities with batch insert (1000+ entities)."""
    from stage_16.claude_code_stage_16 import promote_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    
    # Create 1500 mock rows to trigger batch insert
    mock_rows = []
    all_keys = [
        "entity_id", "parent_id", "source_name", "source_pipeline", "level", "text", "role",
        "message_type", "message_index", "word_count", "char_count", "model",
        "cost_usd", "tool_name", "embedding", "embedding_model", "embedding_dimension",
        "primary_emotion", "primary_emotion_score", "emotions_detected", "all_emotion_scores",
        "intent", "task_type", "code_languages", "complexity", "has_code_block",
        "top_keyword", "top_keyword_score", "keywords", "keywords_with_scores",
        "session_id", "content_date", "timestamp_utc", "created_at", "run_id",
        "validation_status", "validation_score", "fingerprint"
    ]
    
    for i in range(1500):
        mock_row = Mock()
        mock_row.entity_id = f"entity_{i}"
        mock_row.validation_status = "PASSED"
        for attr in all_keys:
            if attr not in ["entity_id", "validation_status"]:
                setattr(mock_row, attr, None)
        
        # Make mock_row behave like a dict
        mock_row.keys.return_value = all_keys
        mock_row.__getitem__ = lambda self, key: getattr(self, key, None)
        mock_rows.append(mock_row)
    
    mock_query_job.result.return_value = iter(mock_rows)
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    with patch('stage_16.claude_code_stage_16.get_existing_entity_ids', return_value=set()):
        result = promote_entities(mock_client, "test_run", include_warnings=True, dry_run=False)
        
        assert isinstance(result, dict)
        assert result["eligible_entities"] == 1500
        # Should have called insert_rows_json at least twice (1000 + 500)
        assert mock_client.insert_rows_json.call_count >= 2
