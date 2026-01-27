"""Expanded tests for shared rollback module.

Target: Increase coverage for rollback functionality.
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


@patch('builtins.print')
def test_validate_stage_valid(mock_print) -> None:
    """Test validate_stage with valid stage numbers."""
    from shared.rollback import validate_stage
    
    assert validate_stage(0) == 0
    assert validate_stage(8) == 8
    assert validate_stage(16) == 16


@patch('builtins.print')
def test_validate_stage_invalid(mock_print) -> None:
    """Test validate_stage with invalid stage numbers."""
    from shared.rollback import validate_stage
    
    try:
        validate_stage(-1)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    
    try:
        validate_stage(17)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


@patch('builtins.print')
def test_validate_run_id_valid(mock_print) -> None:
    """Test validate_run_id with valid run IDs."""
    from shared.rollback import validate_run_id
    
    assert validate_run_id("run_123") == "run_123"
    assert validate_run_id("run-2026-01-27") == "run-2026-01-27"
    assert validate_run_id("test_run_abc123") == "test_run_abc123"


@patch('builtins.print')
def test_validate_run_id_invalid(mock_print) -> None:
    """Test validate_run_id with invalid run IDs."""
    from shared.rollback import validate_run_id
    
    try:
        validate_run_id("")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    
    try:
        validate_run_id("   ")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    
    try:
        validate_run_id("run with spaces")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


@patch('builtins.print')
def test_get_table_for_stage(mock_print) -> None:
    """Test get_table_for_stage function."""
    from shared.rollback import get_table_for_stage
    
    table_id = get_table_for_stage(5)
    
    assert isinstance(table_id, str)
    assert len(table_id) > 0


@patch('builtins.print')
def test_get_bigquery_client(mock_print) -> None:
    """Test get_bigquery_client function."""
    from shared.rollback import get_bigquery_client
    
    # Should return a client (or raise ImportError if dependencies missing)
    try:
        client = get_bigquery_client()
        assert client is not None
    except (ImportError, AttributeError):
        # Expected if dependencies not available
        pass


@patch('builtins.print')
@patch('shared.rollback.get_bigquery_client')
def test_rollback_stage_success(mock_get_client, mock_print) -> None:
    """Test rollback_stage with successful deletion."""
    from shared.rollback import rollback_stage
    from google.cloud import bigquery
    from google.cloud.bigquery import ScalarQueryParameter
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.get_table.return_value = mock_table
    
    # Mock count query
    mock_count_row = Mock()
    mock_count_row.cnt = 10
    mock_count_query_job = Mock()
    mock_count_query_job.result.return_value = iter([mock_count_row])
    
    # Mock delete query
    mock_delete_query_job = Mock()
    mock_delete_query_job.result.return_value = []  # No errors
    mock_delete_query_job.errors = []  # No errors
    
    def query_side_effect(query_str, job_config=None):
        if "COUNT(*)" in query_str:
            return mock_count_query_job
        elif "DELETE FROM" in query_str:
            return mock_delete_query_job
        return mock_count_query_job
    
    mock_client.query.side_effect = query_side_effect
    mock_get_client.return_value = mock_client
    
    result = rollback_stage(5, "test_run", confirm=True)
    
    # Should return True on success
    assert result is True


@patch('builtins.print')
@patch('builtins.input', return_value='no')
@patch('shared.rollback.get_bigquery_client')
def test_rollback_stage_cancelled(mock_get_client, mock_input, mock_print) -> None:
    """Test rollback_stage when user cancels."""
    from shared.rollback import rollback_stage
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.get_table.return_value = mock_table
    
    # Mock count query
    mock_count_row = Mock()
    mock_count_row.cnt = 10
    mock_count_query_job = Mock()
    mock_count_query_job.result.return_value = iter([mock_count_row])
    mock_client.query.return_value = mock_count_query_job
    mock_get_client.return_value = mock_client
    
    # When user says 'no', should return False
    result = rollback_stage(5, "test_run", confirm=False)
    
    assert result is False
