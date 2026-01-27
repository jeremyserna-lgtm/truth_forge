"""Comprehensive tests for Stage 0.

Target: 90%+ coverage of assessment stage.
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
def test_stage_0_parse_session_file(mock_run_id, mock_logger) -> None:
    """Test stage_0 parse_session_file function."""
    from stage_0.claude_code_stage_0 import parse_session_file
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        # JSONL format - one JSON object per line
        session_data1 = {
            "messages": [
                {"role": "user", "content": "Test message 1"},
                {"role": "assistant", "content": "Test response 1"}
            ]
        }
        json.dump(session_data1, f)
        f.write('\n')
        f.flush()
        file_path = Path(f.name)
    
    try:
        result = parse_session_file(file_path)
        
        assert isinstance(result, dict)
        assert "message_count" in result
        assert "message_types" in result
        assert "models_used" in result
    finally:
        file_path.unlink(missing_ok=True)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_0_generate_assessment_report(mock_run_id, mock_logger) -> None:
    """Test stage_0 generate_assessment_report function."""
    from stage_0.claude_code_stage_0 import generate_assessment_report
    from collections import defaultdict
    
    session_files = [
        Path("/test/session1.jsonl"),
        Path("/test/session2.jsonl")
    ]
    
    # Mock parse_session_file to return sample data with all required fields
    with patch('stage_0.claude_code_stage_0.parse_session_file') as mock_parse:
        mock_parse.return_value = {
            "message_count": 10,
            "total_cost_usd": 0.01,
            "message_types": defaultdict(int, {"user": 5, "assistant": 5}),
            "models_used": {"gpt-4"},
            "tools_used": defaultdict(int),
            "errors": [],
            "timestamps": ["2024-01-01T00:00:00Z"]
        }
        
        report = generate_assessment_report(session_files, sample_size=100)
        
        assert isinstance(report, dict)
        assert "summary" in report
        assert "recommendations" in report
        assert "go_no_go" in report


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_0_determine_go_no_go(mock_run_id, mock_logger) -> None:
    """Test stage_0 _determine_go_no_go function."""
    from stage_0.claude_code_stage_0 import _determine_go_no_go
    
    # Test GO scenario - report has summary dict with files_sampled
    go_report = {
        "summary": {
            "total_files_discovered": 10,
            "files_sampled": 10,
            "total_messages": 100,
            "files_with_errors": 0
        },
        "files_analyzed": []
    }
    
    result = _determine_go_no_go(go_report)
    assert "GO" in result or "CAUTION" in result
    
    # Test NO-GO scenario
    no_go_report = {
        "summary": {
            "total_files_discovered": 10,
            "files_sampled": 10,
            "total_messages": 100,
            "files_with_errors": 10  # All files have errors
        },
        "files_analyzed": [{"errors": ["critical"]}]
    }
    
    result = _determine_go_no_go(no_go_report)
    assert "NO-GO" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_0_save_report(mock_run_id, mock_logger) -> None:
    """Test stage_0 save_report function."""
    from stage_0.claude_code_stage_0 import save_report
    import tempfile
    import json
    
    report = {
        "assessment_timestamp": "2024-01-01T00:00:00Z",
        "run_id": "test_run",
        "summary": {
            "total_files_discovered": 10,
            "total_messages": 100
        },
        "recommendations": ["test"]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_path = Path(f.name)
    
    try:
        save_report(report, output_path)
        
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        
        # Verify it's valid JSON
        with open(output_path, 'r') as f:
            loaded = json.load(f)
            assert "summary" in loaded
    finally:
        output_path.unlink(missing_ok=True)
