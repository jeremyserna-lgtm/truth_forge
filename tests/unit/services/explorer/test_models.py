"""Tests for explorer models module."""

from __future__ import annotations

from datetime import UTC, datetime

from truth_forge.services.explorer.models import (
    ExplorationConfig,
    ExplorationDepth,
    ExplorationReport,
    Finding,
    IterationBudget,
    Pattern,
    ResonanceMetrics,
    Significance,
    StruggleState,
    ToolResult,
)


class TestEnums:
    """Test enum classes."""

    def test_exploration_depth(self) -> None:
        """Test ExplorationDepth enum."""
        assert ExplorationDepth.SHALLOW.value == "shallow"
        assert ExplorationDepth.MEDIUM.value == "medium"
        assert ExplorationDepth.DEEP.value == "deep"

    def test_significance(self) -> None:
        """Test Significance enum."""
        assert Significance.LOW.value == "low"
        assert Significance.MEDIUM.value == "medium"
        assert Significance.HIGH.value == "high"

    def test_struggle_state(self) -> None:
        """Test StruggleState enum."""
        assert StruggleState.DROWNING.value == "drowning"
        assert StruggleState.SWIMMING.value == "swimming"
        assert StruggleState.SURPLUS.value == "surplus"


class TestExplorationConfig:
    """Test ExplorationConfig model."""

    def test_defaults(self) -> None:
        """Test default configuration values."""
        config = ExplorationConfig()
        assert config.iterations == 5
        assert config.depth == ExplorationDepth.MEDIUM
        assert config.focus_area is None

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = ExplorationConfig(
            iterations=10,
            focus_area="Test area",
            depth=ExplorationDepth.DEEP,
        )
        assert config.iterations == 10
        assert config.focus_area == "Test area"
        assert config.depth == ExplorationDepth.DEEP


class TestResonanceMetrics:
    """Test ResonanceMetrics dataclass."""

    def test_total_resonance_score_zero(self) -> None:
        """Test total_resonance_score when no findings."""
        metrics = ResonanceMetrics()
        assert metrics.total_resonance_score == 0.0

    def test_total_resonance_score_calculation(self) -> None:
        """Test total_resonance_score calculation."""
        metrics = ResonanceMetrics(
            total_findings=10,
            stage_5_findings=8,
            manifestation_count=7,
            resonance_count=6,
            surplus_value_count=5,
        )
        score = metrics.total_resonance_score
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be high with good metrics

    def test_is_exist_now_ready_true(self) -> None:
        """Test is_exist_now_ready when conditions met."""
        metrics = ResonanceMetrics(
            total_findings=10,
            stage_5_findings=8,
            surplus_value_count=3,
        )
        # Set score manually for test
        metrics.total_findings = 10
        metrics.stage_5_findings = 8
        metrics.manifestation_count = 8
        metrics.resonance_count = 8
        metrics.surplus_value_count = 3

        assert metrics.is_exist_now_ready is True

    def test_is_exist_now_ready_false(self) -> None:
        """Test is_exist_now_ready when conditions not met."""
        metrics = ResonanceMetrics()
        assert metrics.is_exist_now_ready is False

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        metrics = ResonanceMetrics(total_findings=5)
        data = metrics.to_dict()
        assert data["total_findings"] == 5
        assert "total_resonance_score" in data


class TestToolResult:
    """Test ToolResult model."""

    def test_creation(self) -> None:
        """Test creating ToolResult."""
        result = ToolResult(
            tool_name="test_tool",
            category="entity",
            content="Test content",
        )
        assert result.tool_name == "test_tool"
        assert result.category == "entity"
        assert result.success is True

    def test_with_error(self) -> None:
        """Test ToolResult with error."""
        result = ToolResult(
            tool_name="test_tool",
            category="entity",
            content="",
            success=False,
            error="Tool failed",
        )
        assert result.success is False
        assert result.error == "Tool failed"


