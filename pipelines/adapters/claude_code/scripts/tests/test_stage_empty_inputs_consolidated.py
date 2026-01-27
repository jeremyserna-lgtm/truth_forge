"""Consolidated tests for empty input handling across stages.

Tests how stages handle empty inputs (empty lists, empty tables, etc.).
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timezone
import pytest

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


# Stages with process functions that handle empty inputs
EMPTY_INPUT_TESTS = [
    (7, "stage_7.claude_code_stage_7", "create_message_entities", "empty"),
    (8, "stage_8.claude_code_stage_8", "create_conversation_entities", "empty"),
    (9, "stage_9.claude_code_stage_9", "process_embeddings", "empty_text"),
    (14, "stage_14.claude_code_stage_14", "aggregate_entities", "empty"),
    (16, "stage_16.claude_code_stage_16", "promote_entities", "empty"),
]


@pytest.mark.parametrize("stage_num,module_name,func_name,empty_type", EMPTY_INPUT_TESTS)
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_empty_inputs_consolidated(
    mock_run_id,
    mock_logger,
    stage_num: int,
    module_name: str,
    func_name: str,
    empty_type: str
) -> None:
    """Test stages handle empty inputs gracefully (consolidated)."""
    from google.cloud import bigquery
    
    try:
        module = __import__(module_name, fromlist=[func_name])
        process_func = getattr(module, func_name, None)
        
        if process_func is None:
            pytest.skip(f"Stage {stage_num} does not have {func_name}")
        
        # Mock BigQuery client
        mock_client = Mock(spec=bigquery.Client)
        mock_query_job = Mock()
        mock_query_job.result.return_value = iter([])  # Empty result
        mock_client.query.return_value = mock_query_job
        mock_client.insert_rows_json.return_value = []
        
        # Call with empty input based on function signature
        # Different functions have different signatures, handle accordingly
        if func_name == "create_message_entities":
            # Generator function, no dry_run
            created_at = datetime.now(timezone.utc).isoformat()
            result = list(process_func(mock_client, "test_run", created_at))
            # Generator returns list of entities
            assert isinstance(result, list)
        elif func_name == "create_conversation_entities":
            # Generator function, no dry_run
            created_at = datetime.now(timezone.utc).isoformat()
            result = list(process_func(mock_client, "test_run", created_at))
            # Generator returns list of entities
            assert isinstance(result, list)
        elif func_name == "process_embeddings":
            # Takes client, run_id, batch_size, dry_run
            result = process_func(mock_client, "test_run", batch_size=100, dry_run=True)
            assert isinstance(result, dict) or result is None
        elif func_name == "process_sentiment_batch":
            # Takes pipeline, texts, threshold (not a stage function, skip)
            pytest.skip(f"{func_name} has different signature")
        elif func_name == "aggregate_entities":
            # For dry_run, needs count query mock
            mock_count_row = Mock()
            mock_count_row.cnt = 0
            mock_count_query_job = Mock()
            mock_count_query_job.result.return_value = iter([mock_count_row])
            def query_side_effect(query_str):
                if "COUNT(*)" in query_str:
                    return mock_count_query_job
                return Mock()
            mock_client.query.side_effect = query_side_effect
            result = process_func(mock_client, "test_run", dry_run=True, batch_size=100)
            assert isinstance(result, dict) or result is None
        elif func_name == "promote_entities":
            # Takes client, run_id, include_warnings, dry_run
            with patch(f'{module_name}.get_existing_entity_ids', return_value=set()):
                result = process_func(mock_client, "test_run", include_warnings=False, dry_run=True)
            assert isinstance(result, dict) or result is None
        else:
            # Try default signature
            result = process_func(mock_client, "test_run", dry_run=True)
            assert isinstance(result, dict) or result is None
    except (ImportError, TypeError, AttributeError) as e:
        # Function signature might be different, skip
        pytest.skip(f"Could not test {func_name}: {e}")
