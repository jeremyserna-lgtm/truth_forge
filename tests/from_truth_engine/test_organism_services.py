"""Integration tests for organism and business document evolution services."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

script_id = "test_organism_services.py"

# Ensure local imports resolve
sys.path.insert(0, str(Path(__file__).parent))


async def test_organism_evolution_service() -> None:
    """Run organism evolution weekly analysis."""
    print("\n" + "=" * 60)
    print("Testing Organism Evolution Service (Phase 1)")
    print("=" * 60)
    try:
        from src.services.central_services.organism_evolution_service import (
            get_organism_evolution_service,
        )

        service = get_organism_evolution_service()
        result = await service.run_weekly_analysis()
        print(f"Result: {result}")
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Error testing organism service: {exc}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


async def test_business_doc_evolution_service() -> None:
    """Run business document evolution check."""
    print("\n" + "=" * 60)
    print("Testing Business Document Evolution Service (Phase 3)")
    print("=" * 60)
    try:
        from src.services.central_services.business_doc_evolution_service import (
            get_business_doc_evolution_service,
        )

        service = get_business_doc_evolution_service()
        result = await service.run_document_check()
        print(f"Result: {result}")
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Error testing business doc service: {exc}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


async def main() -> None:
    """Run all evolution-related service tests."""
    print(
        """
╔════════════════════════════════════════════════════════════╗
║  ORGANISM EVOLUTION SERVICES TEST SUITE                    ║
║  Phase 1: Organism Evolution Service                       ║
║  Phase 3: Business Document Evolution Service              ║
╚════════════════════════════════════════════════════════════╝
"""
    )

    await test_organism_evolution_service()
    await test_business_doc_evolution_service()

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
