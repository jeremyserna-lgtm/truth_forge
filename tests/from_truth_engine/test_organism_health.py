"""Health checks for core organism systems."""

from __future__ import annotations

import sys
from pathlib import Path

script_id = "test_organism_health.py"

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).parent))


def main() -> None:
    """Run condensed health checks."""
    print("=" * 70)
    print("TRUTH ENGINE ORGANISM HEALTH CHECK")
    print("=" * 70)
    print()

    # Critical service imports
    try:
        from src.services.central_services.core.error_handling import RecoveryStrategy
        from src.services.central_services.organism_evolution_service import get_organism_evolution_service
        from src.services.central_services.wisdom_direction_service import get_wisdom_direction_service
        from src.services.central_services.reproduction_service.spawner import OrganismSpawner

        _ = RecoveryStrategy()
        _ = get_organism_evolution_service()
        _ = get_wisdom_direction_service()
        _ = OrganismSpawner()
        print("✅ Core services import successfully")
    except Exception as exc:
        print(f"❌ Core service import failure: {exc}")
        sys.exit(1)

    # Schema service availability
    try:
        from src.services.central_services.schema_service.service import SchemaService

        schema_service = SchemaService()
        schemas = schema_service.list_schemas()
        print(f"✅ Schema service available; schemas: {schemas}")
    except Exception as exc:
        print(f"❌ Schema service unavailable: {exc}")
        sys.exit(1)

    print("\nAll health checks complete. Ready for daemon startup and evolution workflows.")


if __name__ == "__main__":
    main()
