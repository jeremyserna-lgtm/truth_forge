"""Additional coverage tests for shared utilities.

Target: Increase coverage for utility functions not yet fully tested.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
from google.cloud.exceptions import ServiceUnavailable, InternalServerError

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from shared.utilities import is_retryable_error


def test_is_retryable_error_retryable_exceptions() -> None:
    """Test is_retryable_error with retryable exceptions."""
    # ServiceUnavailable is retryable
    assert is_retryable_error(ServiceUnavailable("Service unavailable")) is True
    
    # InternalServerError is retryable
    assert is_retryable_error(InternalServerError("Internal error")) is True


def test_is_retryable_error_non_retryable_exceptions() -> None:
    """Test is_retryable_error with non-retryable exceptions."""
    # ValueError is not retryable
    assert is_retryable_error(ValueError("Invalid input")) is False
    
    # KeyError is not retryable
    assert is_retryable_error(KeyError("Missing key")) is False
    
    # TypeError is not retryable
    assert is_retryable_error(TypeError("Wrong type")) is False


def test_is_retryable_error_connection_errors() -> None:
    """Test is_retryable_error with connection errors."""
    # Built-in ConnectionError is retryable
    connection_error = ConnectionError("Connection failed")
    assert is_retryable_error(connection_error) is True
    
    # TimeoutError is retryable
    timeout_error = TimeoutError("Timeout")
    assert is_retryable_error(timeout_error) is True


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_validate_input_table_exists_with_data(mock_run_id, mock_logger) -> None:
    """Test validate_input_table_exists with table that has data."""
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
    """Test validate_input_table_exists with empty table."""
    from shared.utilities import validate_input_table_exists
    from google.cloud import bigquery
    import pytest
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_table.num_rows = 0
    mock_client.get_table.return_value = mock_table
    
    with pytest.raises(ValueError, match="exists but is empty"):
        validate_input_table_exists(mock_client, "test_table")


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_validate_gate_no_null_identity_no_nulls(mock_run_id, mock_logger) -> None:
    """Test validate_gate_no_null_identity with no null identities."""
    from shared.utilities import validate_gate_no_null_identity
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.null_count = 0
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    is_valid, null_count = validate_gate_no_null_identity(mock_client, "test_table")
    
    assert is_valid is True
    assert null_count == 0
