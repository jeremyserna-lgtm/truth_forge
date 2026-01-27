#!/usr/bin/env python3
"""Stop the truth_forge daemon.

MOLT LINEAGE:
- Source: Truth_Engine/scripts/daemon/stop.sh
- Version: 2.0.0
- Date: 2026-01-26

Usage:
    python scripts/daemon/stop.py
    python scripts/daemon/stop.py --force
"""

from __future__ import annotations

import argparse
import os
import signal
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent.parent


def stop_daemon(force: bool = False) -> int:
    """Stop the daemon service.

    Args:
        force: Whether to force kill the daemon.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    pid_file = PROJECT_ROOT / "data" / "local" / "daemon.pid"

    if not pid_file.exists():
        print("No daemon PID file found. Is the daemon running?")
        return 1

    try:
        pid = int(pid_file.read_text().strip())
    except (ValueError, OSError) as e:
        print(f"Error reading PID file: {e}")
        return 1

    # Check if process exists
    try:
        os.kill(pid, 0)
    except OSError:
        print(f"No process found with PID {pid}. Cleaning up PID file.")
        pid_file.unlink()
        return 0

    # Send signal
    sig = signal.SIGKILL if force else signal.SIGTERM
    sig_name = "SIGKILL" if force else "SIGTERM"

    print(f"Sending {sig_name} to daemon (PID: {pid})...")
    try:
        os.kill(pid, sig)
        print("Daemon stopped")
        pid_file.unlink()
        return 0
    except OSError as e:
        print(f"Error stopping daemon: {e}")
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Stop the truth_forge daemon",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force kill the daemon (SIGKILL instead of SIGTERM)",
    )

    args = parser.parse_args()
    return stop_daemon(force=args.force)


if __name__ == "__main__":
    sys.exit(main())
