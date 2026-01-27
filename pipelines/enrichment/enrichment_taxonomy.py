"""Taxonomy enrichment - Populate category, domain, content_type fields.

THE PATTERN:
- HOLD₁: entity_unified entities with metadata/source_platform
- AGENT: Taxonomy derivation (rule-based + optional LLM)
- HOLD₂: primary_category, category_path, content_type, domain columns

Purpose: Enable category/domain-based analysis and filtering.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


class TaxonomyEnrichment(BaseEnrichment):
    """Taxonomy and domain enrichment."""

    ENRICHMENT_NAME = "taxonomy"
    COLUMNS_OWNED = [
        "primary_category",
        "category_path",
        "content_type",
        "domain",
        "taxonomy_version",
    ]
    REQUIRES_EMBEDDING = False

    # Domain mapping from source_platform
    DOMAIN_MAP = {
        "claude_code": "code",
        "claude_web": "web",
        "gemini_web": "web",
        "codex": "code",
        "cursor": "code",
        "chatgpt_web": "web",
        "browser_history": "web",
    }

    # Content type mapping from entity_type
    CONTENT_TYPE_MAP = {
        "conversation": "conversation",
        "message": "message",
        "sentence": "sentence",
        "document": "document",
        "website": "website",
        "sms": "message",
    }

    def __init__(self) -> None:
        """Initialize taxonomy enrichment."""
        super().__init__()

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute taxonomy for entity.

        Args:
            text: Text content (used for category detection)
            existing_embedding: Not used for taxonomy

        Returns:
            Dictionary with taxonomy columns
        """
        # This method will be called with row context, but we need source_platform and entity_type
        # For now, return None - will be populated in run() method with full row context
        return {
            "primary_category": None,
            "category_path": None,
            "content_type": None,
            "domain": None,
            "taxonomy_version": "1.0.0",
        }

    def compute_enrichment_from_row(self, row: Any, text: str) -> dict[str, Any]:
        """Compute taxonomy from full row context.

        Args:
            row: BigQuery row with source_platform, entity_type, metadata
            text: Text content

        Returns:
            Dictionary with taxonomy columns
        """
        # Derive domain from source_platform
        source_platform = (
            row.source_platform if hasattr(row, "source_platform") else row.get("source_platform")
        )
        domain = self.DOMAIN_MAP.get(source_platform, "general") if source_platform else None

        # Derive content_type from entity_type
        entity_type = row.entity_type if hasattr(row, "entity_type") else row.get("entity_type")
        content_type = None
        if entity_type:
            # Extract base type (e.g., "conversation:structural" -> "conversation")
            base_type = entity_type.split(":")[0] if ":" in entity_type else entity_type
            content_type = self.CONTENT_TYPE_MAP.get(base_type, base_type)

        # Derive category from metadata or text analysis
        metadata = row.metadata if hasattr(row, "metadata") else row.get("metadata")
        primary_category = None
        category_path = None

        if metadata:
            # Try to extract from metadata JSON
            try:
                if isinstance(metadata, str):
                    metadata_dict = json.loads(metadata)
                else:
                    metadata_dict = metadata

                primary_category = metadata_dict.get("category") or metadata_dict.get(
                    "primary_category"
                )
                category_path = metadata_dict.get("category_path")

            except (json.JSONDecodeError, AttributeError):
                pass

        # If no category from metadata, derive from text/keywords (simple heuristic)
        if not primary_category:
            text_lower = text.lower() if text else ""
            if any(kw in text_lower for kw in ["code", "function", "class", "import", "def"]):
                primary_category = "technology"
                category_path = "technology/code"
            elif any(kw in text_lower for kw in ["question", "how", "what", "why", "help"]):
                primary_category = "question"
                category_path = "communication/question"
            elif any(kw in text_lower for kw in ["error", "problem", "issue", "bug"]):
                primary_category = "problem"
                category_path = "problem/technical"
            else:
                primary_category = "general"
                category_path = "general"

        return {
            "primary_category": primary_category,
            "category_path": category_path,
            "content_type": content_type,
            "domain": domain,
            "taxonomy_version": "1.0.0",
        }

    def run(self) -> None:
        """Override run to use full row context."""
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
    from pipelines.enrichment.utils import format_progress

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    TaxonomyEnrichment().run()
