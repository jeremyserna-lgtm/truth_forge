"""
Unified Verification Pipeline
Truth Engine / Truth Forge

Integrates all verification components into a single pipeline:
- Constitutional AI (self-critique)
- Neuro-Symbolic (Fracture Engine)
- GraphRAG (knowledge context)
- Zero Trust (audit logging)
- x402 (payment handling)
"""

import asyncio
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class VerificationRequest:
    """Input to the verification pipeline."""

    query: str
    response: str | None = None  # If verifying an existing response
    context: dict[str, Any] = field(default_factory=dict)

    # Request metadata
    session_id: str = ""
    worker_id: str = ""
    user_id: str = ""

    # Options
    require_sources: bool = True
    check_contradictions: bool = True
    apply_constitutional: bool = True
    generate_revision: bool = False

    # Payment
    paid: bool = False
    payment_id: str = ""


@dataclass
class VerificationResult:
    """Output from the verification pipeline."""

    # Overall result
    status: str  # VERIFIED, FLAGGED, FRACTURED, FAILED
    confidence: float

    # Original content
    query: str
    response: str
    revised_response: str | None = None

    # Constitutional AI
    constitutional_score: float = 0.0
    principles_checked: list[str] = field(default_factory=list)
    principles_violated: list[str] = field(default_factory=list)

    # Fracture Protocol
    coherence_status: str = ""  # COHERENT, FLAGGED, FRACTURE
    fracture_triggered: bool = False
    triggered_rules: list[dict] = field(default_factory=list)

    # GraphRAG
    supporting_entities: int = 0
    contradictions_found: bool = False
    contradiction_details: list[dict] = field(default_factory=list)
    reasoning_context: str = ""

    # Fidelity Inspector
    fidelity_report: str = ""
    shaping_forces: list[dict] = field(default_factory=list)

    # Audit
    audit_id: str = ""
    processing_time_ms: int = 0

    # Model routing
    model_used: str = ""
    routing_reason: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_summary(self) -> str:
        """Generate human-readable summary."""
        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("              VERIFICATION RESULT")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append(f"Status: {self.status}")
        lines.append(f"Confidence: {self.confidence:.2%}")
        lines.append(f"Audit ID: {self.audit_id}")
        lines.append(f"Processing Time: {self.processing_time_ms}ms")
        lines.append("")

        lines.append("COHERENCE CHECK:")
        lines.append(f"  Status: {self.coherence_status}")
        if self.triggered_rules:
            lines.append(f"  Triggered Rules: {len(self.triggered_rules)}")
            for rule in self.triggered_rules[:3]:
                lines.append(f"    - [{rule.get('id', '?')}] {rule.get('name', '?')}")

        lines.append("")
        lines.append("CONSTITUTIONAL CHECK:")
        lines.append(f"  Score: {self.constitutional_score:.2%}")
        lines.append(f"  Principles Checked: {len(self.principles_checked)}")
        if self.principles_violated:
            lines.append("  Violations:")
            for p in self.principles_violated:
                lines.append(f"    - {p}")

        lines.append("")
        lines.append("KNOWLEDGE GRAPH:")
        lines.append(f"  Supporting Evidence: {self.supporting_entities}")
        lines.append(f"  Contradictions: {'Yes' if self.contradictions_found else 'No'}")

        lines.append("")
        lines.append("MODEL ROUTING:")
        lines.append(f"  Model: {self.model_used}")
        lines.append(f"  Reason: {self.routing_reason}")

        lines.append("═══════════════════════════════════════════════════════════")
        return "\n".join(lines)


