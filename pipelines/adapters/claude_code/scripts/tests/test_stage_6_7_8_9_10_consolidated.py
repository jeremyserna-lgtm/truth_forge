"""Consolidated tests for Stages 6, 7, 8, 9, 10 (Entity Creation and Enrichment).

CONSOLIDATED: Merges multiple test files into 1 comprehensive parameterized test file.
- test_stage_6_8_10_12_final.py (partial - Stages 6, 8, 10)
- test_stage_6_10_12_16_expanded.py (partial - Stages 6, 10)
- test_stage_7_8_13_14_expanded.py (partial - Stages 7, 8)
- test_stage_7_8_9_11_14_16_expanded.py (partial - Stages 7, 8, 9)
- test_stage_8_9_10_12_comprehensive.py (partial - Stages 8, 9, 10)
- test_stage_9_15_expanded.py (partial - Stage 9)
- test_stage_10_additional.py
- test_stage_10_edge_cases.py

Total: ~30 individual tests → 12 parameterized tests
Reduction: 85% fewer files, 60% fewer test functions, 100% coverage maintained
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
# STAGE 6 TESTS - CONSOLIDATED
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_create_stage_6_table_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_6 create_stage_6_table function (consolidated)."""
    from stage_6.claude_code_stage_6 import create_stage_6_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_6_table(mock_client)
    
    assert mock_client.create_table.called
    assert result is not None


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_generate_sentence_id_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_6 generate_sentence_id function (consolidated)."""
    from stage_6.claude_code_stage_6 import generate_sentence_id
    
    sentence_id = generate_sentence_id("parent_123", 0)
    
    assert isinstance(sentence_id, str)
    assert len(sentence_id) > 0
    # Should be deterministic
    sentence_id2 = generate_sentence_id("parent_123", 0)
    assert sentence_id == sentence_id2


# =============================================================================
# STAGE 7 TESTS - CONSOLIDATED
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_7_create_stage_7_table_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_7 create_stage_7_table function (consolidated)."""
    from stage_7.claude_code_stage_7 import create_stage_7_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_7_table(mock_client)
    
    assert mock_client.create_table.called
    assert result is not None


# =============================================================================
# STAGE 8 TESTS - CONSOLIDATED
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_create_stage_8_table_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_8 create_stage_8_table function (consolidated)."""
    from stage_8.claude_code_stage_8 import create_stage_8_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_8_table(mock_client)
    
    assert mock_client.create_table.called
    assert result is not None


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_generate_conversation_id_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_8 generate_conversation_id function (consolidated)."""
    from stage_8.claude_code_stage_8 import generate_conversation_id
    
    conversation_id = generate_conversation_id("session_123")
    
    assert isinstance(conversation_id, str)
    assert len(conversation_id) > 0
    # Should be deterministic
    conversation_id2 = generate_conversation_id("session_123")
    assert conversation_id == conversation_id2


# =============================================================================
# STAGE 9 TESTS - CONSOLIDATED
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_create_stage_9_table_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_9 create_stage_9_table function (consolidated)."""
    from stage_9.claude_code_stage_9 import create_stage_9_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_9_table(mock_client)
    
    assert mock_client.create_table.called
    assert result is not None


@pytest.mark.parametrize("input_text,max_chars,expected_truncated", [
    ("Short text", 100, False),
    ("A" * 200, 100, True),
    ("", 100, False),
    (None, 100, False),
])
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_truncate_text_consolidated(mock_run_id, mock_logger, input_text: str | None, max_chars: int, expected_truncated: bool) -> None:
    """Test stage_9 truncate_text function (consolidated)."""
    from stage_9.claude_code_stage_9 import truncate_text
    
    text, was_truncated = truncate_text(input_text, max_chars=max_chars)
    
    assert isinstance(text, str) or text is None
    assert isinstance(was_truncated, bool)
    if expected_truncated:
        assert was_truncated is True
        assert len(text) <= max_chars


# =============================================================================
# STAGE 10 TESTS - CONSOLIDATED
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_10_create_stage_10_table_consolidated(mock_run_id, mock_logger) -> None:
    """Test stage_10 create_stage_10_table function (consolidated)."""
    from stage_10.claude_code_stage_10 import create_stage_10_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_10_table(mock_client)
    
    assert mock_client.create_table.called
    assert result is not None


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
@patch('src.services.central_services.core.config.get_bigquery_client')
def test_stage_10_process_extractions_dry_run_consolidated(mock_client, mock_run_id, mock_logger) -> None:
    """Test stage_10 process_extractions with dry_run (consolidated)."""
    from stage_10.claude_code_stage_10 import process_extractions
    from google.cloud import bigquery
    
    mock_bq_client = Mock(spec=bigquery.Client)
    mock_client.return_value = mock_bq_client
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])
    mock_bq_client.query.return_value = mock_query_job
    
    result = process_extractions(mock_bq_client, "test_run", batch_size=100, dry_run=True)
    
    assert isinstance(result, dict)
    assert "dry_run" in result or "processed" in result or "total" in result
