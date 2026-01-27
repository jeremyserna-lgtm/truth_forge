"""Import transformation utilities for code migration.

RISK MITIGATION: Automates conversion of legacy imports and patterns:
- from Primitive.* → from truth_forge.*
- from src.services.* → from truth_forge.services.*
- from central_services.* → from truth_forge.services.*
- /Users/jeremyserna/Truth_Engine → PROJECT_ROOT
- Path.home() / "Truth_Engine" → PROJECT_ROOT
- os.environ["..."] → settings.field_name

Usage:
    from truth_forge.migration.transform import transform_file, transform_directory

    # Transform a single file
    result = transform_file(Path("old_service.py"))

    # Transform entire directory
    results = transform_directory(Path("src/services"))
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TransformResult:
    """Result of a file transformation."""

    file_path: Path
    original_content: str
    transformed_content: str
    changes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def was_modified(self) -> bool:
        """Check if file was actually modified."""
        return self.original_content != self.transformed_content

    @property
    def change_count(self) -> int:
        """Number of changes made."""
        return len(self.changes)


# =========================================================================
# Import Patterns
# =========================================================================

IMPORT_TRANSFORMATIONS: list[tuple[str, str, str]] = [
    # Pattern, Replacement, Description
    # Core imports
    (
        r"from\s+Primitive\.core\.([a-zA-Z_]+)\s+import",
        r"from truth_forge.core.\1 import",
        "Primitive.core → truth_forge.core",
    ),
    (
        r"from\s+Primitive\.services\.([a-zA-Z_]+)\s+import",
        r"from truth_forge.services.\1 import",
        "Primitive.services → truth_forge.services",
    ),
    (
        r"from\s+Primitive\.([a-zA-Z_]+)\s+import",
        r"from truth_forge.\1 import",
        "Primitive.* → truth_forge.*",
    ),
    # Old src.services pattern
    (
        r"from\s+src\.services\.central_services\.([a-zA-Z_]+)\s+import",
        r"from truth_forge.services.\1 import",
        "src.services.central_services → truth_forge.services",
    ),
    (
        r"from\s+src\.services\.([a-zA-Z_]+)\s+import",
        r"from truth_forge.services.\1 import",
        "src.services → truth_forge.services",
    ),
    # central_services direct import
    (
        r"from\s+central_services\.([a-zA-Z_]+)\s+import",
        r"from truth_forge.services.\1 import",
        "central_services → truth_forge.services",
    ),
    # architect_central_services (legacy)
    (
        r"from\s+architect_central_services\.([a-zA-Z_]+)\s+import",
        r"from truth_forge.services.\1 import",
        "architect_central_services → truth_forge.services",
    ),
    # Truth_Engine imports
    (
        r"from\s+Truth_Engine\.src\.services\.([a-zA-Z_]+)\s+import",
        r"from truth_forge.services.\1 import",
        "Truth_Engine.src.services → truth_forge.services",
    ),
    (
        r"from\s+Truth_Engine\.([a-zA-Z_]+)\s+import",
        r"from truth_forge.\1 import",
        "Truth_Engine.* → truth_forge.*",
    ),
]


# =========================================================================
# Path Patterns
# =========================================================================

PATH_TRANSFORMATIONS: list[tuple[str, str, str]] = [
    # Hardcoded absolute paths
    (
        r'["\']\/Users\/jeremyserna\/Truth_Engine["\']',
        "PROJECT_ROOT",
        "Hardcoded /Users/jeremyserna/Truth_Engine",
    ),
    (
        r'["\']\/Users\/jeremyserna\/truth_forge["\']',
        "PROJECT_ROOT",
        "Hardcoded /Users/jeremyserna/truth_forge",
    ),
    # Path.home() / "Truth_Engine" patterns
    (
        r'Path\.home\(\)\s*\/\s*["\']Truth_Engine["\']',
        "PROJECT_ROOT",
        "Path.home() / 'Truth_Engine'",
    ),
    (
        r'Path\.home\(\)\s*\/\s*["\']truth_forge["\']',
        "PROJECT_ROOT",
        "Path.home() / 'truth_forge'",
    ),
    # /tmp/ paths for HOLD files (should use proper HOLD paths)
    (
        r'["\']\/tmp\/hold1\.jsonl["\']',
        'get_intake_file("SERVICE_NAME")  # TODO: Set actual service name',
        "/tmp/hold1.jsonl hardcode",
    ),
    (
        r'["\']\/tmp\/hold2\.duckdb["\']',
        'get_duckdb_file("SERVICE_NAME")  # TODO: Set actual service name',
        "/tmp/hold2.duckdb hardcode",
    ),
]


# =========================================================================
# Environment Variable Patterns
# =========================================================================

ENV_TRANSFORMATIONS: list[tuple[str, str, str]] = [
    # os.environ["..."] → settings.field_name
    (
        r'os\.environ(?:\.get)?\(["\']GCP_PROJECT["\']\s*(?:,\s*["\'][^"\']*["\'])?\)',
        "settings.gcp_project",
        "GCP_PROJECT env var",
    ),
    (
        r'os\.environ(?:\.get)?\(["\']GOOGLE_API_KEY["\']\s*(?:,\s*["\'][^"\']*["\'])?\)',
        "settings.google_api_key",
        "GOOGLE_API_KEY env var",
    ),
    (
        r'os\.environ(?:\.get)?\(["\']GEMINI_API_KEY["\']\s*(?:,\s*["\'][^"\']*["\'])?\)',
        "settings.effective_gemini_key",
        "GEMINI_API_KEY env var",
    ),
    (
        r'os\.environ(?:\.get)?\(["\']ANTHROPIC_API_KEY["\']\s*(?:,\s*["\'][^"\']*["\'])?\)',
        "settings.anthropic_api_key",
        "ANTHROPIC_API_KEY env var",
    ),
    (
        r'os\.environ(?:\.get)?\(["\']BIGQUERY_LOCATION["\']\s*(?:,\s*["\'][^"\']*["\'])?\)',
        "settings.bigquery_location",
        "BIGQUERY_LOCATION env var",
    ),
    (
        r'os\.environ(?:\.get)?\(["\']GITHUB_TOKEN["\']\s*(?:,\s*["\'][^"\']*["\'])?\)',
        "settings.github_token",
        "GITHUB_TOKEN env var",
    ),
    (
        r'os\.environ(?:\.get)?\(["\']SERPAPI_KEY["\']\s*(?:,\s*["\'][^"\']*["\'])?\)',
        "settings.serpapi_key",
        "SERPAPI_KEY env var",
    ),
]


# =========================================================================
# Code Pattern Transformations
# =========================================================================

CODE_TRANSFORMATIONS: list[tuple[str, str, str]] = [
    # Thread-unsafe singleton patterns
    (
        r"_instance\s*=\s*None\n\s*@classmethod\n\s*def\s+get_instance",
        "# MIGRATION NOTE: Use ServiceFactory.get() instead of singleton pattern\n"
        "_instance = None\n    @classmethod\n    def get_instance",
        "Thread-unsafe singleton warning",
    ),
    # f-string logging to structured logging
    (
        r'logger\.info\(f["\']([^"\']*)\{([^}]+)\}([^"\']*)["\']',
        r'logger.info("\1%s\3", \2',
        "f-string logging → structured",
    ),
    (
        r'logger\.error\(f["\']([^"\']*)\{([^}]+)\}([^"\']*)["\']',
        r'logger.error("\1%s\3", \2',
        "f-string logging → structured",
    ),
    (
        r'logger\.warning\(f["\']([^"\']*)\{([^}]+)\}([^"\']*)["\']',
        r'logger.warning("\1%s\3", \2',
        "f-string logging → structured",
    ),
    (
        r'logger\.debug\(f["\']([^"\']*)\{([^}]+)\}([^"\']*)["\']',
        r'logger.debug("\1%s\3", \2',
        "f-string logging → structured",
    ),
    # Silent exception handling
    (
        r"except\s+Exception:\s*\n\s*pass",
        "except Exception as e:\n        logger.error('unexpected_error', error=str(e))  # MIGRATION: Add proper handling",
        "Silent exception → logged",
    ),
]


# =========================================================================
# Required Imports (to add when transformations are made)
# =========================================================================

REQUIRED_IMPORTS: dict[str, str] = {
    "PROJECT_ROOT": "from truth_forge.core.paths import PROJECT_ROOT",
    "get_intake_file": "from truth_forge.core.paths import get_intake_file",
    "get_duckdb_file": "from truth_forge.core.paths import get_duckdb_file",
    "settings": "from truth_forge.core.settings import settings",
    "ServiceFactory": "from truth_forge.services.factory import ServiceFactory",
}


# =========================================================================
# Transformation Functions
# =========================================================================


def apply_transformations(
    content: str,
    transformations: list[tuple[str, str, str]],
) -> tuple[str, list[str]]:
    """Apply a list of regex transformations to content.

    Args:
        content: Source code content.
        transformations: List of (pattern, replacement, description) tuples.

    Returns:
        Tuple of (transformed_content, list_of_changes).
    """
    changes: list[str] = []

    for pattern, replacement, description in transformations:
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            changes.append(f"{description}: {count} occurrence(s)")
            content = new_content

    return content, changes


def add_required_imports(content: str, changes: list[str]) -> str:
    """Add required imports based on transformations made.

    Args:
        content: Source code content.
        changes: List of change descriptions.

    Returns:
        Content with required imports added.
    """
    imports_to_add: list[str] = []

    for identifier, import_statement in REQUIRED_IMPORTS.items():
        # Check if identifier is now used but import is missing
        if identifier in content and import_statement not in content:
            imports_to_add.append(import_statement)

    if not imports_to_add:
        return content

    # Find the best place to insert imports
    # After existing imports, or at the top after docstring
    lines = content.split("\n")
    insert_index = 0

    # Skip docstring
    in_docstring = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if i == 0 and stripped.startswith('"""'):
            in_docstring = True
            if stripped.endswith('"""') and len(stripped) > 3:
                in_docstring = False
            continue
        if in_docstring:
            if stripped.endswith('"""'):
                in_docstring = False
            continue
        if stripped.startswith("from ") or stripped.startswith("import "):
            insert_index = i + 1
        elif stripped and not stripped.startswith("#"):
            break

    # Insert imports
    for import_stmt in sorted(set(imports_to_add)):
        lines.insert(insert_index, import_stmt)
        insert_index += 1

    return "\n".join(lines)


