"""Edge case and error path tests for Stages 5, 6, 12.

Target: Cover error handling, edge cases, and uncovered code paths.
Focus: Exception handling, empty inputs, malformed data, boundary conditions.
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
# STAGE 5 - TOKENIZATION (Edge Cases & Error Paths)
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_process_tokenization_spacy_load_error(mock_run_id, mock_logger) -> None:
    """Test process_tokenization handles spaCy load errors."""
    from stage_5.claude_code_stage_5 import process_tokenization
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    
    # Mock the import inside the function
    with patch('builtins.__import__') as mock_import:
        mock_import.side_effect = ImportError("spacy not available")
        
        # Function should raise an exception when spaCy can't be imported
        with pytest.raises(Exception, match="Failed|spaCy|model|ImportError|not available|spacy"):
            process_tokenization(mock_client, "test_run", batch_size=100, dry_run=False)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_process_tokenization_query_error(mock_run_id, mock_logger) -> None:
    """Test process_tokenization handles BigQuery query errors."""
    from stage_5.claude_code_stage_5 import process_tokenization
    from google.cloud import bigquery
    from google.api_core import exceptions as google_exceptions
    
    try:
        import spacy
    except ImportError:
        pytest.skip("spacy not available")
    
    mock_client = Mock(spec=bigquery.Client)
    mock_client.query.side_effect = google_exceptions.ServiceUnavailable("Service unavailable")
    
    with patch('stage_5.claude_code_stage_5.spacy.load') as mock_spacy_load:
        mock_nlp = MagicMock()
        mock_spacy_load.return_value = mock_nlp
        
        with pytest.raises(Exception):
            process_tokenization(mock_client, "test_run", batch_size=100, dry_run=False)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_tokenize_message_none_text(mock_run_id, mock_logger) -> None:
    """Test tokenize_message with None text."""
    from stage_5.claude_code_stage_5 import tokenize_message
    
    message = {"text": None, "entity_id": "entity_123"}
    nlp = MagicMock()
    
    tokens = list(tokenize_message(message, nlp, "run_123", "2026-01-27T00:00:00"))
    
    assert len(tokens) == 0  # None text should yield no tokens


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_create_stage_5_table_error(mock_run_id, mock_logger) -> None:
    """Test create_stage_5_table error handling."""
    from stage_5.claude_code_stage_5 import create_stage_5_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_client.create_table.side_effect = Exception("Table creation failed")
    
    with pytest.raises(Exception):
        create_stage_5_table(mock_client)


# =============================================================================
# STAGE 6 - SENTENCE DETECTION (Edge Cases & Error Paths)
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_detect_sentences_none_text(mock_run_id, mock_logger) -> None:
    """Test detect_sentences with None text."""
    from stage_6.claude_code_stage_6 import detect_sentences
    
    message = {"text": None, "entity_id": "entity_123"}
    nlp = MagicMock()
    
    sentences = list(detect_sentences(message, nlp, "run_123", "2026-01-27T00:00:00"))
    
    assert len(sentences) == 0  # None text should yield no sentences


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_detect_sentences_empty_text(mock_run_id, mock_logger) -> None:
    """Test detect_sentences with empty text."""
    from stage_6.claude_code_stage_6 import detect_sentences
    
    message = {"text": "   ", "entity_id": "entity_123"}  # Whitespace only
    nlp = MagicMock()
    
    sentences = list(detect_sentences(message, nlp, "run_123", "2026-01-27T00:00:00"))
    
    assert len(sentences) == 0  # Whitespace-only text should yield no sentences


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_generate_sentence_id_deterministic(mock_run_id, mock_logger) -> None:
    """Test generate_sentence_id produces deterministic IDs."""
    from stage_6.claude_code_stage_6 import generate_sentence_id
    
    id1 = generate_sentence_id("parent_123", 0)
    id2 = generate_sentence_id("parent_123", 0)
    id3 = generate_sentence_id("parent_123", 1)
    
    assert id1 == id2  # Same inputs = same ID
    assert id1 != id3  # Different index = different ID
    assert len(id1) == 32  # SHA256 hex truncated to 32 chars


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_create_stage_6_table(mock_run_id, mock_logger) -> None:
    """Test create_stage_6_table function."""
    from stage_6.claude_code_stage_6 import create_stage_6_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_6_table(mock_client)
    
    assert result == mock_table
    mock_client.create_table.assert_called_once()


# =============================================================================
# STAGE 12 - TOPICS (Edge Cases & Error Paths)
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_extract_keywords_none_text(mock_run_id, mock_logger) -> None:
    """Test extract_keywords with None text."""
    from stage_12.claude_code_stage_12 import extract_keywords
    
    try:
        import keybert
    except ImportError:
        pytest.skip("keybert not available")
    
    mock_model = MagicMock()
    
    keywords = extract_keywords(mock_model, None, top_n=5)
    
    assert keywords == []  # None text should return empty


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_get_keybert_model_import_error(mock_run_id, mock_logger) -> None:
    """Test get_keybert_model handles import errors."""
    from stage_12.claude_code_stage_12 import get_keybert_model
    
    # Mock the import inside the function
    with patch('builtins.__import__') as mock_import:
        mock_import.side_effect = ImportError("keybert not installed")
        
        with pytest.raises(ImportError):
            get_keybert_model()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_process_topics_query_error(mock_run_id, mock_logger) -> None:
    """Test process_topics handles BigQuery query errors."""
    from stage_12.claude_code_stage_12 import process_topics
    from google.cloud import bigquery
    from google.api_core import exceptions as google_exceptions
    
    mock_client = Mock(spec=bigquery.Client)
    mock_client.query.side_effect = google_exceptions.ServiceUnavailable("Service unavailable")
    
    with pytest.raises(Exception):
        process_topics(mock_client, "test_run", batch_size=100, top_n=5, dry_run=False)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_process_topics_empty_keywords(mock_run_id, mock_logger) -> None:
    """Test process_topics handles messages with no keywords."""
    from stage_12.claude_code_stage_12 import process_topics
    from google.cloud import bigquery
    
    try:
        import keybert
    except ImportError:
        pytest.skip("keybert not available")
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.text = "Short"  # Too short for keyword extraction
    mock_row.session_id = "session_123"
    mock_row.content_date = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    with patch('stage_12.claude_code_stage_12.get_keybert_model') as mock_get_model:
        mock_model = MagicMock()
        mock_model.extract_keywords.return_value = []  # No keywords
        mock_get_model.return_value = mock_model
        
        result = process_topics(mock_client, "test_run", batch_size=100, top_n=5, dry_run=False)
        
        assert isinstance(result, dict)
        assert "topics_extracted" in result or "input_messages" in result
