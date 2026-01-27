"""DEPRECATED: Comprehensive tests for Stages 13, 14, 15, 16.

⚠️  THIS FILE IS DEPRECATED AND WILL BE REMOVED
    Superseded by:
    - test_stage_13_comprehensive.py
    - test_stage_7_14_comprehensive.py
    - test_stage_15_16_comprehensive.py
    
Target: 90%+ coverage of stage processing functions.
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


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_create_table(mock_run_id, mock_logger) -> None:
    """Test stage_13 create_stage_13_table."""
    from stage_13.claude_code_stage_13 import create_stage_13_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_13_table(mock_client)
    assert result == mock_table


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_generate_relationship_id(mock_run_id, mock_logger) -> None:
    """Test stage_13 generate_relationship_id."""
    from stage_13.claude_code_stage_13 import generate_relationship_id
    
    rel_id = generate_relationship_id("source_123", "target_456", "parent_child")
    
    assert rel_id is not None
    assert isinstance(rel_id, str)
    assert len(rel_id) > 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_14_create_table(mock_run_id, mock_logger) -> None:
    """Test stage_14 create_stage_14_table."""
    from stage_14.claude_code_stage_14 import create_stage_14_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_14_table(mock_client)
    assert result == mock_table


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_create_table(mock_run_id, mock_logger) -> None:
    """Test stage_15 create_stage_15_table."""
    from stage_15.claude_code_stage_15 import create_stage_15_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_15_table(mock_client)
    assert result == mock_table


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_validate_entity(mock_run_id, mock_logger) -> None:
    """Test stage_15 validate_entity."""
    from stage_15.claude_code_stage_15 import validate_entity
    
    entity = {
        "entity_id": "test_12345678901234567890123456789012",  # 32 chars
        "text": "test text",
        "level": 2,
        "session_id": "session_123",
        "word_count": 2
    }
    
    status, score, errors, warnings = validate_entity(entity, strict=False)
    
    assert isinstance(status, str)
    assert isinstance(score, float)
    assert isinstance(errors, list)
    assert isinstance(warnings, list)
    assert status in ["PASSED", "WARNING", "FAILED"]


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_ensure_table(mock_run_id, mock_logger) -> None:
    """Test stage_16 ensure_entity_unified_table."""
    from stage_16.claude_code_stage_16 import ensure_entity_unified_table
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    # First call raises NotFound (table doesn't exist), second call returns table
    mock_client.get_table.side_effect = [NotFound("Table not found"), mock_table]
    mock_client.create_table.return_value = mock_table
    
    result = ensure_entity_unified_table(mock_client)
    assert result == mock_table


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_16_get_existing_entity_ids(mock_run_id, mock_logger) -> None:
    """Test stage_16 get_existing_entity_ids."""
    from stage_16.claude_code_stage_16 import get_existing_entity_ids
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = [Mock(entity_id="id1"), Mock(entity_id="id2")]
    mock_client.query.return_value = mock_query_job
    
    result = get_existing_entity_ids(mock_client)
    
    assert isinstance(result, set)
    assert "id1" in result
    assert "id2" in result
