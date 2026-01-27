"""Tests for reasoning module.

Tests the cognitive reasoning engine.
"""

from __future__ import annotations

import pytest

from truth_forge.mind.reasoning import (
    Confidence,
    ReasoningEngine,
    ReasoningResult,
    ReasoningType,
    get_reasoning_engine,
    reason,
)


class TestReasoningType:
    """Tests for ReasoningType enum."""

    def test_type_values(self) -> None:
        """Test reasoning type values."""
        assert ReasoningType.ANALYTICAL.value == "analytical"
        assert ReasoningType.INTUITIVE.value == "intuitive"
        assert ReasoningType.EMOTIONAL.value == "emotional"
        assert ReasoningType.WISDOM.value == "wisdom"
        assert ReasoningType.HOLISTIC.value == "holistic"


class TestConfidence:
    """Tests for Confidence enum."""

    def test_confidence_values(self) -> None:
        """Test confidence level values."""
        assert Confidence.VERY_HIGH.value == "very_high"
        assert Confidence.HIGH.value == "high"
        assert Confidence.MODERATE.value == "moderate"
        assert Confidence.LOW.value == "low"
        assert Confidence.UNCERTAIN.value == "uncertain"


class TestReasoningResult:
    """Tests for ReasoningResult dataclass."""

    def test_default_values(self) -> None:
        """Test default reasoning result values."""
        result = ReasoningResult()
        assert result.question == ""
        assert result.answer == ""
        assert result.reasoning_type == ReasoningType.HOLISTIC
        assert result.confidence == Confidence.MODERATE
        assert result.key_factors == []

    def test_custom_values(self) -> None:
        """Test custom reasoning result values."""
        result = ReasoningResult(
            question="Should we proceed?",
            answer="Yes, proceed",
            reasoning_type=ReasoningType.ANALYTICAL,
            confidence=Confidence.HIGH,
            key_factors=["Factor 1", "Factor 2"],
        )
        assert result.question == "Should we proceed?"
        assert result.answer == "Yes, proceed"
        assert result.reasoning_type == ReasoningType.ANALYTICAL
        assert result.confidence == Confidence.HIGH
        assert len(result.key_factors) == 2

    def test_summary(self) -> None:
        """Test summary generation."""
        result = ReasoningResult(
            question="Test question",
            answer="Test answer",
            key_factors=["Factor 1"],
            wisdom_applied=["Wisdom 1"],
            concerns_noted=["Concern 1"],
        )
        summary = result.summary()

        assert "Test question" in summary
        assert "Test answer" in summary
        assert "Factor" in summary or "Key" in summary

    def test_to_dict(self) -> None:
        """Test converting to dictionary."""
        result = ReasoningResult(
            question="Test",
            answer="Answer",
            reasoning_type=ReasoningType.WISDOM,
            confidence=Confidence.HIGH,
        )
        data = result.to_dict()

        assert data["question"] == "Test"
        assert data["answer"] == "Answer"
        assert data["reasoning_type"] == "wisdom"
        assert data["confidence"] == "high"
        assert "timestamp" in data


