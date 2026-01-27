"""Comprehensive tests for shared utilities.

Target: 100% coverage of shared/utilities.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from shared.utilities import (
    retry_with_backoff,
    is_retryable_error,
    validate_input_table_exists,
    validate_gate_no_null_identity,
    verify_row_counts,
    create_fingerprint,
    chunk_list,
    safe_json_loads,
)


def test_create_fingerprint_basic() -> None:
    """Test create_fingerprint with basic inputs."""
    fp1 = create_fingerprint("test", "value")
    fp2 = create_fingerprint("test", "value")
    
    assert fp1 == fp2, "Same inputs should produce same fingerprint"
    assert len(fp1) == 32, "Fingerprint should be 32 chars"
    assert all(c in "0123456789abcdef" for c in fp1), "Fingerprint should be hex"


def test_create_fingerprint_different_inputs() -> None:
    """Test create_fingerprint produces different outputs for different inputs."""
    fp1 = create_fingerprint("test1")
    fp2 = create_fingerprint("test2")
    
    assert fp1 != fp2, "Different inputs should produce different fingerprints"


def test_create_fingerprint_with_prefix() -> None:
    """Test create_fingerprint with prefix."""
    fp1 = create_fingerprint("test", prefix="prefix")
    fp2 = create_fingerprint("test", prefix="prefix")
    fp3 = create_fingerprint("test", prefix="other")
    
    assert fp1 == fp2, "Same prefix should produce same fingerprint"
    assert fp1 != fp3, "Different prefix should produce different fingerprint"


def test_chunk_list_basic() -> None:
    """Test chunk_list with basic inputs."""
    lst = list(range(10))
    chunks = chunk_list(lst, 3)
    
    assert len(chunks) == 4, "Should have 4 chunks"
    assert chunks[0] == [0, 1, 2], "First chunk should be [0, 1, 2]"
    assert chunks[-1] == [9], "Last chunk should be [9]"


def test_chunk_list_exact_divisor() -> None:
    """Test chunk_list when list length is exact multiple of chunk size."""
    lst = list(range(9))
    chunks = chunk_list(lst, 3)
    
    assert len(chunks) == 3, "Should have 3 chunks"
    assert all(len(chunk) == 3 for chunk in chunks), "All chunks should be size 3"


def test_chunk_list_empty() -> None:
    """Test chunk_list with empty list."""
    chunks = chunk_list([], 3)
    assert chunks == [], "Empty list should produce empty chunks"


def test_safe_json_loads_valid() -> None:
    """Test safe_json_loads with valid JSON."""
    result = safe_json_loads('{"key": "value"}')
    assert result == {"key": "value"}, "Should parse valid JSON"


def test_safe_json_loads_invalid() -> None:
    """Test safe_json_loads with invalid JSON."""
    default = {"error": "parse failed"}
    result = safe_json_loads("invalid json", default=default)
    assert result == default, "Should return default on parse error"


def test_safe_json_loads_no_default() -> None:
    """Test safe_json_loads with invalid JSON and no default."""
    result = safe_json_loads("invalid json")
    assert result is None, "Should return None when no default provided"


def test_is_retryable_error_retryable() -> None:
    """Test is_retryable_error identifies retryable errors."""
    from google.api_core import exceptions as google_exceptions
    
    retryable_errors = [
        google_exceptions.ServiceUnavailable("Service unavailable"),
        google_exceptions.InternalServerError("Internal error"),
        ConnectionError("Connection failed"),
        TimeoutError("Timeout"),
    ]
    
    for error in retryable_errors:
        assert is_retryable_error(error), f"Should identify {type(error).__name__} as retryable"


def test_is_retryable_error_not_retryable() -> None:
    """Test is_retryable_error identifies non-retryable errors."""
    from google.api_core import exceptions as google_exceptions
    
    non_retryable_errors = [
        ValueError("Invalid value"),
        KeyError("Missing key"),
        google_exceptions.BadRequest("Bad request"),
    ]
    
    for error in non_retryable_errors:
        assert not is_retryable_error(error), f"Should identify {type(error).__name__} as non-retryable"


@patch("shared.utilities.time.sleep")
def test_retry_with_backoff_success(mock_sleep: Mock) -> None:
    """Test retry_with_backoff succeeds on first try."""
    func = Mock(return_value="success")
    
    wrapped_func = retry_with_backoff(func, max_retries=3)
    result = wrapped_func()
    
    assert result == "success"
    assert func.call_count == 1
    mock_sleep.assert_not_called()


@patch("shared.utilities.time.sleep")
def test_retry_with_backoff_retries(mock_sleep: Mock) -> None:
    """Test retry_with_backoff retries on retryable errors."""
    from google.api_core import exceptions as google_exceptions
    
    func = Mock(side_effect=[
        google_exceptions.ServiceUnavailable("Retryable"),
        "success"
    ])
    
    wrapped_func = retry_with_backoff(func, max_retries=3)
    result = wrapped_func()
    
    assert result == "success"
    assert func.call_count == 2
    assert mock_sleep.call_count == 1


@patch("shared.utilities.time.sleep")
def test_retry_with_backoff_max_retries(mock_sleep: Mock) -> None:
    """Test retry_with_backoff gives up after max retries."""
    from google.api_core import exceptions as google_exceptions
    
    func = Mock(side_effect=google_exceptions.ServiceUnavailable("Always fails"))
    
    wrapped_func = retry_with_backoff(func, max_retries=2)
    try:
        wrapped_func()
        assert False, "Should raise exception after max retries"
    except google_exceptions.ServiceUnavailable:
        pass
    
    assert func.call_count == 3  # max_retries + 1 = 3 attempts
    assert mock_sleep.call_count == 2  # 2 retries


@patch("shared.utilities.time.sleep")
def test_retry_with_backoff_non_retryable(mock_sleep: Mock) -> None:
    """Test retry_with_backoff doesn't retry non-retryable errors."""
    func = Mock(side_effect=ValueError("Non-retryable"))
    
    wrapped_func = retry_with_backoff(func, max_retries=3)
    try:
        wrapped_func()
        assert False, "Should raise exception immediately"
    except ValueError:
        pass
    
    assert func.call_count == 1
    mock_sleep.assert_not_called()