class TestFinding:
    """Test Finding model."""

    def test_creation(self) -> None:
        """Test creating Finding."""
        finding = Finding(
            id="finding-123",
            tool_name="test_tool",
            tool_category="entity",
            iteration=1,
            raw_result="Raw result",
            analysis="Analysis",
            cognitive_stage=5,
            thought_type="manifestation",
            pantheon_mode="mirror",
            emotional_state="resonance",
            correlation_id="corr-123",
            confidence=0.9,
        )
        assert finding.id == "finding-123"
        assert finding.cognitive_stage == 5
        assert finding.thought_type == "manifestation"

    def test_significance_high(self) -> None:
        """Test significance HIGH calculation."""
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
        assert finding.significance == Significance.HIGH

    def test_significance_medium(self) -> None:
        """Test significance MEDIUM calculation."""
        finding = Finding(
            id="test",
            tool_name="test",
            tool_category="test",
            iteration=1,
            raw_result="test",
            analysis="test",
            cognitive_stage=5,
            thought_type="reflection",
            pantheon_mode="mirror",
            emotional_state="clarity",
            correlation_id="test",
            confidence=0.8,
        )
        assert finding.significance == Significance.MEDIUM

    def test_significance_low(self) -> None:
        """Test significance LOW calculation."""
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
            confidence=0.7,
        )
        assert finding.significance == Significance.LOW

    def test_to_insight_atom_dict(self) -> None:
        """Test to_insight_atom_dict method."""
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
        atom_dict = finding.to_insight_atom_dict()
        assert atom_dict["content"] == "test"
        assert atom_dict["cognitive_stage"] == 5
        assert atom_dict["thought_type"] == "manifestation"


class TestPattern:
    """Test Pattern model."""

    def test_creation(self) -> None:
        """Test creating Pattern."""
        pattern = Pattern(
            id="pattern-123",
            pattern_type="recurring_text",
            description="Test pattern",
            supporting_findings=["finding-1", "finding-2"],
            frequency=5,
        )
        assert pattern.id == "pattern-123"
        assert pattern.frequency == 5
        assert len(pattern.supporting_findings) == 2


class TestIterationBudget:
    """Test IterationBudget dataclass."""

    def test_creation(self) -> None:
        """Test creating IterationBudget."""
        budget = IterationBudget(
            tools_per_iteration=5,
            max_findings_context=25,
            max_entities_per_query=100,
            synthesis_frequency=5,
            parallel_tool_calls=True,
        )
        assert budget.tools_per_iteration == 5
        assert budget.parallel_tool_calls is True

    def test_tokens_per_iteration(self) -> None:
        """Test tokens_per_iteration calculation."""
        budget = IterationBudget(
            tools_per_iteration=5,
            max_findings_context=25,
            max_entities_per_query=100,
            synthesis_frequency=5,
            parallel_tool_calls=True,
        )
        tokens = budget.tokens_per_iteration()
        assert tokens > 0
        # Should be (5 * 500) + (25 * 200) = 2500 + 5000 = 7500
        assert tokens == 7500


class TestExplorationReport:
    """Test ExplorationReport model."""

    def test_creation(self) -> None:
        """Test creating ExplorationReport."""
        config = ExplorationConfig()
        report = ExplorationReport(
            session_id="session-123",
            config=config,
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            iterations_completed=5,
        )
        assert report.session_id == "session-123"
        assert report.iterations_completed == 5

    def test_duration_seconds(self) -> None:
        """Test duration_seconds property."""
        from datetime import timedelta

        start = datetime.now(UTC)
        end = start + timedelta(seconds=10)

        config = ExplorationConfig()
        report = ExplorationReport(
            session_id="test",
            config=config,
            started_at=start,
            completed_at=end,
            iterations_completed=1,
        )
        assert report.duration_seconds == 10.0

    def test_to_total_resonance_packet(self) -> None:
        """Test to_total_resonance_packet method."""
        config = ExplorationConfig()
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

        report = ExplorationReport(
            session_id="test",
            config=config,
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            iterations_completed=1,
            findings=[finding],
        )

        packet = report.to_total_resonance_packet()
        assert len(packet) == 1  # HIGH significance finding included
