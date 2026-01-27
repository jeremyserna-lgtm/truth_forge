"""Consolidated tests for stage main() functions using parameterization.

This replaces multiple individual test functions with a single parameterized test,
reducing test count while maintaining coverage.

CONSOLIDATED: Replaces 5 separate test functions with 1 parameterized test.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
import tempfile

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


@pytest.mark.parametrize("stage,module_name,process_func", [
    (0, "stage_0.claude_code_stage_0", "generate_assessment_report"),
    (1, "stage_1.claude_code_stage_1", "parse_session_file"),
    (2, "stage_2.claude_code_stage_2", "process_cleaning"),
    (3, "stage_3.claude_code_stage_3", "process_identity_generation"),
    (4, "stage_4.claude_code_stage_4", "process_staging"),
])
@patch('src.services.central_services.core.get_logger')
@patch('src.services.central_services.core.get_current_run_id')
def test_stage_main_functions_dry_run(
    mock_run_id,
    mock_logger,
    stage: int,
    module_name: str,
    process_func: str
) -> None:
    """Test stage main() functions with --dry-run (consolidated parameterized test)."""
    # Import the module dynamically
    module = __import__(module_name, fromlist=['main'])
    main_func = module.main
    
    # Mock PipelineTracker
    with patch(f'{module_name}.PipelineTracker') as mock_tracker:
        mock_tracker.return_value.__enter__.return_value = Mock()
        mock_tracker.return_value.__exit__.return_value = None
        
        # Mock stage-specific processing function
        with patch(f'{module_name}.{process_func}') as mock_process:
            # Set up mock return values based on stage
            if stage == 0:
                mock_process.return_value = {
                    "summary": {"files_sampled": 0, "go_no_go": "GO"},
                    "recommendations": []
                }
                # Also mock discover_session_files
                with patch(f'{module_name}.discover_session_files', return_value=[]):
                    with patch(f'{module_name}.save_report'):
                        with tempfile.TemporaryDirectory() as tmpdir:
                            source_dir = Path(tmpdir)
                            with patch('sys.argv', [f'claude_code_stage_{stage}.py', '--source-dir', str(source_dir)]):
                                try:
                                    result = main_func()
                                    assert isinstance(result, int)
                                    assert result in [0, 1]
                                except SystemExit:
                                    pass
            elif stage == 1:
                mock_process.return_value = iter([])
                with patch(f'{module_name}.discover_session_files', return_value=[]):
                    with patch(f'{module_name}.get_bigquery_client') as mock_client:
                        mock_bq_client = Mock()
                        mock_client.return_value.client = mock_bq_client
                        mock_bq_client.query.return_value.result.return_value = iter([])
                        with tempfile.TemporaryDirectory() as tmpdir:
                            source_dir = Path(tmpdir)
                            with patch('sys.argv', [f'claude_code_stage_{stage}.py', '--source-dir', str(source_dir), '--dry-run']):
                                try:
                                    result = main_func()
                                    assert isinstance(result, int)
                                except SystemExit:
                                    pass
            else:
                # Stages 2-4
                mock_process.return_value = {"processed": 0, "dry_run": True}
                with patch(f'{module_name}.get_bigquery_client') as mock_client:
                    mock_bq_client = Mock()
                    mock_client.return_value.client = mock_bq_client
                    mock_bq_client.query.return_value.result.return_value = iter([])
                    with patch('sys.argv', [f'claude_code_stage_{stage}.py', '--dry-run']):
                        try:
                            result = main_func()
                            assert isinstance(result, int)
                        except SystemExit:
                            pass
