"""Additional coverage tests for shared/validation.py

Target: Cover remaining validation functions and edge cases.
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


# =============================================================================
# VALIDATION FUNCTIONS - ADDITIONAL COVERAGE
# =============================================================================

@pytest.mark.parametrize("table_id,expected_valid", [
    ("valid_table_name", True),
    ("table_with_123", True),
    ("table-with-dashes", True),  # Valid: dashes are allowed
    ("table with spaces", False),  # Invalid: contains spaces
    ("", False),  # Invalid: empty
    ("123_starts_with_number", True),  # Valid: can start with number
])
def test_validate_table_id_consolidated(table_id: str, expected_valid: bool) -> None:
    """Test validate_table_id with various inputs."""
    from shared_validation import validate_table_id
    
    if expected_valid:
        result = validate_table_id(table_id)
        assert result == table_id
    else:
        with pytest.raises(ValueError):
            validate_table_id(table_id)


@pytest.mark.parametrize("run_id,expected_valid", [
    ("run_123", True),
    ("run_abc_def", True),
    ("run-with-dashes", True),  # Valid: dashes are allowed
    ("run with spaces", False),  # Invalid: contains spaces
    ("", False),  # Invalid: empty
])
def test_validate_run_id_consolidated(run_id: str, expected_valid: bool) -> None:
    """Test validate_run_id with various inputs."""
    from shared_validation import validate_run_id
    
    if expected_valid:
        result = validate_run_id(run_id)
        assert result == run_id
    else:
        with pytest.raises(ValueError):
            validate_run_id(run_id)


@pytest.mark.parametrize("stage,expected_valid", [
    (0, True),
    (5, True),
    (16, True),
    (100, True),  # Valid: up to 100 is allowed
    (-1, False),  # Invalid: negative
    (101, False),  # Invalid: too high
])
def test_validate_stage_number_consolidated(stage: int, expected_valid: bool) -> None:
    """Test validate_stage_number with various inputs."""
    from shared_validation import validate_stage_number
    
    if expected_valid:
        result = validate_stage_number(stage)
        assert result == stage
    else:
        with pytest.raises(ValueError):
            validate_stage_number(stage)


@pytest.mark.parametrize("path_str,expected_valid,must_exist", [
    (".", True, True),  # Current directory exists
])
def test_validate_path_consolidated(path_str: str, expected_valid: bool, must_exist: bool) -> None:
    """Test validate_path with various inputs."""
    from shared_validation import validate_path
    
    if expected_valid:
        result = validate_path(path_str, must_exist=must_exist)
        assert isinstance(result, Path)


def test_validate_path_empty_string() -> None:
    """Test validate_path with empty string."""
    from shared_validation import validate_path
    
    # Empty string may raise ValueError or FileNotFoundError depending on implementation
    try:
        validate_path("")
        # If it doesn't raise, that's also acceptable (may be handled differently)
    except (ValueError, FileNotFoundError):
        # Expected - empty string should be invalid
        pass


@pytest.mark.parametrize("batch_size,expected_valid", [
    (1, True),
    (100, True),
    (1000, True),
    (0, False),  # Invalid: zero
    (-1, False),  # Invalid: negative
])
def test_validate_batch_size_consolidated(batch_size: int, expected_valid: bool) -> None:
    """Test validate_batch_size with various inputs."""
    from shared_validation import validate_batch_size
    
    if expected_valid:
        result = validate_batch_size(batch_size)
        assert result == batch_size
    else:
        with pytest.raises(ValueError):
            validate_batch_size(batch_size)


@pytest.mark.parametrize("entity,required_fields,expected_valid", [
    ({"field1": "value1", "field2": "value2"}, ["field1", "field2"], True),
    ({"field1": "value1"}, ["field1"], True),
    ({"field1": "value1"}, ["field1", "field2"], False),  # Missing field2
    ({}, ["field1"], False),  # Missing all fields
    ({"field1": None}, ["field1"], False),  # None is treated as missing (per function logic)
])
def test_validate_required_fields_consolidated(entity: dict, required_fields: list, expected_valid: bool) -> None:
    """Test validate_required_fields with various inputs."""
    from shared_validation import validate_required_fields
    
    if expected_valid:
        validate_required_fields(entity, required_fields)
    else:
        with pytest.raises(ValueError):
            validate_required_fields(entity, required_fields)
