"""ExplorerService - Autonomous exploration with full cognitive architecture.

Integrates:
- THE PATTERN: HOLD₁ → AGENT → HOLD₂
- Total Resonance tracking
- Struggle Filter (keep swimming, discard drowning)
- Stage 5 cognitive compliance
- Full Not-Me type system (CognitiveStage, ThoughtType, PantheonMode, EmotionalState)
- Service ecosystem (KnowledgeService, RelationshipService, CognitionService)

THE PATTERN:
- HOLD₁: ExplorationConfig
- AGENT: Exploration Loop (tool invocation → classification → filtering)
- HOLD₂: ExplorationReport with InsightAtoms

MOLT LINEAGE:
- Source: New creation for autonomous data exploration
- Version: 1.0.0
- Date: 2026-02-01
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from truth_forge.schema.event import Event, EventType, create_event
from truth_forge.services.base import BaseService
from truth_forge.services.factory import get_service, register_service

from .context import (
    EXPLORER_CONTEXT_LIMIT,
    EXPLORER_FALLBACK_ORDER,
    EXPLORER_MODEL,
    ContextManager,
    SessionMemory,
    classify_struggle_state,
    get_explorer_context,
)
from .models import (
    ExplorationConfig,
    ExplorationDepth,
    ExplorationReport,
    Finding,
    Pattern,
    StruggleState,
    ToolResult,
)
from .prompts import (
    format_cognitive_classification_prompt,
    format_synthesis_prompt,
    format_tool_selection_prompt,
)
from .session import ExplorationSession
from .tool_bridge import ToolBridge


if TYPE_CHECKING:
    from truth_forge.gateway import ModelGateway

logger = logging.getLogger(__name__)


# =============================================================================
# COST GOVERNANCE (From KnowledgeService pattern)
# =============================================================================

MAX_COST_PER_SESSION: float = 0.50  # Hard limit per session
MAX_CALLS_PER_SESSION: int = 100  # Max LLM calls per session


# =============================================================================
# EXPLORER SERVICE
# =============================================================================


@register_service()
class ExplorerService(BaseService):
    """Autonomous exploration with full cognitive architecture integration.

    Implements:
    - THE PATTERN: HOLD₁ → AGENT → HOLD₂
    - Cognitive Architecture: Stage 5 baseline, emotional metadata
    - Total Resonance: Track ontological alignment
    - Struggle Filter: Keep swimming, discard drowning
    """

    service_name = "explorer"

    def __init__(self) -> None:
        """Initialize ExplorerService."""
        super().__init__()

        # Lazy-loaded in on_startup()
        self._gateway: ModelGateway | None = None
        self._tool_bridge: ToolBridge | None = None
        self._knowledge: Any = None
        self._relationship: Any = None
        self._cognition: Any = None
        self._mediator: Any = None

        # Cost governance
        self._session_cost: float = 0.0
        self._session_calls: int = 0

        # Context management
        self._context_manager: ContextManager | None = None

        # Current session tracking
        self._current_session_id: str | None = None

        # Knowledge context cache (instance-level to avoid memory leaks)
        self._knowledge_cache: dict[str, dict[str, Any]] = {}

    def on_startup(self) -> None:
        """Initialize with full service integration."""
        self._tool_bridge = ToolBridge()
        self._context_manager = ContextManager(get_explorer_context())

        # Gateway (lazy loaded on first use)
        try:
            from truth_forge.gateway import get_gateway

            self._gateway = get_gateway()
        except ImportError:
            self._logger.warning(
                "gateway_not_available",
                extra={"fallback": "direct_ollama"},
            )

        # Service dependencies (lazy-loaded, breaks circular deps)
        try:
            self._knowledge = get_service("knowledge")
        except Exception as e:
            self._logger.warning(
                "knowledge_service_not_available",
                extra={"error": str(e)},
            )

        try:
            self._relationship = get_service("relationship")
        except Exception as e:
            self._logger.warning(
                "relationship_service_not_available",
                extra={"error": str(e)},
            )

        try:
            self._cognition = get_service("cognition")
        except Exception as e:
            self._logger.warning(
                "cognition_service_not_available",
                extra={"error": str(e)},
            )

        try:
            self._mediator = get_service("mediator")
        except Exception as e:
            self._logger.warning(
                "mediator_service_not_available",
                extra={"error": str(e)},
            )

        self._logger.info(
            "explorer_startup",
            extra={
                "tools": len(self._tool_bridge.get_tool_names()) if self._tool_bridge else 0,
                "model": EXPLORER_MODEL,
                "context_limit": EXPLORER_CONTEXT_LIMIT,
                "cognitive_baseline": "Stage_5",
            },
        )

    def on_shutdown(self) -> None:
        """Cleanup and report session stats."""
        self._logger.info(
            "explorer_shutdown",
            extra={
                "session_cost": self._session_cost,
                "session_calls": self._session_calls,
            },
        )

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Process single config (BaseService interface).

        Args:
            record: ExplorationConfig as dict.

        Returns:
            ExplorationReport as dict.
        """
        config = ExplorationConfig(**record)
        report = self.explore(config)
        return report.model_dump()

    def get_session_stats(self) -> dict[str, Any]:
        """Return session cost/call statistics.

        Returns:
            Dictionary with cost/call stats.
        """
        return {
            "cost": self._session_cost,
            "calls": self._session_calls,
            "remaining_budget": MAX_COST_PER_SESSION - self._session_cost,
            "remaining_calls": MAX_CALLS_PER_SESSION - self._session_calls,
            "model": EXPLORER_MODEL,
            "context_limit": EXPLORER_CONTEXT_LIMIT,
        }

    def reset_session_stats(self) -> None:
        """Reset session cost/call counters."""
        self._session_cost = 0.0
        self._session_calls = 0

    # =========================================================================
    # MAIN EXPLORATION METHOD
    # =========================================================================

    def explore(self, config: ExplorationConfig) -> ExplorationReport:
        """Run autonomous exploration with full cognitive architecture integration.

        THE PATTERN:
        - HOLD₁: ExplorationConfig
        - AGENT: Exploration Loop
        - HOLD₂: ExplorationReport

        Args:
            config: Exploration configuration.

        Returns:
            ExplorationReport with findings, patterns, and resonance metrics.
        """
        # Reset session stats for new exploration
        self.reset_session_stats()

        # Create session event (centralized ID - NOT uuid4)
        session_event = create_event(
            event_type=EventType.PROCESSING_STARTED,
            aggregate_type="explorer",
            data={"config": config.model_dump()},
            service=self.service_name,
        )

        self._current_session_id = session_event.id

        # HOLD₁: Record config
        self.inhale(
            data=config.model_dump(),
            event_type=EventType.PROCESSING_STARTED,
            correlation_id=session_event.metadata.correlation_id,
        )

        # Get trust-based depth adjustment
        adjusted_depth = self._get_trust_adjusted_depth(config)

        # Initialize session
        session = ExplorationSession(
            id=session_event.id,
            correlation_id=session_event.metadata.correlation_id,
            config=config,
            started_at=datetime.now(UTC),
        )

        # Initialize memory
        memory = SessionMemory(
            max_findings=self._context_manager.calculate_iteration_budget().max_findings_context
            if self._context_manager
            else 25
        )

        # Publish start event
        self._publish_event(
            "governance.record",
            {
                "event_type": EventType.PROCESSING_STARTED.value,
                "service": self.service_name,
                "session_id": session.id,
                "config": config.model_dump(),
            },
        )

        self._logger.info(
            "exploration_started",
            extra={
                "session_id": session.id,
                "correlation_id": session.correlation_id,
                "iterations": config.iterations,
                "focus": config.focus_area,
                "adjusted_depth": adjusted_depth.value,
            },
        )

        try:
            for iteration in range(config.iterations):
                # Cost governance check
                if not self._check_cost_limit(estimated_cost=0.01):
                    self._logger.warning(
                        "exploration_stopped_cost_limit",
                        extra={"session_id": session.id},
                    )
                    session.request_stop("Cost limit reached")
                    break

                session.current_iteration = iteration

                # Run iteration
                self._run_iteration(
                    session=session,
                    iteration=iteration,
                    session_event=session_event,
                    memory=memory,
                    config=config,
                )

                if session.should_stop:
                    break

            # Generate synthesis
            synthesis = self._generate_synthesis(session)
            patterns = self._extract_patterns(session, session_event)

            # Create completion event
            completion_event = session_event.child_event(
                event_type=EventType.PROCESSING_COMPLETED,
                data={"iterations": session.current_iteration + 1},
            )

            # Build report
            report = ExplorationReport(
                session_id=session.id,
                config=config,
                started_at=session.started_at,
                completed_at=datetime.now(UTC),
                iterations_completed=session.current_iteration + 1,
                findings=session.findings,
                findings_discarded=session.discarded_count,
                patterns_discovered=patterns,
                resonance_metrics=session.resonance_metrics.to_dict(),
                total_resonance_score=session.resonance_metrics.total_resonance_score,
                is_exist_now_ready=session.resonance_metrics.is_exist_now_ready,
                recommendations=synthesis.get("recommendations", []),
                synthesis=synthesis.get("narrative", ""),
                total_cost=self._session_cost,
                metadata=completion_event.metadata,
            )

            # HOLD₂: Record report
            self.exhale(
                processed_data=report.model_dump(),
                source_event=session_event,
            )

            # Publish discoveries
            self._publish_discoveries(session, report)

            self._logger.info(
                "exploration_completed",
                extra={
                    "session_id": session.id,
                    "iterations": report.iterations_completed,
                    "findings": len(report.findings),
                    "patterns": len(report.patterns_discovered),
                    "resonance_score": report.total_resonance_score,
                    "cost": report.total_cost,
                },
            )

            return report

        except Exception as e:
            self._write_error_signal(
                {"session_id": session.id, "config": config.model_dump()},
                e,
            )
            self._publish_event(
                "governance.record",
                {
                    "event_type": EventType.PROCESSING_FAILED.value,
                    "service": self.service_name,
                    "session_id": session.id,
                    "error": str(e),
                },
            )
            raise

    # =========================================================================
    # ITERATION METHODS
    # =========================================================================

    def _run_iteration(
        self,
        session: ExplorationSession,
        iteration: int,
        session_event: Event,
        memory: SessionMemory,
        config: ExplorationConfig,
    ) -> None:
        """Run single exploration iteration.

        Args:
            session: Current session state.
            iteration: Iteration number.
            session_event: Parent event for correlation.
            memory: Session memory for context.
            config: Exploration config.
        """
        self._logger.debug(
            "iteration_started",
            extra={"session_id": session.id, "iteration": iteration},
        )

        # 1. Select tools to invoke
        tools_to_invoke = self._select_tools(session, memory, config, iteration)

        if not tools_to_invoke:
            self._logger.debug(
                "no_tools_selected",
                extra={"iteration": iteration},
            )
            return

        # 2. Invoke tools
        tool_results = self._invoke_tools(tools_to_invoke)
        session.tools_invoked += len(tool_results)

        # 3. Analyze and classify results
        for result in tool_results:
            if not result.success:
                continue

            # Classify with cognitive architecture
            finding = self._analyze_with_cognitive_tags(
                result=result,
                iteration=iteration,
                session_event=session_event,
                session=session,
            )

            if finding is None:
                continue

            # Apply Struggle Filter
            struggle_state = classify_struggle_state(finding)

            # Log filtered findings
            if struggle_state == StruggleState.DROWNING:
                self._logger.debug(
                    "finding_filtered_drowning",
                    extra={
                        "finding_id": finding.id,
                        "tool": finding.tool_name,
                    },
                )

            # Add to session (handles filtering internally)
            session.add_finding(finding, struggle_state)

            # Add to memory for context
            if struggle_state != StruggleState.DROWNING:
                memory.add_finding(finding)

            # SURPLUS findings become InsightAtoms immediately
            if struggle_state == StruggleState.SURPLUS:
                self._publish_insight_atom(finding, session)

        self._logger.debug(
            "iteration_completed",
            extra={
                "session_id": session.id,
                "iteration": iteration,
                "tools_invoked": len(tool_results),
                "findings_added": len(session.findings),
            },
        )

    def _select_tools(
        self,
        session: ExplorationSession,
        memory: SessionMemory,
        config: ExplorationConfig,
        iteration: int,
    ) -> list[tuple[str, dict[str, Any]]]:
        """Select tools to invoke for this iteration.

        Args:
            session: Current session state.
            memory: Session memory.
            config: Exploration config.
            iteration: Current iteration.

        Returns:
            List of (tool_name, arguments) tuples.
        """
        if self._tool_bridge is None:
            return []

        available_tools = self._tool_bridge.get_exploration_tools()
        if not available_tools:
            available_tools = self._tool_bridge.get_tool_names()[:20]

        budget = (
            self._context_manager.calculate_iteration_budget() if self._context_manager else None
        )
        max_tools = budget.tools_per_iteration if budget else 3

        # For first iteration, use diverse tools
        if iteration == 0:
            tools = [
                ("discover_emergent_patterns", {}),
                ("detect_patterns", {"pattern_type": "frequency", "min_frequency": 10}),
                ("get_source_summary", {}),
            ]
            return tools[:max_tools]

        # For subsequent iterations, use LLM to select based on context
        prompt = format_tool_selection_prompt(
            context=memory.get_context_window(),
            available_tools=available_tools,
            focus_area=config.focus_area,
            iteration=iteration,
            total_iterations=config.iterations,
            prior_findings=session.get_findings_summary(),
            max_tools=max_tools,
        )

        response = self._get_completion(prompt)

        try:
            # Parse JSON response
            tools = json.loads(response)
            return [(t["tool"], t.get("arguments", {})) for t in tools]
        except (json.JSONDecodeError, KeyError):
            # Fallback to default tools
            return [("detect_patterns", {"min_frequency": 5})]

    def _invoke_tools(
        self,
        tool_invocations: list[tuple[str, dict[str, Any]]],
    ) -> list[ToolResult]:
        """Invoke selected tools.

        Args:
            tool_invocations: List of (tool_name, arguments) tuples.

        Returns:
            List of ToolResults.
        """
        if self._tool_bridge is None:
            return []

        results = []
        for tool_name, args in tool_invocations:
            result = self._tool_bridge.invoke(tool_name, args)
            results.append(result)

        return results

    def _analyze_with_cognitive_tags(
        self,
        result: ToolResult,
        iteration: int,
        session_event: Event,
        session: ExplorationSession,
    ) -> Finding | None:
        """Analyze tool result and assign cognitive architecture tags.

        Args:
            result: Tool result to analyze.
            iteration: Current iteration.
            session_event: Parent event.
            session: Current session.

        Returns:
            Finding with cognitive tags, or None on failure.
        """
        prompt = format_cognitive_classification_prompt(
            tool_name=result.tool_name,
            tool_result=result.content,
        )

        response = self._get_completion(prompt)

        try:
            classification = json.loads(response)
        except json.JSONDecodeError:
            self._logger.warning(
                "classification_parse_failed",
                extra={"tool": result.tool_name},
            )
            # Default classification
            classification = {
                "cognitive_stage": 4,
                "thought_type": "reflection",
                "pantheon_mode": "mirror",
                "emotional_state": "curiosity",
                "analysis": result.content[:200],
                "confidence": 0.5,
            }

        # Create finding event (centralized ID)
        finding_event = session_event.child_event(
            event_type=EventType.RECORD_CREATED,
            data={"tool": result.tool_name, "iteration": iteration},
        )

        return Finding(
            id=finding_event.id,
            tool_name=result.tool_name,
            tool_category=result.category,
            iteration=iteration,
            raw_result=result.content,
            analysis=classification.get("analysis", ""),
            cognitive_stage=classification.get("cognitive_stage", 4),
            thought_type=classification.get("thought_type", "reflection"),
            pantheon_mode=classification.get("pantheon_mode", "mirror"),
            emotional_state=classification.get("emotional_state", "curiosity"),
            entities_mentioned=result.entities,
            confidence=classification.get("confidence", 0.5),
            correlation_id=session.correlation_id,
            parent_finding_id=None,
            token_count=len(response) // 4,
            created_at=datetime.now(UTC),
        )

    # =========================================================================
    # SYNTHESIS AND PATTERNS
    # =========================================================================

    def _generate_synthesis(self, session: ExplorationSession) -> dict[str, Any]:
        """Generate synthesis of exploration findings.

        Args:
            session: Completed session.

        Returns:
            Synthesis dict with narrative and recommendations.
        """
        if not session.findings:
            return {"narrative": "No findings to synthesize.", "recommendations": []}

        # Format findings for prompt
        findings_str = "\n".join(f"- [{f.tool_name}] {f.analysis}" for f in session.findings[-20:])

        patterns_str = (
            "\n".join(f"- {p.description}" for p in session.patterns)
            if session.patterns
            else "None discovered"
        )

        metrics = session.resonance_metrics

        prompt = format_synthesis_prompt(
            iterations=session.current_iteration + 1,
            findings_count=len(session.findings),
            high_count=len(session.get_high_significance_findings()),
            focus_area=session.config.focus_area,
            findings=findings_str,
            patterns=patterns_str,
            resonance_score=metrics.total_resonance_score,
            stage_5_ratio=metrics.stage_5_findings / max(metrics.total_findings, 1),
            manifestation_ratio=metrics.manifestation_count / max(metrics.total_findings, 1),
        )

        response = self._get_completion(prompt)

        try:
            result: dict[str, Any] = json.loads(response)
            return result
        except json.JSONDecodeError:
            return {"narrative": response, "recommendations": []}

    def _extract_patterns(
        self,
        session: ExplorationSession,
        session_event: Event,
    ) -> list[Pattern]:
        """Extract patterns from session findings.

        Args:
            session: Completed session.
            session_event: Parent event.

        Returns:
            List of discovered patterns.
        """
        # Simple pattern extraction based on repeated tools/categories
        tool_counts: dict[str, int] = {}
        for finding in session.findings:
            tool_counts[finding.tool_category] = tool_counts.get(finding.tool_category, 0) + 1

        patterns = []
        for category, count in tool_counts.items():
            if count >= 3:
                pattern_event = session_event.child_event(
                    event_type=EventType.RECORD_CREATED,
                    data={"pattern_type": "category_frequency"},
                )
                patterns.append(
                    Pattern(
                        id=pattern_event.id,
                        pattern_type="category_frequency",
                        description=f"Frequent findings in {category} category ({count} findings)",
                        frequency=count,
                        confidence=min(count / 10, 1.0),
                    )
                )

        return patterns

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _get_trust_adjusted_depth(self, config: ExplorationConfig) -> ExplorationDepth:
        """Adjust exploration depth based on RelationshipService trust.

        Args:
            config: Exploration config.

        Returns:
            Adjusted exploration depth.
        """
        if not config.focus_area or self._relationship is None:
            return config.depth

        try:
            partnership = self._relationship.get_partnership(config.focus_area)
            trust = partnership.get("trust_level", 0.5) if partnership else 0.5

            if trust > 0.7:
                return ExplorationDepth.DEEP
            elif trust < 0.3:
                return ExplorationDepth.SHALLOW
            return config.depth
        except Exception as e:
            self._logger.warning(
                "trust_depth_adjustment_failed",
                extra={"focus_area": config.focus_area, "error": str(e)},
            )
            return config.depth

    def _get_knowledge_context(self, focus_area: str | None) -> dict[str, Any]:
        """Get exploration context from KnowledgeService (cached).

        Uses instance-level cache to avoid memory leaks from @lru_cache on methods.

        Args:
            focus_area: Focus area to query.

        Returns:
            Context dict with atoms and sources.
        """
        if not focus_area or self._knowledge is None:
            return {}

        # Check instance cache (avoids memory leak from @lru_cache on methods)
        if focus_area in self._knowledge_cache:
            return self._knowledge_cache[focus_area]

        try:
            atoms = self._knowledge.query(f"related to {focus_area}", limit=10)
            result = {
                "atoms": [a.get("content", "")[:200] for a in atoms],
                "sources": list({a.get("source") for a in atoms if a.get("source")}),
            }
            # Cache up to 50 entries
            if len(self._knowledge_cache) < 50:
                self._knowledge_cache[focus_area] = result
            return result
        except Exception as e:
            self._logger.warning(
                "knowledge_context_failed",
                extra={"focus_area": focus_area, "error": str(e)},
            )
            return {}

    def _check_cost_limit(self, estimated_cost: float) -> bool:
        """Check if we're within cost budget.

        Args:
            estimated_cost: Estimated cost of next action.

        Returns:
            True if within budget.
        """
        return (
            self._session_cost + estimated_cost <= MAX_COST_PER_SESSION
            and self._session_calls < MAX_CALLS_PER_SESSION
        )

    def _get_completion(self, prompt: str) -> str:
        """Get LLM completion using explorer model.

        Args:
            prompt: Prompt to send.

        Returns:
            Model response text.
        """
        self._session_calls += 1

        # Try gateway first
        if self._gateway is not None:
            try:
                from truth_forge.gateway import CompletionRequest

                request = CompletionRequest(
                    prompt=prompt,
                    model=EXPLORER_MODEL,
                    max_tokens=2048,
                )
                response = self._gateway.complete_with_fallback(
                    request,
                    fallback_order=EXPLORER_FALLBACK_ORDER,
                )
                self._session_cost += response.cost
                return response.content
            except Exception as e:
                self._logger.warning(
                    "gateway_completion_failed",
                    extra={"error": str(e)},
                )

        # Fallback to direct Ollama call
        return self._direct_ollama_completion(prompt)

    def _direct_ollama_completion(self, prompt: str) -> str:
        """Direct Ollama API call as fallback.

        Args:
            prompt: Prompt to send.

        Returns:
            Model response text.
        """
        import json
        import urllib.request

        try:
            payload = {
                "model": EXPLORER_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            }

            url = "http://localhost:11434/v1/chat/completions"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=120) as response:
                data: dict[str, Any] = json.loads(response.read().decode())
                choices = data.get("choices", [{}])
                message = choices[0].get("message", {}) if choices else {}
                content: str = message.get("content", "") if isinstance(message, dict) else ""
                return content

        except Exception as e:
            self._logger.error(
                "ollama_completion_failed",
                extra={"error": str(e)},
            )
            return ""

    def _publish_event(self, topic: str, data: dict[str, Any]) -> None:
        """Publish event to mediator if available.

        Args:
            topic: Event topic.
            data: Event data.
        """
        if self._mediator is not None:
            try:
                self._mediator.publish(topic, data)
            except Exception as e:
                self._logger.debug(
                    "mediator_publish_failed",
                    extra={"topic": topic, "error": str(e)},
                )

    def _publish_insight_atom(self, finding: Finding, session: ExplorationSession) -> None:
        """Publish SURPLUS finding as InsightAtom.

        Args:
            finding: SURPLUS finding.
            session: Current session.
        """
        atom_dict = finding.to_insight_atom_dict()
        session.insight_atoms.append(atom_dict)

        self._publish_event(
            "knowledge.process",
            {
                "source": "explorer",
                "content": finding.analysis,
                "metadata": {
                    "explorer_session": session.id,
                    "tool": finding.tool_name,
                    "significance": "surplus",
                },
            },
        )

    def _publish_discoveries(
        self,
        session: ExplorationSession,
        report: ExplorationReport,
    ) -> None:
        """Publish high-significance discoveries.

        Args:
            session: Completed session.
            report: Final report.
        """
        high_findings = session.get_high_significance_findings()

        for finding in high_findings[:5]:
            self._publish_event(
                "knowledge.process",
                {
                    "source": "explorer",
                    "content": finding.analysis,
                    "metadata": {
                        "explorer_session": session.id,
                        "tool": finding.tool_name,
                        "significance": "high",
                    },
                },
            )

        # Publish completion to governance
        self._publish_event(
            "governance.record",
            {
                "event_type": EventType.PROCESSING_COMPLETED.value,
                "service": self.service_name,
                "session_id": session.id,
                "findings_count": len(report.findings),
                "patterns_count": len(report.patterns_discovered),
                "cost": report.total_cost,
            },
        )


__all__ = [
    "ExplorerService",
    "MAX_COST_PER_SESSION",
    "MAX_CALLS_PER_SESSION",
]
