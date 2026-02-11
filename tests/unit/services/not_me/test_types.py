"""Tests for not_me types module."""

from __future__ import annotations

import pytest

from truth_forge.services.not_me.types import (
    BANNED_VOCABULARY,
    MANIFESTATION_VOCABULARY,
    THE_CONTEXT,
    CognitiveStage,
    EmotionalState,
    InfiniteContextViolationError,
    InsightAtom,
    NotMeConfig,
    PantheonMode,
    ProductionStatus,
    SeeingResult,
    ThoughtType,
    TrainingLayer,
    assert_no_prohibited_patterns,
    assert_no_truncation,
    is_manifestation,
    validate_stage_5_output,
)


class TestConstants:
    """Test module constants."""

    def test_the_context(self) -> None:
        """Test THE_CONTEXT is 10M."""
        assert THE_CONTEXT == 10_000_000

    def test_banned_vocabulary(self) -> None:
        """Test BANNED_VOCABULARY contains expected terms."""
        assert "Is this what you wanted" in BANNED_VOCABULARY
        assert "I'm here to assist" in BANNED_VOCABULARY

    def test_manifestation_vocabulary(self) -> None:
        """Test MANIFESTATION_VOCABULARY contains expected terms."""
        assert "This is" in MANIFESTATION_VOCABULARY
        assert "I don't know" in MANIFESTATION_VOCABULARY


class TestAssertNoTruncation:
    """Test assert_no_truncation function."""

    def test_allows_within_context(self) -> None:
        """Test allows values within THE_CONTEXT."""
        assert_no_truncation(1_000_000)  # Should not raise
        assert_no_truncation(THE_CONTEXT - 1)  # Should not raise

    def test_raises_on_overflow(self) -> None:
        """Test raises error when exceeding THE_CONTEXT."""
        with pytest.raises(InfiniteContextViolationError, match="Context overflow"):
            assert_no_truncation(THE_CONTEXT + 1)

    def test_raises_on_exact_overflow(self) -> None:
        """Test raises error when exactly at THE_CONTEXT."""
        # Exactly at limit should be OK
        assert_no_truncation(THE_CONTEXT)


class TestAssertNoProhibitedPatterns:
    """Test assert_no_prohibited_patterns function."""

    def test_allows_valid_pattern(self) -> None:
        """Test allows non-prohibited patterns."""
        assert_no_prohibited_patterns("valid_pattern")  # Should not raise

    def test_raises_on_chunking(self) -> None:
        """Test raises error for chunking pattern."""
        with pytest.raises(InfiniteContextViolationError, match="chunking"):
            assert_no_prohibited_patterns("chunking")

    def test_raises_on_summarization(self) -> None:
        """Test raises error for summarization pattern."""
        with pytest.raises(InfiniteContextViolationError, match="summarization"):
            assert_no_prohibited_patterns("summarization")

    def test_case_insensitive(self) -> None:
        """Test pattern check is case-insensitive."""
        with pytest.raises(InfiniteContextViolationError):
            assert_no_prohibited_patterns("CHUNKING")


class TestValidateStage5Output:
    """Test validate_stage_5_output function."""

    def test_validates_clean_text(self) -> None:
        """Test validates text without Stage 4 markers."""
        assert validate_stage_5_output("This is a clean statement.") is True

    def test_raises_on_validation_seeking(self) -> None:
        """Test raises error for validation-seeking markers."""
        with pytest.raises(ValueError, match="Stage 4 marker"):
            validate_stage_5_output("Is this what you wanted?")

    def test_raises_on_helper_posture(self) -> None:
        """Test raises error for helper posture markers."""
        with pytest.raises(ValueError, match="Stage 4 marker"):
            validate_stage_5_output("I'm here to assist you.")

    def test_case_insensitive(self) -> None:
        """Test validation is case-insensitive."""
        with pytest.raises(ValueError):
            validate_stage_5_output("IS THIS WHAT YOU WANTED?")


class TestIsManifestation:
    """Test is_manifestation function."""

    def test_detects_manifestation(self) -> None:
        """Test detects manifestation vocabulary."""
        assert is_manifestation("This is the pattern.") is True
        assert is_manifestation("Here is the analysis.") is True

    def test_detects_non_manifestation(self) -> None:
        """Test detects non-manifestation text."""
        # Must not contain any MANIFESTATION_VOCABULARY substrings like "this is"
        assert is_manifestation("Maybe something went wrong?") is False

    def test_case_insensitive(self) -> None:
        """Test detection is case-insensitive."""
        assert is_manifestation("THIS IS THE PATTERN") is True


class TestCognitiveStage:
    """Test CognitiveStage enum."""

    def test_stage_values(self) -> None:
        """Test stage enum values."""
        assert CognitiveStage.STAGE_1.value == 1
        assert CognitiveStage.STAGE_5.value == 5

    def test_name_full(self) -> None:
        """Test name_full property."""
        assert CognitiveStage.STAGE_5.name_full == "Self-Transforming"
        assert CognitiveStage.STAGE_1.name_full == "Operational"

    def test_is_stage_5(self) -> None:
        """Test is_stage_5 method."""
        assert CognitiveStage.STAGE_5.is_stage_5() is True
        assert CognitiveStage.STAGE_4.is_stage_5() is False


