"""TextBlob sentiment enrichment - Backfill missing sentiment data.

THE PATTERN:
- HOLD₁: entity_unified entities missing TextBlob data
- AGENT: TextBlob sentiment analysis
- HOLD₂: textblob_polarity, textblob_subjectivity columns

Current coverage: ~36.9% (202,496 entities)
Target: 80%+ coverage
"""

from __future__ import annotations

import logging
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


class TextBlobEnrichment(BaseEnrichment):
    """TextBlob sentiment enrichment."""

    ENRICHMENT_NAME = "textblob"
    COLUMNS_OWNED = [
        "textblob_polarity",
        "textblob_subjectivity",
        "textblob_version",
    ]
    REQUIRES_EMBEDDING = False

    def __init__(self) -> None:
        """Initialize TextBlob enrichment."""
        super().__init__()
        try:
            from textblob import TextBlob

            self.TextBlob = TextBlob
        except ImportError:
            logger.error("textblob package not installed. Install with: pip install textblob")
            raise

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute TextBlob sentiment for text.

        Args:
            text: Text content to analyze
            existing_embedding: Not used for TextBlob

        Returns:
            Dictionary with textblob_polarity, textblob_subjectivity, textblob_version
        """
        try:
            blob = self.TextBlob(text)
            sentiment = blob.sentiment

            return {
                "textblob_polarity": round(float(sentiment.polarity), 4),
                "textblob_subjectivity": round(float(sentiment.subjectivity), 4),
                "textblob_version": "0.17.1",
            }
        except Exception as e:
            logger.warning(f"TextBlob analysis failed for text (length {len(text)}): {e}")
            # Return None values - will be skipped or handled by pipeline
            return {
                "textblob_polarity": None,
                "textblob_subjectivity": None,
                "textblob_version": "0.17.1",
            }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    TextBlobEnrichment().run()
