"""Comprehensive tests for Stages 3 and 5.

Target: 90%+ coverage of identity and tokenization stages.
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
@patch('stage_3.claude_code_stage_3.generate_message_id_from_guid')
@patch('stage_3.claude_code_stage_3.register_id')
def test_stage_3_process_identity_generation(mock_register, mock_generate_id, mock_run_id, mock_logger) -> None:
    """Test stage_3 process_identity_generation function."""
    from stage_3.claude_code_stage_3 import process_identity_generation
    from google.cloud import bigquery
    
    # Mock ID generation
    mock_generate_id.return_value = "a" * 32
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.session_id = "session_123"
    mock_row.message_index = 0
    mock_row.fingerprint = "fingerprint_hash"
    mock_query_job.result.return_value = [mock_row]
    mock_client.query.return_value = mock_query_job
    
    result = process_identity_generation(mock_client, "test_run", batch_size=100, dry_run=True)
    
    assert isinstance(result, dict)
    assert "processed" in result or "total" in result or "count" in result or "dry_run" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_generate_token_id(mock_run_id, mock_logger) -> None:
    """Test stage_5 generate_token_id function."""
    from stage_5.claude_code_stage_5 import generate_token_id
    
    token_id = generate_token_id("parent_123", 0)
    
    assert isinstance(token_id, str)
    assert len(token_id) > 0
    # Should be deterministic
    token_id2 = generate_token_id("parent_123", 0)
    assert token_id == token_id2
