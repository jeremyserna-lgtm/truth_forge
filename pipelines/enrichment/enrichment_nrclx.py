"""NRCLx emotion enrichment - Backfill missing emotion data.

THE PATTERN:
- HOLD₁: entity_unified entities missing NRCLx data
- AGENT: NRCLx emotion analysis
- HOLD₂: nrclx_emotions, nrclx_top_emotion, nrclx_top_count columns

Current coverage: ~36.5% (200,115 entities), but nrclx_top_emotion only 24.3%
Target: 80%+ coverage, fix nrclx_top_emotion gap
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


class NRCLxEnrichment(BaseEnrichment):
    """NRCLx emotion enrichment."""

    ENRICHMENT_NAME = "nrclx"
    COLUMNS_OWNED = [
        "nrclx_emotions",
        "nrclx_top_emotion",
        "nrclx_top_count",
        "nrclx_version",
    ]
    REQUIRES_EMBEDDING = False

    def __init__(self) -> None:
        """Initialize NRCLx enrichment."""
        super().__init__()
        try:
            from nrclex import NRCLex

            self.NRCLex = NRCLex
        except ImportError:
            logger.error("nrclex package not installed. Install with: pip install nrclex")
            raise

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute NRCLx emotions for text.

        Args:
            text: Text content to analyze
            existing_embedding: Not used for NRCLx

        Returns:
            Dictionary with nrclx_emotions (JSON), nrclx_top_emotion, nrclx_top_count
        """
        try:
            emotion_obj = self.NRCLex(text)
            affects = emotion_obj.affect_frequencies or {}

            # Normalize to percentages (0.0-1.0)
            total = sum(affects.values()) if affects else 1.0
            normalized = {
                emotion: round(float(score / total), 4) if total > 0 else 0.0
                for emotion, score in affects.items()
            }

            # Find top emotion
            top_emotion = None
            top_count = 0
            if affects:
                top_emotion = max(affects.items(), key=lambda item: item[1])[0]
                top_count = int(affects[top_emotion])

            return {
                "nrclx_emotions": json.dumps(normalized),
                "nrclx_top_emotion": top_emotion,
                "nrclx_top_count": top_count,
                "nrclx_version": "0.1.0",
            }
        except Exception as e:
            logger.warning(f"NRCLx analysis failed for text (length {len(text)}): {e}")
            return {
                "nrclx_emotions": None,
                "nrclx_top_emotion": None,
                "nrclx_top_count": None,
                "nrclx_version": "0.1.0",
            }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    NRCLxEnrichment().run()
