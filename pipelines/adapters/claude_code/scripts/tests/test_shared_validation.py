"""Comprehensive tests for shared_validation module.

Target: 100% coverage of shared_validation.py (security-critical)
"""
from __future__ import annotations

import sys
from pathlib import Path

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
    validate_entity_id,
    validate_path,
    validate_stage_number,
    validate_required_fields,
    validate_batch_size,
)


def test_validate_table_id_valid() -> None:
    """Test validate_table_id with valid table IDs."""
    # Valid formats
    assert validate_table_id("project.dataset.table") == "project.dataset.table"
    assert validate_table_id("dataset.table") == "dataset.table"
    assert validate_table_id("table_name") == "table_name"
    assert validate_table_id("table-name") == "table-name"
    assert validate_table_id("table_name_123") == "table_name_123"


def test_validate_table_id_invalid_empty() -> None:
    """Test validate_table_id with empty string."""
    try:
        validate_table_id("")
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_validate_table_id_invalid_type() -> None:
    """Test validate_table_id with invalid type."""
    try:
        validate_table_id(None)  # type: ignore
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_validate_table_id_sql_injection_patterns() -> None:
    """Test validate_table_id rejects SQL injection patterns."""
    dangerous = [
        "table; DROP TABLE",
        "table--comment",
        "table/*comment*/",
        "table' OR '1'='1",
        "table UNION SELECT",
    ]
    
    for dangerous_id in dangerous:
        try:
            validate_table_id(dangerous_id)
            assert False, f"Should reject: {dangerous_id}"
        except ValueError:
            pass


def test_validate_table_id_dangerous_keywords() -> None:
    """Test validate_table_id rejects dangerous SQL keywords."""
    dangerous = [
        "DROP TABLE test",
        "DELETE FROM test",
        "TRUNCATE test",
        "ALTER TABLE test",
        "CREATE TABLE test",
        "EXEC test",
        "EXECUTE test",
        "UNION SELECT",
    ]
    
    for dangerous_id in dangerous:
        try:
            validate_table_id(dangerous_id)
            assert False, f"Should reject: {dangerous_id}"
        except ValueError:
            pass


def test_validate_run_id_valid() -> None:
    """Test validate_run_id with valid run IDs."""
    assert validate_run_id("run_123") == "run_123"
    assert validate_run_id("run-123") == "run-123"
    assert validate_run_id("run_123_abc") == "run_123_abc"
    assert validate_run_id("abc123") == "abc123"


def test_validate_run_id_invalid() -> None:
    """Test validate_run_id with invalid run IDs."""
    invalid = [
        "",
        "run with spaces",
        "run;drop",
        "run' OR '1'='1",
        None,  # type: ignore
    ]
    
    for invalid_id in invalid:
        try:
            validate_run_id(invalid_id)  # type: ignore
            assert False, f"Should reject: {invalid_id}"
        except (ValueError, TypeError):
            pass


def test_validate_entity_id_valid() -> None:
    """Test validate_entity_id with valid entity IDs."""
    assert validate_entity_id("entity_123") == "entity_123"
    assert validate_entity_id("entity-123") == "entity-123"
    assert validate_entity_id("abc123def456") == "abc123def456"


def test_validate_entity_id_invalid() -> None:
    """Test validate_entity_id with invalid entity IDs."""
    invalid = [
        "",
        "entity;drop",  # SQL injection pattern
        "entity--comment",  # SQL comment
        "entity/*comment*/",  # SQL comment
        None,  # type: ignore
    ]
    
    for invalid_id in invalid:
        try:
            validate_entity_id(invalid_id)  # type: ignore
            assert False, f"Should reject: {invalid_id}"
        except (ValueError, TypeError):
            pass


def test_validate_entity_id_too_long() -> None:
    """Test validate_entity_id rejects IDs that are too long."""
    long_id = "a" * 501  # Over 500 char limit
    
    try:
        validate_entity_id(long_id)
        assert False, "Should reject ID over 500 chars"
    except ValueError as e:
        assert "too long" in str(e).lower()