class TestReasoningEngine:
    """Tests for ReasoningEngine class."""

    def test_init(self) -> None:
        """Test engine initialization."""
        engine = ReasoningEngine()
        assert engine.last_result() is None

    def test_reason_holistic(self) -> None:
        """Test holistic reasoning."""
        engine = ReasoningEngine()
        result = engine.reason(
            "Should we proceed?",
            context={"urgency": "high"},
            reasoning_type=ReasoningType.HOLISTIC,
        )

        assert result.question == "Should we proceed?"
        assert result.answer != ""
        assert result.reasoning_type == ReasoningType.HOLISTIC

    def test_reason_holistic_high_urgency(self) -> None:
        """Test holistic reasoning with high urgency."""
        engine = ReasoningEngine()
        result = engine.reason(
            "Should we act now?",
            context={"urgency": "high"},
            reasoning_type=ReasoningType.HOLISTIC,
        )

        assert "Proceed" in result.answer
        assert result.confidence == Confidence.HIGH

    def test_reason_holistic_with_constraints(self) -> None:
        """Test holistic reasoning with constraints."""
        engine = ReasoningEngine()
        result = engine.reason(
            "Can we do this?",
            context={"constraints": ["Budget limit", "Time limit"]},
            reasoning_type=ReasoningType.HOLISTIC,
        )

        assert result.confidence == Confidence.MODERATE
        assert "caution" in result.answer.lower()

    def test_reason_analytical(self) -> None:
        """Test analytical reasoning."""
        engine = ReasoningEngine()
        result = engine.reason(
            "Is this logical?",
            context={},
            reasoning_type=ReasoningType.ANALYTICAL,
        )

        assert result.reasoning_type == ReasoningType.ANALYTICAL
        assert result.answer != ""

    def test_reason_analytical_blocked(self) -> None:
        """Test analytical reasoning when blocked."""
        engine = ReasoningEngine()
        result = engine.reason(
            "Can we proceed?",
            context={"blocked": True},
            reasoning_type=ReasoningType.ANALYTICAL,
        )

        assert "No" in result.answer
        assert result.confidence == Confidence.VERY_HIGH

    def test_reason_analytical_with_concerns(self) -> None:
        """Test analytical reasoning with concerns."""
        engine = ReasoningEngine()
        result = engine.reason(
            "Should we do this?",
            context={"concerns": ["Risk 1"]},
            reasoning_type=ReasoningType.ANALYTICAL,
        )

        assert "Maybe" in result.answer
        assert result.confidence == Confidence.MODERATE

    def test_reason_intuitive(self) -> None:
        """Test intuitive reasoning."""
        engine = ReasoningEngine()
        result = engine.reason(
            "Does this feel right?",
            reasoning_type=ReasoningType.INTUITIVE,
        )

        assert result.reasoning_type == ReasoningType.INTUITIVE

    def test_reason_intuitive_positive_signals(self) -> None:
        """Test intuitive reasoning with positive signals."""
        engine = ReasoningEngine()
        result = engine.reason(
            "Good pattern?",
            context={"positive_signals": 5, "negative_signals": 1},
            reasoning_type=ReasoningType.INTUITIVE,
        )

        assert "Yes" in result.answer
        assert result.confidence == Confidence.HIGH

    def test_reason_intuitive_negative_signals(self) -> None:
        """Test intuitive reasoning with negative signals."""
        engine = ReasoningEngine()
        result = engine.reason(
            "Bad pattern?",
            context={"positive_signals": 0, "negative_signals": 3},
            reasoning_type=ReasoningType.INTUITIVE,
        )

        assert "Uncertain" in result.answer
        assert result.confidence == Confidence.LOW

    def test_reason_emotional(self) -> None:
        """Test emotional reasoning."""
        engine = ReasoningEngine()
        result = engine.reason(
            "How do I feel about this?",
            context={"mood": "joyful"},
            reasoning_type=ReasoningType.EMOTIONAL,
        )

        assert result.reasoning_type == ReasoningType.EMOTIONAL
        assert "Yes" in result.answer

    def test_reason_emotional_negative_mood(self) -> None:
        """Test emotional reasoning with negative mood."""
        engine = ReasoningEngine()
        result = engine.reason(
            "Should I act now?",
            context={"mood": "anxious"},
            reasoning_type=ReasoningType.EMOTIONAL,
        )

        assert "Wait" in result.answer

    def test_reason_wisdom(self) -> None:
        """Test wisdom-based reasoning."""
        engine = ReasoningEngine()
        result = engine.reason(
            "What is the right thing to do?",
            context={"mission": "Help others grow"},
            reasoning_type=ReasoningType.WISDOM,
        )

        assert result.reasoning_type == ReasoningType.WISDOM
        assert "mission" in result.answer.lower() or "Align" in result.answer

    def test_reason_wisdom_with_wisdom_list(self) -> None:
        """Test wisdom-based reasoning with wisdom list."""
        engine = ReasoningEngine()
        result = engine.reason(
            "What path to take?",
            context={"wisdom": ["Be patient", "Act with integrity"]},
            reasoning_type=ReasoningType.WISDOM,
        )

        assert len(result.wisdom_applied) > 0

    def test_last_result(self) -> None:
        """Test last_result tracking."""
        engine = ReasoningEngine()

        result1 = engine.reason("First question")
        result2 = engine.reason("Second question")

        assert engine.last_result() is result2
        assert engine.last_result().question == "Second question"

    def test_duration_recorded(self) -> None:
        """Test that duration is recorded."""
        engine = ReasoningEngine()
        result = engine.reason("Quick question")

        assert result.duration_ms >= 0


class TestGetReasoningEngine:
    """Tests for get_reasoning_engine function."""

    def test_returns_singleton(self) -> None:
        """Test that get_reasoning_engine returns singleton."""
        import truth_forge.mind.reasoning as reasoning_module

        reasoning_module._engine_instance = None

        engine1 = get_reasoning_engine()
        engine2 = get_reasoning_engine()

        assert engine1 is engine2


class TestReasonFunction:
    """Tests for reason convenience function."""

    def test_reason_function(self) -> None:
        """Test reason convenience function."""
        result = reason("Test question")

        assert result.question == "Test question"
        assert result.answer != ""

    def test_reason_with_context(self) -> None:
        """Test reason with context."""
        result = reason(
            "Should we proceed?",
            context={"urgency": "high"},
            reasoning_type=ReasoningType.HOLISTIC,
        )

        assert result.reasoning_type == ReasoningType.HOLISTIC
