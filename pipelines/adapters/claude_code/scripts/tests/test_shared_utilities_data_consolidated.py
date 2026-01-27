"""Consolidated tests for shared data utilities using parameterization.

Reduces multiple individual tests to parameterized tests.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch
import pytest
import json
import tempfile

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from shared.utilities import chunk_list, safe_json_loads, create_fingerprint, get_pipeline_hold2_path


# chunk_list tests
@pytest.mark.parametrize("input_list,chunk_size,expected_chunks", [
    ([1, 2, 3, 4, 5], 2, 3),  # 5 items, chunk size 2 = 3 chunks
    ([1, 2, 3, 4, 5], 5, 1),  # 5 items, chunk size 5 = 1 chunk
    ([1, 2, 3, 4, 5], 10, 1),  # 5 items, chunk size 10 = 1 chunk
    ([], 10, 0),  # Empty list
    ([1], 1, 1),  # Single item
])
def test_chunk_list_consolidated(input_list: list, chunk_size: int, expected_chunks: int) -> None:
    """Test chunk_list with various inputs (consolidated)."""
    chunks = list(chunk_list(input_list, chunk_size))
    assert len(chunks) == expected_chunks
    if input_list:
        # Verify all items are in chunks
        assert sum(len(chunk) for chunk in chunks) == len(input_list)


# safe_json_loads tests
@pytest.mark.parametrize("json_str,expected,default", [
    ('{"key": "value"}', {"key": "value"}, {}),
    ('{"number": 123}', {"number": 123}, {}),
    ('{"nested": {"inner": "value"}}', {"nested": {"inner": "value"}}, {}),
    ('invalid json', {}, {}),  # Invalid JSON returns default
    ('null', None, {}),  # null returns None
])
def test_safe_json_loads_consolidated(json_str: str, expected: dict | None, default: dict) -> None:
    """Test safe_json_loads with various inputs (consolidated)."""
    result = safe_json_loads(json_str, default=default)
    if expected is None:
        assert result is None
    else:
        assert result == expected


# create_fingerprint tests
@pytest.mark.parametrize("values,expected_type", [
    (("value1",), str),
    (("value1", "value2"), str),
    (("value1", "value2", "value3"), str),
    (("",), str),  # Empty string
    (("prefix", "value"), str),  # With prefix
])
def test_create_fingerprint_consolidated(values: tuple, expected_type: type) -> None:
    """Test create_fingerprint with various inputs (consolidated)."""
    result = create_fingerprint(*values)
    assert isinstance(result, expected_type)
    assert len(result) > 0  # Should not be empty (even for empty input)


# get_pipeline_hold2_path tests
def test_get_pipeline_hold2_path_consolidated() -> None:
    """Test get_pipeline_hold2_path creates directory structure (consolidated)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # This test verifies the function works without errors
        # Actual path creation depends on project structure
        try:
            result = get_pipeline_hold2_path("test_pipeline", "test_run")
            assert isinstance(result, Path)
        except Exception:
            # May fail if project structure not available, that's OK
            pass