def test_validate_path_valid_in_project() -> None:
    """Test validate_path with valid paths in project."""
    # Use a path within the project
    project_file = project_root / "test_file.txt"
    project_file.write_text("test")
    
    try:
        # Should not raise when path is in project
        result = validate_path(project_file, must_be_in_project=True)
        assert result is not None
    finally:
        project_file.unlink(missing_ok=True)


def test_validate_path_traversal() -> None:
    """Test validate_path rejects path traversal."""
    try:
        validate_path("../../../etc/passwd")
        assert False, "Should reject path traversal"
    except ValueError:
        pass


def test_validate_path_with_allow_home() -> None:
    """Test validate_path with allow_home_directory=True."""
    import tempfile
    from pathlib import Path as PathLib
    
    # Create file in home directory
    home_file = PathLib.home() / "test_validation_file.txt"
    home_file.write_text("test")
    
    try:
        # Should work with allow_home_directory=True
        result = validate_path(
            home_file,
            must_be_in_project=True,
            allow_home_directory=True
        )
        assert result is not None
    finally:
        home_file.unlink(missing_ok=True)


def test_validate_stage_number_valid() -> None:
    """Test validate_stage_number with valid stage numbers."""
    for stage in range(17):
        assert validate_stage_number(stage) == stage


def test_validate_stage_number_invalid() -> None:
    """Test validate_stage_number with invalid stage numbers."""
    # validate_stage_number allows 0-100 (reasonable upper bound)
    invalid = [-1, 101, -100]
    
    for invalid_stage in invalid:
        try:
            validate_stage_number(invalid_stage)
            assert False, f"Should reject: {invalid_stage}"
        except ValueError:
            pass


def test_validate_stage_number_valid_range() -> None:
    """Test validate_stage_number with valid range (0-100)."""
    # Stage 17 is valid (within 0-100 range)
    assert validate_stage_number(17) == 17
    assert validate_stage_number(0) == 0
    assert validate_stage_number(100) == 100


def test_validate_stage_number_type_conversion() -> None:
    """Test validate_stage_number converts string to int."""
    # Should convert string to int
    assert validate_stage_number("5") == 5  # type: ignore
    
    # Should reject invalid string
    try:
        validate_stage_number("not_a_number")  # type: ignore
        assert False, "Should reject non-numeric string"
    except ValueError:
        pass


def test_validate_required_fields_present() -> None:
    """Test validate_required_fields when all fields present."""
    record = {"field1": "value1", "field2": "value2", "field3": "value3"}
    required = ["field1", "field2"]
    
    # Should not raise
    validate_required_fields(record, required)


def test_validate_required_fields_missing() -> None:
    """Test validate_required_fields when fields missing."""
    record = {"field1": "value1"}
    required = ["field1", "field2"]
    
    try:
        validate_required_fields(record, required)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "field2" in str(e)


def test_validate_required_fields_empty_record() -> None:
    """Test validate_required_fields with empty record."""
    record = {}
    required = ["field1"]
    
    try:
        validate_required_fields(record, required)
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_validate_batch_size_valid() -> None:
    """Test validate_batch_size with valid sizes."""
    assert validate_batch_size(100) == 100
    assert validate_batch_size(1000) == 1000
    assert validate_batch_size(1) == 1
    assert validate_batch_size(10000) == 10000


def test_validate_batch_size_too_small() -> None:
    """Test validate_batch_size with size too small."""
    try:
        validate_batch_size(0)
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_validate_batch_size_too_large() -> None:
    """Test validate_batch_size with size too large."""
    try:
        validate_batch_size(20000)
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_validate_batch_size_custom_limits() -> None:
    """Test validate_batch_size with custom limits."""
    assert validate_batch_size(50, min_size=10, max_size=100) == 50
    
    try:
        validate_batch_size(5, min_size=10, max_size=100)
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    
    try:
        validate_batch_size(200, min_size=10, max_size=100)
        assert False, "Should raise ValueError"
    except ValueError:
        pass
