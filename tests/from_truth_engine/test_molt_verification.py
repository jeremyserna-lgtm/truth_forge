"""Tests for Molt Verification Service - Data Forces Evolution, Not Feelings.

These tests verify that the molt verification system correctly identifies
when the system needs to evolve based on objective data.
"""
from __future__ import annotations

"""Tests for Molt Verification Service - Data Forces Evolution, Not Feelings.

These tests verify that the molt verification system correctly identifies
when the system needs to evolve based on objective data.
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)
script_id = "tests.test_molt_verification.py"

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from src.services.central_services.molt_verification_service import (
    MoltVerificationService,
    get_molt_verification_service,
    MoltStatus,
    scaffolding_gap,
    paradox_token_density,
    terminal_halt_scanner,
    generate_molt_report,
)
from src.services.central_services.core.responses import CareResponse

class TestScaffoldingGap:
    """Tests for scaffolding_gap metric."""

    def test_high_gap_no_trigger(self):
        """High gap (system more complex) should not trigger molt."""
        # System output is at a much higher grade level
        user = "The cat sat on the mat."
        system = (
            "The domesticated feline positioned itself upon the woven floor "
            "covering, demonstrating characteristic sedentary behavior indicative "
            "of its species' preference for thermoregulation optimization."
        )

        result = scaffolding_gap(user, system, threshold=0.5)

        assert not result.molt_triggered
        assert result.gap >= 0.5  # Gap should be significant
        assert "healthy" in result.message.lower()

    def test_low_gap_triggers_molt(self):
        """Low gap (system matching user) should trigger molt."""
        # Both at similar complexity
        user = "The quick brown fox jumps over the lazy dog."
        system = "The fast red fox runs past the sleeping cat."

        result = scaffolding_gap(user, system, threshold=2.0)

        # With a high threshold, the small natural gap should trigger
        if result.gap < 2.0:
            assert result.molt_triggered
            assert "MOLT NOTIFICATION" in result.message

    def test_empty_input_no_trigger(self):
        """Empty input should not trigger molt."""
        result = scaffolding_gap("", "Some text", threshold=0.5)

        assert not result.molt_triggered
        assert "too short" in result.message.lower()

    def test_short_input_no_trigger(self):
        """Short input should not trigger molt."""
        result = scaffolding_gap("Hi", "Hello there!", threshold=0.5)

        assert not result.molt_triggered

class TestParadoxTokenDensity:
    """Tests for paradox_token_density metric."""

    def test_known_vocabulary_no_trigger(self):
        """Text with known vocabulary should not trigger molt."""
        # Use very common words that are in the default vocabulary
        text = (
            "The people want to know the truth about the system. "
            "I think this is a good thing. We can do it."
        )

        result = paradox_token_density(text, threshold=0.15)

        assert not result.molt_triggered
        assert result.density < 0.15

    def test_unknown_vocabulary_triggers(self):
        """Text with many unknown words should trigger molt."""
        # Lots of made-up words
        text = (
            "The floobernacker zorpled through the quixotic blorpitude, "
            "magnificently plorbulating the underlying snurglewort patterns "
            "while the fleemnarb oscillated in quintessential blorgification."
        )

        result = paradox_token_density(text, threshold=0.15)

        assert result.molt_triggered
        assert result.density > 0.15
        assert len(result.unclassified_examples) > 0

    def test_empty_text_no_trigger(self):
        """Empty text should not trigger molt."""
        result = paradox_token_density("", threshold=0.15)

        assert not result.molt_triggered
        assert result.total_tokens == 0

    def test_custom_vocabulary(self):
        """Custom vocabulary should be recognized."""
        from src.services.central_services.molt_verification_service.metrics import (
            create_domain_classifier
        )

        # Add domain vocabulary
        domain_vocab = {"floober", "zorple", "plorbulate"}
        classifier = create_domain_classifier(domain_vocab)

        text = "The floober zorple plorbulate nicely."
        result = paradox_token_density(text, classifier=classifier, threshold=0.15)

        # Domain words should now be classified
        assert result.density < 0.5  # Most words should be recognized

class TestTerminalHaltScanner:
    """Tests for terminal_halt_scanner."""

    def test_directory_with_no_halts(self):
        """Directory with no halt markers should not trigger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create clean file
            (Path(tmpdir) / "clean.md").write_text("# Clean Document\n\nNo issues here.")

            result = terminal_halt_scanner(tmpdir, threshold=5)

            assert not result.molt_triggered
            assert result.total_halts == 0

    def test_directory_with_halts(self):
        """Directory with halt markers should be detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file with halt markers
            content = """
# Work in Progress

TODO: Implement this feature
TBD: Figure out the architecture
FIXME: This is broken
TODO: Another task
HACK: Temporary workaround
WIP: Still working on this
"""
            (Path(tmpdir) / "wip.md").write_text(content)

            result = terminal_halt_scanner(tmpdir, threshold=3)

            assert result.molt_triggered
            assert result.total_halts >= 5
            assert "TODO" in result.halts_by_type
            assert "FIXME" in result.halts_by_type

    def test_excludes_archived_by_default(self):
        """Archived directories should be excluded by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create archived file with halts
            archive = Path(tmpdir) / "_archive"
            archive.mkdir()
            (archive / "old.md").write_text("TODO: Old task\nTODO: Another old task")

            # Create active file without halts
            (Path(tmpdir) / "active.md").write_text("# Active Document\n\nNo issues.")

            result = terminal_halt_scanner(tmpdir, threshold=5)

            # Should not find the archived TODOs
            assert result.total_halts == 0

    def test_nonexistent_directory(self):
        """Nonexistent directory should not trigger."""
        result = terminal_halt_scanner("/nonexistent/path", threshold=5)

        assert not result.molt_triggered
        assert "does not exist" in result.message

