"""Claude Code Pipeline - Configuration Loader

Loads pipeline configuration from TOML file with stage-specific overrides.

🧠 STAGE FIVE GROUNDING
This module exists to load and provide pipeline configuration.

Structure: Load TOML → Parse → Cache → Serve
Purpose: Centralized configuration management
Boundaries: Config loading only, no validation logic
Control: Singleton pattern for config caching

⚠️ WHAT THIS MODULE CANNOT SEE
- Runtime changes to config file
- Stage execution context
- External service state

🔥 THE FURNACE PRINCIPLE
- Truth (input): pipeline_config.toml file
- Heat (processing): TOML parsing, defaults merging
- Meaning (output): Typed configuration dict
- Care (delivery): Cached config for efficient access
"""
from __future__ import annotations

"""Claude Code Pipeline - Configuration Loader

Loads pipeline configuration from TOML file with stage-specific overrides.

🧠 STAGE FIVE GROUNDING
This module exists to load and provide pipeline configuration.

Structure: Load TOML → Parse → Cache → Serve
Purpose: Centralized configuration management
Boundaries: Config loading only, no validation logic
Control: Singleton pattern for config caching

⚠️ WHAT THIS MODULE CANNOT SEE
- Runtime changes to config file
- Stage execution context
- External service state

🔥 THE FURNACE PRINCIPLE
- Truth (input): pipeline_config.toml file
- Heat (processing): TOML parsing, defaults merging
- Meaning (output): Typed configuration dict
- Care (delivery): Cached config for efficient access
"""
# Use logging bridge or fallback
try:
    from .logging_bridge import get_logger as _get_logger
except Exception:
    try:
        from truth_forge.core.structured_logging import get_logger as _get_logger
    except Exception:
        import logging
        logging.basicConfig(level=logging.INFO)
        def _get_logger(name: str):
            return logging.getLogger(name)

_LOGGER = _get_logger(__name__)
script_id = "pipelines.claude_code.scripts.shared.config.py"

from pathlib import Path
from typing import Any, Dict, Optional

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older Python

# Config file location
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
CONFIG_FILE = CONFIG_DIR / "pipeline_config.toml"

# Cached config
_config_cache: Optional[Dict[str, Any]] = None

def get_config() -> Dict[str, Any]:
    """Load and cache pipeline configuration.

    Returns:
        Full configuration dictionary

    Note:
        Configuration is cached on first load. Restart to reload.
    """
    global _config_cache

    if _config_cache is not None:
        return _config_cache

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "rb") as f:
            _config_cache = tomllib.load(f)
    else:
        # Return defaults if no config file
        _config_cache = _get_defaults()

    return _config_cache

def get_stage_config(stage: int) -> Dict[str, Any]:
    """Get configuration for a specific stage.

    Args:
        stage: Stage number (0-16)

    Returns:
        Stage-specific configuration merged with defaults
    """
    config = get_config()
    stages_config = config.get("stages", {})

    # Get stage-specific config, falling back to defaults
    stage_config = stages_config.get(str(stage), {})

    # Merge with pipeline defaults
    defaults = config.get("pipeline", {})

    return {**defaults, **stage_config}

def _get_defaults() -> Dict[str, Any]:
    """Return default configuration."""
    return {
        "pipeline": {
            "name": "claude_code",
            "version": "2.0.0",
            "source_type": "jsonl",
            "cost_limit_per_stage_usd": 5.0,
            "cost_limit_total_usd": 80.0,
            "batch_size": 1000,
            "parallel_workers": 4,
            "timeout_minutes": 60,
        },
        "bigquery": {
            "project": "flash-clover-464719-g1",
            "dataset": "spine",
            "partition_field": "content_date",
            "clustering_fields": ["source_name", "level", "content_date"],
        },
        "embeddings": {
            "model": "gemini-embedding-001",
            "dimensions": 3072,
        },
        "stages": {},
    }
