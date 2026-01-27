"""Comprehensive tests for Stages 4 and 5.

Target: 90%+ coverage of stage_4 and stage_5 processing functions.
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
def test_stage_4_process_staging_basic(mock_run_id, mock_logger) -> None:
    """Test stage_4 process_staging function."""
    from stage_4.claude_code_stage_4 import process_staging
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.cnt = 0
    mock_query_job.result.return_value = [mock_row]
    mock_client.query.return_value = mock_query_job
    
    # process_staging returns dict, not generator
    result = process_staging(mock_client, "test_run", dry_run=True)
    
    assert isinstance(result, dict)
    assert "input_rows" in result or "output_rows" in result or "dry_run" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_tokenize_message(mock_run_id, mock_logger) -> None:
    """Test stage_5 tokenize_message function."""
    from stage_5.claude_code_stage_5 import tokenize_message
    from unittest.mock import Mock
    
    mock_nlp = Mock()
    mock_doc = Mock()
    mock_token1 = Mock(text="This", lemma_="this", pos_="DET", tag_="DT", dep_="det", is_stop=True, is_alpha=True, is_punct=False)
    mock_token2 = Mock(text="is", lemma_="be", pos_="VERB", tag_="VBZ", dep_="ROOT", is_stop=True, is_alpha=True, is_punct=False)
    mock_doc.__iter__ = Mock(return_value=iter([mock_token1, mock_token2]))
    mock_nlp.return_value = mock_doc
    
    message = {
        "entity_id": "parent_123",
        "text": "This is a test message",
        "session_id": "session_123",
        "content_date": "2024-01-01"
    }
    
    tokens = list(tokenize_message(message, mock_nlp, run_id="test_run", created_at="2024-01-01T00:00:00Z"))
    
    assert isinstance(tokens, list)
    assert len(tokens) > 0
    assert all("entity_id" in token for token in tokens)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_5_process_tokenization(mock_run_id, mock_logger) -> None:
    """Test stage_5 process_tokenization function."""
    # Skip if spacy not available - this is a dependency issue, not a code issue
    try:
        import spacy
    except ImportError:
        import pytest
        pytest.skip("spacy not available - skipping test")
    
    from stage_5.claude_code_stage_5 import process_tokenization
    from google.cloud import bigquery
    from unittest.mock import Mock
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = []  # Empty result
    mock_client.query.return_value = mock_query_job
    
    # This will fail if spacy not installed, but that's expected
    # In a real environment, spacy would be installed
    try:
        result = process_tokenization(mock_client, "test_run", batch_size=100, dry_run=True)
        assert isinstance(result, dict)
        assert "processed" in result or "total" in result or "count" in result or "dry_run" in result
    except (ImportError, ModuleNotFoundError):
        # Expected if spacy not installed - skip test
        import pytest
        pytest.skip("spacy not available")
