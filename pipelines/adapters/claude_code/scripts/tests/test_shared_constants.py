"""Tests for shared constants module.

Target: 100% coverage of shared/constants.py
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

from shared.constants import (
    PROJECT_ID,
    DATASET_ID,
    PIPELINE_NAME,
    SOURCE_NAME,
    TABLE_STAGE_0,
    TABLE_STAGE_1,
    TABLE_STAGE_2,
    TABLE_STAGE_3,
    TABLE_STAGE_4,
    TABLE_STAGE_5,
    TABLE_STAGE_6,
    TABLE_STAGE_7,
    TABLE_STAGE_8,
    TABLE_STAGE_9,
    TABLE_STAGE_10,
    TABLE_STAGE_11,
    TABLE_STAGE_12,
    TABLE_STAGE_13,
    TABLE_STAGE_14,
    TABLE_STAGE_15,
    TABLE_ENTITY_UNIFIED,
    LEVEL_TOKEN,
    LEVEL_SENTENCE,
    LEVEL_MESSAGE,
    LEVEL_CONVERSATION,
    get_stage_table,
    get_full_table_id,
)


def test_constants_exist() -> None:
    """Test that all constants are defined."""
    assert PROJECT_ID is not None
    assert DATASET_ID is not None
    assert PIPELINE_NAME is not None
    assert SOURCE_NAME is not None


def test_table_names_exist() -> None:
    """Test that all table name constants exist."""
    tables = [
        TABLE_STAGE_0, TABLE_STAGE_1, TABLE_STAGE_2, TABLE_STAGE_3,
        TABLE_STAGE_4, TABLE_STAGE_5, TABLE_STAGE_6, TABLE_STAGE_7,
        TABLE_STAGE_8, TABLE_STAGE_9, TABLE_STAGE_10, TABLE_STAGE_11,
        TABLE_STAGE_12, TABLE_STAGE_13, TABLE_STAGE_14, TABLE_STAGE_15,
        TABLE_ENTITY_UNIFIED,
    ]
    for table in tables:
        assert table is not None
        assert isinstance(table, str)
        assert len(table) > 0


def test_entity_levels_exist() -> None:
    """Test that all entity level constants exist."""
    levels = [LEVEL_TOKEN, LEVEL_SENTENCE, LEVEL_MESSAGE, LEVEL_CONVERSATION]
    for level in levels:
        assert level is not None
        assert isinstance(level, int)
        assert level > 0


def test_get_stage_table() -> None:
    """Test get_stage_table function."""
    table_0 = get_stage_table(0)
    assert table_0 == TABLE_STAGE_0
    
    table_5 = get_stage_table(5)
    assert table_5 == TABLE_STAGE_5
    
    table_16 = get_stage_table(16)
    assert table_16 == TABLE_ENTITY_UNIFIED  # Stage 16 uses entity_unified


def test_get_full_table_id() -> None:
    """Test get_full_table_id function."""
    table_id = get_full_table_id("test_table")
    assert "test_table" in table_id
    assert PROJECT_ID in table_id
    assert DATASET_ID in table_id
    
    # Test with project override
    table_id_custom = get_full_table_id("test_table", project="custom_project")
    assert "custom_project" in table_id_custom
    
    # Test with dataset override
    table_id_custom_ds = get_full_table_id("test_table", dataset="custom_dataset")
    assert "custom_dataset" in table_id_custom_ds
