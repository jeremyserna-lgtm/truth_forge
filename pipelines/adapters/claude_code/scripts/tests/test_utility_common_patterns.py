"""Common pattern tests for utility scripts.

Uses parameterized tests to cover common patterns across utility scripts,
dramatically reducing the number of individual test files needed.

Target: Cover 60-70% of utility script code with shared patterns.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


# Common utility script patterns
UTILITY_SCRIPTS = [
    ("run_pipeline", "run_pipeline", True),
    ("router_knowledge_atoms", "router_knowledge_atoms", True),
    ("safe_pipeline_runner", "safe_pipeline_runner", True),
]


@pytest.mark.parametrize("script_name,module_name,has_main", UTILITY_SCRIPTS)
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_utility_main_function_exists(mock_run_id, mock_logger, script_name, module_name, has_main) -> None:
    """Test that utility scripts have main() function."""
    if not has_main:
        pytest.skip(f"{script_name} does not have main function")
    
    try:
        module = __import__(module_name, fromlist=[''])
        main_func = getattr(module, 'main', None)
        
        if main_func is None:
            pytest.skip(f"{script_name} does not have main function")
        
        assert callable(main_func)
    except ImportError:
        pytest.skip(f"Could not import {module_name}")


@pytest.mark.parametrize("script_name,module_name,has_main", UTILITY_SCRIPTS)
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_utility_module_imports(mock_run_id, mock_logger, script_name, module_name, has_main) -> None:
    """Test that utility modules can be imported without errors."""
    try:
        module = __import__(module_name, fromlist=[''])
        assert module is not None
    except ImportError as e:
        pytest.fail(f"Failed to import {module_name}: {e}")


# Test run_pipeline specific patterns
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_run_pipeline_run_stage_exists(mock_run_id, mock_logger) -> None:
    """Test run_pipeline.run_stage function exists."""
    from run_pipeline import run_stage
    assert callable(run_stage)


# Test router_knowledge_atoms specific patterns
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_router_knowledge_atoms_functions_exist(mock_run_id, mock_logger) -> None:
    """Test router_knowledge_atoms key functions exist."""
    from router_knowledge_atoms import (
        read_pipeline_hold2,
        mark_atom_retrieved,
        process_stage_atoms,
    )
    
    assert callable(read_pipeline_hold2)
    assert callable(mark_atom_retrieved)
    assert callable(process_stage_atoms)


# Test safe_pipeline_runner specific patterns
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_safe_pipeline_runner_validator_exists(mock_run_id, mock_logger) -> None:
    """Test PipelineValidator class exists."""
    from safe_pipeline_runner import PipelineValidator
    
    validator = PipelineValidator()
    assert hasattr(validator, 'validate_dependencies')
    assert hasattr(validator, 'validate_config')
    assert hasattr(validator, 'validate_all')
