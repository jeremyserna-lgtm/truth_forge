#!/usr/bin/env python3
"""Federation Launcher - Unified command center for Not-Me production.

This script launches and coordinates all Federation services:
- Scout backbone (checks LM Studio/Llama Stack availability)
- Not-Me production service
- Sovereign Interface (web UI)
- API servers (if enabled)

Usage:
    python scripts/launch_federation.py              # Full launch
    python scripts/launch_federation.py --check     # Health check only
    python scripts/launch_federation.py --ui-only   # Just the web UI
    python scripts/launch_federation.py --api-only  # Just the API server

Version: 1.0.0
Date: 2026-02-01
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# =============================================================================
# CONFIGURATION
# =============================================================================

TRUTH_FORGE_ROOT = Path(__file__).parent.parent
APPS_DIR = TRUTH_FORGE_ROOT / "apps"
CONFIG_DIR = TRUTH_FORGE_ROOT / "config" / "scout"

# Service definitions
SERVICES = {
    "sovereign-interface": {
        "type": "npm",
        "path": APPS_DIR / "sovereign-interface",
        "command": ["npm", "run", "dev"],
        "port": 3000,
        "description": "Sovereign Interface (Web UI)",
    },
    "not-me-chat": {
        "type": "python",
        "path": APPS_DIR / "not_me_chat",
        "command": ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        "port": 8000,
        "description": "Not-Me Chat API",
        "optional": True,
    },
    "admin": {
        "type": "python",
        "path": APPS_DIR / "admin",
        "command": ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"],
        "port": 8001,
        "description": "Admin Dashboard API",
        "optional": True,
    },
}

# Scout endpoints to check
SCOUT_ENDPOINTS = [
    "http://localhost:1234/v1",   # LM Studio
    "http://localhost:8080/v1",   # Llama Stack
    "http://localhost:11434/v1",  # Ollama
]


# =============================================================================
# UTILITIES
# =============================================================================

def print_banner() -> None:
    """Print Federation launch banner."""
    # Check current hardware tier
    tier = os.environ.get("SCOUT_HARDWARE_TIER", "drummer").upper()
    context_map = {
        "DRUMMER": "32K",
        "SOLDIER": "128K",
        "KING": "500K",
        "EMPIRE": "10M",
    }
    context = context_map.get(tier, "32K")

    banner = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ████████╗██╗  ██╗███████╗    ███████╗███████╗██████╗ ███████╗██████╗        ║
║   ╚══██╔══╝██║  ██║██╔════╝    ██╔════╝██╔════╝██╔══██╗██╔════╝██╔══██╗       ║
║      ██║   ███████║█████╗      █████╗  █████╗  ██║  ██║█████╗  ██████╔╝       ║
║      ██║   ██╔══██║██╔══╝      ██╔══╝  ██╔══╝  ██║  ██║██╔══╝  ██╔══██╗       ║
║      ██║   ██║  ██║███████╗    ██║     ███████╗██████╔╝███████╗██║  ██║       ║
║      ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═╝     ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝       ║
║                                                                               ║
║   Hardware Tier: {tier:<10}  Context: {context:<6}  Target: EMPIRE (10M)        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def check_scout_available() -> tuple[bool, str | None]:
    """Check if Scout backend is available.

    Returns:
        Tuple of (available, endpoint_url).
    """
    import urllib.request

    for endpoint in SCOUT_ENDPOINTS:
        try:
            url = f"{endpoint}/models"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    models = [m.get("id", "") for m in data.get("data", [])]
                    print(f"  ✓ Scout available at {endpoint}")
                    print(f"    Models: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")
                    return True, endpoint
        except Exception:
            continue

    return False, None


def check_port_available(port: int) -> bool:
    """Check if a port is available."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0


