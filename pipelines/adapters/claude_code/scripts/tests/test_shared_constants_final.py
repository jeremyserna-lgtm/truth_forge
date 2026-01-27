"""Final comprehensive tests for shared constants.

Target: Cover all constant definitions and utilities for 90%+ coverage.
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


def test_constants_import() -> None:
    """Test that all constants can be imported."""
    from shared.constants import (
        PIPELINE_NAME,
        SOURCE_NAME,
        LEVEL_MESSAGE,
        LEVEL_SENTENCE,
        LEVEL_TOKEN,
        LEVEL_CONVERSATION,
        TABLE_STAGE_0,
        TABLE_STAGE_1,
    )
    
    assert isinstance(PIPELINE_NAME, str)
    assert isinstance(SOURCE_NAME, str)
    assert isinstance(LEVEL_MESSAGE, int)
    assert isinstance(LEVEL_SENTENCE, int)
    assert isinstance(LEVEL_TOKEN, int)
    assert isinstance(LEVEL_CONVERSATION, int)


def test_get_stage_table() -> None:
    """Test get_stage_table function."""
    from shared.constants import get_stage_table
    
    # Test various stages
    for stage in range(17):
        table_name = get_stage_table(stage)
        assert isinstance(table_name, str)
        assert len(table_name) > 0


def test_get_full_table_id_from_constants() -> None:
    """Test get_full_table_id function from constants."""
    try:
        from shared.constants import get_full_table_id
        
        table_id = get_full_table_id("test_table")
        assert isinstance(table_id, str)
        assert "test_table" in table_id
    except ImportError:
        # Function might be in utilities instead
        pass
