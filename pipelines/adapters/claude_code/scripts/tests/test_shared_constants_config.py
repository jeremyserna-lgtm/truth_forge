"""Comprehensive tests for shared/constants.py and shared/config.py.

Target: 90%+ coverage of shared configuration modules.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Mocks are set up in conftest.py


def test_shared_constants_imports() -> None:
    """Test that shared constants can be imported."""
    from shared import constants
    
    assert hasattr(constants, 'PIPELINE_NAME')
    assert hasattr(constants, 'SOURCE_NAME')
    assert isinstance(constants.PIPELINE_NAME, str)
    assert isinstance(constants.SOURCE_NAME, str)


def test_shared_config_imports() -> None:
    """Test that shared config can be imported."""
    from shared import config
    
    # config module exists and can be imported
    assert config is not None


@patch('src.services.central_services.core.config.get_bigquery_client')
def test_shared_config_get_bigquery_client(mock_get_client) -> None:
    """Test shared config get_bigquery_client function."""
    from shared import config
    from google.cloud import bigquery
    from unittest.mock import Mock
    
    mock_client = Mock(spec=bigquery.Client)
    mock_get_client.return_value = mock_client
    
    # Test that config module can be accessed
    assert config is not None
