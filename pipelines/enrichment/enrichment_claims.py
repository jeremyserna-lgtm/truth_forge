"""Claims detection enrichment - Detect factual claims and set Q&A roles.

THE PATTERN:
- HOLD₁: entity_unified entities
- AGENT: Claim detection (LLM or classifier) + Q&A role derivation
- HOLD₂: is_claim, claim_type, qa_role columns

Purpose: Enable claim-centric analysis and Q&A role-based filtering.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


class ClaimsEnrichment(BaseEnrichment):
    """Claims detection and Q&A role enrichment."""

    ENRICHMENT_NAME = "claims"
    COLUMNS_OWNED = [
        "is_claim",
        "claim_type",
        "qa_role",
        "claims_version",
    ]
    REQUIRES_EMBEDDING = False

    def __init__(self) -> None:
        """Initialize claims enrichment."""
        super().__init__()
        self.gemini_client: Any = None
        try:
            import google.generativeai as genai

            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_client = genai.GenerativeModel("gemini-2.0-flash-exp")
        except ImportError:
            logger.warning("google-generativeai not installed - using rule-based claim detection")
        except Exception as e:
            logger.warning(f"Could not initialize Gemini client: {e}")

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute claims detection for text.

        Args:
            text: Text content to analyze
            existing_embedding: Not used for claims

        Returns:
            Dictionary with is_claim, claim_type, qa_role
        """
        # Q&A role will be set from row context in run() method
        # For now, detect claims
        is_claim, claim_type = self._detect_claim(text)

        return {
            "is_claim": is_claim,
            "claim_type": claim_type,
            "qa_role": None,  # Will be set from row context
            "claims_version": "1.0.0",
        }

    def _detect_claim(self, text: str) -> tuple[bool, str | None]:
        """Detect if text contains a factual claim.

        Args:
            text: Text to analyze

        Returns:
            Tuple of (is_claim: bool, claim_type: str | None)
        """
        # Rule-based detection (simple heuristics)
        text_lower = text.lower()

        # Claim indicators
        claim_indicators = [
            "is ",
            "are ",
            "was ",
            "were ",
            "has ",
            "have ",
            "will ",
            "can ",
            "cannot ",
            "does ",
            "doesn't ",
            "did ",
            "didn't ",
            "according to",
            "research shows",
            "studies show",
            "data shows",
            "evidence suggests",
        ]

        # Opinion indicators (not claims)
        opinion_indicators = [
            "i think",
            "i believe",
            "i feel",
            "in my opinion",
            "i guess",
            "maybe",
            "perhaps",
            "might",
        ]

        # Check for claim indicators
        has_claim_indicators = any(indicator in text_lower for indicator in claim_indicators)
        has_opinion_indicators = any(indicator in text_lower for indicator in opinion_indicators)

        if has_opinion_indicators and not has_claim_indicators:
            return False, None

        if has_claim_indicators:
            # Determine claim type
            if any(kw in text_lower for kw in ["will", "going to", "future", "predict"]):
                claim_type = "prediction"
            elif any(kw in text_lower for kw in ["should", "must", "ought", "need to"]):
                claim_type = "prescriptive"
            elif any(kw in text_lower for kw in ["is", "are", "was", "were"]):
                claim_type = "factual"
            else:
                claim_type = "factual"

            return True, claim_type

        # Use LLM if available for better detection
        if self.gemini_client:
            return self._detect_claim_with_llm(text)

        return False, None

    def _detect_claim_with_llm(self, text: str) -> tuple[bool, str | None]:
        """Detect claim using LLM (Gemini Flash)."""
        if self.gemini_client is None:
            return False, None
        try:
            prompt = f"""Analyze this text and determine if it contains a factual claim.

Text: {text[:1000]}

Respond with JSON:
{{
  "is_claim": true/false,
  "claim_type": "factual" | "opinion" | "prediction" | null
}}"""

            response = self.gemini_client.generate_content(prompt)
            response_text = response.text.strip()

            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            try:
                result = json.loads(response_text)
                return (
                    bool(result.get("is_claim", False)),
                    result.get("claim_type"),
                )
            except json.JSONDecodeError:
                return False, None

        except Exception as e:
            logger.warning(f"LLM claim detection failed: {e}")
            return False, None

    def compute_enrichment_from_row(self, row: Any, text: str) -> dict[str, Any]:
        """Compute claims and Q&A role from full row context.

        Args:
            row: BigQuery row with metadata, conversation structure
            text: Text content

        Returns:
            Dictionary with claims columns
        """
        # Detect claim
        is_claim, claim_type = self._detect_claim(text)

        # Derive Q&A role from metadata or conversation structure
        metadata = row.metadata if hasattr(row, "metadata") else row.get("metadata")
        qa_role = None

        if metadata:
            try:
                if isinstance(metadata, str):
                    metadata_dict = json.loads(metadata)
                else:
                    metadata_dict = metadata

                qa_role = metadata_dict.get("role") or metadata_dict.get("qa_role")

            except (json.JSONDecodeError, AttributeError):
                pass

        # Rule-based Q&A role detection
        if not qa_role:
            text_lower = text.lower()
            if any(kw in text_lower for kw in ["user:", "human:", "person:"]):
                qa_role = "user"
            elif any(kw in text_lower for kw in ["assistant:", "ai:", "bot:"]):
                qa_role = "assistant"
            elif any(kw in text_lower for kw in ["system:", "admin:"]):
                qa_role = "system"
            # Default based on text characteristics
            elif text_lower.startswith(("i ", "my ", "we ", "our ")):
                qa_role = "user"
            else:
                qa_role = "assistant"  # Default

        return {
            "is_claim": is_claim,
            "claim_type": claim_type,
            "qa_role": qa_role,
            "claims_version": "1.0.0",
        }

    def run(self) -> None:
        """Override run to use full row context."""
        from pipelines.enrichment.utils import format_progress

        query = self.build_query()

        if self.args.dry_run:
            print(f"DRY RUN - Would execute:\n{query}\n")
            count_query = query.replace(
                "SELECT " + query.split("SELECT ")[1].split(" FROM")[0],
                "SELECT COUNT(*) as count",
                1,
            )
            try:
                result = list(self.client.query(count_query).result())
                if result:
                    count = result[0].count if hasattr(result[0], "count") else result[0][0]
                    print(f"Would process {count:,} entities")
            except Exception as e:
                print(f"Error counting entities: {e}")
            return

        logger.info(f"Querying entities for {self.ENRICHMENT_NAME}...")
        try:
            query_job = self.client.query(query)
            results = list(query_job.result())
            logger.info(f"Found {len(results):,} entities to enrich")
        except Exception as e:
            logger.error(f"Error querying entities: {e}", exc_info=True)
            return

        if not results:
            logger.info("Nothing to process.")
            return

        # Process in batches
        enriched = []
        total = len(results)

        for i, row in enumerate(results):
            try:
                text = row.text if hasattr(row, "text") else row.get("text", "")
                if not text:
                    continue

                result = self.compute_enrichment_from_row(row, text)
                result["entity_id"] = (
                    row.entity_id if hasattr(row, "entity_id") else row.get("entity_id")
                )
                enriched.append(result)

                # Write batch when full
                if len(enriched) >= self.args.write_batch_size:
                    written = self.write_batch(enriched)
                    logger.info(f"Wrote batch: {written} rows ({format_progress(i + 1, total)})")
                    enriched = []

                if self.args.progress and (i + 1) % 100 == 0:
                    logger.info(format_progress(i + 1, total, "Progress: "))

            except Exception as e:
                entity_id = row.entity_id if hasattr(row, "entity_id") else "unknown"
                logger.error(f"Error processing entity {entity_id}: {e}", exc_info=True)
                continue

        # Write remaining
        if enriched:
            written = self.write_batch(enriched)
            logger.info(f"Wrote final batch: {written} rows")

        logger.info(f"Enrichment complete: {total:,} entities processed for {self.ENRICHMENT_NAME}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    ClaimsEnrichment().run()
