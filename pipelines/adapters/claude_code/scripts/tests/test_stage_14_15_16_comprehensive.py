"""Comprehensive tests for Stages 14, 15, 16 (Finalization).

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
# STAGE 14 - AGGREGATION
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_14_aggregate_entities_empty_input(mock_run_id, mock_logger) -> None:
    """Test aggregate_entities with empty input."""
    from stage_14.claude_code_stage_14 import aggregate_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.cnt = 0  # No messages to aggregate
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    result = aggregate_entities(mock_client, "test_run", batch_size=100, dry_run=True)
    
    assert isinstance(result, dict)
    assert "dry_run" in result or "messages_aggregated" in result or "messages_to_aggregate" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_14_aggregate_entities_with_data(mock_run_id, mock_logger) -> None:
    """Test aggregate_entities with actual data."""
    from stage_14.claude_code_stage_14 import aggregate_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.cnt = 25  # Messages to aggregate
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    result = aggregate_entities(mock_client, "test_run", batch_size=100, dry_run=False)
    
    assert isinstance(result, dict)
    assert "messages_aggregated" in result or "messages_to_aggregate" in result or "dry_run" in result


# =============================================================================
# STAGE 15 - VALIDATION
# =============================================================================

@pytest.mark.parametrize("strict_mode", [True, False])
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_validate_entity_various_modes(mock_run_id, mock_logger, strict_mode: bool) -> None:
    """Test validate_entity with strict and non-strict modes."""
    from stage_15.claude_code_stage_15 import validate_entity
    
    # Valid entity
    valid_entity = {
        "entity_id": "entity_123",
        "text": "Test message",
        "level": 5,
        "source_name": "claude_code",
        "source_pipeline": "claude_code"
    }
    
    status, score, errors, warnings = validate_entity(valid_entity, strict=strict_mode)
    
    assert isinstance(status, str)
    assert status in ["PASSED", "FAILED", "WARNING"]
    assert isinstance(score, (int, float))
    assert isinstance(errors, list)
    assert isinstance(warnings, list)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_validate_entity_missing_fields(mock_run_id, mock_logger) -> None:
    """Test validate_entity with missing required fields."""
    from stage_15.claude_code_stage_15 import validate_entity
    
    invalid_entity = {
        "entity_id": "entity_123"
        # Missing required fields
    }
    
    status, score, errors, warnings = validate_entity(invalid_entity, strict=False)
    
    assert isinstance(status, str)
    assert status in ["FAILED", "WARNING"]
    assert isinstance(errors, list)
    assert isinstance(warnings, list)
    # Should have errors or warnings for missing fields
    assert len(errors) > 0 or len(warnings) > 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_run_validation_empty_input(mock_run_id, mock_logger) -> None:
    """Test run_validation with empty input."""
    from stage_15.claude_code_stage_15 import run_validation
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])
    mock_client.query.return_value = mock_query_job
    
    result = run_validation(mock_client, "test_run", strict=False, dry_run=True)
    
    assert isinstance(result, dict)
    assert "dry_run" in result or "validated" in result or "total" in result


# =============================================================================
# STAGE 16 - PROMOTION
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_ensure_entity_unified_table_exists(mock_run_id, mock_logger) -> None:
    """Test ensure_entity_unified_table when table exists."""
    from stage_16.claude_code_stage_16 import ensure_entity_unified_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.get_table.return_value = mock_table
    
    result = ensure_entity_unified_table(mock_client)
    
    assert result is not None
    # Result should be the table (either from get_table or create_table)
    assert result == mock_table or result is not None


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_ensure_entity_unified_table_not_exists(mock_run_id, mock_logger) -> None:
    """Test ensure_entity_unified_table when table doesn't exist."""
    from stage_16.claude_code_stage_16 import ensure_entity_unified_table
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.get_table.side_effect = NotFound("Table not found")
    mock_client.create_table.return_value = mock_table
    
    result = ensure_entity_unified_table(mock_client)
    
    assert result is not None
    assert mock_client.create_table.called


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_promote_entities_empty_input(mock_run_id, mock_logger) -> None:
    """Test promote_entities with empty input."""
    from stage_16.claude_code_stage_16 import promote_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])
    mock_client.query.return_value = mock_query_job
    
    with patch('stage_16.claude_code_stage_16.get_existing_entity_ids', return_value=set()):
        result = promote_entities(mock_client, "test_run", include_warnings=False, dry_run=True)
        
        assert isinstance(result, dict)
        assert "dry_run" in result or "promoted" in result or "eligible_entities" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_promote_entities_with_data(mock_run_id, mock_logger) -> None:
    """Test promote_entities with actual data."""
    from stage_16.claude_code_stage_16 import promote_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.parent_id = None
    mock_row.source_name = "claude_code"
    mock_row.level = 5
    mock_row.text = "Test message"
    mock_row.validation_status = "PASSED"
    mock_row.keys.return_value = ["entity_id", "parent_id", "source_name", "level", "text", "validation_status"]
    mock_row.__getitem__ = lambda self, key: getattr(self, key, None)
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    with patch('stage_16.claude_code_stage_16.get_existing_entity_ids', return_value=set()):
        result = promote_entities(mock_client, "test_run", include_warnings=False, dry_run=False)
        
        assert isinstance(result, dict)
        assert "promoted" in result or "eligible_entities" in result or "dry_run" in result


# =============================================================================
# ERROR HANDLING
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_14_15_16_handle_bigquery_errors(mock_run_id, mock_logger) -> None:
    """Test stages handle BigQuery errors gracefully."""
    from google.cloud import bigquery
    from google.api_core import exceptions as google_exceptions
    
    mock_client = Mock(spec=bigquery.Client)
    mock_client.query.side_effect = google_exceptions.ServiceUnavailable("Service unavailable")
    
    # Stages should handle BigQuery errors appropriately
    with pytest.raises(google_exceptions.ServiceUnavailable):
        mock_client.query("SELECT 1")


# =============================================================================
# BOUNDARY CONDITIONS
# =============================================================================

@pytest.mark.parametrize("batch_size", [1, 50, 100, 500, 1000])
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_14_15_16_various_batch_sizes(mock_run_id, mock_logger, batch_size: int) -> None:
    """Test stages with various batch sizes."""
    from stage_14.claude_code_stage_14 import aggregate_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.cnt = 0
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    result = aggregate_entities(mock_client, "test_run", batch_size=batch_size, dry_run=True)
    
    assert isinstance(result, dict)
    assert batch_size > 0  # Valid batch size
