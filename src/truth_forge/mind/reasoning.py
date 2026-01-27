"""Reasoning - The Cognitive Engine.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/cognition/reasoning.py
- Version: 2.0.0
- Date: 2026-01-26

This module enables deep reasoning that consults cognitive state
to transform raw information into informed insights.

BIOLOGICAL METAPHOR:
- ReasoningEngine = Prefrontal Cortex
- ReasoningResult = Considered judgment
- Context = Working memory

THE PATTERN:
Question + Context (HOLD1) -> Reasoning (AGENT) -> Result (HOLD2)

THE FURNACE:
Truth (state) -> Meaning (reasoning) -> Care (result)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


logger = logging.getLogger(__name__)


class ReasoningType(Enum):
    """Types of reasoning the engine can perform."""

    ANALYTICAL = "analytical"  # Logical analysis
    INTUITIVE = "intuitive"  # Pattern-based
    EMOTIONAL = "emotional"  # Feeling-informed
    WISDOM = "wisdom"  # Principle-based
    HOLISTIC = "holistic"  # All sources integrated


class Confidence(Enum):
    """Confidence levels in reasoning results."""

    VERY_HIGH = "very_high"  # >90% certain
    HIGH = "high"  # 70-90% certain
    MODERATE = "moderate"  # 50-70% certain
    LOW = "low"  # 30-50% certain
    UNCERTAIN = "uncertain"  # <30% certain


@dataclass
class ReasoningResult:
    """The result of a reasoning process."""

    # Core result
    question: str = ""
    answer: str = ""
    reasoning_type: ReasoningType = ReasoningType.HOLISTIC
    confidence: Confidence = Confidence.MODERATE

    # Supporting information
    key_factors: list[str] = field(default_factory=list)
    considerations: list[str] = field(default_factory=list)
    concerns_noted: list[str] = field(default_factory=list)
    wisdom_applied: list[str] = field(default_factory=list)

    # Layer contributions
    layer_inputs: dict[str, str] = field(default_factory=dict)

    # Metadata
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    duration_ms: float = 0.0

    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            "+-----------------------------------------------------------+",
            f"| Question: {self.question[:47]:47}|",
            "+-----------------------------------------------------------+",
            f"| Answer: {self.answer[:49]:49}|",
            f"| Confidence: {self.confidence.value.upper():12} | "
            f"Type: {self.reasoning_type.value:12}|",
            "+-----------------------------------------------------------+",
        ]

        if self.key_factors:
            lines.append("| Key Factors:                                              |")
            for factor in self.key_factors[:3]:
                lines.append(f"|   - {factor[:51]:51}|")

        if self.wisdom_applied:
            lines.append("| Wisdom Applied:                                           |")
            for wisdom in self.wisdom_applied[:2]:
                lines.append(f"|   * {wisdom[:51]:51}|")

        if self.concerns_noted:
            lines.append("| Concerns:                                                 |")
            for concern in self.concerns_noted[:2]:
                lines.append(f"|   ! {concern[:51]:51}|")

        lines.append("+-----------------------------------------------------------+")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question": self.question,
            "answer": self.answer,
            "reasoning_type": self.reasoning_type.value,
            "confidence": self.confidence.value,
            "key_factors": self.key_factors,
            "considerations": self.considerations,
            "concerns_noted": self.concerns_noted,
            "wisdom_applied": self.wisdom_applied,
            "layer_inputs": self.layer_inputs,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
        }


class ReasoningEngine:
    """The cognitive reasoning engine.

    This engine:
    1. Takes a question and context
    2. Applies different reasoning strategies
    3. Produces a reasoned result

    Example:
        engine = get_reasoning_engine()
        result = engine.reason(
            question="Should we proceed with this task?",
            context={"urgency": "high"}
        )
        print(result.summary())
    """

    def __init__(self) -> None:
        """Initialize the reasoning engine."""
        self._last_result: ReasoningResult | None = None
        logger.info("ReasoningEngine initialized")

    def reason(
        self,
        question: str,
        context: dict[str, Any] | None = None,
        reasoning_type: ReasoningType = ReasoningType.HOLISTIC,
    ) -> ReasoningResult:
        """Perform reasoning on a question.

        Args:
            question: The question to reason about
            context: Additional context
            reasoning_type: Type of reasoning to apply

        Returns:
            ReasoningResult with answer and supporting info
        """
        start_time = time.time()

        result = ReasoningResult(
            question=question,
            reasoning_type=reasoning_type,
        )

        context = context or {}

        # Apply different reasoning approaches
        if reasoning_type == ReasoningType.HOLISTIC:
            self._reason_holistically(result, context)
        elif reasoning_type == ReasoningType.ANALYTICAL:
            self._reason_analytically(result, context)
        elif reasoning_type == ReasoningType.INTUITIVE:
            self._reason_intuitively(result, context)
        elif reasoning_type == ReasoningType.EMOTIONAL:
            self._reason_emotionally(result, context)
        elif reasoning_type == ReasoningType.WISDOM:
            self._reason_with_wisdom(result, context)

        result.duration_ms = (time.time() - start_time) * 1000
        self._last_result = result

        return result

    def _reason_holistically(
        self,
        result: ReasoningResult,
        context: dict[str, Any],
    ) -> None:
        """Holistic reasoning using all sources."""
        result.key_factors = []

        # Consider context factors
        urgency = context.get("urgency", "normal")
        result.key_factors.append(f"Urgency: {urgency}")

        # Consider any constraints
        constraints = context.get("constraints", [])
        if constraints:
            result.key_factors.append(f"Constraints: {len(constraints)}")
            result.considerations.extend(constraints[:3])

        # Build answer based on factors
        if urgency == "high":
            result.answer = "Proceed - high urgency indicates action needed"
            result.confidence = Confidence.HIGH
        elif constraints:
            result.answer = "Proceed with caution - constraints noted"
            result.confidence = Confidence.MODERATE
        else:
            result.answer = "Proceed - conditions favorable"
            result.confidence = Confidence.HIGH

    def _reason_analytically(
        self,
        result: ReasoningResult,
        context: dict[str, Any],
    ) -> None:
        """Analytical reasoning - pure logic."""
        result.key_factors = [
            f"Context items: {len(context)}",
        ]

        # Simple decision tree
        if context.get("blocked"):
            result.answer = "No - blocked by constraints"
            result.confidence = Confidence.VERY_HIGH
        elif context.get("concerns"):
            result.answer = "Maybe - concerns need review"
            result.confidence = Confidence.MODERATE
        else:
            result.answer = "Yes - no blocking factors"
            result.confidence = Confidence.HIGH

    def _reason_intuitively(
        self,
        result: ReasoningResult,
        context: dict[str, Any],
    ) -> None:
        """Intuitive reasoning - pattern recognition."""
        result.key_factors = [
            "Pattern-based assessment",
        ]

        # Trust the pattern
        if context.get("positive_signals", 0) > context.get("negative_signals", 0):
            result.answer = "Yes - positive pattern detected"
            result.confidence = Confidence.HIGH
        elif context.get("negative_signals", 0) > 0:
            result.answer = "Uncertain - mixed signals"
            result.confidence = Confidence.LOW
        else:
            result.answer = "Possibly - insufficient pattern data"
            result.confidence = Confidence.MODERATE

    def _reason_emotionally(
        self,
        result: ReasoningResult,
        context: dict[str, Any],
    ) -> None:
        """Emotional reasoning - feeling-informed."""
        mood = context.get("mood", "neutral")
        result.key_factors = [f"Current mood: {mood}"]

        positive_moods = {"content", "joyful", "energized", "curious", "hopeful"}
        if mood.lower() in positive_moods:
            result.answer = "Yes - feels right"
            result.confidence = Confidence.MODERATE
        else:
            result.answer = "Wait - doesn't feel right yet"
            result.confidence = Confidence.MODERATE

    def _reason_with_wisdom(
        self,
        result: ReasoningResult,
        context: dict[str, Any],
    ) -> None:
        """Wisdom-based reasoning - principle-informed."""
        result.key_factors = []

        wisdom = context.get("wisdom", [])
        if wisdom:
            for w in wisdom[:3]:
                result.key_factors.append(f"* {w}")
                result.wisdom_applied.append(w)

        mission = context.get("mission")
        if mission:
            result.key_factors.append(f"Purpose: {mission}")
            result.answer = f"Align with mission: {mission[:30]}"
            result.confidence = Confidence.HIGH
        else:
            result.answer = "Seek clarity on purpose first"
            result.confidence = Confidence.MODERATE

    def last_result(self) -> ReasoningResult | None:
        """Get the last reasoning result."""
        return self._last_result


# Singleton
_engine_instance: ReasoningEngine | None = None


def get_reasoning_engine() -> ReasoningEngine:
    """Get or create the singleton ReasoningEngine."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = ReasoningEngine()
    return _engine_instance


def reason(
    question: str,
    context: dict[str, Any] | None = None,
    reasoning_type: ReasoningType = ReasoningType.HOLISTIC,
) -> ReasoningResult:
    """Convenience function to reason about a question.

    Args:
        question: The question to reason about
        context: Additional context
        reasoning_type: Type of reasoning to apply

    Returns:
        ReasoningResult with answer and supporting info
    """
    engine = get_reasoning_engine()
    return engine.reason(question, context, reasoning_type)


__all__ = [
    "ReasoningEngine",
    "ReasoningResult",
    "ReasoningType",
    "Confidence",
    "get_reasoning_engine",
    "reason",
]
