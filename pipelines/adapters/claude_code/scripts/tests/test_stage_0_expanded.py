"""Expanded tests for Stage 0.

Target: Increase coverage for assessment stage.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import json
from collections import defaultdict

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
def test_stage_0_generate_recommendations(mock_run_id, mock_logger) -> None:
    """Test stage_0 _generate_recommendations function."""
    from stage_0.claude_code_stage_0 import _generate_recommendations
    
    # Test with various report configurations - must include all required keys
    report1 = {
        "summary": {
            "total_files_discovered": 0,
            "total_messages": 0,
            "files_sampled": 0,
            "files_with_errors": 0,
            "message_types": {},
            "total_cost_usd": 0.0
        }
    }
    recommendations = _generate_recommendations(report1)
    assert isinstance(recommendations, list)
    
    # Test with files but no messages
    report2 = {
        "summary": {
            "total_files_discovered": 10,
            "total_messages": 0,
            "files_sampled": 10,
            "files_with_errors": 0,
            "message_types": {},
            "total_cost_usd": 0.0
        }
    }
    recommendations = _generate_recommendations(report2)
    assert isinstance(recommendations, list)
    
    # Test with normal data
    report3 = {
        "summary": {
            "total_files_discovered": 10,
            "total_messages": 100,
            "files_sampled": 10,
            "files_with_errors": 0,
            "message_types": {"user": 50, "assistant": 50},
            "total_cost_usd": 0.01
        }
    }
    recommendations = _generate_recommendations(report3)
    assert isinstance(recommendations, list)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_0_discover_session_files_expanded(mock_run_id, mock_logger) -> None:
    """Test stage_0 discover_session_files function with expanded coverage."""
    from stage_0.claude_code_stage_0 import discover_session_files
    import tempfile
    from pathlib import Path
    
    # Create temporary directory with JSONL files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create some JSONL files
        (tmp_path / "session1.jsonl").write_text('{"type": "message", "content": "test"}')
        (tmp_path / "session2.jsonl").write_text('{"type": "message", "content": "test2"}')
        (tmp_path / "not_jsonl.txt").write_text("not a jsonl file")
        
        files = discover_session_files(tmp_path)
        
        assert isinstance(files, list)
        assert len(files) == 2  # Only JSONL files
        assert all(f.suffix == ".jsonl" for f in files)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_0_parse_session_file_edge_cases(mock_run_id, mock_logger) -> None:
    """Test stage_0 parse_session_file function with edge cases."""
    from stage_0.claude_code_stage_0 import parse_session_file
    import tempfile
    
    # Test with empty file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        file_path = Path(f.name)
    
    try:
        result = parse_session_file(file_path)
        assert isinstance(result, dict)
        assert result["message_count"] == 0
    finally:
        file_path.unlink(missing_ok=True)
    
    # Test with invalid JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write("invalid json\n")
        f.flush()
        file_path = Path(f.name)
    
    try:
        result = parse_session_file(file_path)
        assert isinstance(result, dict)
        assert len(result.get("errors", [])) > 0  # Should have parse errors
    finally:
        file_path.unlink(missing_ok=True)
