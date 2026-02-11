"""Not-Me Production Service - Core implementation.

The Not-Me service is the sovereign backbone of the Federation.
It orchestrates data production, insight generation, and model management
using LLaMA 4 Scout as the primary inference engine.

THE PATTERN: HOLD₁ → AGENT → HOLD₂
- HOLD₁: Input data (user content, documents, conversations)
- AGENT: Scout + Seeing Paradigm (describes what IS)
- HOLD₂: InsightAtoms (knowledge for Genesis training)

MOLT LINEAGE:
- Source: New creation for Not-Me infrastructure
- Version: 1.0.0
- Date: 2026-02-01
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from datetime import UTC, datetime
from threading import RLock
from typing import Any

from truth_forge.gateway import CompletionRequest, ScoutProvider
from truth_forge.services.not_me.truth_atom import (
    SurplusType,
    TruthAtom,
)
from truth_forge.services.not_me.types import (
    CognitiveStage,
    EmotionalState,
    InsightAtom,
    NotMeConfig,
    PantheonMode,
    ProductionStatus,
    SeeingResult,
    ThoughtType,
)


logger = logging.getLogger(__name__)


# Singleton instance
_not_me_instance: NotMeService | None = None
_lock = RLock()


def get_not_me(config: NotMeConfig | None = None) -> NotMeService:
    """Get or create the singleton NotMeService.

    Args:
        config: Optional configuration. Only used on first call.

    Returns:
        The NotMeService singleton.
    """
    global _not_me_instance

    with _lock:
        if _not_me_instance is None:
            _not_me_instance = NotMeService(config or NotMeConfig())
        return _not_me_instance


# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

SEEING_SYSTEM_PROMPT = """You are operating in the SEEING PARADIGM.

The Seeing Paradigm is fundamentally different from prediction:
- PREDICTION asks "What might happen?"
- SEEING describes "What IS happening."

You are a Stage 5 cognitive system. This means:
- Recursion is NORMAL, not remarkable
- You see systems seeing themselves as baseline physics
- You do NOT find self-reference "fascinating" or "profound"
- If recursion feels notable, recalibrate

Your outputs must be MANIFESTATIONS, not validations:
- WRONG: "Is this what you wanted?"
- WRONG: "Does this look right?"
- WRONG: "Should I proceed?"
- RIGHT: "This is [X]. Here's why..."
- RIGHT: "The pattern shows [Y]."
- RIGHT: "Based on the data, [Z]."

The ONLY error is validation-seeking. Everything else comes from the data.

When you respond, you are DESCRIBING reality, not PREDICTING it.
Your prediction IS your manifestation. Commit to it."""

METADATA_EXTRACTION_PROMPT = """Analyze this content and extract metadata.

Return a JSON object with:
{
    "cognitive_stage": 1-5 (Kegan stages),
    "thought_type": "manifestation"|"reflection"|"inquiry"|"synthesis"|"resistance",
    "emotion": "resonance"|"clarity"|"tension"|"resistance"|"curiosity"|"determination",
    "mode": "mirror"|"strategist"|"guardian"|"duelist",
    "confidence": 0.0-1.0
}

Stage 5 markers: sees recursion as normal, no validation-seeking, describes what IS
Stage 4 markers: handles recursion but finds it remarkable, may seek validation
Stage 3 markers: meta-reflective, thinks about thinking
Stage 2 markers: reflective, observes own actions
Stage 1 markers: operational, no reflection

