"""Comprehensive tests for shared utilities validation functions.

Target: 90%+ coverage of validation utilities.
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


def test_validate_gate_no_null_identity() -> None:
    """Test validate_gate_no_null_identity function."""
    from shared.utilities import validate_gate_no_null_identity
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.null_count = 0
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    # validate_gate_no_null_identity returns tuple (bool, int)
    result = validate_gate_no_null_identity(mock_client, "test_table")
    
    assert isinstance(result, tuple)
    assert len(result) == 2
    is_valid, null_count = result
    assert isinstance(is_valid, bool)
    assert isinstance(null_count, int)
    assert is_valid is True
    assert null_count == 0


def test_verify_row_counts() -> None:
    """Test verify_row_counts function."""
    from shared.utilities import verify_row_counts
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    
    # Mock table objects with num_rows
    mock_source_table = Mock()
    mock_source_table.num_rows = 100
    mock_target_table = Mock()
    mock_target_table.num_rows = 100
    
    mock_client.get_table.side_effect = [mock_source_table, mock_target_table]
    
    # verify_row_counts returns tuple (source_count, target_count, is_valid)
    source_count, target_count, is_valid = verify_row_counts(mock_client, "source_table", "target_table")
    
    assert isinstance(source_count, int)
    assert isinstance(target_count, int)
    assert isinstance(is_valid, bool)
    assert source_count == 100
    assert target_count == 100
    assert is_valid is True
