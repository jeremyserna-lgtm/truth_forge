"""Comprehensive tests for safe_pipeline_runner.py.

Target: 90%+ coverage of safe_pipeline_runner.py (currently ~48%).
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


def test_pipeline_validator_init() -> None:
    """Test PipelineValidator initialization."""
    from safe_pipeline_runner import PipelineValidator
    
    validator = PipelineValidator()
    
    assert hasattr(validator, 'errors')
    assert hasattr(validator, 'warnings')
    assert isinstance(validator.errors, list)
    assert isinstance(validator.warnings, list)


def test_pipeline_validator_validate_dependencies() -> None:
    """Test PipelineValidator.validate_dependencies."""
    from safe_pipeline_runner import PipelineValidator
    
    validator = PipelineValidator()
    
    with patch('builtins.print'):
        result = validator.validate_dependencies()
        
        assert isinstance(result, bool)


def test_pipeline_validator_validate_config() -> None:
    """Test PipelineValidator.validate_config."""
    from safe_pipeline_runner import PipelineValidator
    
    validator = PipelineValidator()
    
    with patch('builtins.print'):
        with patch.dict('os.environ', {'GOOGLE_CLOUD_PROJECT': 'test-project'}):
            result = validator.validate_config()
            
            assert isinstance(result, bool)


def test_pipeline_validator_validate_data_sources() -> None:
    """Test PipelineValidator.validate_data_sources."""
    from safe_pipeline_runner import PipelineValidator
    import tempfile
    
    validator = PipelineValidator()
    
    with patch('builtins.print'):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = validator.validate_data_sources(source_dir=Path(tmpdir))
            
            assert isinstance(result, bool)


def test_pipeline_validator_validate_stage_scripts() -> None:
    """Test PipelineValidator.validate_stage_scripts."""
    from safe_pipeline_runner import PipelineValidator
    
    validator = PipelineValidator()
    
    with patch('builtins.print'):
        result = validator.validate_stage_scripts()
        
        assert isinstance(result, bool)


def test_pipeline_validator_validate_all() -> None:
    """Test PipelineValidator.validate_all."""
    from safe_pipeline_runner import PipelineValidator
    
    validator = PipelineValidator()
    
    with patch('builtins.print'):
        result = validator.validate_all()
        
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], bool)  # success
        assert isinstance(result[1], list)  # errors
        assert isinstance(result[2], list)  # warnings


def test_run_stage_safely_success() -> None:
    """Test run_stage_safely with successful execution."""
    from safe_pipeline_runner import run_stage_safely
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0)
        
        with patch('builtins.print'):
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
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=1)
        
        with patch('builtins.print'):
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
    
    with patch('builtins.input', return_value="n"):
        with patch('builtins.print'):
            result, message = run_stage_safely(
                stage_num=0,
                dry_run=True,
                interactive=True
            )
            
            assert result is False
            assert "skipped" in message.lower() or "cancel" in message.lower()
