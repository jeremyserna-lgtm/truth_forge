"""Expanded tests for shared utilities data functions.

Target: Increase coverage for data utility functions like chunk_list,
safe_json_loads, create_fingerprint, and get_pipeline_hold2_path.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import json

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


def test_chunk_list_large_list() -> None:
    """Test chunk_list with a large list."""
    from shared.utilities import chunk_list
    
    large_list = list(range(1000))
    chunks = chunk_list(large_list, chunk_size=100)
    
    assert len(chunks) == 10
    assert all(len(chunk) == 100 for chunk in chunks)
    assert sum(len(chunk) for chunk in chunks) == 1000


def test_chunk_list_single_element_chunks() -> None:
    """Test chunk_list with chunk_size=1."""
    from shared.utilities import chunk_list
    
    test_list = [1, 2, 3, 4, 5]
    chunks = chunk_list(test_list, chunk_size=1)
    
    assert len(chunks) == 5
    assert all(len(chunk) == 1 for chunk in chunks)
    assert chunks == [[1], [2], [3], [4], [5]]


def test_chunk_list_larger_than_list() -> None:
    """Test chunk_list with chunk_size larger than list."""
    from shared.utilities import chunk_list
    
    test_list = [1, 2, 3]
    chunks = chunk_list(test_list, chunk_size=10)
    
    assert len(chunks) == 1
    assert chunks[0] == [1, 2, 3]


def test_safe_json_loads_valid_complex() -> None:
    """Test safe_json_loads with valid complex JSON."""
    from shared.utilities import safe_json_loads
    
    complex_json = '{"nested": {"array": [1, 2, 3], "string": "test"}}'
    result = safe_json_loads(complex_json)
    
    assert isinstance(result, dict)
    assert result["nested"]["array"] == [1, 2, 3]
    assert result["nested"]["string"] == "test"


def test_safe_json_loads_invalid_with_custom_default() -> None:
    """Test safe_json_loads with invalid JSON and custom default."""
    from shared.utilities import safe_json_loads
    
    invalid_json = "{ invalid json }"
    default_value = {"error": "parse_failed"}
    result = safe_json_loads(invalid_json, default=default_value)
    
    assert result == default_value


def test_safe_json_loads_none_input() -> None:
    """Test safe_json_loads with None input."""
    from shared.utilities import safe_json_loads
    
    result = safe_json_loads(None, default="default")
    assert result == "default"


def test_create_fingerprint_single_value() -> None:
    """Test create_fingerprint with single value."""
    from shared.utilities import create_fingerprint
    
    fp1 = create_fingerprint("test")
    fp2 = create_fingerprint("test")
    
    assert isinstance(fp1, str)
    assert len(fp1) == 32
    assert fp1 == fp2  # Deterministic


def test_create_fingerprint_multiple_values() -> None:
    """Test create_fingerprint with multiple values."""
    from shared.utilities import create_fingerprint
    
    fp1 = create_fingerprint("value1", "value2", "value3")
    fp2 = create_fingerprint("value1", "value2", "value3")
    fp3 = create_fingerprint("value1", "value2", "value4")
    
    assert fp1 == fp2  # Same inputs = same fingerprint
    assert fp1 != fp3  # Different inputs = different fingerprint


def test_create_fingerprint_with_prefix() -> None:
    """Test create_fingerprint with prefix."""
    from shared.utilities import create_fingerprint
    
    fp1 = create_fingerprint("test", prefix="PREFIX")
    fp2 = create_fingerprint("test", prefix="PREFIX")
    fp3 = create_fingerprint("test", prefix="OTHER")
    
    assert fp1 == fp2  # Same prefix = same fingerprint
    assert fp1 != fp3  # Different prefix = different fingerprint


def test_create_fingerprint_empty_args() -> None:
    """Test create_fingerprint with no arguments."""
    from shared.utilities import create_fingerprint
    
    fp = create_fingerprint()
    
    assert isinstance(fp, str)
    assert len(fp) == 32


def test_get_pipeline_hold2_path_different_stages() -> None:
    """Test get_pipeline_hold2_path with different stage numbers."""
    from shared.utilities import get_pipeline_hold2_path
    
    path_0 = get_pipeline_hold2_path(0, "claude_code")
    path_5 = get_pipeline_hold2_path(5, "claude_code")
    path_16 = get_pipeline_hold2_path(16, "claude_code")
    
    assert isinstance(path_0, Path)
    assert isinstance(path_5, Path)
    assert isinstance(path_16, Path)
    assert "stage_0" in str(path_0)
    assert "stage_5" in str(path_5)
    assert "stage_16" in str(path_16)


def test_get_pipeline_hold2_path_creates_directory() -> None:
    """Test that get_pipeline_hold2_path creates directory if needed."""
    from shared.utilities import get_pipeline_hold2_path
    
    path = get_pipeline_hold2_path(99, "test_pipeline")
    
    assert path.parent.exists()
    assert path.parent.is_dir()
