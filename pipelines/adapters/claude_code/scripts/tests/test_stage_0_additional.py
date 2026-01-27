"""Additional comprehensive tests for Stage 0.

Target: Increase coverage for assessment stage.
Focus on uncovered functions and edge cases.
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


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_0_discover_session_files_empty_dir(mock_run_id, mock_logger) -> None:
    """Test stage_0 discover_session_files with empty directory."""
    from stage_0.claude_code_stage_0 import discover_session_files
    
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = Path(tmpdir)
        # No files in directory
        
        sessions = discover_session_files(source_dir)
        
        assert isinstance(sessions, list)
        assert len(sessions) == 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_0_discover_session_files_nonexistent_dir(mock_run_id, mock_logger) -> None:
    """Test stage_0 discover_session_files with nonexistent directory."""
    from stage_0.claude_code_stage_0 import discover_session_files
    
    nonexistent_dir = Path("/nonexistent/directory/that/does/not/exist")
    
    sessions = discover_session_files(nonexistent_dir)
    
    assert isinstance(sessions, list)
    assert len(sessions) == 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_0_parse_session_file_with_tool_use(mock_run_id, mock_logger) -> None:
    """Test stage_0 parse_session_file with tool_use messages."""
    from stage_0.claude_code_stage_0 import parse_session_file
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        # Create JSONL with tool_use message
        tool_msg = {
            "type": "tool_use",
            "name": "read_file",
            "input": {"path": "test.py"}
        }
        json.dump(tool_msg, f)
        f.write('\n')
        f.flush()
        file_path = Path(f.name)
    
    try:
        result = parse_session_file(file_path)
        
        assert isinstance(result, dict)
        assert "message_count" in result
        assert "tools_used" in result
        assert "read_file" in result["tools_used"]
    finally:
        file_path.unlink(missing_ok=True)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_0_parse_session_file_with_summary(mock_run_id, mock_logger) -> None:
    """Test stage_0 parse_session_file with summary messages."""
    from stage_0.claude_code_stage_0 import parse_session_file
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        # Create JSONL with summary message
        summary_msg = {
            "type": "summary",
            "model": "claude-3-opus",
            "cost_usd": 0.05
        }
        json.dump(summary_msg, f)
        f.write('\n')
        f.flush()
        file_path = Path(f.name)
    
    try:
        result = parse_session_file(file_path)
        
        assert isinstance(result, dict)
        assert "models_used" in result
        assert "claude-3-opus" in result["models_used"]
        assert result["total_cost_usd"] > 0
    finally:
        file_path.unlink(missing_ok=True)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_0_print_summary(mock_run_id, mock_logger) -> None:
    """Test stage_0 _print_summary function."""
    from stage_0.claude_code_stage_0 import _print_summary
    import tempfile
    
    report = {
        "go_no_go": "GO: Data ready for processing",
        "summary": {
            "total_files_discovered": 10,
            "files_sampled": 5,
            "total_messages": 100,
            "models_used": ["claude-3-opus", "gpt-4"]
        },
        "recommendations": ["OK: Data appears well-formed"]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_path = Path(f.name)
    
    try:
        # Should not raise exception
        _print_summary(report, output_path)
        
        # Function uses print() for console output, so we just verify it doesn't crash
        assert True
    finally:
        output_path.unlink(missing_ok=True)
