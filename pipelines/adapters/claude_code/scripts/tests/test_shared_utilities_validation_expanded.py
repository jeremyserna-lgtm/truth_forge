"""Expanded tests for shared utilities validation functions.

Target: Increase coverage for validation utilities.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


def test_validate_gate_no_null_identity_with_nulls() -> None:
    """Test validate_gate_no_null_identity when nulls are found."""
    from shared.utilities import validate_gate_no_null_identity
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.null_count = 5  # Has nulls
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    # Function raises ValueError when nulls found
    with pytest.raises(ValueError, match="THE GATE VIOLATION.*5.*null"):
        validate_gate_no_null_identity(mock_client, "test_table")


def test_verify_row_counts_mismatch() -> None:
    """Test verify_row_counts when counts don't match."""
    from shared.utilities import verify_row_counts
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    
    mock_source_table = Mock()
    mock_source_table.num_rows = 100
    mock_target_table = Mock()
    mock_target_table.num_rows = 50  # Mismatch
    
    mock_client.get_table.side_effect = [mock_source_table, mock_target_table]
    
    source_count, target_count, is_valid = verify_row_counts(mock_client, "source_table", "target_table")
    
    assert isinstance(source_count, int)
    assert isinstance(target_count, int)
    assert isinstance(is_valid, bool)
    assert source_count == 100
    assert target_count == 50
    assert is_valid is False


def test_verify_row_counts_source_missing() -> None:
    """Test verify_row_counts when source table doesn't exist."""
    from shared.utilities import verify_row_counts
    from google.cloud import bigquery
    from google.api_core.exceptions import NotFound
    
    mock_client = Mock(spec=bigquery.Client)
    mock_client.get_table.side_effect = NotFound("Table not found")
    
    try:
        verify_row_counts(mock_client, "nonexistent_table", "target_table")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Table not found" in str(e)


def test_validate_input_table_exists_with_rows() -> None:
    """Test validate_input_table_exists when table exists with rows."""
    from shared.utilities import validate_input_table_exists
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_table.num_rows = 100  # Has rows
    mock_client.get_table.return_value = mock_table
    
    result = validate_input_table_exists(mock_client, "test_table")
    
    assert result is True


def test_validate_input_table_exists_empty_table() -> None:
    """Test validate_input_table_exists when table is empty."""
    from shared.utilities import validate_input_table_exists
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_table.num_rows = 0  # Empty table
    mock_client.get_table.return_value = mock_table
    
    try:
        validate_input_table_exists(mock_client, "empty_table")
        assert False, "Should have raised ValueError for empty table"
    except ValueError:
        pass  # Expected
