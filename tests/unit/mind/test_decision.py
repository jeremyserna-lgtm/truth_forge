"""Tests for decision module.

Tests the decision-making engine.
"""

from __future__ import annotations

import pytest

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


class TestDecisionUrgency:
    """Tests for DecisionUrgency enum."""

    def test_urgency_values(self) -> None:
        """Test urgency values."""
        assert DecisionUrgency.IMMEDIATE.value == "immediate"
        assert DecisionUrgency.SOON.value == "soon"
        assert DecisionUrgency.PLANNED.value == "planned"
        assert DecisionUrgency.REFLECTIVE.value == "reflective"


class TestDecisionType:
    """Tests for DecisionType enum."""

    def test_type_values(self) -> None:
        """Test decision type values."""
        assert DecisionType.PROCEED.value == "proceed"
        assert DecisionType.CHOOSE.value == "choose"
        assert DecisionType.PRIORITIZE.value == "prioritize"
        assert DecisionType.ALLOCATE.value == "allocate"
        assert DecisionType.DELEGATE.value == "delegate"


class TestDecisionOutcome:
    """Tests for DecisionOutcome enum."""

    def test_outcome_values(self) -> None:
        """Test outcome values."""
        assert DecisionOutcome.PROCEED.value == "proceed"
        assert DecisionOutcome.WAIT.value == "wait"
        assert DecisionOutcome.DECLINE.value == "decline"
        assert DecisionOutcome.DEFER.value == "defer"
        assert DecisionOutcome.ESCALATE.value == "escalate"


class TestDecisionContext:
    """Tests for DecisionContext dataclass."""

    def test_default_values(self) -> None:
        """Test default context values."""
        ctx = DecisionContext()
        assert ctx.question == ""
        assert ctx.decision_type == DecisionType.PROCEED
        assert ctx.urgency == DecisionUrgency.PLANNED
        assert ctx.options == []

    def test_custom_values(self) -> None:
        """Test custom context values."""
        ctx = DecisionContext(
            question="What to do?",
            decision_type=DecisionType.CHOOSE,
            urgency=DecisionUrgency.IMMEDIATE,
            options=["Option A", "Option B"],
            must_respect=["Constraint 1"],
        )
        assert ctx.question == "What to do?"
        assert ctx.decision_type == DecisionType.CHOOSE
        assert ctx.urgency == DecisionUrgency.IMMEDIATE
        assert len(ctx.options) == 2
        assert len(ctx.must_respect) == 1

    def test_to_dict(self) -> None:
        """Test converting to dictionary."""
        ctx = DecisionContext(
            question="Test?",
            decision_type=DecisionType.PRIORITIZE,
            urgency=DecisionUrgency.SOON,
        )
        data = ctx.to_dict()

        assert data["question"] == "Test?"
        assert data["decision_type"] == "prioritize"
        assert data["urgency"] == "soon"


class TestDecision:
    """Tests for Decision dataclass."""

    def test_default_values(self) -> None:
        """Test default decision values."""
        decision = Decision()
        assert decision.decision_id.startswith("dec_")
        assert decision.outcome == DecisionOutcome.WAIT
        assert decision.choice == ""
        assert decision.confidence == 0.5

    def test_custom_values(self) -> None:
        """Test custom decision values."""
        ctx = DecisionContext(question="Test?")
        decision = Decision(
            context=ctx,
            outcome=DecisionOutcome.PROCEED,
            choice="Go ahead",
            reasoning="All clear",
            confidence=0.9,
        )
        assert decision.context is ctx
        assert decision.outcome == DecisionOutcome.PROCEED
        assert decision.choice == "Go ahead"
        assert decision.confidence == 0.9

    def test_summary(self) -> None:
        """Test summary generation."""
        ctx = DecisionContext(question="Should we proceed?")
        decision = Decision(
            context=ctx,
            outcome=DecisionOutcome.PROCEED,
            choice="Yes",
            reasoning="Conditions favorable",
            factors_for=["Good timing"],
            factors_against=["Minor risk"],
            risks=["Small delay possible"],
            next_steps=["Execute plan"],
        )
        summary = decision.summary()

        assert "Should we proceed?" in summary
        assert "PROCEED" in summary
        assert "[OK]" in summary

    def test_summary_different_outcomes(self) -> None:
        """Test summary with different outcomes."""
        for outcome, emoji in [
            (DecisionOutcome.WAIT, "[..]"),
            (DecisionOutcome.DECLINE, "[NO]"),
            (DecisionOutcome.DEFER, "[>>]"),
            (DecisionOutcome.ESCALATE, "[^^]"),
        ]:
            decision = Decision(outcome=outcome)
            summary = decision.summary()
            assert emoji in summary

    def test_to_dict(self) -> None:
        """Test converting to dictionary."""
        ctx = DecisionContext(question="Test?")
        decision = Decision(
            context=ctx,
            outcome=DecisionOutcome.PROCEED,
            choice="Go",
            confidence=0.8,
        )
        data = decision.to_dict()

        assert data["outcome"] == "proceed"
        assert data["choice"] == "Go"
        assert data["confidence"] == 0.8
        assert data["context"]["question"] == "Test?"
        assert "decision_id" in data
        assert "timestamp" in data