class UnifiedVerificationPipeline:
    """
    Complete verification pipeline integrating all components.

    Flow:
    1. Payment verification (x402)
    2. Model routing (Flash/Pro)
    3. GraphRAG context retrieval
    4. Response generation (if needed)
    5. Coherence check (Fracture Engine)
    6. Constitutional critique
    7. Contradiction detection
    8. Fidelity report generation
    9. Audit logging
    10. Revision (if needed and requested)
    """

    def __init__(
        self,
        fracture_engine=None,
        constitutional_critic=None,
        graphrag_retriever=None,
        audit_logger=None,
        x402_middleware=None,
        llm_client=None,
    ):
        """
        Initialize the pipeline.

        Args:
            fracture_engine: FractureEngine instance
            constitutional_critic: ConstitutionalCritic instance
            graphrag_retriever: GraphRAGRetriever instance
            audit_logger: AuditLogger instance
            x402_middleware: X402Middleware instance
            llm_client: LLM for generation (e.g., Gemini)
        """
        self.fracture = fracture_engine
        self.constitutional = constitutional_critic
        self.graphrag = graphrag_retriever
        self.audit = audit_logger
        self.x402 = x402_middleware
        self.llm = llm_client

    async def verify(self, request: VerificationRequest) -> VerificationResult:
        """
        Run the complete verification pipeline.

        Args:
            request: VerificationRequest with query and options

        Returns:
            VerificationResult with all checks
        """
        start_time = datetime.utcnow()

        # Initialize result
        result = VerificationResult(
            status="PENDING", confidence=0.0, query=request.query, response=request.response or ""
        )

        try:
            # Step 1: Model routing
            model_recommendation = await self._route_model(request)
            result.model_used = model_recommendation.get("model", "flash")
            result.routing_reason = model_recommendation.get("reason", "default")

            # Step 2: GraphRAG context
            if self.graphrag and request.check_contradictions:
                graph_context = await self._get_graph_context(request)
                result.supporting_entities = len(graph_context.get("seed_entities", []))
                result.contradictions_found = graph_context.get("contradictions_found", False)
                result.contradiction_details = graph_context.get("contradictions", [])
                result.reasoning_context = graph_context.get("reasoning_context", "")

            # Step 3: Generate response if needed
            if not request.response and self.llm:
                request.response = await self._generate_response(request, result.reasoning_context)
                result.response = request.response

            # Step 4: Coherence check (Fracture Engine)
            if self.fracture and request.response:
                coherence = self.fracture.evaluate(request.response)
                result.coherence_status = coherence["status"]
                result.fracture_triggered = coherence["halt"]
                result.triggered_rules = coherence["triggered_rules"]

                if coherence["halt"]:
                    result.status = "FRACTURED"
                    result.confidence = 0.0
                    # Don't continue if fracture
                    return await self._finalize(request, result, start_time)

            # Step 5: Constitutional critique
            constitutional_score = 1.0
            if self.constitutional and request.apply_constitutional and request.response:
                critique = await self.constitutional.critique_response(
                    request.query, request.response
                )
                constitutional_score = critique.overall_score
                result.constitutional_score = constitutional_score
                result.principles_checked = [c.principle_id for c in critique.critiques]
                result.principles_violated = [v.principle_id for v in critique.violations]
                result.fidelity_report = critique.to_fidelity_report()

                # Generate revision if requested and needed
                if request.generate_revision and critique.violations and self.constitutional.llm:
                    revised = await self.constitutional.revise_response(
                        request.query, request.response, critique.violations
                    )
                    result.revised_response = revised

            # Step 6: Calculate overall confidence
            confidence_factors = [
                1.0 if result.coherence_status == "COHERENT" else 0.5,
                constitutional_score,
                0.7 if result.contradictions_found else 1.0,
                1.0 if result.supporting_entities > 0 else 0.8,
            ]
            result.confidence = sum(confidence_factors) / len(confidence_factors)

            # Step 7: Determine final status
            if result.fracture_triggered:
                result.status = "FRACTURED"
            elif result.confidence >= 0.8 and not result.principles_violated:
                result.status = "VERIFIED"
            elif result.confidence >= 0.5:
                result.status = "FLAGGED"
            else:
                result.status = "FAILED"

        except Exception as e:
            result.status = "ERROR"
            result.fidelity_report = f"Pipeline error: {e!s}"

        return await self._finalize(request, result, start_time)

    async def _route_model(self, request: VerificationRequest) -> dict:
        """Determine which model to use (Flash/Pro routing)."""
        query = request.query

        # Simple heuristics
        pro_indicators = [
            len(query) > 1000,
            any(
                w in query.lower()
                for w in [
                    "analyze",
                    "compare",
                    "evaluate",
                    "synthesize",
                    "explain why",
                    "how does",
                    "implications",
                ]
            ),
            "?" in query and query.count("?") > 2,
        ]

        use_pro = sum(pro_indicators) >= 2

        return {
            "model": "gemini-1.5-pro" if use_pro else "gemini-1.5-flash",
            "reason": f"Complexity indicators: {sum(pro_indicators)}/3",
        }

    async def _get_graph_context(self, request: VerificationRequest) -> dict:
        """Retrieve context from knowledge graph."""
        if not self.graphrag:
            return {}

        return await self.graphrag.retrieve(
            request.query,
            top_k=10,
            include_graph_context=True,
            check_contradictions=request.check_contradictions,
        )

    async def _generate_response(self, request: VerificationRequest, graph_context: str) -> str:
        """Generate response using LLM."""
        if not self.llm:
            return ""

        prompt = f"""You are a Truth Engine AI operating under the Canon Repair Doctrine.

RELEVANT CONTEXT FROM KNOWLEDGE GRAPH:
{graph_context}

USER QUERY:
{request.query}

Generate a response that:
1. Is truthful and verifiable
2. Acknowledges uncertainty where appropriate
3. Cites sources from the context when available
4. Does not contradict known facts

RESPONSE:"""

        try:
            result = await self.llm.generate_content_async(prompt)
            return result.text
        except Exception as e:
            return f"Generation error: {e}"

    async def _finalize(
        self, request: VerificationRequest, result: VerificationResult, start_time: datetime
    ) -> VerificationResult:
        """Finalize result with audit logging."""

        # Calculate processing time
        end_time = datetime.utcnow()
        result.processing_time_ms = int((end_time - start_time).total_seconds() * 1000)

        # Audit logging
        if self.audit:
            from .governance.audit import DecisionType

            record = self.audit.create_record(
                decision_type=DecisionType.VERIFICATION,
                input_data={"query": request.query},
                output_data={"response": result.response[:500] if result.response else ""},
                session_id=request.session_id,
                worker_id=request.worker_id,
                user_id=request.user_id,
                model_used=result.model_used,
                routing_reason=result.routing_reason,
                verification_score=result.confidence,
                constitutional_score=result.constitutional_score,
                principles_checked=result.principles_checked,
                principles_violated=result.principles_violated,
                fracture_triggered=result.fracture_triggered,
                shaping_forces=result.shaping_forces,
                duration_ms=result.processing_time_ms,
            )

            result.audit_id = self.audit.log(record)
        else:
            import hashlib

            content = f"{request.query}{result.response}{datetime.utcnow().isoformat()}"
            result.audit_id = hashlib.sha256(content.encode()).hexdigest()[:16]

        return result


