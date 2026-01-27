"""Comprehensive tests for shared utilities.

Target: Cover all remaining utility functions for 90%+ coverage.
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


def test_is_retryable_error() -> None:
    """Test is_retryable_error function."""
    from shared.utilities import is_retryable_error
    from google.api_core import exceptions as google_exceptions
    
    # Retryable errors
    assert is_retryable_error(google_exceptions.ServiceUnavailable("test")) is True
    assert is_retryable_error(google_exceptions.InternalServerError("test")) is True
    assert is_retryable_error(google_exceptions.TooManyRequests("test")) is True
    assert is_retryable_error(ConnectionError("test")) is True
    
    # Non-retryable errors
    assert is_retryable_error(ValueError("test")) is False
    assert is_retryable_error(TypeError("test")) is False


def test_retry_with_backoff_max_retries() -> None:
    """Test retry_with_backoff with max retries exceeded."""
    from shared.utilities import retry_with_backoff
    from google.api_core import exceptions as google_exceptions
    
    call_count = [0]
    
    def failing_func():
        call_count[0] += 1
        raise google_exceptions.ServiceUnavailable("Temporary failure")
    
    wrapped = retry_with_backoff(failing_func, max_retries=2, retry_delays=(0.01, 0.02))
    
    with patch('time.sleep'):  # Speed up test
        try:
            wrapped()
            assert False, "Should have raised exception"
        except google_exceptions.ServiceUnavailable:
            pass  # Expected
    
    # Should have been called max_retries + 1 times (initial + retries)
    assert call_count[0] == 3  # 1 initial + 2 retries


def test_get_full_table_id_variations() -> None:
    """Test get_full_table_id with various inputs."""
    from shared.utilities import get_full_table_id
    
    # Basic usage
    table_id = get_full_table_id("test_table")
    assert isinstance(table_id, str)
    assert "test_table" in table_id
    
    # With project and dataset
    table_id2 = get_full_table_id("test_table", project="test_project", dataset="test_dataset")
    assert isinstance(table_id2, str)
    assert "test_project" in table_id2
    assert "test_dataset" in table_id2


def test_validate_input_table_exists_not_found() -> None:
    """Test validate_input_table_exists when table not found."""
    from shared.utilities import validate_input_table_exists
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound
    
    mock_client = Mock(spec=bigquery.Client)
    mock_client.get_table.side_effect = NotFound("Table not found")
    
    try:
        validate_input_table_exists(mock_client, "nonexistent_table")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


def test_validate_input_table_exists_empty_table() -> None:
    """Test validate_input_table_exists with empty table."""
    from shared.utilities import validate_input_table_exists
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_table.num_rows = 0
    mock_client.get_table.return_value = mock_table
    
    try:
        validate_input_table_exists(mock_client, "empty_table")
        assert False, "Should have raised ValueError for empty table"
    except ValueError:
        pass  # Expected
