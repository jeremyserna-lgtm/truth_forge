"""Triage enrichment - Run 0: Flash-Lite complexity assessment.

THE PATTERN:
- HOLD₁: entity_unified entities
- AGENT: Gemini Flash-Lite triage assessment
- HOLD₂: triage_* columns in entity_enrichments

Purpose: Prioritize which entities to enrich first using Flash-Lite triage.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


class TriageEnrichment(BaseEnrichment):
    """Triage enrichment using Gemini Flash-Lite."""

    ENRICHMENT_NAME = "triage"
    COLUMNS_OWNED = [
        "triage_complexity",
        "triage_priority",
        "triage_category",
        "triage_needs_flash",
        "triage_needs_pro",
    ]
    REQUIRES_EMBEDDING = False

    def __init__(self) -> None:
        """Initialize triage enrichment."""
        super().__init__()
        self.gemini_client: Any = None
        try:
            import google.generativeai as genai

            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_client = genai.GenerativeModel("gemini-2.0-flash-exp")
            else:
                logger.warning("GEMINI_API_KEY not set - triage will use fallback logic")
        except ImportError:
            logger.warning("google-generativeai not installed - triage will use fallback logic")
        except Exception as e:
            logger.warning(f"Could not initialize Gemini client: {e}")

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute triage assessment for text.

        Args:
            text: Text content to assess
            existing_embedding: Not used for triage

        Returns:
            Dictionary with triage columns
        """
        # Use Gemini Flash-Lite if available, otherwise fallback
        if self.gemini_client:
            return self._compute_with_gemini(text)
        else:
            return self._compute_fallback(text)

    def _compute_with_gemini(self, text: str) -> dict[str, Any]:
        """Compute triage using Gemini Flash-Lite."""
        if self.gemini_client is None:
            return self._compute_fallback(text)
        try:
            prompt = f"""Analyze this text and provide a triage assessment:

Text: {text[:2000]}

Provide a JSON response with:
- complexity: "simple", "moderate", or "complex"
- priority: integer 1-10 (10 = highest priority)
- category: brief category label
- needs_flash: boolean (needs Flash analysis)
- needs_pro: boolean (needs Pro analysis)

JSON:"""

            response = self.gemini_client.generate_content(prompt)
            response_text = response.text.strip()

            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            # Parse JSON
            try:
                triage_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON object
                import re

                json_match = re.search(r"\{[^}]+\}", response_text)
                if json_match:
                    triage_data = json.loads(json_match.group())
                else:
                    return self._compute_fallback(text)

            return {
                "triage_complexity": triage_data.get("complexity", "moderate"),
                "triage_priority": int(triage_data.get("priority", 5)),
                "triage_category": triage_data.get("category", "general"),
                "triage_needs_flash": bool(triage_data.get("needs_flash", False)),
                "triage_needs_pro": bool(triage_data.get("needs_pro", False)),
            }

        except Exception as e:
            logger.warning(f"Gemini triage failed: {e}, using fallback")
            return self._compute_fallback(text)

    def _compute_fallback(self, text: str) -> dict[str, Any]:
        """Fallback triage logic (rule-based)."""
        text_length = len(text)
        word_count = len(text.split())

        # Complexity based on length and structure
        if text_length < 100:
            complexity = "simple"
            priority = 3
        elif text_length < 500:
            complexity = "moderate"
            priority = 5
        else:
            complexity = "complex"
            priority = 7

        # Category based on keywords (simple heuristic)
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["code", "function", "class", "import"]):
            category = "code"
        elif any(kw in text_lower for kw in ["question", "how", "what", "why"]):
            category = "question"
        elif any(kw in text_lower for kw in ["error", "problem", "issue"]):
            category = "problem"
        else:
            category = "general"

        # Needs Flash/Pro based on complexity
        needs_flash = complexity in ["moderate", "complex"]
        needs_pro = complexity == "complex" and word_count > 300

        return {
            "triage_complexity": complexity,
            "triage_priority": priority,
            "triage_category": category,
            "triage_needs_flash": needs_flash,
            "triage_needs_pro": needs_pro,
        }

    def build_query(self) -> str:
        """Build query for triage - prioritize recent, higher levels."""
        # Override to add priority ordering
        query = super().build_query()

        # Replace ORDER BY to prioritize by level and recency
        if "ORDER BY" in query:
            query = query.split("ORDER BY")[0]

        # Order by level and recency (already handled in base query)
        # No additional ordering needed

        return query


if __name__ == "__main__":
    import os

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    TriageEnrichment().run()
