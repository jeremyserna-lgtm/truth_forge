"""Unit tests for molt tracking."""

from pathlib import Path
from tempfile import TemporaryDirectory

from truth_forge.molt.engine import MoltResult
from truth_forge.molt.tracking import MoltRecord, MoltTracker


class TestMoltRecord:
    """Tests for MoltRecord dataclass."""

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        record = MoltRecord(
            timestamp="2026-01-26T10:00:00",
            source_name="test",
            source_path="/source",
            destination_path="/dest",
            archive_path="/archive",
            files_found=10,
            files_migrated=5,
            files_archived=5,
            stubs_created=5,
            skipped=5,
            errors=[],
            dry_run=False,
        )

        data = record.to_dict()

        assert data["timestamp"] == "2026-01-26T10:00:00"
        assert data["source_name"] == "test"
        assert data["files_found"] == 10
        assert data["dry_run"] is False

    def test_from_dict(self) -> None:
        """Test creation from dictionary."""
        data = {
            "timestamp": "2026-01-26T10:00:00",
            "source_name": "test",
            "source_path": "/source",
            "destination_path": "/dest",
            "archive_path": "/archive",
            "files_found": 10,
            "files_migrated": 5,
            "files_archived": 5,
            "stubs_created": 5,
            "skipped": 5,
            "errors": ["error1"],
            "dry_run": True,
        }

        record = MoltRecord.from_dict(data)

        assert record.timestamp == "2026-01-26T10:00:00"
        assert record.source_name == "test"
        assert record.files_found == 10
        assert record.errors == ["error1"]
        assert record.dry_run is True

    def test_roundtrip(self) -> None:
        """Test to_dict and from_dict are inverse operations."""
        original = MoltRecord(
            timestamp="2026-01-26T10:00:00",
            source_name="test",
            source_path="/source",
            destination_path="/dest",
            archive_path="/archive",
            files_found=10,
            files_migrated=5,
            files_archived=5,
            stubs_created=5,
            skipped=5,
            errors=["err1", "err2"],
            dry_run=False,
        )

        roundtripped = MoltRecord.from_dict(original.to_dict())

        assert roundtripped.timestamp == original.timestamp
        assert roundtripped.source_name == original.source_name
        assert roundtripped.files_found == original.files_found
        assert roundtripped.errors == original.errors


class TestMoltTracker:
    """Tests for MoltTracker class."""

    def test_record(self) -> None:
        """Test recording a molt operation."""
        with TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / ".molt" / "history.jsonl"
            tracker = MoltTracker(history_file)

            result = MoltResult(
                source_name="test",
                files_found=10,
                files_migrated=5,
                files_archived=5,
                stubs_created=5,
                skipped=5,
                errors=[],
            )

            record = tracker.record(
                result=result,
                source_path=Path("/source"),
                destination_path=Path("/dest"),
                archive_path=Path("/archive"),
                dry_run=False,
            )

            assert record.source_name == "test"
            assert record.files_found == 10
            assert record.dry_run is False

            # Verify file was created
            assert history_file.exists()

    def test_get_history(self) -> None:
        """Test retrieving history."""
        with TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / ".molt" / "history.jsonl"
            tracker = MoltTracker(history_file)

            # Record multiple operations
            for i in range(3):
                result = MoltResult(
                    source_name=f"source_{i}",
                    files_archived=i + 1,
                )
                tracker.record(
                    result=result,
                    source_path=Path(f"/source_{i}"),
                    destination_path=Path(f"/dest_{i}"),
                    archive_path=Path(f"/archive_{i}"),
                    dry_run=i % 2 == 0,
                )

            history = tracker.get_history()

            assert len(history) == 3
            assert history[0].source_name == "source_0"
            assert history[1].source_name == "source_1"
            assert history[2].source_name == "source_2"

    def test_get_history_empty(self) -> None:
        """Test getting history when none exists."""
        with TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / ".molt" / "history.jsonl"
            tracker = MoltTracker(history_file)

            history = tracker.get_history()

            assert history == []

    def test_get_source_history(self) -> None:
        """Test filtering history by source."""
        with TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / ".molt" / "history.jsonl"
            tracker = MoltTracker(history_file)

            # Record operations for different sources
            for source in ["source_a", "source_b", "source_a"]:
                result = MoltResult(source_name=source, files_archived=1)
                tracker.record(
                    result=result,
                    source_path=Path(f"/{source}"),
                    destination_path=Path("/dest"),
                    archive_path=Path("/archive"),
                    dry_run=False,
                )

            history_a = tracker.get_source_history("source_a")
            history_b = tracker.get_source_history("source_b")

            assert len(history_a) == 2
            assert len(history_b) == 1

    def test_get_summary(self) -> None:
        """Test getting summary statistics."""
        with TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / ".molt" / "history.jsonl"
            tracker = MoltTracker(history_file)

            # Record mix of dry runs and executions
            for i in range(4):
                result = MoltResult(
                    source_name=f"source_{i % 2}",
                    files_archived=10,
                    stubs_created=10,
                    errors=["err"] if i == 0 else [],
                )
                tracker.record(
                    result=result,
                    source_path=Path(f"/source_{i}"),
                    destination_path=Path("/dest"),
                    archive_path=Path("/archive"),
                    dry_run=i % 2 == 0,
                )

            summary = tracker.get_summary()

            assert summary["total_operations"] == 4
            assert summary["executed_operations"] == 2
            assert summary["dry_runs"] == 2
            assert summary["total_files_archived"] == 20  # 2 executed * 10 files
            assert summary["total_stubs_created"] == 20
            assert summary["total_errors"] == 0  # dry run errors don't count
