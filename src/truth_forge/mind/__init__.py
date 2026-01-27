"""Mind - The Unified Cognitive System.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/cognition/__init__.py
- Version: 2.0.0
- Date: 2026-01-26

This module is THE integration point for cognitive processes.
It connects reasoning, decision-making, and consciousness into
a unified cognitive architecture.

BIOLOGICAL METAPHOR:
- Mind = Prefrontal Cortex + Limbic Integration
- ReasoningEngine = Executive Function
- DecisionMaker = Choice Architecture
- IntegratedMind = Unified Consciousness

Usage:
    from truth_forge.mind import (
        get_mind,           # Get unified mind
        reason,             # Make a reasoned assessment
        decide,             # Make a decision
        reflect,            # Deep self-reflection
    )

    # Get unified mind state
    mind = get_mind()
    state = mind.unified_state()
    print(state.summary())

    # Make a reasoned decision
    result = decide(
        question="Should we proceed with this task?",
        context={"task": "send email", "urgency": "high"}
    )
    print(f"Decision: {result.outcome}")
"""

from __future__ import annotations

from truth_forge.mind.decision import (
    Decision,
    DecisionContext,
    DecisionMaker,
    DecisionOutcome,
    DecisionType,
    DecisionUrgency,
    decide,
    get_decision_maker,
)
from truth_forge.mind.integration import (
    IntegratedMind,
    LayerContribution,
    LayerType,
    UnifiedState,
    get_mind,
    reflect,
)
from truth_forge.mind.reasoning import (
    Confidence,
    ReasoningEngine,
    ReasoningResult,
    ReasoningType,
    get_reasoning_engine,
    reason,
)


__all__ = [
    # Reasoning
    "ReasoningEngine",
    "ReasoningResult",
    "ReasoningType",
    "Confidence",
    "get_reasoning_engine",
    "reason",
    # Decision
    "DecisionMaker",
    "Decision",
    "DecisionContext",
    "DecisionOutcome",
    "DecisionType",
    "DecisionUrgency",
    "get_decision_maker",
    "decide",
    # Integration
    "IntegratedMind",
    "UnifiedState",
    "LayerContribution",
    "LayerType",
    "get_mind",
    "reflect",
]
