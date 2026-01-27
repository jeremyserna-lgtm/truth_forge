"""Pipeline Adapters - Project-Specific Configurations.

MOLT LINEAGE:
- Source: Truth_Engine/pipelines/adapters/__init__.py
- Version: 2.0.0
- Date: 2026-01-26

Adapters provide project-specific pipeline configurations.
Each adapter directory contains:
- config.toml: Pipeline configuration
- Optional: Custom stage implementations

THE PATTERN:
- Adapter = Project-specific configuration
- Core = Universal pipeline engine
- Stages = Reusable transformations

Example adapter structure:
    adapters/
    └── my_project/
        ├── config.toml       # Pipeline configuration
        ├── stages/           # Custom stages (optional)
        │   └── custom.py
        └── README.md         # Documentation

Example config.toml:
    [pipeline]
    name = "my_project"
    version = "1.0.0"
    description = "My data pipeline"

    [stages.stage_0]
    name = "Extract"
    type = "extract"
    input = "data/staging/input.jsonl"
    output = "data/staging/extracted.jsonl"
"""

from __future__ import annotations

from pathlib import Path


def get_adapters_dir() -> Path:
    """Get the adapters directory.

    Returns:
        Path to adapters directory.
    """
    return Path(__file__).parent


def list_adapters() -> list[str]:
    """List available adapters.

    Returns:
        List of adapter names.
    """
    adapters_dir = get_adapters_dir()
    return [d.name for d in adapters_dir.iterdir() if d.is_dir() and not d.name.startswith("_")]


__all__ = [
    "get_adapters_dir",
    "list_adapters",
]
