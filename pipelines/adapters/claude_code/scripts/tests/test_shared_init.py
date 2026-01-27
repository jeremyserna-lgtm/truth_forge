"""Tests for shared __init__ module.

Target: 90%+ coverage of shared/__init__.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def test_shared_imports() -> None:
    """Test that shared module can be imported."""
    from shared import (
        PROJECT_ID,
        DATASET_ID,
        PIPELINE_NAME,
        SOURCE_NAME,
        TABLE_STAGE_0,
        get_stage_table,
        get_full_table_id,
        get_config,
        get_stage_config,
        retry_with_backoff,
        validate_input_table_exists,
    )
    
    assert PROJECT_ID is not None
    assert DATASET_ID is not None
    assert PIPELINE_NAME is not None
    assert SOURCE_NAME is not None
    assert TABLE_STAGE_0 is not None


def test_shared_all_exports() -> None:
    """Test that __all__ exports work correctly."""
    import shared
    
    # Check that key exports are available
    assert hasattr(shared, 'PIPELINE_NAME')
    assert hasattr(shared, 'get_stage_table')
    assert hasattr(shared, 'get_config')
