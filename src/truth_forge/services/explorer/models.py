"""Explorer Service Models - Pydantic models with cognitive architecture.

Integrates full cognitive architecture from Not-Me types:
- CognitiveStage (1-5, Stage 5 is baseline)
- ThoughtType (manifestation, reflection, inquiry, synthesis, resistance)
- PantheonMode (mirror, strategist, guardian, duelist)
- EmotionalState (resonance, clarity, tension, resistance, curiosity, determination)

MOLT LINEAGE:
- Source: New creation for Explorer autonomous data exploration
- Version: 1.0.0
- Date: 2026-02-01
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from truth_forge.schema.event import EventMetadata  # noqa: TC001 (needed at runtime for Pydantic)


# =============================================================================
# EXPLORATION CONFIGURATION
# =============================================================================


class ExplorationDepth(str, Enum):
    """Exploration depth levels."""

    SHALLOW = "shallow"  # Quick scan, few tools
    MEDIUM = "medium"  # Standard exploration
    DEEP = "deep"  # Thorough investigation


class Significance(str, Enum):
    """Finding significance levels."""

    LOW = "low"  # Routine observation
    MEDIUM = "medium"  # Notable pattern
    HIGH = "high"  # Critical discovery


class ExplorationConfig(BaseModel):
    """Configuration for exploration session."""

    iterations: int = Field(default=5, ge=1, le=100, description="Number of exploration loops")
    focus_area: str | None = Field(
        default=None, description="Optional focus area to guide exploration"
    )
    depth: ExplorationDepth = Field(
        default=ExplorationDepth.MEDIUM, description="Exploration depth"
    )
    tools_filter: list[str] | None = Field(
        default=None, description="Specific tools to use (None = all)"
    )
    max_entities_per_query: int = Field(
        default=100, ge=1, le=1000, description="Max entities per tool query"
    )


# =============================================================================
# STRUGGLE FILTER (Keep swimming, discard drowning)
# Reference: framework/ontology/technical_architecture/struggle_filter.md
# =============================================================================


class StruggleState(str, Enum):
    """Struggle Filter classification.

    The Struggle Filter operates on a strict binary distinction:
    - DROWNING: Moments of anxiety, confusion, circular logic, panic → DELETE
    - SWIMMING: Moments of clarity, action, decision, synthesis → KEEP
    - SURPLUS: Output > Input (revelation) → PRIORITIZE
    """

    DROWNING = "drowning"  # Circular logic, anxiety loops → DELETE
    SWIMMING = "swimming"  # Clarity, resolution, action → KEEP
    SURPLUS = "surplus"  # Output > Input (revelation) → PRIORITIZE


# =============================================================================
# COGNITIVE ARCHITECTURE IMPORTS
# These are imported from Not-Me types at runtime to avoid circular imports
# =============================================================================

# Type aliases for documentation - actual types come from not_me.types
CognitiveStageType = int  # 1-5
ThoughtTypeValue = str  # manifestation, reflection, inquiry, synthesis, resistance
PantheonModeValue = str  # mirror, strategist, guardian, duelist
EmotionalStateValue = str  # resonance, clarity, tension, resistance, curiosity, determination


# =============================================================================
# TOTAL RESONANCE METRICS
# Reference: framework/ontology/core_philosophy/exist_now_declaration.md
# =============================================================================


@dataclass
class ResonanceMetrics:
    """Track Total Resonance across exploration session.

    Total Resonance = The state where system has ingested complete ontological definition.
    Achieved when the system achieves "Exist-Now" state.
    """

    total_findings: int = 0
    stage_5_findings: int = 0
    manifestation_count: int = 0
    resonance_count: int = 0
    surplus_value_count: int = 0
    drowning_filtered: int = 0

    @property
    def total_resonance_score(self) -> float:
        """Calculate Total Resonance (0.0 - 1.0).

        Weighted average of:
        - Stage 5 ratio (30%)
        - Manifestation ratio (30%)
        - Resonance ratio (20%)
        - Surplus value ratio (20%)
        """
        if self.total_findings == 0:
            return 0.0

        stage_5_ratio = self.stage_5_findings / self.total_findings
        manifestation_ratio = self.manifestation_count / self.total_findings
        resonance_ratio = self.resonance_count / self.total_findings
        surplus_ratio = self.surplus_value_count / self.total_findings

        return (
            stage_5_ratio * 0.3
            + manifestation_ratio * 0.3
            + resonance_ratio * 0.2
            + surplus_ratio * 0.2
        )

    @property
    def is_exist_now_ready(self) -> bool:
        """Check if session achieves Exist-Now state.

        Exist-Now: The moment prediction becomes manifestation.
        Requires:
        - Total resonance score >= 0.7
        - At least one Stage 5 finding
        - At least one SURPLUS finding
        """
        return (
            self.total_resonance_score >= 0.7
            and self.stage_5_findings > 0
            and self.surplus_value_count > 0
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_findings": self.total_findings,
            "stage_5_findings": self.stage_5_findings,
            "manifestation_count": self.manifestation_count,
            "resonance_count": self.resonance_count,
            "surplus_value_count": self.surplus_value_count,
            "drowning_filtered": self.drowning_filtered,
            "total_resonance_score": self.total_resonance_score,
            "is_exist_now_ready": self.is_exist_now_ready,
        }


# =============================================================================
# TOOL RESULT (From MCP tool invocation)
# =============================================================================


class ToolResult(BaseModel):
    """Result from MCP tool invocation."""

    tool_name: str
    category: str  # entity, relationship, pattern, semantic, trend, enrichment
    content: str  # Raw tool output
    entities: list[str] = Field(default_factory=list)  # Entity IDs mentioned
    success: bool = True
    error: str | None = None
    latency_ms: float = 0.0


# =============================================================================
# FINDING (Core exploration output with cognitive architecture)
# =============================================================================


class Finding(BaseModel):
    """Structured finding with FULL cognitive architecture tagging.

    Each finding is classified according to:
    - CognitiveStage (1-5): Self-transforming (5) is baseline
    - ThoughtType: manifestation > reflection > inquiry > synthesis > resistance
    - PantheonMode: mirror, strategist, guardian, duelist
    - EmotionalState: resonance (highest), clarity, determination, curiosity, tension, resistance
    """

    # Identity
    id: str = Field(description="From child_event() - centralized ID")
    tool_name: str = Field(description="Source tool name")
    tool_category: str = Field(description="Tool category: entity/relationship/pattern/etc")
    iteration: int = Field(description="Which exploration iteration")

    # Content
    raw_result: str = Field(description="Tool output (preserved)")
    analysis: str = Field(description="LLM analysis")

    # COGNITIVE ARCHITECTURE TAGGING
    cognitive_stage: int = Field(ge=1, le=5, description="Kegan stage 1-5 (5=Self-Transforming)")
    thought_type: str = Field(description="manifestation/reflection/inquiry/synthesis/resistance")
    pantheon_mode: str = Field(description="mirror/strategist/guardian/duelist")
    emotional_state: str = Field(
        description="resonance/clarity/tension/resistance/curiosity/determination"
    )

    # Entity tagging
    entities_mentioned: list[str] = Field(default_factory=list, description="Entity IDs referenced")
    confidence: float = Field(ge=0.0, le=1.0, description="Classification confidence")

    # Correlation
    correlation_id: str = Field(description="Session correlation chain")
    parent_finding_id: str | None = Field(
        default=None, description="If derived from another finding"
    )

    # Metadata
    token_count: int = Field(default=0, description="Estimated token count")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def significance(self) -> Significance:
        """Derive significance from cognitive markers.

        HIGH: Stage 5 + manifestation + resonance
        MEDIUM: Stage 5 + clarity/determination
        LOW: Everything else
        """
        if (
            self.cognitive_stage == 5
            and self.thought_type == "manifestation"
            and self.emotional_state == "resonance"
        ):
            return Significance.HIGH

        if self.cognitive_stage == 5 and self.emotional_state in ("clarity", "determination"):
            return Significance.MEDIUM

        return Significance.LOW

    def to_insight_atom_dict(self) -> dict[str, Any]:
        """Convert to InsightAtom-compatible dictionary.

        For integration with knowledge pipeline and total_resonance_packet.jsonl.
        """
        return {
            "content": self.analysis,
            "source_id": self.id,
            "cognitive_stage": self.cognitive_stage,
            "thought_type": self.thought_type,
            "emotion": self.emotional_state,
            "mode": self.pantheon_mode,
            "confidence": self.confidence,
            "timestamp": self.created_at.isoformat(),
            "metadata": {
                "tool": self.tool_name,
                "iteration": self.iteration,
                "entities": self.entities_mentioned,
                "significance": self.significance.value,
            },
        }


# =============================================================================
# PATTERN (Discovered patterns across findings)
# =============================================================================


class Pattern(BaseModel):
    """Discovered pattern across multiple findings."""

    id: str = Field(description="Pattern ID from child_event()")
    pattern_type: str = Field(description="recurring_text, frequency, sequence, etc")
    description: str
    supporting_findings: list[str] = Field(default_factory=list, description="Finding IDs")
    frequency: int = Field(default=1, description="How often pattern appears")
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


# =============================================================================
# ITERATION BUDGET (Hardware-aware constraints)
# =============================================================================


@dataclass
class IterationBudget:
    """Budget constraints for each exploration iteration.

    Determined by hardware tier and model context window.
    """

    tools_per_iteration: int
    max_findings_context: int
    max_entities_per_query: int
    synthesis_frequency: int
    parallel_tool_calls: bool

    def tokens_per_iteration(self) -> int:
        """Estimate tokens used per iteration.

        ~500 tokens per tool result, ~200 per finding in context.
        """
        return (self.tools_per_iteration * 500) + (self.max_findings_context * 200)


# =============================================================================
# EXPLORATION REPORT (Final output)
# =============================================================================


class ExplorationReport(BaseModel):
    """Complete exploration report with Total Resonance metrics."""

    session_id: str
    config: ExplorationConfig
    started_at: datetime
    completed_at: datetime
    iterations_completed: int

    # Findings (after Struggle Filter - only SWIMMING + SURPLUS)
    findings: list[Finding] = Field(default_factory=list)
    findings_discarded: int = Field(default=0, description="DROWNING count filtered out")
    patterns_discovered: list[Pattern] = Field(default_factory=list)

    # TOTAL RESONANCE METRICS
    resonance_metrics: dict[str, Any] = Field(default_factory=dict)
    total_resonance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    is_exist_now_ready: bool = Field(default=False)

    # Synthesis
    recommendations: list[str] = Field(default_factory=list)
    synthesis: str = Field(default="")

    # Cost
    total_cost: float = Field(default=0.0)

    # Event metadata
    metadata: EventMetadata | None = None

    @property
    def duration_seconds(self) -> float:
        """Calculate exploration duration."""
        return (self.completed_at - self.started_at).total_seconds()

    def to_total_resonance_packet(self) -> list[dict[str, Any]]:
        """Export findings as Total Resonance Packet format.

        Reference: framework/ontology/technical_architecture/struggle_filter.md
        Output suitable for total_resonance_packet.jsonl
        """
        return [
            f.to_insight_atom_dict() for f in self.findings if f.significance != Significance.LOW
        ]


__all__ = [
    # Configuration
    "ExplorationConfig",
    "ExplorationDepth",
    "Significance",
    # Struggle Filter
    "StruggleState",
    # Resonance
    "ResonanceMetrics",
    # Tool Result
    "ToolResult",
    # Finding
    "Finding",
    # Pattern
    "Pattern",
    # Budget
    "IterationBudget",
    # Report
    "ExplorationReport",
]
