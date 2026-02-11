"""Experiential Integration Protocol - Swimming vs Drowning classification.

THE PARADIGM SHIFT:
From "data cleaning" to "training through lived experience"
We PRESERVE struggle — it is the high-value asset for building resistance.

THE PATTERN:
- HOLD₁: entity_unified entities
- AGENT: Pattern detection (swimming vs drowning classification)
- HOLD₂: struggle_* columns for training weight assignment

From Experiential Integration Protocol:
"Fidelity before flourish — sanitizing is lobotomization."

Swimming (Resolution):
- Problem statement → Struggle evidence → Resolution
- Learning arc, productive friction
- Training weight: 1.0

Drowning (Loop):
- Anxiety → Loop → More anxiety
- PRESERVED for building resistance protocols and "No Module"
- Training weight: 0.5-0.7 (lower but NOT deleted)

Struggle Arc (complete):
- Drowning → Recognition → Swimming
- HIGHEST value — shows complete recovery pattern
- Training weight: 1.2
"""

from __future__ import annotations

import logging
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


# Anxiety markers (drowning indicators)
ANXIETY_MARKERS = [
    "worried",
    "anxious",
    "frustrated",
    "confused",
    "stuck",
    "lost",
    "overwhelmed",
    "don't understand",
    "keeps happening",
    "still not working",
    "giving up",
    "impossible",
    "never works",
    "hate this",
    "so annoying",
    "why won't",
    "can't figure",
    "driving me crazy",
    "at my wit's end",
    "this is ridiculous",
]

# Resolution markers (swimming indicators)
RESOLUTION_MARKERS = [
    "got it",
    "working now",
    "fixed",
    "solved",
    "understand now",
    "makes sense",
    "that's it",
    "perfect",
    "finally",
    "figured it out",
    "that worked",
    "thanks",
    "thank you",
    "awesome",
    "great",
    "exactly what i needed",
    "now i see",
    "ah i see",
    "of course",
    "that explains",
]

# Problem markers (needed for swimming arc)
PROBLEM_MARKERS = [
    "issue",
    "problem",
    "error",
    "bug",
    "broken",
    "not working",
    "fails",
    "crash",
    "exception",
    "unexpected",
    "wrong",
    "incorrect",
    "doesn't work",
    "won't work",
    "how do i",
    "how can i",
    "why does",
    "why is",
    "what's wrong",
]


class StruggleFilterEnrichment(BaseEnrichment):
    """Experiential Integration Protocol - Swimming vs Drowning classification.
    
    Paradigm: ALL data is preserved. Struggle data builds resistance protocols.
    We assign training WEIGHTS, not delete markers.
    """

    ENRICHMENT_NAME = "struggle_filter"
    COLUMNS_OWNED = [
        "struggle_pattern_type",        # swimming | drowning | struggle_arc | neutral
        "struggle_has_problem_statement",
        "struggle_has_struggle_evidence",
        "struggle_has_resolution",
        "struggle_swimming_score",
        "struggle_anxiety_markers",
        "struggle_repetition_count",
        "struggle_escalation_detected",
        "struggle_drowning_score",
        "struggle_training_weight",     # Numeric 0.5-1.2 (replaces training_value)
        "struggle_arc_position",        # null | loop | recognition | resolution
        "struggle_resistance_value",    # How much this builds the "No Module"
    ]
    REQUIRES_EMBEDDING = False

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute struggle filter classification for text.

        Args:
            text: Text content to analyze
            existing_embedding: Not used

        Returns:
            Dictionary with struggle_* columns
        """
        text_lower = text.lower()

        # Detect markers
        anxiety_found = [m for m in ANXIETY_MARKERS if m in text_lower]
        resolution_found = any(m in text_lower for m in RESOLUTION_MARKERS)
        problem_found = any(m in text_lower for m in PROBLEM_MARKERS)
        has_struggle = len(anxiety_found) > 0

        # Repetition detection (same phrases repeated - sign of loop)
        words = text_lower.split()
        word_counts: dict[str, int] = {}
        for w in words:
            if len(w) > 3:  # Only count meaningful words
                word_counts[w] = word_counts.get(w, 0) + 1
        repetition_count = sum(1 for c in word_counts.values() if c > 2)

        # Escalation detection (CAPS, multiple !, increasing negativity)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        exclamation_count = text.count("!")
        question_spam = text.count("?") > 3
        escalation = caps_ratio > 0.3 or exclamation_count > 3 or question_spam

        # Calculate drowning score (0-1)
        drowning_score = 0.0
        drowning_score += len(anxiety_found) * 0.15  # Each anxiety marker
        drowning_score += repetition_count * 0.1  # Repetitive loops
        drowning_score += 0.2 if escalation else 0.0  # Escalation
        drowning_score += 0.1 if not resolution_found and has_struggle else 0.0  # No resolution
        drowning_score = min(1.0, drowning_score)

        # Calculate swimming score (0-1)
        swimming_score = 0.0
        swimming_score += 0.3 if problem_found else 0.0  # Has problem (start of arc)
        swimming_score += 0.2 if has_struggle and len(anxiety_found) < 3 else 0.0  # Moderate struggle
        swimming_score += 0.4 if resolution_found else 0.0  # Has resolution (end of arc)
        swimming_score += 0.1 if problem_found and resolution_found else 0.0  # Full arc bonus
        swimming_score = min(1.0, swimming_score)

        # Determine pattern type, arc position, and training weight
        # EXPERIENTIAL INTEGRATION: All data preserved, weights assigned
        
        # Detect if this is part of a struggle arc
        if problem_found and has_struggle and resolution_found:
            # Complete arc: Drowning → Recognition → Swimming
            pattern_type = "struggle_arc"
            arc_position = "complete"
            training_weight = 1.2  # HIGHEST value - complete recovery pattern
            resistance_value = 0.8  # High value for "No Module"
        elif resolution_found and swimming_score > 0.5:
            pattern_type = "swimming"
            arc_position = "resolution"
            training_weight = 1.0  # Core competence signal
            resistance_value = 0.3
        elif has_struggle and not resolution_found and drowning_score > 0.3:
            pattern_type = "drowning"
            arc_position = "loop"
            # PRESERVED: Drowning builds resistance protocols
            training_weight = 0.7 if drowning_score < 0.7 else 0.5
            resistance_value = min(0.9, drowning_score + 0.2)  # High resistance value
        elif problem_found and has_struggle:
            pattern_type = "drowning"
            arc_position = "recognition"  # Struggling but self-aware
            training_weight = 0.8
            resistance_value = 0.6
        else:
            pattern_type = "neutral"
            arc_position = None
            training_weight = 0.6
            resistance_value = 0.2

        return {
            "struggle_pattern_type": pattern_type,
            "struggle_has_problem_statement": problem_found,
            "struggle_has_struggle_evidence": has_struggle,
            "struggle_has_resolution": resolution_found,
            "struggle_swimming_score": round(swimming_score, 3),
            "struggle_anxiety_markers": anxiety_found,
            "struggle_repetition_count": repetition_count,
            "struggle_escalation_detected": escalation,
            "struggle_drowning_score": round(drowning_score, 3),
            "struggle_training_weight": round(training_weight, 2),
            "struggle_arc_position": arc_position,
            "struggle_resistance_value": round(resistance_value, 2),
        }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    StruggleFilterEnrichment().run()
