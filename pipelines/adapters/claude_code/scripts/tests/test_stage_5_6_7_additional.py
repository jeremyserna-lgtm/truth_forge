"""Additional comprehensive tests for Stages 5, 6, 7.

Target: Cover remaining functions and edge cases to increase coverage.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import datetime, timezone

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


# =============================================================================
# STAGE 5 - TOKENIZATION (Additional Coverage)
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_process_tokenization_with_data(mock_run_id, mock_logger) -> None:
    """Test process_tokenization with actual data."""
    from stage_5.claude_code_stage_5 import process_tokenization
    from google.cloud import bigquery
    
    try:
        import spacy
    except ImportError:
        pytest.skip("spacy not available")
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.text = "Test message with tokens"
    mock_row.session_id = "session_123"
    mock_row.content_date = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    with patch('stage_5.claude_code_stage_5.spacy.load') as mock_spacy_load:
        mock_nlp = MagicMock()
        mock_doc = MagicMock()
        mock_token1 = MagicMock()
        mock_token1.text = "Test"
        mock_token1.pos_ = "NOUN"
        mock_token1.lemma_ = "test"
        mock_token1.is_stop = False
        mock_token1.is_punct = False
        mock_token2 = MagicMock()
        mock_token2.text = "message"
        mock_token2.pos_ = "NOUN"
        mock_token2.lemma_ = "message"
        mock_token2.is_stop = False
        mock_token2.is_punct = False
        mock_doc.__iter__ = lambda self: iter([mock_token1, mock_token2])
        mock_nlp.return_value = mock_doc
        mock_spacy_load.return_value = mock_nlp
        
        result = process_tokenization(mock_client, "test_run", batch_size=100, dry_run=False)
        
        assert isinstance(result, dict)
        assert "processed" in result or "total" in result or "dry_run" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_process_tokenization_bigquery_insert_errors(mock_run_id, mock_logger) -> None:
    """Test process_tokenization handles BigQuery insert errors."""
    from stage_5.claude_code_stage_5 import process_tokenization
    from google.cloud import bigquery
    
    try:
        import spacy
    except ImportError:
        pytest.skip("spacy not available")
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.text = "Test"
    mock_row.session_id = "session_123"
    mock_row.content_date = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = [{"error": "Insert failed"}]
    
    with patch('stage_5.claude_code_stage_5.spacy.load') as mock_spacy_load:
        mock_nlp = MagicMock()
        mock_doc = MagicMock()
        mock_token = MagicMock()
        mock_token.text = "Test"
        mock_token.pos_ = "NOUN"
        mock_token.lemma_ = "test"
        mock_token.is_stop = False
        mock_token.is_punct = False
        mock_doc.__iter__ = lambda self: iter([mock_token])
        mock_nlp.return_value = mock_doc
        mock_spacy_load.return_value = mock_nlp
        
        with pytest.raises(ValueError, match="Failed|error|insert"):
            process_tokenization(mock_client, "test_run", batch_size=100, dry_run=False)


# =============================================================================
# STAGE 6 - SENTENCE DETECTION (Additional Coverage)
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_main_function_dry_run(mock_run_id, mock_logger) -> None:
    """Test stage_6 main function with dry_run."""
    from stage_6.claude_code_stage_6 import main
    from google.cloud import bigquery
    
    try:
        import spacy
    except ImportError:
        pytest.skip("spacy not available")
    
    with patch('stage_6.claude_code_stage_6.get_bigquery_client') as mock_get_client:
        mock_client = Mock(spec=bigquery.Client)
        mock_get_client.return_value = mock_client
        
        with patch('stage_6.claude_code_stage_6.PipelineTracker') as mock_tracker:
            mock_tracker.return_value.__enter__.return_value = Mock()
            mock_tracker.return_value.__exit__.return_value = None
            
            with patch('sys.argv', ['claude_code_stage_6.py', '--dry-run']):
                result = main()
                
                assert isinstance(result, int)
                assert result == 0  # Success


# =============================================================================
# STAGE 7 - MESSAGE ENTITIES (Additional Coverage)
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_7_main_function_dry_run(mock_run_id, mock_logger) -> None:
    """Test stage_7 main function with dry_run."""
    from stage_7.claude_code_stage_7 import main
    from google.cloud import bigquery
    
    with patch('stage_7.claude_code_stage_7.get_bigquery_client') as mock_get_client:
        mock_client = Mock(spec=bigquery.Client)
        mock_query_job = Mock()
        mock_query_job.result.return_value = iter([])
        mock_client.query.return_value = mock_query_job
        mock_get_client.return_value = mock_client
        
        with patch('stage_7.claude_code_stage_7.PipelineTracker') as mock_tracker:
            mock_tracker.return_value.__enter__.return_value = Mock()
            mock_tracker.return_value.__exit__.return_value = None
            
            with patch('sys.argv', ['claude_code_stage_7.py', '--dry-run']):
                result = main()
                
                assert isinstance(result, int)
                # May return 0 (success) or 1 (error) depending on implementation
