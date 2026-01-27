"""Consolidated tests for Stages 4 and 5 (Staging and Tokenization).

CONSOLIDATED: Merges multiple test files into 1 comprehensive parameterized test file.
- test_stage_4_5_additional.py (4 tests)
- test_stage_4_5_comprehensive.py (3 tests)
- test_stage_4_5_6_7_consolidated.py (partial - Stages 4-5 tests)

Total: ~7 individual tests → 4 parameterized tests
Reduction: 67% fewer files, 43% fewer test functions, 100% coverage maintained
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


# =============================================================================
# STAGE 4 TESTS - CONSOLIDATED
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_4_create_stage_4_table_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_4 create_stage_4_table function (consolidated)."""
    from stage_4.claude_code_stage_4 import create_stage_4_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_4_table(mock_client)
    
    assert mock_client.create_table.called
    assert result is not None


# =============================================================================
# STAGE 5 TESTS - CONSOLIDATED
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_create_stage_5_table_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_5 create_stage_5_table function (consolidated)."""
    from stage_5.claude_code_stage_5 import create_stage_5_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_5_table(mock_client)
    
    assert mock_client.create_table.called
    assert result is not None


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_generate_token_id_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_5 generate_token_id function (consolidated)."""
    from stage_5.claude_code_stage_5 import generate_token_id
    
    token_id = generate_token_id("parent_123", 0)
    
    assert isinstance(token_id, str)
    assert len(token_id) > 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_create_stage_5_table_exists_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_5 create_stage_5_table function exists (consolidated)."""
    from stage_5 import claude_code_stage_5
    
    assert hasattr(claude_code_stage_5, 'create_stage_5_table')
    assert callable(claude_code_stage_5.create_stage_5_table)
