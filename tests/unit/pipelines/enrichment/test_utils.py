"""Tests for enrichment utils."""

from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from pipelines.enrichment.utils import format_progress


class TestFormatProgress:
    """Tests for format_progress."""

    def test_basic(self) -> None:
        """Progress string includes current, total, and percentage."""
        s = format_progress(50, 100)
        assert "50" in s
        assert "100" in s
        assert "50.0" in s

    def test_prefix(self) -> None:
        """Prefix is prepended when given."""
        s = format_progress(1, 10, prefix="Progress: ")
        assert s.startswith("Progress: ")

    def test_zero_total(self) -> None:
        """Zero total does not divide by zero."""
        s = format_progress(0, 0)
        assert "0" in s
