"""Comprehensive tests for run_pipeline.py.

Target: 90%+ coverage of run_pipeline.py (currently ~40%).
"""
from __future__ import annotations

import sys
import subprocess
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
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0)
        
        script_path = scripts_dir / "stage_1" / "claude_code_stage_1.py"
        result = run_stage(
            stage_num=1,
            script_path=script_path,
            dry_run=True
        )
        
        assert result is True


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_run_stage_failure(mock_run_id, mock_logger) -> None:
    """Test run_stage with failed execution."""
    from run_pipeline import run_stage
    import tempfile
    
    with patch('subprocess.run') as mock_run:
        # run_stage uses check=True, so a non-zero returncode will raise CalledProcessError
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(returncode=1, cmd=["python"], stderr=b"Error occurred")
        
        script_path = scripts_dir / "stage_1" / "claude_code_stage_1.py"
        result = run_stage(
            stage_num=1,
            script_path=script_path,
            dry_run=True
        )
        
        assert result is False


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_run_stage_timeout(mock_run_id, mock_logger) -> None:
    """Test run_stage with timeout."""
    from run_pipeline import run_stage
    
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired("python", 30)
        
        script_path = scripts_dir / "stage_1" / "claude_code_stage_1.py"
        result = run_stage(
            stage_num=1,
            script_path=script_path,
            dry_run=True
        )
        
        assert result is False


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_run_stage_with_source_dir(mock_run_id, mock_logger) -> None:
    """Test run_stage with source_dir argument."""
    from run_pipeline import run_stage
    import tempfile
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = scripts_dir / "stage_1" / "claude_code_stage_1.py"
            result = run_stage(
                stage_num=1,
                script_path=script_path,
                source_dir=Path(tmpdir),
                dry_run=True
            )
            
            assert result is True


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_run_stage_with_run_id(mock_run_id, mock_logger) -> None:
    """Test run_stage with run_id argument."""
    from run_pipeline import run_stage
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0)
        
        script_path = scripts_dir / "stage_1" / "claude_code_stage_1.py"
        result = run_stage(
            stage_num=1,
            script_path=script_path,
            run_id="custom_run_123",
            dry_run=True
        )
        
        assert result is True


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_run_stage_script_not_found(mock_run_id, mock_logger) -> None:
    """Test run_stage when script doesn't exist."""
    from run_pipeline import run_stage
    
    non_existent = Path("/nonexistent/script.py")
    result = run_stage(
        stage_num=1,
        script_path=non_existent,
        dry_run=True
    )
    
    assert result is False
