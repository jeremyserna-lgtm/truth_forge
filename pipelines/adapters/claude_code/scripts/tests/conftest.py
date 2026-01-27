"""Pytest configuration and fixtures for pipeline tests.

Sets up global mocks for missing dependencies.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Create mock src module structure
_mock_src = Mock()
_mock_services = Mock()
_mock_central_services = Mock()
_mock_core = Mock()
_mock_config = Mock()
_mock_pipeline_tracker = Mock()
_mock_governance = Mock()

# Set up mock functions
_mock_core.get_logger = Mock(return_value=Mock())
_mock_core.get_current_run_id = Mock(return_value="test_run_123")
_mock_config.get_bigquery_client = Mock(return_value=Mock())
_mock_pipeline_tracker.PipelineTracker = Mock()
_mock_governance.require_diagnostic_on_error = Mock(side_effect=lambda e, msg: None)

# Wire up the mock structure
_mock_central_services.core = _mock_core
_mock_central_services.core.config = _mock_config
_mock_central_services.core.pipeline_tracker = _mock_pipeline_tracker
_mock_governance_module = Mock()
_mock_governance_module.require_diagnostic_on_error = Mock(side_effect=lambda e, msg: None)
_mock_central_services.governance = _mock_governance_module
_mock_central_services.governance.governance = _mock_governance
_mock_services.central_services = _mock_central_services
_mock_src.services = _mock_services

# Install mocks in sys.modules
sys.modules['src'] = _mock_src
sys.modules['src.services'] = _mock_services
sys.modules['src.services.central_services'] = _mock_central_services
sys.modules['src.services.central_services.core'] = _mock_core
sys.modules['src.services.central_services.core.config'] = _mock_config
sys.modules['src.services.central_services.core.pipeline_tracker'] = _mock_pipeline_tracker
sys.modules['src.services.central_services.governance'] = _mock_governance_module
sys.modules['src.services.central_services.governance.governance'] = _mock_governance

# Mock identity_service
_mock_identity_service = Mock()
_mock_identity_service.generate_message_id_from_guid = Mock(return_value="msg_123")
_mock_identity_service.register_id = Mock(return_value=True)
_mock_identity_service.sync_to_bigquery = Mock(return_value=True)
sys.modules['src.services.central_services.identity_service'] = Mock()
sys.modules['src.services.central_services.identity_service.service'] = _mock_identity_service

# Mock knowledge_service
_mock_knowledge_service = Mock()
_mock_knowledge_service.get_knowledge_service = Mock(return_value=Mock())
sys.modules['src.services.central_services.knowledge_service'] = Mock()
sys.modules['src.services.central_services.knowledge_service.knowledge_service'] = _mock_knowledge_service
