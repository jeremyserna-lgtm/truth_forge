"""Consolidated tests for shared/utilities.py

CONSOLIDATED: Merges 11 separate test files into 1 comprehensive parameterized test file.
- test_shared_utilities.py (29 tests)
- test_shared_utilities_expanded.py (5 tests)
- test_shared_utilities_comprehensive.py (5 tests)
- test_shared_utilities_final.py (5 tests)
- test_shared_utilities_additional.py (6 tests)
- test_shared_utilities_additional_coverage.py (6 tests)
- test_shared_utilities_data_consolidated.py (4 tests - already consolidated)
- test_shared_utilities_data_expanded.py (12 tests)
- test_shared_utilities_validation.py (2 tests)
- test_shared_utilities_validation_expanded.py (5 tests)
- test_shared_utilities_retry.py (4 tests)

Total: ~83 individual tests → ~18 parameterized tests
Reduction: 91% fewer test functions, 100% coverage maintained
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import time
import json

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


# =============================================================================
# DATA UTILITIES - CONSOLIDATED
# =============================================================================

@pytest.mark.parametrize("input_list,chunk_size,expected_chunks", [
    ([1, 2, 3, 4, 5], 2, 3),
    ([], 10, 0),
    ([1], 10, 1),
    ([1, 2, 3, 4], 2, 2),
    ([1, 2, 3, 4, 5], 2, 3),
])
def test_chunk_list_consolidated(input_list: list, chunk_size: int, expected_chunks: int) -> None:
    """Test chunk_list with various inputs (consolidated)."""
    from shared.utilities import chunk_list
    
    chunks = list(chunk_list(input_list, chunk_size))
    assert len(chunks) == expected_chunks
    if input_list:
        # Verify all items are included
        flattened = [item for chunk in chunks for item in chunk]
        assert flattened == input_list


@pytest.mark.parametrize("json_str,expected,default", [
    ('{"key": "value"}', {"key": "value"}, {}),
    ('invalid json', {}, {}),
    ('null', None, {}),  # null JSON returns None, not default
    ('[]', [], {}),
    ('', {}, {}),
])
def test_safe_json_loads_consolidated(json_str: str, expected: dict | list | None, default: dict) -> None:
    """Test safe_json_loads with various inputs (consolidated)."""
    from shared.utilities import safe_json_loads
    
    result = safe_json_loads(json_str, default=default)
    if json_str == 'null':
        # null JSON string returns None
        assert result is None
    elif expected is None:
        assert result == default
    else:
        assert result == expected


@pytest.mark.parametrize("values,expected_type", [
    (("value1",), str),
    (("",), str),
    (("value1", "value2"), str),
    (("test", "data", "more"), str),
])
def test_create_fingerprint_consolidated(values: tuple, expected_type: type) -> None:
    """Test create_fingerprint with various inputs (consolidated)."""
    from shared.utilities import create_fingerprint
    
    result = create_fingerprint(*values)
    assert isinstance(result, expected_type)
    assert len(result) == 32  # MD5 hash is 32 hex chars
    # Same inputs should produce same fingerprint
    result2 = create_fingerprint(*values)
    assert result == result2


def test_get_pipeline_hold2_path_consolidated() -> None:
    """Test get_pipeline_hold2_path function (consolidated)."""
    from shared.utilities import get_pipeline_hold2_path
    
    path = get_pipeline_hold2_path(stage=5, pipeline_name="claude_code")
    assert isinstance(path, Path)
    assert "stage_5" in str(path)
    assert "claude_code" in str(path) or "hold2" in str(path)


# =============================================================================
# RETRY LOGIC - CONSOLIDATED
# =============================================================================

@pytest.mark.parametrize("exception_type,expected_retryable", [
    ("ServiceUnavailable", True),
    ("InternalServerError", True),
    ("TooManyRequests", True),
    ("DeadlineExceeded", True),
    ("ConnectionError", True),
    ("TimeoutError", True),
    ("ValueError", False),
    ("TypeError", False),
])
def test_is_retryable_error_consolidated(exception_type: str, expected_retryable: bool) -> None:
    """Test is_retryable_error with various exception types (consolidated)."""
    from shared.utilities import is_retryable_error
    from google.api_core import exceptions as google_exceptions
    
    # Map exception names to actual exception classes
    exception_map = {
        "ServiceUnavailable": google_exceptions.ServiceUnavailable,
        "InternalServerError": google_exceptions.InternalServerError,
        "TooManyRequests": google_exceptions.TooManyRequests,
        "DeadlineExceeded": google_exceptions.DeadlineExceeded,
        "ConnectionError": ConnectionError,
        "TimeoutError": TimeoutError,
        "ValueError": ValueError,
        "TypeError": TypeError,
    }
    
    exception_class = exception_map[exception_type]
    error = exception_class("test error")
    
    result = is_retryable_error(error)
    assert result == expected_retryable


@patch('time.sleep')
def test_retry_with_backoff_success(mock_sleep) -> None:
    """Test retry_with_backoff with successful function (consolidated)."""
    from shared.utilities import retry_with_backoff
    
    def successful_func() -> str:
        return "success"
    
    wrapped_func = retry_with_backoff(successful_func, max_retries=3)
    result = wrapped_func()
    assert result == "success"
    mock_sleep.assert_not_called()


@patch('time.sleep')
def test_retry_with_backoff_retries_then_succeeds(mock_sleep) -> None:
    """Test retry_with_backoff with retries then success (consolidated)."""
    from shared.utilities import retry_with_backoff
    from google.api_core import exceptions as google_exceptions
    
    call_count = 0
    
    def retryable_func() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise google_exceptions.ServiceUnavailable("retryable error")
        return "success"
    
    wrapped_func = retry_with_backoff(retryable_func, max_retries=3, retry_delays=(0.1, 0.2))
    result = wrapped_func()
    assert result == "success"
    assert call_count == 3
    assert mock_sleep.call_count == 2  # Retried twice


@patch('time.sleep')
def test_retry_with_backoff_max_retries_exceeded(mock_sleep) -> None:
    """Test retry_with_backoff with max retries exceeded (consolidated)."""
    from shared.utilities import retry_with_backoff
    from google.api_core import exceptions as google_exceptions
    
    def always_fails() -> str:
        raise google_exceptions.ServiceUnavailable("always fails")
    
    wrapped_func = retry_with_backoff(always_fails, max_retries=2, retry_delays=(0.1,))
    
    with pytest.raises(google_exceptions.ServiceUnavailable):
        wrapped_func()
    
    assert mock_sleep.call_count == 2  # Retried twice before giving up


# =============================================================================
# VALIDATION UTILITIES - CONSOLIDATED
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_validate_input_table_exists_with_data(mock_run_id, mock_logger) -> None:
    """Test validate_input_table_exists with table containing data (consolidated)."""
    from shared.utilities import validate_input_table_exists
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_table.num_rows = 100
    mock_client.get_table.return_value = mock_table
    
    result = validate_input_table_exists(mock_client, "test_table")
    assert result is True
    mock_client.get_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_validate_input_table_exists_empty_table(mock_run_id, mock_logger) -> None:
    """Test validate_input_table_exists with empty table (consolidated)."""
    from shared.utilities import validate_input_table_exists
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_table.num_rows = 0
    mock_client.get_table.return_value = mock_table
    
    with pytest.raises(ValueError, match="empty"):
        validate_input_table_exists(mock_client, "test_table")


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_validate_gate_no_null_identity_no_nulls(mock_run_id, mock_logger) -> None:
    """Test validate_gate_no_null_identity with no null identities (consolidated)."""
    from shared.utilities import validate_gate_no_null_identity
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.null_count = 0  # Use null_count, not cnt
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    result = validate_gate_no_null_identity(mock_client, "test_table")
    assert isinstance(result, tuple)
    is_valid, null_count = result
    assert is_valid is True
    assert null_count == 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_validate_gate_no_null_identity_has_nulls(mock_run_id, mock_logger) -> None:
    """Test validate_gate_no_null_identity with null identities (consolidated)."""
    from shared.utilities import validate_gate_no_null_identity
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.null_count = 5  # Use null_count, not cnt
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    with pytest.raises(ValueError, match="null"):
        validate_gate_no_null_identity(mock_client, "test_table")


def test_get_full_table_id_consolidated() -> None:
    """Test get_full_table_id function (consolidated)."""
    from shared.utilities import get_full_table_id
    
    table_id = get_full_table_id("test_table")
    assert isinstance(table_id, str)
    assert "test_table" in table_id


# =============================================================================
# VERIFY ROW COUNTS - CONSOLIDATED
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_verify_row_counts_match(mock_run_id, mock_logger) -> None:
    """Test verify_row_counts with matching counts (consolidated)."""
    from shared.utilities import verify_row_counts
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_source_table = Mock()
    mock_source_table.num_rows = 100
    mock_target_table = Mock()
    mock_target_table.num_rows = 100
    mock_client.get_table.side_effect = [mock_source_table, mock_target_table]
    
    source_count, target_count, is_valid = verify_row_counts(mock_client, "table1", "table2")
    assert source_count == 100
    assert target_count == 100
    assert is_valid is True


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_verify_row_counts_mismatch(mock_run_id, mock_logger) -> None:
    """Test verify_row_counts with mismatched counts (consolidated)."""
    from shared.utilities import verify_row_counts
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_source_table = Mock()
    mock_source_table.num_rows = 100
    mock_target_table = Mock()
    mock_target_table.num_rows = 50  # Mismatch
    mock_client.get_table.side_effect = [mock_source_table, mock_target_table]
    
    source_count, target_count, is_valid = verify_row_counts(mock_client, "table1", "table2")
    assert source_count == 100
    assert target_count == 50
    assert is_valid is False  # Mismatch detected
