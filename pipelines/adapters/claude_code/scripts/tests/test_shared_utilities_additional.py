"""Additional tests for shared utilities to reach 100% coverage.

Target: Cover remaining functions in shared/utilities.py
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

from shared.utilities import chunk_list, safe_json_loads, create_fingerprint


def test_chunk_list_single_chunk() -> None:
    """Test chunk_list when list fits in one chunk."""
    lst = list(range(5))
    chunks = chunk_list(lst, 10)
    
    assert len(chunks) == 1
    assert chunks[0] == lst


def test_chunk_list_type_generic() -> None:
    """Test chunk_list works with different types."""
    # Test with strings
    str_chunks = chunk_list(["a", "b", "c", "d"], 2)
    assert len(str_chunks) == 2
    assert str_chunks[0] == ["a", "b"]
    
    # Test with mixed types
    mixed = [1, "a", 2, "b"]
    mixed_chunks = chunk_list(mixed, 2)
    assert len(mixed_chunks) == 2


def test_safe_json_loads_none_input() -> None:
    """Test safe_json_loads with None input."""
    result = safe_json_loads(None, default="default")  # type: ignore
    assert result == "default"


def test_safe_json_loads_empty_string() -> None:
    """Test safe_json_loads with empty string."""
    result = safe_json_loads("", default="default")
    assert result == "default"


def test_create_fingerprint_empty_args() -> None:
    """Test create_fingerprint with no arguments."""
    fp = create_fingerprint()
    assert len(fp) == 32
    assert all(c in "0123456789abcdef" for c in fp)


def test_create_fingerprint_none_values() -> None:
    """Test create_fingerprint with None values."""
    fp1 = create_fingerprint(None, "test")
    fp2 = create_fingerprint(None, "test")
    
    assert fp1 == fp2
    assert len(fp1) == 32
