#!/usr/bin/env python3
"""Pre-commit hook for truth_forge.

MOLT LINEAGE:
- Source: Truth_Engine/.git/hooks/pre-commit
- Version: 2.0.0
- Date: 2026-01-26

Installation:
    ln -sf ../../scripts/hooks/pre_commit.py .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit

Usage:
    python scripts/hooks/pre_commit.py
    python scripts/hooks/pre_commit.py --skip-tests
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent.parent


def get_staged_python_files() -> list[str]:
    """Get list of staged Python files.

    Returns:
        List of staged Python file paths.
    """
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    files = result.stdout.strip().split("\n")
    return [f for f in files if f.endswith(".py")]


def run_check(name: str, cmd: list[str]) -> bool:
    """Run a check command.

    Args:
        name: Name of the check.
        cmd: Command to run.

    Returns:
        True if check passed.
    """
    print(f"Running {name}...", end=" ", flush=True)
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True)
    if result.returncode == 0:
        print("✓")
        return True
    else:
        print("✗")
        print(result.stdout.decode())
        print(result.stderr.decode())
        return False


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Pre-commit hook for truth_forge",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests",
    )
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Check all files, not just staged ones",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Pre-commit Checks")
    print("=" * 60)

    # Get files to check
    if args.all_files:
        target = "src/"
    else:
        staged = get_staged_python_files()
        if not staged:
            print("No Python files staged for commit")
            return 0
        target = " ".join(staged)
        print(f"Checking {len(staged)} staged file(s)")

    print()
    all_passed = True
    pip = str(PROJECT_ROOT / ".venv" / "bin")

    # Run ruff format check
    if not run_check("ruff format", [f"{pip}/ruff", "format", "--check", target]):
        all_passed = False

    # Run ruff lint
    if not run_check("ruff check", [f"{pip}/ruff", "check", target]):
        all_passed = False

    # Run mypy
    if not run_check("mypy", [f"{pip}/mypy", target, "--strict"]):
        all_passed = False

    # Run tests (optional)
    if not args.skip_tests:
        if not run_check("pytest", [f"{pip}/pytest", "tests/", "-q"]):
            all_passed = False

    print()
    print("=" * 60)
    if all_passed:
        print("✓ All checks passed")
        return 0
    else:
        print("✗ Commit blocked - fix issues above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
