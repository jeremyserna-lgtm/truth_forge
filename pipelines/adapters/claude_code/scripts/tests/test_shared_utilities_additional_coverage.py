"""Additional coverage tests for shared/utilities.py

Target: Cover remaining functions not fully tested in consolidated tests.
Focus: Edge cases, error paths, and uncovered utility functions.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
from google.cloud import bigquery
from google.api_core import exceptions as google_exceptions

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


# =============================================================================
# VALIDATION UTILITIES - ADDITIONAL COVERAGE
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_validate_input_table_exists_not_found(mock_run_id, mock_logger) -> None:
    """Test validate_input_table_exists when table doesn't exist."""
    from shared.utilities import validate_input_table_exists
    from google.cloud.exceptions import NotFound
    
    mock_client = Mock(spec=bigquery.Client)
    mock_client.get_table.side_effect = NotFound("Table not found")
    
    with pytest.raises(NotFound):
        validate_input_table_exists(mock_client, "test_table")


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_validate_input_table_exists_success(mock_run_id, mock_logger) -> None:
    """Test validate_input_table_exists when table exists."""
    from shared.utilities import validate_input_table_exists
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.get_table.return_value = mock_table
    
    # Should not raise
    validate_input_table_exists(mock_client, "test_table")
    mock_client.get_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_validate_gate_no_null_identity_with_nulls(mock_run_id, mock_logger) -> None:
    """Test validate_gate_no_null_identity when nulls are found."""
    from shared.utilities import validate_gate_no_null_identity
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.null_count = 5  # Has nulls
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    with pytest.raises(ValueError, match="null.*identity"):
        validate_gate_no_null_identity(mock_client, "test_table", "test_field")


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_validate_gate_no_null_identity_no_nulls(mock_run_id, mock_logger) -> None:
    """Test validate_gate_no_null_identity when no nulls found."""
    from shared.utilities import validate_gate_no_null_identity
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.null_count = 0  # No nulls
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    # Should not raise
    validate_gate_no_null_identity(mock_client, "test_table", "test_field")


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_verify_row_counts_match(mock_run_id, mock_logger) -> None:
    """Test verify_row_counts when counts match."""
    from shared.utilities import verify_row_counts
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.cnt = 100
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    # Should not raise
    verify_row_counts(mock_client, "table1", "table2", expected_diff=0)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_verify_row_counts_mismatch(mock_run_id, mock_logger) -> None:
    """Test verify_row_counts when counts don't match."""
    from shared.utilities import verify_row_counts
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    # First query returns 100, second returns 50 (diff = 50, but expected_diff = 0)
    mock_row1 = Mock()
    mock_row1.cnt = 100
    mock_row2 = Mock()
    mock_row2.cnt = 50
    mock_query_job.result.side_effect = [iter([mock_row1]), iter([mock_row2])]
    mock_client.query.return_value = mock_query_job
    
    with pytest.raises(ValueError, match="row count"):
        verify_row_counts(mock_client, "table1", "table2", expected_diff=0)


# =============================================================================
# RETRY LOGIC - ADDITIONAL COVERAGE
# =============================================================================

def test_is_retryable_error_retryable() -> None:
    """Test is_retryable_error with retryable errors."""
    from shared.utilities import is_retryable_error
    
    assert is_retryable_error(google_exceptions.ServiceUnavailable("test"))
    assert is_retryable_error(google_exceptions.InternalServerError("test"))
    assert is_retryable_error(google_exceptions.TooManyRequests("test"))
    assert is_retryable_error(google_exceptions.DeadlineExceeded("test"))
    assert is_retryable_error(ConnectionError("test"))
    assert is_retryable_error(TimeoutError("test"))


def test_is_retryable_error_not_retryable() -> None:
    """Test is_retryable_error with non-retryable errors."""
    from shared.utilities import is_retryable_error
    
    assert not is_retryable_error(ValueError("test"))
    assert not is_retryable_error(KeyError("test"))
    assert not is_retryable_error(TypeError("test"))


