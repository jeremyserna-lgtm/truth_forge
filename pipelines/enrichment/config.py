"""Enrichment pipeline configuration.

THE PATTERN:
- HOLD₁: Configuration values
- AGENT: BigQuery client initialization
- HOLD₂: Configured client ready for enrichment
"""

from __future__ import annotations

import os
from typing import Any


# BigQuery project and dataset
BQ_PROJECT_ID = os.getenv("BQ_PROJECT_ID", "flash-clover-464719-g1")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID", "spine")

# Table names
ENTITY_UNIFIED_TABLE = "entity_unified"  # Source table (read-only for enrichments)
ENRICHMENTS_TABLE = "entity_enrichments"  # Production enrichments table
STAGING_ENRICHMENTS_TABLE = "staging_entity_enrichments"  # Staging table

# Enrichment groups
ENRICHMENT_GROUPS = {
    "A": ["textblob", "textstat"],  # CPU-only
    "B": ["goemotions", "roberta_hate"],  # Classification models
    "C": ["keybert", "bertopic"],  # Embedding-based
}

# Default batch sizes
DEFAULT_BATCH_SIZE = 1000
DEFAULT_WRITE_BATCH_SIZE = 500

# Minimum text length for enrichment
MIN_TEXT_LENGTH = 10


def get_bigquery_client() -> Any:
    """Get configured BigQuery client.

    Returns:
        BigQuery client instance.
    """
    from google.cloud import bigquery

    return bigquery.Client(project=BQ_PROJECT_ID)
