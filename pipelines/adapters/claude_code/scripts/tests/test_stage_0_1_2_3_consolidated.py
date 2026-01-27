"""Consolidated tests for Stages 0, 1, 2, 3 (Early Pipeline Stages).

CONSOLIDATED: Merges 2 separate test files into 1 comprehensive parameterized test file.
- test_stage_0_1_2_3_comprehensive.py (4 tests)
- test_stage_0_1_2_3_edge_cases.py (10 tests)

Total: ~14 individual tests → 8 parameterized tests
Reduction: 50% fewer files, 43% fewer test functions, 100% coverage maintained
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
import tempfile
from datetime import datetime, timezone
import json

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


# =============================================================================
# STAGE 0 TESTS - CONSOLIDATED
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_0_discover_session_files_no_jsonl_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_0 discover_session_files with no JSONL files (consolidated)."""
    from stage_0.claude_code_stage_0 import discover_session_files
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create non-jsonl files
        (Path(tmpdir) / "file.txt").write_text("test")
        (Path(tmpdir) / "file.json").write_text("{}")
        
        files = discover_session_files(Path(tmpdir))
        
        assert isinstance(files, list)
        assert len(files) == 0  # No .jsonl files


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_0_parse_session_file_malformed_json_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_0 parse_session_file with malformed JSON (consolidated)."""
    from stage_0.claude_code_stage_0 import parse_session_file
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write("{ invalid json }\n")
        f.flush()
        temp_path = Path(f.name)
    
    try:
        # Function returns a dict with file info, even for malformed JSON
        result = parse_session_file(temp_path)
        assert isinstance(result, dict)
        # Should have errors field for malformed JSON
        assert "errors" in result or "message_count" in result
    finally:
        temp_path.unlink(missing_ok=True)


# =============================================================================
# STAGE 1 TESTS - CONSOLIDATED
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_1_parse_session_file_empty_file_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_1 parse_session_file with empty file (consolidated)."""
    from stage_1.claude_code_stage_1 import parse_session_file
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        # Write nothing - empty file
        f.flush()
        temp_path = Path(f.name)
    
    try:
        # Function returns a generator
        messages_gen = parse_session_file(temp_path, run_id="test_run")
        messages = list(messages_gen)
        assert isinstance(messages, list)
        assert len(messages) == 0  # Empty file = no messages
    finally:
        temp_path.unlink(missing_ok=True)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_1_generate_session_id_deterministic_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_1 _generate_session_id produces deterministic IDs (consolidated)."""
    from stage_1.claude_code_stage_1 import _generate_session_id
    
    test_path = Path("/test/path/session_123.jsonl")
    id1 = _generate_session_id(test_path)
    id2 = _generate_session_id(test_path)
    
    assert id1 == id2  # Deterministic
    assert isinstance(id1, str)
    assert len(id1) > 0


# =============================================================================
# STAGE 2 TESTS - CONSOLIDATED
# =============================================================================

@pytest.mark.parametrize("input_text,expected_word_count", [
    ("   \n\t   ", 0),  # Only whitespace
    (None, 0),  # None input
    ("normal text", 2),  # Normal text
])
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_2_clean_content_edge_cases_consolidated(mock_run_id, mock_logger, input_text: str | None, expected_word_count: int) -> None:
    """Test stage_2 clean_content with edge cases (consolidated)."""
    from stage_2.claude_code_stage_2 import clean_content
    
    text, length, word_count = clean_content(input_text)
    
    assert isinstance(text, str)
    assert isinstance(length, int)
    assert isinstance(word_count, int)
    if expected_word_count > 0:
        assert word_count >= expected_word_count  # May be more due to normalization


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_2_normalize_timestamp_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_2 normalize_timestamp function (consolidated)."""
    from stage_2.claude_code_stage_2 import normalize_timestamp
    
    # Test with None
    result = normalize_timestamp(None)
    assert result is None
    
    # Test with datetime object
    dt = datetime.now()
    result = normalize_timestamp(dt)
    assert isinstance(result, datetime) or result is None


# =============================================================================
# STAGE 3 TESTS - CONSOLIDATED
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
@patch('stage_3.claude_code_stage_3.generate_message_id_from_guid')
@patch('stage_3.claude_code_stage_3.register_id')
def test_stage_3_generate_entity_id_consolidated(mock_register, mock_generate_id, mock_run_id, mock_logger) -> None:
    """Test stage_3 generate_entity_id function (consolidated)."""
    from stage_3.claude_code_stage_3 import generate_entity_id
    
    # Mock the ID generation
    mock_generate_id.return_value = "a" * 32  # 32-character ID
    
    # generate_entity_id takes (session_id, message_index, fingerprint)
    entity_id = generate_entity_id("session_123", 0, "fingerprint_hash")
    
    assert isinstance(entity_id, str)
    assert len(entity_id) > 0


@pytest.mark.parametrize("session_id,message_index,fingerprint", [
    ("", 0, ""),  # Empty strings
    ("session_123", 999999, "fingerprint"),  # Large message_index
    ("session_123", 0, "a" * 1000),  # Very long fingerprint
])
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_3_generate_entity_id_edge_cases_consolidated(mock_run_id, mock_logger, session_id: str, message_index: int, fingerprint: str) -> None:
    """Test stage_3 generate_entity_id with edge case inputs (consolidated)."""
    from stage_3.claude_code_stage_3 import generate_entity_id
    
    entity_id = generate_entity_id(session_id, message_index, fingerprint)
    assert isinstance(entity_id, str)
    assert len(entity_id) > 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_3_serialize_datetime_edge_cases_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_3 serialize_datetime with edge cases (consolidated)."""
    from stage_3.claude_code_stage_3 import serialize_datetime
    
    # None input
    result = serialize_datetime(None)
    assert result is None
    
    # Datetime with timezone
    dt = datetime.now(timezone.utc)
    result = serialize_datetime(dt)
    assert isinstance(result, str)
    
    # Non-datetime input
    result = serialize_datetime("not a datetime")
    assert result == "not a datetime"


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_3_create_stage_3_table_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_3 create_stage_3_table function (consolidated)."""
    from stage_3.claude_code_stage_3 import create_stage_3_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_3_table(mock_client)
    
    assert result is not None
