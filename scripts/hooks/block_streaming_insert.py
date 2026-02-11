#!/usr/bin/env python3
"""Block streaming insert patterns at commit time.

Per DATA PROTECTION LAWS:
- Streaming inserts caused 8.9 MILLION duplicate rows
- They are FORBIDDEN in all production code
- Use load_table_from_file() instead

FORBIDDEN PATTERNS:
- client.insert_rows_json(...)
- client.insert_rows(...)
- bigquery.Client.insert_rows_json
- bigquery.Client.insert_rows

ALLOWED:
- client.load_table_from_file(...)
- Test files (test_*.py, *_test.py)
- Files with documented EXCEPTION comments
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FORBIDDEN_PATTERNS = [
    (r"\.insert_rows_json\s*\(", "Streaming insert (insert_rows_json)"),
    (r"\.insert_rows\s*\(", "Streaming insert (insert_rows)"),
    (r"client\.insert_rows", "Direct streaming insert"),
]

ALLOWED_CONTEXTS = [
    "# LEGACY:",  # Documented legacy code
    "# EXCEPTION:",  # Documented exception with justification
    "mock",  # Test mocks
    "Mock",
    "patch",
    "assert",
]


def check_file(filepath: str) -> list[str]:
    """Check file for forbidden patterns.

    Returns list of error messages.
    """
    errors = []
    path = Path(filepath)

    # Skip test files
    if "test" in path.name.lower() or path.name.startswith("test_"):
        return []

    # Skip if file doesn't exist (may have been deleted)
    if not path.exists():
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []  # Binary file

    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        # Skip allowed contexts
        if any(ctx in line for ctx in ALLOWED_CONTEXTS):
            continue

        for pattern, description in FORBIDDEN_PATTERNS:
            if re.search(pattern, line):
                errors.append(
                    f"{filepath}:{line_num}: FORBIDDEN: {description}\n"
                    f"  Use load_table_from_file() instead.\n"
                    f"  Line: {line.strip()[:80]}"
                )

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
        print("STREAMING INSERT BLOCKED")
        print("=" * 70)
        print()
        print("Per DATA PROTECTION LAWS:")
        print("- Streaming inserts caused 8.9 MILLION duplicate rows")
        print("- They are FORBIDDEN in all production code")
        print("- Use load_table_from_file() instead")
        print()
        for error in all_errors:
            print(error)
            print()
        print("=" * 70)
        print("FIX: Replace insert_rows_json with load_table_from_file")
        print("SEE: CLAUDE.md DATA PROTECTION LAWS")
        print("=" * 70)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
