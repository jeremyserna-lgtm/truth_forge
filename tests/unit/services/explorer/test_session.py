"""Tests for explorer session module."""

from __future__ import annotations

from datetime import UTC, datetime

from truth_forge.services.explorer.models import (
    ExplorationConfig,
    Finding,
    Pattern,
    StruggleState,
)
from truth_forge.services.explorer.session import ExplorationSession


class TestExplorationSession:
    """Test ExplorationSession class."""

    def test_init(self) -> None:
        """Test ExplorationSession initialization."""
        config = ExplorationConfig()
        session = ExplorationSession(
            id="session-123",
            correlation_id="corr-123",
            config=config,
            started_at=datetime.now(UTC),
        )
        assert session.id == "session-123"
        assert session.current_iteration == 0
        assert len(session.findings) == 0

    def test_should_stop_manual(self) -> None:
        """Test should_stop when manually requested."""
        config = ExplorationConfig()
        session = ExplorationSession(
            id="test",
            correlation_id="test",
            config=config,
            started_at=datetime.now(UTC),
        )
        session.request_stop("Manual stop")
        assert session.should_stop is True
        assert session.stop_reason == "Manual stop"

    def test_should_stop_high_resonance(self) -> None:
        """Test should_stop when high resonance achieved."""
        config = ExplorationConfig()
        session = ExplorationSession(
            id="test",
            correlation_id="test",
            config=config,
            started_at=datetime.now(UTC),
        )
        # Set high resonance - need to add findings to update metrics properly
        finding = Finding(
            id="test",
            tool_name="test",
            tool_category="test",
            iteration=1,
            raw_result="test",
            analysis="test",
            cognitive_stage=5,
            thought_type="manifestation",
            pantheon_mode="mirror",
            emotional_state="resonance",
            correlation_id="test",
            confidence=0.9,
        )
        # Add multiple findings to get high resonance
        for _ in range(10):
            session.add_finding(finding, StruggleState.SURPLUS)

        # Manually set high resonance score
        session.resonance_metrics.total_findings = 10
        session.resonance_metrics.stage_5_findings = 10
        session.resonance_metrics.manifestation_count = 10
        session.resonance_metrics.resonance_count = 10
        session.resonance_metrics.surplus_value_count = 10

        assert session.should_stop is True
        assert session.stop_reason is not None

    def test_add_finding_swimming(self) -> None:
        """Test adding swimming finding."""
        config = ExplorationConfig()
        session = ExplorationSession(
            id="test",
            correlation_id="test",
            config=config,
            started_at=datetime.now(UTC),
        )
        finding = Finding(
            id="test",
            tool_name="test",
            tool_category="test",
            iteration=1,
            raw_result="test",
            analysis="test",
            cognitive_stage=5,
            thought_type="manifestation",
            pantheon_mode="mirror",
            emotional_state="resonance",
            correlation_id="test",
            confidence=0.9,
        )
        session.add_finding(finding, StruggleState.SWIMMING)
        assert len(session.findings) == 1
        assert session.discarded_count == 0

    def test_add_finding_drowning(self) -> None:
        """Test adding drowning finding (should be discarded)."""
        config = ExplorationConfig()
        session = ExplorationSession(
            id="test",
            correlation_id="test",
            config=config,
            started_at=datetime.now(UTC),
        )
        finding = Finding(
            id="test",
            tool_name="test",
            tool_category="test",
            iteration=1,
            raw_result="test",
            analysis="test",
            cognitive_stage=3,
            thought_type="reflection",
            pantheon_mode="mirror",
            emotional_state="curiosity",
            correlation_id="test",
            confidence=0.5,
        )
        session.add_finding(finding, StruggleState.DROWNING)
        assert len(session.findings) == 0
        assert session.discarded_count == 1

    def test_add_finding_surplus(self) -> None:
        """Test adding surplus finding (becomes insight atom)."""
        config = ExplorationConfig()
        session = ExplorationSession(
            id="test",
            correlation_id="test",
            config=config,
            started_at=datetime.now(UTC),
        )
        finding = Finding(
            id="test",
            tool_name="test",
            tool_category="test",
            iteration=1,
            raw_result="test",
            analysis="test",
            cognitive_stage=5,
            thought_type="manifestation",
            pantheon_mode="mirror",
            emotional_state="resonance",
            correlation_id="test",
            confidence=0.9,
        )
        session.add_finding(finding, StruggleState.SURPLUS)
        assert len(session.findings) == 1
        assert len(session.insight_atoms) == 1

    def test_update_resonance_metrics(self) -> None:
        """Test resonance metrics update."""
        config = ExplorationConfig()
        session = ExplorationSession(
            id="test",
            correlation_id="test",
            config=config,
            started_at=datetime.now(UTC),
        )
        finding = Finding(
            id="test",
            tool_name="test",
            tool_category="test",
            iteration=1,
            raw_result="test",
            analysis="test",
            cognitive_stage=5,
            thought_type="manifestation",
            pantheon_mode="mirror",
            emotional_state="resonance",
            correlation_id="test",
            confidence=0.9,
        )
        session.add_finding(finding, StruggleState.SURPLUS)
        assert session.resonance_metrics.total_findings == 1
        assert session.resonance_metrics.stage_5_findings == 1
        assert session.resonance_metrics.manifestation_count == 1
        assert session.resonance_metrics.resonance_count == 1
        assert session.resonance_metrics.surplus_value_count == 1

    def test_add_pattern(self) -> None:
        """Test adding pattern."""
        config = ExplorationConfig()
        session = ExplorationSession(
            id="test",
            correlation_id="test",
            config=config,
            started_at=datetime.now(UTC),
        )
        pattern = Pattern(
            id="pattern-123",
            pattern_type="recurring_text",
            description="Test pattern",
        )
        session.add_pattern(pattern)
        assert len(session.patterns) == 1
