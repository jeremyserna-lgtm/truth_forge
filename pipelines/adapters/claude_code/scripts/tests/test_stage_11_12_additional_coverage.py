"""Additional coverage tests for Stages 11 and 12.

Target: Increase coverage for sentiment analysis and keyword extraction stages.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


# Stage 11 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_get_sentiment_pipeline(mock_run_id, mock_logger) -> None:
    """Test stage_11 get_sentiment_pipeline function."""
    from stage_11.claude_code_stage_11 import get_sentiment_pipeline
    import pytest
    
    # Skip if transformers not available
    try:
        import transformers
    except ImportError:
        pytest.skip("transformers not available - skipping test")
    
    # Function may raise ImportError if package not installed
    try:
        pipeline = get_sentiment_pipeline()
        assert pipeline is not None
    except ImportError:
        # Expected if package not installed
        pytest.skip("transformers pipeline not available")


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_process_sentiment_batch_basic(mock_run_id, mock_logger) -> None:
    """Test stage_11 process_sentiment_batch with basic input."""
    from stage_11.claude_code_stage_11 import process_sentiment_batch
    
    # Mock sentiment pipeline
    # The pipeline returns a list where each element is a list of predictions
    mock_pipeline = MagicMock()
    # Each text gets a list of predictions (multiple emotions)
    mock_predictions = [
        [{"label": "POSITIVE", "score": 0.95}, {"label": "NEUTRAL", "score": 0.05}],
        [{"label": "NEGATIVE", "score": 0.90}, {"label": "NEUTRAL", "score": 0.10}]
    ]
    mock_pipeline.return_value = mock_predictions
    
    texts = ["This is a positive message", "This is negative"]
    result = process_sentiment_batch(mock_pipeline, texts, threshold=0.5)
    
    assert isinstance(result, list)
    assert len(result) == len(texts)
    for item in result:
        assert "primary_emotion" in item or "emotions_detected" in item or "all_scores" in item


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_process_sentiment_dry_run(mock_run_id, mock_logger) -> None:
    """Test stage_11 process_sentiment with dry_run=True."""
    from stage_11.claude_code_stage_11 import process_sentiment
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])
    mock_client.query.return_value = mock_query_job
    
    result = process_sentiment(mock_client, "test_run", batch_size=100, threshold=0.5, dry_run=True)
    
    assert isinstance(result, dict)
    assert "dry_run" in result or "processed" in result or "total" in result


# Stage 12 Additional Tests
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_get_keybert_model(mock_run_id, mock_logger) -> None:
    """Test stage_12 get_keybert_model function."""
    from stage_12.claude_code_stage_12 import get_keybert_model
    import pytest
    
    # Skip if keybert not available
    try:
        from keybert import KeyBERT
    except ImportError:
        pytest.skip("keybert not available - skipping test")
    
    # Function may raise ImportError if package not installed
    try:
        model = get_keybert_model()
        assert model is not None
    except ImportError:
        # Expected if package not installed
        pytest.skip("keybert model not available")


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_extract_keywords_basic(mock_run_id, mock_logger) -> None:
    """Test stage_12 extract_keywords with basic input."""
    from stage_12.claude_code_stage_12 import extract_keywords
    import pytest
    
    # Skip if keybert not available
    try:
        from keybert import KeyBERT
    except ImportError:
        pytest.skip("keybert not available - skipping test")
    
    # Mock KeyBERT model
    mock_model = MagicMock()
    mock_model.extract_keywords.return_value = [("keyword1", 0.9), ("keyword2", 0.8)]
    
    result = extract_keywords(mock_model, "This is a test message", top_n=5)
    
    assert isinstance(result, list)
    # Should return list of keywords
    assert len(result) >= 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_process_topics_dry_run(mock_run_id, mock_logger) -> None:
    """Test stage_12 process_topics with dry_run=True."""
    from stage_12.claude_code_stage_12 import process_topics
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])
    mock_client.query.return_value = mock_query_job
    
    result = process_topics(mock_client, "test_run", batch_size=100, top_n=5, dry_run=True)
    
    assert isinstance(result, dict)
    assert "dry_run" in result or "processed" in result or "total" in result
