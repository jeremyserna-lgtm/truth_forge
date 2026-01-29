"""Comprehensive tests for Stages 11, 12, 13 (Enrichment and Relationships).

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


# =============================================================================
# STAGE 12 - KEYWORD EXTRACTION
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_extract_keywords_empty_text(mock_run_id, mock_logger) -> None:
    """Test extract_keywords with empty text."""
    from stage_12.claude_code_stage_12 import extract_keywords
    
    try:
        import keybert
    except ImportError:
        pytest.skip("keybert not available")
    
    mock_model = Mock()
    mock_model.extract_keywords.return_value = []
    
    keywords = extract_keywords(mock_model, "", top_n=5)
    
    assert isinstance(keywords, list)
    assert len(keywords) == 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_12_extract_keywords_with_text(mock_run_id, mock_logger) -> None:
    """Test extract_keywords with text."""
    from stage_12.claude_code_stage_12 import extract_keywords
    
    try:
        import keybert
    except ImportError:
        pytest.skip("keybert not available")
    
    mock_model = Mock()
    mock_model.extract_keywords.return_value = [
        ("python", 0.9),
        ("function", 0.8),
        ("code", 0.7)
    ]
    
    keywords = extract_keywords(mock_model, "Write a Python function", top_n=5)
    
    assert isinstance(keywords, list)
    assert len(keywords) > 0
    assert all(isinstance(kw, tuple) and len(kw) == 2 for kw in keywords)


# =============================================================================
# STAGE 13 - RELATIONSHIPS
# =============================================================================

@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_generate_relationship_id_deterministic(mock_run_id, mock_logger) -> None:
    """Test generate_relationship_id produces deterministic IDs."""
    from stage_13.claude_code_stage_13 import generate_relationship_id
    
    id1 = generate_relationship_id("source_123", "target_456", "parent_child")
    id2 = generate_relationship_id("source_123", "target_456", "parent_child")
    
    assert id1 == id2
    assert isinstance(id1, str)
    assert len(id1) > 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_generate_relationship_id_different_inputs(mock_run_id, mock_logger) -> None:
    """Test generate_relationship_id produces different IDs for different inputs."""
    from stage_13.claude_code_stage_13 import generate_relationship_id
    
    id1 = generate_relationship_id("source_123", "target_456", "parent_child")
    id2 = generate_relationship_id("source_789", "target_456", "parent_child")
    
    assert id1 != id2


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_build_parent_child_relationships_empty(mock_run_id, mock_logger) -> None:
    """Test build_parent_child_relationships with empty input."""
    from stage_13.claude_code_stage_13 import build_parent_child_relationships
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_query_job.result.return_value = iter([])
    mock_client.query.return_value = mock_query_job
    
    created_at = datetime.now(timezone.utc).isoformat()
    relationships = list(build_parent_child_relationships(mock_client, "test_run", created_at))
    
    assert isinstance(relationships, list)
    assert len(relationships) == 0


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_13_build_parent_child_relationships_with_data(mock_run_id, mock_logger) -> None:
    """Test build_parent_child_relationships with actual data."""
    from stage_13.claude_code_stage_13 import build_parent_child_relationships
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.parent_id = "parent_123"
    mock_row.child_id = "child_456"
    mock_row.parent_level = 1
    mock_row.child_level = 2
    mock_row.session_id = "session_123"
    mock_row.content_date = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    
    created_at = datetime.now(timezone.utc).isoformat()
    relationships = list(build_parent_child_relationships(mock_client, "test_run", created_at))
    
    assert isinstance(relationships, list)
    assert all("relationship_id" in r for r in relationships)
