#!/usr/bin/env python3
"""Require structured logging instead of print statements.

Per DATA PROTECTION LAWS:
- print() statements are not queryable
- Use structured logging (logger.info/warning/error with extra={})
- This enables observability and debugging

FORBIDDEN in src/ and pipelines/:
- print(...)
- print(f"...")
- sys.stdout.write(...)

ALLOWED:
- CLI tools (*cli*.py, main.py with __name__ == "__main__")
- Test files
- Scripts in scripts/ directory
- Files with # EXCEPTION: comment
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FORBIDDEN_PATTERNS = [
    (r"^\s*print\s*\(", "print() statement"),
    (r"^\s*sys\.stdout\.write\s*\(", "sys.stdout.write()"),
    (r"^\s*sys\.stderr\.write\s*\(", "sys.stderr.write()"),
]

ALLOWED_FILES = [
    "cli",
    "main.py",
    "__main__.py",
    "repl",
]

ALLOWED_CONTEXTS = [
    "# EXCEPTION:",
    "if __name__",  # Allow in main blocks
    "test",
    "Test",
    "argparse",  # CLI argument parsing context
]


def check_file(filepath: str) -> list[str]:
    """Check file for print statements."""
    errors = []
    path = Path(filepath)

    # Skip test files
    if "test" in path.name.lower() or path.name.startswith("test_"):
        return []

    # Skip allowed file patterns
    if any(pattern in path.name.lower() for pattern in ALLOWED_FILES):
        return []

    if not path.exists():
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    # Check if file has a main block - allow prints there
    has_main_block = 'if __name__ == "__main__"' in content or "if __name__ == '__main__'" in content

    lines = content.split("\n")
    in_main_block = False

    for line_num, line in enumerate(lines, 1):
        # Track if we're in __main__ block
        if 'if __name__' in line:
            in_main_block = True
            continue

        # Skip if in main block (CLI usage is OK)
        if in_main_block and has_main_block:
            continue

        # Skip allowed contexts
        if any(ctx in line for ctx in ALLOWED_CONTEXTS):
            continue

        for pattern, description in FORBIDDEN_PATTERNS:
            if re.search(pattern, line):
                errors.append(
                    f"{filepath}:{line_num}: FORBIDDEN: {description}\n"
                    f"  Use structured logging instead: logger.info('message', extra={{...}})\n"
                    f"  Line: {line.strip()[:80]}"
                )

    return errors


def main() -> int:
    """Check all staged files."""
    files = sys.argv[1:]
    all_errors = []

    for f in files:
        if f.endswith(".py"):
            # Only check src/ and pipelines/
            if "/src/" in f or "/pipelines/" in f:
                errors = check_file(f)
                all_errors.extend(errors)

    if all_errors:
        print("=" * 70)
        print("PRINT STATEMENT BLOCKED")
        print("=" * 70)
        print()
        print("Per DATA PROTECTION LAWS:")
        print("- Use structured logging for observability")
        print("- print() output is not queryable")
        print()
        for error in all_errors:
            print(error)
            print()
        print("=" * 70)
        print("FIX: Replace print() with structured logging:")
        print("  logger.info('operation_complete', extra={'count': 42})")
        print("=" * 70)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
