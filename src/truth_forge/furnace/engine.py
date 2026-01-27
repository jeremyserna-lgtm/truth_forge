"""Furnace Engine - The True Narrative Core.

Raw Truth -> Extract Truths -> Retrieve Corpus -> Forge Together -> Enriched Narrative

This is not transformation. This is forging.

MOLT LINEAGE:
- Source: Truth_Engine furnace_engine.py
- Version: 2.0.0
- Date: 2026-01-26
- Changes: Decoupled from BigQuery, made LLM-agnostic
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol


logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================


@dataclass(slots=True)
class Truth:
    """A single extracted truth.

    Truths are the atomic units of meaning extracted from narratives.
    """

    category: str  # pattern, principle, theme, event, realization, etc.
    statement: str  # The truth itself
    evidence: str = ""  # Supporting quote or reference

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary."""
        return {
            "category": self.category,
            "statement": self.statement,
            "evidence": self.evidence,
        }


@dataclass(slots=True)
class CorpusTruth:
    """A truth retrieved from the corpus.

    These are existing truths that relate to the current narrative.
    """

    entity_id: str
    text: str
    source: str
    timestamp: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ForgeResult:
    """Result of the furnace forging process.

    Contains the enriched narrative and all intermediate results.
    """

    enriched_narrative: str
    extracted_truths: list[Truth]
    corpus_truths: list[CorpusTruth]
    synthesis: list[dict[str, str]]
    provenance: dict[str, Any]

    @property
    def success(self) -> bool:
        """Check if forging was successful."""
        return bool(self.enriched_narrative)


@dataclass(slots=True)
class FurnaceConfig:
    """Configuration for the Furnace Engine."""

    max_corpus_results: int = 10
    default_lens: str = "Furnace"
    extraction_temperature: float = 0.3
    synthesis_temperature: float = 0.7
    max_output_tokens: int = 4096


# ============================================================================
# Protocols for Dependency Injection
# ============================================================================


class LLMClient(Protocol):
    """Protocol for LLM clients (Gemini, Claude, etc.)."""

    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: str | None = None,
    ) -> str:
        """Generate text from prompt.

        Args:
            prompt: The prompt to send
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_format: Optional format hint (e.g., "json")

        Returns:
            Generated text
        """
        ...


class CorpusRetriever(Protocol):
    """Protocol for corpus retrieval (BigQuery, DuckDB, etc.)."""

    def retrieve(
        self,
        truths: list[Truth],
        max_results: int = 10,
    ) -> list[CorpusTruth]:
        """Retrieve related truths from corpus.

        Args:
            truths: Truths to find related content for
            max_results: Maximum results to return

        Returns:
            List of related corpus truths
        """
        ...


# ============================================================================
# Base Implementations
# ============================================================================


class NoOpCorpusRetriever:
    """A no-op corpus retriever that returns empty results.

    Use when corpus retrieval is not available or not needed.
    """

    def retrieve(
        self,
        truths: list[Truth],
        max_results: int = 10,
    ) -> list[CorpusTruth]:
        """Return empty results."""
        _ = truths
        _ = max_results
        return []


class InMemoryCorpusRetriever:
    """Simple in-memory corpus retriever for testing/development."""

    def __init__(self, corpus: list[CorpusTruth] | None = None) -> None:
        """Initialize with optional corpus."""
        self.corpus = corpus or []

    def add(self, truth: CorpusTruth) -> None:
        """Add a truth to the corpus."""
        self.corpus.append(truth)

    def retrieve(
        self,
        truths: list[Truth],
        max_results: int = 10,
    ) -> list[CorpusTruth]:
        """Simple keyword matching retrieval."""
        if not self.corpus or not truths:
            return []

        # Extract keywords from truths
        keywords = set()
        for truth in truths:
            keywords.update(truth.statement.lower().split())

        # Score corpus by keyword overlap
        scored = []
        for ct in self.corpus:
            text_words = set(ct.text.lower().split())
            score = len(keywords & text_words)
            if score > 0:
                scored.append((score, ct))

        # Return top results
        scored.sort(key=lambda x: x[0], reverse=True)
        return [ct for _, ct in scored[:max_results]]


