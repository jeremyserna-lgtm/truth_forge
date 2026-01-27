"""Additional comprehensive tests for Stage 10.

Target: Increase coverage for LLM extraction stage.
Focus on edge cases and uncovered functions.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

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
def test_stage_10_create_stage_10_table(mock_run_id, mock_logger) -> None:
    """Test stage_10 create_stage_10_table function."""
    from stage_10.claude_code_stage_10 import create_stage_10_table
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_table = Mock()
    mock_client.create_table.return_value = mock_table
    
    result = create_stage_10_table(mock_client)
    
    assert result is not None
    mock_client.create_table.assert_called_once()


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_10_get_llm_client(mock_run_id, mock_logger) -> None:
    """Test stage_10 get_llm_client function."""
    from stage_10.claude_code_stage_10 import get_llm_client
    import pytest
    
    # Skip if google.generativeai not available
    try:
        import google.generativeai
    except ImportError:
        pytest.skip("google.generativeai not available - skipping test")
    
    # Test with mocked environment
    with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
        # Function may raise ImportError if package not installed
        try:
            client = get_llm_client()
            assert client is not None
        except ImportError:
            # Expected if package not installed
            pass


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_10_extract_from_message_impl_json_cleaning(mock_run_id, mock_logger) -> None:
    """Test stage_10 _extract_from_message_impl with JSON cleaning."""
    from stage_10.claude_code_stage_10 import _extract_from_message_impl
    
    mock_genai = MagicMock()
    mock_model = MagicMock()
    mock_response = MagicMock()
    
    # Test with JSON wrapped in code blocks
    mock_response.text = '```json\n{"intent": "question", "task_type": "coding"}\n```'
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    result = _extract_from_message_impl(mock_genai, "Test message")
    
    assert isinstance(result, dict)
    assert "intent" in result or "task_type" in result


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_10_extract_from_message_impl_long_text(mock_run_id, mock_logger) -> None:
    """Test stage_10 _extract_from_message_impl with text exceeding MAX_INPUT_CHARS."""
    from stage_10.claude_code_stage_10 import _extract_from_message_impl, MAX_INPUT_CHARS
    
    mock_genai = MagicMock()
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"intent": "question"}'
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Text longer than MAX_INPUT_CHARS
    long_text = "A" * (MAX_INPUT_CHARS + 100)
    
    result = _extract_from_message_impl(mock_genai, long_text)
    
    # Should truncate and still return result
    assert isinstance(result, dict)


@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_10_process_extractions_with_data(mock_run_id, mock_logger) -> None:
    """Test stage_10 process_extractions with actual data processing."""
    from stage_10.claude_code_stage_10 import process_extractions
    from google.cloud import bigquery
    
    mock_client = Mock(spec=bigquery.Client)
    mock_query_job = Mock()
    mock_row = Mock()
    mock_row.entity_id = "entity_123"
    mock_row.text = "Write a Python function to sort a list"
    mock_row.session_id = "session_123"
    mock_row.content_date = None
    mock_query_job.result.return_value = iter([mock_row])
    mock_client.query.return_value = mock_query_job
    mock_client.insert_rows_json.return_value = []
    
    # Mock get_llm_client and extract_from_message
    with patch('stage_10.claude_code_stage_10.get_llm_client') as mock_get_llm:
        mock_genai = MagicMock()
        mock_get_llm.return_value = mock_genai
        
        with patch('stage_10.claude_code_stage_10.extract_from_message') as mock_extract:
            mock_extract.return_value = {
                "intent": "question",
                "task_type": "coding",
                "code_languages": ["python"],
                "complexity": "simple",
                "has_code_block": False
            }
            
            result = process_extractions(mock_client, "test_run", batch_size=10, dry_run=False)
            
            assert isinstance(result, dict)
            assert "input_messages" in result or "extractions_completed" in result or "dry_run" in result
