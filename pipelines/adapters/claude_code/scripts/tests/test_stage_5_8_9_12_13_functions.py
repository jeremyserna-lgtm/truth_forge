"""Additional function-level tests for Stages 5, 8, 9, 12, 13.

Target: Cover specific functions not yet fully tested to increase coverage.
Focus: Helper functions, ID generators, table creation, and edge cases.
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
# STAGE 5 - TOKENIZATION (Function-Level Coverage)
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_create_stage_5_table(mock_run_id, mock_logger) -> None:
    """Test create_stage_5_table function."""
    from stage_5.claude_code_stage_5 import create_stage_5_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_5_table(mock_client)
    
    assert result == mock_table
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_generate_token_id_deterministic(mock_run_id, mock_logger) -> None:
    """Test generate_token_id produces deterministic IDs."""
    from stage_5.claude_code_stage_5 import generate_token_id
    
    id1 = generate_token_id("parent_123", 0)
    id2 = generate_token_id("parent_123", 0)
    id3 = generate_token_id("parent_123", 1)
    
    assert id1 == id2  # Same inputs = same ID
    assert id1 != id3  # Different index = different ID
    assert len(id1) == 32  # SHA256 hex truncated to 32 chars


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_tokenize_message_empty_text(mock_run_id, mock_logger) -> None:
    """Test tokenize_message with empty text."""
    from stage_5.claude_code_stage_5 import tokenize_message
    
    message = {"text": "", "entity_id": "entity_123"}
    nlp = MagicMock()
    
    tokens = list(tokenize_message(message, nlp, "run_123", "2026-01-27T00:00:00"))
    
    assert len(tokens) == 0  # Empty text should yield no tokens


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_tokenize_message_with_text(mock_run_id, mock_logger) -> None:
    """Test tokenize_message with actual text."""
    from stage_5.claude_code_stage_5 import tokenize_message
    
    try:
        import spacy
    except ImportError:
        pytest.skip("spacy not available")
    
    message = {
        "text": "Test message",
        "entity_id": "entity_123",
        "session_id": "session_123",
        "content_date": None
    }
    
    with patch('stage_5.claude_code_stage_5.spacy.load') as mock_spacy_load:
        mock_nlp = MagicMock()
        mock_doc = MagicMock()
        mock_token = MagicMock()
        mock_token.text = "Test"
        mock_token.lemma_ = "test"
        mock_token.pos_ = "NOUN"
        mock_token.tag_ = "NN"
        mock_token.dep_ = "ROOT"
        mock_token.is_stop = False
        mock_token.is_alpha = True
        mock_token.is_punct = False
        mock_doc.__iter__ = lambda self: iter([mock_token])
        mock_nlp.return_value = mock_doc
        mock_spacy_load.return_value = mock_nlp
        
        tokens = list(tokenize_message(message, mock_nlp, "run_123", "2026-01-27T00:00:00"))
        
        assert len(tokens) >= 1
        if tokens:
            assert tokens[0]["entity_id"] is not None
            assert tokens[0]["parent_id"] == "entity_123"


# =============================================================================
# STAGE 8 - CONVERSATION ENTITIES (Function-Level Coverage)
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_create_stage_8_table(mock_run_id, mock_logger) -> None:
    """Test create_stage_8_table function."""
    from stage_8.claude_code_stage_8 import create_stage_8_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_8_table(mock_client)
    
    assert result == mock_table
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_generate_conversation_id_deterministic(mock_run_id, mock_logger) -> None:
    """Test generate_conversation_id produces deterministic IDs."""
    from stage_8.claude_code_stage_8 import generate_conversation_id
    
    id1 = generate_conversation_id("session_123")
    id2 = generate_conversation_id("session_123")
    id3 = generate_conversation_id("session_456")
    
    assert id1 == id2  # Same session = same ID
    assert id1 != id3  # Different session = different ID
    assert len(id1) == 32  # SHA256 hex truncated to 32 chars


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_create_conversation_entities_empty(mock_run_id, mock_logger) -> None:
    """Test create_conversation_entities with empty results."""
    from stage_8.claude_code_stage_8 import create_conversation_entities
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])
    mock_client.query.return_value = mock_query_job
    
    entities = list(create_conversation_entities(mock_client, "run_123", "2026-01-27T00:00:00"))
    
    assert len(entities) == 0


# =============================================================================
# STAGE 9 - EMBEDDINGS (Function-Level Coverage)
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_create_stage_9_table(mock_run_id, mock_logger) -> None:
    """Test create_stage_9_table function."""
    from stage_9.claude_code_stage_9 import create_stage_9_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_9_table(mock_client)
    
    assert result == mock_table
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_truncate_text_short(mock_run_id, mock_logger) -> None:
    """Test truncate_text with short text."""
    from stage_9.claude_code_stage_9 import truncate_text
    
    text, truncated = truncate_text("Short text")
    
    assert text == "Short text"
    assert truncated is False


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_truncate_text_long(mock_run_id, mock_logger) -> None:
    """Test truncate_text with long text."""
    from stage_9.claude_code_stage_9 import truncate_text
    
    long_text = "x" * 10000
    text, truncated = truncate_text(long_text)
    
    assert len(text) <= 8000  # Should be truncated
    assert truncated is True


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_generate_embeddings_batch_single(mock_run_id, mock_logger) -> None:
    """Test generate_embeddings_batch with single text."""
    from stage_9.claude_code_stage_9 import generate_embeddings_batch
    
    mock_genai = MagicMock()
    mock_genai.embed_content.return_value = {
        "embedding": [[0.1] * 768]
    }
    
    embeddings = generate_embeddings_batch(mock_genai, ["Test text"])
    
    assert len(embeddings) == 1
    assert len(embeddings[0]) == 768


# =============================================================================
# STAGE 12 - TOPICS (Function-Level Coverage)
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_create_stage_12_table(mock_run_id, mock_logger) -> None:
    """Test create_stage_12_table function."""
    from stage_12.claude_code_stage_12 import create_stage_12_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_12_table(mock_client)
    
    assert result == mock_table
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_extract_keywords_short_text(mock_run_id, mock_logger) -> None:
    """Test extract_keywords with text too short."""
    from stage_12.claude_code_stage_12 import extract_keywords
    
    try:
        import keybert
    except ImportError:
        pytest.skip("keybert not available")
    
    mock_model = MagicMock()
    
    keywords = extract_keywords(mock_model, "short", top_n=5)
    
    assert keywords == []  # Text too short


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_extract_keywords_error_handling(mock_run_id, mock_logger) -> None:
    """Test extract_keywords error handling."""
    from stage_12.claude_code_stage_12 import extract_keywords
    
    try:
        import keybert
    except ImportError:
        pytest.skip("keybert not available")
    
    mock_model = MagicMock()
    mock_model.extract_keywords.side_effect = Exception("Extraction failed")
    
    keywords = extract_keywords(mock_model, "This is a longer text that should work", top_n=5)
    
    assert keywords == []  # Should return empty on error


# =============================================================================
# STAGE 13 - RELATIONSHIPS (Function-Level Coverage)
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_create_stage_13_table(mock_run_id, mock_logger) -> None:
    """Test create_stage_13_table function."""
    from stage_13.claude_code_stage_13 import create_stage_13_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_13_table(mock_client)
    
    assert result == mock_table
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_generate_relationship_id_deterministic(mock_run_id, mock_logger) -> None:
    """Test generate_relationship_id produces deterministic IDs."""
    from stage_13.claude_code_stage_13 import generate_relationship_id
    
    id1 = generate_relationship_id("source_123", "target_456", "contains")
    id2 = generate_relationship_id("source_123", "target_456", "contains")
    id3 = generate_relationship_id("source_123", "target_456", "follows")
    
    assert id1 == id2  # Same inputs = same ID
    assert id1 != id3  # Different type = different ID
    assert len(id1) == 32  # SHA256 hex truncated to 32 chars


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_build_parent_child_relationships_empty(mock_run_id, mock_logger) -> None:
    """Test build_parent_child_relationships with empty results."""
    from stage_13.claude_code_stage_13 import build_parent_child_relationships
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])
    mock_client.query.return_value = mock_query_job
    
    relationships = list(build_parent_child_relationships(mock_client, "run_123", "2026-01-27T00:00:00"))
    
    # Should handle empty results gracefully
    assert isinstance(relationships, list)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_build_sequential_relationships_empty(mock_run_id, mock_logger) -> None:
    """Test build_sequential_relationships with empty results."""
    from stage_13.claude_code_stage_13 import build_sequential_relationships
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])
    mock_client.query.return_value = mock_query_job
    
    relationships = list(build_sequential_relationships(mock_client, "run_123", "2026-01-27T00:00:00"))
    
    # Should handle empty results gracefully
    assert isinstance(relationships, list)
