# Script Contract

**What you put in a script.**

*A script is an Agent. It must follow one of the four patterns: Bridge, Loop, Observer, or Forge.*

See [THE_SCRIPT_PATTERNS.md](../2_concepts/THE_SCRIPT_PATTERNS.md) for definitions.

---

## Required Imports

```python
from architect_central_services import (
    get_logger,
    get_current_run_id,
    get_correlation_ids,
    track_cost,
    write_event,
)

logger = get_logger(__name__)
run_id = get_current_run_id()
```

---

## Required Events

### On Start

```python
write_event(
    source=__name__,
    event_type="start",
    content={"args": sys.argv, "config": config}
)
```

### On End

```python
write_event(
    source=__name__,
    event_type="end",
    content={"status": "success", "items_processed": count}
)
```

### On Error

```python
except Exception as e:
    write_event(
        source=__name__,
        event_type="error",
        content={"error": str(e), "traceback": traceback.format_exc()}
    )
    raise
```

### On Cost

```python
track_cost(
    operation="bigquery_query",
    cost_usd=estimated_cost,
    component=__name__
)
```

---

## Template

```python
#!/usr/bin/env python3
"""
[Description of what this script does]
"""

import sys
import traceback
from architect_central_services import (
    get_logger,
    get_current_run_id,
    get_correlation_ids,
    track_cost,
    write_event,
)

logger = get_logger(__name__)
run_id = get_current_run_id()
correlation_ids = get_correlation_ids()


def main():
    """Main entry point."""
    write_event(__name__, "start", {"args": sys.argv})

    try:
        # Your code here
        result = do_work()

        write_event(__name__, "end", {"status": "success", "result": result})

    except Exception as e:
        write_event(__name__, "error", {
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        raise


if __name__ == "__main__":
    main()
```

---

## Checklist

```
[ ] Imports central services
[ ] Creates logger with __name__
[ ] Gets run_id at start
[ ] Writes start event
[ ] Writes end event with status
[ ] Catches and writes errors
[ ] Tracks cost for billable operations
```

---

## Writes To

`~/.primitive_engine/executions.jsonl`

---

## The Sentence

| WHO | DOES | TO | HOW |
|-----|------|----|-----|
| Script | writes | events | to executions.jsonl via write_event() |

---

*Derived from [THE_ENTITY_CONTRACTS.md](../THE_ENTITY_CONTRACTS.md)*
