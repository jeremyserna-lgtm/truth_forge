"""Additional coverage tests for Stages 5 and 6.

Target: Increase coverage for tokenization and sentence detection stages.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import pytest

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


# Stage 5 Additional Tests
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
    
    # Different indices should produce different IDs
    token_id3 = generate_token_id("parent_123", 1)
    assert token_id != token_id3


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_tokenize_message_with_nlp(mock_run_id, mock_logger) -> None:
    """Test stage_5 tokenize_message with mocked spaCy model."""
    from stage_5.claude_code_stage_5 import tokenize_message
    import pytest
    
    # Skip if spacy not available
    try:
        import spacy
    except ImportError:
        pytest.skip("spacy not available - skipping test")
    
    # Mock spaCy model
    mock_nlp = MagicMock()
    mock_doc = MagicMock()
    
    # Mock tokens
    mock_token1 = MagicMock()
    mock_token1.text = "Hello"
    mock_token1.pos_ = "INTJ"
    mock_token1.is_punct = False
    mock_token1.is_space = False
    
    mock_token2 = MagicMock()
    mock_token2.text = "world"
    mock_token2.pos_ = "NOUN"
    mock_token2.is_punct = False
    mock_token2.is_space = False
    
    mock_doc.__iter__ = lambda self: iter([mock_token1, mock_token2])
    mock_nlp.return_value = mock_doc
    
    # Test tokenization
    created_at = datetime.now(timezone.utc).isoformat()
    tokens = list(tokenize_message(mock_nlp, "parent_123", "Hello world", "test_run", created_at))
    
    assert isinstance(tokens, list)
    assert len(tokens) > 0
    # Each token should have entity_id and parent_id
    for token in tokens:
        assert "entity_id" in token
        assert "parent_id" in token


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_process_tokenization_dry_run(mock_run_id, mock_logger) -> None:
    """Test stage_5 process_tokenization with dry_run=True."""
    import pytest
    
    # Skip if spacy not available (function imports it internally)
    try:
        import spacy
    except ImportError:
        pytest.skip("spacy not available - skipping test")
    
    from stage_5.claude_code_stage_5 import process_tokenization
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_count_row = Mock()
    mock_count_row.cnt = 10
    mock_query_job.result.return_value = iter([mock_count_row])
    mock_client.query.return_value = mock_query_job
    
    # dry_run=True skips actual tokenization but still imports spacy
    result = process_tokenization(mock_client, "test_run", batch_size=100, dry_run=True)
    
    assert isinstance(result, dict)
    assert "dry_run" in result
    assert result["dry_run"] is True
    assert "messages_processed" in result


# Stage 6 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_generate_sentence_id(mock_run_id, mock_logger) -> None:
    """Test stage_6 generate_sentence_id function."""
    from stage_6.claude_code_stage_6 import generate_sentence_id
    
    sentence_id = generate_sentence_id("parent_123", 0)
    
    assert isinstance(sentence_id, str)
    assert len(sentence_id) > 0
    
    # Should be deterministic
    sentence_id2 = generate_sentence_id("parent_123", 0)
    assert sentence_id == sentence_id2
    
    # Different indices should produce different IDs
    sentence_id3 = generate_sentence_id("parent_123", 1)
    assert sentence_id != sentence_id3


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_detect_sentences_with_nlp(mock_run_id, mock_logger) -> None:
    """Test stage_6 detect_sentences with mocked spaCy model."""
    from stage_6.claude_code_stage_6 import detect_sentences
    import pytest
    
    # Skip if spacy not available
    try:
        import spacy
    except ImportError:
        pytest.skip("spacy not available - skipping test")
    
    # Mock spaCy model
    mock_nlp = MagicMock()
    mock_doc = MagicMock()
    
    # Mock sentences
    mock_sent1 = MagicMock()
    mock_sent1.text = "First sentence."
    mock_sent1.start_char = 0
    mock_sent1.end_char = 16
    
    mock_sent2 = MagicMock()
    mock_sent2.text = "Second sentence."
    mock_sent2.start_char = 17
    mock_sent2.end_char = 34
    
    mock_doc.sents = [mock_sent1, mock_sent2]
    mock_nlp.return_value = mock_doc
    
    # Test sentence detection
    message = {"text": "First sentence. Second sentence."}
    created_at = datetime.now(timezone.utc).isoformat()
    sentences = list(detect_sentences(message, mock_nlp, "test_run", created_at))
    
    assert isinstance(sentences, list)
    assert len(sentences) > 0
    # Each sentence should have entity_id and parent_id
    for sentence in sentences:
        assert "entity_id" in sentence
        assert "parent_id" in sentence


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_main_function_exists(mock_run_id, mock_logger) -> None:
    """Test stage_6 main function exists and is callable."""
    from stage_6.claude_code_stage_6 import main
    
    assert callable(main)
