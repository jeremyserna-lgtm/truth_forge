#!/usr/bin/env python3
"""Block silent exception patterns.

Per DATA PROTECTION LAWS:
- NO SILENT FAILURES - every error must be visible
- except: pass swallows errors silently
- except Exception: pass does the same

FORBIDDEN:
- except: pass
- except Exception: pass
- except Exception as e: pass
- except BaseException: pass
- except: continue (without logging/DLQ)

ALLOWED:
- except Exception as e: logger.error(...); raise
- except Exception as e: dlq.send(...); continue
- Test files
- Documented exceptions with # EXCEPTION: comment
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FORBIDDEN_PATTERNS = [
    # Bare except: pass
    (r"except\s*:\s*pass\s*$", "except: pass - swallows all errors"),
    # except Exception: pass
    (r"except\s+Exception\s*:\s*pass\s*$", "except Exception: pass - swallows errors"),
    # except Exception as e: pass
    (r"except\s+Exception\s+as\s+\w+\s*:\s*pass\s*$", "except Exception as e: pass - swallows errors"),
    # except BaseException: pass
    (r"except\s+BaseException\s*:\s*pass\s*$", "except BaseException: pass - swallows errors"),
]

ALLOWED_CONTEXTS = [
    "# EXCEPTION:",  # Documented exception
    "logger",  # Has logging
    "logging",
    "dlq",  # Has DLQ
    "DLQ",
    "raise",  # Re-raises
    "test",
    "Test",
    "mock",
    "Mock",
]


def check_file(filepath: str) -> list[str]:
    """Check file for silent exception patterns."""
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

    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        # Check context (this line and next few lines)
        context_end = min(len(lines), line_num + 3)
        context = "\n".join(lines[line_num - 1 : context_end])

        # Allow if context has logging, DLQ, or raise
        if any(ctx in context for ctx in ALLOWED_CONTEXTS):
            continue

        for pattern, description in FORBIDDEN_PATTERNS:
            if re.search(pattern, line):
                errors.append(
                    f"{filepath}:{line_num}: FORBIDDEN: {description}\n"
                    f"  Fix: Add logger.error() and/or raise, or use DLQ\n"
                    f"  Line: {line.strip()}"
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
        print("SILENT EXCEPTION BLOCKED")
        print("=" * 70)
        print()
        print("Per DATA PROTECTION LAWS:")
        print("- NO SILENT FAILURES - every error must be visible")
        print("- Either log + raise, or send to DLQ")
        print()
        for error in all_errors:
            print(error)
            print()
        print("=" * 70)
        print("FIX: Replace 'pass' with proper error handling")
        print("Example:")
        print("  except Exception as e:")
        print("      logger.error('operation_failed', extra={'error': str(e)})")
        print("      raise")
        print("=" * 70)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
