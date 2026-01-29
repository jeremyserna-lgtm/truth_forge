"""Tests for BaseEnrichment (mocked BigQuery)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from typing import ClassVar

from pipelines.enrichment.base_enrichment import BaseEnrichment


class _ConcreteEnrichment(BaseEnrichment):
    """Minimal concrete implementation for testing."""

    ENRICHMENT_NAME: ClassVar[str] = "test"
    COLUMNS_OWNED: ClassVar[list[str]] = ["col_a", "col_b"]
    REQUIRES_EMBEDDING: ClassVar[bool] = False

    def compute_enrichment(self, text: str, existing_embedding: list[float] | None = None) -> dict:
        return {"col_a": 1, "col_b": "x"}


class TestBaseEnrichment:
    """Tests for BaseEnrichment."""

    @patch("pipelines.enrichment.base_enrichment.get_bigquery_client")
    def test_build_query_levels(self, mock_bq: MagicMock) -> None:
        """build_query includes level filter."""
        mock_bq.return_value = MagicMock()
        with patch.object(sys, "argv", ["prog", "--level", "5,8"]):
            en = _ConcreteEnrichment()
        q = en.build_query()
        assert "level IN (5, 8)" in q or "5, 8" in q
        assert "entity_unified" in q
        assert "entity_enrichments" in q

    @patch("pipelines.enrichment.base_enrichment.get_bigquery_client")
    def test_get_target_table_staging(self, mock_bq: MagicMock) -> None:
        """get_target_table uses staging by default."""
        mock_bq.return_value = MagicMock()
        with patch.object(sys, "argv", ["prog"]):
            en = _ConcreteEnrichment()
        t = en.get_target_table()
        assert "staging_entity_enrichments" in t

    @patch("pipelines.enrichment.base_enrichment.get_bigquery_client")
    def test_get_target_table_production(self, mock_bq: MagicMock) -> None:
        """get_target_table uses production when --production."""
        mock_bq.return_value = MagicMock()
        with patch.object(sys, "argv", ["prog", "--production"]):
            en = _ConcreteEnrichment()
        t = en.get_target_table()
        assert "entity_enrichments" in t
        assert "staging" not in t
