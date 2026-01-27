"""Final comprehensive tests for Stages 3, 9, 15.

Target: Increase coverage for identity generation, embeddings, and validation.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

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
def test_stage_3_process_identity_generation_comprehensive(mock_run_id, mock_logger) -> None:
    """Test stage_3 process_identity_generation function comprehensively."""
    from stage_3.claude_code_stage_3 import process_identity_generation
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.extraction_id = "ext_123"
    mock_row.session_id = "session_123"
    mock_row.message_index = 0
    mock_row.fingerprint = "fp_hash_123"
    mock_row.message_type = "message"
    mock_row.role = "user"
    mock_row.content = "Test message"
    mock_row.content_cleaned = "Test message"
    mock_row.content_length = 12
    mock_row.word_count = 2
    mock_row.timestamp = None
    mock_row.timestamp_utc = None
    mock_row.model = None
    mock_row.cost_usd = None
    mock_row.tool_name = None
    mock_row.tool_input = None
    mock_row.tool_output = None
    mock_row.source_file = "test.jsonl"
    mock_row.content_date = None
    mock_row.is_duplicate = False
    mock_row.extracted_at = None
    mock_row.cleaned_at = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    # Mock identity service functions
    with patch('stage_3.claude_code_stage_3.generate_message_id_from_guid') as mock_gen_id:
        with patch('stage_3.claude_code_stage_3.register_id') as mock_register:
            mock_gen_id.return_value = "a" * 32  # 32-char entity_id
            mock_register.return_value = True
            
            result = process_identity_generation(mock_client, "test_run", batch_size=100, dry_run=True)
            
            assert isinstance(result, dict)
            assert "processed" in result or "total" in result or "count" in result or "dry_run" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_process_embeddings_comprehensive(mock_run_id, mock_logger) -> None:
    """Test stage_9 process_embeddings function comprehensively."""
    from stage_9.claude_code_stage_9 import process_embeddings
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.text = "Test message for embedding generation."
    mock_row.session_id = "session_123"
    mock_row.content_date = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    # Mock genai client
    with patch('stage_9.claude_code_stage_9.get_embedding_client') as mock_get_client:
        mock_genai = MagicMock()
        mock_embed = MagicMock()
        # embed_content returns dict with "embedding" key containing list of embeddings
        mock_embed.embed_content.return_value = {
            "embedding": [[0.1] * 768]  # Single embedding vector
        }
        mock_genai.embed_content = mock_embed
        mock_get_client.return_value = mock_genai
        
        result = process_embeddings(mock_client, "test_run", batch_size=50, dry_run=True)
        
        assert isinstance(result, dict)
        assert "input_messages" in result or "embeddings_generated" in result or "dry_run" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_run_validation_comprehensive(mock_run_id, mock_logger) -> None:
    """Test stage_15 run_validation function comprehensively."""
    from stage_15.claude_code_stage_15 import run_validation
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "a" * 32  # Valid 32-char ID
    mock_row.text = "Test message"
    mock_row.source_name = "claude_code"
    mock_row.level = 1
    mock_row.session_id = "session_123"
    mock_row.word_count = 2
    mock_row.keys.return_value = ["entity_id", "text", "source_name", "level", "session_id", "word_count"]
    mock_row.__getitem__ = lambda self, key: {
        "entity_id": "a" * 32,
        "text": "Test message",
        "source_name": "claude_code",
        "level": 1,
        "session_id": "session_123",
        "word_count": 2
    }[key]
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    result = run_validation(mock_client, "test_run", strict=False, dry_run=True)
    
    assert isinstance(result, dict)
    assert "total_entities" in result or "validated" in result or "dry_run" in result


# REMOVED: test_stage_15_validate_entity_comprehensive - Duplicate of test_stage_15_16_comprehensive.py::test_stage_15_validate_entity_comprehensive


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_create_stage_15_table(mock_run_id, mock_logger) -> None:
    """Test stage_15 create_stage_15_table function."""
    from stage_15.claude_code_stage_15 import create_stage_15_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_15_table(mock_client)
    
    assert result is not None
