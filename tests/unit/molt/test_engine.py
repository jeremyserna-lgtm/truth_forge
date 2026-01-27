"""Unit tests for molt engine."""

from pathlib import Path
from tempfile import TemporaryDirectory

from truth_forge.molt.config import MoltConfig, SourceMapping
from truth_forge.molt.engine import MoltEngine, MoltResult


class TestMoltResult:
    """Tests for MoltResult dataclass."""

    def test_success_when_all_archived(self) -> None:
        """Test success property when all files archived."""
        result = MoltResult(
            source_name="test",
            files_found=10,
            files_migrated=5,
            files_archived=5,
            stubs_created=5,
            skipped=5,
            errors=[],
        )
        assert result.success is True

    def test_failure_when_errors(self) -> None:
        """Test success is False when errors present."""
        result = MoltResult(
            source_name="test",
            files_found=10,
            files_migrated=5,
            files_archived=5,
            stubs_created=5,
            skipped=5,
            errors=["Something went wrong"],
        )
        assert result.success is False

    def test_failure_when_incomplete(self) -> None:
        """Test success is False when not all migrated files archived."""
        result = MoltResult(
            source_name="test",
            files_found=10,
            files_migrated=5,
            files_archived=3,  # Less than migrated
            stubs_created=3,
            skipped=5,
            errors=[],
        )
        assert result.success is False


class TestMoltEngine:
    """Tests for MoltEngine class."""

    def _create_config(self, tmpdir: Path) -> MoltConfig:
        """Create test configuration.

        Args:
            tmpdir: Temporary directory.

        Returns:
            MoltConfig instance.
        """
        source = tmpdir / "source"
        dest = tmpdir / "dest"
        archive = tmpdir / "archive"

        source.mkdir()
        dest.mkdir()

        return MoltConfig(
            organism_name="test",
            organism_type="offspring",
            sources=[
                SourceMapping(
                    name="test",
                    source=source,
                    destination=dest,
                    archive=archive,
                )
            ],
        )

    def test_molt_source_no_files(self) -> None:
        """Test molt with no files."""
        with TemporaryDirectory() as tmpdir:
            config = self._create_config(Path(tmpdir))
            engine = MoltEngine(config)

            result = engine.molt_source(config.sources[0], dry_run=True)

            assert result.files_found == 0
            assert result.files_migrated == 0
            assert result.skipped == 0
            assert len(result.errors) == 0

    def test_molt_source_with_files(self) -> None:
        """Test molt with files in both source and destination."""
        with TemporaryDirectory() as tmpdir:
            config = self._create_config(Path(tmpdir))

            # Create files in both source and destination
            source = config.sources[0].source
            dest = config.sources[0].destination

            (source / "file1.md").write_text("# File 1\nOriginal content")
            (source / "file2.md").write_text("# File 2\nOriginal content")

            (dest / "file1.md").write_text("# File 1\nMigrated content")
            # file2.md not in dest - should be skipped

            engine = MoltEngine(config)
            result = engine.molt_source(config.sources[0], dry_run=True)

            assert result.files_found == 2
            assert result.files_migrated == 1  # Only file1 exists in dest
            assert result.skipped == 1  # file2 not in dest

    def test_molt_source_skips_stubs(self) -> None:
        """Test that existing stubs are skipped."""
        with TemporaryDirectory() as tmpdir:
            config = self._create_config(Path(tmpdir))
            source = config.sources[0].source
            dest = config.sources[0].destination

            # Create a stub file
            stub_content = """# File 1

> **MOVED**: This document has been molted.
>
> **New Location**: [file1.md](../dest/file1.md)
"""
            (source / "file1.md").write_text(stub_content)
            (dest / "file1.md").write_text("# File 1\nMigrated")

            engine = MoltEngine(config)
            result = engine.molt_source(config.sources[0], dry_run=True)

            assert result.files_found == 1
            assert result.skipped == 1  # Already a stub

    def test_molt_source_execute(self) -> None:
        """Test actual molt execution."""
        with TemporaryDirectory() as tmpdir:
            config = self._create_config(Path(tmpdir))
            source = config.sources[0].source
            dest = config.sources[0].destination

            original_content = "# File 1\nOriginal content"
            (source / "file1.md").write_text(original_content)
            (dest / "file1.md").write_text("# File 1\nMigrated")

            engine = MoltEngine(config)
            result = engine.molt_source(config.sources[0], dry_run=False)

            assert result.files_archived == 1
            assert result.stubs_created == 1

            # Verify source is now a stub
            stub_content = (source / "file1.md").read_text()
            assert "> **MOVED**:" in stub_content
            assert "**New Location**" in stub_content
            assert "**Archive**" in stub_content
            assert "**Molted On**" in stub_content

            # Verify archive has original
            archive_files = list(config.sources[0].archive.rglob("file1.md"))
            assert len(archive_files) == 1
            assert archive_files[0].read_text() == original_content

    def test_molt_source_nonexistent(self) -> None:
        """Test molt with nonexistent source."""
        with TemporaryDirectory() as tmpdir:
            config = MoltConfig(
                organism_name="test",
                organism_type="offspring",
                sources=[
                    SourceMapping(
                        name="test",
                        source=Path(tmpdir) / "nonexistent",
                        destination=Path(tmpdir) / "dest",
                        archive=Path(tmpdir) / "archive",
                    )
                ],
            )

            engine = MoltEngine(config)
            result = engine.molt_source(config.sources[0], dry_run=True)

            assert len(result.errors) > 0
            assert "does not exist" in result.errors[0]

    def test_molt_all(self) -> None:
        """Test molt all sources."""
        with TemporaryDirectory() as tmpdir:
            source1 = Path(tmpdir) / "source1"
            source2 = Path(tmpdir) / "source2"
            dest1 = Path(tmpdir) / "dest1"
            dest2 = Path(tmpdir) / "dest2"

            for d in [source1, source2, dest1, dest2]:
                d.mkdir()

            config = MoltConfig(
                organism_name="test",
                organism_type="offspring",
                sources=[
                    SourceMapping(
                        name="s1",
                        source=source1,
                        destination=dest1,
                        archive=Path(tmpdir) / "archive",
                    ),
                    SourceMapping(
                        name="s2",
                        source=source2,
                        destination=dest2,
                        archive=Path(tmpdir) / "archive",
                    ),
                ],
            )

            engine = MoltEngine(config)
            results = engine.molt_all(dry_run=True)

            assert "s1" in results
            assert "s2" in results

    def test_update_archive_index_creates_new(self) -> None:
        """Test archive index creation."""
        with TemporaryDirectory() as tmpdir:
            config = self._create_config(Path(tmpdir))
            archive_dir = Path(tmpdir) / "archive" / "molt_2026_01_26"
            archive_dir.mkdir(parents=True)

            result = MoltResult(
                source_name="test",
                files_archived=5,
            )

            engine = MoltEngine(config)
            engine.update_archive_index(archive_dir, result)

            index_path = archive_dir.parent / "INDEX.md"
            assert index_path.exists()

            content = index_path.read_text()
            assert "Archive Index" in content
            assert "test" in content
            assert "5" in content