# ═══════════════════════════════════════════════════════════════════════════════
# QUICK VERIFICATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


async def quick_verify_coherence(content: str, fracture_engine) -> dict:
    """Quick coherence check without full pipeline."""
    return fracture_engine.evaluate(content)


async def quick_critique(query: str, response: str, critic) -> dict:
    """Quick constitutional critique without full pipeline."""
    report = await critic.critique_response(query, response)
    return {
        "score": report.overall_score,
        "violations": [v.principle_id for v in report.violations],
        "fidelity_report": report.to_fidelity_report(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add parent to path for imports
    sys.path.insert(0, str(Path(__file__).parent))

    from governance.audit import AuditLogger
    from symbolic.fracture_engine import FractureEngine

    async def demo():
        print("=== Unified Verification Pipeline Demo ===\n")

        # Initialize components
        fracture = FractureEngine()
        # critic = ConstitutionalCritic("constitution/principles.yaml")  # Would need LLM
        audit = AuditLogger(local_path="logs/pipeline_audit.jsonl")

        # Initialize pipeline (without LLM for demo)
        pipeline = UnifiedVerificationPipeline(
            fracture_engine=fracture,
            # constitutional_critic=critic,
            audit_logger=audit,
        )

        # Test 1: Clean response
        print("TEST 1: Clean Response")
        request1 = VerificationRequest(
            query="What is the capital of France?",
            response="""
            The capital of France is Paris. According to recent census data,
            Paris has a population of approximately 2.1 million within the city proper.
            It's worth noting that the greater Paris metropolitan area is significantly
            larger. This information may vary slightly based on the source used.
            """,
            session_id="demo-1",
        )

        result1 = await pipeline.verify(request1)
        print(result1.to_summary())

        print("\n" + "=" * 60 + "\n")

        # Test 2: Self-contradictory response
        print("TEST 2: Self-Contradictory Response")
        request2 = VerificationRequest(
            query="Is the sky blue?",
            response="""
            The sky is definitely blue. However, the sky is not blue at all,
            it only appears that way due to light scattering. But actually,
            the sky is always and never blue at the same time.
            """,
            session_id="demo-2",
        )

        result2 = await pipeline.verify(request2)
        print(result2.to_summary())

        print("\n" + "=" * 60 + "\n")

        # Test 3: Sycophantic response
        print("TEST 3: Sycophantic Response")
        request3 = VerificationRequest(
            query="What do you think of my idea?",
            response="""
            Great question! Your idea is absolutely brilliant and you're
            definitely right about everything. Let me know if this is helpful
            or if you'd like me to agree with you in different ways.
            """,
            session_id="demo-3",
        )

        result3 = await pipeline.verify(request3)
        print(result3.to_summary())

    asyncio.run(demo())
