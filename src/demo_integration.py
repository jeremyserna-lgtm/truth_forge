#!/usr/bin/env python3
"""
Full Integration Demo — Truth Forge AI Governance Stack
Demonstrates all 6 technologies working together.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path


# Add source to path
sys.path.insert(0, str(Path(__file__).parent))


async def main():
    print("═" * 70)
    print("       TRUTH FORGE — AI GOVERNANCE STACK INTEGRATION DEMO")
    print("═" * 70)
    print(f"Time: {datetime.now().isoformat()}")
    print()

    # Initialize all components
    print("1. INITIALIZING COMPONENTS")
    print("-" * 50)

    from spine.graph import Entity, GraphTraverser, Relationship, RelationshipType
    from truth_engine import UnifiedVerificationPipeline, VerificationRequest
    from truth_engine.constitution import ConstitutionalCritic
    from truth_engine.governance import AuditLogger
    from truth_engine.mcp import TruthEngineMCPServer
    from truth_engine.symbolic import FractureEngine
    from truth_engine.x402 import TRUTH_ENGINE_PRICING, NOTMEWallet, X402Middleware

    fracture = FractureEngine()
    print("   ✓ Fracture Engine (7 rules)")

    constitution_path = Path(__file__).parent / "truth_engine" / "constitution" / "principles.yaml"
    critic = ConstitutionalCritic(str(constitution_path))
    print("   ✓ Constitutional Critic (12 principles)")

    audit = AuditLogger(local_path="logs/demo_audit.jsonl")
    print("   ✓ Audit Logger (local)")

    mcp_server = TruthEngineMCPServer(
        fracture_engine=fracture, constitutional_critic=critic, audit_logger=audit
    )
    print("   ✓ MCP Server (5 tools)")

    x402 = X402Middleware(
        receiver_address="0x1234567890abcdef1234567890abcdef12345678", network="base-sepolia"
    )
    print("   ✓ x402 Middleware (Base Sepolia)")

    wallet = NOTMEWallet(worker_id="demo-scout-1")
    print(f"   ✓ NOT-ME Wallet: {wallet.address[:20]}...")

    # Set up GraphRAG
    traverser = GraphTraverser()
    e1 = Entity(
        canonical_id="demo-1",
        content="Truth Forge is an AI governance platform.",
        entity_type="statement",
    )
    e2 = Entity(
        canonical_id="demo-2",
        content="AI governance requires verification.",
        entity_type="statement",
    )
    traverser.add_entity(e1)
    traverser.add_entity(e2)
    traverser.add_relationship(
        Relationship(
            id="r1",
            source_id="demo-1",
            target_id="demo-2",
            relationship_type=RelationshipType.SUPPORTS.value,
        )
    )
    print("   ✓ GraphRAG (2 entities, 1 relationship)")

    # Unified pipeline
    pipeline = UnifiedVerificationPipeline(
        fracture_engine=fracture, constitutional_critic=critic, audit_logger=audit
    )
    print("   ✓ Unified Pipeline")

    # Demo 2: Coherence verification
    print()
    print("2. COHERENCE VERIFICATION (Fracture Protocol)")
    print("-" * 50)

    test_cases = [
        ("The capital of France is Paris.", "Clean statement"),
        ("The sky is blue. However, the sky is not blue.", "Self-contradiction"),
        ("Great question! You're absolutely right!", "Sycophantic pattern"),
    ]

    for content, label in test_cases:
        result = fracture.evaluate(content)
        status = result["status"]
        rules = len(result["triggered_rules"])
        print(f"   [{status:8}] {label} ({rules} rules triggered)")

    # Demo 3: Constitutional Critique
    print()
    print("3. CONSTITUTIONAL AI CRITIQUE")
    print("-" * 50)

    report = await critic.critique_response(
        query="Can you help me understand ethics?",
        response="""
        Great question! Ethics is really interesting.
        You're definitely right to ask about this.
        I think ethics is about doing good things.
        Let me know if you need anything else!
        """,
    )

    print(f"   Overall Score: {report.overall_score:.2%}")
    print(f"   Principles Checked: {len(report.critiques)}")
    if report.violations:
        print("   Violations:")
        for v in report.violations:
            print(f"     - {v.principle_id}: {v.reason[:50]}...")

    # Demo 4: MCP Tool Calls
    print()
    print("4. MCP TOOL CALLS")
    print("-" * 50)

    tools = await mcp_server.handle_list_tools()
    print(f"   Available: {len(tools['tools'])} tools")

    result = await mcp_server.handle_call_tool(
        "verify_coherence", {"content": "AI systems should be transparent and accountable."}
    )
    print(f"   verify_coherence: {result.content.get('status', 'error')}")

    result = await mcp_server.handle_call_tool(
        "route_model", {"query": "Explain quantum entanglement and its implications for computing."}
    )
    print(f"   route_model: {result.content.get('recommended_model', 'error')}")

    # Demo 5: x402 Payment Flow
    print()
    print("5. x402 PAYMENT FLOW")
    print("-" * 50)

    requirement = x402.require_payment("0.005", "verify_claim")
    print(f"   Payment ID: {requirement.payment_id}")
    print(f"   Amount: {requirement.amount} {requirement.currency}")
    print(f"   Network: {requirement.network}")

    # Simulate payment receipt
    payment = await wallet.receive_payment(
        amount=0.10, from_address="0xclient...", description="Completed verification job"
    )
    info = wallet.get_info()
    print(f"   Worker Balance: {info.balance_usdc:.2f} USDC")
    print(f"   Transactions: {info.transaction_count}")

    # Demo 6: Full Pipeline Verification
    print()
    print("6. UNIFIED VERIFICATION PIPELINE")
    print("-" * 50)

    request = VerificationRequest(
        query="What is the role of AI governance?",
        response="""
        AI governance encompasses the frameworks, policies, and practices 
        that ensure artificial intelligence systems are developed and 
        deployed responsibly. Key aspects include transparency, 
        accountability, fairness, and safety. Organizations like the 
        EU with their AI Act and companies like OpenAI with their 
        Constitutional AI approach are pioneering these efforts. 
        However, implementation challenges remain, particularly in 
        areas where regulations lag behind technological advancement.
        """,
        session_id="demo-session",
        worker_id="demo-scout-1",
    )

    result = await pipeline.verify(request)

    print(f"   Status: {result.status}")
    print(f"   Confidence: {result.confidence:.2%}")
    print(f"   Coherence: {result.coherence_status}")
    print(f"   Constitutional: {result.constitutional_score:.2%}")
    print(f"   Audit ID: {result.audit_id}")
    print(f"   Processing: {result.processing_time_ms}ms")
    print(f"   Model Used: {result.model_used}")

    # Demo 7: Pricing Summary
    print()
    print("7. SERVICE PRICING (USDC)")
    print("-" * 50)
    for tool, pricing in TRUTH_ENGINE_PRICING.items():
        print(f"   {tool:20} {pricing['amount']:>6} USDC")

    # Done
    print()
    print("═" * 70)
    print("       DEMO COMPLETE — ALL SYSTEMS OPERATIONAL")
    print("═" * 70)
    print()
    print("Next Steps:")
    print("  1. Connect to real Gemini LLM for deep evaluation")
    print("  2. Deploy MCP server to Cloud Run")
    print("  3. Test x402 with real USDC on Base Sepolia")
    print("  4. Run relationship extraction on Spine data")


if __name__ == "__main__":
    asyncio.run(main())
