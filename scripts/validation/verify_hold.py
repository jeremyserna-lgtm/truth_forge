#!/usr/bin/env python3
"""Verify HOLD pattern implementation across services.

MOLT LINEAGE:
- Source: Truth_Engine/scripts/validation/verify_pattern.py
- Version: 2.0.0
- Date: 2026-01-26

Usage:
    python scripts/validation/verify_hold.py
    python scripts/validation/verify_hold.py --service secret
    python scripts/validation/verify_hold.py --verbose
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


# Add src to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def verify_service_hold(service_name: str) -> dict[str, Any]:
    """Verify HOLD pattern for a service.

    Args:
        service_name: Name of the service to verify.

    Returns:
        Verification result with pattern compliance details.
    """
    result: dict[str, Any] = {
        "service": service_name,
        "has_hold1": False,
        "has_agent": False,
        "has_hold2": False,
        "compliant": False,
        "issues": [],
    }

    service_dir = PROJECT_ROOT / "src" / "truth_forge" / "services" / service_name

    if not service_dir.exists():
        result["issues"].append(f"Service directory not found: {service_dir}")
        return result

    # Check for __init__.py
    init_file = service_dir / "__init__.py"
    if not init_file.exists():
        result["issues"].append("Missing __init__.py")
        return result

    # Check for service.py
    service_file = service_dir / "service.py"
    if not service_file.exists():
        result["issues"].append("Missing service.py")
        return result

    # Read service file and check for HOLD pattern
    content = service_file.read_text()

    # Check for HOLD1 (input/receive method)
    hold1_indicators = ["def receive", "def input", "HOLD1", "hold_1", "_receive"]
    for indicator in hold1_indicators:
        if indicator in content:
            result["has_hold1"] = True
            break

    # Check for AGENT (process/transform method)
    agent_indicators = ["def process", "def transform", "AGENT", "_process"]
    for indicator in agent_indicators:
        if indicator in content:
            result["has_agent"] = True
            break

    # Check for HOLD2 (output/deliver method)
    hold2_indicators = ["def deliver", "def output", "HOLD2", "hold_2", "_deliver"]
    for indicator in hold2_indicators:
        if indicator in content:
            result["has_hold2"] = True
            break

    # Determine compliance
    if result["has_hold1"] and result["has_agent"] and result["has_hold2"]:
        result["compliant"] = True
    else:
        if not result["has_hold1"]:
            result["issues"].append("Missing HOLD1 (receive/input) method")
        if not result["has_agent"]:
            result["issues"].append("Missing AGENT (process/transform) method")
        if not result["has_hold2"]:
            result["issues"].append("Missing HOLD2 (deliver/output) method")

    return result


def get_all_services() -> list[str]:
    """Get list of all services.

    Returns:
        List of service names.
    """
    services_dir = PROJECT_ROOT / "src" / "truth_forge" / "services"
    if not services_dir.exists():
        return []

    return [
        d.name
        for d in services_dir.iterdir()
        if d.is_dir() and not d.name.startswith("_") and (d / "service.py").exists()
    ]


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify HOLD pattern implementation",
    )
    parser.add_argument(
        "--service",
        "-s",
        help="Verify specific service (default: all)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("HOLD Pattern Verification")
    print("=" * 60)
    print("Pattern: HOLD1 (input) → AGENT (process) → HOLD2 (output)")
    print()

    services = [args.service] if args.service else get_all_services()

    if not services:
        print("No services found")
        return 1

    results = []
    for service in services:
        result = verify_service_hold(service)
        results.append(result)

        status = "✓" if result["compliant"] else "✗"
        print(f"{status} {service}")

        if args.verbose:
            print(f"    HOLD1: {'✓' if result['has_hold1'] else '✗'}")
            print(f"    AGENT: {'✓' if result['has_agent'] else '✗'}")
            print(f"    HOLD2: {'✓' if result['has_hold2'] else '✗'}")

        if result["issues"] and args.verbose:
            for issue in result["issues"]:
                print(f"    ⚠ {issue}")

    # Summary
    print()
    compliant = sum(1 for r in results if r["compliant"])
    total = len(results)

    print("=" * 60)
    print(f"Compliant: {compliant}/{total}")

    if compliant == total:
        print("✓ All services follow THE PATTERN")
        return 0
    else:
        print("✗ Some services need HOLD pattern implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
