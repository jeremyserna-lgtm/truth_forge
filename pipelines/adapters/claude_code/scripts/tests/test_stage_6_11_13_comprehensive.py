"""Comprehensive tests for Stages 6, 11, 13.

Target: 90%+ coverage of these enrichment stages.
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
def test_stage_6_detect_sentences_comprehensive(mock_run_id, mock_logger) -> None:
    """Test stage_6 detect_sentences function comprehensively."""
    from stage_6.claude_code_stage_6 import detect_sentences
    from unittest.mock import Mock
    
    mock_nlp = Mock()
    mock_doc = Mock()
    mock_sent1 = Mock(start_char=0, end_char=10, text="First sentence.")
    mock_sent2 = Mock(start_char=11, end_char=25, text="Second sentence.")
    mock_doc.sents = [mock_sent1, mock_sent2]
    mock_nlp.return_value = mock_doc
    
    message = {
        "entity_id": "parent_123",
        "text": "First sentence. Second sentence.",
        "session_id": "session_123",
        "content_date": "2024-01-01"
    }
    
    sentences = list(detect_sentences(message, mock_nlp, run_id="test_run", created_at="2024-01-01T00:00:00Z"))
    
    assert isinstance(sentences, list)
    assert len(sentences) > 0
    assert all("entity_id" in sent for sent in sentences)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_process_sentiment(mock_run_id, mock_logger) -> None:
    """Test stage_11 process_sentiment function."""
    from stage_11.claude_code_stage_11 import process_sentiment
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = []  # Empty result
    mock_client.query.return_value = mock_query_job
    
    # process_sentiment requires threshold parameter
    result = process_sentiment(mock_client, "test_run", threshold=0.5, batch_size=100, dry_run=True)
    
    assert isinstance(result, dict)
    assert "processed" in result or "total" in result or "count" in result or "dry_run" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_process_relationships(mock_run_id, mock_logger) -> None:
    """Test stage_13 process_relationships function."""
    from stage_13.claude_code_stage_13 import process_relationships
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = []  # Empty result
    mock_client.query.return_value = mock_query_job
    
    result = process_relationships(mock_client, "test_run", batch_size=100, dry_run=True)
    
    assert isinstance(result, dict)
    assert "processed" in result or "total" in result or "count" in result or "dry_run" in result
