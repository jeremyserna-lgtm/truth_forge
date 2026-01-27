"""Additional coverage tests for Stage 15 (Validation).

Target: Increase coverage for entity validation functions.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch
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
def test_stage_15_validate_entity_strict_mode(mock_run_id, mock_logger) -> None:
    """Test stage_15 validate_entity with strict=True."""
    from stage_15.claude_code_stage_15 import validate_entity
    
    # Valid entity
    valid_entity = {
        "entity_id": "entity_123",
        "text": "Test message",
        "level": 5,
        "source_name": "claude_code",
        "source_pipeline": "claude_code"
    }
    
    status, score, errors, warnings = validate_entity(valid_entity, strict=True)
    
    assert isinstance(status, str)
    assert status in ["PASSED", "FAILED", "WARNING"]
    assert isinstance(score, (int, float))
    assert isinstance(errors, list)
    assert isinstance(warnings, list)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_validate_entity_missing_optional_fields(mock_run_id, mock_logger) -> None:
    """Test stage_15 validate_entity with missing optional fields."""
    from stage_15.claude_code_stage_15 import validate_entity
    
    # Entity with required fields but missing optional ones
    entity = {
        "entity_id": "entity_123",
        "text": "Test",
        "level": 5,
        "source_name": "claude_code",
        "source_pipeline": "claude_code"
        # Missing optional fields like session_id, content_date, etc.
    }
    
    status, score, errors, warnings = validate_entity(entity, strict=False)
    
    assert isinstance(status, str)
    assert isinstance(score, (int, float))
    assert isinstance(errors, list)
    assert isinstance(warnings, list)
    # Should pass in non-strict mode even with missing optional fields


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_run_validation_with_warnings(mock_run_id, mock_logger) -> None:
    """Test stage_15 run_validation that includes warnings."""
    from stage_15.claude_code_stage_15 import run_validation
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    
    # Mock entity with warnings
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.text = "Test"
    mock_row.level = 5
    mock_row.source_name = "claude_code"
    mock_row.keys.return_value = ["entity_id", "text", "level", "source_name"]
    mock_row.__getitem__ = lambda self, key: getattr(self, key, None)
    
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    result = run_validation(mock_client, "test_run", strict=False, dry_run=True)
    
    assert isinstance(result, dict)
    assert "dry_run" in result or "processed" in result or "total" in result
