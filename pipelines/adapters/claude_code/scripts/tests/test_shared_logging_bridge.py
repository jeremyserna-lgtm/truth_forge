"""Tests for shared logging_bridge module.

Target: 90%+ coverage of shared/logging_bridge.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch, Mock

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def test_get_logger_truth_forge_available() -> None:
    """Test get_logger when truth_forge is available."""
    # Test that get_logger works (uses truth_forge if available, fallback otherwise)
    from shared.logging_bridge import get_logger
    
    logger = get_logger("test")
    assert logger is not None


def test_get_current_run_id() -> None:
    """Test get_current_run_id function."""
    from shared.logging_bridge import get_current_run_id
    
    run_id = get_current_run_id()
    assert run_id is not None
    assert isinstance(run_id, str)
    assert len(run_id) > 0


def test_ensure_stage_logging_context() -> None:
    """Test ensure_stage_logging_context function."""
    from shared.logging_bridge import ensure_stage_logging_context
    
    # Should not raise
    ensure_stage_logging_context(stage=0, run_id="test_run", pipeline_name="test_pipeline")


def test_bind_context() -> None:
    """Test bind_context function."""
    from shared.logging_bridge import bind_context
    
    # Should not raise (may be no-op in fallback)
    bind_context(test="value")


def test_set_run_id() -> None:
    """Test set_run_id function."""
    from shared.logging_bridge import set_run_id
    
    # Should not raise (may be no-op in fallback)
    set_run_id("test_run")
