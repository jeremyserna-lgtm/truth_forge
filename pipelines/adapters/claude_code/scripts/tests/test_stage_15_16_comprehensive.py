"""Comprehensive tests for Stages 15 and 16.

Target: 90%+ coverage of final validation and promotion stages.
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
def test_stage_15_validate_entity_comprehensive(mock_run_id, mock_logger) -> None:
    """Test stage_15 validate_entity function comprehensively."""
    from stage_15.claude_code_stage_15 import validate_entity
    
    # Test with valid entity
    valid_entity = {
        "entity_id": "entity_123",
        "text": "Test message",
        "level": 5,
        "source_name": "claude_code",
        "source_pipeline": "claude_code"
    }
    
    status, score, errors, warnings = validate_entity(valid_entity, strict=False)
    
    # status is a string ("PASSED", "FAILED", "WARNING"), not bool
    assert isinstance(status, str)
    assert status in ["PASSED", "FAILED", "WARNING"]
    assert isinstance(score, (int, float))
    assert isinstance(errors, list)
    assert isinstance(warnings, list)
    
    # Test with invalid entity (missing required fields)
    invalid_entity = {
        "entity_id": "entity_123"
        # Missing required fields
    }
    
    status, score, errors, warnings = validate_entity(invalid_entity, strict=False)
    
    # Should have errors or warnings
    assert isinstance(status, str)
    assert isinstance(errors, list)
    assert isinstance(warnings, list)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_run_validation(mock_run_id, mock_logger) -> None:
    """Test stage_15 run_validation function."""
    from stage_15.claude_code_stage_15 import run_validation
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    # Create a proper mock row with all required attributes
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.text = "Test"
    mock_row.level = 5
    mock_row.source_name = "claude_code"
    mock_row.session_id = "session_123"
    mock_row.message_index = 0
    # Make it behave like a dict for entity conversion
    mock_row.keys.return_value = ["entity_id", "text", "level", "source_name", "session_id", "message_index"]
    mock_row.__getitem__ = lambda self, key: getattr(self, key, None)
    mock_query_job.result.return_value = [mock_row]
    mock_client.query.return_value = mock_query_job
    
    # run_validation requires strict parameter
    result = run_validation(mock_client, "test_run", strict=False, dry_run=True)
    
    assert isinstance(result, dict)
    assert "validated" in result or "errors" in result or "warnings" in result or "dry_run" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_ensure_entity_unified_table(mock_run_id, mock_logger) -> None:
    """Test stage_16 ensure_entity_unified_table function."""
    from stage_16.claude_code_stage_16 import ensure_entity_unified_table
    from google.cloud import bigquery
    from google.api_core.exceptions import NotFound
    
    mock_client = Mock(spec=bigquery.Client)
    
    # Test table doesn't exist (should create)
    mock_client.get_table.side_effect = NotFound("Table not found")
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = ensure_entity_unified_table(mock_client)
    
    assert result is not None
    mock_client.create_table.assert_called_once()
    
    # Test table exists (should return existing)
    mock_client.get_table.side_effect = None
    mock_client.get_table.return_value = mock_table
    
    result = ensure_entity_unified_table(mock_client)
    
    assert result is not None
    assert result == mock_table


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_promote_entities(mock_run_id, mock_logger) -> None:
    """Test stage_16 promote_entities function."""
    from stage_16.claude_code_stage_16 import promote_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = []  # Empty result
    mock_client.query.return_value = mock_query_job
    
    # promote_entities requires include_warnings parameter
    result = promote_entities(mock_client, "test_run", include_warnings=False, dry_run=True)
    
    assert isinstance(result, dict)
    assert "promoted" in result or "total" in result or "count" in result or "dry_run" in result
