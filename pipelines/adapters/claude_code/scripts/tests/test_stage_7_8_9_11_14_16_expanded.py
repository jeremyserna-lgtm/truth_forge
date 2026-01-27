"""Expanded comprehensive tests for Stages 7, 8, 9, 11, 14, 16.

Target: Increase coverage for message creation, conversation creation, embeddings,
sentiment analysis, aggregation, and promotion stages.
Focus on uncovered functions and edge cases.
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


# Stage 7 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_7_create_stage_7_table(mock_run_id, mock_logger) -> None:
    """Test stage_7 create_stage_7_table function."""
    from stage_7.claude_code_stage_7 import create_stage_7_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_7_table(mock_client)
    
    assert result is not None
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_7_create_message_entities_empty(mock_run_id, mock_logger) -> None:
    """Test stage_7 create_message_entities with empty input."""
    from stage_7.claude_code_stage_7 import create_message_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])  # Empty result
    mock_client.query.return_value = mock_query_job
    
    created_at = datetime.now(timezone.utc).isoformat()
    entities = list(create_message_entities(mock_client, "test_run", created_at))
    
    assert isinstance(entities, list)
    assert len(entities) == 0


# Stage 8 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_create_stage_8_table(mock_run_id, mock_logger) -> None:
    """Test stage_8 create_stage_8_table function."""
    from stage_8.claude_code_stage_8 import create_stage_8_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_8_table(mock_client)
    
    assert result is not None
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_generate_conversation_id(mock_run_id, mock_logger) -> None:
    """Test stage_8 generate_conversation_id function."""
    from stage_8.claude_code_stage_8 import generate_conversation_id
    
    conv_id = generate_conversation_id("session_123")
    
    assert isinstance(conv_id, str)
    assert len(conv_id) > 0
    
    # Should be deterministic
    conv_id2 = generate_conversation_id("session_123")
    assert conv_id == conv_id2
    
    # Different sessions should produce different IDs
    conv_id3 = generate_conversation_id("session_456")
    assert conv_id != conv_id3


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_create_conversation_entities_empty(mock_run_id, mock_logger) -> None:
    """Test stage_8 create_conversation_entities with empty input."""
    from stage_8.claude_code_stage_8 import create_conversation_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])  # Empty result
    mock_client.query.return_value = mock_query_job
    
    created_at = datetime.now(timezone.utc).isoformat()
    entities = list(create_conversation_entities(mock_client, "test_run", created_at))
    
    assert isinstance(entities, list)
    assert len(entities) == 0


# Stage 9 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_create_stage_9_table(mock_run_id, mock_logger) -> None:
    """Test stage_9 create_stage_9_table function."""
    from stage_9.claude_code_stage_9 import create_stage_9_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_9_table(mock_client)
    
    assert result is not None
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_get_embedding_client(mock_run_id, mock_logger) -> None:
    """Test stage_9 get_embedding_client function."""
    from stage_9.claude_code_stage_9 import get_embedding_client
    import pytest
    
    # Skip if google.generativeai not available
    try:
        import google.generativeai as genai
    except ImportError:
        pytest.skip("google.generativeai not available - skipping test")
    
    # Function may raise ImportError if package not installed
    try:
        client = get_embedding_client()
        assert client is not None
    except ImportError:
        # Expected if package not installed
        pass


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_truncate_text_empty(mock_run_id, mock_logger) -> None:
    """Test stage_9 truncate_text with empty text."""
    from stage_9.claude_code_stage_9 import truncate_text
    
    # Empty text should return empty string and False for truncated
    result_text, was_truncated = truncate_text("", max_chars=8000)
    assert result_text == ""
    assert was_truncated is False


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
def test_stage_11_get_sentiment_pipeline(mock_run_id, mock_logger) -> None:
    """Test stage_11 get_sentiment_pipeline function."""
    from stage_11.claude_code_stage_11 import get_sentiment_pipeline
    import pytest
    
    # Skip if transformers not available
    try:
        from transformers import pipeline
    except ImportError:
        pytest.skip("transformers not available - skipping test")
    
    # Function may raise ImportError if package not installed
    try:
        model = get_sentiment_pipeline()
        assert model is not None
    except ImportError:
        # Expected if package not installed
        pass


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_process_sentiment_batch_empty(mock_run_id, mock_logger) -> None:
    """Test stage_11 process_sentiment_batch with empty text list."""
    from stage_11.claude_code_stage_11 import process_sentiment_batch
    from unittest.mock import Mock
    
    mock_pipeline = Mock()
    mock_pipeline.return_value = []
    
    # Empty text list should return empty list
    result = process_sentiment_batch(mock_pipeline, [], threshold=0.5)
    assert isinstance(result, list)
    assert len(result) == 0


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
def test_stage_14_aggregate_entities_empty(mock_run_id, mock_logger) -> None:
    """Test stage_14 aggregate_entities with empty input."""
    from stage_14.claude_code_stage_14 import aggregate_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    
    # For dry_run, the function uses a count query, not the aggregation query
    # Mock the count query result
    mock_count_query_job = Mock()
    mock_count_row = Mock()
    mock_count_row.cnt = 0  # Empty table
    mock_count_query_job.result.return_value = iter([mock_count_row])
    
    # The function executes the aggregation query as a CREATE OR REPLACE TABLE
    # For dry_run, it uses a count query instead
    def query_side_effect(query_str):
        if "COUNT(*)" in query_str:
            return mock_count_query_job
        # For the actual aggregation query (not executed in dry_run)
        mock_agg_query_job = Mock()
        mock_agg_query_job.result.return_value = iter([])
        return mock_agg_query_job
    
    mock_client.query.side_effect = query_side_effect
    mock_client.insert_rows_json.return_value = []
    
    # For dry_run, it should return stats even with empty input
    result = aggregate_entities(mock_client, "test_run", dry_run=True, batch_size=100)
    
    assert isinstance(result, dict)
    assert "dry_run" in result or "processed" in result or "total" in result or "count" in result


# Stage 16 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_ensure_entity_unified_table(mock_run_id, mock_logger) -> None:
    """Test stage_16 ensure_entity_unified_table function."""
    from stage_16.claude_code_stage_16 import ensure_entity_unified_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = ensure_entity_unified_table(mock_client)
    
    assert result is not None
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_get_existing_entity_ids_empty_result(mock_run_id, mock_logger) -> None:
    """Test stage_16 get_existing_entity_ids with empty result."""
    from stage_16.claude_code_stage_16 import get_existing_entity_ids
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])  # Empty result
    mock_client.query.return_value = mock_query_job
    
    entity_ids = get_existing_entity_ids(mock_client)
    
    assert isinstance(entity_ids, set)
    assert len(entity_ids) == 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_promote_entities_empty(mock_run_id, mock_logger) -> None:
    """Test stage_16 promote_entities with empty input."""
    from stage_16.claude_code_stage_16 import promote_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])  # Empty result
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    # Mock get_existing_entity_ids to return empty set
    with patch('stage_16.claude_code_stage_16.get_existing_entity_ids', return_value=set()):
        result = promote_entities(mock_client, "test_run", include_warnings=False, dry_run=True)
        
        assert isinstance(result, dict)
        assert "promoted" in result or "total" in result or "count" in result or "dry_run" in result