def transform_file(
    file_path: Path,
    dry_run: bool = False,
    include_code_patterns: bool = True,
) -> TransformResult:
    """Transform a single Python file.

    Args:
        file_path: Path to the Python file.
        dry_run: If True, don't write changes.
        include_code_patterns: Also apply code pattern transformations.

    Returns:
        TransformResult with details of changes.
    """
    result = TransformResult(
        file_path=file_path,
        original_content="",
        transformed_content="",
    )

    try:
        content = file_path.read_text()
        result.original_content = content
    except Exception as e:
        result.errors.append(f"Cannot read file: {e}")
        return result

    # Apply import transformations
    content, import_changes = apply_transformations(content, IMPORT_TRANSFORMATIONS)
    result.changes.extend(import_changes)

    # Apply path transformations
    content, path_changes = apply_transformations(content, PATH_TRANSFORMATIONS)
    result.changes.extend(path_changes)

    # Apply env var transformations
    content, env_changes = apply_transformations(content, ENV_TRANSFORMATIONS)
    result.changes.extend(env_changes)

    # Apply code pattern transformations
    if include_code_patterns:
        content, code_changes = apply_transformations(content, CODE_TRANSFORMATIONS)
        result.changes.extend(code_changes)

    # Add required imports
    if result.changes:
        content = add_required_imports(content, result.changes)

    result.transformed_content = content

    # Write if not dry run and changes were made
    if not dry_run and result.was_modified:
        try:
            file_path.write_text(content)
        except Exception as e:
            result.errors.append(f"Cannot write file: {e}")

    return result


