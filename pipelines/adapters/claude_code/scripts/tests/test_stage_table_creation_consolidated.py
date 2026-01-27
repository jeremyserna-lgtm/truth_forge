"""Consolidated tests for stage table creation functions.

Uses parameterization to test create_stage_X_table functions across all stages.
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


# Stages with create_stage_X_table functions
STAGE_TABLE_CREATION = [
    (4, "stage_4.claude_code_stage_4", "create_stage_4_table"),
    (5, "stage_5.claude_code_stage_5", "create_stage_5_table"),
    (6, "stage_6.claude_code_stage_6", "create_stage_6_table"),
    (7, "stage_7.claude_code_stage_7", "create_stage_7_table"),
    (8, "stage_8.claude_code_stage_8", "create_stage_8_table"),
    (9, "stage_9.claude_code_stage_9", "create_stage_9_table"),
    (10, "stage_10.claude_code_stage_10", "create_stage_10_table"),
    (11, "stage_11.claude_code_stage_11", "create_stage_11_table"),
    (12, "stage_12.claude_code_stage_12", "create_stage_12_table"),
    (13, "stage_13.claude_code_stage_13", "create_stage_13_table"),
    (14, "stage_14.claude_code_stage_14", "create_stage_14_table"),
    (15, "stage_15.claude_code_stage_15", "create_stage_15_table"),
]


@pytest.mark.parametrize("stage_num,module_name,func_name", STAGE_TABLE_CREATION)
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_table_creation_consolidated(
    mock_run_id,
    mock_logger,
    stage_num: int,
    module_name: str,
    func_name: str
) -> None:
    """Test create_stage_X_table functions (consolidated parameterized test)."""
    from google.cloud import bigquery
    
    try:
        module = __import__(module_name, fromlist=[func_name])
        create_table_func = getattr(module, func_name, None)
        
        if create_table_func is None:
            pytest.skip(f"Stage {stage_num} does not have {func_name}")
        
        # Mock BigQuery client
        mock_client = Mock(spec=bigquery.Client)
        mock_table = Mock(spec=bigquery.Table)
        mock_client.create_table.return_value = mock_table
        
        # Call the function
        result = create_table_func(mock_client)
        
        # Verify table creation was called
        assert mock_client.create_table.called
        assert result is not None
    except ImportError:
        pytest.skip(f"Could not import {module_name}")
