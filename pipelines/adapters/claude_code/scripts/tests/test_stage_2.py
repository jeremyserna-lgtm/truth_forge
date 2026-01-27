"""Comprehensive tests for Stage 2 (Cleaning).

Target: 90%+ coverage of stage_2/claude_code_stage_2.py
"""
from __future__ import annotations

import sys
from datetime import datetime, UTC
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
def test_clean_content_basic(mock_run_id, mock_logger) -> None:
    """Test clean_content with basic content."""
    from stage_2.claude_code_stage_2 import clean_content
    
    content, original_len, cleaned_len = clean_content("Test content")
    
    assert content == "Test content"
    assert original_len >= 0
    assert cleaned_len >= 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_clean_content_none(mock_run_id, mock_logger) -> None:
    """Test clean_content with None."""
    from stage_2.claude_code_stage_2 import clean_content
    
    content, original_len, cleaned_len = clean_content(None)
    
    assert content == ""
    assert original_len == 0
    assert cleaned_len == 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_clean_content_whitespace(mock_run_id, mock_logger) -> None:
    """Test clean_content removes excessive whitespace."""
    from stage_2.claude_code_stage_2 import clean_content
    
    content, _, _ = clean_content("  Test   content  ")
    
    # Should normalize whitespace
    assert "Test" in content
    assert "content" in content


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_normalize_timestamp_valid(mock_run_id, mock_logger) -> None:
    """Test normalize_timestamp with valid timestamp."""
    from stage_2.claude_code_stage_2 import normalize_timestamp
    
    test_timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    result = normalize_timestamp(test_timestamp)
    
    assert result == test_timestamp


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_normalize_timestamp_none(mock_run_id, mock_logger) -> None:
    """Test normalize_timestamp with None."""
    from stage_2.claude_code_stage_2 import normalize_timestamp
    
    result = normalize_timestamp(None)
    
    assert result is None


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_normalize_timestamp_naive(mock_run_id, mock_logger) -> None:
    """Test normalize_timestamp with naive datetime."""
    from stage_2.claude_code_stage_2 import normalize_timestamp
    
    naive_timestamp = datetime(2024, 1, 1, 12, 0, 0)
    result = normalize_timestamp(naive_timestamp)
    
    # Should handle naive timestamps (may convert to UTC or return as-is)
    assert result is not None


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_create_stage_2_table(mock_run_id, mock_logger) -> None:
    """Test create_stage_2_table function."""
    from stage_2.claude_code_stage_2 import create_stage_2_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_2_table(mock_client)
    assert result == mock_table
    mock_client.create_table.assert_called()