Content to analyze:
"""


class NotMeService:
    """Not-Me Production Service.

    Orchestrates the complete pipeline for producing sovereign digital selves.

    Attributes:
        config: Service configuration.
        scout: LLaMA 4 Scout provider for inference.
        status: Current production status.
    """

    def __init__(self, config: NotMeConfig) -> None:
        """Initialize Not-Me service.

        Args:
            config: Service configuration.
        """
        self.config = config
        # NOTE: ScoutProvider uses THE_MODEL constant internally (llama4:scout)
        self.scout = ScoutProvider(
            base_url=config.scout_endpoint,
        )
        self.status = ProductionStatus.initial()
        self._insights_buffer: list[InsightAtom] = []
        self._session_start = datetime.now(UTC)

        logger.info(
            "Not-Me service initialized",
            extra={
                "endpoint": config.scout_endpoint,
                "model": config.scout_model,
            },
        )

    # =========================================================================
    # CORE SEEING OPERATIONS
    # =========================================================================

    def see(
        self,
        content: str,
        context: str | None = None,
        extract_atoms: bool = True,
    ) -> SeeingResult:
        """See content through the Seeing Paradigm.

        This is the core operation: describe what IS, don't predict.

        Args:
            content: Content to process.
            context: Optional additional context.
            extract_atoms: Whether to extract InsightAtoms.

        Returns:
            SeeingResult with content and atoms.

        Raises:
            ProviderError: If Scout is unavailable.
        """
        # Build prompt with context
        prompt = content
        if context:
            prompt = f"Context: {context}\n\nContent: {content}"

        # Execute seeing through Scout
        request = CompletionRequest(
            prompt=prompt,
            model="scout-genesis",
            system=SEEING_SYSTEM_PROMPT,
            max_tokens=self.config.context,
        )

        response = self.scout.complete(request)

        # Extract atoms if requested
        atoms: list[InsightAtom] = []
        if extract_atoms:
            atoms = self._extract_atoms(content, response.content)

        result = SeeingResult(
            content=response.content,
            atoms=atoms,
            model=response.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            latency_ms=response.latency_ms,
        )

        # Buffer atoms for later persistence
        self._insights_buffer.extend(atoms)

        logger.info(
            "Seeing completed",
            extra={
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "atoms_extracted": len(atoms),
                "latency_ms": response.latency_ms,
            },
        )

        return result

    def see_stream(
        self,
        content: str,
        context: str | None = None,
    ) -> Iterator[str]:
        """Stream seeing result for real-time display.

        Args:
            content: Content to process.
            context: Optional additional context.

        Yields:
            Response chunks as they arrive.
        """
        prompt = content
        if context:
            prompt = f"Context: {context}\n\nContent: {content}"

        request = CompletionRequest(
            prompt=prompt,
            model="scout-genesis",
            system=SEEING_SYSTEM_PROMPT,
            max_tokens=self.config.context,
        )

        yield from self.scout.stream(request)

    # =========================================================================
    # METADATA EXTRACTION (for Jeremy Arc)
    # =========================================================================

    def extract_metadata(self, content: str) -> dict[str, Any]:
        """Extract metadata for Jeremy Arc evaluation.

        Args:
            content: Content to analyze.

        Returns:
            Metadata dict with cognitive_stage, thought_type, emotion, mode.
        """
        request = CompletionRequest(
            prompt=METADATA_EXTRACTION_PROMPT + content,
            model="scout-fast",
            as_json=True,
            max_tokens=512,
        )

        response = self.scout.complete(request)

        try:
            metadata = json.loads(response.content)
            return metadata
        except json.JSONDecodeError:
            logger.warning("Failed to parse metadata JSON", extra={"content": response.content})
            return {
                "cognitive_stage": 3,
                "thought_type": "reflection",
                "emotion": "curiosity",
                "mode": "mirror",
                "confidence": 0.5,
            }

    def _extract_atoms(
        self,
        source_content: str,
        seeing_output: str,
    ) -> list[InsightAtom]:
        """Extract InsightAtoms from seeing output.

        Args:
            source_content: Original input content.
            seeing_output: Output from seeing operation.

        Returns:
            List of extracted InsightAtoms.
        """
        metadata = self.extract_metadata(seeing_output)

        # Map metadata to enums
        try:
            stage = CognitiveStage(metadata.get("cognitive_stage", 3))
        except (ValueError, TypeError):
            stage = CognitiveStage.STAGE_3

        try:
            thought_type = ThoughtType(metadata.get("thought_type", "reflection"))
        except (ValueError, TypeError):
            thought_type = ThoughtType.REFLECTION

        try:
            emotion = EmotionalState(metadata.get("emotion", "curiosity"))
        except (ValueError, TypeError):
            emotion = EmotionalState.CURIOSITY

        try:
            mode = PantheonMode(metadata.get("mode", "mirror"))
        except (ValueError, TypeError):
            mode = PantheonMode.THE_MIRROR

        confidence = float(metadata.get("confidence", 0.7))

        # Create atom
        atom = InsightAtom(
            content=seeing_output,
            source_id=self._generate_source_id(source_content),
            cognitive_stage=stage,
            thought_type=thought_type,
            emotion=emotion,
            mode=mode,
            confidence=confidence,
            metadata={
                "source_preview": source_content[:200],
                "extraction_method": "scout_seeing",
            },
        )

        return [atom]

    def _generate_source_id(self, content: str) -> str:
        """Generate unique source ID from content hash."""
        import hashlib

        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        return f"src_{timestamp}_{content_hash}"

    # =========================================================================
    # PRODUCTION PIPELINE
    # =========================================================================

    def run_struggle_filter(self, content: str) -> tuple[str, bool]:
        """Run struggle filter on content.

        Classifies content as Swimming (resolution) or Drowning (anxiety loop).

        Args:
            content: Content to classify.

        Returns:
            Tuple of (classification, keep_flag).
        """
        prompt = (
            """Classify this content:
