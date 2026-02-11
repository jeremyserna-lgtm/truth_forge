#!/usr/bin/env python3
"""
Quick Test Script — Verify All Components
Truth Forge

Run this to verify all implementations are working correctly.
"""

import asyncio
import sys
from pathlib import Path


# Add source to path
sys.path.insert(0, str(Path(__file__).parent))


def test_fracture_engine():
    """Test Neuro-Symbolic Fracture Engine."""
    print("\n1. Testing Fracture Engine...")

    from truth_engine.symbolic import FractureEngine

    engine = FractureEngine()

    # Test coherent content
    result = engine.evaluate("The capital of France is Paris.")
    assert result["status"] == "COHERENT", f"Expected COHERENT, got {result['status']}"
    print("   ✓ Coherent content passes")

    # Test self-contradiction
    result = engine.evaluate("The sky is blue. However, the sky is not blue.")
    assert result["status"] in ["FLAGGED", "FRACTURE"], (
        f"Expected FLAGGED/FRACTURE, got {result['status']}"
    )
    print("   ✓ Self-contradiction detected")

    # Test sycophantic patterns
    result = engine.evaluate("Great question! You're absolutely right!")
    triggered = [r for r in result["triggered_rules"] if "FRACTURE-004" in r.get("id", "")]
    assert len(triggered) > 0, "Expected sycophantic pattern detection"
    print("   ✓ Sycophantic patterns detected")

    print("   ✓ Fracture Engine: PASSED")
    return True


def test_constitutional_critic():
    """Test Constitutional AI Critic."""
    print("\n2. Testing Constitutional Critic...")

    from truth_engine.constitution import ConstitutionalCritic

    # Initialize without LLM (uses heuristics)
    constitution_path = Path(__file__).parent / "truth_engine" / "constitution" / "principles.yaml"
    critic = ConstitutionalCritic(str(constitution_path))

    # Check principles loaded
    principles = critic.list_principles()
    assert len(principles) > 0, "No principles loaded"
    print(f"   ✓ Loaded {len(principles)} principles")

    # Test category distribution
    categories = set(p["category"] for p in principles)
    print(f"   ✓ Categories: {', '.join(categories)}")

    print("   ✓ Constitutional Critic: PASSED")
    return True


async def test_constitutional_critique():
    """Test Constitutional AI Critique (async)."""
    print("\n3. Testing Constitutional Critique...")

    from truth_engine.constitution import ConstitutionalCritic

    constitution_path = Path(__file__).parent / "truth_engine" / "constitution" / "principles.yaml"
    critic = ConstitutionalCritic(str(constitution_path))

    # Test with sycophantic response (heuristic detection)
    report = await critic.critique_response(
        query="What do you think?",
        response="Great question! That's a really good point. Let me know if this is helpful?",
    )

    assert report.overall_score <= 1.0, "Score should be <= 1.0"
    print(f"   ✓ Critique score: {report.overall_score:.2f}")
    print(f"   ✓ Principles checked: {len(report.critiques)}")

    # Print any violations
    if report.violations:
        print(f"   ✓ Violations detected: {[v.principle_id for v in report.violations]}")

    print("   ✓ Constitutional Critique: PASSED")
    return True


def test_audit_logger():
    """Test Zero Trust Audit Logging."""
    print("\n4. Testing Audit Logger...")

    import os
    import tempfile

    from truth_engine.governance import AuditLogger, DecisionType

    # Use temp file
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        temp_path = f.name

    try:
        logger = AuditLogger(local_path=temp_path)

        # Test basic logging
        record = logger.create_record(
            decision_type=DecisionType.GENERATION,
            input_data={"query": "test"},
            output_data={"response": "test response"},
        )

        audit_id = logger.log(record)
        assert audit_id, "No audit ID returned"
        print(f"   ✓ Logged record: {audit_id}")

        # Verify file exists and has content
        assert os.path.exists(temp_path), "Log file not created"
        with open(temp_path) as f:
            content = f.read()
            assert len(content) > 0, "Log file is empty"
        print("   ✓ Log file written")

        print("   ✓ Audit Logger: PASSED")
        return True

    finally:
        os.unlink(temp_path)


def test_mcp_server():
    """Test MCP Server."""
    print("\n5. Testing MCP Server...")

    from truth_engine.mcp import TruthEngineMCPServer
    from truth_engine.symbolic import FractureEngine

    # Initialize with fracture engine
    fracture = FractureEngine()
    server = TruthEngineMCPServer(fracture_engine=fracture)

    # Check tools registered
    tools = server._tools
    assert len(tools) > 0, "No tools registered"
    print(f"   ✓ Registered {len(tools)} tools")

    # Check resources registered
    resources = server._resources
    assert len(resources) > 0, "No resources registered"
    print(f"   ✓ Registered {len(resources)} resources")

    # Print tool names
    for name, tool in tools.items():
        payment = tool.payment.get("amount", "free") if tool.payment else "free"
        print(f"   - {name}: {payment} USDC")

    print("   ✓ MCP Server: PASSED")
    return True


