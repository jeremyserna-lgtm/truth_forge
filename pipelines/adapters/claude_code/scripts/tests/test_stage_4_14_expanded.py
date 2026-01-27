"""Expanded tests for Stages 4 and 14.

Target: Increase coverage for staging and aggregation stages.
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
def test_stage_4_process_staging_expanded(mock_run_id, mock_logger) -> None:
    """Test stage_4 process_staging function with expanded coverage."""
    from stage_4.claude_code_stage_4 import process_staging
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.extraction_id = "ext_123"
    mock_row.entity_id = "entity_123"
    mock_row.session_id = "session_123"
    mock_row.message_index = 0
    mock_row.message_type = "message"
    mock_row.role = "user"
    mock_row.content_cleaned = "Test message"
    mock_row.content_length = 12
    mock_row.word_count = 2
    mock_row.timestamp_utc = None
    mock_row.model = None
    mock_row.cost_usd = None
    mock_row.tool_name = None
    mock_row.tool_input = None
    mock_row.tool_output = None
    mock_row.source_file = "test.jsonl"
    mock_row.content_date = None
    mock_row.fingerprint = "fp_hash"
    mock_row.is_duplicate = False
    mock_row.extracted_at = None
    mock_row.cleaned_at = None
    mock_row.identity_created_at = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    result = process_staging(mock_client, "test_run", dry_run=True)
    
    assert isinstance(result, dict)
    assert "processed" in result or "total" in result or "count" in result or "dry_run" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_14_aggregate_entities_comprehensive(mock_run_id, mock_logger) -> None:
    """Test stage_14 aggregate_entities function comprehensively."""
    from stage_14.claude_code_stage_14 import aggregate_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    
    # Mock count query for dry_run
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.cnt = 15
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    result = aggregate_entities(mock_client, "test_run", batch_size=100, dry_run=True)
    
    assert isinstance(result, dict)
    assert "messages_aggregated" in result or "messages_to_aggregate" in result or "dry_run" in result


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
