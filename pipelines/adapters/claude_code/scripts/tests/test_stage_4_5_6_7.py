"""DEPRECATED: Comprehensive tests for Stages 4, 5, 6, 7.

⚠️  THIS FILE IS DEPRECATED AND WILL BE REMOVED
    Superseded by:
    - test_stage_4_5_comprehensive.py
    - test_stage_6_11_13_comprehensive.py
    - test_stage_7_14_comprehensive.py
    
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
def test_stage_4_create_table(mock_run_id, mock_logger) -> None:
    """Test stage_4 create_stage_4_table."""
    from stage_4.claude_code_stage_4 import create_stage_4_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_4_table(mock_client)
    assert result == mock_table


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_generate_token_id(mock_run_id, mock_logger) -> None:
    """Test stage_5 generate_token_id."""
    from stage_5.claude_code_stage_5 import generate_token_id
    
    token_id = generate_token_id(parent_id="parent_123", token_index=0)
    
    assert token_id is not None
    assert isinstance(token_id, str)
    assert "parent_123" in token_id or "0" in token_id


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_generate_sentence_id(mock_run_id, mock_logger) -> None:
    """Test stage_6 generate_sentence_id."""
    from stage_6.claude_code_stage_6 import generate_sentence_id
    
    sentence_id = generate_sentence_id(parent_id="parent_123", sentence_index=0)
    
    assert sentence_id is not None
    assert isinstance(sentence_id, str)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_6_detect_sentences(mock_run_id, mock_logger) -> None:
    """Test stage_6 detect_sentences."""
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
    
    # detect_sentences is a generator
    sentences = list(detect_sentences(
        message,
        nlp=mock_nlp,
        run_id="test_run",
        created_at="2024-01-01T00:00:00Z"
    ))
    
    # Should return list of sentence records
    assert len(sentences) == 2
    assert sentences[0]["text"] == "First sentence."
    assert sentences[1]["text"] == "Second sentence!"


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_7_create_table(mock_run_id, mock_logger) -> None:
    """Test stage_7 create_stage_7_table."""
    from stage_7.claude_code_stage_7 import create_stage_7_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock(spec=bigquery.Table)
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_7_table(mock_client)
    assert result == mock_table
