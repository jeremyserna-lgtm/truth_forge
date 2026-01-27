"""Comprehensive tests for Stages 0, 1, 2, 3.

Target: 90%+ coverage of early pipeline stages.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

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
def test_stage_0_discover_sessions(mock_run_id, mock_logger) -> None:
    """Test stage_0 discover_session_files function."""
    from stage_0.claude_code_stage_0 import discover_session_files
    
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = Path(tmpdir)
        # Create mock JSONL session files
        (source_dir / "session_123.jsonl").write_text('{"test": "data"}\n')
        
        sessions = discover_session_files(source_dir)
        
        assert isinstance(sessions, list)
        assert len(sessions) > 0


# REMOVED: test_stage_1_parse_session_file - Duplicate, covered by test_stage_1_11_13_final.py::test_stage_1_parse_session_file_comprehensive

# REMOVED: test_stage_2_clean_content - Duplicate, covered by test_stage_2_7_final.py::test_stage_2_clean_content_comprehensive and test_stage_1_2_expanded.py::test_stage_2_clean_content_edge_cases


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_2_normalize_timestamp(mock_run_id, mock_logger) -> None:
    """Test stage_2 normalize_timestamp function."""
    from stage_2.claude_code_stage_2 import normalize_timestamp
    from datetime import datetime
    
    # normalize_timestamp takes datetime | None, returns datetime | None
    test_datetime = datetime(2024, 1, 1, 0, 0, 0)
    normalized = normalize_timestamp(test_datetime)
    
    assert normalized is not None
    assert isinstance(normalized, datetime)
    
    # Test None case
    result = normalize_timestamp(None)
    assert result is None or isinstance(result, datetime)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
@patch('stage_3.claude_code_stage_3.generate_message_id_from_guid')
@patch('stage_3.claude_code_stage_3.register_id')
def test_stage_3_generate_entity_id(mock_register, mock_generate_id, mock_run_id, mock_logger) -> None:
    """Test stage_3 generate_entity_id function."""
    from stage_3.claude_code_stage_3 import generate_entity_id
    
    # Mock the ID generation
    mock_generate_id.return_value = "a" * 32  # 32-character ID
    
    # generate_entity_id takes (session_id, message_index, fingerprint)
    entity_id = generate_entity_id("session_123", 0, "fingerprint_hash")
    
    assert isinstance(entity_id, str)
    assert len(entity_id) > 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_3_create_stage_3_table(mock_run_id, mock_logger) -> None:
    """Test stage_3 create_stage_3_table function."""
    from stage_3.claude_code_stage_3 import create_stage_3_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_3_table(mock_client)
    
    assert result is not None
