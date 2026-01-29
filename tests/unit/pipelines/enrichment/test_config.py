"""Tests for enrichment config."""

from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from pipelines.enrichment import config


class TestEnrichmentConfig:
    """Tests for config module."""

    def test_constants(self) -> None:
        """Config constants are set."""
        assert config.BQ_PROJECT_ID
        assert config.BQ_DATASET_ID == "spine"
        assert config.ENTITY_UNIFIED_TABLE == "entity_unified"
        assert config.ENRICHMENTS_TABLE == "entity_enrichments"
        assert config.STAGING_ENRICHMENTS_TABLE == "staging_entity_enrichments"

    def test_get_bigquery_client(self) -> None:
        """get_bigquery_client returns a client."""
        client = config.get_bigquery_client()
        assert client is not None
        assert client.project == config.BQ_PROJECT_ID
