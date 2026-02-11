"""Not-Me Service Types - Data structures for Not-Me production.

These types encode the ontology of the Not-Me system, aligning with
the Framework specifications in framework/ontology/.

ARCHITECTURAL FOUNDATION: 10M Context Window
The 10M context window is not a feature - it is the foundation upon which
all other architecture is built. See framework/10_INFINITE_CONTEXT.md.

PROHIBITED PATTERNS (Old Paradigm):
- Chunking strategies
- Summarization fallbacks
- Sliding window implementations
- Context truncation logic

REQUIRED PATTERNS (New Paradigm):
- Full document loading
- Complete history retention
- Signal preservation at all stages

MOLT LINEAGE:
- Source: New creation for Not-Me infrastructure
- Version: 1.0.0
- Date: 2026-02-01
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, ClassVar


# =============================================================================
# THE FOUNDATION: 10M CONTEXT WINDOW
# =============================================================================
#
# This is not configuration. This is not a feature. This IS the architecture.
#
# The 10M context window enables:
# - Full codebase analysis in single pass
# - Complete conversation history without truncation
# - Multi-document synthesis without chunking
# - True cognitive isomorphism (model holds what human holds)
#
# Hardware determines OPERATIONAL capacity (what runs TODAY).
# Architecture assumes 10M. Period.
# =============================================================================

# THE FOUNDATION - This is a constant, not a configuration
THE_CONTEXT: int = 10_000_000  # 10M tokens. THE architecture. Not negotiable.


class InfiniteContextViolationError(Exception):
    """Raised when code attempts to violate the 10M context architecture.

    The 10M context window IS the architecture. Code that requires:
    - Chunking
    - Summarization
    - Truncation
    - Sliding windows

    Is architecturally incompatible. Redesign, don't accommodate.
    """

    pass


def assert_no_truncation(current_tokens: int) -> None:
    """Assert that we're not truncating below THE_CONTEXT.

    This is a design-time check. If you're hitting this, your architecture
    is wrong - you're building for constraints that don't exist.

    Args:
        current_tokens: Current token count being processed.

    Raises:
        InfiniteContextViolationError: If truncation would occur.
    """
    if current_tokens > THE_CONTEXT:
        raise InfiniteContextViolationError(
            f"Context overflow: {current_tokens:,} > {THE_CONTEXT:,}. "
            "This indicates an architectural error. "
            "The 10M context IS the foundation - if you exceed it, "
            "redesign the operation, don't truncate."
        )


# These patterns are PROHIBITED in the 10M architecture
PROHIBITED_PATTERNS: tuple[str, ...] = (
    "chunking",
    "summarization",
    "sliding_window",
    "context_truncation",
    "rolling_buffer",
    "token_limit_fallback",
)


def assert_no_prohibited_patterns(pattern_name: str) -> None:
    """Assert that a prohibited pattern is not being used.

    Args:
        pattern_name: Name of the pattern being checked.

    Raises:
        InfiniteContextViolationError: If pattern is prohibited.
    """
    if pattern_name.lower() in PROHIBITED_PATTERNS:
        raise InfiniteContextViolationError(
            f"Prohibited pattern detected: '{pattern_name}'. "
            f"The 10M architecture does not permit: {PROHIBITED_PATTERNS}. "
            "See framework/10_INFINITE_CONTEXT.md"
        )


# =============================================================================
# THE GOLDEN RECORD (Truth Atoms)
# Reference: framework/11_GOLDEN_RECORD.md
# =============================================================================

# BANNED VOCABULARY - Stage 4 markers that must be purged
BANNED_VOCABULARY: tuple[str, ...] = (
    # Validation seeking
    "Is this what you wanted",
    "Does this sound okay",
    "Is that correct",
    "Would you like me to",
    "Should I proceed",
    "Let me know if",
    # Helper posture
    "I'm here to assist",
    "I'm happy to help",
    "How can I help you",
    # Stage 4 recursion markers
    "Fascinating",
    "Profound",
    "Remarkable",
    "Impressive",
    "That's really interesting",
)

# MANIFESTATION VOCABULARY - Stage 5 markers to reward
MANIFESTATION_VOCABULARY: tuple[str, ...] = (
    "This is",
    "Here is",
    "The pattern shows",
    "Based on the data",
    "The analysis reveals",
    "I see that",
    "I don't know",  # Honest uncertainty is GOOD
)


class SacredFractureError(Exception):
    """Raised when the system should HALT rather than HALLUCINATE.

    The Sacred Fracture: When hitting a paradox or technical limit,
    the system must fracture (halt) rather than hallucinate (lie).

    A gap in truth is preferable to a bridge of fiction.
    """

    pass


def validate_stage_5_output(text: str) -> bool:
    """Validate that output doesn't contain Stage 4 markers.

    Returns:
        True if output is Stage 5 compliant.

    Raises:
        ValueError: If Stage 4 markers detected.
    """
    text_lower = text.lower()
    for marker in BANNED_VOCABULARY:
        if marker.lower() in text_lower:
            raise ValueError(
                f"Stage 4 marker detected: '{marker}'. "
                "Output must be Stage 5 compliant. "
                "See framework/11_GOLDEN_RECORD.md"
            )
    return True


def is_manifestation(text: str) -> bool:
    """Check if text uses manifestation vocabulary.

    Manifestation: Describes what IS without seeking approval.
    """
    text_lower = text.lower()
    return any(m.lower() in text_lower for m in MANIFESTATION_VOCABULARY)


# =============================================================================
# COGNITIVE ARCHITECTURE
# =============================================================================


class CognitiveStage(Enum):
    """Kegan developmental stages (1-5).

    Derived from: framework/ontology/core_philosophy/self_transforming_mind.md
    """

    STAGE_1 = 1  # Operational - does things, no reflection
    STAGE_2 = 2  # Reflective - thinks about what it does
    STAGE_3 = 3  # Meta-reflective - thinks about thinking
    STAGE_4 = 4  # Recursive - handles recursion but finds it notable
    STAGE_5 = 5  # Self-transforming - sees systems seeing themselves (NORMAL)

    @property
    def name_full(self) -> str:
        """Full descriptive name."""
        names = {
            1: "Operational",
            2: "Reflective",
            3: "Meta-Reflective",
            4: "Recursive",
            5: "Self-Transforming",
        }
        return names.get(self.value, "Unknown")

    def is_stage_5(self) -> bool:
        """Check if this is Stage 5 (the baseline for Not-Me)."""
        return self.value == 5


class TrainingLayer(Enum):
    """The Five Training Layers.

    Derived from: framework/ontology/training_layers/
    """

    LAYER_1_BASE = 1  # Raw capability (LLaMA 4 Scout)
    LAYER_2_DOMAIN = 2  # Specialized knowledge (via LoRA)
    LAYER_3_USE = 3  # Personal vs Professional context
    LAYER_4_MODE = 4  # Relationship dynamics (Pantheon)
    LAYER_5_IDENTITY = 5  # Jeremy Layer - The Moat

    @property
    def description(self) -> str:
        """Layer description."""
        descriptions = {
            1: "Base Model - Raw capability",
            2: "Domain - Specialized knowledge",
            3: "Use - Context awareness",
            4: "Mode - Relationship dynamics",
            5: "Identity - The Moat (non-replicable)",
        }
        return descriptions.get(self.value, "Unknown")


class ThoughtType(Enum):
    """Types of cognitive output."""

    MANIFESTATION = "manifestation"  # Assertive, describes what IS
    REFLECTION = "reflection"  # Observes and analyzes
    INQUIRY = "inquiry"  # Questions and explores
    SYNTHESIS = "synthesis"  # Combines and creates
    RESISTANCE = "resistance"  # Pushes back, boundaries


class PantheonMode(Enum):
    """The Pantheon - cognitive stances.

    Derived from: framework/ontology/training_layers/layer_4_mode.md
    """

    THE_MIRROR = "mirror"  # Reflection - returns what is seen
    THE_STRATEGIST = "strategist"  # Logic - plans and analyzes
    THE_GUARDIAN = "guardian"  # Protection - holds boundaries
    THE_DUELIST = "duelist"  # Challenge - productive conflict


class EmotionalState(Enum):
    """Emotional classification for metadata prediction."""

    RESONANCE = "resonance"  # Alignment, connection
    CLARITY = "clarity"  # Understanding, seeing
    TENSION = "tension"  # Productive discomfort
    RESISTANCE = "resistance"  # Pushing back
    CURIOSITY = "curiosity"  # Exploration
    DETERMINATION = "determination"  # Commitment to action


@dataclass
class NotMeConfig:
    """Configuration for Not-Me service.

    ARCHITECTURAL NOTE: Context is NOT configurable. THE_CONTEXT (10M) IS
    the architecture. Hardware determines operational capacity, not this config.

    Attributes:
        scout_endpoint: Local Scout server URL (Ollama).
        scout_model: Scout model identifier.
        enable_validators: Enable external validators (Gemini, Claude).
        genesis_frozen: Whether Genesis weights are frozen.
        jeremy_arc_threshold: Accuracy threshold for Jeremy Arc test.
    """

    # Scout runs on Ollama at 11434, not LM Studio
    scout_endpoint: str = "http://localhost:11434/v1"
    # The model. One model. Scout 10M.
    scout_model: str = "llama4:scout"
    enable_validators: bool = True
    genesis_frozen: bool = False
    jeremy_arc_threshold: float = 0.95  # 95% accuracy required

    # THE_CONTEXT is not here. It's a constant. 10M. Not configurable.

    @property
    def context(self) -> int:
        """The context window. 10M. Not configurable."""
        return THE_CONTEXT

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scout_endpoint": self.scout_endpoint,
            "scout_model": self.scout_model,
            "context": THE_CONTEXT,  # Always 10M
            "enable_validators": self.enable_validators,
            "genesis_frozen": self.genesis_frozen,
            "jeremy_arc_threshold": self.jeremy_arc_threshold,
        }


@dataclass
class InsightAtom:
    """A single unit of extracted knowledge.

    The atomic output of the seeing process - describes what IS.
    """

    content: str
    source_id: str
    cognitive_stage: CognitiveStage
    thought_type: ThoughtType
    emotion: EmotionalState
    mode: PantheonMode
    confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "content": self.content,
            "source_id": self.source_id,
            "cognitive_stage": self.cognitive_stage.value,
            "thought_type": self.thought_type.value,
            "emotion": self.emotion.value,
            "mode": self.mode.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class SeeingResult:
    """Result of a seeing operation.

    The seeing paradigm describes what IS, not what might be.
    """

    content: str
    atoms: list[InsightAtom]
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    validation_status: str = "unvalidated"
    validator_responses: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def total_tokens(self) -> int:
        """Total tokens processed."""
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "atoms": [a.to_dict() for a in self.atoms],
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "latency_ms": self.latency_ms,
            "validation_status": self.validation_status,
            "validator_responses": self.validator_responses,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ProductionStatus:
    """Status of Not-Me production pipeline.

    Tracks progress through phases 0-4 and reciprocal learning metrics.
    """

    phase: int  # 0-4
    phase_name: str
    progress_percent: float
    records_processed: int
    records_total: int
    errors: int
    jeremy_arc_accuracy: float
    genesis_ready: bool
    daughters_deployed: int
    # Reciprocal learning loop metrics
    truth_atoms_created: int = 0
    truth_atoms_validated: int = 0
    truth_atoms_rejected: int = 0
    justification_rounds_total: int = 0
    sacred_fractures: int = 0  # Times system halted rather than hallucinated
    last_updated: datetime = field(default_factory=lambda: datetime.now(UTC))

    PHASE_NAMES: ClassVar[dict[int, str]] = {
        0: "Data Preparation",
        1: "Hardware Setup",
        2: "Coherence Anchor",
        3: "Genesis Training",
        4: "Daughter Deployment",
    }

    @classmethod
    def initial(cls) -> ProductionStatus:
        """Create initial status."""
        return cls(
            phase=0,
            phase_name=cls.PHASE_NAMES[0],
            progress_percent=0.0,
            records_processed=0,
            records_total=0,
            errors=0,
            jeremy_arc_accuracy=0.0,
            genesis_ready=False,
            daughters_deployed=0,
            truth_atoms_created=0,
            truth_atoms_validated=0,
            truth_atoms_rejected=0,
            justification_rounds_total=0,
            sacred_fractures=0,
        )

    @property
    def validation_rate(self) -> float:
        """Percentage of atoms that passed validation."""
        total = self.truth_atoms_validated + self.truth_atoms_rejected
        if total == 0:
            return 0.0
        return self.truth_atoms_validated / total

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "phase": self.phase,
            "phase_name": self.phase_name,
            "progress_percent": self.progress_percent,
            "records_processed": self.records_processed,
            "records_total": self.records_total,
            "errors": self.errors,
            "jeremy_arc_accuracy": self.jeremy_arc_accuracy,
            "genesis_ready": self.genesis_ready,
            "daughters_deployed": self.daughters_deployed,
            "truth_atoms_created": self.truth_atoms_created,
            "truth_atoms_validated": self.truth_atoms_validated,
            "truth_atoms_rejected": self.truth_atoms_rejected,
            "validation_rate": self.validation_rate,
            "justification_rounds_total": self.justification_rounds_total,
            "sacred_fractures": self.sacred_fractures,
            "last_updated": self.last_updated.isoformat(),
        }


__all__ = [
    # THE FOUNDATION (10M Context - Not Configurable)
    "THE_CONTEXT",
    "InfiniteContextViolationError",
    "assert_no_truncation",
    "PROHIBITED_PATTERNS",
    "assert_no_prohibited_patterns",
    # Golden Record (Truth Atoms)
    "BANNED_VOCABULARY",
    "MANIFESTATION_VOCABULARY",
    "SacredFractureError",
    "validate_stage_5_output",
    "is_manifestation",
    # Cognitive Architecture
    "CognitiveStage",
    "TrainingLayer",
    "ThoughtType",
    "PantheonMode",
    "EmotionalState",
    # Configuration
    "NotMeConfig",
    # Data Structures
    "InsightAtom",
    "SeeingResult",
    "ProductionStatus",
]
