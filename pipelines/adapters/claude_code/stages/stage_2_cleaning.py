"""Stage 2: Cleaning - Normalize and validate data.

PATTERN: HOLD1 (extracted) → AGENT (cleaning) → HOLD2 (cleaned)

Normalizes timestamps, deduplicates records, validates content,
and optionally cleans user message text using Gemini.

Usage:
    stage = CleaningStage(config)
    result = stage.run()
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from pipelines.core.stage import Stage


logger = logging.getLogger(__name__)


class CleaningStage(Stage):
    """Stage 2: Clean and normalize extracted data."""

    STAGE_TYPE = "cleaning"

    def __init__(self, config: Any) -> None:
        """Initialize cleaning stage.
        
        Args:
            config: Stage configuration.
        """
        super().__init__(config)
        self.seen_keys: set[tuple[str, int]] = set()
        self.duplicate_count = 0
        self.gemini_client = None
        self.use_gemini = config.extra.get("use_gemini_cleaning", False)

    def transform(self, record: dict[str, Any]) -> dict[str, Any] | None:
        """Clean and normalize a single record.
        
        Args:
            record: Extracted record.
            
        Returns:
            Cleaned record, or None if duplicate/invalid.
        """
        # Deduplicate by (session_id, message_index)
        key = (record["session_id"], record["message_index"])
        if key in self.seen_keys:
            self.duplicate_count += 1
            logger.debug(f"Skipping duplicate: {key}")
            return None
        self.seen_keys.add(key)
        
        # Normalize text
        text = record["text"].strip()
        if not text and record["role"] in ("user", "assistant"):
            logger.warning(
                f"Empty text for {record['role']} message: "
                f"{record['session_id']}[{record['message_index']}]"
            )
            return None
        
        # Normalize timestamp to ISO 8601
        timestamp_utc = record.get("timestamp_utc")
        if timestamp_utc:
            try:
                # Parse and re-format to ensure ISO 8601
                if isinstance(timestamp_utc, str):
                    dt = datetime.fromisoformat(timestamp_utc.replace("Z", "+00:00"))
                    timestamp_utc = dt.isoformat()
            except ValueError as e:
                logger.warning(f"Invalid timestamp: {timestamp_utc}: {e}")
                timestamp_utc = None
        
        # Build cleaned record
        cleaned = {
            "session_id": record["session_id"],
            "message_index": record["message_index"],
            "text": text,
            "text_original": record["text"],  # Preserve original
            "role": record["role"],
            "message_type": record["message_type"],
            "source_file": record.get("source_file"),
            "timestamp_utc": timestamp_utc,
            "content_date": record.get("content_date"),
            "raw_metadata": record.get("raw_metadata", {}),
            "cleaning_applied": False,
            "cleaning_method": None,
        }
        
        # Optional: Gemini text cleaning for user messages
        if self.use_gemini and record["role"] == "user" and len(text) > 10:
            cleaned_text = self._clean_with_gemini(text)
            if cleaned_text and cleaned_text != text:
                cleaned["text"] = cleaned_text
                cleaned["cleaning_applied"] = True
                cleaned["cleaning_method"] = "gemini-2.0-flash-lite"
        
        return cleaned

    def _clean_with_gemini(self, text: str) -> str | None:
        """Clean text using Gemini (spelling/grammar).
        
        Args:
            text: Original text.
            
        Returns:
            Cleaned text, or None if error.
        """
        if self.gemini_client is None:
            try:
                import os
                import google.generativeai as genai
                
                api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
                if not api_key:
                    logger.warning("No Gemini API key found, skipping text cleaning")
                    return None
                
                genai.configure(api_key=api_key)
                self.gemini_client = genai.GenerativeModel("gemini-2.0-flash-lite")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
                return None
        
        try:
            prompt = (
                f"Fix spelling and grammar errors only. "
                f"Do not change meaning, tone, or technical content. "
                f"Return only the corrected text, no explanations.\n\n{text[:2000]}"
            )
            response = self.gemini_client.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini cleaning failed: {e}")
            return None

    def write_output(self, records: list[dict[str, Any]]) -> int:
        """Write cleaned records.
        
        Args:
            records: Cleaned records.
            
        Returns:
            Number of records written.
        """
        count = super().write_output(records)
        
        if self.duplicate_count > 0:
            logger.info(f"Removed {self.duplicate_count} duplicate records")
        
        return count


__all__ = ["CleaningStage"]