def test_validate_input_table_exists_success() -> None:
    """Test validate_input_table_exists when table exists."""
    from google.cloud import bigquery
    from unittest.mock import Mock
    
    mock_bq = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_bq.get_table.return_value = mock_table
    
    result = validate_input_table_exists(mock_bq, "project.dataset.table")
    
    assert result is True
    mock_bq.get_table.assert_called_once()


def test_validate_input_table_exists_not_found() -> None:
    """Test validate_input_table_exists when table doesn't exist."""
    from google.cloud import bigquery
    from google.api_core import exceptions as google_exceptions
    from unittest.mock import Mock
    
    mock_bq = Mock(spec=bigquery.Client)
    mock_bq.get_table.side_effect = google_exceptions.NotFound("Table not found")
    
    try:
        validate_input_table_exists(mock_bq, "project.dataset.table")
        assert False, "Should raise exception"
    except ValueError as e:
        assert "does not exist" in str(e).lower() or "not found" in str(e).lower()


def test_validate_gate_no_null_identity_success() -> None:
    """Test validate_gate_no_null_identity when no nulls."""
    from google.cloud import bigquery
    from unittest.mock import Mock
    
    mock_bq = Mock(spec=bigquery.Client)
    mock_row = Mock(null_count=0)
    mock_result = Mock()
    mock_result.__iter__ = Mock(return_value=iter([mock_row]))
    mock_query_job = Mock()
    mock_query_job.result.return_value = mock_result
    mock_bq.query.return_value = mock_query_job
    
    result, null_count = validate_gate_no_null_identity(mock_bq, "project.dataset.table", "entity_id")
    
    assert result is True
    assert null_count == 0


def test_validate_gate_no_null_identity_violation() -> None:
    """Test validate_gate_no_null_identity when nulls exist."""
    from google.cloud import bigquery
    from unittest.mock import Mock
    
    mock_bq = Mock(spec=bigquery.Client)
    mock_row = Mock(null_count=5)
    mock_result = Mock()
    mock_result.__iter__ = Mock(return_value=iter([mock_row]))
    mock_query_job = Mock()
    mock_query_job.result.return_value = mock_result
    mock_bq.query.return_value = mock_query_job
    
    try:
        validate_gate_no_null_identity(mock_bq, "project.dataset.table", "entity_id")
        assert False, "Should raise exception"
    except ValueError as e:
        assert "null" in str(e).lower()
        assert "5" in str(e)


def test_verify_row_counts_success() -> None:
    """Test verify_row_counts when counts match."""
    from google.cloud import bigquery
    from unittest.mock import Mock
    
    mock_bq = Mock(spec=bigquery.Client)
    mock_source = Mock(num_rows=100)
    mock_target = Mock(num_rows=100)
    mock_bq.get_table.side_effect = [mock_source, mock_target]
    
    source_count, target_count, is_valid = verify_row_counts(
        mock_bq, "source_table", "target_table"
    )
    
    assert source_count == 100
    assert target_count == 100
    assert is_valid is True


def test_verify_row_counts_mismatch() -> None:
    """Test verify_row_counts when counts don't match."""
    from google.cloud import bigquery
    from unittest.mock import Mock
    
    mock_bq = Mock(spec=bigquery.Client)
    mock_source = Mock(num_rows=100)
    mock_target = Mock(num_rows=50)
    mock_bq.get_table.side_effect = [mock_source, mock_target]
    
    source_count, target_count, is_valid = verify_row_counts(
        mock_bq, "source_table", "target_table", expected_ratio=1.0, tolerance=0.01
    )
    
    assert source_count == 100
    assert target_count == 50
    assert is_valid is False


