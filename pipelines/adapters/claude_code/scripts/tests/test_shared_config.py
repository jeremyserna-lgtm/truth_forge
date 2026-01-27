"""Tests for shared config module.

Target: 100% coverage of shared/config.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch, mock_open

# Add paths
project_root = Path(__file__).resolve().parents[4]
scripts_dir = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for path in [project_root, src_path, scripts_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from shared.config import get_config, get_stage_config


def test_get_config_defaults() -> None:
    """Test get_config returns defaults when no config file exists."""
    with patch("shared.config.CONFIG_FILE") as mock_file:
        mock_file.exists.return_value = False
        # Clear cache
        import shared.config
        shared.config._config_cache = None
        
        config = get_config()
        
        assert "pipeline" in config
        assert "bigquery" in config
        assert "embeddings" in config
        assert "stages" in config
        assert config["pipeline"]["name"] == "claude_code"


def test_get_config_cached() -> None:
    """Test get_config uses cache on second call."""
    import shared.config
    original_cache = shared.config._config_cache
    original_file = shared.config.CONFIG_FILE
    shared.config._config_cache = None
    
    try:
        # Use a non-existent file path
        fake_path = Path("/nonexistent/config/pipeline_config.toml")
        shared.config.CONFIG_FILE = fake_path
        
        config1 = get_config()
        config2 = get_config()
        
        # Should be same object (cached)
        assert config1 is config2
    finally:
        shared.config._config_cache = original_cache
        shared.config.CONFIG_FILE = original_file


def test_get_stage_config() -> None:
    """Test get_stage_config function."""
    import shared.config
    original_cache = shared.config._config_cache
    original_file = shared.config.CONFIG_FILE
    shared.config._config_cache = None
    
    try:
        # Use a non-existent file path
        fake_path = Path("/nonexistent/config/pipeline_config.toml")
        shared.config.CONFIG_FILE = fake_path
        
        stage_config = get_stage_config(0)
        
        assert isinstance(stage_config, dict)
        assert "name" in stage_config or "batch_size" in stage_config
    finally:
        shared.config._config_cache = original_cache
        shared.config.CONFIG_FILE = original_file


def test_get_stage_config_with_overrides() -> None:
    """Test get_stage_config with stage-specific overrides."""
    import shared.config
    import tempfile
    original_cache = shared.config._config_cache
    original_file = shared.config.CONFIG_FILE
    shared.config._config_cache = None
    
    config_data = {
        "pipeline": {"name": "claude_code", "batch_size": 1000},
        "stages": {
            "5": {"batch_size": 500}
        }
    }
    
    try:
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.toml', delete=False) as f:
            # Write minimal TOML (we'll mock the load anyway)
            f.write(b"[pipeline]\nname = 'claude_code'\n")
            temp_path = Path(f.name)
        
        shared.config.CONFIG_FILE = temp_path
        
        with patch("shared.config.tomllib.load", return_value=config_data):
            stage_5_config = get_stage_config(5)
            # Stage 5 should have batch_size override
            assert stage_5_config.get("batch_size") == 500
    finally:
        shared.config._config_cache = original_cache
        shared.config.CONFIG_FILE = original_file
        if 'temp_path' in locals():
            temp_path.unlink(missing_ok=True)


def test_get_config_with_file() -> None:
    """Test get_config when config file exists."""
    import shared.config
    import tempfile
    original_cache = shared.config._config_cache
    original_file = shared.config.CONFIG_FILE
    shared.config._config_cache = None
    
    config_data = {
        "pipeline": {"name": "test", "version": "1.0.0"},
        "bigquery": {"project": "test"},
        "embeddings": {"model": "test"},
        "stages": {}
    }
    
    try:
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.toml', delete=False) as f:
            f.write(b"[pipeline]\nname = 'test'\n")
            temp_path = Path(f.name)
        
        shared.config.CONFIG_FILE = temp_path
        
        with patch("shared.config.tomllib.load", return_value=config_data):
            config = get_config()
            assert config == config_data
    finally:
        shared.config._config_cache = original_cache
        shared.config.CONFIG_FILE = original_file
        if 'temp_path' in locals():
            temp_path.unlink(missing_ok=True)
