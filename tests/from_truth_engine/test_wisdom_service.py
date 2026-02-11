"""Quick test for Phase 2: Wisdom Direction Service."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

script_id = "test_wisdom_service.py"

sys.path.insert(0, str(Path(__file__).parent))


async def test_wisdom_direction_service() -> None:
    """Test the wisdom direction service."""
    print("\n" + "=" * 60)
    print("Testing Wisdom Direction Service (Phase 2)")
    print("=" * 60)

    try:
        from src.services.central_services.wisdom_direction_service import (
            get_wisdom_direction_service,
        )

        service = get_wisdom_direction_service()
        result = await service.run_monthly_analysis()
        print(f"Result: {result}")
    except Exception as exc:  # noqa: BLE001 - test harness should surface errors
        print(f"❌ Error testing wisdom service: {exc}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


async def main() -> None:
    """Run test."""
    print(
        """
╔════════════════════════════════════════════════════════════╗
║  PHASE 2: WISDOM DIRECTION SERVICE TEST                    ║
║  Extracts patterns and proposes evolution directions       ║
╚════════════════════════════════════════════════════════════╝
"""
    )

    await test_wisdom_direction_service()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
