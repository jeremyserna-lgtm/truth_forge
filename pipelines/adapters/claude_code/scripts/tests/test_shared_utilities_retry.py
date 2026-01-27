"""Comprehensive tests for retry utilities.

Target: Cover all retry logic paths for 90%+ coverage.
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


def test_retry_with_backoff_success_immediate() -> None:
    """Test retry_with_backoff with immediate success."""
    from shared.utilities import retry_with_backoff
    
    call_count = [0]
    
    def success_func():
        call_count[0] += 1
        return "success"
    
    wrapped = retry_with_backoff(success_func, max_retries=3, retry_delays=(0.01, 0.02))
    result = wrapped()
    
    assert result == "success"
    assert call_count[0] == 1  # Should only be called once


def test_retry_with_backoff_retry_then_success() -> None:
    """Test retry_with_backoff with retry then success."""
    from shared.utilities import retry_with_backoff
    from google.api_core import exceptions as google_exceptions
    
    call_count = [0]
    
    def retry_then_success():
        call_count[0] += 1
        if call_count[0] == 1:
            raise google_exceptions.ServiceUnavailable("Temporary failure")
        return "success"
    
    wrapped = retry_with_backoff(retry_then_success, max_retries=3, retry_delays=(0.01, 0.02))
    
    with patch('time.sleep'):  # Speed up test
        result = wrapped()
    
    assert result == "success"
    assert call_count[0] == 2  # Called twice (initial + 1 retry)


def test_retry_with_backoff_non_retryable_error() -> None:
    """Test retry_with_backoff with non-retryable error."""
    from shared.utilities import retry_with_backoff
    
    def non_retryable_func():
        raise ValueError("Not retryable")
    
    wrapped = retry_with_backoff(non_retryable_func, max_retries=3, retry_delays=(0.01, 0.02))
    
    try:
        wrapped()
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


def test_is_retryable_error_comprehensive() -> None:
    """Test is_retryable_error with all error types."""
    from shared.utilities import is_retryable_error
    from google.api_core import exceptions as google_exceptions
    
    # All retryable errors
    assert is_retryable_error(google_exceptions.ServiceUnavailable("test")) is True
    assert is_retryable_error(google_exceptions.InternalServerError("test")) is True
    assert is_retryable_error(google_exceptions.TooManyRequests("test")) is True
    assert is_retryable_error(google_exceptions.DeadlineExceeded("test")) is True
    assert is_retryable_error(ConnectionError("test")) is True
    
    # Non-retryable errors
    assert is_retryable_error(ValueError("test")) is False
    assert is_retryable_error(TypeError("test")) is False
    assert is_retryable_error(KeyError("test")) is False
    assert is_retryable_error(AttributeError("test")) is False
