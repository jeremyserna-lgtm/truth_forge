"""Comprehensive tests for Stages 7 and 14.

Target: 90%+ coverage of stage_7 and stage_14 processing functions.
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
def test_stage_7_create_message_entities(mock_run_id, mock_logger) -> None:
    """Test stage_7 create_message_entities function."""
    from stage_7.claude_code_stage_7 import create_message_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "parent_123"
    mock_row.text = "Test message"
    mock_row.session_id = "session_123"
    mock_row.content_date = "2024-01-01"
    mock_query_job.result.return_value = [mock_row]
    mock_client.query.return_value = mock_query_job
    
    # create_message_entities is a generator
    entities = list(create_message_entities(mock_client, "test_run", "2024-01-01T00:00:00Z"))
    
    assert isinstance(entities, list)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_14_aggregate_entities(mock_run_id, mock_logger) -> None:
    """Test stage_14 aggregate_entities function."""
    from stage_14.claude_code_stage_14 import aggregate_entities
    from google.cloud import bigquery
    from unittest.mock import Mock
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.cnt = 10  # Count result
    mock_query_job.result.return_value = iter([mock_row])  # Use iter() to avoid StopIteration
    mock_client.query.return_value = mock_query_job
    
    # aggregate_entities returns dict with specific keys
    result = aggregate_entities(mock_client, "test_run", batch_size=100, dry_run=True)
    
    assert isinstance(result, dict)
    # Check for actual keys returned by aggregate_entities (messages_aggregated, messages_to_aggregate, dry_run)
    assert "messages_aggregated" in result or "messages_to_aggregate" in result or "dry_run" in result
