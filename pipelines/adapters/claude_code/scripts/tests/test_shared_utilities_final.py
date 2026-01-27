"""Final comprehensive tests for shared utilities.

Target: Cover remaining utility functions for 90%+ coverage.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import time

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


def test_chunk_list_edge_cases() -> None:
    """Test chunk_list with edge cases."""
    from shared.utilities import chunk_list
    
    # Empty list
    result = list(chunk_list([], 10))
    assert result == []
    
    # Single item
    result = list(chunk_list([1], 10))
    assert result == [[1]]
    
    # Exact multiple
    result = list(chunk_list([1, 2, 3, 4], 2))
    assert result == [[1, 2], [3, 4]]
    
    # Not exact multiple
    result = list(chunk_list([1, 2, 3, 4, 5], 2))
    assert result == [[1, 2], [3, 4], [5]]


def test_safe_json_loads_edge_cases() -> None:
    """Test safe_json_loads with edge cases."""
    from shared.utilities import safe_json_loads
    
    # Valid JSON
    result = safe_json_loads('{"key": "value"}')
    assert result == {"key": "value"}
    
    # Invalid JSON
    result = safe_json_loads('invalid json')
    assert result is None
    
    # None input
    result = safe_json_loads(None)
    assert result is None
    
    # Empty string
    result = safe_json_loads('')
    assert result is None


def test_create_fingerprint_variations() -> None:
    """Test create_fingerprint with various inputs."""
    from shared.utilities import create_fingerprint
    
    # Single string
    fp1 = create_fingerprint("test")
    assert isinstance(fp1, str)
    assert len(fp1) > 0
    
    # Multiple args
    fp2 = create_fingerprint("test", "data", "123")
    assert isinstance(fp2, str)
    
    # With prefix
    fp3 = create_fingerprint("test", prefix="PREFIX")
    assert isinstance(fp3, str)
    assert fp3 != fp1  # Should be different


def test_retry_with_backoff_exception_handling() -> None:
    """Test retry_with_backoff with various exception scenarios."""
    from shared.utilities import retry_with_backoff
    from google.api_core import exceptions as google_exceptions
    
    # Function that succeeds
    def success_func():
        return "success"
    
    wrapped = retry_with_backoff(success_func, max_retries=3, retry_delays=(0.01, 0.02))
    result = wrapped()
    assert result == "success"
    
    # Function that raises non-retryable exception
    def non_retryable_func():
        raise ValueError("Not retryable")
    
    wrapped = retry_with_backoff(non_retryable_func, max_retries=3, retry_delays=(0.01, 0.02))
    try:
        wrapped()
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


def test_get_pipeline_hold2_path_variations() -> None:
    """Test get_pipeline_hold2_path with various inputs."""
    from shared.utilities import get_pipeline_hold2_path
    
    # Test different stages
    path1 = get_pipeline_hold2_path(0, "claude_code")
    path2 = get_pipeline_hold2_path(16, "claude_code")
    
    assert isinstance(path1, Path)
    assert isinstance(path2, Path)
    assert path1 != path2  # Different stages should have different paths
