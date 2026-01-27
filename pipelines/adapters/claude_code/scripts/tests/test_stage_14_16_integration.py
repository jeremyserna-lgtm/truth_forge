"""Integration tests for Stages 14 and 16.

Target: Test data flow between aggregation and promotion stages.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch
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
def test_stage_14_to_15_data_flow(mock_run_id, mock_logger) -> None:
    """Test data flow from stage_14 aggregation to stage_15 validation."""
    from stage_14.claude_code_stage_14 import aggregate_entities
    from stage_15.claude_code_stage_15 import run_validation
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    
    # Mock stage_14 output (aggregated entities)
    mock_agg_row = Mock()
    mock_agg_row.entity_id = "entity_123"
    mock_agg_row.text = "Test message"
    mock_agg_row.level = 5
    mock_agg_row.source_name = "claude_code"
    mock_agg_row.session_id = "session_123"
    mock_agg_row.message_index = 0
    mock_agg_row.keys.return_value = ["entity_id", "text", "level", "source_name", "session_id", "message_index"]
    mock_agg_row.__getitem__ = lambda self, key: getattr(self, key, None)
    
    # Mock stage_15 input (reading from stage_14 table)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([mock_agg_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    # Test aggregation
    agg_result = aggregate_entities(mock_client, "test_run", dry_run=True, batch_size=100)
    assert isinstance(agg_result, dict)
    
    # Test validation (reads from stage_14, writes to stage_15)
    val_result = run_validation(mock_client, "test_run", strict=False, dry_run=True)
    assert isinstance(val_result, dict)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_to_16_data_flow(mock_run_id, mock_logger) -> None:
    """Test data flow from stage_15 validation to stage_16 promotion."""
    from stage_15.claude_code_stage_15 import run_validation
    from stage_16.claude_code_stage_16 import promote_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    
    # Mock stage_15 output (validated entities)
    mock_val_row = Mock()
    mock_val_row.entity_id = "entity_123"
    mock_val_row.validation_status = "PASSED"
    mock_val_row.text = "Test message"
    mock_val_row.level = 5
    mock_val_row.source_name = "claude_code"
    mock_val_row.session_id = "session_123"
    mock_val_row.keys.return_value = ["entity_id", "validation_status", "text", "level", "source_name", "session_id"]
    mock_val_row.__getitem__ = lambda self, key: getattr(self, key, None)
    
    # Mock queries
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([mock_val_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    # Test validation
    val_result = run_validation(mock_client, "test_run", strict=False, dry_run=True)
    assert isinstance(val_result, dict)
    
    # Test promotion (reads from stage_15, writes to entity_unified)
    with patch('stage_16.claude_code_stage_16.get_existing_entity_ids', return_value=set()):
        promo_result = promote_entities(mock_client, "test_run", include_warnings=False, dry_run=True)
        assert isinstance(promo_result, dict)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_promote_entities_with_warnings(mock_run_id, mock_logger) -> None:
    """Test stage_16 promote_entities with include_warnings=True."""
    from stage_16.claude_code_stage_16 import promote_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    
    # Mock validated entities with WARNING status
    mock_warning_row = Mock()
    mock_warning_row.entity_id = "entity_123"
    mock_warning_row.validation_status = "WARNING"
    mock_warning_row.text = "Test message"
    mock_warning_row.level = 5
    mock_warning_row.source_name = "claude_code"
    mock_warning_row.session_id = "session_123"
    mock_warning_row.keys.return_value = ["entity_id", "validation_status", "text", "level", "source_name", "session_id"]
    mock_warning_row.__getitem__ = lambda self, key: getattr(self, key, None)
    
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([mock_warning_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    with patch('stage_16.claude_code_stage_16.get_existing_entity_ids', return_value=set()):
        result = promote_entities(mock_client, "test_run", include_warnings=True, dry_run=True)
        assert isinstance(result, dict)
        assert "promoted" in result or "total" in result or "count" in result or "dry_run" in result
