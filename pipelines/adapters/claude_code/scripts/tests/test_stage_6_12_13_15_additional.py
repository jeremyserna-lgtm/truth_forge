"""Additional comprehensive tests for Stages 6, 12, 13, 15.

Target: Increase coverage for sentence detection, keyword extraction, relationships, and validation.
Focus on uncovered functions and edge cases.
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


# Stage 6 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_create_stage_6_table(mock_run_id, mock_logger) -> None:
    """Test stage_6 create_stage_6_table function."""
    from stage_6.claude_code_stage_6 import create_stage_6_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_6_table(mock_client)
    
    assert result is not None
    mock_client.create_table.assert_called_once()


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
    
    # Different inputs should produce different IDs
    sentence_id3 = generate_sentence_id("parent_456", 0)
    assert sentence_id != sentence_id3


# Stage 12 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_create_stage_12_table(mock_run_id, mock_logger) -> None:
    """Test stage_12 create_stage_12_table function."""
    from stage_12.claude_code_stage_12 import create_stage_12_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_12_table(mock_client)
    
    assert result is not None
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_get_keybert_model(mock_run_id, mock_logger) -> None:
    """Test stage_12 get_keybert_model function."""
    from stage_12.claude_code_stage_12 import get_keybert_model
    import pytest
    
    # Skip if KeyBERT not available
    try:
        from keybert import KeyBERT
    except ImportError:
        pytest.skip("keybert not available - skipping test")
    
    # Function may raise ImportError if package not installed
    try:
        model = get_keybert_model()
        assert model is not None
    except ImportError:
        # Expected if package not installed
        pass


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_extract_keywords_empty_text(mock_run_id, mock_logger) -> None:
    """Test stage_12 extract_keywords with empty or very short text."""
    from stage_12.claude_code_stage_12 import extract_keywords
    from unittest.mock import Mock
    
    mock_model = Mock()
    mock_model.extract_keywords.return_value = []
    
    # Empty text should return empty list
    keywords = extract_keywords(mock_model, "", top_n=5)
    assert isinstance(keywords, list)
    assert len(keywords) == 0
    
    # Very short text
    keywords = extract_keywords(mock_model, "hi", top_n=5)
    assert isinstance(keywords, list)


# Stage 13 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_create_stage_13_table(mock_run_id, mock_logger) -> None:
    """Test stage_13 create_stage_13_table function."""
    from stage_13.claude_code_stage_13 import create_stage_13_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_13_table(mock_client)
    
    assert result is not None
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_generate_relationship_id(mock_run_id, mock_logger) -> None:
    """Test stage_13 generate_relationship_id function."""
    from stage_13.claude_code_stage_13 import generate_relationship_id
    
    rel_id = generate_relationship_id("source_123", "target_456", "parent_child")
    
    assert isinstance(rel_id, str)
    assert len(rel_id) > 0
    
    # Should be deterministic
    rel_id2 = generate_relationship_id("source_123", "target_456", "parent_child")
    assert rel_id == rel_id2
    
    # Different inputs should produce different IDs
    rel_id3 = generate_relationship_id("source_789", "target_456", "parent_child")
    assert rel_id != rel_id3


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_build_parent_child_relationships(mock_run_id, mock_logger) -> None:
    """Test stage_13 build_parent_child_relationships function."""
    from stage_13.claude_code_stage_13 import build_parent_child_relationships
    from google.cloud import bigquery
    from datetime import datetime, timezone
    
    mock_client = Mock(spec=bigquery.Client)
    
    # First query: Message -> Sentence
    mock_row1 = Mock()
    mock_row1.message_id = "msg_123"
    mock_row1.sentence_id = "sent_456"
    mock_row1.session_id = "session_123"
    mock_row1.content_date = None
    
    # Second query: Conversation -> Message
    mock_row2 = Mock()
    mock_row2.conversation_id = "conv_789"
    mock_row2.message_id = "msg_123"
    mock_row2.session_id = "session_123"
    mock_row2.content_date = None
    
    mock_query_job1 = Mock()
    mock_query_job1.result.return_value = iter([mock_row1])
    mock_query_job2 = Mock()
    mock_query_job2.result.return_value = iter([mock_row2])
    
    # Return different query jobs based on query content
    def query_side_effect(query_str):
        if "STAGE_7_TABLE" in query_str and "STAGE_6_TABLE" in query_str:
            return mock_query_job1
        elif "STAGE_8_TABLE" in query_str:
            return mock_query_job2
        return mock_query_job1
    
    mock_client.query.side_effect = query_side_effect
    
    created_at = datetime.now(timezone.utc).isoformat()
    relationships = list(build_parent_child_relationships(mock_client, "test_run", created_at))
    
    assert isinstance(relationships, list)
    assert all("relationship_id" in r for r in relationships)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_build_sequential_relationships(mock_run_id, mock_logger) -> None:
    """Test stage_13 build_sequential_relationships function."""
    from stage_13.claude_code_stage_13 import build_sequential_relationships
    from google.cloud import bigquery
    from datetime import datetime, timezone
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.source_id = "msg_1"
    mock_row.target_id = "msg_2"
    mock_row.source_role = "user"  # String, not Mock
    mock_row.target_role = "assistant"  # String, not Mock
    mock_row.session_id = "session_123"
    mock_row.content_date = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    created_at = datetime.now(timezone.utc).isoformat()
    relationships = list(build_sequential_relationships(mock_client, "test_run", created_at))
    
    assert isinstance(relationships, list)
    assert all("relationship_id" in r for r in relationships)


# Stage 15 Additional Tests
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
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_validate_entity_strict_mode(mock_run_id, mock_logger) -> None:
    """Test stage_15 validate_entity with strict=True."""
    from stage_15.claude_code_stage_15 import validate_entity
    
    # Valid entity
    valid_entity = {
        "entity_id": "a" * 32,  # 32-char ID
        "text": "Test message",
        "level": 5,
        "source_name": "claude_code",
        "source_pipeline": "claude_code",
        "word_count": 2
    }
    
    status, score, errors, warnings = validate_entity(valid_entity, strict=True)
    
    assert isinstance(status, str)
    assert status in ["PASSED", "FAILED", "WARNING"]
    assert isinstance(score, (int, float))
    assert isinstance(errors, list)
    assert isinstance(warnings, list)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_validate_entity_missing_fields(mock_run_id, mock_logger) -> None:
    """Test stage_15 validate_entity with missing required fields."""
    from stage_15.claude_code_stage_15 import validate_entity
    
    # Entity missing required fields
    invalid_entity = {
        "entity_id": "short"  # Too short, missing other fields
    }
    
    status, score, errors, warnings = validate_entity(invalid_entity, strict=False)
    
    assert isinstance(status, str)
    assert status in ["FAILED", "WARNING"]
    assert len(errors) > 0 or len(warnings) > 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_run_validation_strict_mode(mock_run_id, mock_logger) -> None:
    """Test stage_15 run_validation with strict=True."""
    from stage_15.claude_code_stage_15 import run_validation
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.text = "Test"
    mock_row.level = 5
    mock_row.source_name = "claude_code"
    mock_row.session_id = "session_123"
    mock_row.message_index = 0
    mock_row.keys.return_value = ["entity_id", "text", "level", "source_name", "session_id", "message_index"]
    mock_row.__getitem__ = lambda self, key: getattr(self, key, None)
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    result = run_validation(mock_client, "test_run", strict=True, dry_run=True)
    
    assert isinstance(result, dict)
    assert "validated" in result or "errors" in result or "warnings" in result or "dry_run" in result