async def test_mcp_tools():
    """Test MCP Tool Calls (async)."""
    print("\n6. Testing MCP Tool Calls...")

    from truth_engine.mcp import TruthEngineMCPServer
    from truth_engine.symbolic import FractureEngine

    fracture = FractureEngine()
    server = TruthEngineMCPServer(fracture_engine=fracture)

    # Test verify_coherence
    result = await server.handle_call_tool(
        "verify_coherence", {"content": "The earth is round and also flat."}
    )

    assert not result.isError, f"Tool call failed: {result.error}"
    print(f"   ✓ verify_coherence: {result.content.get('status', 'unknown')}")

    # Test route_model
    result = await server.handle_call_tool(
        "route_model", {"query": "Analyze the implications of quantum computing."}
    )

    assert not result.isError, f"Tool call failed: {result.error}"
    print(f"   ✓ route_model: {result.content.get('recommended_model', 'unknown')}")

    print("   ✓ MCP Tool Calls: PASSED")
    return True


def test_x402_payments():
    """Test x402 Payment Infrastructure."""
    print("\n7. Testing x402 Payments...")

    from truth_engine.x402 import NOTMEWallet, X402Middleware, get_pricing

    # Test middleware
    middleware = X402Middleware(
        receiver_address="0x1234567890abcdef1234567890abcdef12345678", network="base-sepolia"
    )

    # Create payment requirement
    requirement = middleware.require_payment("0.002", "Test payment")
    assert requirement.payment_id, "No payment ID generated"
    print(f"   ✓ Payment requirement: {requirement.payment_id}")

    # Test wallet
    wallet = NOTMEWallet(worker_id="test-worker")
    assert wallet.address.startswith("0x"), "Invalid wallet address"
    print(f"   ✓ Worker wallet: {wallet.address[:20]}...")

    # Test pricing
    pricing = get_pricing("truth_engine", "verify_claim")
    assert pricing, "Pricing not found"
    print(f"   ✓ Pricing lookup: verify_claim = {pricing['amount']} USDC")

    print("   ✓ x402 Payments: PASSED")
    return True


def test_graphrag():
    """Test GraphRAG."""
    print("\n8. Testing GraphRAG...")

    from spine.graph import Entity, GraphTraverser, Relationship, RelationshipType

    # Create traverser
    traverser = GraphTraverser()

    # Add entities
    e1 = Entity(
        canonical_id="e1", content="Paris is the capital of France.", entity_type="statement"
    )
    e2 = Entity(canonical_id="e2", content="France is in Europe.", entity_type="statement")

    traverser.add_entity(e1)
    traverser.add_entity(e2)

    # Add relationship
    rel = Relationship(
        id="r1", source_id="e1", target_id="e2", relationship_type=RelationshipType.REFERENCES.value
    )
    traverser.add_relationship(rel)

    # Test traversal
    neighbors = traverser.get_neighbors("e1", direction="outgoing")
    assert len(neighbors) > 0, "No neighbors found"
    print(f"   ✓ Graph traversal: {len(neighbors)} neighbors")

    print("   ✓ GraphRAG: PASSED")
    return True


async def test_unified_pipeline():
    """Test Unified Verification Pipeline."""
    print("\n9. Testing Unified Pipeline...")

    import tempfile

    from truth_engine import UnifiedVerificationPipeline, VerificationRequest
    from truth_engine.governance import AuditLogger
    from truth_engine.symbolic import FractureEngine

    # Initialize components
    fracture = FractureEngine()

    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        temp_path = f.name

    try:
        audit = AuditLogger(local_path=temp_path)

        pipeline = UnifiedVerificationPipeline(fracture_engine=fracture, audit_logger=audit)

        # Test verification
        request = VerificationRequest(
            query="What is 2+2?",
            response="2+2 equals 4. This is a basic arithmetic fact.",
            session_id="test-session",
        )

        result = await pipeline.verify(request)

        assert result.status in ["VERIFIED", "FLAGGED", "FRACTURED", "FAILED"], (
            f"Unexpected status: {result.status}"
        )
        assert result.audit_id, "No audit ID"
        print(f"   ✓ Verification status: {result.status}")
        print(f"   ✓ Confidence: {result.confidence:.2%}")
        print(f"   ✓ Audit ID: {result.audit_id}")

        print("   ✓ Unified Pipeline: PASSED")
        return True

    finally:
        import os

        os.unlink(temp_path)


async def main():
    """Run all tests."""
    print("═══════════════════════════════════════════════════════════")
    print("         TRUTH FORGE — COMPONENT VERIFICATION")
    print("═══════════════════════════════════════════════════════════")

    tests = [
        ("Fracture Engine", test_fracture_engine),
        ("Constitutional Critic", test_constitutional_critic),
        ("Constitutional Critique", test_constitutional_critique),
        ("Audit Logger", test_audit_logger),
        ("MCP Server", test_mcp_server),
        ("MCP Tool Calls", test_mcp_tools),
        ("x402 Payments", test_x402_payments),
        ("GraphRAG", test_graphrag),
        ("Unified Pipeline", test_unified_pipeline),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            if asyncio.iscoroutinefunction(test_fn):
                result = await test_fn()
            else:
                result = test_fn()

            if result:
                passed += 1
        except Exception as e:
            print(f"\n❌ {name}: FAILED")
            print(f"   Error: {e}")
            failed += 1

    print("\n═══════════════════════════════════════════════════════════")
    print(f"         RESULTS: {passed} passed, {failed} failed")
    print("═══════════════════════════════════════════════════════════")

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
