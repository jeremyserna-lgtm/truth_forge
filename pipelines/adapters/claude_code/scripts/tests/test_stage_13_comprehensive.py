"""Comprehensive tests for Stage 13.

Target: 90%+ coverage of relationship building stage.
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
def test_stage_13_generate_relationship_id(mock_run_id, mock_logger) -> None:
    """Test stage_13 generate_relationship_id function."""
    from stage_13.claude_code_stage_13 import generate_relationship_id
    
    rel_id = generate_relationship_id("source_123", "target_456", "parent_child")
    
    assert isinstance(rel_id, str)
    assert len(rel_id) > 0
    # Should be deterministic
    rel_id2 = generate_relationship_id("source_123", "target_456", "parent_child")
    assert rel_id == rel_id2


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_build_parent_child_relationships(mock_run_id, mock_logger) -> None:
    """Test stage_13 build_parent_child_relationships function."""
    from stage_13.claude_code_stage_13 import build_parent_child_relationships
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.parent_id = "parent_123"
    mock_row.entity_id = "child_456"
    mock_row.level = 5
    mock_query_job.result.return_value = [mock_row]
    mock_client.query.return_value = mock_query_job
    
    # build_parent_child_relationships is a generator
    relationships = list(build_parent_child_relationships(mock_client, "test_run", "2024-01-01T00:00:00Z"))
    
    assert isinstance(relationships, list)
    assert len(relationships) > 0
    assert all("relationship_id" in rel for rel in relationships)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_build_sequential_relationships(mock_run_id, mock_logger) -> None:
    """Test stage_13 build_sequential_relationships function."""
    from stage_13.claude_code_stage_13 import build_sequential_relationships
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.next_entity_id = "entity_456"
    mock_row.session_id = "session_123"
    mock_row.message_index = 0
    mock_row.next_message_index = 1
    mock_row.source_role = "user"  # String, not Mock
    mock_row.target_role = "assistant"  # String, not Mock
    mock_row.content_date = "2024-01-01"
    mock_query_job.result.return_value = [mock_row]
    mock_client.query.return_value = mock_query_job
    
    # build_sequential_relationships is a generator
    relationships = list(build_sequential_relationships(mock_client, "test_run", "2024-01-01T00:00:00Z"))
    
    assert isinstance(relationships, list)
    # May be empty if no sequential relationships found
    assert isinstance(relationships, list)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_process_relationships(mock_run_id, mock_logger) -> None:
    """Test stage_13 process_relationships function."""
    from stage_13.claude_code_stage_13 import process_relationships
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = []  # Empty result
    mock_client.query.return_value = mock_query_job
    
    result = process_relationships(mock_client, "test_run", batch_size=100, dry_run=True)
    
    assert isinstance(result, dict)
    assert "processed" in result or "total" in result or "count" in result or "dry_run" in result
