"""Comprehensive tests for Stage 1 (Extraction).

Target: 90%+ coverage of stage_1/claude_code_stage_1.py
"""
from __future__ import annotations

import json
import sys
import tempfile
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


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_discover_session_files_exists(mock_run_id, mock_logger) -> None:
    """Test discover_session_files when directory exists."""
    # Import after mocking
    from stage_1.claude_code_stage_1 import discover_session_files
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create test JSONL files
        (tmp_path / "file1.jsonl").write_text('{"test": "data"}')
        (tmp_path / "file2.jsonl").write_text('{"test": "data2"}')
        
        files = discover_session_files(tmp_path)
        
        assert len(files) == 2
        assert all(f.suffix == ".jsonl" for f in files)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_discover_session_files_not_exists(mock_run_id, mock_logger) -> None:
    """Test discover_session_files when directory doesn't exist."""
    from stage_1.claude_code_stage_1 import discover_session_files
    
    non_existent = Path("/nonexistent/path/12345")
    files = discover_session_files(non_existent)
    assert files == []


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_discover_session_files_no_jsonl(mock_run_id, mock_logger) -> None:
    """Test discover_session_files when no JSONL files exist."""
    from stage_1.claude_code_stage_1 import discover_session_files
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        (tmp_path / "file.txt").write_text("not jsonl")
        
        files = discover_session_files(tmp_path)
        assert files == []


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_generate_session_id(mock_run_id, mock_logger) -> None:
    """Test _generate_session_id function."""
    from stage_1.claude_code_stage_1 import _generate_session_id
    
    file_path = Path("/test/path/session_123.jsonl")
    session_id = _generate_session_id(file_path)
    
    assert session_id is not None
    assert isinstance(session_id, str)
    assert len(session_id) > 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_parse_session_file_valid(mock_run_id, mock_logger) -> None:
    """Test parse_session_file with valid JSONL."""
    from stage_1.claude_code_stage_1 import parse_session_file
    
    sample_data = {
        "type": "user",
        "content": "Test message",
        "model": "claude-3-opus",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        json.dump(sample_data, f)
        f.write('\n')
        f.flush()
        
        try:
            records = list(parse_session_file(Path(f.name), run_id="test_run"))
            
            assert len(records) > 0
            assert records[0]["role"] == "user"
            assert records[0]["content"] == "Test message"
            assert "extraction_id" in records[0]
            assert "session_id" in records[0]
        finally:
            Path(f.name).unlink()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_parse_session_file_invalid_json(mock_run_id, mock_logger) -> None:
    """Test parse_session_file with invalid JSON."""
    from stage_1.claude_code_stage_1 import parse_session_file
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write("invalid json\n")
        f.flush()
        
        try:
            records = list(parse_session_file(Path(f.name), run_id="test_run"))
            
            # Should handle invalid JSON gracefully (skip invalid lines)
            assert isinstance(records, list)
            # May be empty if all lines are invalid
        finally:
            Path(f.name).unlink()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_parse_session_file_empty(mock_run_id, mock_logger) -> None:
    """Test parse_session_file with empty file."""
    from stage_1.claude_code_stage_1 import parse_session_file
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write("")
        f.flush()
        
        try:
            records = list(parse_session_file(Path(f.name), run_id="test_run"))
            
            assert isinstance(records, list)
            assert len(records) == 0
        finally:
            Path(f.name).unlink()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_create_stage_1_table(mock_run_id, mock_logger) -> None:
    """Test create_stage_1_table function."""
    from stage_1.claude_code_stage_1 import create_stage_1_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    # create_table with exists_ok=True handles both cases
    result = create_stage_1_table(mock_client)
    assert result == mock_table
    mock_client.create_table.assert_called()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_load_to_bigquery_success(mock_run_id, mock_logger) -> None:
    """Test load_to_bigquery with successful load."""
    from stage_1.claude_code_stage_1 import load_to_bigquery
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_client.insert_rows_json.return_value = []  # No errors
    
    rows = [{"field1": "value1", "field2": "value2"}]
    
    result = load_to_bigquery(mock_client, rows, dry_run=False)
    
    assert result == len(rows)
    mock_client.insert_rows_json.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_load_to_bigquery_empty_rows(mock_run_id, mock_logger) -> None:
    """Test load_to_bigquery with empty rows."""
    from stage_1.claude_code_stage_1 import load_to_bigquery
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    
    result = load_to_bigquery(mock_client, [], dry_run=False)
    
    # Should return 0 for empty rows
    assert result == 0
    mock_client.insert_rows_json.assert_not_called()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_load_to_bigquery_dry_run(mock_run_id, mock_logger) -> None:
    """Test load_to_bigquery in dry-run mode."""
    from stage_1.claude_code_stage_1 import load_to_bigquery
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    rows = [{"field1": "value1"}]
    
    result = load_to_bigquery(mock_client, rows, dry_run=True)
    
    assert result == len(rows)
    mock_client.insert_rows_json.assert_not_called()  # Should not insert in dry-run


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_load_to_bigquery_with_errors(mock_run_id, mock_logger) -> None:
    """Test load_to_bigquery with insert errors."""
    from stage_1.claude_code_stage_1 import load_to_bigquery
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_client.insert_rows_json.return_value = [{"error": "test error"}]
    
    rows = [{"field1": "value1"}]
    
    try:
        load_to_bigquery(mock_client, rows, dry_run=False)
        assert False, "Should raise ValueError on insert errors"
    except ValueError as e:
        assert "Failed to insert" in str(e)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_parse_session_file_with_summary(mock_run_id, mock_logger) -> None:
    """Test parse_session_file handles summary message."""
    from stage_1.claude_code_stage_1 import parse_session_file
    
    summary_data = {"type": "summary", "session_id": "test_session_123", "model": "claude-3-opus"}
    message_data = {"type": "user", "content": "Test message"}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        json.dump(summary_data, f)
        f.write('\n')
        json.dump(message_data, f)
        f.write('\n')
        f.flush()
        
        try:
            records = list(parse_session_file(Path(f.name), run_id="test_run"))
            
            # Should extract session_id from summary
            assert len(records) > 0
            assert records[0]["session_id"] == "test_session_123"
        finally:
            Path(f.name).unlink()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_parse_session_file_different_message_types(mock_run_id, mock_logger) -> None:
    """Test parse_session_file handles different message types."""
    from stage_1.claude_code_stage_1 import parse_session_file
    
    user_data = {"type": "user", "content": "User message"}
    assistant_data = {"type": "assistant", "content": "Assistant response"}
    tool_data = {"type": "tool_result", "output": "Tool output"}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        json.dump(user_data, f)
        f.write('\n')
        json.dump(assistant_data, f)
        f.write('\n')
        json.dump(tool_data, f)
        f.write('\n')
        f.flush()
        
        try:
            records = list(parse_session_file(Path(f.name), run_id="test_run"))
            
            assert len(records) == 3
            assert records[0]["role"] == "user"
            assert records[1]["role"] == "assistant"
            assert records[2]["role"] == "tool"
        finally:
            Path(f.name).unlink()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_parse_session_file_content_as_dict(mock_run_id, mock_logger) -> None:
    """Test parse_session_file handles content as dict/list."""
    from stage_1.claude_code_stage_1 import parse_session_file
    
    # Content as dict
    dict_data = {"type": "user", "content": {"text": "Message"}}
    # Content as list
    list_data = {"type": "assistant", "content": [{"type": "text", "text": "Response"}]}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        json.dump(dict_data, f)
        f.write('\n')
        json.dump(list_data, f)
        f.write('\n')
        f.flush()
        
        try:
            records = list(parse_session_file(Path(f.name), run_id="test_run"))
            
            assert len(records) == 2
            # Content should be JSON string
            assert isinstance(records[0]["content"], str)
            assert isinstance(records[1]["content"], str)
        finally:
            Path(f.name).unlink()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_parse_session_file_timestamp_parsing(mock_run_id, mock_logger) -> None:
    """Test parse_session_file parses timestamps correctly."""
    from stage_1.claude_code_stage_1 import parse_session_file
    
    # Valid timestamp
    valid_data = {"type": "user", "content": "Test", "timestamp": "2024-01-01T00:00:00Z"}
    # Invalid timestamp
    invalid_data = {"type": "assistant", "content": "Test", "timestamp": "invalid"}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        json.dump(valid_data, f)
        f.write('\n')
        json.dump(invalid_data, f)
        f.write('\n')
        f.flush()
        
        try:
            records = list(parse_session_file(Path(f.name), run_id="test_run"))
            
            assert len(records) == 2
            # First should have timestamp
            assert records[0]["timestamp"] is not None
            # Second may have None timestamp
        finally:
            Path(f.name).unlink()
