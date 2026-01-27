"""Expanded tests for Stages 7, 8, 13, 14.

Target: Increase coverage for these stages with lower coverage.
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
def test_stage_7_create_message_entities_expanded(mock_run_id, mock_logger) -> None:
    """Test stage_7 create_message_entities function with expanded coverage."""
    from stage_7.claude_code_stage_7 import create_message_entities
    from google.cloud import bigquery
    from datetime import datetime, timezone
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.extraction_id = "ext_123"
    mock_row.session_id = "session_123"
    mock_row.message_index = 0
    mock_row.message_type = "message"
    mock_row.role = "user"
    mock_row.content_cleaned = "Test message"
    mock_row.content_length = 12
    mock_row.word_count = 2
    mock_row.timestamp_utc = datetime.now(timezone.utc)
    mock_row.model = None
    mock_row.cost_usd = None
    mock_row.tool_name = None
    mock_row.tool_input = None
    mock_row.tool_output = None
    mock_row.source_file = "test.jsonl"
    mock_row.content_date = None
    mock_row.fingerprint = "fp_hash"
    mock_row.is_duplicate = False
    mock_row.extracted_at = datetime.now(timezone.utc)
    mock_row.cleaned_at = datetime.now(timezone.utc)
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    # create_message_entities is a generator, takes (client, run_id, created_at)
    created_at = datetime.now(timezone.utc).isoformat()
    entities = list(create_message_entities(mock_client, "test_run", created_at))
    
    assert isinstance(entities, list)
    assert all("entity_id" in e for e in entities)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_create_conversation_entities_expanded(mock_run_id, mock_logger) -> None:
    """Test stage_8 create_conversation_entities function with expanded coverage."""
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
    
    # create_conversation_entities is a generator, takes (client, run_id, created_at)
    created_at = datetime.now(timezone.utc).isoformat()
    entities = list(create_conversation_entities(mock_client, "test_run", created_at))
    
    assert isinstance(entities, list)
    assert all("entity_id" in e for e in entities)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_generate_relationship_id(mock_run_id, mock_logger) -> None:
    """Test stage_13 generate_relationship_id function."""
    from stage_13.claude_code_stage_13 import generate_relationship_id
    
    relationship_id = generate_relationship_id("source_123", "target_456", "parent_child")
    
    assert isinstance(relationship_id, str)
    assert len(relationship_id) > 0
    # Should be deterministic
    relationship_id2 = generate_relationship_id("source_123", "target_456", "parent_child")
    assert relationship_id == relationship_id2


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_build_parent_child_relationships_expanded(mock_run_id, mock_logger) -> None:
    """Test stage_13 build_parent_child_relationships function with expanded coverage."""
    from stage_13.claude_code_stage_13 import build_parent_child_relationships
    from google.cloud import bigquery
    from datetime import datetime, timezone
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.parent_id = "parent_123"
    mock_row.child_id = "child_456"
    mock_row.parent_level = 1
    mock_row.child_level = 2
    mock_row.session_id = "session_123"
    mock_row.content_date = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    # build_parent_child_relationships is a generator, takes (client, run_id, created_at)
    created_at = datetime.now(timezone.utc).isoformat()
    relationships = list(build_parent_child_relationships(mock_client, "test_run", created_at))
    
    assert isinstance(relationships, list)
    assert all("relationship_id" in r for r in relationships)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_14_aggregate_entities_expanded(mock_run_id, mock_logger) -> None:
    """Test stage_14 aggregate_entities function with expanded coverage."""
    from stage_14.claude_code_stage_14 import aggregate_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.cnt = 25
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    result = aggregate_entities(mock_client, "test_run", batch_size=100, dry_run=True)
    
    assert isinstance(result, dict)
    assert "messages_aggregated" in result or "messages_to_aggregate" in result or "dry_run" in result
