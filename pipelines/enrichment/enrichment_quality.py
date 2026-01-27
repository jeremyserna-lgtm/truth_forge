"""Quality flags enrichment - Set quality flags and enrichment metadata.

THE PATTERN:
- HOLD₁: entity_enrichments rows with enrichment data
- AGENT: Quality assessment
- HOLD₂: enrichment_quality_flags, enrichment_metadata columns

Purpose: Enable quality filtering, debugging, and enrichment lineage tracking.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


class QualityEnrichment(BaseEnrichment):
    """Quality flags and metadata enrichment."""

    ENRICHMENT_NAME = "quality"
    COLUMNS_OWNED = [
        "enrichment_quality_flags",
        "enrichment_metadata",
        "quality_version",
    ]
    REQUIRES_EMBEDDING = False

    def __init__(self) -> None:
        """Initialize quality enrichment."""
        super().__init__()

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute quality flags (not used - will use row context).

        Args:
            text: Not used directly
            existing_embedding: Not used

        Returns:
            Dictionary with quality flags
        """
        # Will be computed from row context in run()
        return {
            "enrichment_quality_flags": None,
            "enrichment_metadata": None,
            "quality_version": "1.0.0",
        }

    def compute_enrichment_from_row(self, row: Any, text: str) -> dict[str, Any]:
        """Compute quality flags from full enrichment row.

        Args:
            row: BigQuery row with all enrichment columns
            text: Text content

        Returns:
            Dictionary with quality flags and metadata
        """
        flags = []
        metadata = {}

        # Check for missing required enrichments
        required_enrichments = [
            "textblob_polarity",
            "textstat_flesch_reading_ease",
            "sentence_embedding",
        ]

        missing: list[str] = []
        for req in required_enrichments:
            value = getattr(row, req, None) if hasattr(row, req) else row.get(req)
            if value is None:
                missing.append(req)

        if missing:
            flags.append("missing_required")
            metadata["missing_enrichments"] = missing

        # Check for low confidence scores
        if hasattr(row, "textblob_polarity") and row.textblob_polarity is not None:
            if abs(row.textblob_polarity) < 0.1:
                flags.append("low_sentiment_confidence")

        if (
            hasattr(row, "bertopic_topic_probability")
            and row.bertopic_topic_probability is not None
        ):
            if row.bertopic_topic_probability < 0.3:
                flags.append("low_topic_confidence")

        # Check for anomalies
        if text:
            text_length = len(text)
            if text_length > 100000:
                flags.append("very_long_text")
                metadata["text_length"] = text_length
            elif text_length < 10:
                flags.append("very_short_text")
                metadata["text_length"] = text_length

            # Check for unusual character patterns
            if text.count("\x00") > 0:
                flags.append("null_bytes_detected")

        # Add processing metadata
        metadata["processed_at"] = datetime.utcnow().isoformat()
        metadata["processing_version"] = "1.0.0"

        return {
            "enrichment_quality_flags": flags if flags else None,
            "enrichment_metadata": json.dumps(metadata) if metadata else None,
            "quality_version": "1.0.0",
        }

    def run(self) -> None:
        """Override run to query enrichments table and assess quality."""
        from pipelines.enrichment.config import BQ_DATASET_ID, BQ_PROJECT_ID, ENRICHMENTS_TABLE
        from pipelines.enrichment.utils import format_progress

        # Query enrichments table (not entity_unified)
        query = f"""
        SELECT 
            e.entity_id,
            e.text,
            e.textblob_polarity,
            e.textblob_subjectivity,
            e.textstat_flesch_reading_ease,
            e.sentence_embedding,
            e.bertopic_topic_probability,
            e.enrichment_quality_flags,
            e.enrichment_metadata
        FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}` e
        WHERE 1=1
        """

        # Mode-specific filter
        if self.args.mode == "null-only":
            query += " AND (e.enrichment_quality_flags IS NULL OR e.enrichment_metadata IS NULL)"

        # Source filter
        if self.args.source:
            query += f" AND e.source_platform = '{self.args.source}'"

        # Limit
        if self.args.limit > 0:
            query += f" LIMIT {self.args.limit}"

        if self.args.dry_run:
            print(f"DRY RUN - Would execute:\n{query}\n")
            count_query = query.replace("SELECT e.entity_id,", "SELECT COUNT(*) as count,").split(
                "LIMIT"
            )[0]
            try:
                result = list(self.client.query(count_query).result())
                if result:
                    count = result[0].count if hasattr(result[0], "count") else result[0][0]
                    print(f"Would process {count:,} entities")
            except Exception as e:
                print(f"Error counting entities: {e}")
            return

        logger.info(f"Querying enrichments for {self.ENRICHMENT_NAME}...")
        try:
            query_job = self.client.query(query)
            results = list(query_job.result())
            logger.info(f"Found {len(results):,} entities to assess")
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

    QualityEnrichment().run()
