"""Comprehensive tests for Stage 3 (THE GATE - Identity Generation).

Target: 90%+ coverage of stage_3/claude_code_stage_3.py
"""
from __future__ import annotations

import sys
from datetime import datetime, UTC
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
def test_serialize_datetime(mock_run_id, mock_logger) -> None:
    """Test serialize_datetime function."""
    from stage_3.claude_code_stage_3 import serialize_datetime
    
    test_dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    result = serialize_datetime(test_dt)
    
    # Should serialize to ISO format string
    assert isinstance(result, str)
    assert "2024" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_serialize_datetime_none(mock_run_id, mock_logger) -> None:
    """Test serialize_datetime with None."""
    from stage_3.claude_code_stage_3 import serialize_datetime
    
    result = serialize_datetime(None)
    
    assert result is None


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_generate_entity_id(mock_run_id, mock_logger) -> None:
    """Test generate_entity_id function."""
    from stage_3.claude_code_stage_3 import generate_entity_id
    
    entity_id = generate_entity_id(
        session_id="test_session",
        message_index=0,
        fingerprint="test_fingerprint"
    )
    
    assert entity_id is not None
    assert isinstance(entity_id, str)
    assert len(entity_id) > 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_create_stage_3_table(mock_run_id, mock_logger) -> None:
    """Test create_stage_3_table function."""
    from stage_3.claude_code_stage_3 import create_stage_3_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_3_table(mock_client)
    assert result == mock_table
    mock_client.create_table.assert_called()
