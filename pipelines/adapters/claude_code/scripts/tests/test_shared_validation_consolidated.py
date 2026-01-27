"""Consolidated validation tests using parameterization.

Replaces multiple individual validation tests with parameterized tests.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from shared_validation import (
    validate_table_id,
    validate_run_id,
    validate_stage_number,
    validate_batch_size,
    validate_required_fields,
)


# Table ID validation tests
@pytest.mark.parametrize("valid_id", [
    "project.dataset.table",
    "dataset.table",
    "table_name",
    "table-name",
    "table_name_123",
])
def test_validate_table_id_valid_consolidated(valid_id: str) -> None:
    """Test validate_table_id with valid table IDs (consolidated)."""
    assert validate_table_id(valid_id) == valid_id


@pytest.mark.parametrize("invalid_id", [
    "",
    "test; DROP TABLE users;--",
    "table' OR '1'='1",
    "table--comment",
    "table; DELETE",
])
def test_validate_table_id_invalid_consolidated(invalid_id: str) -> None:
    """Test validate_table_id with invalid table IDs (consolidated)."""
    with pytest.raises(ValueError):
        validate_table_id(invalid_id)


# Run ID validation tests
@pytest.mark.parametrize("valid_run_id", [
    "run_123",
    "run-123",
    "run_123_abc",
    "abc123",
    "test_run_2026_01_27",
])
def test_validate_run_id_valid_consolidated(valid_run_id: str) -> None:
    """Test validate_run_id with valid run IDs (consolidated)."""
    assert validate_run_id(valid_run_id) == valid_run_id


@pytest.mark.parametrize("invalid_run_id", [
    "",
    "run; DROP TABLE users;--",
    "run with spaces",
    "   ",
])
def test_validate_run_id_invalid_consolidated(invalid_run_id: str) -> None:
    """Test validate_run_id with invalid run IDs (consolidated)."""
    with pytest.raises(ValueError):
        validate_run_id(invalid_run_id)


# Stage number validation tests
@pytest.mark.parametrize("valid_stage", [0, 5, 10, 16, 100])
def test_validate_stage_number_valid_consolidated(valid_stage: int) -> None:
    """Test validate_stage_number with valid stage numbers (consolidated)."""
    assert validate_stage_number(valid_stage) == valid_stage


@pytest.mark.parametrize("invalid_stage", [-1, 101, 1000])
def test_validate_stage_number_invalid_consolidated(invalid_stage: int) -> None:
    """Test validate_stage_number with invalid stage numbers (consolidated)."""
    with pytest.raises(ValueError):
        validate_stage_number(invalid_stage)


# Batch size validation tests
@pytest.mark.parametrize("valid_size", [1, 100, 1000, 10000])
def test_validate_batch_size_valid_consolidated(valid_size: int) -> None:
    """Test validate_batch_size with valid batch sizes (consolidated)."""
    assert validate_batch_size(valid_size) == valid_size


@pytest.mark.parametrize("invalid_size", [0, -1, 20000])
def test_validate_batch_size_invalid_consolidated(invalid_size: int) -> None:
    """Test validate_batch_size with invalid batch sizes (consolidated)."""
    with pytest.raises(ValueError):
        validate_batch_size(invalid_size)


# Required fields validation tests
def test_validate_required_fields_present_consolidated() -> None:
    """Test validate_required_fields with all fields present (consolidated)."""
    data = {
        "entity_id": "test_123",
        "session_id": "session_456",
        "text": "Test message"
    }
    required = ["entity_id", "session_id", "text"]
    
    # Should not raise
    validate_required_fields(data, required)


def test_validate_required_fields_missing_consolidated() -> None:
    """Test validate_required_fields with missing fields (consolidated)."""
    data = {
        "entity_id": "test_123"
        # Missing session_id and text
    }
    required = ["entity_id", "session_id", "text"]
    
    with pytest.raises(ValueError, match="missing required fields"):
        validate_required_fields(data, required)
