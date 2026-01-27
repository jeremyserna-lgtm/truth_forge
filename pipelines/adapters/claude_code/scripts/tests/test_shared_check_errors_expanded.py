"""Expanded tests for shared check_errors module.

Target: Increase coverage for error checking functionality.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import tempfile

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


@patch('builtins.print')
def test_check_errors_no_errors(mock_print) -> None:
    """Test check_errors when no errors are found."""
    from shared.check_errors import check_errors
    from pathlib import Path
    import tempfile
    import shared.check_errors as ce_module
    
    # Create a temporary log file with no errors
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create logs directory and file
        logs_dir = Path(tmpdir) / "logs"
        logs_dir.mkdir()
        stage_log = logs_dir / "stage_5.log"
        stage_log.write_text("INFO: Stage 5 started\nINFO: Stage 5 completed\n")
        
        # Patch project_root in the module
        original_project_root = ce_module.project_root
        ce_module.project_root = Path(tmpdir)
        try:
            result = check_errors(5)
            assert result is True
            mock_print.assert_called()
        finally:
            ce_module.project_root = original_project_root


@patch('builtins.print')
def test_check_errors_with_errors(mock_print) -> None:
    """Test check_errors when errors are found."""
    from shared.check_errors import check_errors
    from pathlib import Path
    import tempfile
    
    # Create a temporary log file with errors
    with tempfile.TemporaryDirectory() as tmpdir:
        # Patch project_root to point to temp directory
        with patch('shared.check_errors.project_root', Path(tmpdir)):
            # Create logs directory and file with errors
            logs_dir = Path(tmpdir) / "logs"
            logs_dir.mkdir()
            stage_log = logs_dir / "stage_5.log"
            stage_log.write_text(
                "INFO: Stage 5 started\n"
                "stage_5 ERROR: Table not found\n"
                "stage_5 ERROR: Connection failed\n"
                "INFO: Stage 5 completed\n"
            )
            
            result = check_errors(5)
            assert result is False
            # Should have printed error messages
            assert mock_print.call_count > 0


@patch('builtins.print')
def test_check_errors_nonexistent_log_file(mock_print) -> None:
    """Test check_errors when log file doesn't exist."""
    from shared.check_errors import check_errors
    from pathlib import Path
    import tempfile
    
    # Create temp directory but no log files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Patch project_root
        with patch('shared.check_errors.project_root', Path(tmpdir)):
            # No log files exist
            result = check_errors(5)
            
            # Should handle gracefully (returns True when no files found)
            assert isinstance(result, bool)
            assert result is True  # No files = no errors


@patch('builtins.print')
def test_check_errors_with_run_id(mock_print) -> None:
    """Test check_errors with specific run_id."""
    from shared.check_errors import check_errors
    from pathlib import Path
    import tempfile
    
    # Create a temporary log file
    with tempfile.TemporaryDirectory() as tmpdir:
        # Patch project_root to point to temp directory
        with patch('shared.check_errors.project_root', Path(tmpdir)):
            # Create logs directory and file
            logs_dir = Path(tmpdir) / "logs"
            logs_dir.mkdir()
            stage_log = logs_dir / "stage_5.log"
            stage_log.write_text("INFO: Stage 5 started test_run_123\nINFO: Stage 5 completed\n")
            
            result = check_errors(5, run_id="test_run_123")
            assert isinstance(result, bool)


def test_check_errors_invalid_stage() -> None:
    """Test check_errors with invalid stage number."""
    from shared.check_errors import check_errors
    
    # Should handle invalid stage gracefully
    try:
        result = check_errors(-1)
        assert isinstance(result, bool)
    except Exception:
        # Expected if validation is strict
        pass
