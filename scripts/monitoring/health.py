#!/usr/bin/env python3
"""Health monitoring for truth_forge.

MOLT LINEAGE:
- Source: Truth_Engine/scripts/monitoring/health_check.py
- Version: 2.0.0
- Date: 2026-01-26

Usage:
    python scripts/monitoring/health.py
    python scripts/monitoring/health.py --daemon
    python scripts/monitoring/health.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def check_directories() -> dict[str, Any]:
    """Check required directories exist.

    Returns:
        Health check result for directories.
    """
    required = [
        PROJECT_ROOT / "src" / "truth_forge",
        PROJECT_ROOT / "data",
        PROJECT_ROOT / "config",
    ]

    missing = [str(d.relative_to(PROJECT_ROOT)) for d in required if not d.exists()]

    return {
        "name": "directories",
        "healthy": len(missing) == 0,
        "missing": missing,
    }


def check_venv() -> dict[str, Any]:
    """Check virtual environment exists.

    Returns:
        Health check result for venv.
    """
    venv_path = PROJECT_ROOT / ".venv"
    pip_path = venv_path / "bin" / "pip"

    return {
        "name": "virtual_environment",
        "healthy": venv_path.exists() and pip_path.exists(),
        "path": str(venv_path) if venv_path.exists() else None,
    }


def check_daemon(port: int = 8765) -> dict[str, Any]:
    """Check daemon health.

    Args:
        port: Daemon port.

    Returns:
        Health check result for daemon.
    """
    result: dict[str, Any] = {
        "name": "daemon",
        "healthy": False,
        "port": port,
        "version": None,
    }

    try:
        url = f"http://localhost:{port}/health"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            result["healthy"] = data.get("status") == "healthy"
            result["version"] = data.get("version")
    except Exception as e:
        result["error"] = str(e)

    return result


def check_database() -> dict[str, Any]:
    """Check database connectivity.

    Returns:
        Health check result for database.
    """
    db_path = PROJECT_ROOT / "data" / "local" / "knowledge.duckdb"

    result: dict[str, Any] = {
        "name": "database",
        "healthy": False,
        "path": str(db_path.relative_to(PROJECT_ROOT)),
        "exists": db_path.exists(),
    }

    if db_path.exists():
        try:
            import duckdb

            conn = duckdb.connect(str(db_path), read_only=True)
            conn.execute("SELECT 1").fetchone()
            conn.close()
            result["healthy"] = True
        except ImportError:
            result["error"] = "duckdb not installed"
        except Exception as e:
            result["error"] = str(e)
    else:
        result["error"] = "Database file not found"

    return result


def run_health_checks(include_daemon: bool = False) -> dict[str, Any]:
    """Run all health checks.

    Args:
        include_daemon: Whether to check daemon.

    Returns:
        Combined health check results.
    """
    checks = [
        check_directories(),
        check_venv(),
        check_database(),
    ]

    if include_daemon:
        checks.append(check_daemon())

    all_healthy = all(c["healthy"] for c in checks)

    return {
        "overall_healthy": all_healthy,
        "checks": checks,
        "healthy_count": sum(1 for c in checks if c["healthy"]),
        "total_count": len(checks),
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Health monitoring for truth_forge",
    )
    parser.add_argument(
        "--daemon",
        "-d",
        action="store_true",
        help="Include daemon health check",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8765,
        help="Daemon port (default: 8765)",
    )

    args = parser.parse_args()
    result = run_health_checks(include_daemon=args.daemon)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("=" * 60)
        print("Health Check Report")
        print("=" * 60)
        print()

        for check in result["checks"]:
            status = "✓" if check["healthy"] else "✗"
            print(f"{status} {check['name']}")

            # Print details
            for key, value in check.items():
                if key not in ("name", "healthy"):
                    print(f"    {key}: {value}")

        print()
        print("=" * 60)
        healthy = result["healthy_count"]
        total = result["total_count"]

        if result["overall_healthy"]:
            print(f"✓ ALL HEALTHY ({healthy}/{total})")
        else:
            print(f"✗ ISSUES FOUND ({healthy}/{total} healthy)")

    return 0 if result["overall_healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