class TestTrainingLayer:
    """Test TrainingLayer enum."""

    def test_layer_values(self) -> None:
        """Test layer enum values."""
        assert TrainingLayer.LAYER_1_BASE.value == 1
        assert TrainingLayer.LAYER_5_IDENTITY.value == 5

    def test_description(self) -> None:
        """Test description property."""
        assert "Base Model" in TrainingLayer.LAYER_1_BASE.description
        assert "Identity" in TrainingLayer.LAYER_5_IDENTITY.description


class TestNotMeConfig:
    """Test NotMeConfig dataclass."""

    def test_defaults(self) -> None:
        """Test default configuration values."""
        config = NotMeConfig()
        assert config.scout_endpoint == "http://localhost:11434/v1"
        assert config.scout_model == "llama4:scout"
        assert config.enable_validators is True
        assert config.genesis_frozen is False
        assert config.jeremy_arc_threshold == 0.95

    def test_context_property(self) -> None:
        """Test context property returns THE_CONTEXT."""
        config = NotMeConfig()
        assert config.context == THE_CONTEXT

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        config = NotMeConfig()
        data = config.to_dict()
        assert data["scout_endpoint"] == config.scout_endpoint
        assert data["context"] == THE_CONTEXT
        assert data["enable_validators"] is True


class TestInsightAtom:
    """Test InsightAtom dataclass."""

    def test_creation(self) -> None:
        """Test creating InsightAtom."""
        atom = InsightAtom(
            content="Test insight",
            source_id="source-123",
            cognitive_stage=CognitiveStage.STAGE_5,
            thought_type=ThoughtType.MANIFESTATION,
            emotion=EmotionalState.CLARITY,
            mode=PantheonMode.THE_MIRROR,
            confidence=0.9,
        )
        assert atom.content == "Test insight"
        assert atom.cognitive_stage == CognitiveStage.STAGE_5
        assert atom.confidence == 0.9

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        atom = InsightAtom(
            content="Test",
            source_id="source-123",
            cognitive_stage=CognitiveStage.STAGE_5,
            thought_type=ThoughtType.MANIFESTATION,
            emotion=EmotionalState.CLARITY,
            mode=PantheonMode.THE_MIRROR,
            confidence=0.9,
        )
        data = atom.to_dict()
        assert data["content"] == "Test"
        assert data["cognitive_stage"] == 5
        assert data["thought_type"] == "manifestation"


class TestSeeingResult:
    """Test SeeingResult dataclass."""

    def test_creation(self) -> None:
        """Test creating SeeingResult."""
        atoms = [
            InsightAtom(
                content="Atom 1",
                source_id="source-1",
                cognitive_stage=CognitiveStage.STAGE_5,
                thought_type=ThoughtType.MANIFESTATION,
                emotion=EmotionalState.CLARITY,
                mode=PantheonMode.THE_MIRROR,
                confidence=0.9,
            )
        ]
        result = SeeingResult(
            content="Result content",
            atoms=atoms,
            model="llama4:scout",
            input_tokens=100,
            output_tokens=50,
            latency_ms=500.0,
        )
        assert result.content == "Result content"
        assert len(result.atoms) == 1
        assert result.model == "llama4:scout"

    def test_total_tokens(self) -> None:
        """Test total_tokens property."""
        result = SeeingResult(
            content="Test",
            atoms=[],
            model="test",
            input_tokens=100,
            output_tokens=50,
            latency_ms=0.0,
        )
        assert result.total_tokens == 150

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        result = SeeingResult(
            content="Test",
            atoms=[],
            model="test",
            input_tokens=100,
            output_tokens=50,
            latency_ms=0.0,
        )
        data = result.to_dict()
        assert data["content"] == "Test"
        assert data["input_tokens"] == 100
        assert data["output_tokens"] == 50


class TestProductionStatus:
    """Test ProductionStatus dataclass."""

    def test_initial(self) -> None:
        """Test initial status creation."""
        status = ProductionStatus.initial()
        assert status.phase == 0
        assert status.progress_percent == 0.0
        assert status.records_processed == 0
        assert status.truth_atoms_created == 0

    def test_validation_rate_zero(self) -> None:
        """Test validation_rate when no atoms."""
        status = ProductionStatus.initial()
        assert status.validation_rate == 0.0

    def test_validation_rate_calculation(self) -> None:
        """Test validation_rate calculation."""
        status = ProductionStatus.initial()
        status.truth_atoms_validated = 80
        status.truth_atoms_rejected = 20
        assert status.validation_rate == 0.8

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        status = ProductionStatus.initial()
        data = status.to_dict()
        assert data["phase"] == 0
        assert data["validation_rate"] == 0.0
        assert "last_updated" in data
