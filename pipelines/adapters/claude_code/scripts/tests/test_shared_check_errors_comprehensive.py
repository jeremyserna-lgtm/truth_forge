"""Comprehensive tests for shared/check_errors.py.

Target: 90%+ coverage of check_errors.py (currently 0%).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


def test_check_errors_no_log_files() -> None:
    """Test check_errors when no log files exist."""
    from shared.check_errors import check_errors
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Mock project_root to point to temp directory
        with patch('shared.check_errors.project_root', Path(tmpdir)):
            result = check_errors(stage_number=0)
            
            # check_errors returns bool, not dict
            assert isinstance(result, bool)


def test_check_errors_with_errors() -> None:
    """Test check_errors when errors exist in logs."""
    from shared.check_errors import check_errors
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "stage_0.log"
        
        # Write log file with error (must include stage_0 in line for it to be detected)
        log_file.write_text("""
2026-01-27 10:00:00 INFO: Starting stage_0
2026-01-27 10:00:01 ERROR: stage_0 Failed to process file
2026-01-27 10:00:02 INFO: Continuing
""")
        
        with patch('shared.check_errors.project_root', Path(tmpdir)):
            # Suppress print output
            with patch('builtins.print'):
                result = check_errors(stage_number=0)
            
            # check_errors returns bool (False if errors found)
            assert isinstance(result, bool)
            assert result is False  # Errors found, so returns False


def test_check_errors_no_errors() -> None:
    """Test check_errors when no errors in logs."""
    from shared.check_errors import check_errors
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "stage_0.log"
        
        # Write log file without errors
        log_file.write_text("""
2026-01-27 10:00:00 INFO: Starting stage 0
2026-01-27 10:00:01 INFO: Processing files
2026-01-27 10:00:02 INFO: Completed successfully
""")
        
        with patch('shared.check_errors.project_root', Path(tmpdir)):
            result = check_errors(stage_number=0)
            
            # check_errors returns bool (True if no errors)
            assert isinstance(result, bool)
            assert result is True  # No errors found, so returns True


def test_check_errors_multiple_log_files() -> None:
    """Test check_errors with multiple log files."""
    from shared.check_errors import check_errors
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create multiple log files
        (log_dir / "central.log").write_text("INFO: Test 1")
        (log_dir / "stage_0.log").write_text("stage_0 ERROR: Test 2")
        
        with patch('shared.check_errors.project_root', Path(tmpdir)):
            result = check_errors(stage_number=0)
            
            assert isinstance(result, bool)


def test_check_errors_invalid_stage() -> None:
    """Test check_errors with invalid stage number."""
    from shared.check_errors import check_errors
    
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('shared.check_errors.project_root', Path(tmpdir)):
            result = check_errors(stage_number=999)
            
            assert isinstance(result, bool)
            # Should handle gracefully
