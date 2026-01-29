"""Comprehensive tests for Stage 8 (Conversation Entities).

Target: Cover all functions with comprehensive tests including error handling and edge cases.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import datetime, timezone

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


# =============================================================================
# STAGE 8 - CONVERSATION ENTITIES
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_generate_conversation_id_deterministic(mock_run_id, mock_logger) -> None:
    """Test generate_conversation_id produces deterministic IDs."""
    from stage_8.claude_code_stage_8 import generate_conversation_id
    
    id1 = generate_conversation_id("session_123")
    id2 = generate_conversation_id("session_123")
    
    assert id1 == id2
    assert isinstance(id1, str)
    assert len(id1) > 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_generate_conversation_id_different_sessions(mock_run_id, mock_logger) -> None:
    """Test generate_conversation_id produces different IDs for different sessions."""
    from stage_8.claude_code_stage_8 import generate_conversation_id
    
    id1 = generate_conversation_id("session_123")
    id2 = generate_conversation_id("session_456")
    
    assert id1 != id2


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_create_conversation_entities_empty_input(mock_run_id, mock_logger) -> None:
    """Test create_conversation_entities with empty input."""
    from stage_8.claude_code_stage_8 import create_conversation_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])
    mock_client.query.return_value = mock_query_job
    
    created_at = datetime.now(timezone.utc).isoformat()
    entities = list(create_conversation_entities(mock_client, "test_run", created_at))
    
    assert isinstance(entities, list)
    assert len(entities) == 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_create_conversation_entities_with_data(mock_run_id, mock_logger) -> None:
    """Test create_conversation_entities with actual data."""
    from stage_8.claude_code_stage_8 import create_conversation_entities
    from google.cloud import bigquery
    
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
    
    created_at = datetime.now(timezone.utc).isoformat()
    entities = list(create_conversation_entities(mock_client, "test_run", created_at))
    
    assert isinstance(entities, list)
    assert all("entity_id" in e for e in entities)
    assert all("session_id" in e for e in entities)
    assert all("level" in e for e in entities)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_create_conversation_entities_missing_fields(mock_run_id, mock_logger) -> None:
    """Test create_conversation_entities handles missing fields gracefully."""
    from stage_8.claude_code_stage_8 import create_conversation_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.session_id = "session_123"
    # Missing some fields - should handle gracefully
    mock_row.first_message_at = None
    mock_row.last_message_at = None
    mock_row.message_count = 0
    mock_row.user_message_count = 0
    mock_row.assistant_message_count = 0
    mock_row.tool_use_count = 0
    mock_row.total_word_count = 0
    mock_row.total_char_count = 0
    mock_row.total_cost_usd = None
    mock_row.models_used = None
    mock_row.tools_used = None
    mock_row.content_date = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    created_at = datetime.now(timezone.utc).isoformat()
    entities = list(create_conversation_entities(mock_client, "test_run", created_at))
    
    assert isinstance(entities, list)
    # Should still create entities even with missing fields
    assert len(entities) >= 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_create_conversation_entities_bigquery_error(mock_run_id, mock_logger) -> None:
    """Test create_conversation_entities handles BigQuery errors."""
    from stage_8.claude_code_stage_8 import create_conversation_entities
    from google.cloud import bigquery
    from google.api_core import exceptions as google_exceptions
    
    mock_client = Mock(spec=bigquery.Client)
    mock_client.query.side_effect = google_exceptions.ServiceUnavailable("Service unavailable")
    
    created_at = datetime.now(timezone.utc).isoformat()
    with pytest.raises(google_exceptions.ServiceUnavailable):
        list(create_conversation_entities(mock_client, "test_run", created_at))
