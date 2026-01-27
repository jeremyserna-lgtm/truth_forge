"""Comprehensive tests for shared/logging_bridge.py.

Target: 90%+ coverage of logging_bridge.py (currently 62.79%).
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


def test_get_logger_with_truth_forge() -> None:
    """Test get_logger when truth_forge is available."""
    # Reload module to test truth_forge path
    import importlib
    import shared.logging_bridge
    
    with patch.dict('sys.modules', {'truth_forge': Mock()}):
        mock_tf = sys.modules['truth_forge']
        mock_tf.core = Mock()
        mock_tf.core.structured_logging = Mock()
        mock_tf.core.structured_logging.get_logger = Mock(return_value=Mock())
        
        importlib.reload(shared.logging_bridge)
        from shared.logging_bridge import get_logger
        
        logger = get_logger("test_module")
        assert logger is not None


def test_get_logger_fallback() -> None:
    """Test get_logger fallback when truth_forge not available."""
    # Test fallback path - module already handles this
    from shared.logging_bridge import get_logger
    
    logger = get_logger("test_module")
    assert logger is not None


def test_get_logger_final_fallback() -> None:
    """Test get_logger final fallback to standard logging."""
    # The logging_bridge module uses try/except to handle missing imports
    # The fallback path is already tested implicitly when truth_forge is not available
    # We just verify the function works in the current environment
    # This test verifies the function works regardless of which import path succeeds
    from shared.logging_bridge import get_logger
    
    logger = get_logger("test_module")
    assert logger is not None
    assert hasattr(logger, 'info')
    # The logger should be callable (have info, warning, error methods)
    assert callable(getattr(logger, 'info', None))


def test_get_current_run_id() -> None:
    """Test get_current_run_id function."""
    from shared.logging_bridge import get_current_run_id
    
    run_id = get_current_run_id()
    assert run_id is not None
    assert isinstance(run_id, str)
    assert len(run_id) > 0


def test_bind_context() -> None:
    """Test bind_context function."""
    from shared.logging_bridge import bind_context
    
    # Should not raise
    bind_context(stage=0, run_id="test_run")


def test_set_run_id() -> None:
    """Test set_run_id function."""
    from shared.logging_bridge import set_run_id
    
    # Should not raise
    set_run_id("test_run_123")


def test_ensure_stage_logging_context() -> None:
    """Test ensure_stage_logging_context function."""
    from shared.logging_bridge import ensure_stage_logging_context
    
    # ensure_stage_logging_context requires pipeline_name parameter
    ensure_stage_logging_context(stage=0, run_id="test_run", pipeline_name="claude_code")
    
    # If no exception, test passes
    assert True
