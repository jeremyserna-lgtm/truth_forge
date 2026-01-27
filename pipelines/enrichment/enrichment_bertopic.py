"""BERTopic topic modeling completion - Populate missing BERTopic columns.

THE PATTERN:
- HOLD₁: entity_unified entities with bertopic_topic_words but missing topic_id/probability
- AGENT: BERTopic topic assignment
- HOLD₂: bertopic_topic_id, bertopic_topic_probability columns

Current state: bertopic_topic_words is 100%, but bertopic_topic_id, bertopic_topic_probability are 0%

Note: BERTopic requires fitting on a corpus first, then assigning topics.
"""

from __future__ import annotations

import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

from pipelines.enrichment.base_enrichment import BaseEnrichment
from pipelines.enrichment.config import BQ_DATASET_ID, BQ_PROJECT_ID, ENTITY_UNIFIED_TABLE


logger = logging.getLogger(__name__)


class BERTopicEnrichment(BaseEnrichment):
    """BERTopic topic modeling enrichment."""

    ENRICHMENT_NAME: ClassVar[str] = "bertopic"
    COLUMNS_OWNED: ClassVar[list[str]] = [
        "bertopic_topic_id",
        "bertopic_topic_probability",
        "bertopic_model_id",
        "bertopic_version",
    ]
    REQUIRES_EMBEDDING: ClassVar[bool] = True

    def __init__(self) -> None:
        """Initialize BERTopic enrichment."""
        super().__init__()
        self.topic_model = None
        self.model_id = None

        # Try to load existing model
        model_path = getattr(self, "model_path", None)
        if model_path and Path(model_path).exists():
            try:
                with Path(model_path).open("rb") as f:
                    self.topic_model = pickle.load(f)
                self.model_id = Path(model_path).stem
                logger.info(f"Loaded BERTopic model from {model_path}")
            except Exception as e:
                logger.warning(f"Could not load model from {model_path}: {e}")

        # If no model loaded, will need to fit one
        if not self.topic_model:
            logger.warning("No BERTopic model provided. Use --fit-model to fit a new model first.")

    def parse_args(self) -> Any:
        """Extend argument parser with BERTopic-specific options."""
        args = super().parse_args()

        # Add BERTopic-specific args manually (since we can't modify parser after super())
        import sys

        if "--model-path" in sys.argv:
            idx = sys.argv.index("--model-path")
            if idx + 1 < len(sys.argv):
                self.model_path = sys.argv[idx + 1]
        if "--fit-model" in sys.argv:
            self.fit_model_flag = True
        else:
            self.fit_model_flag = False

        return args

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute BERTopic topic assignment for text.

        Args:
            text: Text content to analyze
            existing_embedding: Existing sentence embedding (if available)

        Returns:
            Dictionary with bertopic_topic_id, bertopic_topic_probability
        """
        if not self.topic_model:
            return {
                "bertopic_topic_id": None,
                "bertopic_topic_probability": None,
                "bertopic_model_id": None,
                "bertopic_version": None,
            }

        try:
            # Transform text to get topic
            topics, probs = self.topic_model.transform([text])

            topic_id = int(topics[0]) if topics else -1  # -1 = outlier/noise
            topic_prob = float(probs[0][0]) if probs and len(probs[0]) > 0 else 0.0

            return {
                "bertopic_topic_id": topic_id,
                "bertopic_topic_probability": round(topic_prob, 4),
                "bertopic_model_id": self.model_id or "default",
                "bertopic_version": "0.16.0",
            }

        except Exception as e:
            logger.warning(f"BERTopic analysis failed for text (length {len(text)}): {e}")
            return {
                "bertopic_topic_id": None,
                "bertopic_topic_probability": None,
                "bertopic_model_id": self.model_id or "default",
                "bertopic_version": "0.16.0",
            }

    def fit_model(self, sample_size: int = 10000) -> None:
        """Fit BERTopic model on sample corpus.

        Args:
            sample_size: Number of entities to use for fitting
        """
        try:
            from bertopic import BERTopic
            from sentence_transformers import SentenceTransformer

            logger.info(f"Fitting BERTopic model on {sample_size:,} entities...")

            # Get sample entities
            query = f"""
            SELECT text
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_UNIFIED_TABLE}`
            WHERE text IS NOT NULL
              AND LENGTH(text) > 50
            ORDER BY RAND()
            LIMIT {sample_size}
            """

            query_job = self.client.query(query)
            results = list(query_job.result())
            texts = [row.text for row in results if row.text]

            logger.info(f"Fitting on {len(texts):,} texts...")

            # Fit model
            embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            self.topic_model = BERTopic(embedding_model=embedding_model, verbose=True)
            _topics, _probs = self.topic_model.fit_transform(texts)

            # Save model
            model_id = f"bertopic_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            model_path = f"/tmp/{model_id}.pkl"
            with open(model_path, "wb") as f:
                pickle.dump(self.topic_model, f)

            self.model_id = model_id
            logger.info(f"Model fitted and saved to {model_path}")

        except Exception as e:
            logger.error(f"Failed to fit BERTopic model: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    enrichment = BERTopicEnrichment()
    if getattr(enrichment, "fit_model_flag", False):
        sample_size = 10000
        if "--fit-sample-size" in sys.argv:
            idx = sys.argv.index("--fit-sample-size")
            if idx + 1 < len(sys.argv):
                sample_size = int(sys.argv[idx + 1])
        enrichment.fit_model(sample_size)
    else:
        enrichment.run()
