"""Additional coverage tests for Stage 13 (Relationships).

Target: Increase coverage for relationship building functions.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timezone
import pytest

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
def test_stage_13_generate_relationship_id(mock_run_id, mock_logger) -> None:
    """Test stage_13 generate_relationship_id function."""
    from stage_13.claude_code_stage_13 import generate_relationship_id
    
    rel_id = generate_relationship_id("source_123", "target_456", "parent_child")
    
    assert isinstance(rel_id, str)
    assert len(rel_id) > 0
    
    # Should be deterministic
    rel_id2 = generate_relationship_id("source_123", "target_456", "parent_child")
    assert rel_id == rel_id2
    
    # Different relationship types should produce different IDs
    rel_id3 = generate_relationship_id("source_123", "target_456", "sequential")
    assert rel_id != rel_id3


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_build_parent_child_relationships_empty(mock_run_id, mock_logger) -> None:
    """Test stage_13 build_parent_child_relationships with empty input."""
    from stage_13.claude_code_stage_13 import build_parent_child_relationships
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    
    # Mock empty query results
    mock_query_job1 = Mock()
    mock_query_job1.result.return_value = iter([])  # Message -> Sentence (empty)
    mock_query_job2 = Mock()
    mock_query_job2.result.return_value = iter([])  # Conversation -> Message (empty)
    
    def query_side_effect(query_str):
        if "STAGE_7_TABLE" in query_str and "STAGE_6_TABLE" in query_str:
            return mock_query_job1
        elif "STAGE_8_TABLE" in query_str:
            return mock_query_job2
        return mock_query_job1
    
    mock_client.query.side_effect = query_side_effect
    mock_client.insert_rows_json.return_value = []
    
    created_at = datetime.now(timezone.utc).isoformat()
    relationships = list(build_parent_child_relationships(mock_client, "test_run", created_at))
    
    assert isinstance(relationships, list)
    assert len(relationships) == 0  # Empty input = no relationships


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_build_sequential_relationships_empty(mock_run_id, mock_logger) -> None:
    """Test stage_13 build_sequential_relationships with empty input."""
    from stage_13.claude_code_stage_13 import build_sequential_relationships
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    
    # Mock empty query result
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    created_at = datetime.now(timezone.utc).isoformat()
    relationships = list(build_sequential_relationships(mock_client, "test_run", created_at))
    
    assert isinstance(relationships, list)
    assert len(relationships) == 0  # Empty input = no relationships


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_process_relationships_dry_run(mock_run_id, mock_logger) -> None:
    """Test stage_13 process_relationships with dry_run=True."""
    from stage_13.claude_code_stage_13 import process_relationships
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])
    mock_client.query.return_value = mock_query_job
    
    result = process_relationships(mock_client, "test_run", batch_size=100, dry_run=True)
    
    assert isinstance(result, dict)
    assert "dry_run" in result or "processed" in result or "total" in result
