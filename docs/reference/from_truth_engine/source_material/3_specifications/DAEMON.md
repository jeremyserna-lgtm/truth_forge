# Daemon Contract

**What you put in a daemon.**

*A daemon is a long-running process that performs work continuously.*

---

## Required Structure

```python
import signal
import time
from architect_central_services import (
    get_logger,
    get_current_run_id,
    write_event,
)

logger = get_logger(__name__)
run_id = get_current_run_id()

DAEMON_NAME = "my_daemon"
INTERVAL_SECONDS = 60
HEARTBEAT_SECONDS = 300

_shutdown_requested = False


def signal_handler(signum, frame):
    global _shutdown_requested
    _shutdown_requested = True
    write_event(DAEMON_NAME, "shutdown_requested", {"signal": signum})


def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    write_event(DAEMON_NAME, "start", {
        "interval": INTERVAL_SECONDS,
        "heartbeat": HEARTBEAT_SECONDS,
        "pid": os.getpid()
    })

    last_heartbeat = time.time()

    while not _shutdown_requested:
        try:
            # Do work
            do_cycle()

            write_event(DAEMON_NAME, "cycle", {"status": "success"})

            # Heartbeat
            if time.time() - last_heartbeat > HEARTBEAT_SECONDS:
                write_event(DAEMON_NAME, "heartbeat", {"status": "alive"})
                last_heartbeat = time.time()

            # Wait for next cycle
            time.sleep(INTERVAL_SECONDS)

        except Exception as e:
            write_event(DAEMON_NAME, "error", {"error": str(e)})
            time.sleep(INTERVAL_SECONDS)  # Don't spin on errors

    write_event(DAEMON_NAME, "shutdown", {"reason": "signal"})
```

---

## Required Events

### On Start

```python
write_event(DAEMON_NAME, "start", {
    "interval": INTERVAL_SECONDS,
    "heartbeat": HEARTBEAT_SECONDS,
    "pid": os.getpid(),
    "config": config
})
```

### On Heartbeat

```python
write_event(DAEMON_NAME, "heartbeat", {
    "status": "alive",
    "uptime_seconds": time.time() - start_time,
    "cycles_completed": cycle_count
})
```

### On Cycle

```python
write_event(DAEMON_NAME, "cycle", {
    "status": "success",
    "items_processed": count,
    "duration_seconds": elapsed
})
```

### On Error

```python
write_event(DAEMON_NAME, "error", {
    "error": str(e),
    "traceback": traceback.format_exc(),
    "will_retry": True
})
```

### On Shutdown

```python
write_event(DAEMON_NAME, "shutdown", {
    "reason": "signal",  # or "error", "manual"
    "uptime_seconds": time.time() - start_time,
    "cycles_completed": cycle_count
})
```

---

## Template

```python
#!/usr/bin/env python3
"""
[Daemon Name] Daemon

Purpose: [What this daemon does]
Interval: Runs every N seconds
"""

import os
import signal
import time
import traceback
from architect_central_services import (
    get_logger,
    get_current_run_id,
    write_event,
)

logger = get_logger(__name__)
run_id = get_current_run_id()

DAEMON_NAME = "my_daemon"
INTERVAL_SECONDS = 60
HEARTBEAT_SECONDS = 300

_shutdown_requested = False
_start_time = None
_cycle_count = 0


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    global _shutdown_requested
    _shutdown_requested = True
    logger.info(f"Shutdown requested via signal {signum}")


def do_cycle():
    """Perform one cycle of work."""
    global _cycle_count

    # Your work here
    items = get_items_to_process()
    for item in items:
        process_item(item)

    _cycle_count += 1
    return len(items)


def main():
    """Main entry point."""
    global _start_time, _shutdown_requested

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    _start_time = time.time()
    last_heartbeat = _start_time

    write_event(DAEMON_NAME, "start", {
        "interval": INTERVAL_SECONDS,
        "heartbeat": HEARTBEAT_SECONDS,
        "pid": os.getpid()
    })

    logger.info(f"Daemon started: {DAEMON_NAME}")

    while not _shutdown_requested:
        cycle_start = time.time()

        try:
            items_processed = do_cycle()

            write_event(DAEMON_NAME, "cycle", {
                "status": "success",
                "items_processed": items_processed,
                "duration_seconds": time.time() - cycle_start
            })

        except Exception as e:
            logger.error(f"Cycle failed: {e}")
            write_event(DAEMON_NAME, "error", {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "will_retry": True
            })

        # Heartbeat
        now = time.time()
        if now - last_heartbeat > HEARTBEAT_SECONDS:
            write_event(DAEMON_NAME, "heartbeat", {
                "status": "alive",
                "uptime_seconds": now - _start_time,
                "cycles_completed": _cycle_count
            })
            last_heartbeat = now

        # Wait for next cycle
        elapsed = time.time() - cycle_start
        sleep_time = max(0, INTERVAL_SECONDS - elapsed)
        time.sleep(sleep_time)

    # Clean shutdown
    write_event(DAEMON_NAME, "shutdown", {
        "reason": "signal",
        "uptime_seconds": time.time() - _start_time,
        "cycles_completed": _cycle_count
    })

    logger.info(f"Daemon stopped: {DAEMON_NAME}")


if __name__ == "__main__":
    main()
```

---

## Checklist

```
[ ] Has defined DAEMON_NAME
[ ] Has defined INTERVAL_SECONDS
[ ] Has defined HEARTBEAT_SECONDS
[ ] Registers signal handlers (SIGTERM, SIGINT)
[ ] Writes start event with config and PID
[ ] Writes heartbeat every N seconds
[ ] Writes cycle event after each cycle
[ ] Writes error events (doesn't crash on error)
[ ] Writes shutdown event with reason
[ ] Graceful shutdown on signal
```

---

## Writes To

`~/.primitive_engine/daemon.jsonl`

---

## The Sentence

| WHO | DOES | TO | HOW |
|-----|------|----|-----|
| Daemon | writes | lifecycle events | to daemon.jsonl via write_event() |

---

*Derived from [THE_ENTITY_CONTRACTS.md](../THE_ENTITY_CONTRACTS.md)*
