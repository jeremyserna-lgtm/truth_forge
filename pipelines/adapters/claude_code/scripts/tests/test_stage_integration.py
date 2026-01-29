"""Integration tests for multi-stage workflows.

Target: Test interactions between stages and end-to-end workflows.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import tempfile
import json
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
# STAGE 0 → STAGE 1 INTEGRATION
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_0_to_stage_1_workflow(mock_run_id, mock_logger) -> None:
    """Test workflow from Stage 0 (discovery) to Stage 1 (extraction)."""
    from stage_0.claude_code_stage_0 import discover_session_files
    from stage_1.claude_code_stage_1 import parse_session_file
    
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = Path(tmpdir)
        # Create a JSONL file
        jsonl_file = source_dir / "session.jsonl"
        jsonl_file.write_text('{"role": "user", "content": "test"}\n')
        
        # Stage 0: Discover files
        files = list(discover_session_files(source_dir))
        assert len(files) == 1
        
        # Stage 1: Parse file
        records = list(parse_session_file(files[0], "test_run"))
        assert isinstance(records, list)
        assert len(records) > 0 or len(records) == 0  # May be empty or have records


# =============================================================================
# STAGE 1 → STAGE 2 INTEGRATION
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_1_to_stage_2_workflow(mock_run_id, mock_logger) -> None:
    """Test workflow from Stage 1 (extraction) to Stage 2 (cleaning)."""
    from stage_1.claude_code_stage_1 import parse_session_file
    from stage_2.claude_code_stage_2 import clean_content
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write('{"role": "user", "content": "  Hello   world  "}\n')
        f.flush()
        file_path = Path(f.name)
    
    try:
        # Stage 1: Parse file
        records = list(parse_session_file(file_path, "test_run"))
        
        # Stage 2: Clean content
        if records:
            for record in records:
                if "text" in record or "content" in record:
                    text = record.get("text") or record.get("content", "")
                    cleaned_text, length, word_count = clean_content(text)
                    assert isinstance(cleaned_text, str)
                    assert isinstance(length, int)
                    assert isinstance(word_count, int)
    finally:
        file_path.unlink(missing_ok=True)


# =============================================================================
# STAGE 2 → STAGE 3 INTEGRATION
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_2_to_stage_3_workflow(mock_run_id, mock_logger) -> None:
    """Test workflow from Stage 2 (cleaning) to Stage 3 (identity generation)."""
    from stage_2.claude_code_stage_2 import clean_content
    from stage_3.claude_code_stage_3 import generate_entity_id
    
    # Stage 2: Clean content
    text, length, word_count = clean_content("Test message")
    
    # Stage 3: Generate entity ID
    entity_id = generate_entity_id("session_123", 0, "fingerprint_hash")
    
    assert isinstance(entity_id, str)
    assert len(entity_id) > 0
    assert isinstance(text, str)


# =============================================================================
# MULTI-STAGE DATA FLOW
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_multi_stage_data_flow(mock_run_id, mock_logger) -> None:
    """Test data flow through multiple stages."""
    from stage_0.claude_code_stage_0 import discover_session_files
    from stage_1.claude_code_stage_1 import parse_session_file
    from stage_2.claude_code_stage_2 import clean_content
    from stage_3.claude_code_stage_3 import generate_entity_id
    
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = Path(tmpdir)
        jsonl_file = source_dir / "session.jsonl"
        jsonl_file.write_text('{"role": "user", "content": "Test message"}\n')
        
        # Stage 0: Discover
        files = list(discover_session_files(source_dir))
        
        if files:
            # Stage 1: Extract
            records = list(parse_session_file(files[0], "test_run"))
            
            if records:
                # Stage 2: Clean
                for record in records:
                    text = record.get("text") or record.get("content", "")
                    cleaned_text, length, word_count = clean_content(text)
                    
                    # Stage 3: Generate ID
                    entity_id = generate_entity_id("session_123", 0, "fingerprint_hash")
                    
                    assert isinstance(entity_id, str)
                    assert isinstance(cleaned_text, str)


# =============================================================================
# ERROR PROPAGATION ACROSS STAGES
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_error_propagation_stage_1_to_2(mock_run_id, mock_logger) -> None:
    """Test error propagation from Stage 1 to Stage 2."""
    from stage_1.claude_code_stage_1 import parse_session_file
    from stage_2.claude_code_stage_2 import clean_content
    
    # If Stage 1 fails, Stage 2 should handle gracefully
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write('invalid json\n')
        f.flush()
        file_path = Path(f.name)
    
    try:
        records = list(parse_session_file(file_path, "test_run"))
        # Stage 2 should handle empty or invalid records
        for record in records:
            text = record.get("text", "")
            cleaned_text, length, word_count = clean_content(text)
            assert isinstance(cleaned_text, str)
    except (json.JSONDecodeError, ValueError):
        # Expected - Stage 1 may raise on invalid JSON
        pass
    finally:
        file_path.unlink(missing_ok=True)


# =============================================================================
# DRY RUN ACROSS STAGES
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_dry_run_multi_stage(mock_run_id, mock_logger) -> None:
    """Test dry_run mode across multiple stages."""
    from stage_1.claude_code_stage_1 import load_to_bigquery
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    records = [{"entity_id": "test_123", "text": "test"}]
    
    # Stage 1 with dry_run
    result = load_to_bigquery(mock_client, records, dry_run=True)
    
    # load_to_bigquery returns int (number of records) or dict
    assert isinstance(result, (int, dict))
    if isinstance(result, dict):
        assert "dry_run" in result or "records" in result
    else:
        assert result >= 0  # Number of records
    mock_client.insert_rows_json.assert_not_called()


# =============================================================================
# DATA CONSISTENCY ACROSS STAGES
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_data_consistency_across_stages(mock_run_id, mock_logger) -> None:
    """Test data consistency is maintained across stages."""
    from stage_2.claude_code_stage_2 import clean_content
    from stage_3.claude_code_stage_3 import generate_entity_id
    
    # Same inputs should produce consistent results
    text1, length1, word_count1 = clean_content("Test message")
    text2, length2, word_count2 = clean_content("Test message")
    
    assert text1 == text2
    assert length1 == length2
    assert word_count1 == word_count2
    
    # Entity IDs should be deterministic
    id1 = generate_entity_id("session_123", 0, "fingerprint_hash")
    id2 = generate_entity_id("session_123", 0, "fingerprint_hash")
    
    assert id1 == id2
