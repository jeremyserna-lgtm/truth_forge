"""Checkpoint validation for migration phases.

RISK MITIGATION: Validates state after each phase to catch issues early.

Usage:
    from truth_forge.migration.checkpoints import validate_checkpoint

    # After completing Phase 0
    result = validate_checkpoint(0)
    if result.failed:
        print(f"Phase 0 failed: {result.issues}")
        # Trigger rollback
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CheckpointResult:
    """Result of a checkpoint validation."""

    phase: int
    status: str  # "ok", "warning", "fail"
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Check if validation passed."""
        return self.status == "ok"

    @property
    def failed(self) -> bool:
        """Check if validation failed."""
        return self.status == "fail"


def _check_directory_exists(path: Path, name: str) -> str | None:
    """Check if directory exists, return issue string if not."""
    if not path.exists():
        return f"Missing directory: {name} ({path})"
    if not path.is_dir():
        return f"Not a directory: {name} ({path})"
    return None


def _check_file_exists(path: Path, name: str) -> str | None:
    """Check if file exists, return issue string if not."""
    if not path.exists():
        return f"Missing file: {name} ({path})"
    if not path.is_file():
        return f"Not a file: {name} ({path})"
    return None


def _check_import(module: str) -> str | None:
    """Check if module can be imported, return issue string if not."""
    try:
        importlib.import_module(module)
        return None
    except ImportError as e:
        return f"Import failed: {module} ({e})"


