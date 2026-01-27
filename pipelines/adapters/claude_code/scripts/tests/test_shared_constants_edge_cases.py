"""Edge case tests for shared constants.

Target: 100% coverage including edge cases.
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

from shared.constants import get_stage_table, get_full_table_id


def test_get_stage_table_edge_cases() -> None:
    """Test get_stage_table edge cases."""
    # Test stage 16 (special case)
    table_16 = get_stage_table(16)
    assert table_16 == "entity_unified"
    
    # Test valid stages
    for stage in range(16):
        table = get_stage_table(stage)
        assert table is not None
        assert isinstance(table, str)
    
    # Test invalid stage (should raise)
    try:
        get_stage_table(17)
        assert False, "Should raise ValueError for stage 17"
    except ValueError:
        pass
    
    # Test negative stage (should raise)
    try:
        get_stage_table(-1)
        assert False, "Should raise ValueError for stage -1"
    except ValueError:
        pass


def test_get_full_table_id_all_combinations() -> None:
    """Test get_full_table_id with all parameter combinations."""
    # Default
    table_id = get_full_table_id("test_table")
    assert "test_table" in table_id
    
    # With project only
    table_id_p = get_full_table_id("test_table", project="custom_project")
    assert "custom_project" in table_id_p
    assert "test_table" in table_id_p
    
    # With dataset only
    table_id_d = get_full_table_id("test_table", dataset="custom_dataset")
    assert "custom_dataset" in table_id_d
    assert "test_table" in table_id_d
    
    # With both
    table_id_both = get_full_table_id("test_table", project="p", dataset="d")
    assert "p.d.test_table" == table_id_both
