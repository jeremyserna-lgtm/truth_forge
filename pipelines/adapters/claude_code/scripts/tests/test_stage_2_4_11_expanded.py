"""Expanded tests for Stages 2, 4, 11.

Target: Increase coverage for these stages.
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
def test_stage_2_process_cleaning(mock_run_id, mock_logger) -> None:
    """Test stage_2 process_cleaning function."""
    from stage_2.claude_code_stage_2 import process_cleaning
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.cnt = 100
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    result = process_cleaning(mock_client, "test_run", batch_size=100, dry_run=True)
    
    assert isinstance(result, dict)
    assert "processed" in result or "total" in result or "count" in result or "dry_run" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_4_create_stage_4_table(mock_run_id, mock_logger) -> None:
    """Test stage_4 create_stage_4_table function."""
    from stage_4.claude_code_stage_4 import create_stage_4_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_4_table(mock_client)
    
    assert result is not None


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_get_sentiment_pipeline(mock_run_id, mock_logger) -> None:
    """Test stage_11 get_sentiment_pipeline function."""
    from stage_11.claude_code_stage_11 import get_sentiment_pipeline
    import pytest
    
    # Skip if transformers not available - this is a dependency issue
    try:
        import transformers
    except ImportError:
        pytest.skip("transformers not available - skipping test")
    
    # get_sentiment_pipeline returns a pipeline/model
    pipeline = get_sentiment_pipeline()
    
    assert pipeline is not None


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_11_process_sentiment_batch(mock_run_id, mock_logger) -> None:
    """Test stage_11 process_sentiment_batch function."""
    from stage_11.claude_code_stage_11 import process_sentiment_batch
    from unittest.mock import Mock
    
    # Mock the sentiment pipeline
    mock_pipeline = Mock()
    # The pipeline returns a list of predictions per text
    mock_pipeline.return_value = [
        [{"label": "POSITIVE", "score": 0.9}, {"label": "NEGATIVE", "score": 0.1}],
        [{"label": "NEGATIVE", "score": 0.8}, {"label": "POSITIVE", "score": 0.2}]
    ]
    
    texts = ["This is great!", "This is terrible."]
    
    # process_sentiment_batch requires threshold parameter
    results = process_sentiment_batch(mock_pipeline, texts, threshold=0.5)
    
    assert isinstance(results, list)
    assert len(results) == len(texts)
    assert all("primary_emotion" in r for r in results)
