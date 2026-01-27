#!/usr/bin/env python3
"""Install and setup truth_forge.

MOLT LINEAGE:
- Source: Truth_Engine/scripts/setup.sh
- Version: 2.0.0
- Date: 2026-01-26

Usage:
    python scripts/setup/install.py
    python scripts/setup/install.py --dev
    python scripts/setup/install.py --check
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent.parent


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a command and print output.

    Args:
        cmd: Command to run.
        check: Whether to raise on non-zero exit.

    Returns:
        Completed process result.
    """
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=PROJECT_ROOT, check=check, capture_output=False)


def check_prerequisites() -> bool:
    """Check that prerequisites are installed.

    Returns:
        True if all prerequisites are met.
    """
    all_ok = True

    # Check Python version (runtime check, keep even if project requires 3.11+)
    if sys.version_info < (3, 11):  # noqa: UP036
        print(f"✗ Python 3.11+ required (found {sys.version})")
        all_ok = False
    else:
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")

    # Check pyproject.toml
    if (PROJECT_ROOT / "pyproject.toml").exists():
        print("✓ pyproject.toml exists")
    else:
        print("✗ pyproject.toml missing")
        all_ok = False

    return all_ok


def setup_venv() -> bool:
    """Create and setup virtual environment.

    Returns:
        True if successful.
    """
    venv_path = PROJECT_ROOT / ".venv"

    if venv_path.exists():
        print("✓ Virtual environment exists")
        return True

    print("Creating virtual environment...")
    result = run_command([sys.executable, "-m", "venv", str(venv_path)], check=False)
    if result.returncode != 0:
        print("✗ Failed to create virtual environment")
        return False

    print("✓ Virtual environment created")
    return True


def install_dependencies(dev: bool = False) -> bool:
    """Install project dependencies.

    Args:
        dev: Whether to install dev dependencies.

    Returns:
        True if successful.
    """
    pip_path = PROJECT_ROOT / ".venv" / "bin" / "pip"

    # Upgrade pip
    run_command([str(pip_path), "install", "--upgrade", "pip"], check=False)

    # Install package
    if dev:
        print("Installing with dev dependencies...")
        cmd = [str(pip_path), "install", "-e", ".[dev]"]
    else:
        print("Installing package...")
        cmd = [str(pip_path), "install", "-e", "."]

    result = run_command(cmd, check=False)
    if result.returncode != 0:
        print("✗ Failed to install dependencies")
        return False

    print("✓ Dependencies installed")
    return True


def setup_directories() -> bool:
    """Create required directories.

    Returns:
        True if successful.
    """
    dirs = [
        PROJECT_ROOT / "data" / "local",
        PROJECT_ROOT / "data" / "staging",
        PROJECT_ROOT / "data" / "output",
        PROJECT_ROOT / "config" / "local" / "env",
        PROJECT_ROOT / "config" / "local" / "credentials",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"✓ {d.relative_to(PROJECT_ROOT)}")

    return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Install and setup truth_forge",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Install dev dependencies",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check prerequisites",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("truth_forge Setup")
    print("=" * 60)

    # Check prerequisites
    print("\n## Prerequisites")
    if not check_prerequisites():
        return 1

    if args.check:
        print("\n✓ Prerequisites check passed")
        return 0

    # Setup venv
    print("\n## Virtual Environment")
    if not setup_venv():
        return 1

    # Install dependencies
    print("\n## Dependencies")
    if not install_dependencies(dev=args.dev):
        return 1

    # Setup directories
    print("\n## Directories")
    if not setup_directories():
        return 1

    print("\n" + "=" * 60)
    print("✓ Setup complete!")
    print("=" * 60)
    print("\nActivate the virtual environment:")
    print("  source .venv/bin/activate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
