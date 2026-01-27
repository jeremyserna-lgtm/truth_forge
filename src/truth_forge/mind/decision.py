"""Decision - The Choice Architecture.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/cognition/decision.py
- Version: 2.0.0
- Date: 2026-01-26

This module enables informed decision-making by using structured
reasoning to reach conclusions.

BIOLOGICAL METAPHOR:
- DecisionMaker = Executive Function
- Decision = Action potential
- DecisionContext = Situational awareness

THE LOOP PHASE:
This is the CHOOSE phase of WANT -> CHOOSE -> EXIST:NOW -> SEE -> HOLD -> MOVE

THE PATTERN:
Options (HOLD1) -> Decision Process (AGENT) -> Choice (HOLD2)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from truth_forge.core.paths import DATA_ROOT


logger = logging.getLogger(__name__)


class DecisionUrgency(Enum):
    """How urgent is this decision?"""

    IMMEDIATE = "immediate"  # Decide now
    SOON = "soon"  # Decide within the hour
    PLANNED = "planned"  # Can wait for proper consideration
    REFLECTIVE = "reflective"  # Deep consideration needed


class DecisionType(Enum):
    """What kind of decision is this?"""

    PROCEED = "proceed"  # Go/no-go decision
    CHOOSE = "choose"  # Select from options
    PRIORITIZE = "prioritize"  # Order by importance
    ALLOCATE = "allocate"  # Resource distribution
    DELEGATE = "delegate"  # Who should do this


class DecisionOutcome(Enum):
    """The outcome of a decision."""

    PROCEED = "proceed"  # Go ahead
    WAIT = "wait"  # Not yet
    DECLINE = "decline"  # No
    DEFER = "defer"  # Someone else decides
    ESCALATE = "escalate"  # Need human input


@dataclass
class DecisionContext:
    """Context for making a decision."""

    # The decision to make
    question: str = ""
    decision_type: DecisionType = DecisionType.PROCEED
    urgency: DecisionUrgency = DecisionUrgency.PLANNED

    # Options (for CHOOSE type)
    options: list[str] = field(default_factory=list)

    # Constraints
    must_respect: list[str] = field(default_factory=list)  # Hard constraints
    should_consider: list[str] = field(default_factory=list)  # Soft factors
    avoid: list[str] = field(default_factory=list)  # What to avoid

    # Additional context
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question": self.question,
            "decision_type": self.decision_type.value,
            "urgency": self.urgency.value,
            "options": self.options,
            "must_respect": self.must_respect,
            "should_consider": self.should_consider,
            "avoid": self.avoid,
            "metadata": self.metadata,
        }


@dataclass
class Decision:
    """The result of a decision process."""

    decision_id: str = field(default_factory=lambda: f"dec_{uuid4().hex[:8]}")
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Input
    context: DecisionContext | None = None

    # Output
    outcome: DecisionOutcome = DecisionOutcome.WAIT
    choice: str = ""  # What was decided
    reasoning: str = ""  # Why

    # Supporting information
    factors_for: list[str] = field(default_factory=list)
    factors_against: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    mitigations: list[str] = field(default_factory=list)

    # Confidence
    confidence: float = 0.5  # 0.0 to 1.0

    # State at decision time
    mood: str = ""
    health: float = 1.0

    # Follow-up
    next_steps: list[str] = field(default_factory=list)
    revisit_if: list[str] = field(default_factory=list)

    def summary(self) -> str:
        """Generate human-readable summary."""
        outcome_emoji = {
            DecisionOutcome.PROCEED: "[OK]",
            DecisionOutcome.WAIT: "[..]",
            DecisionOutcome.DECLINE: "[NO]",
            DecisionOutcome.DEFER: "[>>]",
            DecisionOutcome.ESCALATE: "[^^]",
        }

        lines = [
            "+===========================================================+",
            "|                    DECISION MADE                          |",
            "+===========================================================+",
        ]

        if self.context:
            lines.append(f"|  Question: {self.context.question[:45]:45}|")

        emoji = outcome_emoji.get(self.outcome, "[??]")
        lines.append(
            f"|  Outcome: {emoji} {self.outcome.value.upper():12} | "
            f"Confidence: {self.confidence * 100:.0f}%   |"
        )

        if self.choice:
            lines.append(f"|  Choice: {self.choice[:47]:47}|")

        lines.append("+-----------------------------------------------------------+")

        if self.reasoning:
            lines.append(f"|  Reasoning: {self.reasoning[:44]:44}|")

        if self.factors_for:
            lines.append("|  + Factors For:                                          |")
            for factor in self.factors_for[:2]:
                lines.append(f"|     - {factor[:49]:49}|")

        if self.factors_against:
            lines.append("|  - Factors Against:                                      |")
            for factor in self.factors_against[:2]:
                lines.append(f"|     - {factor[:49]:49}|")

        if self.risks:
            lines.append("|  ! Risks:                                                |")
            for risk in self.risks[:2]:
                lines.append(f"|     - {risk[:49]:49}|")

        if self.next_steps:
            lines.append("|  Next Steps:                                             |")
            for step in self.next_steps[:2]:
                lines.append(f"|     -> {step[:48]:48}|")

        lines.append("+===========================================================+")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context.to_dict() if self.context else None,
            "outcome": self.outcome.value,
            "choice": self.choice,
            "reasoning": self.reasoning,
            "factors_for": self.factors_for,
            "factors_against": self.factors_against,
            "risks": self.risks,
            "mitigations": self.mitigations,
            "confidence": self.confidence,
            "mood": self.mood,
            "health": self.health,
            "next_steps": self.next_steps,
            "revisit_if": self.revisit_if,
        }


class DecisionMaker:
    """The decision-making engine.

    This engine:
    1. Takes a decision context
    2. Uses reasoning to evaluate options
    3. Produces a well-considered decision

    Example:
        maker = get_decision_maker()

        decision = maker.decide(
            question="Should we proceed with this task?",
            urgency=DecisionUrgency.SOON,
        )

        if decision.outcome == DecisionOutcome.PROCEED:
            execute_task()
    """

    def __init__(self) -> None:
        """Initialize the decision maker."""
        self._history: list[Decision] = []
        self._history_path: Path | None = None

        try:
            self._history_path = DATA_ROOT / "local" / "mind" / "decisions.jsonl"
            self._history_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        logger.info("DecisionMaker initialized")

    def decide(
        self,
        question: str,
        urgency: DecisionUrgency = DecisionUrgency.PLANNED,
        decision_type: DecisionType = DecisionType.PROCEED,
        options: list[str] | None = None,
        constraints: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> Decision:
        """Make a decision.

        Args:
            question: What to decide
            urgency: How urgent
            decision_type: Type of decision
            options: Options to choose from (for CHOOSE type)
            constraints: Hard constraints to respect
            context: Additional context

        Returns:
            Decision with outcome and reasoning
        """
        # Build context
        ctx = DecisionContext(
            question=question,
            decision_type=decision_type,
            urgency=urgency,
            options=options or [],
            must_respect=constraints or [],
            metadata=context or {},
        )

        decision = Decision(context=ctx)

        # Make the decision based on type
        if decision_type == DecisionType.PROCEED:
            self._decide_proceed(decision, ctx)
        elif decision_type == DecisionType.CHOOSE:
            self._decide_choose(decision, ctx)
        elif decision_type == DecisionType.PRIORITIZE:
            self._decide_prioritize(decision, ctx)
        else:
            self._decide_proceed(decision, ctx)

        # Add to history
        self._record_decision(decision)

        return decision

    def _decide_proceed(self, decision: Decision, ctx: DecisionContext) -> None:
        """Make a go/no-go decision."""
        # Score the decision
        score = 0.5  # Start neutral

        # Urgency factor
        if ctx.urgency == DecisionUrgency.IMMEDIATE:
            score += 0.1  # Bias toward action for immediate
            decision.factors_for.append("High urgency - action bias")
        elif ctx.urgency == DecisionUrgency.REFLECTIVE:
            score -= 0.1  # Bias toward caution for reflective
            decision.factors_against.append("Reflective - caution bias")

        # Constraints factor
        if ctx.must_respect:
            score -= 0.05 * len(ctx.must_respect)
            decision.factors_against.append(f"{len(ctx.must_respect)} constraints noted")

        # Convert score to decision
        if score > 0.6:
            decision.outcome = DecisionOutcome.PROCEED
            decision.reasoning = "Favorable conditions - proceed"
            decision.confidence = min(0.95, score)
            decision.next_steps.append("Execute the planned action")
        elif score > 0.4:
            decision.outcome = DecisionOutcome.PROCEED
            decision.reasoning = "Conditions acceptable - proceed with awareness"
            decision.confidence = score
            decision.next_steps.append("Proceed but monitor for issues")
            decision.revisit_if.append("Conditions deteriorate")
        elif score > 0.3:
            decision.outcome = DecisionOutcome.WAIT
            decision.reasoning = "Uncertain conditions - wait for clarity"
            decision.confidence = 0.5 + (0.5 - score)
            decision.next_steps.append("Reassess when conditions improve")
        else:
            decision.outcome = DecisionOutcome.DECLINE
            decision.reasoning = "Unfavorable conditions - do not proceed"
            decision.confidence = min(0.9, 0.5 + (0.5 - score))
            decision.next_steps.append("Address blocking factors first")

    def _decide_choose(self, decision: Decision, ctx: DecisionContext) -> None:
        """Choose from multiple options."""
        if not ctx.options:
            decision.outcome = DecisionOutcome.DEFER
            decision.reasoning = "No options provided"
            return

        # Simple scoring: first option unless concerns suggest otherwise
        decision.choice = ctx.options[0]
        decision.outcome = DecisionOutcome.PROCEED
        decision.reasoning = f"Selected '{ctx.options[0]}' as best available option"
        decision.confidence = 0.6

        if len(ctx.options) > 1:
            decision.factors_for.append(f"Considered {len(ctx.options)} options")
            decision.next_steps.append(f"Alternative if needed: {ctx.options[1]}")

    def _decide_prioritize(self, decision: Decision, ctx: DecisionContext) -> None:
        """Prioritize items."""
        if not ctx.options:
            decision.outcome = DecisionOutcome.DEFER
            decision.reasoning = "No items to prioritize"
            return

        # For now, just preserve order
        prioritized = list(ctx.options)

        decision.choice = " > ".join(prioritized[:3])
        decision.outcome = DecisionOutcome.PROCEED
        decision.reasoning = "Prioritized based on current context"
        decision.confidence = 0.7

    def _record_decision(self, decision: Decision) -> None:
        """Record decision to history."""
        self._history.append(decision)

        # Persist to disk
        if self._history_path:
            try:
                with open(self._history_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(decision.to_dict()) + "\n")
            except Exception as e:
                logger.debug("Failed to persist decision", extra={"error": str(e)})

    def recent(self, count: int = 10) -> list[Decision]:
        """Get recent decisions."""
        return self._history[-count:]


# Singleton
_maker_instance: DecisionMaker | None = None


def get_decision_maker() -> DecisionMaker:
    """Get or create the singleton DecisionMaker."""
    global _maker_instance
    if _maker_instance is None:
        _maker_instance = DecisionMaker()
    return _maker_instance


def decide(
    question: str,
    urgency: DecisionUrgency = DecisionUrgency.PLANNED,
    decision_type: DecisionType = DecisionType.PROCEED,
    options: list[str] | None = None,
    context: dict[str, Any] | None = None,
) -> Decision:
    """Convenience function to make a decision.

    Args:
        question: What to decide
        urgency: How urgent
        decision_type: Type of decision
        options: Options for CHOOSE type
        context: Additional context

    Returns:
        Decision with outcome and reasoning
    """
    maker = get_decision_maker()
    return maker.decide(question, urgency, decision_type, options, context=context)


__all__ = [
    "DecisionMaker",
    "Decision",
    "DecisionContext",
    "DecisionOutcome",
    "DecisionType",
    "DecisionUrgency",
    "get_decision_maker",
    "decide",
]
