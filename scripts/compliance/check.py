#!/usr/bin/env python3
"""Run compliance checks for truth_forge.

MOLT LINEAGE:
- Source: Truth_Engine/scripts/compliance/run_checks.sh
- Version: 2.0.0
- Date: 2026-01-26

Usage:
    python scripts/compliance/check.py
    python scripts/compliance/check.py --strict
    python scripts/compliance/check.py --fix
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


PROJECT_ROOT = Path(__file__).parent.parent.parent


class CheckResult(NamedTuple):
    """Result of a compliance check."""

    name: str
    passed: bool
    output: str
    fixed: bool = False


def run_mypy(strict: bool = True) -> CheckResult:
    """Run mypy type checking.

    Args:
        strict: Whether to use strict mode.

    Returns:
        Check result.
    """
    cmd = [str(PROJECT_ROOT / ".venv" / "bin" / "mypy"), "src/"]
    if strict:
        cmd.append("--strict")

    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    return CheckResult(
        name="mypy",
        passed=result.returncode == 0,
        output=result.stdout + result.stderr,
    )


def run_ruff_check(fix: bool = False) -> CheckResult:
    """Run ruff linter.

    Args:
        fix: Whether to auto-fix issues.

    Returns:
        Check result.
    """
    cmd = [str(PROJECT_ROOT / ".venv" / "bin" / "ruff"), "check", "src/"]
    if fix:
        cmd.append("--fix")

    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    return CheckResult(
        name="ruff check",
        passed=result.returncode == 0,
        output=result.stdout + result.stderr,
        fixed=fix and result.returncode == 0,
    )


def run_ruff_format(check_only: bool = True) -> CheckResult:
    """Run ruff formatter.

    Args:
        check_only: Whether to only check (not modify).

    Returns:
        Check result.
    """
    cmd = [str(PROJECT_ROOT / ".venv" / "bin" / "ruff"), "format", "src/"]
    if check_only:
        cmd.append("--check")

    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    return CheckResult(
        name="ruff format",
        passed=result.returncode == 0,
        output=result.stdout + result.stderr,
        fixed=not check_only and result.returncode == 0,
    )


def run_pytest(coverage: bool = True) -> CheckResult:
    """Run pytest.

    Args:
        coverage: Whether to include coverage.

    Returns:
        Check result.
    """
    cmd = [str(PROJECT_ROOT / ".venv" / "bin" / "pytest"), "tests/", "-v"]
    if coverage:
        cmd.extend(["--cov=src/truth_forge", "--cov-report=term-missing"])

    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    return CheckResult(
        name="pytest",
        passed=result.returncode == 0,
        output=result.stdout + result.stderr,
    )


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run compliance checks for truth_forge",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Use strict mode for mypy (default: True)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix issues where possible",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip pytest",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Compliance Check")
    print("=" * 60)

    results: list[CheckResult] = []

    # Run mypy
    print("\n## mypy --strict")
    mypy_result = run_mypy(strict=args.strict)
    results.append(mypy_result)
    status = "✓ PASS" if mypy_result.passed else "✗ FAIL"
    print(status)
    if args.verbose and not mypy_result.passed:
        print(mypy_result.output)

    # Run ruff check
    print("\n## ruff check")
    ruff_result = run_ruff_check(fix=args.fix)
    results.append(ruff_result)
    status = "✓ PASS" if ruff_result.passed else "✗ FAIL"
    if ruff_result.fixed:
        status += " (fixed)"
    print(status)
    if args.verbose and not ruff_result.passed:
        print(ruff_result.output)

    # Run ruff format
    print("\n## ruff format")
    format_result = run_ruff_format(check_only=not args.fix)
    results.append(format_result)
    status = "✓ PASS" if format_result.passed else "✗ FAIL"
    if format_result.fixed:
        status += " (fixed)"
    print(status)
    if args.verbose and not format_result.passed:
        print(format_result.output)

    # Run pytest
    if not args.skip_tests:
        print("\n## pytest")
        pytest_result = run_pytest()
        results.append(pytest_result)
        status = "✓ PASS" if pytest_result.passed else "✗ FAIL"
        print(status)
        if args.verbose and not pytest_result.passed:
            print(pytest_result.output)

    # Summary
    print("\n" + "=" * 60)
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    all_passed = all(r.passed for r in results)

    if all_passed:
        print(f"✓ ALL CHECKS PASSED ({passed}/{total})")
        return 0
    else:
        print(f"✗ CHECKS FAILED ({passed}/{total} passed)")
        for r in results:
            if not r.passed:
                print(f"  - {r.name}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
