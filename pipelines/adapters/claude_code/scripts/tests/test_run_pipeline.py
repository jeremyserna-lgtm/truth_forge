"""Tests for run_pipeline module.

Target: 90%+ coverage of run_pipeline.py
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

# Mocks are set up in conftest.py


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_run_stage_success(mock_run_id, mock_logger) -> None:
    """Test run_stage with successful execution."""
    from run_pipeline import run_stage
    
    mock_script = Path("/tmp/test_script.py")
    mock_script.write_text("#!/usr/bin/env python3\nprint('success')\n")
    mock_script.chmod(0o755)
    
    try:
        result = run_stage(
            stage_num=0,
            script_path=mock_script,
            dry_run=False,
        )
        
        assert result is True
    finally:
        mock_script.unlink(missing_ok=True)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_run_stage_failure(mock_run_id, mock_logger) -> None:
    """Test run_stage with failed execution."""
    from run_pipeline import run_stage
    
    mock_script = Path("/tmp/test_script_fail.py")
    mock_script.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(1)\n")
    mock_script.chmod(0o755)
    
    try:
        result = run_stage(
            stage_num=0,
            script_path=mock_script,
            dry_run=False,
        )
        
        assert result is False
    finally:
        mock_script.unlink(missing_ok=True)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_run_stage_timeout(mock_run_id, mock_logger) -> None:
    """Test run_stage handles timeout correctly."""
    from run_pipeline import run_stage
    import subprocess
    
    mock_script = Path("/tmp/test_script_timeout.py")
    mock_script.write_text("#!/usr/bin/env python3\nprint('test')\n")
    mock_script.chmod(0o755)
    
    try:
        # Test that run_stage handles TimeoutExpired exception
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=1)
            result = run_stage(
                stage_num=0,
                script_path=mock_script,
                dry_run=False,
            )
            
            # Should handle timeout and return False
            assert result is False
    finally:
        mock_script.unlink(missing_ok=True)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_run_stage_with_source_dir(mock_run_id, mock_logger) -> None:
    """Test run_stage with source directory."""
    from run_pipeline import run_stage
    
    mock_script = Path("/tmp/test_script_source.py")
    mock_script.write_text("#!/usr/bin/env python3\nprint('success')\n")
    mock_script.chmod(0o755)
    
    with patch("tempfile.TemporaryDirectory") as mock_tmp:
        mock_tmp.return_value.__enter__.return_value = "/tmp/test_source"
        
        try:
            result = run_stage(
                stage_num=0,
                script_path=mock_script,
                source_dir=Path("/tmp/test_source"),
                dry_run=False,
            )
            
            assert result is True
        finally:
            mock_script.unlink(missing_ok=True)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_run_stage_with_manifest(mock_run_id, mock_logger) -> None:
    """Test run_stage with manifest path."""
    from run_pipeline import run_stage
    
    mock_script = Path("/tmp/test_script_manifest.py")
    mock_script.write_text("#!/usr/bin/env python3\nprint('success')\n")
    mock_script.chmod(0o755)
    
    mock_manifest = Path("/tmp/test_manifest.json")
    mock_manifest.write_text('{"test": "data"}')
    
    try:
        result = run_stage(
            stage_num=0,
            script_path=mock_script,
            manifest_path=mock_manifest,
            dry_run=False,
        )
        
        assert result is True
    finally:
        mock_script.unlink(missing_ok=True)
        mock_manifest.unlink(missing_ok=True)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_run_stage_with_run_id(mock_run_id, mock_logger) -> None:
    """Test run_stage with run_id."""
    from run_pipeline import run_stage
    
    mock_script = Path("/tmp/test_script_runid.py")
    mock_script.write_text("#!/usr/bin/env python3\nprint('success')\n")
    mock_script.chmod(0o755)
    
    try:
        result = run_stage(
            stage_num=0,
            script_path=mock_script,
            run_id="test_run_123",
            dry_run=False,
        )
        
        assert result is True
    finally:
        mock_script.unlink(missing_ok=True)