# ============================================================================
# Furnace Engine
# ============================================================================


class BaseFurnaceEngine(ABC):
    """Abstract base class for Furnace Engine implementations."""

    def __init__(
        self,
        config: FurnaceConfig | None = None,
        corpus_retriever: CorpusRetriever | None = None,
    ) -> None:
        """Initialize the Furnace Engine.

        Args:
            config: Configuration for the engine
            corpus_retriever: Retriever for corpus truths
        """
        self.config = config or FurnaceConfig()
        self.corpus_retriever = corpus_retriever or NoOpCorpusRetriever()

    @abstractmethod
    def _call_llm(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: str | None = None,
    ) -> str:
        """Call the LLM with the given prompt.

        Subclasses must implement this method.
        """
        ...

    def forge_narrative(
        self,
        raw_text: str,
        entity_metadata: dict[str, Any] | None = None,
        lens: str | None = None,
        max_corpus_results: int | None = None,
    ) -> ForgeResult:
        """The full Furnace process.

        Args:
            raw_text: The raw narrative/truth to process
            entity_metadata: Optional metadata about the entity
            lens: The lens to apply (default: Furnace)
            max_corpus_results: Max results to retrieve from corpus

        Returns:
            ForgeResult containing enriched narrative and metadata
        """
        lens = lens or self.config.default_lens
        max_corpus_results = max_corpus_results or self.config.max_corpus_results

        logger.info(
            "forge_start",
            extra={"text_length": len(raw_text), "lens": lens},
        )

        # Step 1: Extract truths from raw input
        extracted_truths = self._extract_truths(raw_text, entity_metadata)
        logger.info("truths_extracted", extra={"count": len(extracted_truths)})

        # Step 2: Retrieve related truths from corpus
        corpus_truths = self.corpus_retriever.retrieve(extracted_truths, max_corpus_results)
        logger.info("corpus_retrieved", extra={"count": len(corpus_truths)})

        # Step 3: Forge them together
        forged = self._forge_synthesis(
            raw_text=raw_text,
            extracted_truths=extracted_truths,
            corpus_truths=corpus_truths,
            lens=lens,
        )

        logger.info(
            "narrative_forged",
            extra={"output_length": len(forged.get("enriched_narrative", ""))},
        )

        return ForgeResult(
            enriched_narrative=forged.get("enriched_narrative", raw_text),
            extracted_truths=extracted_truths,
            corpus_truths=corpus_truths,
            synthesis=forged.get("synthesis", []),
            provenance={
                "source": "furnace_engine_v2",
                "lens": lens,
                "corpus_results_used": len(corpus_truths),
                "truths_extracted": len(extracted_truths),
            },
        )

    def _extract_truths(
        self,
        raw_text: str,
        metadata: dict[str, Any] | None = None,
    ) -> list[Truth]:
        """Extract core truths/patterns/themes from raw text."""
        metadata_str = f"METADATA: {json.dumps(metadata)}" if metadata else ""

        prompt = f"""You are a truth extraction engine. Your job is to identify core truths, patterns, themes, and principles from narratives.

INPUT NARRATIVE:
{raw_text}

{metadata_str}

Extract 5-10 core truths from this narrative. For each truth, identify:
1. **Category**: What type of truth is this? (pattern, principle, theme, event, realization, etc.)
2. **Statement**: A clear, concise statement of the truth
3. **Evidence**: A brief quote or reference from the narrative that supports this truth

Focus on:
- Behavioral patterns (how someone acts/responds)
- Core principles (what someone believes/values)
- Recovery mechanisms (how someone overcomes challenges)
- Identity markers (who someone is fundamentally)
- System insights (how things work)

Return ONLY valid JSON in this format:
{{
  "truths": [
    {{
      "category": "pattern",
      "statement": "The statement of truth",
      "evidence": "Quote from the narrative"
    }}
  ]
}}
"""

        try:
            response = self._call_llm(
                prompt,
                temperature=self.config.extraction_temperature,
                response_format="json",
            )
            result = json.loads(response)
            return [
                Truth(
                    category=t.get("category", "unknown"),
                    statement=t.get("statement", ""),
                    evidence=t.get("evidence", ""),
                )
                for t in result.get("truths", [])
            ]
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("truth_extraction_failed", extra={"error": str(e)})
            return []

    def _forge_synthesis(
        self,
        raw_text: str,
        extracted_truths: list[Truth],
        corpus_truths: list[CorpusTruth],
        lens: str,
    ) -> dict[str, Any]:
        """The forging step: Combine input truths + corpus truths -> enriched narrative."""
        # Build corpus context
        corpus_context = "\n\n".join(
            f"**Corpus Truth {i + 1}** (from {ct.source}, {ct.timestamp}):\n{ct.text}"
            for i, ct in enumerate(corpus_truths[:5])
        )

        # Build extracted truths context
        extracted_context = "\n".join(
            f"- **{t.category.upper()}**: {t.statement}\n  Evidence: {t.evidence}"
            for t in extracted_truths
        )

        prompt = f"""You are the Furnace. Your job is to take raw truth, forge meaning from it, and deliver it with care.

You have been given:
1. A raw narrative (new truth)
2. Truths extracted from that narrative
3. Related truths from the corpus (existing knowledge)

Your task: FORGE THEM TOGETHER.

---

## RAW NARRATIVE (NEW TRUTH)

{raw_text}

---

## EXTRACTED TRUTHS FROM THIS NARRATIVE

{extracted_context}

---

## RELATED TRUTHS FROM CORPUS (EXISTING KNOWLEDGE)

{corpus_context if corpus_context else "(No related corpus truths available)"}

---

## YOUR TASK: THE FURNACE PROCESS

**Take the raw narrative + extracted truths + corpus truths and FORGE them into an enriched narrative.**

The enriched narrative should:

1. **Preserve the original** - Keep the core story intact
2. **Connect to corpus** - Weave in related truths from existing knowledge
3. **Synthesize new insights** - Find patterns across input + corpus that weren't visible before
4. **Deliver with care** - Make it powerful, clear, and useful

**Key questions to answer through synthesis:**
- How does this narrative connect to existing patterns in the corpus?
- What does the corpus reveal about this narrative that wasn't explicit?
- What new insights emerge when you combine these truths?
- What does this add to the body of knowledge?

**Output format:**

Return valid JSON with:
{{
  "enriched_narrative": "The full enriched narrative text (markdown format, 800-1500 words)",
  "synthesis": [
    {{
      "insight": "New insight discovered by combining input + corpus",
      "evidence_from_input": "Quote from original narrative",
      "evidence_from_corpus": "Reference to corpus truth",
      "significance": "Why this matters"
    }}
  ]
}}

**Apply the {lens} lens:**
- Furnace: Raw truth -> Forged meaning -> Delivered with care
- Show the heat, the transformation, the forging process itself

Generate the enriched narrative now.
"""

        try:
            response = self._call_llm(
                prompt,
                temperature=self.config.synthesis_temperature,
                max_tokens=self.config.max_output_tokens,
                response_format="json",
            )
            result: dict[str, Any] = json.loads(response)
            return result
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("synthesis_failed", extra={"error": str(e)})
            return {"enriched_narrative": raw_text, "synthesis": [], "error": str(e)}


class FurnaceEngine(BaseFurnaceEngine):
    """Furnace Engine with pluggable LLM client.

    This is the main implementation that accepts any LLM client
    implementing the LLMClient protocol.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        config: FurnaceConfig | None = None,
        corpus_retriever: CorpusRetriever | None = None,
    ) -> None:
        """Initialize the Furnace Engine.

        Args:
            llm_client: The LLM client to use for generation
            config: Configuration for the engine
            corpus_retriever: Retriever for corpus truths
        """
        super().__init__(config, corpus_retriever)
        self.llm_client = llm_client

    def _call_llm(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: str | None = None,
    ) -> str:
        """Call the LLM client."""
        return self.llm_client.generate(
            prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Data Models
    "Truth",
    "CorpusTruth",
    "ForgeResult",
    "FurnaceConfig",
    # Protocols
    "LLMClient",
    "CorpusRetriever",
    # Implementations
    "BaseFurnaceEngine",
    "FurnaceEngine",
    "NoOpCorpusRetriever",
    "InMemoryCorpusRetriever",
]
