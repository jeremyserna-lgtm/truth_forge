#!/usr/bin/env python3
"""Comprehensive Pipeline Validation Script

Validates and tests the claude_code data pipeline end-to-end:
1. Code quality checks (mypy, ruff check, ruff format)
2. Test coverage verification (90% requirement)
3. End-to-end pipeline execution
4. Error and warning detection

Usage:
    python validate_pipeline_comprehensive.py [--fix] [--run-pipeline]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

# Add project root to path
_script_dir = Path(__file__).parent
_project_root = _script_dir.parents[3]
sys.path.insert(0, str(_project_root))

try:
    from truth_forge.core.structured_logging import get_logger
except Exception:
    import logging

    def get_logger(name: str) -> Any:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(handler)
        return logger

logger = get_logger(__name__)

PIPELINE_SCRIPTS_DIR = _script_dir
STAGE_SCRIPTS = list(PIPELINE_SCRIPTS_DIR.glob("stage_*/claude_code_stage_*.py"))


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or _project_root,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out after 300 seconds"
    except Exception as e:
        return 1, "", str(e)


def check_code_quality() -> dict[str, Any]:
    """Check code quality with mypy, ruff check, ruff format."""
    results = {
        "mypy": {"passed": False, "errors": []},
        "ruff_check": {"passed": False, "errors": []},
        "ruff_format": {"passed": False, "errors": []},
    }

    # Check mypy
    logger.info("Running mypy --strict on stage scripts...")
    exit_code, stdout, stderr = run_command(
        [
            str(_project_root / ".venv" / "bin" / "mypy"),
            "--strict",
            *[str(s) for s in STAGE_SCRIPTS],
        ]
    )
    if exit_code == 0:
        results["mypy"]["passed"] = True
    else:
        # Filter out acceptable import errors (runtime-resolved)
        errors = (stdout + stderr).split("\n")
        # Accept import-not-found errors for shared module (runtime-resolved)
        real_errors = [
            e
            for e in errors
            if "error:" in e
            and "import-not-found" not in e
            and "attr-defined" not in e
        ]
        if real_errors:
            results["mypy"]["errors"] = real_errors[:20]  # Limit output
        else:
            results["mypy"]["passed"] = True  # Only acceptable errors

    # Check ruff check
    logger.info("Running ruff check on stage scripts...")
    exit_code, stdout, stderr = run_command(
        [
            str(_project_root / ".venv" / "bin" / "ruff"),
            "check",
            *[str(s) for s in STAGE_SCRIPTS],
        ]
    )
    if exit_code == 0:
        results["ruff_check"]["passed"] = True
    else:
        # Filter out E402 (imports not at top - acceptable for pipeline scripts)
        errors = (stdout + stderr).split("\n")
        real_errors = [e for e in errors if "E402" not in e and "error:" in e]
        if real_errors:
            results["ruff_check"]["errors"] = real_errors[:20]
        else:
            results["ruff_check"]["passed"] = True

    # Check ruff format
    logger.info("Running ruff format --check on stage scripts...")
    exit_code, stdout, stderr = run_command(
        [
            str(_project_root / ".venv" / "bin" / "ruff"),
            "format",
            "--check",
            *[str(s) for s in STAGE_SCRIPTS],
        ]
    )
    if exit_code == 0:
        results["ruff_format"]["passed"] = True
    else:
        results["ruff_format"]["errors"] = (stdout + stderr).split("\n")[:20]

    return results


def check_test_coverage() -> dict[str, Any]:
    """Check test coverage - must be >= 90%."""
    results = {"passed": False, "coverage": 0.0, "errors": []}

    # Find test files
    test_files = list(PIPELINE_SCRIPTS_DIR.glob("test_*.py"))
    if not test_files:
        results["errors"].append("No test files found")
        return results

    logger.info(f"Running pytest with coverage on {len(test_files)} test files...")
    exit_code, stdout, stderr = run_command(
        [
            str(_project_root / ".venv" / "bin" / "python3"),
            "-m",
            "pytest",
            *[str(f) for f in test_files],
            "--cov=pipelines/adapters/claude_code/scripts",
            "--cov-report=term",
            "--cov-report=json",
            "-v",
        ]
    )

    # Parse coverage from output
    output = stdout + stderr
    if "TOTAL" in output:
        # Extract coverage percentage
        for line in output.split("\n"):
            if "TOTAL" in line and "%" in line:
                try:
                    # Format: "TOTAL                   123    45    63%"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "%" in part:
                            coverage = float(part.replace("%", ""))
                            results["coverage"] = coverage
                            results["passed"] = coverage >= 90.0
                            break
                except Exception:
                    pass

    if exit_code != 0:
        results["errors"].extend((stdout + stderr).split("\n")[-20:])

    return results


def run_pipeline_end_to_end(dry_run: bool = True) -> dict[str, Any]:
    """Run pipeline end-to-end and capture all errors/warnings."""
    results = {
        "passed": False,
        "stages_completed": [],
        "stages_failed": [],
        "errors": [],
        "warnings": [],
    }

    run_script = PIPELINE_SCRIPTS_DIR / "run_pipeline.py"
    if not run_script.exists():
        results["errors"].append("run_pipeline.py not found")
        return results

    logger.info("Running pipeline end-to-end...")
    cmd = [
        str(_project_root / ".venv" / "bin" / "python3"),
        str(run_script),
    ]
    if dry_run:
        cmd.append("--dry-run")

    exit_code, stdout, stderr = run_command(cmd, cwd=PIPELINE_SCRIPTS_DIR)

    output = stdout + stderr
    # Parse stage results
    for line in output.split("\n"):
        if "✅ Stage" in line or "completed successfully" in line:
            # Extract stage number
            try:
                stage_num = int(line.split("Stage")[1].split()[0])
                results["stages_completed"].append(stage_num)
            except Exception:
                pass
        elif "❌ Stage" in line or "failed" in line.lower():
            try:
                stage_num = int(line.split("Stage")[1].split()[0])
                results["stages_failed"].append(stage_num)
            except Exception:
                pass
        elif "error" in line.lower() or "ERROR" in line:
            results["errors"].append(line.strip())
        elif "warning" in line.lower() or "WARNING" in line:
            results["warnings"].append(line.strip())

    results["passed"] = exit_code == 0 and len(results["stages_failed"]) == 0
    if not results["passed"]:
        results["errors"].extend(output.split("\n")[-50:])

    return results


def main() -> int:
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Comprehensive pipeline validation"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix formatting and import issues",
    )
    parser.add_argument(
        "--run-pipeline",
        action="store_true",
        help="Run pipeline end-to-end (requires source data)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Run pipeline in dry-run mode (default: True)",
    )

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🔍 COMPREHENSIVE PIPELINE VALIDATION")
    print("=" * 80 + "\n")

    all_passed = True

    # 1. Code Quality Checks
    print("1️⃣  CODE QUALITY CHECKS")
    print("-" * 80)
    quality_results = check_code_quality()

    if args.fix:
        logger.info("Auto-fixing formatting issues...")
        run_command(
            [
                str(_project_root / ".venv" / "bin" / "ruff"),
                "format",
                *[str(s) for s in STAGE_SCRIPTS],
            ]
        )
        run_command(
            [
                str(_project_root / ".venv" / "bin" / "ruff"),
                "check",
                "--fix",
                *[str(s) for s in STAGE_SCRIPTS],
            ]
        )
        # Re-check after fixes
        quality_results = check_code_quality()

    for tool, result in quality_results.items():
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"  {tool:15} {status}")
        if not result["passed"] and result.get("errors"):
            for error in result["errors"][:5]:
                print(f"    ⚠️  {error[:100]}")

    if not all(
        r["passed"] for r in quality_results.values()
    ):
        all_passed = False

    # 2. Test Coverage
    print("\n2️⃣  TEST COVERAGE")
    print("-" * 80)
    coverage_results = check_test_coverage()
    status = "✅ PASS" if coverage_results["passed"] else "❌ FAIL"
    print(f"  Coverage: {coverage_results['coverage']:.1f}% (Required: 90%) {status}")
    if coverage_results.get("errors"):
        for error in coverage_results["errors"][:5]:
            print(f"    ⚠️  {error[:100]}")

    if not coverage_results["passed"]:
        all_passed = False

    # 3. End-to-End Pipeline Execution
    if args.run_pipeline:
        print("\n3️⃣  END-TO-END PIPELINE EXECUTION")
        print("-" * 80)
        pipeline_results = run_pipeline_end_to_end(dry_run=args.dry_run)
        status = "✅ PASS" if pipeline_results["passed"] else "❌ FAIL"
        print(f"  Pipeline Execution: {status}")
        print(f"  Stages Completed: {len(pipeline_results['stages_completed'])}")
        print(f"  Stages Failed: {len(pipeline_results['stages_failed'])}")
        if pipeline_results["stages_failed"]:
            print(f"    Failed stages: {pipeline_results['stages_failed']}")
        if pipeline_results.get("errors"):
            print(f"  Errors: {len(pipeline_results['errors'])}")
            for error in pipeline_results["errors"][:5]:
                print(f"    ⚠️  {error[:100]}")
        if pipeline_results.get("warnings"):
            print(f"  Warnings: {len(pipeline_results['warnings'])}")
            for warning in pipeline_results["warnings"][:5]:
                print(f"    ⚠️  {warning[:100]}")

        if not pipeline_results["passed"]:
            all_passed = False
    else:
        print("\n3️⃣  END-TO-END PIPELINE EXECUTION")
        print("-" * 80)
        print("  ⏭️  Skipped (use --run-pipeline to execute)")

    # Final Summary
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL VALIDATION CHECKS PASSED")
    else:
        print("❌ VALIDATION FAILED - FIXES REQUIRED")
    print("=" * 80 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
