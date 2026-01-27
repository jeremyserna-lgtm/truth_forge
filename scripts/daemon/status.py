#!/usr/bin/env python3
"""Check the status of the truth_forge daemon.

MOLT LINEAGE:
- Source: Truth_Engine/scripts/daemon/status.sh
- Version: 2.0.0
- Date: 2026-01-26

Usage:
    python scripts/daemon/status.py
    python scripts/daemon/status.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).parent.parent.parent


def get_daemon_status(port: int = 8765) -> dict[str, Any]:
    """Get daemon status.

    Args:
        port: Port the daemon is running on.

    Returns:
        Status dictionary with daemon information.
    """
    pid_file = PROJECT_ROOT / "data" / "local" / "daemon.pid"

    status: dict[str, Any] = {
        "running": False,
        "pid": None,
        "port": port,
        "healthy": False,
        "version": None,
    }

    # Check PID file
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            # Check if process exists
            try:
                os.kill(pid, 0)
                status["running"] = True
                status["pid"] = pid
            except OSError:
                pass
        except (ValueError, OSError):
            pass

    # Try to connect to health endpoint
    if status["running"]:
        try:
            url = f"http://localhost:{port}/health"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                status["healthy"] = data.get("status") == "healthy"
                status["version"] = data.get("version")
        except Exception:
            status["healthy"] = False

    return status


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check truth_forge daemon status",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8765,
        help="Port to check (default: 8765)",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()
    status = get_daemon_status(port=args.port)

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print("truth_forge Daemon Status")
        print("=" * 40)
        print(f"Running: {'Yes' if status['running'] else 'No'}")
        if status["running"]:
            print(f"PID: {status['pid']}")
            print(f"Port: {status['port']}")
            print(f"Healthy: {'Yes' if status['healthy'] else 'No'}")
            if status["version"]:
                print(f"Version: {status['version']}")

    return 0 if status["running"] and status["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
