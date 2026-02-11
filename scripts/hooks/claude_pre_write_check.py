#!/usr/bin/env python3
"""Claude Code pre-write hook - blocks dangerous patterns.

This hook runs BEFORE Claude writes any file content.
It blocks patterns that have caused data corruption.

Receives tool input via stdin as JSON.
Exit 0 = allow, Exit 1 = block.
"""
from __future__ import annotations

import json
import re
import sys


FORBIDDEN_PATTERNS = [
    # Streaming inserts (caused 8.9M duplicates)
    (r"insert_rows_json", "BLOCKED: Use load_table_from_file instead of streaming insert"),
    (r"\.insert_rows\s*\(", "BLOCKED: Use load_table_from_file instead of streaming insert"),

    # Dangerous BigQuery operations
    (r"WRITE_TRUNCATE.*entity_unified", "BLOCKED: Cannot TRUNCATE production entity_unified"),
    (r"WRITE_TRUNCATE.*entity_enrichments", "BLOCKED: Cannot TRUNCATE production entity_enrichments"),
    (r"DROP\s+TABLE\s+.*spine\.", "BLOCKED: Cannot DROP production spine tables"),
    (r"DELETE\s+FROM\s+.*spine\.(?!_temp)", "BLOCKED: Cannot DELETE from production spine tables"),

    # Silent exceptions
    (r"except\s*:\s*pass\s*$", "BLOCKED: No silent exceptions - use logger + raise"),
    (r"except\s+Exception\s*:\s*pass", "BLOCKED: No silent exceptions - use logger + raise"),

    # Bypass flags
    (r"--skip-validation", "BLOCKED: No validation bypass flags allowed"),
    (r"--no-validate", "BLOCKED: No validation bypass flags allowed"),
    (r"SKIP_VALIDATION", "BLOCKED: No validation bypass env vars allowed"),
]

ALLOWED_CONTEXTS = [
    "# EXCEPTION:",  # Documented exception
    "mock",
    "Mock",
    "patch",
    "assert",
    "def test_",
    "class Test",
]


def check_content(content: str) -> list[str]:
    """Check content for forbidden patterns."""
    errors = []

    for line_num, line in enumerate(content.split("\n"), 1):
        # Skip allowed contexts
        if any(ctx in line for ctx in ALLOWED_CONTEXTS):
            continue

        for pattern, message in FORBIDDEN_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                errors.append(f"Line {line_num}: {message}")

    return errors


def main() -> int:
    """Check tool input for forbidden patterns."""
    # Read tool input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # Allow if we can't parse

    # Get content being written
    content = input_data.get("content", "") or input_data.get("new_string", "")
    if not content:
        return 0

    errors = check_content(content)
    if errors:
        print("=" * 60, file=sys.stderr)
        print("BLOCKED BY DATA PROTECTION HOOK", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Per DATA PROTECTION LAWS in CLAUDE.md", file=sys.stderr)
        print("These patterns have caused data corruption.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