def start_service(name: str, config: dict[str, Any]) -> subprocess.Popen | None:
    """Start a service.

    Args:
        name: Service name.
        config: Service configuration.

    Returns:
        Process handle or None if failed.
    """
    path = config["path"]
    command = config["command"]
    port = config["port"]

    if not path.exists():
        print(f"  ✗ {name}: Directory not found ({path})")
        return None

    if not check_port_available(port):
        print(f"  ✗ {name}: Port {port} already in use")
        return None

    try:
        process = subprocess.Popen(
            command,
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        print(f"  ✓ {name} starting on port {port}")
        return process
    except Exception as e:
        print(f"  ✗ {name}: Failed to start ({e})")
        return None


# =============================================================================
# COMMANDS
# =============================================================================

def cmd_check() -> int:
    """Run health check on all services."""
    print("\n[Federation Health Check]\n")

    # Check Scout
    print("Scout Backbone:")
    scout_ok, scout_endpoint = check_scout_available()
    if not scout_ok:
        print("  ✗ No Scout server found")
        print("    Start LM Studio or Llama Stack with a Scout model")

    # Check service ports
    print("\nService Ports:")
    for name, config in SERVICES.items():
        port = config["port"]
        available = check_port_available(port)
        status = "available" if available else "in use"
        symbol = "✓" if available else "!"
        print(f"  {symbol} Port {port} ({name}): {status}")

    # Check paths
    print("\nService Paths:")
    for name, config in SERVICES.items():
        path = config["path"]
        exists = path.exists()
        symbol = "✓" if exists else "✗"
        print(f"  {symbol} {name}: {path}")

    return 0 if scout_ok else 1


def cmd_launch(ui_only: bool = False, api_only: bool = False) -> int:
    """Launch Federation services."""
    print_banner()
    print("[Launching Federation]\n")

    # Check Scout first
    print("1. Checking Scout backbone...")
    scout_ok, scout_endpoint = check_scout_available()

    if not scout_ok:
        print("\n⚠ WARNING: Scout server not detected!")
        print("  The Sovereign Interface will show 'disconnected' until Scout is running.")
        print("  Start LM Studio with a LLaMA 4 Scout model to enable full functionality.")
        print()

    # Export Scout endpoint for services
    if scout_endpoint:
        os.environ["SCOUT_BASE_URL"] = scout_endpoint

    # Start services
    processes: dict[str, subprocess.Popen] = {}

    print("\n2. Starting services...")

    if not api_only:
        # Start Sovereign Interface
        if "sovereign-interface" in SERVICES:
            process = start_service("sovereign-interface", SERVICES["sovereign-interface"])
            if process:
                processes["sovereign-interface"] = process

    if not ui_only:
        # Start API services (optional)
        for name, config in SERVICES.items():
            if name == "sovereign-interface":
                continue
            if config.get("optional"):
                print(f"  - {name}: Skipping (optional)")
                continue
            process = start_service(name, config)
            if process:
                processes[name] = process

    if not processes:
        print("\n✗ No services started!")
        return 1

    # Wait and show status
    print("\n3. Services running:")
    for name, process in processes.items():
        config = SERVICES[name]
        print(f"  • {config['description']}: http://localhost:{config['port']}")

    print("\n[Press Ctrl+C to stop all services]\n")

    # Wait for Ctrl+C
    try:
        while True:
            time.sleep(1)
            # Check if any process died
            for name, process in list(processes.items()):
                if process.poll() is not None:
                    print(f"⚠ Service {name} stopped unexpectedly")
                    del processes[name]
            if not processes:
                print("All services stopped.")
                break
    except KeyboardInterrupt:
        print("\n\n[Stopping services...]")
        for name, process in processes.items():
            print(f"  Stopping {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    return 0


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Federation Launcher - Unified command center for Not-Me production",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/launch_federation.py              # Full launch
  python scripts/launch_federation.py --check     # Health check only
  python scripts/launch_federation.py --ui-only   # Just the web UI
        """,
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Run health check only",
    )
    parser.add_argument(
        "--ui-only",
        action="store_true",
        help="Launch only the web UI",
    )
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Launch only API services",
    )

    args = parser.parse_args()

    if args.check:
        return cmd_check()
    else:
        return cmd_launch(ui_only=args.ui_only, api_only=args.api_only)


if __name__ == "__main__":
    sys.exit(main())
