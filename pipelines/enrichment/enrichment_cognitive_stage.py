"""Cognitive Stage enrichment - Kegan 1-5 classification.

THE PATTERN:
- HOLD₁: entity_unified entities missing cognitive stage data
- AGENT: Vocabulary pattern detection (banned vs manifestation)
- HOLD₂: cognitive_* columns for Stage 5 training

From Golden Record: "Stage 5 is the floor, not the ceiling."

Stage 4 indicators (validation seeking, helper posture):
- "Is this what you wanted?"
- "I'm happy to help"
- "Fascinating"

Stage 5 indicators (sovereign, manifestation):
- "This is"
- "The data shows"
- "I don't know" (honest uncertainty is GOOD)
"""

from __future__ import annotations

import logging
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


# Stage 4 banned vocabulary (validation seeking, helper posture)
BANNED_VOCABULARY = [
    # Validation seeking
    "is this what you wanted",
    "does this sound okay",
    "is that correct",
    "would you like me to",
    "should i proceed",
    "let me know if",
    "hope this helps",
    "hope that helps",
    "does that make sense",
    "is there anything else",
    # Helper posture
    "i'm here to assist",
    "i'm happy to help",
    "how can i help you",
    "i'd be happy to",
    "feel free to ask",
    # Stage 4 recursion markers (engagement theater)
    "fascinating",
    "profound",
    "remarkable",
    "impressive",
    "that's really interesting",
    "great question",
    "excellent question",
    "wonderful",
    "absolutely",
]

# Stage 5 manifestation vocabulary (direct, evidence-based, honest)
MANIFESTATION_VOCABULARY = [
    # Direct statements
    "this is",
    "here is",
    "the pattern shows",
    "based on the data",
    "the analysis reveals",
    "i see that",
    "looking at this",
    # Honest uncertainty (GOOD in Stage 5)
    "i don't know",
    "i'm not sure",
    "i cannot determine",
    "unclear from",
    "would need more information",
    # Evidence-based
    "the evidence suggests",
    "the data indicates",
    "according to",
    "based on",
    # Direct action
    "let's",
    "we can",
    "the solution is",
    "the issue is",
]


class CognitiveStageEnrichment(BaseEnrichment):
    """Cognitive Stage (Kegan 1-5) enrichment."""

    ENRICHMENT_NAME = "cognitive_stage"
    COLUMNS_OWNED = [
        "cognitive_stage",
        "cognitive_stage_confidence",
        "cognitive_stage_markers",
        "cognitive_banned_vocab_count",
        "cognitive_banned_vocab_matches",
        "cognitive_manifestation_vocab_count",
        "cognitive_manifestation_vocab_matches",
        "cognitive_stage_polarity",
    ]
    REQUIRES_EMBEDDING = False

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute cognitive stage classification for text.

        Args:
            text: Text content to analyze
            existing_embedding: Not used

        Returns:
            Dictionary with cognitive_* columns
        """
        text_lower = text.lower()

        # Detect banned vocabulary (Stage 4 indicators)
        banned_matches = [v for v in BANNED_VOCABULARY if v in text_lower]
        banned_count = len(banned_matches)

        # Detect manifestation vocabulary (Stage 5 indicators)
        manifestation_matches = [v for v in MANIFESTATION_VOCABULARY if v in text_lower]
        manifestation_count = len(manifestation_matches)

        # Calculate stage polarity: positive = Stage 5, negative = Stage 4
        total = banned_count + manifestation_count
        if total > 0:
            polarity = (manifestation_count - banned_count) / total
        else:
            polarity = 0.0

        # Determine stage
        if polarity > 0.3:
            stage = 5
            confidence = min(0.9, 0.6 + polarity * 0.3)
        elif polarity < -0.3:
            stage = 4
            confidence = min(0.9, 0.6 + abs(polarity) * 0.3)
        else:
            stage = 3  # Neutral/ambiguous
            confidence = 0.5

        # Combine markers for storage
        all_markers = banned_matches + manifestation_matches

        return {
            "cognitive_stage": stage,
            "cognitive_stage_confidence": round(confidence, 3),
            "cognitive_stage_markers": all_markers,
            "cognitive_banned_vocab_count": banned_count,
            "cognitive_banned_vocab_matches": banned_matches,
            "cognitive_manifestation_vocab_count": manifestation_count,
            "cognitive_manifestation_vocab_matches": manifestation_matches,
            "cognitive_stage_polarity": round(polarity, 3),
        }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    CognitiveStageEnrichment().run()
