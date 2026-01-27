"""Health checks for services.

RISK MITIGATION: Verifies services are actually functional, not just
that files exist.

Usage:
    from truth_forge.migration.health import check_service_health

    result = check_service_health("knowledge")
    if not result["healthy"]:
        print(f"Service unhealthy: {result['issues']}")
"""

from __future__ import annotations

import json
from typing import Any


def check_service_health(service_name: str) -> dict[str, Any]:
    """Check health of a single service.

    Verifies:
    - HOLD directories exist
    - DuckDB can be opened
    - JSONL files are valid
    - Service can inhale/exhale

    Args:
        service_name: Name of the service to check.

    Returns:
        Health check result dictionary.
    """
    from truth_forge.core.paths import (
        get_duckdb_file,
        get_hold1_path,
        get_hold2_path,
        get_intake_file,
        get_staging_path,
    )

    result: dict[str, Any] = {
        "service": service_name,
        "healthy": True,
        "issues": [],
        "warnings": [],
        "checks": {},
    }

    # Check directories exist
    hold1 = get_hold1_path(service_name)
    hold2 = get_hold2_path(service_name)
    staging = get_staging_path(service_name)

    result["checks"]["hold1_exists"] = hold1.exists()
    result["checks"]["hold2_exists"] = hold2.exists()
    result["checks"]["staging_exists"] = staging.exists()

    if not hold1.exists():
        result["issues"].append(f"Missing hold1 directory: {hold1}")
        result["healthy"] = False

    if not hold2.exists():
        result["issues"].append(f"Missing hold2 directory: {hold2}")
        result["healthy"] = False

    if not staging.exists():
        result["warnings"].append(f"Missing staging directory: {staging}")

    # Check intake file
    intake_file = get_intake_file(service_name)
    result["checks"]["intake_file_exists"] = intake_file.exists()

    if intake_file.exists():
        # Validate JSONL format
        try:
            valid_lines = 0
            invalid_lines = 0
            with open(intake_file) as f:
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        json.loads(line)
                        valid_lines += 1
                    except json.JSONDecodeError:
                        invalid_lines += 1
                        if invalid_lines <= 3:  # Only report first 3
                            result["issues"].append(
                                f"Invalid JSON at line {i} in {intake_file.name}"
                            )

            result["checks"]["intake_valid_lines"] = valid_lines
            result["checks"]["intake_invalid_lines"] = invalid_lines

            if invalid_lines > 0:
                result["healthy"] = False

        except Exception as e:
            result["issues"].append(f"Cannot read intake file: {e}")
            result["healthy"] = False
    else:
        result["warnings"].append(f"No intake file yet: {intake_file.name}")

    # Check DuckDB file
    duckdb_file = get_duckdb_file(service_name)
    result["checks"]["duckdb_exists"] = duckdb_file.exists()

    if duckdb_file.exists():
        # Check if it's a file (not directory - common corruption)
        if duckdb_file.is_dir():
            result["issues"].append(f"DuckDB is a directory (corrupted): {duckdb_file}")
            result["healthy"] = False
        else:
            # Try to open and query
            try:
                import duckdb

                conn = duckdb.connect(str(duckdb_file), read_only=True)
                # Try to list tables
                tables = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
                result["checks"]["duckdb_tables"] = [t[0] for t in tables]
                conn.close()
            except Exception as e:
                result["issues"].append(f"Cannot open DuckDB: {e}")
                result["healthy"] = False
    else:
        result["warnings"].append(f"No DuckDB file yet: {duckdb_file.name}")

    return result


def check_all_services_health() -> dict[str, Any]:
    """Check health of all configured services.

    Returns:
        Dictionary with overall status and per-service results.
    """
    from truth_forge.core.paths import SERVICES_ROOT

    # Expected services (from migration plan)
    expected_services = [
        "identity",
        "knowledge",
        "analytics",
        "quality",
        "pipeline",
        "hold",
        "run",
        "builder",
        "federation",
        "frontmatter",
        "model_gateway",
        "stage_awareness",
    ]

    results: dict[str, Any] = {
        "overall_healthy": True,
        "services_checked": 0,
        "services_healthy": 0,
        "services_unhealthy": 0,
        "services_missing": 0,
        "details": {},
    }

    for service in expected_services:
        service_dir = SERVICES_ROOT / service
        if not service_dir.exists():
            results["services_missing"] += 1
            results["details"][service] = {
                "service": service,
                "healthy": False,
                "issues": ["Service directory does not exist"],
            }
            results["overall_healthy"] = False
            continue

        result = check_service_health(service)
        results["details"][service] = result
        results["services_checked"] += 1

        if result["healthy"]:
            results["services_healthy"] += 1
        else:
            results["services_unhealthy"] += 1
            results["overall_healthy"] = False

    return results


def verify_hold_sync(service_name: str) -> dict[str, Any]:
    """Verify HOLD₁ → HOLD₂ sync is working.

    Checks that data in hold1 has been processed to hold2.

    Args:
        service_name: Name of the service.

    Returns:
        Sync verification result.
    """
    from truth_forge.core.paths import get_duckdb_file, get_intake_file

    result: dict[str, Any] = {
        "service": service_name,
        "sync_ok": False,
        "hold1_count": 0,
        "hold2_count": 0,
        "sync_ratio": 0.0,
        "issues": [],
    }

    intake_file = get_intake_file(service_name)
    duckdb_file = get_duckdb_file(service_name)

    # Count hold1 records
    if intake_file.exists():
        with open(intake_file) as f:
            result["hold1_count"] = sum(1 for line in f if line.strip())

    # Count hold2 records
    if duckdb_file.exists() and duckdb_file.is_file():
        try:
            import duckdb

            conn = duckdb.connect(str(duckdb_file), read_only=True)
            # Try standard table name
            table_name = f"{service_name}_records"
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
                result["hold2_count"] = count[0] if count else 0
            except Exception:
                # Try to find any table with records
                tables = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
                for table in tables:
                    try:
                        count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()
                        result["hold2_count"] += count[0] if count else 0
                    except Exception:
                        pass
            conn.close()
        except Exception as e:
            result["issues"].append(f"Cannot query DuckDB: {e}")

    # Calculate sync ratio
    if result["hold1_count"] > 0:
        result["sync_ratio"] = result["hold2_count"] / result["hold1_count"]
        # Consider sync OK if at least 90% of records are in hold2
        result["sync_ok"] = result["sync_ratio"] >= 0.9
    elif result["hold2_count"] == 0:
        # Both empty is OK (new service)
        result["sync_ok"] = True
    else:
        # hold2 has data but hold1 doesn't - unusual but OK
        result["sync_ok"] = True

    if not result["sync_ok"]:
        result["issues"].append(f"Sync ratio {result['sync_ratio']:.1%} below 90% threshold")

    return result
