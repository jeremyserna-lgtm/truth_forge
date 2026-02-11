"""Stage 5: L1 Tokens - Create token entities using spaCy.

PATTERN: HOLD1 (staged) → AGENT (spaCy tokenization) → HOLD2 (L1 entities)

Uses spaCy to tokenize message text and create L1 token entities with
linguistic attributes (POS tags, lemmas, dependencies).

Usage:
    stage = L1TokensStage(config)
    result = stage.run()
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pipelines.core.stage import Stage
from .base import generate_token_id, build_entity_unified_row


logger = logging.getLogger(__name__)


class L1TokensStage(Stage):
    """Stage 5: Create L1 token entities using spaCy."""

    STAGE_TYPE = "entity_creation"

    def __init__(self, config: Any) -> None:
        """Initialize L1 tokens stage.
        
        Args:
            config: Stage configuration.
        """
        super().__init__(config)
        self.nlp = None
        self.token_count = 0

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
        """Tokenize message text and create L1 entities.
        
        Args:
            record: Staged message record.
            
        Returns:
            Dict with L1 token entities for this message.
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
        
        # Tokenize with spaCy
        doc = self.nlp(text)
        
        tokens = []
        for i, token in enumerate(doc):
            token_id = generate_token_id(message_id, i)
            
            # Extract linguistic attributes
            token_metadata = {
                "pos": token.pos_,
                "tag": token.tag_,
                "dep": token.dep_,
                "shape": token.shape_,
                "is_alpha": token.is_alpha,
                "is_stop": token.is_stop,
                "is_punct": token.is_punct,
                "token_index": i,
            }
            
            # Build entity_unified row
            token_row = build_entity_unified_row(
                entity_id=token_id,
                level=1,
                entity_type="token",
                source_pipeline=source_pipeline,
                parent_id=message_id,
                conversation_id=conversation_id,
                message_id=message_id,
                text=token.text,
                canonical_form=token.lemma_,  # Lemma as canonical form
                metadata=token_metadata,
                content_date=record.get("content_date"),
                source_file=record.get("source_file"),
                source_message_timestamp=record.get("timestamp_utc"),
            )
            
            tokens.append(token_row)
            self.token_count += 1
        
        # Return wrapper with tokens
        return {
            "message_id": message_id,
            "l1_count": len(tokens),
            "tokens": tokens,
        }

    def write_output(self, results: list[dict[str, Any]]) -> int:
        """Write L1 token entities to output.
        
        Args:
            results: List of token result dicts.
            
        Returns:
            Number of tokens written.
        """
        output_path = self.config.output_path
        import json
        from pathlib import Path
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Flatten tokens from all messages
        with open(output_path, "w", encoding="utf-8") as f:
            for result in results:
                if result and "tokens" in result:
                    for token in result["tokens"]:
                        f.write(json.dumps(token) + "\n")
        
        logger.info(f"Wrote {self.token_count} L1 tokens to {output_path}")
        return self.token_count


__all__ = ["L1TokensStage"]
