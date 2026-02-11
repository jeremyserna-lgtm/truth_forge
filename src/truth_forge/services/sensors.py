"""Lightweight presence/sensor collection for Genesis.

Collects host-level signals used for heartbeats, observability, and night-watch
tasks. Avoids heavy deps; uses stdlib only.
"""

from __future__ import annotations

import os
import socket
from datetime import UTC, datetime
from shutil import disk_usage
from typing import Any


def collect_presence() -> dict[str, Any]:
    """Return a snapshot of host/system presence signals."""
    now = datetime.now(UTC)
    hostname = socket.gethostname()

    # loadavg may not be available on all platforms
    try:
        load1, load5, load15 = os.getloadavg()
    except (AttributeError, OSError):
        load1 = load5 = load15 = None

    total, used, free = disk_usage("/")

    return {
        "timestamp_utc": now.isoformat(),
        "hostname": hostname,
        "pid": os.getpid(),
        "loadavg": {"1m": load1, "5m": load5, "15m": load15},
        "disk": {
            "total_bytes": total,
            "used_bytes": used,
            "free_bytes": free,
            "free_pct": round((free / total) * 100, 2) if total else None,
        },
        "env_mode": os.environ.get("GENESIS_EXECUTION_MODE", "servant"),
        "local_hour": now.astimezone().hour,
    }
