"""Knowledge Atom Factory - Multi-perspective knowledge generation.

ALL models participate, each with their role:
- Scout (Seeing - what IS, 10M context, observation)
- Maverick (Deep reasoning - dialectical challenge, 128 experts)
- R1 (The Architect - protocol design, system synthesis, meta-cognition)
- Future models (extensible)

ALL models share the SAME MemoryCortex (5 graphs):
- Semantic, Temporal, Causal, Entity, Emotional

They communicate via tensor space (shared memory), not language.
R1 DESIGNED this protocol - the cognition bus that makes it possible.
Knowledge atoms capture multi-dimensional, multi-perspective truth.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog

from truth_forge.gateway.types import CompletionRequest
from truth_forge.services.exo_inference import ExoInferenceTool
from truth_forge.services.knowledge_atom_models import (
    get_knowledge_atom_models,
    validate_cluster_capacity,
)


if TYPE_CHECKING:
    from sovereign.memory.cortex import EnrichedInput, MemoryCortex
    from truth_forge.gateway.providers.maverick import MaverickProvider
    from truth_forge.gateway.providers.r1 import R1Provider
    from truth_forge.gateway.providers.scout import ScoutProvider


logger = structlog.get_logger(__name__)


@dataclass
class ModelPerspective:
    """A single model's perspective on enriched input.

    Captures what THIS model saw/thought/concluded.
    """

    model_name: str  # "scout", "maverick", "r1"
    model_id: str  # Actual model ID (e.g., "Llama-4-Scout-17B-16E")
    response_content: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    timestamp: str


@dataclass
class KnowledgeAtom:
    """Multi-dimensional, multi-perspective knowledge unit.

    This is NOT-ME's native training data format.
    Captures truth at the cognitive level, not just language level.
    """

    atom_id: str  # Unique identifier
    created_at: str  # ISO timestamp

    # What was said (raw)
    raw_input: str

    # What memory provided (pre-linguistic enrichment)
    # These are the TENSORS - the shared cognitive space
    semantic_context: list[dict[str, Any]]
    temporal_context: list[dict[str, Any]]
    causal_context: list[dict[str, Any]]
    entity_context: list[dict[str, Any]]
    emotional_context: dict[str, Any]
    enrichment_metadata: dict[str, Any]

    # Model perspectives (each model's view of the enriched input)
    perspectives: list[ModelPerspective] = field(default_factory=list)

    # Convergence analysis (where models agree)
    convergence_score: float | None = None  # 0.0-1.0
    convergence_summary: str | None = None

    # Divergence analysis (where models disagree - valuable for training!)
    divergence_points: list[str] = field(default_factory=list)
    divergence_summary: str | None = None

    # What got committed back to memory (the new knowledge)
    memory_commit: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "atom_id": self.atom_id,
            "created_at": self.created_at,
            "raw_input": self.raw_input,
            "semantic_context": self.semantic_context,
            "temporal_context": self.temporal_context,
            "causal_context": self.causal_context,
            "entity_context": self.entity_context,
            "emotional_context": self.emotional_context,
            "enrichment_metadata": self.enrichment_metadata,
            "perspectives": [asdict(p) for p in self.perspectives],
            "convergence_score": self.convergence_score,
            "convergence_summary": self.convergence_summary,
            "divergence_points": self.divergence_points,
            "divergence_summary": self.divergence_summary,
            "memory_commit": self.memory_commit,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class KnowledgeAtomFactory:
    """Factory for generating multi-perspective knowledge atoms.

    Architecture:
        ALL models flow through the SAME MemoryCortex.
        ALL models read from the SAME 5 memory graphs.
        ALL models write to the SAME memory pool.

    This is tensor-level communication - shared cognitive space.
    Models don't talk in English, they talk in memory.
    """

    def __init__(
        self,
        memory_cortex: MemoryCortex,
        scout_provider: ScoutProvider | None = None,
        maverick_provider: MaverickProvider | None = None,
        r1_provider: R1Provider | None = None,
        output_dir: Path | None = None,
        use_exo: bool = True,
    ) -> None:
        """Initialize the Knowledge Atom Factory.

        Args:
            memory_cortex: The shared memory cortex (5 graphs)
            scout_provider: Scout model provider (optional)
            maverick_provider: Maverick model provider (optional)
            r1_provider: R1 model provider (optional)
            output_dir: Where to save atoms (optional)
            use_exo: Use EXO distributed inference for large models (default: True)
        """
        self._cortex = memory_cortex
        self._scout = scout_provider
        self._maverick = maverick_provider
        self._r1 = r1_provider
        self._output_dir = output_dir or Path("data/knowledge_atoms")
        self._output_dir.mkdir(parents=True, exist_ok=True)

        # EXO distributed inference for Maverick and R1
        self._exo = ExoInferenceTool() if use_exo else None

        # Load true model specifications
        self._scout_model, self._maverick_model, self._r1_model = get_knowledge_atom_models()

        # Validate cluster capacity
        validate_cluster_capacity()
        logger.info(
            "knowledge_atom_factory_initialized",
            extra={
                "scout": self._scout_model.name,
                "maverick": self._maverick_model.name,
                "r1": self._r1_model.name,
                "total_memory_gb": 1280,  # 1.28TB
                "allocated_memory_gb": 455,
                "free_headroom_gb": 855,
                "exo_enabled": use_exo,
            },
        )

    async def generate_atom(
        self,
        user_input: str,
        models: list[str] | None = None,
        commit_to_memory: bool = True,
    ) -> KnowledgeAtom:
        """Generate a multi-perspective knowledge atom.

        Process:
        1. PERCEIVE through memory cortex (enrichment)
        2. GENERATE responses from each model in parallel
        3. ANALYZE convergence/divergence
        4. COMMIT to memory (optional)
        5. PERSIST atom

        Args:
            user_input: Raw user input
            models: Which models to use (default: all available)
            commit_to_memory: Whether to commit to shared memory

        Returns:
            KnowledgeAtom with all perspectives
        """
        atom_id = self._generate_atom_id()
        timestamp = datetime.now(UTC).isoformat()

        logger.info(
            "atom_generation_start",
            extra={"atom_id": atom_id, "input_length": len(user_input)},
        )

        # STEP 1: PERCEIVE through memory (enrichment)
        enriched = await self._cortex.perceive(user_input)

        logger.info(
            "perception_complete",
            extra={
                "atom_id": atom_id,
                "semantic_hits": enriched.enrichment_metadata.get("semantic_hits", 0),
                "temporal_hits": enriched.enrichment_metadata.get("temporal_hits", 0),
                "entity_hits": enriched.enrichment_metadata.get("entity_hits", 0),
            },
        )

        # STEP 2: GENERATE perspectives from all models (parallel)
        perspectives = await self._generate_perspectives(enriched, models)

        logger.info(
            "perspectives_generated",
            extra={
                "atom_id": atom_id,
                "perspective_count": len(perspectives),
                "models": [p.model_name for p in perspectives],
            },
        )

        # STEP 3: ANALYZE convergence/divergence
        convergence_score, convergence_summary = self._analyze_convergence(perspectives)
        divergence_points, divergence_summary = self._analyze_divergence(perspectives)

        # STEP 4: COMMIT to memory (if requested)
        memory_commit = {}
        if commit_to_memory and perspectives:
            # Use first perspective as "canonical" response
            canonical_response = perspectives[0].response_content
            await self._cortex.commit(user_input, canonical_response)
            memory_commit = {
                "committed_at": datetime.now(UTC).isoformat(),
                "response_used": perspectives[0].model_name,
            }
            logger.info(
                "memory_committed",
                extra={"atom_id": atom_id, "model": perspectives[0].model_name},
            )

        # STEP 5: CREATE atom
        atom = KnowledgeAtom(
            atom_id=atom_id,
            created_at=timestamp,
            raw_input=user_input,
            semantic_context=enriched.semantic_context,
            temporal_context=enriched.temporal_context,
            causal_context=enriched.causal_context,
            entity_context=enriched.entity_context,
            emotional_context=enriched.emotional_context,
            enrichment_metadata=enriched.enrichment_metadata,
            perspectives=perspectives,
            convergence_score=convergence_score,
            convergence_summary=convergence_summary,
            divergence_points=divergence_points,
            divergence_summary=divergence_summary,
            memory_commit=memory_commit,
        )

        # STEP 6: PERSIST atom
        self._persist_atom(atom)

        logger.info(
            "atom_generation_complete",
            extra={
                "atom_id": atom_id,
                "perspectives": len(perspectives),
                "convergence": convergence_score,
            },
        )

        return atom

    async def _generate_perspectives(
        self,
        enriched: EnrichedInput,
        models: list[str] | None = None,
    ) -> list[ModelPerspective]:
        """Generate perspectives from all requested models in parallel.

        All models receive the SAME enriched input (shared memory).
        """
        tasks = []

        # Determine which models to use
        use_scout = (models is None or "scout" in models) and self._scout is not None
        use_maverick = (models is None or "maverick" in models) and self._maverick is not None
        use_r1 = (models is None or "r1" in models) and self._r1 is not None

        # Build context from enriched input
        context_block = self._cortex.build_context_block(enriched)

        # Scout perspective
        if use_scout and self._scout.is_available():
            tasks.append(self._get_scout_perspective(context_block))

        # Maverick perspective
        if use_maverick and self._maverick.is_available():
            tasks.append(self._get_maverick_perspective(context_block))

        # R1 perspective
        if use_r1 and self._r1.is_available():
            tasks.append(self._get_r1_perspective(context_block))

        # Execute in parallel
        if not tasks:
            logger.warning("no_models_available")
            return []

        perspectives = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_perspectives = [p for p in perspectives if isinstance(p, ModelPerspective)]

        return valid_perspectives

    async def _get_scout_perspective(self, prompt: str) -> ModelPerspective:
        """Get Scout's perspective (Seeing - what IS).

        Scout runs on King (single-node) with 10M context window.
        Model: LLaMA 4 Scout 109GB (8-bit), 169GB allocated.
        """
        import time

        start = time.time()
        # Use Scout's true model specification
        request = CompletionRequest(
            prompt=prompt,
            model=self._scout_model.model_id,
            max_tokens=min(131072, self._scout_model.context_window),  # Operational limit
        )
        response = self._scout.complete(request)
        latency = (time.time() - start) * 1000

        return ModelPerspective(
            model_name=self._scout_model.name,
            model_id=self._scout_model.model_id,
            response_content=response.content,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            latency_ms=latency,
            timestamp=datetime.now(UTC).isoformat(),
        )

    async def _get_maverick_perspective(self, prompt: str) -> ModelPerspective:
        """Get Maverick's perspective (Deep reasoning - dialectical challenge).

        Maverick uses EXO distributed inference (400B, 8-bit, 210GB allocated).
        Distributed across cluster via tensor parallelism.
        """
        import time

        start = time.time()

        # Check if EXO should be used for distributed inference
        prompt_tokens = len(prompt.split()) * 1.3  # Rough estimate
        if self._exo and self._exo.can_distribute("maverick", int(prompt_tokens)):
            # Use EXO distributed inference
            messages = [{"role": "user", "content": prompt}]
            result = self._exo.distributed_inference(
                model=self._maverick_model.model_id,
                messages=messages,
                temperature=0.7,
            )
            latency = result["latency_ms"]
            content = result["content"]
            input_tokens = 0  # EXO doesn't return token counts yet
            output_tokens = 0
        else:
            # Fallback to single-node (if available)
            request = CompletionRequest(
                prompt=prompt,
                model=self._maverick_model.model_id,
            )
            response = self._maverick.complete(request)
            latency = (time.time() - start) * 1000
            content = response.content
            input_tokens = response.input_tokens
            output_tokens = response.output_tokens

        return ModelPerspective(
            model_name=self._maverick_model.name,
            model_id=self._maverick_model.model_id,
            response_content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency,
            timestamp=datetime.now(UTC).isoformat(),
        )

    async def _get_r1_perspective(self, prompt: str) -> ModelPerspective:
        """Get R1's perspective (The Architect - protocol design, system synthesis).

        R1 designed the cognition bus that makes Scout/Maverick communication possible.
        DeepSeek R1 671B requires FULL FLEET via EXO (~1.3TB at 8-bit).
        Currently using 4-bit (36GB) until cluster expanded.
        """
        import time

        start = time.time()

        # R1 671B ALWAYS uses EXO distributed inference (too large for single node)
        prompt_tokens = len(prompt.split()) * 1.3  # Rough estimate
        if self._exo and self._exo.can_distribute("r1", int(prompt_tokens)):
            # Use EXO full fleet distribution
            messages = [{"role": "user", "content": prompt}]
            result = self._exo.distributed_inference(
                model=self._r1_model.model_id,
                messages=messages,
                temperature=0.7,
            )
            latency = result["latency_ms"]
            content = result["content"]
            input_tokens = 0
            output_tokens = 0
        else:
            # Fallback to 4-bit single-node version
            logger.warning(
                "r1_using_4bit_fallback",
                extra={"reason": "EXO unavailable, using quantized version"},
            )
            request = CompletionRequest(
                prompt=prompt,
                model="deepseek-r1:4bit",  # Fallback to 4-bit
            )
            response = self._r1.complete(request)
            latency = (time.time() - start) * 1000
            content = response.content
            input_tokens = response.input_tokens
            output_tokens = response.output_tokens

        return ModelPerspective(
            model_name=self._r1_model.name,
            model_id=self._r1_model.model_id,
            response_content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency,
            timestamp=datetime.now(UTC).isoformat(),
        )

    def _analyze_convergence(
        self,
        perspectives: list[ModelPerspective],
    ) -> tuple[float | None, str | None]:
        """Analyze where models agree (high confidence).

        Returns:
            (convergence_score, summary)
        """
        if len(perspectives) < 2:
            return None, None

        # Simple similarity for now (can be enhanced with embeddings)
        # TODO: Implement semantic similarity via embeddings
        # For now, return placeholder
        score = 0.5  # Placeholder
        summary = f"Analyzed {len(perspectives)} perspectives"

        return score, summary

    def _analyze_divergence(
        self,
        perspectives: list[ModelPerspective],
    ) -> tuple[list[str], str | None]:
        """Analyze where models disagree (valuable training signal!).

        Returns:
            (divergence_points, summary)
        """
        if len(perspectives) < 2:
            return [], None

        # TODO: Implement divergence analysis
        # For now, return placeholder
        points = []
        summary = "Divergence analysis pending implementation"

        return points, summary

    def _persist_atom(self, atom: KnowledgeAtom) -> None:
        """Persist atom to disk."""
        filename = f"{atom.atom_id}.json"
        filepath = self._output_dir / filename

        with filepath.open("w", encoding="utf-8") as f:
            f.write(atom.to_json())

        logger.info(
            "atom_persisted",
            extra={"atom_id": atom.atom_id, "path": str(filepath)},
        )

    def _generate_atom_id(self) -> str:
        """Generate unique atom ID."""
        import uuid

        return f"atom-{uuid.uuid4().hex[:12]}"


__all__ = [
    "KnowledgeAtom",
    "ModelPerspective",
    "KnowledgeAtomFactory",
]
