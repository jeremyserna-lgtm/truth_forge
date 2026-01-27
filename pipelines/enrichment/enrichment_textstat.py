"""TextStat readability enrichment - Backfill missing readability metrics.

THE PATTERN:
- HOLD₁: entity_unified entities missing TextStat data
- AGENT: TextStat readability analysis
- HOLD₂: textstat_* columns (13 readability metrics)

Current coverage: ~36.9% (202,435 entities)
Target: 80%+ coverage
"""

from __future__ import annotations

import logging
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


class TextStatEnrichment(BaseEnrichment):
    """TextStat readability enrichment."""

    ENRICHMENT_NAME = "textstat"
    COLUMNS_OWNED = [
        "textstat_flesch_reading_ease",
        "textstat_flesch_kincaid_grade",
        "textstat_gunning_fog",
        "textstat_smog_index",
        "textstat_automated_readability_index",
        "textstat_coleman_liau_index",
        "textstat_linsear_write_formula",
        "textstat_dale_chall_readability_score",
        "textstat_difficult_words",
        "textstat_syllable_count",
        "textstat_lexicon_count",
        "textstat_sentence_count",
        "textstat_char_count",
        "textstat_version",
    ]
    REQUIRES_EMBEDDING = False

    def __init__(self) -> None:
        """Initialize TextStat enrichment."""
        super().__init__()
        try:
            import textstat

            self.textstat = textstat
        except ImportError:
            logger.error("textstat package not installed. Install with: pip install textstat")
            raise

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute TextStat readability metrics for text.

        Args:
            text: Text content to analyze
            existing_embedding: Not used for TextStat

        Returns:
            Dictionary with all textstat_* columns
        """
        try:
            return {
                "textstat_flesch_reading_ease": round(
                    float(self.textstat.flesch_reading_ease(text)), 2
                ),
                "textstat_flesch_kincaid_grade": round(
                    float(self.textstat.flesch_kincaid(text)), 2
                ),
                "textstat_gunning_fog": round(float(self.textstat.gunning_fog(text)), 2),
                "textstat_smog_index": round(float(self.textstat.smog_index(text)), 2),
                "textstat_automated_readability_index": round(
                    float(self.textstat.automated_readability_index(text)), 2
                ),
                "textstat_coleman_liau_index": round(
                    float(self.textstat.coleman_liau_index(text)), 2
                ),
                "textstat_linsear_write_formula": round(
                    float(self.textstat.linsear_write_formula(text)), 2
                ),
                "textstat_dale_chall_readability_score": round(
                    float(self.textstat.dale_chall_readability_score(text)), 2
                ),
                "textstat_difficult_words": int(self.textstat.difficult_words(text)),
                "textstat_syllable_count": int(self.textstat.syllable_count(text)),
                "textstat_lexicon_count": int(self.textstat.lexicon_count(text)),
                "textstat_sentence_count": int(self.textstat.sentence_count(text)),
                "textstat_char_count": int(self.textstat.char_count(text)),
                "textstat_version": "0.7.3",
            }
        except Exception as e:
            logger.warning(f"TextStat analysis failed for text (length {len(text)}): {e}")
            # Return None values for all metrics
            return {col: None for col in self.COLUMNS_OWNED if col != "textstat_version"} | {
                "textstat_version": "0.7.3"
            }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    TextStatEnrichment().run()
