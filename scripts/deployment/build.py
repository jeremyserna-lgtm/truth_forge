#!/usr/bin/env python3
"""Build script for truth_forge deployment.

MOLT LINEAGE:
- Source: Truth_Engine/scripts/deployment/build.sh
- Version: 2.0.0
- Date: 2026-01-26

Usage:
    python scripts/deployment/build.py
    python scripts/deployment/build.py --clean
    python scripts/deployment/build.py --target docker
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).parent.parent.parent


def clean_build_artifacts() -> None:
    """Clean build artifacts."""
    dirs_to_clean: list[Path] = [
        PROJECT_ROOT / "dist",
        PROJECT_ROOT / "build",
        PROJECT_ROOT / ".eggs",
    ]

    # Clean egg-info directories
    dirs_to_clean.extend(PROJECT_ROOT.glob("**/*.egg-info"))

    # Clean pycache
    dirs_to_clean.extend(PROJECT_ROOT.glob("**/__pycache__"))

    for d in dirs_to_clean:
        if d.exists():
            print(f"Removing {d.relative_to(PROJECT_ROOT)}")
            shutil.rmtree(d)


def build_wheel() -> bool:
    """Build Python wheel.

    Returns:
        True if successful.
    """
    print("Building wheel...")
    result = subprocess.run(
        [sys.executable, "-m", "build"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Build failed:")
        print(result.stderr)
        return False

    print("✓ Wheel built successfully")

    # List built artifacts
    dist_dir = PROJECT_ROOT / "dist"
    if dist_dir.exists():
        for f in dist_dir.iterdir():
            print(f"    {f.name}")

    return True


def build_docker() -> bool:
    """Build Docker image.

    Returns:
        True if successful.
    """
    print("Building Docker image...")

    dockerfile = PROJECT_ROOT / "Dockerfile"
    if not dockerfile.exists():
        print("✗ No Dockerfile found")
        return False

    result = subprocess.run(
        [
            "docker",
            "build",
            "-t",
            "truth_forge:latest",
            "-f",
            str(dockerfile),
            str(PROJECT_ROOT),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Docker build failed:")
        print(result.stderr)
        return False

    print("✓ Docker image built successfully")
    return True


def get_version() -> str:
    """Get current version from pyproject.toml.

    Returns:
        Version string.
    """
    pyproject = PROJECT_ROOT / "pyproject.toml"
    if not pyproject.exists():
        return "0.0.0"

    content = pyproject.read_text()
    for line in content.split("\n"):
        if line.startswith("version"):
            # Extract version from line like: version = "2.0.0"
            parts = line.split("=")
            if len(parts) == 2:
                return parts[1].strip().strip('"').strip("'")

    return "0.0.0"


def generate_build_info() -> dict[str, Any]:
    """Generate build info.

    Returns:
        Build information dictionary.
    """
    import datetime

    return {
        "version": get_version(),
        "build_time": datetime.datetime.now(datetime.UTC).isoformat(),
        "python_version": sys.version,
        "platform": sys.platform,
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build truth_forge for deployment",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts before building",
    )
    parser.add_argument(
        "--target",
        choices=["wheel", "docker", "all"],
        default="wheel",
        help="Build target (default: wheel)",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Only show build info",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("truth_forge Build")
    print("=" * 60)

    # Show build info
    info = generate_build_info()
    print(f"\nVersion: {info['version']}")
    print(f"Python: {info['python_version'].split()[0]}")
    print(f"Platform: {info['platform']}")

    if args.info:
        return 0

    # Clean if requested
    if args.clean:
        print("\n## Cleaning")
        clean_build_artifacts()

    success = True

    # Build wheel
    if args.target in ("wheel", "all"):
        print("\n## Building Wheel")
        if not build_wheel():
            success = False

    # Build Docker
    if args.target in ("docker", "all"):
        print("\n## Building Docker")
        if not build_docker():
            success = False

    print("\n" + "=" * 60)
    if success:
        print("✓ Build complete")
        return 0
    else:
        print("✗ Build failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
