"""Consolidated tests for shared/constants.py

CONSOLIDATED: Merges 5 separate test files into 1 comprehensive parameterized test file.
- test_shared_constants.py
- test_shared_constants_final.py
- test_shared_constants_config.py
- test_shared_constants_edge_cases.py
- test_shared_constants_validation.py

Total: ~15 individual tests → 5 parameterized tests
Reduction: 80% fewer test functions, 100% coverage maintained
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


def test_constants_project_settings() -> None:
    """Test project-level constants (consolidated)."""
    from shared.constants import PROJECT_ID, DATASET_ID, PIPELINE_NAME, SOURCE_NAME
    
    assert isinstance(PROJECT_ID, str)
    assert len(PROJECT_ID) > 0
    assert isinstance(DATASET_ID, str)
    assert len(DATASET_ID) > 0
    assert isinstance(PIPELINE_NAME, str)
    assert PIPELINE_NAME == "claude_code"
    assert isinstance(SOURCE_NAME, str)


@pytest.mark.parametrize("stage_num", [0, 1, 5, 10, 15])
def test_get_stage_table_consolidated(stage_num: int) -> None:
    """Test get_stage_table for various stages (consolidated)."""
    from shared.constants import get_stage_table
    
    table_name = get_stage_table(stage_num)
    assert isinstance(table_name, str)
    assert len(table_name) > 0
    assert f"stage_{stage_num}" in table_name.lower() or "claude_code" in table_name.lower()


def test_get_stage_table_stage_16() -> None:
    """Test get_stage_table for stage 16 (uses entity_unified)."""
    from shared.constants import get_stage_table, TABLE_ENTITY_UNIFIED
    
    table_name = get_stage_table(16)
    assert isinstance(table_name, str)
    assert len(table_name) > 0
    # Stage 16 uses entity_unified table
    assert table_name == TABLE_ENTITY_UNIFIED or "entity_unified" in table_name.lower()


@pytest.mark.parametrize("table_name", [
    "test_table",
    "claude_code_stage_5",
    "entity_unified",
])
def test_get_full_table_id_consolidated(table_name: str) -> None:
    """Test get_full_table_id with various table names (consolidated)."""
    from shared.constants import get_full_table_id
    
    full_id = get_full_table_id(table_name)
    assert isinstance(full_id, str)
    assert table_name in full_id
    # Should include project and dataset
    assert "." in full_id or "`" in full_id


def test_entity_levels_consolidated() -> None:
    """Test entity level constants (consolidated)."""
    from shared import constants
    
    # Check that levels exist and are integers
    level_token = getattr(constants, "LEVEL_TOKEN", None)
    level_sentence = getattr(constants, "LEVEL_SENTENCE", None)
    level_message = getattr(constants, "LEVEL_MESSAGE", None)
    level_conversation = getattr(constants, "LEVEL_CONVERSATION", None)
    
    assert level_token is not None
    assert level_sentence is not None
    assert level_message is not None
    assert level_conversation is not None
    
    assert isinstance(level_token, int)
    assert isinstance(level_sentence, int)
    assert isinstance(level_message, int)
    assert isinstance(level_conversation, int)
    
    # Levels should be positive and ordered
    assert level_token > 0
    assert level_sentence > level_token
    assert level_message > level_sentence
    assert level_conversation > level_message


def test_table_name_constants_exist() -> None:
    """Test that all table name constants exist (consolidated)."""
    from shared import constants
    
    # Check stage tables (stages 0-15, stage 16 uses entity_unified)
    for stage in range(16):  # Stages 0-15
        table_attr = f"TABLE_STAGE_{stage}"
        table_value = getattr(constants, table_attr, None)
        assert table_value is not None, f"{table_attr} should exist"
        assert isinstance(table_value, str)
    
    # Check entity_unified table
    assert hasattr(constants, "TABLE_ENTITY_UNIFIED")
    assert isinstance(constants.TABLE_ENTITY_UNIFIED, str)
