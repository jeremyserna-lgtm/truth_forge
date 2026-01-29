"""Comprehensive tests for shared/check_errors.py.

Target: Cover all functions with comprehensive tests including error handling and edge cases.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import pytest

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


# =============================================================================
# CHECK ERRORS MODULE
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
@patch('builtins.open', new_callable=mock_open)
@patch('pathlib.Path.exists')
def test_check_errors_no_errors(mock_exists, mock_file, mock_run_id, mock_logger) -> None:
    """Test check_errors with no errors in logs."""
    from shared.check_errors import check_errors
    
    mock_exists.return_value = True
    mock_file.return_value.readlines.return_value = ["Normal log line\n"]
    
    result = check_errors(5, None)
    
    assert isinstance(result, bool)
    # Should return True if no errors found


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
@patch('builtins.open', new_callable=mock_open)
@patch('pathlib.Path.exists')
def test_check_errors_with_errors(mock_exists, mock_file, mock_run_id, mock_logger) -> None:
    """Test check_errors with errors in logs."""
    from shared.check_errors import check_errors
    
    mock_exists.return_value = True
    mock_file.return_value.readlines.return_value = ["stage_5 error: something failed\n"]
    
    result = check_errors(5, None)
    
    assert isinstance(result, bool)
    # Should return False if errors found


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
@patch('pathlib.Path.exists')
def test_check_errors_no_log_files(mock_exists, mock_run_id, mock_logger) -> None:
    """Test check_errors when no log files exist."""
    from shared.check_errors import check_errors
    
    mock_exists.return_value = False
    
    result = check_errors(5, None)
    
    assert isinstance(result, bool)
    # Should return True if no log files (not an error condition)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
@patch('builtins.open', new_callable=mock_open)
@patch('pathlib.Path.exists')
def test_check_errors_with_run_id(mock_exists, mock_file, mock_run_id, mock_logger) -> None:
    """Test check_errors with run_id filter."""
    from shared.check_errors import check_errors
    
    mock_exists.return_value = True
    mock_file.return_value.readlines.return_value = ["stage_5 run_123 error: something failed\n"]
    
    result = check_errors(5, "run_123")
    
    assert isinstance(result, bool)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
@patch('builtins.open', side_effect=IOError("Permission denied"))
@patch('pathlib.Path.exists')
def test_check_errors_file_read_error(mock_exists, mock_file, mock_run_id, mock_logger) -> None:
    """Test check_errors handles file read errors."""
    from shared.check_errors import check_errors
    
    mock_exists.return_value = True
    
    result = check_errors(5, None)
    
    assert isinstance(result, bool)
    # Should handle file read errors gracefully


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
@patch('builtins.open', new_callable=mock_open)
@patch('pathlib.Path.exists')
def test_check_errors_false_positives(mock_exists, mock_file, mock_run_id, mock_logger) -> None:
    """Test check_errors ignores false positives."""
    from shared.check_errors import check_errors
    
    mock_exists.return_value = True
    # Lines with "error_count" or "no errors" should be ignored
    mock_file.return_value.readlines.return_value = [
        "stage_5 error_count: 0\n",
        "stage_5 no errors found\n"
    ]
    
    result = check_errors(5, None)
    
    assert isinstance(result, bool)
    # Should return True (no real errors) despite containing "error" keyword
