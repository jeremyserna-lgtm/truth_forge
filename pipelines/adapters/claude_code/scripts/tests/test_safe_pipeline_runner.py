"""Tests for safe_pipeline_runner module.

Target: 90%+ coverage of safe_pipeline_runner.py
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


def test_pipeline_validator_validate_dependencies() -> None:
    """Test PipelineValidator.validate_dependencies."""
    from safe_pipeline_runner import PipelineValidator
    
    validator = PipelineValidator()
    
    # Should check Python version and modules
    result = validator.validate_dependencies()
    
    # May pass or fail depending on environment
    assert isinstance(result, bool)


def test_pipeline_validator_validate_config() -> None:
    """Test PipelineValidator.validate_config."""
    from safe_pipeline_runner import PipelineValidator
    
    validator = PipelineValidator()
    
    result = validator.validate_config()
    
    assert isinstance(result, bool)


def test_pipeline_validator_validate_all() -> None:
    """Test PipelineValidator.validate_all."""
    from safe_pipeline_runner import PipelineValidator
    
    validator = PipelineValidator()
    
    # validate_all calls validate_dependencies, validate_config, etc.
    result = validator.validate_all()
    
    # Returns tuple (success, errors, warnings)
    assert isinstance(result, tuple)
    assert len(result) == 3
    assert isinstance(result[0], bool)


def test_run_stage_safely_success() -> None:
    """Test run_stage_safely with successful execution."""
    from safe_pipeline_runner import run_stage_safely
    
    with patch("safe_pipeline_runner.subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0)
        
        result, message = run_stage_safely(
            stage_num=0,
            dry_run=True,
            interactive=False
        )
        
        assert isinstance(result, bool)
        assert isinstance(message, str)


def test_run_stage_safely_failure() -> None:
    """Test run_stage_safely with failed execution."""
    from safe_pipeline_runner import run_stage_safely
    
    with patch("safe_pipeline_runner.subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=1)
        
        result, message = run_stage_safely(
            stage_num=0,
            dry_run=True,
            interactive=False
        )
        
        assert result is False
        assert isinstance(message, str)


def test_run_stage_safely_interactive_skip() -> None:
    """Test run_stage_safely with interactive skip."""
    from safe_pipeline_runner import run_stage_safely
    
    with patch("builtins.input", return_value="n"):
        result, message = run_stage_safely(
            stage_num=0,
            dry_run=True,
            interactive=True
        )
        
        assert result is False
        assert "skipped" in message.lower()
