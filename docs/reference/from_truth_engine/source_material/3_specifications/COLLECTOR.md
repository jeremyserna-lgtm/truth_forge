# Collector Contract

**What you put in a collector.**

*A collector reads from sources and writes to a unified destination.*

---

## Required Structure

```python
from architect_central_services import (
    get_logger,
    get_current_run_id,
    write_event,
)

logger = get_logger(__name__)
run_id = get_current_run_id()

COLLECTOR_NAME = "my_collector"


def collect():
    """Run collection cycle."""
    write_event(COLLECTOR_NAME, "sync_start", {
        "sources": list(SOURCES.keys())
    })

    total_collected = 0

    for source_name, source_config in SOURCES.items():
        try:
            count = collect_from_source(source_name, source_config)
            total_collected += count

            write_event(COLLECTOR_NAME, "source_complete", {
                "source": source_name,
                "items_collected": count
            })

        except Exception as e:
            write_event(COLLECTOR_NAME, "source_error", {
                "source": source_name,
                "error": str(e)
            })

    write_event(COLLECTOR_NAME, "sync_complete", {
        "total_collected": total_collected
    })
```

---

## Required Events

### On Sync Start

```python
write_event(COLLECTOR_NAME, "sync_start", {
    "sources": ["source1", "source2"],
    "destination": "intake.jsonl"
})
```

### On Source Complete

```python
write_event(COLLECTOR_NAME, "source_complete", {
    "source": "source_name",
    "items_collected": count,
    "last_position": position  # for resumability
})
```

### On Source Error

```python
write_event(COLLECTOR_NAME, "source_error", {
    "source": "source_name",
    "error": str(e),
    "will_retry": True
})
```

### On Sync Complete

```python
write_event(COLLECTOR_NAME, "sync_complete", {
    "total_collected": total,
    "sources_succeeded": succeeded,
    "sources_failed": failed,
    "duration_seconds": elapsed
})
```

---

## Template

```python
#!/usr/bin/env python3
"""
[Collector Name] Collector

Sources: [List of sources this collector reads from]
Destination: [Where this collector writes to]
"""

import json
import time
from pathlib import Path
from architect_central_services import (
    get_logger,
    get_current_run_id,
    write_event,
)

logger = get_logger(__name__)
run_id = get_current_run_id()

COLLECTOR_NAME = "my_collector"
DESTINATION = Path("~/.primitive_engine/intake.jsonl").expanduser()
STATE_FILE = Path("~/.primitive_engine/collector_state.jsonl").expanduser()

SOURCES = {
    "source1": {"path": "/path/to/source1"},
    "source2": {"path": "/path/to/source2"},
}


def load_state() -> dict:
    """Load collector state (last positions per source)."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state: dict):
    """Save collector state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def collect_from_source(source_name: str, config: dict, state: dict) -> int:
    """
    Collect from a single source.

    Returns:
        Number of items collected.
    """
    last_position = state.get(source_name, 0)

    # Read from source starting at last position
    items = read_source(config["path"], start=last_position)

    # Write to destination
    with open(DESTINATION, "a") as f:
        for item in items:
            # Transform to unified format
            record = {
                "source": source_name,
                "content": item,
                # metadata added by write_event pattern
            }
            f.write(json.dumps(record) + "\n")

    # Update state
    state[source_name] = last_position + len(items)
    save_state(state)

    return len(items)


def main():
    """Main entry point."""
    start_time = time.time()
    state = load_state()

    write_event(COLLECTOR_NAME, "sync_start", {
        "sources": list(SOURCES.keys()),
        "destination": str(DESTINATION)
    })

    total = 0
    succeeded = 0
    failed = 0

    for source_name, config in SOURCES.items():
        try:
            count = collect_from_source(source_name, config, state)
            total += count
            succeeded += 1

            write_event(COLLECTOR_NAME, "source_complete", {
                "source": source_name,
                "items_collected": count,
                "last_position": state.get(source_name)
            })

        except Exception as e:
            failed += 1
            logger.error(f"Failed to collect from {source_name}: {e}")

            write_event(COLLECTOR_NAME, "source_error", {
                "source": source_name,
                "error": str(e)
            })

    write_event(COLLECTOR_NAME, "sync_complete", {
        "total_collected": total,
        "sources_succeeded": succeeded,
        "sources_failed": failed,
        "duration_seconds": time.time() - start_time
    })


if __name__ == "__main__":
    main()
```

---

## Checklist

```
[ ] Has defined COLLECTOR_NAME
[ ] Has defined SOURCES (what to read from)
[ ] Has defined DESTINATION (where to write)
[ ] Tracks state (last position per source)
[ ] Writes sync_start event
[ ] Writes source_complete for each source
[ ] Writes source_error on failures
[ ] Writes sync_complete with totals
[ ] Handles source failures gracefully (continues with other sources)
[ ] Transforms to unified format
```

---

## Writes To

`~/.primitive_engine/collector.jsonl`

---

## The Sentence

| WHO | DOES | TO | HOW |
|-----|------|----|-----|
| Collector | writes | sync events | to collector.jsonl via write_event() |

---

*Derived from [The Entity Contracts](INDEX.md)*
