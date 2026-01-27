"""Centralized path resolution for truth_forge.

RISK MITIGATION: Replaces all hardcoded paths like:
- /Users/jeremyserna/Truth_Engine
- /tmp/hold1.jsonl
- Path.home() / "Truth_Engine"

All code should use these constants/functions instead.

Usage:
    from truth_forge.core.paths import PROJECT_ROOT, get_service_root

    # Get project root (works on any machine)
    root = PROJECT_ROOT

    # Get service-specific paths
    service_root = get_service_root("knowledge")
    hold1 = get_hold1_path("knowledge")
    hold2 = get_hold2_path("knowledge")
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


class PathResolutionError(Exception):
    """Raised when project root cannot be determined."""

    pass


@lru_cache(maxsize=1)
def get_project_root() -> Path:
    """Determine project root directory.

    Resolution order:
    1. TRUTH_FORGE_ROOT environment variable
    2. Walk up from this file looking for pyproject.toml
    3. Current working directory (fallback)

    Returns:
        Path to project root.

    Raises:
        PathResolutionError: If root cannot be determined.
    """
    # 1. Environment variable (highest priority)
    if env_root := os.getenv("TRUTH_FORGE_ROOT"):
        root = Path(env_root).resolve()
        if root.exists():
            return root

    # 2. Walk up from this file looking for pyproject.toml
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent

    # 3. Try current working directory
    cwd = Path.cwd()
    if (cwd / "pyproject.toml").exists():
        return cwd

    # 4. Fallback: assume we're in src/truth_forge/core/
    #    so root is 4 levels up
    fallback = Path(__file__).resolve().parents[3]
    if (fallback / "pyproject.toml").exists():
        return fallback

    raise PathResolutionError(
        "Cannot determine project root. "
        "Set TRUTH_FORGE_ROOT environment variable or run from project directory."
    )


# Core paths - resolved at import time
PROJECT_ROOT = get_project_root()
DATA_ROOT = PROJECT_ROOT / "data"
SERVICES_ROOT = DATA_ROOT / "services"
FRAMEWORK_ROOT = PROJECT_ROOT / "framework"
CONFIG_ROOT = PROJECT_ROOT / "config"
TESTS_ROOT = PROJECT_ROOT / "tests"


def get_service_root(service_name: str) -> Path:
    """Get root directory for a service.

    Args:
        service_name: Name of the service (e.g., "knowledge", "identity").

    Returns:
        Path to service directory: data/services/{service_name}/
    """
    return SERVICES_ROOT / service_name


def get_hold1_path(service_name: str, filename: str | None = None) -> Path:
    """Get HOLD₁ (intake) path for a service.

    Args:
        service_name: Name of the service.
        filename: Optional specific filename. Defaults to {service}_intake.jsonl.

    Returns:
        Path to hold1 directory or specific file.

    Example:
        >>> get_hold1_path("knowledge")
        Path('data/services/knowledge/hold1')
        >>> get_hold1_path("knowledge", "knowledge_intake.jsonl")
        Path('data/services/knowledge/hold1/knowledge_intake.jsonl')
    """
    hold1 = get_service_root(service_name) / "hold1"
    if filename:
        return hold1 / filename
    return hold1


def get_hold2_path(service_name: str, filename: str | None = None) -> Path:
    """Get HOLD₂ (processed) path for a service.

    Args:
        service_name: Name of the service.
        filename: Optional specific filename. Defaults to {service}.duckdb.

    Returns:
        Path to hold2 directory or specific file.

    Example:
        >>> get_hold2_path("knowledge")
        Path('data/services/knowledge/hold2')
        >>> get_hold2_path("knowledge", "knowledge.duckdb")
        Path('data/services/knowledge/hold2/knowledge.duckdb')
    """
    hold2 = get_service_root(service_name) / "hold2"
    if filename:
        return hold2 / filename
    return hold2


def get_staging_path(service_name: str, filename: str | None = None) -> Path:
    """Get staging path for a service.

    Args:
        service_name: Name of the service.
        filename: Optional specific filename.

    Returns:
        Path to staging directory or specific file.
    """
    staging = get_service_root(service_name) / "staging"
    if filename:
        return staging / filename
    return staging


def get_intake_file(service_name: str) -> Path:
    """Get the standard intake JSONL file path.

    Args:
        service_name: Name of the service.

    Returns:
        Path to {service}_intake.jsonl in hold1/.
    """
    return get_hold1_path(service_name, f"{service_name}_intake.jsonl")


def get_duckdb_file(service_name: str) -> Path:
    """Get the standard DuckDB file path.

    Args:
        service_name: Name of the service.

    Returns:
        Path to {service}.duckdb in hold2/.
    """
    return get_hold2_path(service_name, f"{service_name}.duckdb")


def ensure_service_directories(service_name: str) -> dict[str, Path]:
    """Create standard HOLD directories for a service.

    Creates:
    - data/services/{service}/hold1/
    - data/services/{service}/hold2/
    - data/services/{service}/staging/

    Args:
        service_name: Name of the service.

    Returns:
        Dictionary with paths to created directories.
    """
    paths = {
        "root": get_service_root(service_name),
        "hold1": get_hold1_path(service_name),
        "hold2": get_hold2_path(service_name),
        "staging": get_staging_path(service_name),
    }

    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)

    return paths


# Compatibility aliases for migration
# These will be removed after migration is complete
def get_legacy_root() -> Path:
    """Get legacy Truth_Engine root (for migration only)."""
    return PROJECT_ROOT / "Truth_Engine"


def get_legacy_services_root() -> Path:
    """Get legacy services root (for migration only)."""
    return get_legacy_root() / "src" / "services" / "central_services"