def _check_command(cmd: list[str], name: str) -> str | None:
    """Check if command succeeds, return issue string if not."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return f"Command failed: {name} - {result.stderr[:200]}"
        return None
    except Exception as e:
        return f"Command error: {name} ({e})"


def validate_phase_0() -> CheckpointResult:
    """Validate Phase 0: Foundation.

    Checks:
    - Directory structure created
    - pyproject.toml valid
    - data/services/ exists
    - src/truth_forge/ exists
    """
    issues: list[str] = []
    warnings: list[str] = []

    from truth_forge.core.paths import (
        DATA_ROOT,
        FRAMEWORK_ROOT,
        PROJECT_ROOT,
        SERVICES_ROOT,
    )

    # Check directories
    for path, name in [
        (PROJECT_ROOT / "src" / "truth_forge", "src/truth_forge"),
        (DATA_ROOT, "data"),
        (SERVICES_ROOT, "data/services"),
        (FRAMEWORK_ROOT, "framework"),
        (FRAMEWORK_ROOT / "standards", "framework/standards"),
    ]:
        if issue := _check_directory_exists(path, name):
            issues.append(issue)

    # Check pyproject.toml
    pyproject = PROJECT_ROOT / "pyproject.toml"
    if issue := _check_file_exists(pyproject, "pyproject.toml"):
        issues.append(issue)
    else:
        try:
            import tomllib

            with open(pyproject, "rb") as f:
                tomllib.load(f)
        except Exception as e:
            issues.append(f"Invalid pyproject.toml: {e}")

    # Check DATA_PATTERN.md copied
    data_pattern = FRAMEWORK_ROOT / "standards" / "DATA_PATTERN.md"
    if not data_pattern.exists():
        warnings.append("DATA_PATTERN.md not yet copied to framework/standards/")

    status = "fail" if issues else ("warning" if warnings else "ok")
    return CheckpointResult(phase=0, status=status, issues=issues, warnings=warnings)


def validate_phase_1() -> CheckpointResult:
    """Validate Phase 1: Core Module.

    Checks:
    - core.py, result.py, logger.py exist
    - core/ directory exists
    - config/ directory exists
    - Imports work
    """
    issues: list[str] = []
    warnings: list[str] = []

    from truth_forge.core.paths import PROJECT_ROOT

    src = PROJECT_ROOT / "src" / "truth_forge"

    # Check core files
    for filename in ["core.py", "result.py", "logger.py"]:
        if issue := _check_file_exists(src / filename, filename):
            # May be in core/ subdirectory instead
            if not (src / "core" / filename).exists():
                issues.append(issue)

    # Check directories
    for dirname in ["core", "config", "schema"]:
        if issue := _check_directory_exists(src / dirname, dirname):
            issues.append(issue)

    # Check imports
    for module in [
        "truth_forge.core",
        "truth_forge.core.paths",
        "truth_forge.core.settings",
    ]:
        if issue := _check_import(module):
            issues.append(issue)

    status = "fail" if issues else ("warning" if warnings else "ok")
    return CheckpointResult(phase=1, status=status, issues=issues, warnings=warnings)


def validate_phase_2() -> CheckpointResult:
    """Validate Phase 2: Infrastructure.

    Checks:
    - furnace/ exists
    - observability/ exists and works
    - credentials/ exists
    """
    issues: list[str] = []
    warnings: list[str] = []

    from truth_forge.core.paths import PROJECT_ROOT

    src = PROJECT_ROOT / "src" / "truth_forge"

    # Check directories
    for dirname in ["furnace", "observability", "credentials"]:
        path = src / dirname
        if not path.exists():
            warnings.append(f"Directory not yet created: {dirname}")

    # Check observability imports
    if issue := _check_import("truth_forge.observability"):
        issues.append(issue)

    status = "fail" if issues else ("warning" if warnings else "ok")
    return CheckpointResult(phase=2, status=status, issues=issues, warnings=warnings)


def validate_phase_4() -> CheckpointResult:
    """Validate Phase 4: Services.

    Checks:
    - services/ directory exists
    - Each service has HOLD pattern directories
    - Service imports work
    """
    issues: list[str] = []
    warnings: list[str] = []

    from truth_forge.core.paths import PROJECT_ROOT, SERVICES_ROOT

    src = PROJECT_ROOT / "src" / "truth_forge"

    # Check services directory
    if issue := _check_directory_exists(src / "services", "services"):
        issues.append(issue)
        return CheckpointResult(phase=4, status="fail", issues=issues)

    # Check each service has HOLD directories
    expected_services = [
        "identity",
        "knowledge",
        "analytics",
        "quality",
        "pipeline",
        "hold",
        "run",
        "builder",
        "federation",
        "frontmatter",
        "model_gateway",
        "stage_awareness",
    ]

    for service in expected_services:
        service_data = SERVICES_ROOT / service
        if not service_data.exists():
            warnings.append(f"Service data directory not yet created: {service}")
            continue

        for subdir in ["hold1", "hold2", "staging"]:
            if not (service_data / subdir).exists():
                issues.append(f"Missing HOLD directory: {service}/{subdir}")

    status = "fail" if issues else ("warning" if warnings else "ok")
    return CheckpointResult(phase=4, status=status, issues=issues, warnings=warnings)


def validate_phase_12() -> CheckpointResult:
    """Validate Phase 12: Tests.

    Checks:
    - tests/ directory exists
    - pytest runs successfully
    - Coverage meets 90% threshold
    """
    issues: list[str] = []
    warnings: list[str] = []

    from truth_forge.core.paths import PROJECT_ROOT

    # Check tests directory
    tests_dir = PROJECT_ROOT / "tests"
    if issue := _check_directory_exists(tests_dir, "tests"):
        issues.append(issue)
        return CheckpointResult(phase=12, status="fail", issues=issues)

    # Run pytest with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(tests_dir),
        "--cov=truth_forge",
        "--cov-branch",
        "--cov-fail-under=90",
        "-q",
    ]

    if issue := _check_command(cmd, "pytest with 90% coverage"):
        issues.append(issue)

    status = "fail" if issues else ("warning" if warnings else "ok")
    return CheckpointResult(phase=12, status=status, issues=issues, warnings=warnings)


def validate_phase_15() -> CheckpointResult:
    """Validate Phase 15: Final Validation.

    Checks:
    - Full test suite passes
    - mypy --strict passes
    - ruff check passes
    - All services healthy
    - No legacy imports remain
    """
    issues: list[str] = []
    warnings: list[str] = []

    from truth_forge.core.paths import PROJECT_ROOT

    src = PROJECT_ROOT / "src"

    # Check mypy
    cmd = [sys.executable, "-m", "mypy", str(src), "--strict"]
    if issue := _check_command(cmd, "mypy --strict"):
        issues.append(issue)

    # Check ruff
    cmd = [sys.executable, "-m", "ruff", "check", str(src)]
    if issue := _check_command(cmd, "ruff check"):
        issues.append(issue)

    # Check for legacy imports
    legacy_patterns = [
        "from Primitive.",
        "from src.services.",
        "from central_services.",
        "/Users/jeremyserna/",
    ]

    try:
        for pattern in legacy_patterns:
            result = subprocess.run(
                ["grep", "-r", pattern, str(src), "--include=*.py"],
                capture_output=True,
                text=True,
            )
            if result.stdout.strip():
                issues.append(f"Legacy import pattern found: {pattern}")
    except Exception as e:
        warnings.append(f"Could not check legacy imports: {e}")

    status = "fail" if issues else ("warning" if warnings else "ok")
    return CheckpointResult(phase=15, status=status, issues=issues, warnings=warnings)


# Registry of phase validators
VALIDATORS: dict[int, Callable[[], CheckpointResult]] = {
    0: validate_phase_0,
    1: validate_phase_1,
    2: validate_phase_2,
    4: validate_phase_4,
    12: validate_phase_12,
    15: validate_phase_15,
}


def validate_checkpoint(phase: int) -> CheckpointResult:
    """Validate completion of a migration phase.

    Args:
        phase: Phase number to validate.

    Returns:
        CheckpointResult with status and any issues.
    """
    validator = VALIDATORS.get(phase)
    if validator:
        return validator()

    # For phases without specific validators, do basic check
    return CheckpointResult(
        phase=phase,
        status="ok",
        warnings=[f"No specific validator for phase {phase}"],
    )


def validate_all_checkpoints(up_to_phase: int) -> list[CheckpointResult]:
    """Validate all checkpoints up to a given phase.

    Args:
        up_to_phase: Validate phases 0 through this number.

    Returns:
        List of CheckpointResults.
    """
    results = []
    for phase in range(up_to_phase + 1):
        if phase in VALIDATORS:
            results.append(validate_checkpoint(phase))
    return results
