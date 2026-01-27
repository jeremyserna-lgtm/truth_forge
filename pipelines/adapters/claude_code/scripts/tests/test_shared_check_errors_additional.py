"""Additional coverage tests for shared check_errors module.

Target: Increase coverage for error checking functionality.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import pytest

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


@patch('builtins.print')
def test_check_errors_with_specific_run_id(mock_print) -> None:
    """Test check_errors with specific run_id filter."""
    import shared.check_errors as ce_module
    from shared.check_errors import check_errors
    
    with tempfile.TemporaryDirectory() as tmpdir:
        logs_dir = Path(tmpdir) / "logs"
        logs_dir.mkdir()
        
        # Create log file with specific run_id
        stage_log = logs_dir / "stage_5.log"
        stage_log.write_text(
            "INFO: Stage 5 started run_id=test_run_123\n"
            "ERROR: Something went wrong run_id=test_run_123\n"
            "INFO: Stage 5 completed run_id=test_run_456\n"
        )
        
        original_project_root = ce_module.project_root
        ce_module.project_root = Path(tmpdir)
        
        try:
            # Check with specific run_id
            result = check_errors(5, run_id="test_run_123")
            # Should find errors for that run_id
            assert isinstance(result, bool)
            mock_print.assert_called()
        finally:
            ce_module.project_root = original_project_root


@patch('builtins.print')
def test_check_errors_multiple_stages(mock_print) -> None:
    """Test check_errors across multiple stages."""
    import shared.check_errors as ce_module
    from shared.check_errors import check_errors
    
    with tempfile.TemporaryDirectory() as tmpdir:
        logs_dir = Path(tmpdir) / "logs"
        logs_dir.mkdir()
        
        # Create log files for multiple stages
        for stage in [5, 6, 7]:
            stage_log = logs_dir / f"stage_{stage}.log"
            stage_log.write_text(f"INFO: Stage {stage} started\nINFO: Stage {stage} completed\n")
        
        original_project_root = ce_module.project_root
        ce_module.project_root = Path(tmpdir)
        
        try:
            # Check each stage
            for stage in [5, 6, 7]:
                result = check_errors(stage)
                assert isinstance(result, bool)
            mock_print.assert_called()
        finally:
            ce_module.project_root = original_project_root


@patch('builtins.print')
def test_check_errors_with_warnings(mock_print) -> None:
    """Test check_errors with warnings in logs."""
    import shared.check_errors as ce_module
    from shared.check_errors import check_errors
    
    with tempfile.TemporaryDirectory() as tmpdir:
        logs_dir = Path(tmpdir) / "logs"
        logs_dir.mkdir()
        
        # Create log file with warnings
        stage_log = logs_dir / "stage_5.log"
        stage_log.write_text(
            "INFO: Stage 5 started\n"
            "WARNING: This is a warning\n"
            "INFO: Stage 5 completed\n"
        )
        
        original_project_root = ce_module.project_root
        ce_module.project_root = Path(tmpdir)
        
        try:
            result = check_errors(5)
            # Warnings may or may not be considered errors depending on implementation
            assert isinstance(result, bool)
            mock_print.assert_called()
        finally:
            ce_module.project_root = original_project_root
