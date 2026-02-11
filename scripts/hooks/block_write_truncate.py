#!/usr/bin/env python3
"""Block WRITE_TRUNCATE on production tables.

Per DATA PROTECTION LAWS:
- WRITE_TRUNCATE on production tables destroys data
- It should ONLY be used on temp/staging tables
- Always use WRITE_APPEND for production

FORBIDDEN:
- WriteDisposition.WRITE_TRUNCATE near production table patterns
- write_disposition="WRITE_TRUNCATE" near production tables

ALLOWED:
- WRITE_TRUNCATE on temp tables (_temp_, _staging_)
- WRITE_TRUNCATE in test code
- WRITE_TRUNCATE with explicit # EXCEPTION: comment
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PRODUCTION_TABLE_PATTERNS = [
    r"entity_unified",
    r"entity_enrichments",
    r"contacts_master",
    r"id_registry",
]

ALLOWED_CONTEXTS = [
    "_temp_",
    "_staging_",
    "_backup_",
    "# EXCEPTION:",
    "test",
    "Test",
    "mock",
    "Mock",
]


def check_file(filepath: str) -> list[str]:
    """Check file for dangerous WRITE_TRUNCATE patterns."""
    errors = []
    path = Path(filepath)

    # Skip test files
    if "test" in path.name.lower() or path.name.startswith("test_"):
        return []

    if not path.exists():
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    # Quick check - skip if no WRITE_TRUNCATE
    if "WRITE_TRUNCATE" not in content:
        return []

    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        if "WRITE_TRUNCATE" not in line:
            continue

        # Check context around this line
        context_start = max(0, line_num - 15)
        context_end = min(len(lines), line_num + 5)
        context = "\n".join(lines[context_start:context_end])

        # Allow if context contains safe patterns
        if any(ctx in context for ctx in ALLOWED_CONTEXTS):
            continue

        # Check for production tables in context
        for pattern in PRODUCTION_TABLE_PATTERNS:
            if re.search(pattern, context, re.IGNORECASE):
                errors.append(
                    f"{filepath}:{line_num}: FORBIDDEN: WRITE_TRUNCATE near production table\n"
                    f"  Table pattern: {pattern}\n"
                    f"  Use WRITE_APPEND instead, or use temp tables.\n"
                    f"  Line: {line.strip()[:80]}"
                )
                break

    return errors


def main() -> int:
    """Check all staged files."""
    files = sys.argv[1:]
    all_errors = []

    for f in files:
        if f.endswith(".py"):
            errors = check_file(f)
            all_errors.extend(errors)

    if all_errors:
        print("=" * 70)
        print("WRITE_TRUNCATE ON PRODUCTION BLOCKED")
        print("=" * 70)
        print()
        print("Per DATA PROTECTION LAWS:")
        print("- WRITE_TRUNCATE on production tables destroys data")
        print("- Use WRITE_APPEND or write to temp tables first")
        print()
        for error in all_errors:
            print(error)
            print()
        print("=" * 70)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
