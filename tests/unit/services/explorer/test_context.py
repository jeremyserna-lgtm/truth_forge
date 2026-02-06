"""Tests for explorer context module."""

from __future__ import annotations

from truth_forge.services.explorer.context import (
    EXPLORER_CONTEXT_LIMIT,
    EXPLORER_FALLBACK_ORDER,
    EXPLORER_MODEL,
    EXPLORER_MODEL_TIERS,
    ContextManager,
    SessionMemory,
    apply_struggle_filter,
    classify_struggle_state,
    get_explorer_context,
)
from truth_forge.services.explorer.models import Finding, StruggleState


class TestConstants:
    """Test module constants."""

    def test_explorer_model(self) -> None:
        """Test EXPLORER_MODEL constant."""
        assert EXPLORER_MODEL == "qwen2.5:14b"

    def test_explorer_context_limit(self) -> None:
        """Test EXPLORER_CONTEXT_LIMIT constant."""
        assert EXPLORER_CONTEXT_LIMIT == 500_000

    def test_explorer_model_tiers(self) -> None:
        """Test EXPLORER_MODEL_TIERS dictionary."""
        assert "qwen2.5:32b" in EXPLORER_MODEL_TIERS
        assert EXPLORER_MODEL_TIERS["qwen2.5:14b"][0] == 500_000

    def test_explorer_fallback_order(self) -> None:
        """Test EXPLORER_FALLBACK_ORDER list."""
        assert len(EXPLORER_FALLBACK_ORDER) > 0
        assert EXPLORER_FALLBACK_ORDER[0] == "qwen2.5:14b"


class TestGetExplorerContext:
    """Test get_explorer_context function."""

    def test_high_memory(self) -> None:
        """Test context for high memory systems."""
        context = get_explorer_context(256)
        assert context == 1_000_000

    def test_medium_memory(self) -> None:
        """Test context for medium memory systems."""
        context = get_explorer_context(128)
        assert context == 500_000

    def test_low_memory(self) -> None:
        """Test context for low memory systems."""
        context = get_explorer_context(64)
        assert context == 256_000

    def test_minimal_memory(self) -> None:
        """Test context for minimal memory systems."""
        context = get_explorer_context(32)
        assert context == 128_000


class TestContextManager:
    """Test ContextManager class."""

    def test_init_default(self) -> None:
        """Test initialization with default context."""
        manager = ContextManager()
        assert manager.operational_context > 0

    def test_init_custom(self) -> None:
        """Test initialization with custom context."""
        manager = ContextManager(operational_context=1_000_000)
        assert manager.operational_context == 1_000_000

    def test_estimate_tokens(self) -> None:
        """Test token estimation."""
        manager = ContextManager()
        tokens = manager.estimate_tokens("test" * 100)
        assert tokens > 0
        assert tokens == len("test" * 100) // 4  # 4 chars per token

    def test_can_fit(self) -> None:
        """Test can_fit method."""
        manager = ContextManager(operational_context=1000)
        assert manager.can_fit("short text") is True
        # Very long text should not fit
        long_text = "x" * 10000
        assert manager.can_fit(long_text) is False

    def test_get_budget(self) -> None:
        """Test get_budget method."""
        manager = ContextManager(operational_context=1000)
        budget = manager.get_budget()
        assert budget == 800  # 80% of 1000

    def test_calculate_iteration_budget_high_memory(self) -> None:
        """Test iteration budget for high memory."""
        manager = ContextManager()
        budget = manager.calculate_iteration_budget(256)
        assert budget.tools_per_iteration >= 5
        assert budget.parallel_tool_calls is True

    def test_calculate_iteration_budget_low_memory(self) -> None:
        """Test iteration budget for low memory."""
        manager = ContextManager()
        budget = manager.calculate_iteration_budget(32)
        assert budget.tools_per_iteration <= 3
        assert budget.max_findings_context <= 15