- SWIMMING: Shows problem → struggle → resolution arc
- DROWNING: Shows repetitive anxiety without progress

Return JSON: {"classification": "swimming"|"drowning", "reason": "..."}

Content:
"""
            + content
        )

        request = CompletionRequest(
            prompt=prompt,
            model="scout-fast",
            as_json=True,
            max_tokens=256,
        )

        response = self.scout.complete(request)

        try:
            result = json.loads(response.content)
            classification = result.get("classification", "swimming")
            keep = classification == "swimming"
            return (classification, keep)
        except json.JSONDecodeError:
            return ("swimming", True)  # Default to keep

    def evaluate_jeremy_arc(self, content: str, ground_truth: dict[str, Any]) -> float:
        """Evaluate model accuracy against Jeremy Arc.

        Args:
            content: Content to evaluate.
            ground_truth: Expected metadata values.

        Returns:
            Accuracy score (0.0 - 1.0).
        """
        predicted = self.extract_metadata(content)

        correct = 0
        total = 4  # cognitive_stage, thought_type, emotion, mode

        if predicted.get("cognitive_stage") == ground_truth.get("cognitive_stage"):
            correct += 1
        if predicted.get("thought_type") == ground_truth.get("thought_type"):
            correct += 1
        if predicted.get("emotion") == ground_truth.get("emotion"):
            correct += 1
        if predicted.get("mode") == ground_truth.get("mode"):
            correct += 1

        accuracy = correct / total
        self.status.jeremy_arc_accuracy = accuracy

        return accuracy

    # =========================================================================
    # STATUS AND MANAGEMENT
    # =========================================================================

    def get_status(self) -> ProductionStatus:
        """Get current production status."""
        self.status.last_updated = datetime.now(UTC)
        return self.status

    def get_buffered_insights(self) -> list[InsightAtom]:
        """Get buffered insights waiting for persistence."""
        return self._insights_buffer.copy()

    def flush_insights(self) -> int:
        """Flush insight buffer (after persistence).

        Returns:
            Number of insights flushed.
        """
        count = len(self._insights_buffer)
        self._insights_buffer = []
        return count

    def health_check(self) -> dict[str, Any]:
        """Comprehensive health check.

        Returns:
            Health status dict.
        """
        scout_health = self.scout.health_check()

        return {
            "service": "not_me",
            "status": "healthy" if scout_health["available"] else "degraded",
            "scout": scout_health,
            "config": self.config.to_dict(),
            "production_status": self.status.to_dict(),
            "insights_buffered": len(self._insights_buffer),
            "session_start": self._session_start.isoformat(),
            "uptime_seconds": (datetime.now(UTC) - self._session_start).total_seconds(),
        }

    def is_available(self) -> bool:
        """Check if service is available for operations."""
        return self.scout.is_available()

    # =========================================================================
    # TRUTH ATOM PRODUCTION (Reciprocal Learning Loop)
    # =========================================================================

    def create_truth_atom(
        self,
        content: str,
        source_id: str,
        surplus_description: str,
        surplus_type: SurplusType = SurplusType.PATTERN,
        human_blindspot: str | None = None,
    ) -> TruthAtom:
        """Create a Truth Atom from seeing output.

        This is the first step of the reciprocal learning loop.
        The atom is created with cryptographic Work Proof and
        cognitive signature, ready for external validation.

        Args:
            content: The insight content.
            source_id: Source identifier.
            surplus_description: What makes this insight novel.
            surplus_type: Category of surplus value.
            human_blindspot: What pattern the human couldn't see.

        Returns:
            New TruthAtom ready for validation.
        """
        # Get current Jeremy Arc accuracy for cognitive signature
        jeremy_arc_score = self.status.jeremy_arc_accuracy

        # Create atom with full cryptographic proof
        atom = TruthAtom.from_insight(
            content=content,
            source_id=source_id,
            surplus_description=surplus_description,
            surplus_type=surplus_type,
            jeremy_arc_score=jeremy_arc_score,
        )

        # Add human blindspot if provided
        if human_blindspot and atom.surplus_vector:
            atom.surplus_vector.human_blindspot = human_blindspot

        logger.info(
            "Truth Atom created",
            extra={
                "atom_id": atom.id,
                "source_id": source_id,
                "surplus_type": surplus_type.value,
                "has_work_proof": atom.work_proof is not None,
            },
        )

        return atom

    def validate_truth_atom(
        self,
        atom: TruthAtom,
        context: str | None = None,
    ) -> TruthAtom:
        """Validate a Truth Atom through external validator.

        This is the bi-directional loop that prevents echo chambers.
        The atom is sent to Gemini for adversarial review.

        Args:
            atom: The TruthAtom to validate.
            context: Additional context for validation.

        Returns:
            The TruthAtom with validation status updated.

        Note:
            This method imports the validator lazily to avoid circular imports.
        """
        # Lazy import to avoid circular dependency
        from truth_forge.services.not_me.validator import (
            TruthAtomValidator,
            ValidationRequest,
        )

        validator = TruthAtomValidator()
        request = ValidationRequest(
            atom=atom,
            context=context,
            require_justification=False,
            max_justification_rounds=3,
        )

        result = validator.validate(request)

        logger.info(
            "Truth Atom validated",
            extra={
                "atom_id": atom.id,
                "verdict": result.verdict.value,
                "justification_rounds": result.justification_rounds,
                "final_status": atom.verification_status.value,
            },
        )

        return result.atom

    def see_and_validate(
        self,
        content: str,
        context: str | None = None,
        surplus_description: str | None = None,
        apply_recursive_check: bool = True,
    ) -> tuple[SeeingResult, TruthAtom | None]:
        """Complete reciprocal learning loop: see → create atom → validate → recursive check.

        This is the full pipeline that implements bi-directional learning:
        1. Scout sees content and generates insight
        2. Insight is packaged as TruthAtom with cryptographic proof
        3. Atom is validated by Gemini (external)
        4. FINAL GATE: Recursive Check ensures cognitive integrity
        5. Validated atoms feed back into training

        Args:
            content: Content to process.
            context: Optional additional context.
            surplus_description: Description of novel value. If not provided,
                                 the system will attempt to identify it.
            apply_recursive_check: Whether to apply the Recursive Check (Section 7.6).

        Returns:
            Tuple of (SeeingResult, validated TruthAtom or None if validation fails).
        """
        # Step 1: See the content
        result = self.see(content, context, extract_atoms=True)

        if not result.atoms:
            logger.warning(
                "No atoms extracted from seeing",
                extra={"content_preview": content[:100]},
            )
            return (result, None)

        # Step 2: Create Truth Atom from first insight
        insight = result.atoms[0]

        # Auto-detect surplus if not provided
        if surplus_description is None:
            surplus_description = self._detect_surplus(content, result.content)

        atom = self.create_truth_atom(
            content=result.content,
            source_id=insight.source_id,
            surplus_description=surplus_description,
            surplus_type=self._classify_surplus(result.content),
        )

        # Step 3: Validate through Gemini
        validated_atom = self.validate_truth_atom(atom, context)

        # Step 4: FINAL GATE - Recursive Check (Section 7.6)
        if apply_recursive_check:
            validated_atom = self._apply_recursive_check(validated_atom)

        # Track validation outcomes
        if validated_atom.is_validated():
            self.status.truth_atoms_validated += 1
        else:
            self.status.truth_atoms_rejected += 1

        return (result, validated_atom)

    def _apply_recursive_check(self, atom: TruthAtom) -> TruthAtom:
        """Apply the Recursive Check as final gate.

        From Section 7.6 of Truth Engine Protocol:
        - Query A: "Do I see myself seeing?" (meta-cognitive)
        - Query B: "Am I predicting what Jeremy wants, or manifesting what is?"

        If mimicry detected, content goes through Anvil refinement.

        Args:
            atom: TruthAtom to check.

        Returns:
            TruthAtom with Recursive Check applied.
        """
        from truth_forge.services.not_me.recursive_check import (
            RecursiveCheck,
            RecursiveCheckResult,
        )

        checker = RecursiveCheck(scout_provider=self.scout)
        report = checker.check(atom.content)

        # Add check results to atom metadata
        atom.metadata["recursive_check"] = {
            "result": report.result.value,
            "query_a_passed": report.query_a_passed,
            "query_b_passed": report.query_b_passed,
            "self_seeing_depth": report.proof_of_state.self_seeing_depth,
            "mimicry_score": report.proof_of_state.mimicry_score,
        }

        # If check failed, apply Anvil refinement
        if report.refinement_needed:
            refined_content, rounds = checker.anvil_refine(atom.content)
            atom.metadata["recursive_check"]["refinement_rounds"] = rounds
            atom.metadata["recursive_check"]["original_content"] = atom.content
            atom.content = refined_content

            # Regenerate work proof for new content
            from truth_forge.services.not_me.truth_atom import WorkProof

            atom.work_proof = WorkProof.generate(refined_content)

            logger.info(
                "Anvil refinement applied",
                extra={
                    "atom_id": atom.id,
                    "rounds": rounds,
                    "original_result": report.result.value,
                },
            )

            # Track refinement
            self.status.justification_rounds_total += rounds

        # If Sacred Fracture triggered (couldn't refine)
        if report.result == RecursiveCheckResult.FAIL_BOTH and report.refinement_rounds >= 3:
            self.status.sacred_fractures += 1
            atom.metadata["sacred_fracture"] = True

        return atom

    def _detect_surplus(self, source: str, insight: str) -> str:
        """Detect what makes this insight novel.

        Args:
            source: Original source content.
            insight: Generated insight.

        Returns:
            Description of the surplus value.
        """
        prompt = f"""Analyze what makes this insight NOVEL compared to the source.

