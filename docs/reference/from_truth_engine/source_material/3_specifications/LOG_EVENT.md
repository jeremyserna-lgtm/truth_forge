# Log Event Contract

**What goes in a log event.**

*A log event is a single line in a JSONL file that records something that happened.*

---

## Required Fields

Every log event MUST have these fields:

| Field | Type | Source | Purpose |
|-------|------|--------|---------|
| `source` | string | Caller provides | WHO wrote this |
| `event_type` | string | Caller provides | WHAT kind of event |
| `timestamp` | string (ISO 8601) | Auto-generated | WHEN it happened |
| `run_id` | string | `get_current_run_id()` | WHICH execution |
| `row_id` | string | `generate_execution_id()` | Unique identity |
| `content` | object | Caller provides | THE data |

---

## Format

```json
{
  "source": "my_script",
  "event_type": "start",
  "timestamp": "2025-12-29T10:30:42.123456+00:00",
  "run_id": "run_a1b2c3d4",
  "row_id": "my_script:20251229:103042:a1b2c3d4",
  "content": {
    "args": ["--input", "data.jsonl"],
    "config": {"max_items": 1000}
  }
}
```

---

## Creating a Log Event

### Via write_event() (Recommended)

```python
from architect_central_services import write_event

write_event(
    source="my_script",
    event_type="start",
    content={"args": sys.argv}
)
```

The function adds `timestamp`, `run_id`, and `row_id` automatically.

### Manually (If Needed)

```python
from datetime import datetime, timezone
from architect_central_services import get_current_run_id, generate_execution_id

event = {
    "source": "my_script",
    "event_type": "start",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "run_id": get_current_run_id(),
    "row_id": generate_execution_id("my_script"),
    "content": {"args": sys.argv}
}

# Write to JSONL
with open(destination, "a") as f:
    f.write(json.dumps(event) + "\n")
```

---

## Event Types

### Standard Event Types

| event_type | When to Use | Typical Content |
|------------|-------------|-----------------|
| `start` | Beginning of execution | args, config |
| `end` | End of execution | status, metrics |
| `error` | Error occurred | error message, traceback |
| `checkpoint` | Progress saved | position, count |
| `call` | Service method called | method, args |
| `return` | Service method returned | status, result summary |
| `trigger` | Hook triggered | event context |
| `decision` | Hook decided | allow/block, reason |
| `stage_start` | Pipeline stage started | stage number, config |
| `stage_end` | Pipeline stage ended | metrics |
| `heartbeat` | Daemon still alive | uptime, cycle count |
| `cycle` | Daemon completed cycle | items processed |
| `shutdown` | Daemon stopping | reason, final metrics |
| `sync_start` | Collector starting | sources |
| `sync_complete` | Collector finished | totals |
| `cost` | Cost incurred | amount, operation |

### Custom Event Types

You can define custom event types. Use lowercase with underscores:

```python
write_event("my_component", "custom_event", {...})
```

---

## Content Guidelines

### What to Include

- **Identifiers**: IDs of things being processed
- **Counts**: How many items processed/failed/skipped
- **Durations**: How long things took
- **Status**: Success/failure/partial
- **Context**: Relevant configuration or state

### What NOT to Include

- **Secrets**: API keys, passwords, tokens
- **Large data**: Full document contents (use references)
- **PII without reason**: Only if necessary for traceability

### Size Limits

- Keep individual events under 10KB
- Keep content strings under 1000 characters
- Use references for large objects

---

## JSONL Rules

### One Line Per Event

```
{"source":"a","event_type":"start",...}
{"source":"a","event_type":"end",...}
```

NOT:

```
{
  "source": "a",
  "event_type": "start",
  ...
}
```

### No Newlines in Content

```python
# WRONG - will break JSONL
content = {"message": "line1\nline2"}

# RIGHT - escape or replace
content = {"message": "line1\\nline2"}
# or
content = {"message": "line1 | line2"}
```

### Valid JSON

Every line must be valid JSON. Use `json.dumps()`:

```python
import json
line = json.dumps(event)  # Handles escaping
```

---

## Checklist

```
[ ] Has source (who wrote it)
[ ] Has event_type (what kind)
[ ] Has timestamp (ISO 8601 with timezone)
[ ] Has run_id (which execution)
[ ] Has row_id (unique identity)
[ ] Has content (the data)
[ ] Is valid JSON
[ ] Is one line (no newlines)
[ ] Content is under 10KB
[ ] No secrets in content
```

---

## The Sentence

| WHO | DOES | TO | HOW |
|-----|------|----|-----|
| Log event | exists | in JSONL | as one line of JSON |

---

*Derived from [The Entity Contracts](INDEX.md)*
