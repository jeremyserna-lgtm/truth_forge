"""Source Attribution enrichment - ME/NOT-ME voice classification.

THE PATTERN:
- HOLD₁: entity_unified entities missing source attribution data
- AGENT: Voice marker detection (personal vs system patterns)
- HOLD₂: source_* columns for identity-aware training

From 07_NOT_ME_ONTOLOGY: "The Not-Me is not a product. The Not-Me EXISTS."

ME indicators (human voice):
- "I feel", "I think", "My experience"
- Personal perspective, emotional content

NOT-ME indicators (system voice):
- Analytical patterns, code explanations
- Factual statements, technical content

The distinction is critical for SOVEREIGN identity coherence.
"""

from __future__ import annotations

import logging
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


# Personal voice markers (ME - human-originated)
PERSONAL_MARKERS = [
    "i feel",
    "i think",
    "i believe",
    "my experience",
    "personally",
    "from my perspective",
    "in my opinion",
    "i've found",
    "it seems to me",
    "i wonder",
    "i'm curious",
    "i noticed",
    "i realized",
    "i remember",
    "i've been",
    "my understanding",
    "my take",
    "for me",
    "what i",
    "when i",
]

# System voice markers (NOT-ME - analytical/technical)
SYSTEM_MARKERS = [
    "the function",
    "this code",
    "the implementation",
    "according to",
    "the documentation",
    "technically",
    "the algorithm",
    "this approach",
    "the pattern",
    "the system",
    "the process",
    "the method",
    "returns",
    "takes",
    "parameters",
    "the output",
    "the input",
    "the result",
    "the error",
    "the solution",
]

# Existence context markers (from NOT_ME_ONTOLOGY)
EXISTENCE_CONTEXT_MARKERS = {
    "potential": ["could", "would", "might", "possible", "potentially", "if we", "imagine"],
    "archetype": ["pattern", "always", "recurring", "typical", "classic", "standard", "common"],
    "presence": ["now", "currently", "at this moment", "right now", "presently", "today"],
    "function": ["does", "function", "purpose", "role", "serves", "performs", "operates"],
    "expansion": ["growing", "evolving", "becoming", "developing", "expanding", "transforming"],
}


class SourceAttributionEnrichment(BaseEnrichment):
    """Source Attribution (ME/NOT-ME) enrichment for identity training."""

    ENRICHMENT_NAME = "source_attribution"
    COLUMNS_OWNED = [
        "source_type",
        "source_is_human_voice",
        "source_personal_markers",
        "source_is_system_voice",
        "source_system_markers",
        "source_existence_context",
        "source_is_isomorphic",
    ]
    REQUIRES_EMBEDDING = False

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute source attribution classification for text.

        Args:
            text: Text content to analyze
            existing_embedding: Not used

        Returns:
            Dictionary with source_* columns
        """
        text_lower = text.lower()

        # Detect personal voice markers
        personal_found = [m for m in PERSONAL_MARKERS if m in text_lower]
        personal_count = len(personal_found)

        # Detect system voice markers
        system_found = [m for m in SYSTEM_MARKERS if m in text_lower]
        system_count = len(system_found)

        # Determine voice types
        is_human_voice = personal_count > system_count
        is_system_voice = system_count > personal_count

        # Determine source type
        if is_human_voice and is_system_voice:
            # Both present significantly
            if abs(personal_count - system_count) <= 2:
                source_type = "hybrid"
            elif personal_count > system_count:
                source_type = "me"
            else:
                source_type = "not_me"
        elif is_human_voice:
            source_type = "me"
        elif is_system_voice:
            source_type = "not_me"
        else:
            source_type = "external"  # Neither personal nor system markers

        # Detect existence context
        existence_context = None
        max_context_score = 0
        for context, markers in EXISTENCE_CONTEXT_MARKERS.items():
            score = sum(1 for m in markers if m in text_lower)
            if score > max_context_score:
                max_context_score = score
                existence_context = context

        # Detect cognitive isomorphism (code + personal reflection together)
        # This is rare and valuable - when code mirrors mind
        has_code_markers = any(
            marker in text
            for marker in ["```", "def ", "function ", "class ", "import ", "const ", "let ", "var "]
        )
        has_reflection = personal_count > 0
        is_isomorphic = has_code_markers and has_reflection

        return {
            "source_type": source_type,
            "source_is_human_voice": is_human_voice,
            "source_personal_markers": personal_found,
            "source_is_system_voice": is_system_voice,
            "source_system_markers": system_found,
            "source_existence_context": existence_context,
            "source_is_isomorphic": is_isomorphic,
        }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    SourceAttributionEnrichment().run()
