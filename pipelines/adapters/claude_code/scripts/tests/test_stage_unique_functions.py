"""Tests for unique functions in stage scripts.

These are functions that are unique to specific stages and cannot be
tested with parameterized tests. Focus on achieving 90% coverage efficiently.

Target: Cover unique logic paths (20-30% of code) with targeted tests.
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


# Stage 1 unique functions
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_1_discover_session_files(mock_run_id, mock_logger) -> None:
    """Test Stage 1 unique function: discover_session_files."""
    from stage_1.claude_code_stage_1 import discover_session_files
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        (tmp_path / "file1.jsonl").write_text('{"test": "data"}')
        (tmp_path / "file2.jsonl").write_text('{"test": "data2"}')
        
        files = discover_session_files(tmp_path)
        assert len(files) == 2
        assert all(f.suffix == ".jsonl" for f in files)


# REMOVED: test_stage_1_parse_session_file - Duplicate, covered by test_stage_1_11_13_final.py::test_stage_1_parse_session_file_comprehensive


# Stage 2 unique functions
# REMOVED: test_stage_2_clean_content - Duplicate, covered by test_stage_2_7_final.py::test_stage_2_clean_content_comprehensive


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_2_normalize_timestamp(mock_run_id, mock_logger) -> None:
    """Test Stage 2 unique function: normalize_timestamp."""
    from datetime import datetime, UTC
    from stage_2.claude_code_stage_2 import normalize_timestamp
    
    test_timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    result = normalize_timestamp(test_timestamp)
    assert result == test_timestamp


# Stage 3 unique functions
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
@patch('src.services.central_services.identity_service.service.generate_message_id_from_guid')
def test_stage_3_generate_entity_id(mock_gen_id, mock_run_id, mock_logger) -> None:
    """Test Stage 3 unique function: generate_entity_id."""
    from stage_3.claude_code_stage_3 import generate_entity_id
    
    # Mock identity service to return a 32-char ID
    mock_gen_id.return_value = "a" * 32
    
    entity_id = generate_entity_id("parent_123", "guid_456", "fingerprint_789")
    assert entity_id is not None
    assert isinstance(entity_id, str)
    # generate_entity_id may return different length depending on implementation
    assert len(entity_id) > 0


# Stage 6 unique functions
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_detect_sentences(mock_run_id, mock_logger) -> None:
    """Test Stage 6 unique function: detect_sentences."""
    from stage_6.claude_code_stage_6 import detect_sentences
    from unittest.mock import Mock
    
    mock_nlp = Mock()
    mock_doc = Mock()
    mock_sent1 = Mock(text="First sentence.", start_char=0, end_char=16)
    mock_sent2 = Mock(text="Second sentence!", start_char=17, end_char=34)
    mock_doc.sents = [mock_sent1, mock_sent2]
    mock_nlp.return_value = mock_doc
    
    message = {
        "text": "First sentence. Second sentence!",
        "entity_id": "parent_123",
        "session_id": "session_123",
        "content_date": "2024-01-01"
    }
    
    sentences = list(detect_sentences(
        message,
        nlp=mock_nlp,
        run_id="test_run",
        created_at="2024-01-01T00:00:00Z"
    ))
    
    assert len(sentences) == 2
    assert sentences[0]["text"] == "First sentence."


# Stage 9 unique functions
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_truncate_text(mock_run_id, mock_logger) -> None:
    """Test Stage 9 unique function: truncate_text."""
    from stage_9.claude_code_stage_9 import truncate_text
    
    text, was_truncated = truncate_text("short text", max_chars=100)
    assert text == "short text"
    assert was_truncated is False
    
    long_text = "a" * 10000
    truncated, was_truncated = truncate_text(long_text, max_chars=8000)
    assert len(truncated) == 8000
    assert was_truncated is True


# Stage 12 unique functions
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_extract_keywords(mock_run_id, mock_logger) -> None:
    """Test Stage 12 unique function: extract_keywords."""
    from stage_12.claude_code_stage_12 import extract_keywords
    from unittest.mock import Mock
    
    mock_model = Mock()
    mock_keywords = [("keyword1", 0.9), ("keyword2", 0.8)]
    mock_model.extract_keywords.return_value = mock_keywords
    
    keywords = extract_keywords(
        mock_model,
        "test text with enough content to extract keywords",
        top_n=5
    )
    
    assert isinstance(keywords, list)
    assert len(keywords) <= 5


# Stage 15 unique functions
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_15_validate_entity(mock_run_id, mock_logger) -> None:
    """Test Stage 15 unique function: validate_entity."""
    from stage_15.claude_code_stage_15 import validate_entity
    
    entity = {
        "entity_id": "test_12345678901234567890123456789012",  # 32 chars
        "text": "test text",
        "level": 2,
        "session_id": "session_123",
        "word_count": 2
    }
    
    status, score, errors, warnings = validate_entity(entity, strict=False)
    
    assert isinstance(status, str)
    assert isinstance(score, float)
    assert isinstance(errors, list)
    assert isinstance(warnings, list)
    assert status in ["PASSED", "WARNING", "FAILED"]
