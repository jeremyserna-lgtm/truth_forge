# THE SCRIPTS

**Version**: 1.1
**Status**: Living Document

---

## Document Structure

- **Theory**: Why scripts are written and validated this way
- **Specification**: What Claude does, what the System does
- **Reference**: How to use the patterns

---

# THEORY

## The Core Separation

**Claude is not a linter.**

Claude writes. The System validates. The System repairs. The System escalates.

This separation matters because:
- Claude's job is to express intent quickly
- Linting is mechanical—machines do it better
- Human intervention (Jeremy) should be for decisions, not fixes

## The Two Loops

```
┌─────────────────────────────────────────────────────────────────────────┐
│ LOOP 1: Jeremy's Loop (MINE)                                            │
│                                                                          │
│   Jeremy (HOLD₁) → Claude Code (AGENT) → Files land (HOLD₂)            │
│                                                                          │
│   Claude does what Jeremy says. Right or wrong. Just does.              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ LOOP 2: System's Loop (THE SYSTEM'S)                                    │
│                                                                          │
│   Files land (HOLD₁) → Processor (AGENT) → Canonical state (HOLD₂)     │
│                                                                          │
│   System validates, repairs (using -p claude), places.                  │
│   Jeremy never sees this unless escalated.                              │
└─────────────────────────────────────────────────────────────────────────┘
```

**Loop 1 is fast.** Claude writes, file appears.
**Loop 2 is invisible.** System catches, fixes, or escalates.

## The Repair Philosophy

**Hooks use Claude to fix Claude's mistakes.**

When a hook finds an issue:
1. Hook calls `claude -p` with the file and issue description
2. Claude worker attempts the fix
3. Hook verifies the fix worked
4. Repeat up to 3 times
5. If still broken → Quarantine + Backlog → Jeremy directs

This is NOT Claude Code linting itself. This is:
- **Claude Code** (primary) doing the work fast
- **Claude workers** (`-p claude`) doing mechanical repairs
- **The System** orchestrating and escalating

## Why Architecture > Enforcement

If Claude has to remember 50 rules, Claude will forget some.
If the architecture makes the right thing easy, Claude does the right thing naturally.

**Good architecture:**
- Patterns that are compliant by default
- Imports that bring everything needed
- Templates that have the structure pre-baked
- Hooks that fix, not just fail

**Bad architecture:**
- Rules Claude must remember
- Manual steps Claude must perform
- Hooks that just block without helping

---

# SPECIFICATION

## What Claude Does (Write)

### The Script Pattern

Every script follows this structure:

```python
#!/usr/bin/env python3
"""
[One line describing what this script does]

Usage:
    python scripts/[name].py [args]

Part of: [pipeline/system name]
"""

import sys
from pathlib import Path

# Standard path setup (copy exactly)
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Central services (the architecture that enables compliance)
from architect_central_services import (
    get_logger,
    get_current_run_id,
)

logger = get_logger(__name__)


def main():
    """Main entry point."""
    run_id = get_current_run_id()
    logger.info(f"Starting {Path(__file__).stem}", extra={"run_id": run_id})

    # Your code here

    logger.info("Completed successfully")


if __name__ == "__main__":
    main()
```

### Why This Pattern

| Element | Why | Hook Checks? |
|---------|-----|--------------|
| Docstring at top | Future you knows what this does | ✓ |
| Path setup block | Always finds central services | ✓ |
| `get_logger(__name__)` | Never use `print()` | ✓ |
| `get_current_run_id()` | Traceability | Advisory |
| `main()` function | Testable, importable | ✓ |
| `if __name__` guard | Safe imports | ✓ |

### What Claude Should NOT Do

❌ **Don't lint your own code.** The System does that.
❌ **Don't run pre-commit manually.** It runs on commit.
❌ **Don't check import paths.** The pattern handles it.
❌ **Don't validate compliance.** The checkpoints do that.

Just follow the pattern. Write the script. Let the System handle the rest.

---

## What The System Does (Validate, Repair, Escalate)

### The Repair Service

Location: `architect_central_services/scripts/hooks/repair_service.py`

```python
from hooks.repair_service import repair_or_escalate

issues = check_file(filepath)
if issues:
    success = repair_or_escalate(
        filepath,
        issues,
        verify_func=check_file  # Re-verify after repair
    )
    if not success:
        # Already escalated to backlog
        sys.exit(1)
```

**The repair flow:**

```
Issue detected
     │
     ▼
┌─────────────────────────────────────────────┐
│ claude -p "Fix {issues} in {filepath}"      │
│                                             │
│ Attempt 1 ──failed──▶ Attempt 2 ──failed──▶ │
│     │                     │                 │
│  success               success              │
│     │                     │                 │
│     ▼                     ▼                 │
│  verify                verify               │
└─────────────────────────────────────────────┘
     │                                    │
  passes                              Attempt 3
     │                                    │
     ▼                                 failed
   Done                                   │
                                          ▼
                              ┌───────────────────────┐
                              │ Quarantine file       │
                              │ Log to backlog        │
                              │ BLOCK commit          │
                              └───────────────────────┘
```

