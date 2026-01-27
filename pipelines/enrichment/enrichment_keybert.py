"""KeyBERT keyword extraction completion - Populate missing KeyBERT columns.

THE PATTERN:
- HOLD₁: entity_unified entities with keybert_top_5_keywords but missing other KeyBERT data
- AGENT: KeyBERT keyword extraction
- HOLD₂: keybert_top_keyword, keybert_top_score, keybert_all_keywords columns

Current state: keybert_top_5_keywords is 100%, but keybert_top_keyword, keybert_top_score, keybert_all_keywords are 0%
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


class KeyBERTEnrichment(BaseEnrichment):
    """KeyBERT keyword extraction enrichment."""

    ENRICHMENT_NAME = "keybert"
    COLUMNS_OWNED = [
        "keybert_top_keyword",
        "keybert_top_score",
        "keybert_all_keywords",
        "keybert_version",
    ]
    REQUIRES_EMBEDDING = True

    def __init__(self) -> None:
        """Initialize KeyBERT enrichment."""
        super().__init__()
        self.keybert_model = None
        self.embedding_model = None
        try:
            from keybert import KeyBERT
            from sentence_transformers import SentenceTransformer

            # Use same embedding model as BERTopic for consistency
            embedding_model_name = "all-MiniLM-L6-v2"
            self.embedding_model = SentenceTransformer(embedding_model_name)
            self.keybert_model = KeyBERT(model=self.embedding_model)

            logger.info(f"KeyBERT model loaded with {embedding_model_name}")

        except ImportError:
            logger.error(
                "keybert or sentence-transformers not installed. Install with: pip install keybert sentence-transformers"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to load KeyBERT model: {e}")
            raise

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute KeyBERT keywords for text.

        Args:
            text: Text content to analyze
            existing_embedding: Existing sentence embedding (if available)

        Returns:
            Dictionary with keybert_top_keyword, keybert_top_score, keybert_all_keywords
        """
        if not self.keybert_model:
            return {
                "keybert_top_keyword": None,
                "keybert_top_score": None,
                "keybert_all_keywords": None,
                "keybert_version": None,
            }

        try:
            # Extract keywords
            # Use existing embedding if available, otherwise KeyBERT will compute
            if existing_embedding:
                # Reshape for KeyBERT (needs 2D array)
                import numpy as np

                doc_embedding = np.array(existing_embedding).reshape(1, -1)
                keywords = self.keybert_model.extract_keywords(
                    text,
                    keyphrase_ngram_range=(1, 2),
                    stop_words="english",
                    top_n=20,  # Get top 20 for all_keywords
                    doc_embeddings=doc_embedding,
                    use_mmr=True,
                    diversity=0.5,
                )
            else:
                keywords = self.keybert_model.extract_keywords(
                    text,
                    keyphrase_ngram_range=(1, 2),
                    stop_words="english",
                    top_n=20,
                    use_mmr=True,
                    diversity=0.5,
                )

            if not keywords:
                return {
                    "keybert_top_keyword": None,
                    "keybert_top_score": None,
                    "keybert_all_keywords": None,
                    "keybert_version": "0.8.3",
                }

            # Top keyword and score
            top_keyword, top_score = keywords[0]

            # All keywords as JSON (limit to top 20 to avoid huge JSON)
            all_keywords_dict = {kw: float(score) for kw, score in keywords[:20]}

            return {
                "keybert_top_keyword": str(top_keyword),
                "keybert_top_score": round(float(top_score), 4),
                "keybert_all_keywords": json.dumps(all_keywords_dict),
                "keybert_version": "0.8.3",
            }

        except Exception as e:
            logger.warning(f"KeyBERT analysis failed for text (length {len(text)}): {e}")
            return {
                "keybert_top_keyword": None,
                "keybert_top_score": None,
                "keybert_all_keywords": None,
                "keybert_version": "0.8.3",
            }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    KeyBERTEnrichment().run()
