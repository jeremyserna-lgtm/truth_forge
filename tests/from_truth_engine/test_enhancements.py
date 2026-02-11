#!/usr/bin/env python3
"""
ENHANCEMENT VERIFICATION TEST - Verify all cutting-edge enhancements work.

Tests:
1. All new modules import successfully
2. Services initialize without errors
3. Daemon loads with all endpoints
4. Core functionality works
5. Evolution events integrate
"""
from __future__ import annotations

#!/usr/bin/env python3
"""
ENHANCEMENT VERIFICATION TEST - Verify all cutting-edge enhancements work.

Tests:
1. All new modules import successfully
2. Services initialize without errors
3. Daemon loads with all endpoints
4. Core functionality works
5. Evolution events integrate
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)
script_id = "test_enhancements.py"

import sys
import asyncio
from pathlib import Path

# Add workspace to path
WORKSPACE_ROOT = Path(__file__).parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

def print_header(title: str):
    """Print colored header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_imports():
    """Test all new modules import successfully."""
    print_header("1. Testing Module Imports")

    try:
        from daemon.state_tracking_service import get_state_tracking_service
        print("✅ state_tracking_service")

        from daemon.cognitive_reasoning_engine import get_reasoning_engine
        print("✅ cognitive_reasoning_engine")

        from daemon.care_emotion_system import get_care_system
        print("✅ care_emotion_system")

        from daemon.profitability_tracker import get_profitability_tracker
        print("✅ profitability_tracker")

        from organism_cli import OrganismCLI
        print("✅ organism_cli")

        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_service_initialization():
    """Test services initialize without errors."""
    print_header("2. Testing Service Initialization")

    try:
        from daemon.state_tracking_service import get_state_tracking_service
        service = get_state_tracking_service(WORKSPACE_ROOT)
        print(f"✅ State tracking service initialized")
        print(f"   Organism ID: {service.organism_id}")

        from daemon.cognitive_reasoning_engine import get_reasoning_engine
        engine = get_reasoning_engine()
        print(f"✅ Cognitive reasoning engine initialized")

        from daemon.care_emotion_system import get_care_system
        care = get_care_system(str(WORKSPACE_ROOT / "data"))
        print(f"✅ Care & emotion system initialized")

        from daemon.profitability_tracker import get_profitability_tracker
        tracker = get_profitability_tracker(str(WORKSPACE_ROOT / "data"))
        print(f"✅ Profitability tracker initialized")

        return True
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False

def test_daemon_loading():
    """Test daemon loads with all endpoints."""
    print_header("3. Testing Daemon Loading")

    try:
        from daemon.primitive_engine_daemon import app

        endpoint_count = len(app.routes)
        print(f"✅ Daemon loaded successfully")
        print(f"   Total endpoints: {endpoint_count}")

        # List new endpoints
        new_endpoints = [
            "/organism/state",
            "/organism/metrics",
            "/organism/emotions",
            "/organism/partnerships",
            "/organism/decide",
            "/organism/reason",
            "/organism/reasoning-quality",
        ]

        found_new = []
        for route in app.routes:
            path = getattr(route, 'path', '')
            if any(ep in path for ep in new_endpoints):
                found_new.append(path)

        print(f"\n   New Endpoints Found:")
        for ep in sorted(set(found_new)):
            print(f"   ✅ {ep}")

        if len(found_new) >= 7:
            print(f"\n✅ All new endpoints present ({len(found_new)}/7)")
            return True
        else:
            print(f"\n❌ Only {len(found_new)}/7 new endpoints found")
            return False

    except Exception as e:
        print(f"❌ Daemon loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_functionality():
    """Test core functionality."""
    print_header("4. Testing Core Functionality")

    try:
        from daemon.state_tracking_service import get_state_tracking_service
        from daemon.cognitive_reasoning_engine import get_reasoning_engine
        from daemon.care_emotion_system import get_care_system, InteractionType, EmotionalResponse
        from daemon.profitability_tracker import get_profitability_tracker, CostCategory, ValueCategory

        # Test state tracking
        service = get_state_tracking_service(WORKSPACE_ROOT)
        state = await service.get_state("test_run")
        print(f"✅ State tracking - got phase: {state.phase}")

        metrics = await service.get_metrics()
        print(f"✅ Metrics - energy: {metrics.get('energy', 0):.1f}%")

        # Test reasoning
        engine = get_reasoning_engine()
        decision = await engine.make_decision(
            decision="Test decision",
            relevant_facts=[{"statement": "Test fact", "confidence": 80, "source": "test"}],
            alternatives=["Option A", "Option B"],
            decision_context="Test",
        )
        print(f"✅ Decision making - confidence: {decision.confidence.value}")
        print(f"   Quality score: {decision.decision_quality_score:.1f}/100")

        # Test care system
        care = get_care_system(str(WORKSPACE_ROOT / "data"))
        partnership = await care.create_partnership("Test Partner", "test")
        print(f"✅ Partnership created: {partnership.partnership_id}")

        event = await care.record_care_event(
            partnership_id=partnership.partnership_id,
            interaction_type=InteractionType.SUPPORT,
            description="Test care event",
            effort_hours=1.0,
            estimated_value_usd=100.0,
            our_emotional_response=EmotionalResponse.FULFILLED,
        )
        print(f"✅ Care event recorded: {event.event_id}")

        health = care.get_partnership_health(partnership.partnership_id)
        print(f"✅ Partnership health - care score: {health['metrics']['care_score']:.1f}")

        # Test profitability
        tracker = get_profitability_tracker(str(WORKSPACE_ROOT / "data"))
        tracker.record_cost(
            category=CostCategory.COMPUTE,
            amount_usd=50.0,
            description="Test cost",
        )
        tracker.record_value(
            category=ValueCategory.AUTONOMOUS_VALUE,
            amount_usd=200.0,
            description="Test value",
        )
        snapshot = tracker.get_snapshot("monthly")
        print(f"✅ Profitability - net value: ${snapshot.net_profit:.2f}")
        print(f"   ROI: {snapshot.roi:.2f}x")

        return True

    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_evolution_integration():
    """Test evolution event integration."""
    print_header("5. Testing Evolution Integration")

    try:
        # Evolution ingest is TypeScript, check the file exists
        evolution_file = WORKSPACE_ROOT / "apps" / "common" / "evolution_ingest" / "index.ts"
        if evolution_file.exists():
            print("✅ Evolution ingest module found (TypeScript)")
            print(f"   File: {evolution_file}")
            with open(evolution_file) as f:
                content = f.read()
                if "sendEvolutionEvent" in content:
                    print("✅ sendEvolutionEvent exported")
                if "localhost:8000/input/evolution_event" in content:
                    print("✅ Daemon endpoint configured")
            return True
        else:
            print(f"❌ Evolution ingest file not found: {evolution_file}")
            return False
    except Exception as e:
        print(f"❌ Evolution integration check failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  ENHANCEMENT VERIFICATION TEST SUITE")
    print("="*60)

    results = {
        "Imports": test_imports(),
        "Initialization": test_service_initialization(),
        "Daemon": test_daemon_loading(),
        "Functionality": await test_functionality(),
        "Evolution": test_evolution_integration(),
    }

    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")

    print(f"\n{'='*60}")
    print(f"  Total: {passed}/{total} tests passed")
    print(f"{'='*60}\n")

    if passed == total:
        print("🎉 ALL ENHANCEMENTS VERIFIED - System is ready!")
        return 0
    else:
        print("⚠️  Some tests failed - review above for details")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
