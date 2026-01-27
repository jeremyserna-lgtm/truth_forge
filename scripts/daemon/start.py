#!/usr/bin/env python3
"""Start the truth_forge daemon.

MOLT LINEAGE:
- Source: Truth_Engine/scripts/daemon/start.sh
- Version: 2.0.0
- Date: 2026-01-26

Usage:
    python scripts/daemon/start.py
    python scripts/daemon/start.py --port 8080
    python scripts/daemon/start.py --background
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


# Add src to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def start_daemon(port: int, background: bool = False) -> int:
    """Start the daemon service.

    Args:
        port: Port to listen on.
        background: Whether to run in background.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    from truth_forge.daemon.service import TruthForgeDaemon

    daemon = TruthForgeDaemon(port=port)

    if background:
        # Fork to background
        pid = os.fork()
        if pid > 0:
            # Parent process
            print(f"Daemon started in background (PID: {pid})")
            pid_file = PROJECT_ROOT / "data" / "local" / "daemon.pid"
            pid_file.parent.mkdir(parents=True, exist_ok=True)
            pid_file.write_text(str(pid))
            return 0

    # Child process or foreground mode
    print(f"Starting truth_forge daemon on port {port}...")
    try:
        daemon.start()
    except KeyboardInterrupt:
        print("\nDaemon stopped by user")
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Start the truth_forge daemon",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8765,
        help="Port to listen on (default: 8765)",
    )
    parser.add_argument(
        "--background",
        "-b",
        action="store_true",
        help="Run daemon in background",
    )

    args = parser.parse_args()
    return start_daemon(port=args.port, background=args.background)


if __name__ == "__main__":
    sys.exit(main())
