"""BigQuery configuration for spine dataset.

THE PATTERN:
- HOLD₁: Configuration values
- AGENT: BigQuery client initialization
- HOLD₂: Configured client ready for queries
"""

from __future__ import annotations

import os
from typing import Any

# BigQuery project and dataset
BQ_PROJECT_ID = os.getenv("BQ_PROJECT_ID", "flash-clover-464719-g1")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID", "spine")

# Primary table names
ENTITY_TABLE = "entity_production"  # Main entity table
DOCUMENT_TABLE = "document"  # Document metadata
RELATIONSHIP_TABLE = "entity_relationship"  # Entity relationships

# Data source identifiers
DATA_SOURCES = {
    "claude_code": "Claude code generation and analysis",
    "claude_web": "Claude web browsing and research",
    "gemini_web": "Gemini web search and content analysis",
    "codex": "Codex AI code generation",
    "cursor": "Cursor IDE interactions",
}

# Spine levels (L1-L12)
SPINE_LEVELS = {
    1: "Token",
    2: "Word",
    3: "Span",
    4: "Sentence",
    5: "Message",
    6: "Turn",
    7: "Topic Segment",
    8: "Document",
    9: "Domain",
    10: "Context",
    11: "Phase",
    12: "Identity",
}

# Query defaults
DEFAULT_LIMIT = 100
MAX_LIMIT = 1000
DEFAULT_TIMEOUT = 30  # seconds


def get_bigquery_client() -> Any:
    """Get configured BigQuery client.

    Returns:
        BigQuery client instance.
    """
    from google.cloud import bigquery

    return bigquery.Client(project=BQ_PROJECT_ID)