def transform_directory(
    directory: Path,
    dry_run: bool = False,
    include_code_patterns: bool = True,
    exclude_patterns: list[str] | None = None,
) -> list[TransformResult]:
    """Transform all Python files in a directory.

    Args:
        directory: Root directory to transform.
        dry_run: If True, don't write changes.
        include_code_patterns: Also apply code pattern transformations.
        exclude_patterns: Glob patterns to exclude.

    Returns:
        List of TransformResults.
    """
    exclude_patterns = exclude_patterns or [
        "**/venv/**",
        "**/.venv/**",
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/.git/**",
    ]

    results: list[TransformResult] = []

    for py_file in directory.rglob("*.py"):
        # Check exclusions
        skip = False
        for pattern in exclude_patterns:
            if py_file.match(pattern):
                skip = True
                break

        if skip:
            continue

        result = transform_file(
            py_file,
            dry_run=dry_run,
            include_code_patterns=include_code_patterns,
        )
        results.append(result)

    return results


def generate_migration_report(results: list[TransformResult]) -> str:
    """Generate a markdown report of transformations.

    Args:
        results: List of TransformResults.

    Returns:
        Markdown report string.
    """
    modified = [r for r in results if r.was_modified]
    errors = [r for r in results if r.errors]

    report = [
        "# Migration Transformation Report",
        "",
        f"**Files scanned:** {len(results)}",
        f"**Files modified:** {len(modified)}",
        f"**Files with errors:** {len(errors)}",
        "",
    ]

    if modified:
        report.extend(["## Modified Files", ""])
        for r in modified:
            report.append(f"### {r.file_path}")
            report.append(f"Changes: {r.change_count}")
            for change in r.changes:
                report.append(f"- {change}")
            report.append("")

    if errors:
        report.extend(["## Errors", ""])
        for r in errors:
            report.append(f"### {r.file_path}")
            for error in r.errors:
                report.append(f"- {error}")
            report.append("")

    return "\n".join(report)