@patch('time.sleep')
def test_retry_with_backoff_success_first_attempt(mock_sleep) -> None:
    """Test retry_with_backoff when function succeeds on first attempt."""
    from shared.utilities import retry_with_backoff
    
    def test_func() -> str:
        return "success"
    
    wrapped = retry_with_backoff(test_func)
    result = wrapped()
    
    assert result == "success"
    mock_sleep.assert_not_called()


@patch('time.sleep')
def test_retry_with_backoff_retries_on_retryable_error(mock_sleep) -> None:
    """Test retry_with_backoff retries on retryable errors."""
    from shared.utilities import retry_with_backoff
    
    attempt_count = 0
    
    def test_func() -> str:
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 2:
            raise google_exceptions.ServiceUnavailable("retryable")
        return "success"
    
    wrapped = retry_with_backoff(test_func, max_retries=3, retry_delays=(1, 2, 3))
    result = wrapped()
    
    assert result == "success"
    assert attempt_count == 2
    assert mock_sleep.call_count == 1  # Should have slept once


@patch('time.sleep')
def test_retry_with_backoff_raises_on_non_retryable_error(mock_sleep) -> None:
    """Test retry_with_backoff raises immediately on non-retryable errors."""
    from shared.utilities import retry_with_backoff
    
    def test_func() -> str:
        raise ValueError("non-retryable")
    
    wrapped = retry_with_backoff(test_func, max_retries=3)
    
    with pytest.raises(ValueError):
        wrapped()
    
    mock_sleep.assert_not_called()  # Should not retry


@patch('time.sleep')
def test_retry_with_backoff_exhausts_retries(mock_sleep) -> None:
    """Test retry_with_backoff exhausts retries and raises."""
    from shared.utilities import retry_with_backoff
    
    def test_func() -> str:
        raise google_exceptions.ServiceUnavailable("always fails")
    
    wrapped = retry_with_backoff(test_func, max_retries=2, retry_delays=(0.1, 0.1))
    
    with pytest.raises(google_exceptions.ServiceUnavailable):
        wrapped()
    
    assert mock_sleep.call_count == 2  # Should have retried 2 times


# =============================================================================
# DATA UTILITIES - ADDITIONAL EDGE CASES
# =============================================================================

def test_chunk_list_empty_list() -> None:
    """Test chunk_list with empty list."""
    from shared.utilities import chunk_list
    
    chunks = list(chunk_list([], 10))
    assert chunks == []


def test_chunk_list_single_chunk() -> None:
    """Test chunk_list where all items fit in one chunk."""
    from shared.utilities import chunk_list
    
    chunks = list(chunk_list([1, 2, 3], 10))
    assert len(chunks) == 1
    assert chunks[0] == [1, 2, 3]


def test_safe_json_loads_invalid_json() -> None:
    """Test safe_json_loads with invalid JSON."""
    from shared.utilities import safe_json_loads
    
    result = safe_json_loads("invalid json", default={})
    assert result == {}


def test_safe_json_loads_empty_string() -> None:
    """Test safe_json_loads with empty string."""
    from shared.utilities import safe_json_loads
    
    result = safe_json_loads("", default={})
    assert result == {}


def test_create_fingerprint_deterministic() -> None:
    """Test create_fingerprint produces same result for same inputs."""
    from shared.utilities import create_fingerprint
    
    fp1 = create_fingerprint("test", "data")
    fp2 = create_fingerprint("test", "data")
    
    assert fp1 == fp2
    assert len(fp1) == 32  # MD5 hash length


def test_create_fingerprint_different_inputs() -> None:
    """Test create_fingerprint produces different results for different inputs."""
    from shared.utilities import create_fingerprint
    
    fp1 = create_fingerprint("test1")
    fp2 = create_fingerprint("test2")
    
    assert fp1 != fp2