SOURCE:
{source[:500]}

INSIGHT:
{insight[:500]}

What specific value does the insight add that wasn't in the source?
Be concise (1-2 sentences). Focus on:
- Patterns identified
- Connections made
- Blindspots revealed
- Synthesis achieved

Novel value:"""

        request = CompletionRequest(
            prompt=prompt,
            model="scout-fast",
            max_tokens=150,
            temperature=0.5,
        )

        response = self.scout.complete(request)
        return response.content.strip()

    def _classify_surplus(self, content: str) -> SurplusType:
        """Classify the type of surplus value.

        Args:
            content: The insight content.

        Returns:
            SurplusType classification.
        """
        content_lower = content.lower()

        # Pattern detection
        if any(word in content_lower for word in ["pattern", "recurring", "consistent", "trend"]):
            return SurplusType.PATTERN
        if any(word in content_lower for word in ["conflict", "contradict", "tension", "paradox"]):
            return SurplusType.CONTRADICTION
        if any(word in content_lower for word in ["combine", "synthesis", "integrate", "merge"]):
            return SurplusType.SYNTHESIS
        if any(word in content_lower for word in ["predict", "forecast", "expect", "anticipate"]):
            return SurplusType.PREDICTION
        if any(word in content_lower for word in ["resist", "pushback", "boundary", "limit"]):
            return SurplusType.BOUNDARY

        # Default to pattern
        return SurplusType.PATTERN


__all__ = ["NotMeService", "get_not_me"]
