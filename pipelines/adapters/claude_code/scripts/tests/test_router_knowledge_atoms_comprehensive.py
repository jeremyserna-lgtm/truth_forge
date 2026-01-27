"""Comprehensive tests for router_knowledge_atoms.py.

Target: 90%+ coverage of router_knowledge_atoms.py (currently ~52%).
"""
from __future__ import annotations

import sys
import json
import tempfile
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


def test_process_stage_atoms_no_atoms() -> None:
    """Test process_stage_atoms when no atoms exist."""
    import sys
    if 'router_knowledge_atoms' in sys.modules:
        del sys.modules['router_knowledge_atoms']
    
    with patch('router_knowledge_atoms.get_pipeline_hold2_path', return_value=Path("/nonexistent/hold2.jsonl")):
        with patch('router_knowledge_atoms.read_pipeline_hold2', return_value=[]):
            from router_knowledge_atoms import process_stage_atoms
            
            result = process_stage_atoms(stage=0)
            
            assert isinstance(result, dict)
            assert "read" in result
            assert "processed" in result
            assert "errors" in result
            assert result["read"] == 0


def test_process_stage_atoms_with_atoms() -> None:
    """Test process_stage_atoms when atoms exist."""
    import sys
    if 'router_knowledge_atoms' in sys.modules:
        del sys.modules['router_knowledge_atoms']
    
    mock_atoms = [
        {"status": "pending", "content": "Test 1", "hash": "hash1"},
        {"status": "pending", "content": "Test 2", "hash": "hash2"}
    ]
    
    with patch('router_knowledge_atoms.get_pipeline_hold2_path', return_value=Path("/nonexistent/hold2.jsonl")):
        with patch('router_knowledge_atoms.read_pipeline_hold2', return_value=mock_atoms):
            with patch('router_knowledge_atoms.get_knowledge_service') as mock_ks:
                mock_service = Mock()
                mock_service.retrieve.return_value = {"status": "success"}
                mock_ks.return_value = mock_service
                
                from router_knowledge_atoms import process_stage_atoms
                
                result = process_stage_atoms(stage=0)
                
                assert isinstance(result, dict)
                assert result["read"] == 2


def test_process_all_stages() -> None:
    """Test process_all_stages function."""
    import sys
    if 'router_knowledge_atoms' in sys.modules:
        del sys.modules['router_knowledge_atoms']
    
    with patch('router_knowledge_atoms.get_pipeline_hold2_path', return_value=Path("/nonexistent/hold2.jsonl")):
        with patch('router_knowledge_atoms.process_stage_atoms') as mock_process:
            mock_process.return_value = {"read": 0, "processed": 0, "errors": 0}
            
            from router_knowledge_atoms import process_all_stages
            
            result = process_all_stages()
            
            assert isinstance(result, dict)
            assert "total_read" in result
            assert "total_processed" in result
            assert "total_errors" in result
            assert "by_stage" in result
            # Should process all 17 stages
            assert len(result["by_stage"]) == 17
