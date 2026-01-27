"""Fine-grained identity linkage - Populate span_id, word_id for L2-L4 entities.

THE PATTERN:
- HOLD₁: entity_unified entities (L2-L4) with parent relationships
- AGENT: Fine-grained linkage derivation
- HOLD₂: span_id, word_id columns

Purpose: Enable span/word-level analytics and fine-grained identity tracking.
"""

from __future__ import annotations

import logging
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


class FineGrainedEnrichment(BaseEnrichment):
    """Fine-grained identity linkage enrichment."""

    ENRICHMENT_NAME = "fine_grained"
    COLUMNS_OWNED = [
        "span_id",
        "word_id",
        "fine_grained_version",
    ]
    REQUIRES_EMBEDDING = False

    def __init__(self) -> None:
        """Initialize fine-grained enrichment."""
        super().__init__()

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute fine-grained linkage (not used - will use row context).

        Args:
            text: Not used
            existing_embedding: Not used

        Returns:
            Dictionary with span_id, word_id
        """
        # Will be populated from row context in run()
        return {
            "span_id": None,
            "word_id": None,
            "fine_grained_version": "1.0.0",
        }

    def compute_enrichment_from_row(self, row: Any, text: str) -> dict[str, Any]:
        """Compute fine-grained linkage from row context.

        Args:
            row: BigQuery row with level, parent_id, hierarchy
            text: Not used

        Returns:
            Dictionary with span_id, word_id
        """
        level = row.level if hasattr(row, "level") else row.get("level")
        parent_id = row.parent_id if hasattr(row, "parent_id") else row.get("parent_id")

        span_id = None
        word_id = None

        # For L4 (sentence), link to L3 (span) parent
        if level == 4:
            span_id = parent_id  # parent is L3 span

        # For L3 (span), link to L2 (word) parent
        elif level == 3:
            word_id = parent_id  # parent is L2 word

        # For L2 (word), no fine-grained linkage needed
        # (word is already the finest grain)

        return {
            "span_id": span_id,
            "word_id": word_id,
            "fine_grained_version": "1.0.0",
        }

    def run(self) -> None:
        """Override run to use full row context."""
        from pipelines.enrichment.utils import format_progress

        # Only process L2-L4
        query = self.build_query()
        # Ensure we only get L2-L4
        if "WHERE" in query:
            query = query.replace(
                "WHERE",
                "WHERE e.level IN (2, 3, 4) AND",
                1,
            )
        else:
            query += " AND e.level IN (2, 3, 4)"

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

    FineGrainedEnrichment().run()