### Checkpoint 1: Pre-commit (Current)

Hooks run on `git commit`:

| Hook | What It Does | Uses Repair? |
|------|--------------|--------------|
| `check_definition_of_done.py` | Pipeline standards | ✓ Yes |
| `check_framework_compliance.py` | Script structure | ✓ Yes |
| `check_cost_protection_bypass.py` | Cost safety | No (blocking) |
| `black` | Code formatting | Auto-fix |
| `isort` | Import sorting | Auto-fix |
| `py-compile` | Syntax check | No (blocking) |

**Repair-enabled hooks attempt 3 fixes before blocking.**

### Checkpoint 2: On File Create (Future)

File watcher triggers on new file:

```
File created → Watcher → Validate → Repair (3x) → Done
                              │
                           failed
                              │
                              ▼
                     Quarantine + Backlog
```

### The Backlog Loop

```
~/.primitive_engine/
├── backlog.jsonl          ← Issues that couldn't be auto-fixed
├── quarantine/            ← Files that failed all repair attempts
│   ├── 20260102_143022_bad_script.py
│   └── 20260102_143022_bad_script.py.meta.json
└── config.yaml
```

**Backlog entry format:**

```json
{
  "timestamp": "2026-01-02T14:30:22Z",
  "type": "hook_failure",
  "filepath": "/path/to/file.py",
  "issues": [
    {"type": "MISSING:logging", "message": "Uses print() instead of get_logger()"}
  ],
  "repair_attempts": 3,
  "status": "open",
  "source": "pre-commit-hook"
}
```

**Claude Code sees this next session.** Jeremy directs the fix. Loop closes.

### The Four Streams

```
┌─────────────────────────────────────────────────────────────────────────┐
│ truth status                                                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ LOG:        What the system did, when, to what                          │
│ BACKLOG:    What the system couldn't fix (open items)                   │
│ DECISIONS:  What Jeremy said to do                                      │
│ COMPLETED:  What got done (closed backlog items)                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# REFERENCE

## Hook Files

| File | Purpose | Repair? |
|------|---------|---------|
| `repair_service.py` | Repair infrastructure | — |
| `check_definition_of_done.py` | Pipeline standards | ✓ |
| `check_framework_compliance.py` | Script structure | ✓ |
| `check_cost_protection_bypass.py` | Cost safety | ✗ |
| `check_circular_imports.py` | Import cycles | Advisory |
| `check_sql_first.py` | SQL vs Python | Advisory |

## Creating a Repair-Enabled Hook

```python
#!/usr/bin/env python3
"""My Custom Hook (with Auto-Repair)"""

import sys
from typing import List, Tuple

try:
    from repair_service import repair_or_escalate
    REPAIR_AVAILABLE = True
except ImportError:
    REPAIR_AVAILABLE = False


def check_file(filepath: str) -> List[Tuple[str, str]]:
    """Return list of (issue_type, message) tuples."""
    issues = []
    # Your checking logic here
    return issues


def main():
    files = sys.argv[1:]
    failures = []

    for filepath in files:
        issues = check_file(filepath)
        if not issues:
            continue

        if REPAIR_AVAILABLE:
            success = repair_or_escalate(filepath, issues, verify_func=check_file)
            if success:
                continue

        failures.append((filepath, issues))

    if failures:
        # Print failures, exit 1
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
```

## File Placement

| Script Type | Location |
|-------------|----------|
| One-off utility | `architect_central_services/scripts/` |
| Pipeline stage | `architect_central_services/pipelines/[name]/scripts/` |
| Hook | `architect_central_services/scripts/hooks/` |
| Test | `architect_central_services/tests/` |

## Central Services Available

```python
from architect_central_services import (
    # Logging (never use print)
    get_logger,

    # Identity (never generate IDs manually)
    get_current_run_id,
    generate_conversation_id,
    generate_message_id,
    generate_entity_id,

    # Cost (always track billable operations)
    track_cost,

    # BigQuery (use the protected client)
    get_bigquery_client,
)

from architect_central_services.core.shared import (
    SessionCostLimiter,  # For pipelines
)
```

---

## The Principle

**Claude writes. The System repairs. Jeremy decides.**

1. Claude Code follows patterns that make compliance easy
2. Hooks catch issues and attempt repair using `-p claude`
3. What can't be auto-fixed gets escalated to backlog
4. Jeremy sees organized problems, not scattered chaos
5. Loop closes—nothing falls through

**The architecture protects Jeremy. Jeremy doesn't protect himself.**

---

*This document follows THE_FRAMEWORK structure: Theory, Specification, Reference.*
*— THE_SCRIPTS*
