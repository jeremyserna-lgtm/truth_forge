"""Expanded tests for shared/utilities.py.

Target: 90%+ coverage of all utility functions.
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

# Mocks are set up in conftest.py


def test_get_full_table_id() -> None:
    """Test get_full_table_id function."""
    from shared.utilities import get_full_table_id
    
    table_id = get_full_table_id("test_table")
    
    assert isinstance(table_id, str)
    assert "test_table" in table_id


def test_validate_input_table_exists() -> None:
    """Test validate_input_table_exists function."""
    from shared.utilities import validate_input_table_exists
    from google.cloud import bigquery
    from google.api_core import exceptions as google_exceptions
    
    mock_client = Mock(spec=bigquery.Client)
    
    # Test table exists with rows
    mock_table = Mock()
    mock_table.num_rows = 10  # Has rows
    mock_client.get_table.return_value = mock_table
    result = validate_input_table_exists(mock_client, "test_table")
    assert result is True
    
    # Test table doesn't exist - raises ValueError
    mock_client.get_table.side_effect = google_exceptions.NotFound("Table not found")
    try:
        validate_input_table_exists(mock_client, "test_table")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "does not exist" in str(e)


def test_retry_with_backoff_success() -> None:
    """Test retry_with_backoff with successful call."""
    from shared.utilities import retry_with_backoff
    
    def successful_func():
        return "success"
    
    retried_func = retry_with_backoff(successful_func, max_retries=3, retry_delays=(1, 2, 4))
    result = retried_func()
    
    assert result == "success"


def test_retry_with_backoff_retry() -> None:
    """Test retry_with_backoff with retries."""
    from shared.utilities import retry_with_backoff, is_retryable_error
    from unittest.mock import patch
    
    call_count = [0]
    
    def failing_then_success():
        call_count[0] += 1
        if call_count[0] < 2:
            # Create a retryable error
            error = Exception("Temporary failure")
            # Make it retryable by checking
            if not is_retryable_error(error):
                # If not retryable by default, use a retryable exception type
                from google.api_core.exceptions import ServiceUnavailable
                raise ServiceUnavailable("Temporary failure")
            raise error
        return "success"
    
    # Mock time.sleep to speed up test
    with patch('shared.utilities.time.sleep'):
        retried_func = retry_with_backoff(failing_then_success, max_retries=3, retry_delays=(0.01, 0.02, 0.04))
        result = retried_func()
        
        assert result == "success"
        assert call_count[0] == 2


def test_get_pipeline_hold2_path() -> None:
    """Test get_pipeline_hold2_path function."""
    from shared.utilities import get_pipeline_hold2_path
    
    path = get_pipeline_hold2_path(stage=0, pipeline_name="claude_code")
    
    assert isinstance(path, Path)
    assert "stage_0" in str(path) or "hold2" in str(path)