class TestDecisionMaker:
    """Tests for DecisionMaker class."""

    def test_init(self) -> None:
        """Test maker initialization."""
        maker = DecisionMaker()
        assert maker.recent() == []

    def test_decide_proceed_favorable(self) -> None:
        """Test proceed decision with favorable conditions."""
        maker = DecisionMaker()
        decision = maker.decide(
            "Should we proceed?",
            urgency=DecisionUrgency.IMMEDIATE,
        )

        assert decision.outcome == DecisionOutcome.PROCEED
        assert decision.confidence > 0.5

    def test_decide_proceed_with_constraints(self) -> None:
        """Test proceed decision with constraints."""
        maker = DecisionMaker()
        decision = maker.decide(
            "Can we proceed?",
            constraints=["Budget limit", "Time limit", "Resource limit"],
        )

        # Many constraints should lower score
        assert decision.context is not None
        assert len(decision.context.must_respect) == 3

    def test_decide_proceed_reflective(self) -> None:
        """Test proceed decision with reflective urgency."""
        maker = DecisionMaker()
        decision = maker.decide(
            "Should we proceed carefully?",
            urgency=DecisionUrgency.REFLECTIVE,
        )

        assert "caution" in decision.reasoning.lower() or decision.factors_against

    def test_decide_choose(self) -> None:
        """Test choose decision."""
        maker = DecisionMaker()
        decision = maker.decide(
            "Which option?",
            decision_type=DecisionType.CHOOSE,
            options=["Option A", "Option B", "Option C"],
        )

        assert decision.outcome == DecisionOutcome.PROCEED
        assert decision.choice == "Option A"
        assert "Option B" in str(decision.next_steps)

    def test_decide_choose_no_options(self) -> None:
        """Test choose decision with no options."""
        maker = DecisionMaker()
        decision = maker.decide(
            "Which option?",
            decision_type=DecisionType.CHOOSE,
            options=[],
        )

        assert decision.outcome == DecisionOutcome.DEFER
        assert "No options" in decision.reasoning

    def test_decide_prioritize(self) -> None:
        """Test prioritize decision."""
        maker = DecisionMaker()
        decision = maker.decide(
            "What order?",
            decision_type=DecisionType.PRIORITIZE,
            options=["Task 1", "Task 2", "Task 3"],
        )

        assert decision.outcome == DecisionOutcome.PROCEED
        assert ">" in decision.choice

    def test_decide_prioritize_no_items(self) -> None:
        """Test prioritize decision with no items."""
        maker = DecisionMaker()
        decision = maker.decide(
            "What order?",
            decision_type=DecisionType.PRIORITIZE,
            options=[],
        )

        assert decision.outcome == DecisionOutcome.DEFER

    def test_recent_tracking(self) -> None:
        """Test recent decisions tracking."""
        maker = DecisionMaker()

        maker.decide("Decision 1")
        maker.decide("Decision 2")
        maker.decide("Decision 3")

        recent = maker.recent(2)
        assert len(recent) == 2
        assert recent[0].context is not None
        assert recent[0].context.question == "Decision 2"

    def test_decision_recorded(self) -> None:
        """Test that decisions are recorded in history."""
        maker = DecisionMaker()

        decision = maker.decide("Test decision")

        assert decision in maker._history


class TestGetDecisionMaker:
    """Tests for get_decision_maker function."""

    def test_returns_singleton(self) -> None:
        """Test that get_decision_maker returns singleton."""
        import truth_forge.mind.decision as decision_module

        decision_module._maker_instance = None

        maker1 = get_decision_maker()
        maker2 = get_decision_maker()

        assert maker1 is maker2


class TestDecideFunction:
    """Tests for decide convenience function."""

    def test_decide_function(self) -> None:
        """Test decide convenience function."""
        decision = decide("Test question")

        assert decision.context is not None
        assert decision.context.question == "Test question"
        assert decision.outcome in DecisionOutcome

    def test_decide_with_options(self) -> None:
        """Test decide with options."""
        decision = decide(
            "Which one?",
            decision_type=DecisionType.CHOOSE,
            options=["A", "B"],
        )

        assert decision.choice != ""
