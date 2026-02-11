"""Context Management - Context window management and Struggle Filter.

Implements:
- ContextManager: Token estimation and budget management
- SessionMemory: Context window for exploration iterations
- Struggle Filter: Keep swimming, discard drowning

NO CHUNKING/SUMMARIZATION per Infinite Context Architecture.

MOLT LINEAGE:
- Source: New creation for Explorer autonomous data exploration
- Version: 1.0.0
- Date: 2026-02-01
"""

from __future__ import annotations

from collections import deque

from .models import Finding, IterationBudget, Significance, StruggleState


# =============================================================================
# EXPLORER MODEL CONFIGURATION
# =============================================================================

# Default model for 128GB system - smaller model = larger context
EXPLORER_MODEL = "qwen2.5:14b"
EXPLORER_CONTEXT_LIMIT = 500_000  # 500K tokens on 128GB

# Model tiers: model -> (context_limit, quality_score)
EXPLORER_MODEL_TIERS: dict[str, tuple[int, float]] = {
    "qwen2.5:32b": (256_000, 0.9),  # Best quality for 128GB
    "qwen2.5:14b": (500_000, 0.8),  # Default - good quality, 500K context
    "qwen2.5:7b": (1_000_000, 0.7),  # Decent quality, 1M context
    "llama3.2:3b": (2_000_000, 0.5),  # Acceptable, maximum context
}

# Fallback chain
EXPLORER_FALLBACK_ORDER = ["qwen2.5:14b", "qwen2.5:7b", "llama3.2:3b"]


def get_explorer_context(memory_gb: int = 128) -> int:
    """Get context limit for explorer's chosen model.

    Args:
        memory_gb: System memory in GB.

    Returns:
        Operational context limit in tokens.
    """
    if memory_gb >= 256:
        return 1_000_000  # Can use larger model + big context
    elif memory_gb >= 128:
        return 500_000  # qwen2.5:14b sweet spot
    elif memory_gb >= 64:
        return 256_000  # qwen2.5:7b
    else:
        return 128_000  # Minimal


# =============================================================================
# CONTEXT MANAGER
# =============================================================================


