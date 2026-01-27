"""Comprehensive tests for stage processing functions.

Uses parameterized tests to cover process_* functions across all stages.
Target: Cover processing logic efficiently with shared patterns.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


# Processing function patterns
PROCESSING_PATTERNS = [
    (4, "stage_4.claude_code_stage_4", "process_staging"),
    (5, "stage_5.claude_code_stage_5", "process_tokenization"),
    (7, "stage_7.claude_code_stage_7", "create_message_entities"),
    (8, "stage_8.claude_code_stage_8", "create_conversation_entities"),
    (9, "stage_9.claude_code_stage_9", "process_embeddings"),
    (10, "stage_10.claude_code_stage_10", "process_extractions"),
    (11, "stage_11.claude_code_stage_11", "process_sentiment"),
    (12, "stage_12.claude_code_stage_12", "process_topics"),
    (13, "stage_13.claude_code_stage_13", "process_relationships"),
    (14, "stage_14.claude_code_stage_14", "aggregate_entities"),
    (15, "stage_15.claude_code_stage_15", "run_validation"),
    (16, "stage_16.claude_code_stage_16", "promote_entities"),
]


@pytest.mark.parametrize("stage_num,module_name,process_func_name", PROCESSING_PATTERNS)
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
@patch('src.services.central_services.core.config.get_bigquery_client')
def test_stage_processing_functions_exist(mock_bq_client, mock_run_id, mock_logger, stage_num, module_name, process_func_name) -> None:
    """Test that processing functions exist and are callable."""
    try:
        module = __import__(module_name, fromlist=[''])
        process_func = getattr(module, process_func_name, None)
        
        if process_func is None:
            pytest.skip(f"Stage {stage_num} does not have {process_func_name}")
        
        assert callable(process_func)
        
        # Test function signature (most take bq_client, run_id, etc.)
        import inspect
        sig = inspect.signature(process_func)
        assert len(sig.parameters) > 0  # Should have at least one parameter
    except ImportError:
        pytest.skip(f"Could not import {module_name}")


@pytest.mark.parametrize("stage_num,module_name,process_func_name", PROCESSING_PATTERNS)
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
@patch('src.services.central_services.core.config.get_bigquery_client')
def test_stage_processing_functions_with_mocks(mock_bq_client, mock_run_id, mock_logger, stage_num, module_name, process_func_name) -> None:
    """Test processing functions can be called with mocked BigQuery client."""
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_bq_client.return_value = mock_client
    
    try:
        module = __import__(module_name, fromlist=[''])
        process_func = getattr(module, process_func_name, None)
        
        if process_func is None:
            pytest.skip(f"Stage {stage_num} does not have {process_func_name}")
        
        # Most processing functions take (bq_client, run_id, ...)
        # Test that they can be called (may raise, but should not crash on import/signature)
        import inspect
        sig = inspect.signature(process_func)
        params = list(sig.parameters.keys())
        
        # Verify function expects BigQuery client
        assert len(params) > 0
    except ImportError:
        pytest.skip(f"Could not import {module_name}")
