"""Comprehensive tests for Stage 1.

Target: 90%+ coverage of extraction stage.
"""
from __future__ import annotations

import sys
import tempfile
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
def test_stage_1_generate_session_id(mock_run_id, mock_logger) -> None:
    """Test stage_1 _generate_session_id function."""
    from stage_1.claude_code_stage_1 import _generate_session_id
    
    file_path = Path("/test/session_123.jsonl")
    session_id = _generate_session_id(file_path)
    
    assert isinstance(session_id, str)
    assert len(session_id) > 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_1_load_to_bigquery(mock_run_id, mock_logger) -> None:
    """Test stage_1 load_to_bigquery function."""
    from stage_1.claude_code_stage_1 import load_to_bigquery
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_client.insert_rows_json.return_value = []  # No errors
    
    records = [
        {
            "entity_id": "entity_123",
            "session_id": "session_123",
            "text": "Test message"
        }
    ]
    
    # load_to_bigquery doesn't take batch_size, returns int
    result = load_to_bigquery(mock_client, records, dry_run=False)
    
    assert isinstance(result, int)
    assert result == len(records)
