"""Tests for shared constants validation.

Target: Cover validation function.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Test that validation runs on import
def test_constants_validation_runs() -> None:
    """Test that _validate_config runs on import."""
    # The validation runs when constants is imported
    # If it fails, the import would fail
    from shared import constants  # noqa: F401
    
    # If we get here, validation passed
    assert True


def test_get_stage_table_validation() -> None:
    """Test get_stage_table validation logic."""
    from shared.constants import get_stage_table
    
    # Test all valid stages
    for stage in range(17):
        table = get_stage_table(stage)
        assert table is not None
        assert isinstance(table, str)
