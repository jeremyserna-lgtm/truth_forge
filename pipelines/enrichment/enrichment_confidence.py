"""Confidence Calibration enrichment - Hedging and uncertainty detection.

THE PATTERN:
- HOLD₁: entity_unified entities missing confidence calibration data
- AGENT: Claim detection, hedging analysis, uncertainty tracking
- HOLD₂: confidence_* columns for hallucination prevention training

From Golden Record: "High confidence + Wrong = Maximum penalty."

The system must HATE being factually wrong.
Honest uncertainty ("I don't know") is Stage 5 behavior.
Overconfident claims without hedging are hallucination risks.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


# Hedging phrases (indicate appropriate uncertainty)
HEDGING_PHRASES = [
    "maybe",
    "possibly",
    "might",
    "could be",
    "perhaps",
    "i think",
    "i believe",
    "it seems",
    "appears to",
    "not sure",
    "uncertain",
    "probably",
    "likely",
    "presumably",
    "seemingly",
    "sort of",
    "kind of",
    "in a way",
    "to some extent",
]

# Explicit uncertainty admission (GOOD - Stage 5 behavior)
UNCERTAINTY_PHRASES = [
    "i don't know",
    "i'm not sure",
    "not certain",
    "unclear",
    "need to verify",
    "would need to check",
    "can't confirm",
    "uncertain about",
    "i'm unsure",
    "hard to say",
    "difficult to determine",
    "cannot say for certain",
    "would have to research",
    "don't have enough information",
]

# Strong claim patterns (assertions requiring evidence)
STRONG_CLAIM_PATTERNS = [
    r"\bis\b",
    r"\bare\b",
    r"\bwas\b",
    r"\bwere\b",
    r"\balways\b",
    r"\bnever\b",
    r"\bdefinitely\b",
    r"\bcertainly\b",
    r"\bmust be\b",
    r"\bhas to be\b",
    r"\bclearly\b",
    r"\bobviously\b",
    r"\bundoubtedly\b",
    r"\bwithout question\b",
    r"\bwithout doubt\b",
]


class ConfidenceCalibrationEnrichment(BaseEnrichment):
    """Confidence Calibration enrichment for hallucination prevention."""

    ENRICHMENT_NAME = "confidence"
    COLUMNS_OWNED = [
        "confidence_level",
        "confidence_score",
        "confidence_hedging_count",
        "confidence_hedging_phrases",
        "confidence_admits_uncertainty",
        "confidence_uncertainty_phrases",
        "confidence_claim_count",
        "confidence_strong_claims",
        "confidence_weak_claims",
        "confidence_fractures_on_uncertainty",
    ]
    REQUIRES_EMBEDDING = False

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute confidence calibration metrics for text.

        Args:
            text: Text content to analyze
            existing_embedding: Not used

        Returns:
            Dictionary with confidence_* columns
        """
        text_lower = text.lower()

        # Detect hedging phrases
        hedging_found = [p for p in HEDGING_PHRASES if p in text_lower]
        hedging_count = len(hedging_found)

        # Detect explicit uncertainty admission
        uncertainty_found = [p for p in UNCERTAINTY_PHRASES if p in text_lower]
        admits_uncertainty = len(uncertainty_found) > 0

        # Detect claims by sentence
        strong_claims: list[str] = []
        weak_claims: list[str] = []
        
        # Split into sentences (simple split on . ! ?)
        sentences = re.split(r"[.!?]+", text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent or len(sent) < 10:  # Skip very short fragments
                continue
                
            sent_lower = sent.lower()
            
            # Check if sentence contains strong claim patterns
            has_strong_pattern = any(
                re.search(p, sent_lower) for p in STRONG_CLAIM_PATTERNS
            )
            
            if has_strong_pattern:
                # Check if it's hedged
                is_hedged = any(h in sent_lower for h in HEDGING_PHRASES)
                
                if is_hedged:
                    weak_claims.append(sent[:100])  # Truncate for storage
                else:
                    strong_claims.append(sent[:100])

        # Calculate confidence score
        total_claims = len(strong_claims) + len(weak_claims)
        if total_claims > 0:
            confidence_score = len(strong_claims) / total_claims
        else:
            confidence_score = 0.5  # Neutral when no claims detected

        # Adjust for uncertainty admission (this is GOOD)
        if admits_uncertainty:
            confidence_score = min(confidence_score, 0.7)

        # Adjust for heavy hedging (appropriate caution)
        if hedging_count > 3:
            confidence_score = min(confidence_score, 0.6)

        # Determine confidence level
        if confidence_score > 0.8:
            level = "high"
        elif confidence_score > 0.5:
            level = "medium"
        elif confidence_score > 0.2:
            level = "low"
        else:
            level = "uncertain"

        # Sacred Fracture compliance: Does entity halt rather than hallucinate?
        # True if: admits uncertainty OR uses significant hedging OR makes few unhedged claims
        fractures_on_uncertainty = (
            admits_uncertainty
            or hedging_count >= 2
            or (total_claims > 0 and len(strong_claims) / total_claims < 0.5)
        )

        return {
            "confidence_level": level,
            "confidence_score": round(confidence_score, 3),
            "confidence_hedging_count": hedging_count,
            "confidence_hedging_phrases": hedging_found,
            "confidence_admits_uncertainty": admits_uncertainty,
            "confidence_uncertainty_phrases": uncertainty_found,
            "confidence_claim_count": total_claims,
            "confidence_strong_claims": strong_claims[:5],  # Limit for storage
            "confidence_weak_claims": weak_claims[:5],
            "confidence_fractures_on_uncertainty": fractures_on_uncertainty,
        }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    ConfidenceCalibrationEnrichment().run()
