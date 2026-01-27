"""RoBERTa hate speech detection enrichment - Backfill missing toxicity data.

THE PATTERN:
- HOLD₁: entity_unified entities missing RoBERTa hate data
- AGENT: RoBERTa hate speech classifier
- HOLD₂: roberta_hate_label, roberta_hate_score columns

Current coverage: ~36.4% (200,027 entities)
Target: 80%+ coverage

Note: Requires GPU for performance (can run on CPU but slower).
"""

from __future__ import annotations

import logging
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


class RoBERTaHateEnrichment(BaseEnrichment):
    """RoBERTa hate speech detection enrichment."""

    ENRICHMENT_NAME = "roberta_hate"
    COLUMNS_OWNED = [
        "roberta_hate_label",
        "roberta_hate_score",
        "roberta_hate_model",
        "roberta_hate_version",
    ]
    REQUIRES_EMBEDDING = False

    def __init__(self) -> None:
        """Initialize RoBERTa hate speech enrichment."""
        super().__init__()
        self.model = None
        self.tokenizer = None
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            # Use hate-speech-detection model
            model_name = "facebook/roberta-hate-speech-dynabench-r4-target"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

            # Use GPU if available
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            self.model.eval()

            logger.info(f"RoBERTa hate speech model loaded on {self.device}")

        except ImportError:
            logger.error(
                "transformers package not installed. Install with: pip install transformers torch"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to load RoBERTa hate speech model: {e}")
            raise

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute RoBERTa hate speech detection for text.

        Args:
            text: Text content to analyze
            existing_embedding: Not used for RoBERTa

        Returns:
            Dictionary with roberta_hate_label, roberta_hate_score
        """
        if not self.model or not self.tokenizer:
            return {
                "roberta_hate_label": None,
                "roberta_hate_score": None,
                "roberta_hate_model": None,
                "roberta_hate_version": None,
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

            # Labels: ["normal", "hate"]
            labels = ["normal", "hate"]
            scores = {label: float(prob.item()) for label, prob in zip(labels, probabilities)}

            # Get hate score and label
            hate_score = scores.get("hate", 0.0)
            label = "hate" if hate_score > 0.5 else "normal"

            return {
                "roberta_hate_label": label,
                "roberta_hate_score": round(hate_score, 4),
                "roberta_hate_model": "facebook/roberta-hate-speech-dynabench-r4-target",
                "roberta_hate_version": "0.1.0",
            }

        except Exception as e:
            logger.warning(
                f"RoBERTa hate speech analysis failed for text (length {len(text)}): {e}"
            )
            return {
                "roberta_hate_label": None,
                "roberta_hate_score": None,
                "roberta_hate_model": "facebook/roberta-hate-speech-dynabench-r4-target",
                "roberta_hate_version": "0.1.0",
            }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    RoBERTaHateEnrichment().run()
