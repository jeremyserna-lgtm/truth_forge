# Hook Contract

**What you put in a hook.**

*A hook is a function that executes in response to an event to enforce policy.*

---

## Required Structure

```python
import sys
from architect_central_services import write_event

HOOK_NAME = "check_something"


def main():
    """Main entry point for hook."""
    # Get context from environment or stdin
    context = get_context()

    write_event(HOOK_NAME, "trigger", {
        "event_type": context.event_type,
        "target": context.target
    })

    # Check condition
    result = check_condition(context)

    write_event(HOOK_NAME, "decision", {
        "result": "allow" if result.allow else "block",
        "reason": result.reason
    })

    if not result.allow:
        print(f"BLOCKED: {result.reason}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)
```

---

## Required Events

### On Trigger

```python
write_event(HOOK_NAME, "trigger", {
    "event_type": "tool_call",  # or "commit", "file_write", etc.
    "target": target_path_or_action,
    "context": relevant_context
})
```

### On Decision

```python
write_event(HOOK_NAME, "decision", {
    "result": "allow",  # or "block"
    "reason": "why this decision was made",
    "details": additional_info
})
```

---

## Template

```python
#!/usr/bin/env python3
"""
Hook: [Hook Name]

Checks: [What this hook checks]
Blocks: [When this hook blocks]
"""

import json
import os
import sys
from architect_central_services import write_event

HOOK_NAME = "check_something"


def get_context() -> dict:
    """Get context from environment or stdin."""
    # For Claude Code hooks, context comes from stdin
    if not sys.stdin.isatty():
        return json.load(sys.stdin)

    # For pre-commit hooks, context comes from args/env
    return {
        "files": sys.argv[1:],
        "event_type": os.environ.get("PRE_COMMIT_HOOK", "unknown")
    }


def check_condition(context: dict) -> tuple[bool, str]:
    """
    Check the condition.

    Returns:
        (allow: bool, reason: str)
    """
    # Your check logic here
    if something_bad(context):
        return False, "Blocked because [reason]"

    return True, "Allowed because [reason]"


def main():
    """Main entry point."""
    context = get_context()

    write_event(HOOK_NAME, "trigger", {
        "event_type": context.get("event_type"),
        "context_keys": list(context.keys())
    })

    allow, reason = check_condition(context)

    write_event(HOOK_NAME, "decision", {
        "result": "allow" if allow else "block",
        "reason": reason
    })

    if not allow:
        # Provide feedback to user
        print(f"BLOCKED by {HOOK_NAME}: {reason}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## Hook Types

### Claude Code Hook

Registered in `.claude/hooks.json`:

```json
{
  "hooks": [
    {
      "matcher": {
        "tool_name": "Bash"
      },
      "hooks": [
        {
          "type": "command",
          "command": "python bin/hooks/check_something.py"
        }
      ]
    }
  ]
}
```

### Pre-Commit Hook

Registered in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: check-something
        name: Check Something
        entry: python bin/hooks/check_something.py
        language: python
        types: [python]
```

---

## Checklist

```
[ ] Has defined HOOK_NAME
[ ] Gets context from appropriate source
[ ] Writes trigger event
[ ] Performs check
[ ] Writes decision event with result and reason
[ ] Returns appropriate exit code (0=allow, 1=block)
[ ] Provides clear feedback when blocking
[ ] Fast execution (hooks block the action)
```

---

## Writes To

`~/.primitive_engine/hooks.jsonl`

---

## The Sentence

| WHO | DOES | TO | HOW |
|-----|------|----|-----|
| Hook | writes | enforcement events | to hooks.jsonl via write_event() |

---

*Derived from [The Entity Contracts](INDEX.md)*
