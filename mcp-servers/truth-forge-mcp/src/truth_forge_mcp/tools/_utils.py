"""Utility functions for MCP tools.

Provides path setup and common utilities.
"""

from __future__ import annotations

import sys
from pathlib import Path


def setup_project_path() -> None:
    """Add project root to sys.path if not already present.

    This allows tools to import from truth_forge services.
    """
    project_root = Path(__file__).parent.parent.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
