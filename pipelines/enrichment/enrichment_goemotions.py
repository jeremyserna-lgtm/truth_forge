"""GoEmotions enrichment - Backfill missing emotion classification data.

THE PATTERN:
- HOLD₁: entity_unified entities missing GoEmotions data
- AGENT: GoEmotions emotion classifier
- HOLD₂: goemotions_* columns

Current coverage: ~36.4% (199,693 entities)
Target: 80%+ coverage

Note: Requires GPU for performance (can run on CPU but slower).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


class GoEmotionsEnrichment(BaseEnrichment):
    """GoEmotions emotion classification enrichment."""

    ENRICHMENT_NAME = "goemotions"
    COLUMNS_OWNED = [
        "goemotions_scores",
        "goemotions_top_emotions",
        "goemotions_primary_emotion",
        "goemotions_primary_score",
        "goemotions_model",
        "goemotions_version",
    ]
    REQUIRES_EMBEDDING = False

    def __init__(self) -> None:
        """Initialize GoEmotions enrichment."""
        super().__init__()
        self.model = None
        self.tokenizer = None
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            model_name = "j-hartmann/emotion-english-distilroberta-base"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

            # Use GPU if available
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            self.model.eval()

            logger.info(f"GoEmotions model loaded on {self.device}")

        except ImportError:
            logger.error(
                "transformers package not installed. Install with: pip install transformers torch"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to load GoEmotions model: {e}")
            raise

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute GoEmotions classification for text.

        Args:
            text: Text content to analyze
            existing_embedding: Not used for GoEmotions

        Returns:
            Dictionary with goemotions_* columns
        """
        if not self.model or not self.tokenizer:
            return {
                "goemotions_scores": None,
                "goemotions_top_emotions": None,
                "goemotions_primary_emotion": None,
                "goemotions_primary_score": None,
                "goemotions_model": None,
                "goemotions_version": None,
            }

        try:
            import torch

            # Tokenize and predict
            inputs = self.tokenizer(
                text, return_tensors="pt", truncation=True, max_length=512, padding=True
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)[0]

            # Get emotion labels (27 emotions in GoEmotions)
            emotion_labels = [
                "admiration",
                "amusement",
                "anger",
                "annoyance",
                "approval",
                "caring",
                "confusion",
                "curiosity",
                "desire",
                "disappointment",
                "disapproval",
                "disgust",
                "embarrassment",
                "excitement",
                "fear",
                "gratitude",
                "grief",
                "joy",
                "love",
                "nervousness",
                "optimism",
                "pride",
                "realization",
                "relief",
                "remorse",
                "sadness",
                "surprise",
            ]

            # Get scores
            scores = {
                label: float(prob.item()) for label, prob in zip(emotion_labels, probabilities)
            }

            # Get top emotions (top 3)
            sorted_emotions = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            top_emotions = [emotion for emotion, _ in sorted_emotions[:3]]
            primary_emotion, primary_score = sorted_emotions[0]

            return {
                "goemotions_scores": json.dumps(scores),
                "goemotions_top_emotions": top_emotions,
                "goemotions_primary_emotion": primary_emotion,
                "goemotions_primary_score": round(primary_score, 4),
                "goemotions_model": "j-hartmann/emotion-english-distilroberta-base",
                "goemotions_version": "0.1.0",
            }

        except Exception as e:
            logger.warning(f"GoEmotions analysis failed for text (length {len(text)}): {e}")
            return {
                "goemotions_scores": None,
                "goemotions_top_emotions": None,
                "goemotions_primary_emotion": None,
                "goemotions_primary_score": None,
                "goemotions_model": "j-hartmann/emotion-english-distilroberta-base",
                "goemotions_version": "0.1.0",
            }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    GoEmotionsEnrichment().run()