class TestSessionMemory:
    """Test SessionMemory class."""

    def test_init(self) -> None:
        """Test SessionMemory initialization."""
        memory = SessionMemory(max_findings=10)
        assert len(memory.findings) == 0

    def test_add_finding(self) -> None:
        """Test adding finding to memory."""
        memory = SessionMemory(max_findings=5)
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
        memory.add_finding(finding)
        assert len(memory.findings) == 1

    def test_max_findings_limit(self) -> None:
        """Test max findings limit."""
        memory = SessionMemory(max_findings=2)
        for i in range(5):
            finding = Finding(
                id=f"test-{i}",
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
            memory.add_finding(finding)

        # Should only keep last 2
        assert len(memory.findings) == 2

    def test_get_context_window(self) -> None:
        """Test getting context window string."""
        memory = SessionMemory(max_findings=5)
        finding = Finding(
            id="test",
            tool_name="test",
            tool_category="test",
            iteration=1,
            raw_result="test",
            analysis="test analysis",
            cognitive_stage=5,
            thought_type="manifestation",
            pantheon_mode="mirror",
            emotional_state="resonance",
            correlation_id="test",
            confidence=0.9,
        )
        memory.add_finding(finding)
        context = memory.get_context_window()
        assert "test analysis" in context


class TestClassifyStruggleState:
    """Test classify_struggle_state function."""

    def test_classify_swimming(self) -> None:
        """Test classifying swimming state."""
        finding = Finding(
            id="test",
            tool_name="test",
            tool_category="test",
            iteration=1,
            raw_result="test",
            analysis="This is clear. The pattern shows resolution.",
            cognitive_stage=5,
            thought_type="manifestation",
            pantheon_mode="mirror",
            emotional_state="clarity",
            correlation_id="test",
            confidence=0.8,
        )
        state = classify_struggle_state(finding)
        assert state == StruggleState.SWIMMING

    def test_classify_drowning(self) -> None:
        """Test classifying drowning state."""
        finding = Finding(
            id="test",
            tool_name="test",
            tool_category="test",
            iteration=1,
            raw_result="test",
            analysis="I'm confused. This doesn't make sense.",
            cognitive_stage=3,
            thought_type="reflection",
            pantheon_mode="mirror",
            emotional_state="tension",
            correlation_id="test",
            confidence=0.5,
        )
        state = classify_struggle_state(finding)
        assert state == StruggleState.DROWNING

    def test_classify_surplus(self) -> None:
        """Test classifying surplus state."""
        finding = Finding(
            id="test",
            tool_name="test",
            tool_category="test",
            iteration=1,
            raw_result="test",
            analysis="This reveals something new.",
            cognitive_stage=5,
            thought_type="manifestation",
            pantheon_mode="mirror",
            emotional_state="resonance",
            correlation_id="test",
            confidence=0.9,  # High confidence required for SURPLUS
        )
        state = classify_struggle_state(finding)
        assert state == StruggleState.SURPLUS


class TestApplyStruggleFilter:
    """Test apply_struggle_filter function."""

    def test_filter_keeps_swimming(self) -> None:
        """Test filter keeps swimming findings."""
        finding = Finding(
            id="test",
            tool_name="test",
            tool_category="test",
            iteration=1,
            raw_result="test",
            analysis="Clear analysis with resolution",
            cognitive_stage=5,
            thought_type="manifestation",
            pantheon_mode="mirror",
            emotional_state="clarity",
            correlation_id="test",
            confidence=0.8,
        )
        filtered, discarded = apply_struggle_filter([finding])
        assert len(filtered) == 1
        assert discarded == 0

    def test_filter_discards_drowning(self) -> None:
        """Test filter discards drowning findings."""
        finding = Finding(
            id="test",
            tool_name="test",
            tool_category="test",
            iteration=1,
            raw_result="test",
            analysis="I'm confused and don't understand this",
            cognitive_stage=3,
            thought_type="reflection",
            pantheon_mode="mirror",
            emotional_state="tension",
            correlation_id="test",
            confidence=0.5,
        )
        filtered, discarded = apply_struggle_filter([finding])
        assert len(filtered) == 0
        assert discarded == 1
