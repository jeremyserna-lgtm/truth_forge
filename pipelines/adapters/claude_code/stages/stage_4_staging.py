"""Stage 4: Staging - LLM Cleaning + Prepare for SPINE entity creation.

PATTERN: HOLD1 (with IDs) → AGENT (LLM cleaning + staging) → HOLD2 (cleaned & staged)

CRITICAL: This stage performs LLM-based text cleaning (spelling/grammar) using Gemini
BEFORE entity creation. This ensures spaCy processes clean text in stages 5-6.

Flow:
1. Clean user message text with Gemini (preserve meaning/tone)
2. Structure metadata
3. Prepare for entity creation

Usage:
    stage = StagingStage(config)
    result = stage.run()
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pipelines.core.stage import Stage


logger = logging.getLogger(__name__)


class StagingStage(Stage):
    """Stage 4: LLM cleaning and staging for SPINE entity creation."""

    STAGE_TYPE = "staging"

    def __init__(self, config: Any) -> None:
        """Initialize staging stage.
        
        Args:
            config: Stage configuration.
        """
        super().__init__(config)
        self.gemini_client = None
        self.cleaned_count = 0

    def transform(self, record: dict[str, Any]) -> dict[str, Any]:
        """Clean text with LLM and stage record for entity creation.
        
        Args:
            record: Record with entity IDs from stage 3.
            
        Returns:
            Staged record with cleaned text, ready for entity creation.
        """
        text = record["text"]
        text_original = record.get("text_original", text)
        role = record["role"]
        
        # Clean user messages with Gemini (assistant messages are canonical)
        cleaned_text = text
        cleaning_applied = False
        cleaning_method = None
        
        if role == "user" and len(text) > 10:
            gemini_cleaned = self._clean_with_gemini(text)
            if gemini_cleaned and gemini_cleaned != text:
                cleaned_text = gemini_cleaned
                cleaning_applied = True
                cleaning_method = "gemini-2.0-flash-lite"
                self.cleaned_count += 1
                logger.debug(f"Cleaned message {record['entity_id']}")
        
        # Structure core metadata
        metadata = {
            "role": role,
            "message_type": record["message_type"],
            "message_index": record["message_index"],
            "text_original": text_original,
            "cleaning_applied": cleaning_applied,
            "cleaning_method": cleaning_method,
        }
        
        # Merge additional metadata
        if record.get("raw_metadata"):
            metadata.update(record["raw_metadata"])
        
        # Build staged record
        staged = {
            # Identity fields (from Stage 3)
            "entity_id": record["entity_id"],
            "conversation_id": record["conversation_id"],
            "source_pipeline": record["source_pipeline"],
            
            # Core content (CLEANED TEXT)
            "text": cleaned_text,  # ← This is the cleaned version
            "role": role,
            "message_type": record["message_type"],
            
            # Temporal
            "timestamp_utc": record.get("timestamp_utc"),
            "content_date": record.get("content_date"),
            
            # Source tracking
            "source_file": record.get("source_file"),
            
            # Structured metadata (JSON string for BigQuery)
            "metadata_json": json.dumps(metadata),
            
            # Placeholder hierarchy fields (will be populated in entity creation)
            "level": 5,  # L5 = message
            "entity_type": "message",
            "parent_id": None,
            "l3_count": None,  # Will be calculated from sentence segmentation
            "l1_count": None,  # Will be calculated from tokenization
        }
        
        return staged

    def _clean_with_gemini(self, text: str) -> str | None:
        """Clean text using Gemini (spelling/grammar only).
        
        CRITICAL: Only fixes spelling/grammar. Does NOT change:
        - Meaning or intent
        - Tone or emojis
        - Technical content (code, file paths)
        
        Args:
            text: Original text.
            
        Returns:
            Cleaned text, or None if error/unavailable.
        """
        if self.gemini_client is None:
            try:
                import os
                import google.generativeai as genai
                
                api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
                if not api_key:
                    logger.info("No Gemini API key found, skipping LLM text cleaning")
                    return None
                
                genai.configure(api_key=api_key)
                self.gemini_client = genai.GenerativeModel("gemini-2.0-flash-lite")
                logger.info("Initialized Gemini for text cleaning")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
                return None
        
        try:
            prompt = (
                f"Fix spelling and grammar errors ONLY. "
                f"Do NOT change meaning, tone, emojis, or technical content (code/paths). "
                f"Return ONLY the corrected text, no explanations.\n\n{text[:2000]}"
            )
            response = self.gemini_client.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini cleaning failed for text: {e}")
            return None

    def write_output(self, records: list[dict[str, Any]]) -> int:
        """Write staged records.
        
        Args:
            records: Staged records with cleaned text.
            
        Returns:
            Number of records written.
        """
        count = super().write_output(records)
        
        if self.cleaned_count > 0:
            logger.info(f"LLM cleaned {self.cleaned_count}/{count} user messages")
        
        return count


__all__ = ["StagingStage"]
