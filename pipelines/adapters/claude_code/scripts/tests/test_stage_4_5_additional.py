"""Additional comprehensive tests for Stages 4 and 5.

Target: Increase coverage for staging and tokenization stages.
Focus on uncovered functions and edge cases.
"""
from __future__ import annotations

import sys
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


# Stage 4 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_4_create_stage_4_table(mock_run_id, mock_logger) -> None:
    """Test stage_4 create_stage_4_table function."""
    from stage_4.claude_code_stage_4 import create_stage_4_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_4_table(mock_client)
    
    assert result is not None
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_4_process_staging_with_data(mock_run_id, mock_logger) -> None:
    """Test stage_4 process_staging with actual data processing."""
    from stage_4.claude_code_stage_4 import process_staging
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.extraction_id = "ext_123"
    mock_row.entity_id = "entity_123"
    mock_row.session_id = "session_123"
    mock_row.message_index = 0
    mock_row.message_type = "message"
    mock_row.role = "user"
    mock_row.content_cleaned = "Test message"
    mock_row.content_length = 12
    mock_row.word_count = 2
    mock_row.timestamp_utc = None
    mock_row.model = None
    mock_row.cost_usd = None
    mock_row.tool_name = None
    mock_row.tool_input = None
    mock_row.tool_output = None
    mock_row.source_file = "test.jsonl"
    mock_row.content_date = None
    mock_row.fingerprint = "fp_hash"
    mock_row.is_duplicate = False
    mock_row.extracted_at = None
    mock_row.cleaned_at = None
    mock_row.identity_created_at = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    result = process_staging(mock_client, "test_run", dry_run=False)
    
    assert isinstance(result, dict)
    assert "input_rows" in result or "output_rows" in result or "dry_run" in result


# Stage 5 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_create_stage_5_table(mock_run_id, mock_logger) -> None:
    """Test stage_5 create_stage_5_table function."""
    from stage_5.claude_code_stage_5 import create_stage_5_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_5_table(mock_client)
    
    assert result is not None
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_process_tokenization_with_data(mock_run_id, mock_logger) -> None:
    """Test stage_5 process_tokenization with actual data processing."""
    from stage_5.claude_code_stage_5 import process_tokenization
    from google.cloud import bigquery
    import pytest
    
    # Skip if spacy not available
    try:
        import spacy
    except ImportError:
        pytest.skip("spacy not available - skipping test")
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.text = "Test message for tokenization"
    mock_row.session_id = "session_123"
    mock_row.content_date = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    # Mock spacy.load
    with patch('stage_5.claude_code_stage_5.spacy.load') as mock_spacy_load:
        mock_nlp = MagicMock()
        mock_doc = MagicMock()
        mock_token = MagicMock()
        mock_token.text = "Test"
        mock_token.pos_ = "NOUN"
        mock_token.lemma_ = "test"
        mock_token.is_stop = False
        mock_token.is_punct = False
        mock_token.is_space = False
        
        def mock_iter(self):
            return iter([mock_token])
        mock_doc.__iter__ = mock_iter
        mock_nlp.return_value = mock_doc
        mock_spacy_load.return_value = mock_nlp
        
        result = process_tokenization(mock_client, "test_run", batch_size=10, dry_run=False)
        
        assert isinstance(result, dict)
        assert "processed" in result or "total" in result or "count" in result or "dry_run" in result
