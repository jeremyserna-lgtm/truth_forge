"""Stage 6: L3 Sentences - Create sentence entities using spaCy.

PATTERN: HOLD1 (staged) → AGENT (spaCy segmentation) → HOLD2 (L3 entities)

Uses spaCy to segment message text into sentences and create L3 sentence
entities with position metadata.

Usage:
    stage = L3SentencesStage(config)
    result = stage.run()
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pipelines.core.stage import Stage
from .base import generate_sentence_id, build_entity_unified_row


logger = logging.getLogger(__name__)


class L3SentencesStage(Stage):
    """Stage 6: Create L3 sentence entities using spaCy."""

    STAGE_TYPE = "entity_creation"

    def __init__(self, config: Any) -> None:
        """Initialize L3 sentences stage.
        
        Args:
            config: Stage configuration.
        """
        super().__init__(config)
        self.nlp = None
        self.sentence_count = 0

    def start_bundle(self) -> None:
        """Load spaCy model once."""
        import spacy
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy model: en_core_web_sm")
        except OSError:
            logger.info("Downloading spaCy model: en_core_web_sm")
            import subprocess
            subprocess.run(
                ["python", "-m", "spacy", "download", "en_core_web_sm"],
                check=True,
            )
            self.nlp = spacy.load("en_core_web_sm")

    def read_input(self) -> list[dict[str, Any]]:
        """Load input and initialize spaCy."""
        self.start_bundle()
        return super().read_input()

    def transform(self, record: dict[str, Any]) -> dict[str, Any] | None:
        """Segment message text into sentences using spaCy.
        
        Args:
            record: Staged message record.
            
        Returns:
            Dict with L3 sentence entities for this message.
        """
        if not self.nlp:
            logger.error("spaCy model not loaded")
            return None
        
        text = record.get("text", "")
        if not text:
            return None
        
        message_id = record["entity_id"]
        conversation_id = record["conversation_id"]
        source_pipeline = record["source_pipeline"]
        
        # Segment with spaCy
        doc = self.nlp(text)
        
        sentences = []
        for i, sent in enumerate(doc.sents):
            sentence_id = generate_sentence_id(message_id, i)
            
            # Extract sentence position metadata
            sent_metadata = {
                "start_char": sent.start_char,
                "end_char": sent.end_char,
                "sentence_index": i,
                "role": record.get("role"),
                "message_type": record.get("message_type"),
            }
            
            # Build entity_unified row
            sent_row = build_entity_unified_row(
                entity_id=sentence_id,
                level=3,
                entity_type="sentence",
                source_pipeline=source_pipeline,
                parent_id=message_id,
                conversation_id=conversation_id,
                message_id=message_id,
                sentence_id=sentence_id,
                text=sent.text,
                metadata=sent_metadata,
                content_date=record.get("content_date"),
                source_file=record.get("source_file"),
                source_message_timestamp=record.get("timestamp_utc"),
            )
            
            sentences.append(sent_row)
            self.sentence_count += 1
        
        # Return wrapper with sentences
        return {
            "message_id": message_id,
            "l3_count": len(sentences),
            "sentences": sentences,
        }

    def write_output(self, results: list[dict[str, Any]]) -> int:
        """Write L3 sentence entities to output.
        
        Args:
            results: List of sentence result dicts.
            
        Returns:
            Number of sentences written.
        """
        output_path = self.config.output_path
        import json
        from pathlib import Path
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Flatten sentences from all messages
        with open(output_path, "w", encoding="utf-8") as f:
            for result in results:
                if result and "sentences" in result:
                    for sentence in result["sentences"]:
                        f.write(json.dumps(sentence) + "\n")
        
        logger.info(f"Wrote {self.sentence_count} L3 sentences to {output_path}")
        return self.sentence_count


__all__ = ["L3SentencesStage"]