class ContextManager:
    """Manage exploration context within operational limits.

    NO CHUNKING/SUMMARIZATION per Infinite Context Architecture.
    Instead, uses intelligent batching to stay within context window.
    """

    def __init__(self, operational_context: int | None = None) -> None:
        """Initialize context manager.

        Args:
            operational_context: Max tokens available. Defaults to auto-detected.
        """
        self._operational_context = operational_context or get_explorer_context()
        self._token_estimate_ratio = 4  # ~4 chars per token (conservative)

    @property
    def operational_context(self) -> int:
        """Get operational context limit."""
        return self._operational_context

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (conservative).

        Args:
            text: Text to estimate.

        Returns:
            Estimated token count.
        """
        return len(text) // self._token_estimate_ratio

    def can_fit(self, *contents: str) -> bool:
        """Check if all contents fit in operational context.

        Uses 80% safety margin.

        Args:
            contents: Text contents to check.

        Returns:
            True if all contents fit within context.
        """
        total = sum(self.estimate_tokens(c) for c in contents)
        return total < self._operational_context * 0.8

    def get_budget(self) -> int:
        """Get remaining token budget for this request.

        Returns 80% of operational context for safety margin.
        """
        return int(self._operational_context * 0.8)

    def calculate_iteration_budget(self, memory_gb: int = 128) -> IterationBudget:
        """Calculate per-iteration budgets based on explorer context.

        Args:
            memory_gb: System memory in GB.

        Returns:
            IterationBudget with appropriate constraints.
        """
        context = get_explorer_context(memory_gb)

        if context >= 500_000:  # 128GB + smaller model
            return IterationBudget(
                tools_per_iteration=5,
                max_findings_context=25,
                max_entities_per_query=100,
                synthesis_frequency=5,
                parallel_tool_calls=True,
            )
        elif context >= 256_000:  # Mid-tier
            return IterationBudget(
                tools_per_iteration=4,
                max_findings_context=15,
                max_entities_per_query=50,
                synthesis_frequency=4,
                parallel_tool_calls=True,
            )
        else:  # Conservative
            return IterationBudget(
                tools_per_iteration=2,
                max_findings_context=8,
                max_entities_per_query=25,
                synthesis_frequency=2,
                parallel_tool_calls=False,
            )


# =============================================================================
# STRUGGLE FILTER
# Reference: framework/ontology/technical_architecture/struggle_filter.md
# =============================================================================


def classify_struggle_state(finding: Finding) -> StruggleState:
    """Apply Struggle Filter to finding.

    The Struggle Filter operates on a strict binary distinction:
    - DROWNING: Anxiety, confusion, circular logic → DELETE
    - SWIMMING: Clarity, resolution, action → KEEP
    - SURPLUS: Output > Input (revelation) → PRIORITIZE

    Args:
        finding: Finding to classify.

    Returns:
        StruggleState classification.
    """
    # SURPLUS: manifestation + resonance + high confidence
    # This represents "Surplus Value" - interactions where output generated
    # clarity and revelation greater than the input.
    if (
        finding.thought_type == "manifestation"
        and finding.emotional_state == "resonance"
        and finding.confidence > 0.8
    ):
        return StruggleState.SURPLUS

    # SWIMMING: Stage 5 + clarity/determination/resonance
    # These are moments of clarity, action, decision, and synthesis.
    if finding.cognitive_stage == 5 and finding.emotional_state in (
        "clarity",
        "determination",
        "resonance",
    ):
        return StruggleState.SWIMMING

    # DROWNING: Stage 3/4 + tension/resistance without resolution
    # These are anxiety loops and circular logic.
    if (
        finding.cognitive_stage < 5
        and finding.emotional_state in ("tension", "resistance")
        and finding.thought_type != "synthesis"
    ):
        return StruggleState.DROWNING

    # Default to SWIMMING (keep the finding)
    return StruggleState.SWIMMING


def apply_struggle_filter(findings: list[Finding]) -> tuple[list[Finding], int]:
    """Filter findings for total resonance packet.

    Keep: SWIMMING, SURPLUS
    Discard: DROWNING
    Prioritize: SURPLUS (move to front)

    Args:
        findings: List of findings to filter.

    Returns:
        Tuple of (filtered_findings, discarded_count).
    """
    filtered: list[Finding] = []
    surplus: list[Finding] = []
    discarded = 0

    for finding in findings:
        state = classify_struggle_state(finding)
        if state == StruggleState.SURPLUS:
            surplus.append(finding)
        elif state == StruggleState.SWIMMING:
            filtered.append(finding)
        else:  # DROWNING
            discarded += 1

    # SURPLUS first (prioritized), then SWIMMING
    return surplus + filtered, discarded


# =============================================================================
# SESSION MEMORY
# =============================================================================


class SessionMemory:
    """Manages what to keep in context across iterations.

    NO CHUNKING per Infinite Context Architecture.
    Instead, uses intelligent selection to stay within context window.
    """

    def __init__(self, max_findings: int = 25) -> None:
        """Initialize session memory.

        Args:
            max_findings: Maximum findings to keep in context.
        """
        self._max_findings = max_findings
        self._findings: deque[Finding] = deque(maxlen=max_findings)
        self._synthesized_knowledge: str = ""
        self._insight_atoms: list[dict[str, object]] = []

    @property
    def findings(self) -> list[Finding]:
        """Get current findings in memory."""
        return list(self._findings)

    @property
    def insight_atoms(self) -> list[dict[str, object]]:
        """Get generated insight atoms."""
        return self._insight_atoms

    def add_finding(self, finding: Finding) -> None:
        """Add finding, auto-evicting oldest if at capacity.

        Args:
            finding: Finding to add.
        """
        self._findings.append(finding)

    def add_insight_atom(self, atom_dict: dict[str, object]) -> None:
        """Add insight atom for knowledge pipeline.

        Args:
            atom_dict: InsightAtom-compatible dictionary.
        """
        self._insight_atoms.append(atom_dict)

    def get_context_window(self) -> str:
        """Get context for next iteration.

        Returns string that fits within operational context limit.
        Includes recent findings and synthesized knowledge.
        """
        # Recent findings (most relevant - last 5)
        recent = "\n\n".join(f.analysis for f in list(self._findings)[-5:])

        # Synthesized knowledge (compressed history)
        history = self._synthesized_knowledge if self._synthesized_knowledge else ""

        if history:
            return f"## Prior Knowledge\n{history}\n\n## Recent Findings\n{recent}"
        return f"## Recent Findings\n{recent}"

    def synthesize(self, synthesis: str) -> None:
        """Compress findings into synthesized knowledge.

        After synthesis, keep only HIGH significance findings.

        Args:
            synthesis: Synthesis text from LLM.
        """
        self._synthesized_knowledge = synthesis

        # Keep only HIGH significance findings after synthesis
        high_findings = [f for f in self._findings if f.significance == Significance.HIGH]
        self._findings.clear()
        for f in high_findings[-3:]:  # Keep last 3 high-significance
            self._findings.append(f)

    def get_high_significance_findings(self) -> list[Finding]:
        """Get HIGH significance findings.

        Returns:
            List of HIGH significance findings.
        """
        return [f for f in self._findings if f.significance == Significance.HIGH]

    def clear(self) -> None:
        """Clear memory state."""
        self._findings.clear()
        self._synthesized_knowledge = ""
        self._insight_atoms.clear()


__all__ = [
    # Model config
    "EXPLORER_MODEL",
    "EXPLORER_CONTEXT_LIMIT",
    "EXPLORER_MODEL_TIERS",
    "EXPLORER_FALLBACK_ORDER",
    "get_explorer_context",
    # Context management
    "ContextManager",
    # Struggle filter
    "classify_struggle_state",
    "apply_struggle_filter",
    # Session memory
    "SessionMemory",
]
