"""DEPRECATED: Comprehensive tests for Stages 8, 9, 10, 11, 12.

⚠️  THIS FILE IS DEPRECATED AND WILL BE REMOVED
    Superseded by:
    - test_stage_8_9_10_12_comprehensive.py
    - test_stage_6_11_13_comprehensive.py
    
Target: 90%+ coverage of stage processing functions.
"""
from __future__ import annotations

import sys
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
def test_stage_8_create_table(mock_run_id, mock_logger) -> None:
    """Test stage_8 create_stage_8_table."""
    from stage_8.claude_code_stage_8 import create_stage_8_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_8_table(mock_client)
    assert result == mock_table


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_8_generate_conversation_id(mock_run_id, mock_logger) -> None:
    """Test stage_8 generate_conversation_id."""
    from stage_8.claude_code_stage_8 import generate_conversation_id
    
    conv_id = generate_conversation_id("session_123")
    
    assert conv_id is not None
    assert isinstance(conv_id, str)
    assert len(conv_id) > 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_create_table(mock_run_id, mock_logger) -> None:
    """Test stage_9 create_stage_9_table."""
    from stage_9.claude_code_stage_9 import create_stage_9_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_9_table(mock_client)
    assert result == mock_table


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_9_truncate_text(mock_run_id, mock_logger) -> None:
    """Test stage_9 truncate_text."""
    from stage_9.claude_code_stage_9 import truncate_text
    
    text, was_truncated = truncate_text("short text", max_chars=100)
    assert text == "short text"
    assert was_truncated is False
    
    long_text = "a" * 10000
    truncated, was_truncated = truncate_text(long_text, max_chars=8000)
    assert len(truncated) == 8000
    assert was_truncated is True


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_10_create_table(mock_run_id, mock_logger) -> None:
    """Test stage_10 create_stage_10_table."""
    from stage_10.claude_code_stage_10 import create_stage_10_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_10_table(mock_client)
    assert result == mock_table


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_create_table(mock_run_id, mock_logger) -> None:
    """Test stage_11 create_stage_11_table."""
    from stage_11.claude_code_stage_11 import create_stage_11_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_11_table(mock_client)
    assert result == mock_table


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_create_table(mock_run_id, mock_logger) -> None:
    """Test stage_12 create_stage_12_table."""
    from stage_12.claude_code_stage_12 import create_stage_12_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_12_table(mock_client)
    assert result == mock_table


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_extract_keywords(mock_run_id, mock_logger) -> None:
    """Test stage_12 extract_keywords."""
    from stage_12.claude_code_stage_12 import extract_keywords
    from unittest.mock import Mock
    
    mock_model = Mock()
    # extract_keywords returns list of tuples (keyword, score)
    mock_keywords = [("keyword1", 0.9), ("keyword2", 0.8)]
    mock_model.extract_keywords.return_value = mock_keywords
    
    keywords = extract_keywords(mock_model, "test text with enough content to extract keywords", top_n=5)
    
    assert isinstance(keywords, list)
    # extract_keywords returns list of (keyword, score) tuples
    assert len(keywords) <= 5