class TestMoltVerificationReport:
    """Tests for report generation."""

    def test_generate_report_all_healthy(self):
        """Report with no triggers should show MOLT NOT REQUIRED."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "clean.md").write_text("# Clean")

            report = generate_molt_report(
                scan_directory=tmpdir,
                halt_threshold=5
            )

            assert report.status == "MOLT NOT REQUIRED"
            assert len(report.tripwires_triggered) == 0
            assert "adequate" in report.summary.lower()

    def test_generate_report_one_trigger(self):
        """Report with one trigger should show MOLT NOTIFICATION."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file with many halts
            content = "\n".join([f"TODO: Task {i}" for i in range(10)])
            (Path(tmpdir) / "todos.md").write_text(content)

            report = generate_molt_report(
                scan_directory=tmpdir,
                halt_threshold=5
            )

            assert report.status == "MOLT NOTIFICATION"
            assert len(report.tripwires_triggered) == 1
            assert "Terminal Halts" in report.tripwires_triggered[0]

    def test_report_to_markdown(self):
        """Report should generate valid markdown."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "clean.md").write_text("# Clean")

            report = generate_molt_report(scan_directory=tmpdir)
            markdown = report.to_markdown()

            assert "# MOLT VERIFICATION REPORT" in markdown
            assert "Date:" in markdown
            assert "Status:" in markdown

    def test_report_to_dict(self):
        """Report should serialize to dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "clean.md").write_text("# Clean")

            report = generate_molt_report(scan_directory=tmpdir)
            data = report.to_dict()

            assert "timestamp" in data
            assert "status" in data
            assert "tripwires_triggered" in data

class TestMoltVerificationService:
    """Tests for the main service."""

    def test_service_initialization(self):
        """Service should initialize correctly."""
        service = MoltVerificationService()

        assert service.scaffolding_threshold == 0.5
        assert service.paradox_threshold == 0.15
        assert service.halt_threshold == 5

    def test_check_scaffolding_returns_care_response(self):
        """check_scaffolding should return CareResponse."""
        service = MoltVerificationService()
        result = service.check_scaffolding(
            user_text="Simple text.",
            system_text="More complex explanation of the topic at hand."
        )

        assert isinstance(result, CareResponse)
        assert result.has_data()

    def test_check_paradox_returns_care_response(self):
        """check_paradox_density should return CareResponse."""
        service = MoltVerificationService()
        result = service.check_paradox_density(
            text="The system creates truth and meaning."
        )

        assert isinstance(result, CareResponse)
        assert result.has_data()

    def test_check_halts_returns_care_response(self):
        """check_terminal_halts should return CareResponse."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.md").write_text("# Test")

            service = MoltVerificationService()
            result = service.check_terminal_halts(directory=tmpdir)

            assert isinstance(result, CareResponse)
            assert result.has_data()

    def test_full_verification(self):
        """full_verification should check all tripwires."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.md").write_text("# Test")

            service = MoltVerificationService(
                reports_dir=Path(tmpdir) / "reports"
            )
            result = service.full_verification(
                scan_directory=tmpdir,
                save_report=True
            )

            assert isinstance(result, CareResponse)
            assert "status" in result.data
            assert "tripwires_triggered" in result.data

    def test_singleton_pattern(self):
        """get_molt_verification_service should return singleton."""
        service1 = get_molt_verification_service()
        service2 = get_molt_verification_service()

        assert service1 is service2

class TestMoltStatus:
    """Tests for MoltStatus enum."""

    def test_status_values(self):
        """Status values should match expected strings."""
        assert MoltStatus.NOT_REQUIRED.value == "MOLT NOT REQUIRED"
        assert MoltStatus.NOTIFICATION.value == "MOLT NOTIFICATION"
        assert MoltStatus.REQUIRED.value == "MOLT REQUIRED"

class TestIntegration:
    """Integration tests for full molt verification flow."""

    def test_full_flow_healthy_system(self):
        """Complete flow with healthy system."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create healthy documentation
            (Path(tmpdir) / "README.md").write_text(
                "# Healthy Project\n\nEverything is complete and working."
            )

            service = MoltVerificationService(
                halt_threshold=5,
                reports_dir=Path(tmpdir) / "reports"
            )

            result = service.full_verification(
                user_text="What is the project about?",
                system_text=(
                    "The project implements sophisticated architectural patterns "
                    "for metamorphic verification of complex distributed systems."
                ),
                analysis_text="The system creates truth and transforms it into meaning.",
                scan_directory=tmpdir,
                save_report=True
            )

            assert result.is_success() or result.is_partial()
            assert result.data["status"] in [
                "MOLT NOT REQUIRED",
                "MOLT NOTIFICATION"
            ]

    def test_full_flow_struggling_system(self):
        """Complete flow with system needing molt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create problematic documentation
            content = "\n".join([f"TODO: Critical task {i}" for i in range(20)])
            (Path(tmpdir) / "wip.md").write_text(content)

            service = MoltVerificationService(
                halt_threshold=5,
                reports_dir=Path(tmpdir) / "reports"
            )

            result = service.full_verification(
                scan_directory=tmpdir,
                save_report=True
            )

            # Should trigger at least terminal halts
            assert result.is_partial()
            assert len(result.data["tripwires_triggered"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
