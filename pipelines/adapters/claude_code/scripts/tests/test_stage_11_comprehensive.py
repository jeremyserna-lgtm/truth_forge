"""Comprehensive tests for Stage 11 (Sentiment Analysis).

Target: Cover all functions with comprehensive tests including error handling and edge cases.
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
# STAGE 11 - SENTIMENT ANALYSIS
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_get_sentiment_pipeline_available(mock_run_id, mock_logger) -> None:
    """Test get_sentiment_pipeline when transformers is available."""
    from stage_11.claude_code_stage_11 import get_sentiment_pipeline
    
    try:
        import transformers
    except ImportError:
        pytest.skip("transformers not available")
    
    with patch('stage_11.claude_code_stage_11.transformers.pipeline') as mock_pipeline:
        mock_pipeline.return_value = MagicMock()
        result = get_sentiment_pipeline()
        
        assert result is not None
        mock_pipeline.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_get_sentiment_pipeline_not_available(mock_run_id, mock_logger) -> None:
    """Test get_sentiment_pipeline when transformers is not available."""
    from stage_11.claude_code_stage_11 import get_sentiment_pipeline
    
    with patch('builtins.__import__', side_effect=ImportError("No module named 'transformers'")):
        with pytest.raises(ImportError):
            get_sentiment_pipeline()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_process_sentiment_batch_empty(mock_run_id, mock_logger) -> None:
    """Test process_sentiment_batch with empty input."""
    from stage_11.claude_code_stage_11 import process_sentiment_batch
    
    try:
        import transformers
    except ImportError:
        pytest.skip("transformers not available")
    
    mock_pipeline = MagicMock()
    mock_pipeline.return_value = []
    
    results = process_sentiment_batch(mock_pipeline, [], threshold=0.5)
    
    assert isinstance(results, list)
    assert len(results) == 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_process_sentiment_batch_with_texts(mock_run_id, mock_logger) -> None:
    """Test process_sentiment_batch with texts."""
    from stage_11.claude_code_stage_11 import process_sentiment_batch
    
    try:
        import transformers
    except ImportError:
        pytest.skip("transformers not available")
    
    mock_pipeline = MagicMock()
    # Return list of lists (one list per text)
    mock_pipeline.return_value = [
        [{"label": "POSITIVE", "score": 0.95}],
        [{"label": "NEGATIVE", "score": 0.90}]
    ]
    
    texts = ["Great!", "Terrible."]
    results = process_sentiment_batch(mock_pipeline, texts, threshold=0.5)
    
    assert isinstance(results, list)
    assert len(results) == len(texts)
    assert all("primary_emotion" in r for r in results)
    assert all("primary_emotion_score" in r for r in results)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_process_sentiment_batch_below_threshold(mock_run_id, mock_logger) -> None:
    """Test process_sentiment_batch with scores below threshold."""
    from stage_11.claude_code_stage_11 import process_sentiment_batch
    
    try:
        import transformers
    except ImportError:
        pytest.skip("transformers not available")
    
    mock_pipeline = MagicMock()
    # Return scores below threshold
    mock_pipeline.return_value = [
        [{"label": "POSITIVE", "score": 0.3}]  # Below 0.5 threshold
    ]
    
    texts = ["Uncertain text"]
    results = process_sentiment_batch(mock_pipeline, texts, threshold=0.5)
    
    assert isinstance(results, list)
    assert len(results) == len(texts)
    # Should still return results, but may have different handling


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_process_sentiment_empty_input(mock_run_id, mock_logger) -> None:
    """Test process_sentiment with empty input."""
    from stage_11.claude_code_stage_11 import process_sentiment
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])
    mock_client.query.return_value = mock_query_job
    
    try:
        import transformers
    except ImportError:
        pytest.skip("transformers not available")
    
    with patch('stage_11.claude_code_stage_11.get_sentiment_pipeline') as mock_get_pipeline:
        mock_pipeline = MagicMock()
        mock_get_pipeline.return_value = mock_pipeline
        
        result = process_sentiment(mock_client, "test_run", batch_size=100, dry_run=True)
        
        assert isinstance(result, dict)
        assert "dry_run" in result or "processed" in result or "total" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_process_sentiment_bigquery_error(mock_run_id, mock_logger) -> None:
    """Test process_sentiment handles BigQuery errors."""
    from stage_11.claude_code_stage_11 import process_sentiment
    from google.cloud import bigquery
    from google.api_core import exceptions as google_exceptions
    
    mock_client = Mock(spec=bigquery.Client)
    mock_client.query.side_effect = google_exceptions.ServiceUnavailable("Service unavailable")
    
    with pytest.raises(google_exceptions.ServiceUnavailable):
        process_sentiment(mock_client, "test_run", batch_size=100, threshold=0.3, dry_run=True)
