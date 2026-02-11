#!/usr/bin/env python3
"""Claude Code pre-bash hook - blocks dangerous commands.

This hook runs BEFORE Claude executes any bash command.
It blocks commands that could destroy data.

Receives tool input via stdin as JSON.
Exit 0 = allow, Exit 1 = block.
"""
from __future__ import annotations

import json
import re
import sys


FORBIDDEN_COMMANDS = [
    # Direct pipeline runs without validation
    (r"python.*pipeline.*--skip-validation", "BLOCKED: Pipelines must run with validation"),
    (r"python.*pipeline.*--no-validate", "BLOCKED: Pipelines must run with validation"),

    # BigQuery dangerous operations
    (r"bq\s+rm\s+.*spine\.", "BLOCKED: Cannot delete spine tables via CLI"),
    (r"bq\s+rm\s+.*entity_unified", "BLOCKED: Cannot delete entity_unified via CLI"),
    (r"bq\s+rm\s+.*entity_enrichments", "BLOCKED: Cannot delete entity_enrichments via CLI"),
    (r"bq\s+query.*DELETE\s+FROM", "BLOCKED: No DELETE via bq query"),
    (r"bq\s+query.*DROP\s+TABLE", "BLOCKED: No DROP TABLE via bq query"),
    (r"bq\s+query.*TRUNCATE", "BLOCKED: No TRUNCATE via bq query"),

    # Dangerous file operations
    (r"rm\s+-rf?\s+.*/pipelines", "BLOCKED: Cannot rm -rf pipelines directory"),
    (r"rm\s+-rf?\s+.*/data", "BLOCKED: Cannot rm -rf data directory"),
    (r"rm\s+-rf?\s+.*/src", "BLOCKED: Cannot rm -rf src directory"),
    (r"rm\s+-rf?\s+~/", "BLOCKED: Cannot rm -rf in home directory"),

    # Git operations that could lose data
    (r"git\s+reset\s+--hard", "BLOCKED: git reset --hard can lose work - use carefully"),
    (r"git\s+clean\s+-fd", "BLOCKED: git clean can delete untracked files"),
    (r"git\s+push.*--force.*main", "BLOCKED: Cannot force push to main"),
    (r"git\s+push.*--force.*master", "BLOCKED: Cannot force push to master"),
]


def main() -> int:
    """Check command for dangerous patterns."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    command = input_data.get("command", "")
    if not command:
        return 0

    for pattern, message in FORBIDDEN_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            print(f"BLOCKED: {message}", file=sys.stderr)
            print(f"Command: {command[:100]}", file=sys.stderr)
            print("", file=sys.stderr)
            print("Per DATA PROTECTION LAWS in CLAUDE.md", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