def test_verify_row_counts_empty_source() -> None:
    """Test verify_row_counts when source is empty."""
    from google.cloud import bigquery
    from unittest.mock import Mock
    
    mock_bq = Mock(spec=bigquery.Client)
    mock_source = Mock(num_rows=0)
    mock_target = Mock(num_rows=0)
    mock_bq.get_table.side_effect = [mock_source, mock_target]
    
    source_count, target_count, is_valid = verify_row_counts(
        mock_bq, "source_table", "target_table"
    )
    
    assert source_count == 0
    assert target_count == 0
    assert is_valid is True  # Both empty is valid


def test_validate_input_table_exists_empty() -> None:
    """Test validate_input_table_exists when table is empty."""
    from google.cloud import bigquery
    from unittest.mock import Mock
    
    mock_bq = Mock(spec=bigquery.Client)
    mock_table = Mock(num_rows=0)
    mock_bq.get_table.return_value = mock_table
    
    try:
        validate_input_table_exists(mock_bq, "project.dataset.table")
        assert False, "Should raise exception for empty table"
    except ValueError as e:
        assert "empty" in str(e).lower()


def test_verify_row_counts_not_found() -> None:
    """Test verify_row_counts when table is not found."""
    from google.cloud import bigquery
    from google.api_core import exceptions as google_exceptions
    from unittest.mock import Mock
    
    mock_bq = Mock(spec=bigquery.Client)
    mock_bq.get_table.side_effect = google_exceptions.NotFound("Table not found")
    
    try:
        verify_row_counts(mock_bq, "source_table", "target_table")
        assert False, "Should raise exception"
    except ValueError as e:
        assert "not found" in str(e).lower()


def test_retry_with_backoff_custom_retryable_check() -> None:
    """Test retry_with_backoff with custom retryable check."""
    from unittest.mock import Mock, patch
    
    custom_check = Mock(return_value=True)
    func = Mock(side_effect=[ValueError("Custom retryable"), "success"])
    
    wrapped_func = retry_with_backoff(func, max_retries=1, retryable_check=custom_check)
    
    with patch("shared.utilities.time.sleep"):
        result = wrapped_func()
    
    assert result == "success"
    assert func.call_count == 2
    custom_check.assert_called_once()


def test_retry_with_backoff_exhausts_delays() -> None:
    """Test retry_with_backoff when retry delays are exhausted."""
    from google.api_core import exceptions as google_exceptions
    from unittest.mock import Mock, patch
    
    func = Mock(side_effect=google_exceptions.ServiceUnavailable("Always fails"))
    short_delays = (1, 1)  # Only 2 delays for 3 retries
    
    wrapped_func = retry_with_backoff(func, max_retries=3, retry_delays=short_delays)
    
    with patch("shared.utilities.time.sleep") as mock_sleep:
        try:
            wrapped_func()
            assert False, "Should raise exception"
        except google_exceptions.ServiceUnavailable:
            pass
    
    assert func.call_count == 4  # max_retries + 1
    assert mock_sleep.call_count == 3  # 3 retries


def test_retry_with_backoff_never_reaches_end() -> None:
    """Test retry_with_backoff never reaches the 'should never reach here' line."""
    # This test verifies the logic prevents reaching line 138
    # The function should always raise or return before reaching that line
    from google.api_core import exceptions as google_exceptions
    from unittest.mock import Mock, patch
    
    # Test that max_retries logic prevents reaching line 138
    func = Mock(side_effect=google_exceptions.ServiceUnavailable("Fails"))
    wrapped_func = retry_with_backoff(func, max_retries=0)  # No retries
    
    with patch("shared.utilities.time.sleep"):
        try:
            wrapped_func()
            assert False, "Should raise immediately"
        except google_exceptions.ServiceUnavailable:
            pass
    
    # Should raise on first attempt, never reach line 138
    assert func.call_count == 1


def test_verify_row_counts_with_ratio() -> None:
    """Test verify_row_counts with different expected ratios."""
    from google.cloud import bigquery
    from unittest.mock import Mock
    
    mock_bq = Mock(spec=bigquery.Client)
    mock_source = Mock(num_rows=100)
    mock_target = Mock(num_rows=200)  # 2:1 ratio
    mock_bq.get_table.side_effect = [mock_source, mock_target]
    
    source_count, target_count, is_valid = verify_row_counts(
        mock_bq, "source_table", "target_table", expected_ratio=2.0, tolerance=0.01
    )
    
    assert source_count == 100
    assert target_count == 200
    assert is_valid is True  # 200/100 = 2.0, matches expected ratio


def test_verify_row_counts_with_tolerance() -> None:
    """Test verify_row_counts with tolerance."""
    from google.cloud import bigquery
    from unittest.mock import Mock
    
    mock_bq = Mock(spec=bigquery.Client)
    mock_source = Mock(num_rows=100)
    mock_target = Mock(num_rows=101)  # 1% difference
    mock_bq.get_table.side_effect = [mock_source, mock_target]
    
    source_count, target_count, is_valid = verify_row_counts(
        mock_bq, "source_table", "target_table", expected_ratio=1.0, tolerance=0.02
    )
    
    assert source_count == 100
    assert target_count == 101
    assert is_valid is True  # Within 2% tolerance
