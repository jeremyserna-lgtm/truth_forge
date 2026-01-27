"""Unit tests for molt configuration."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from truth_forge.molt.config import (
    ArchiveSettings,
    MoltConfig,
    SourceMapping,
    StubSettings,
    TrackingSettings,
    VerificationSettings,
)


class TestSourceMapping:
    """Tests for SourceMapping dataclass."""

    def test_defaults(self) -> None:
        """Test default values."""
        mapping = SourceMapping(
            name="test",
            source=Path("/source"),
            destination=Path("/dest"),
            archive=Path("/archive"),
        )
        assert mapping.patterns == ["*.md", "**/*.md"]
        assert mapping.exclude == ["**/archive/**", "**/.git/**"]

    def test_custom_patterns(self) -> None:
        """Test custom patterns."""
        mapping = SourceMapping(
            name="test",
            source=Path("/source"),
            destination=Path("/dest"),
            archive=Path("/archive"),
            patterns=["*.txt"],
            exclude=["**/node_modules/**"],
        )
        assert mapping.patterns == ["*.txt"]
        assert mapping.exclude == ["**/node_modules/**"]


class TestArchiveSettings:
    """Tests for ArchiveSettings dataclass."""

    def test_defaults(self) -> None:
        """Test default values."""
        settings = ArchiveSettings()
        assert settings.date_format == "%Y_%m_%d"
        assert settings.index_file == "INDEX.md"
        assert settings.preserve_structure is True


class TestStubSettings:
    """Tests for StubSettings dataclass."""

    def test_defaults(self) -> None:
        """Test default values."""
        settings = StubSettings()
        assert "**MOVED**" in settings.template
        assert settings.max_lines == 20


class TestVerificationSettings:
    """Tests for VerificationSettings dataclass."""

    def test_defaults(self) -> None:
        """Test default values."""
        settings = VerificationSettings()
        assert settings.max_stub_lines == 20
        assert "**MOVED**" in settings.required_markers


class TestTrackingSettings:
    """Tests for TrackingSettings dataclass."""

    def test_defaults(self) -> None:
        """Test default values."""
        settings = TrackingSettings()
        assert settings.enabled is True
        assert settings.history_file == Path(".molt/history.jsonl")


class TestMoltConfig:
    """Tests for MoltConfig dataclass."""

    def test_minimal_config(self) -> None:
        """Test minimal configuration."""
        config = MoltConfig(
            organism_name="test",
            organism_type="offspring",
            sources=[],
        )
        assert config.organism_name == "test"
        assert config.organism_type == "offspring"
        assert len(config.sources) == 0

    def test_validation_empty_name(self) -> None:
        """Test validation catches empty name."""
        config = MoltConfig(
            organism_name="",
            organism_type="offspring",
            sources=[],
        )
        errors = config.validate()
        assert "organism.name is required" in errors

    def test_validation_invalid_type(self) -> None:
        """Test validation catches invalid type."""
        config = MoltConfig(
            organism_name="test",
            organism_type="invalid",
            sources=[],
        )
        errors = config.validate()
        assert any("organism.type must be" in e for e in errors)

    def test_validation_empty_sources(self) -> None:
        """Test validation catches empty sources."""
        config = MoltConfig(
            organism_name="test",
            organism_type="offspring",
            sources=[],
        )
        errors = config.validate()
        assert "At least one source mapping is required" in errors

    def test_from_yaml(self) -> None:
        """Test loading from YAML file."""
        with TemporaryDirectory() as tmpdir:
            # Create test directories
            source_dir = Path(tmpdir) / "source"
            dest_dir = Path(tmpdir) / "dest"
            source_dir.mkdir()
            dest_dir.mkdir()

            # Create config file
            config_path = Path(tmpdir) / "molt.yaml"
            config_path.write_text(f"""
organism:
  name: test_org
  type: offspring

sources:
  - name: test_source
    source: source
    destination: dest
    archive: archive
""")

            config = MoltConfig.from_yaml(config_path)
            assert config.organism_name == "test_org"
            assert config.organism_type == "offspring"
            assert len(config.sources) == 1
            assert config.sources[0].name == "test_source"

    def test_from_yaml_not_found(self) -> None:
        """Test error when config file not found."""
        with pytest.raises(FileNotFoundError):
            MoltConfig.from_yaml(Path("/nonexistent/molt.yaml"))

    def test_find_config(self) -> None:
        """Test config file discovery."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "molt.yaml"
            config_path.write_text("organism:\n  name: test\n")

            found = MoltConfig.find_config(Path(tmpdir))
            # Use resolve() to handle macOS symlinks (/var -> /private/var)
            assert found is not None
            assert found.resolve() == config_path.resolve()

    def test_find_config_not_found(self) -> None:
        """Test when no config found."""
        with TemporaryDirectory() as tmpdir:
            found = MoltConfig.find_config(Path(tmpdir))
            # May find global config or return None
            # Just verify it doesn't crash
            assert found is None or found.exists()
