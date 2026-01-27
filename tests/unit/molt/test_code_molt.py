"""Unit tests for code molt engine."""

from pathlib import Path
from tempfile import TemporaryDirectory

from truth_forge.molt.code_molt import (
    CodeMoltEngine,
    CodeMoltResult,
    TransformConfig,
    TransformRule,
)


class TestTransformRule:
    """Tests for TransformRule."""

    def test_apply_literal_match(self) -> None:
        """Test literal string replacement."""
        rule = TransformRule(
            pattern="from Primitive.core",
            replacement="from truth_forge.core",
        )
        content = "from Primitive.core import Base"
        result, count = rule.apply(content)

        assert result == "from truth_forge.core import Base"
        assert count == 1

    def test_apply_no_match(self) -> None:
        """Test when pattern doesn't match."""
        rule = TransformRule(
            pattern="from Primitive.core",
            replacement="from truth_forge.core",
        )
        content = "from other_module import Base"
        result, count = rule.apply(content)

        assert result == content
        assert count == 0

    def test_apply_regex_match(self) -> None:
        """Test regex pattern replacement."""
        rule = TransformRule(
            pattern=r"from Primitive\.(\w+)",
            replacement=r"from truth_forge.\1",
            is_regex=True,
        )
        content = "from Primitive.core import Base\nfrom Primitive.utils import helper"
        result, count = rule.apply(content)

        assert "from truth_forge.core import Base" in result
        assert "from truth_forge.utils import helper" in result
        assert count == 2

    def test_apply_multiple_occurrences(self) -> None:
        """Test multiple literal matches."""
        rule = TransformRule(
            pattern="/Users/jeremyserna/Truth_Engine",
            replacement="PROJECT_ROOT",
        )
        content = 'path1 = "/Users/jeremyserna/Truth_Engine/src"\npath2 = "/Users/jeremyserna/Truth_Engine/data"'
        result, count = rule.apply(content)

        assert "PROJECT_ROOT/src" in result
        assert "PROJECT_ROOT/data" in result
        assert count == 2


class TestTransformConfig:
    """Tests for TransformConfig."""

    def test_from_dict(self) -> None:
        """Test creating config from dictionary."""
        data = {
            "imports": [
                {"from": "from Primitive.*", "to": "from truth_forge.*"},
            ],
            "paths": [
                {"from": "/old/path", "to": "/new/path"},
            ],
            "env": [
                {"from": "os.environ['VAR']", "to": "settings.var"},
            ],
        }

        config = TransformConfig.from_dict(data)

        assert len(config.import_rules) == 1
        assert len(config.path_rules) == 1
        assert len(config.env_rules) == 1
        assert config.import_rules[0].pattern == "from Primitive.*"

    def test_from_dict_empty(self) -> None:
        """Test creating config from empty dictionary."""
        config = TransformConfig.from_dict({})

        assert config.import_rules == []
        assert config.path_rules == []
        assert config.env_rules == []

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = TransformConfig.default()

        assert len(config.import_rules) > 0
        assert len(config.path_rules) > 0
        assert len(config.env_rules) > 0


class TestCodeMoltResult:
    """Tests for CodeMoltResult."""

    def test_success_no_errors(self) -> None:
        """Test success property when no errors."""
        result = CodeMoltResult(
            source_name="test",
            files_found=10,
            files_transformed=5,
            errors=[],
        )
        assert result.success is True

    def test_failure_with_errors(self) -> None:
        """Test success is False when errors present."""
        result = CodeMoltResult(
            source_name="test",
            files_found=10,
            files_transformed=5,
            errors=["Something went wrong"],
        )
        assert result.success is False


class TestCodeMoltEngine:
    """Tests for CodeMoltEngine."""

    def test_transform_content_imports(self) -> None:
        """Test import transformation."""
        config = TransformConfig(
            import_rules=[
                TransformRule(
                    pattern=r"from Primitive\.(\w+)",
                    replacement=r"from truth_forge.\1",
                    is_regex=True,
                )
            ],
        )
        engine = CodeMoltEngine(config)

        content = """from Primitive.core import Base
from Primitive.utils import helper
import os
"""
        transformed, counts = engine.transform_content(content)

        assert "from truth_forge.core import Base" in transformed
        assert "from truth_forge.utils import helper" in transformed
        assert "import os" in transformed
        assert counts["imports"] == 2

    def test_transform_content_paths(self) -> None:
        """Test path transformation."""
        config = TransformConfig(
            path_rules=[
                TransformRule(
                    pattern="/Users/jeremyserna/Truth_Engine",
                    replacement="PROJECT_ROOT",
                )
            ],
        )
        engine = CodeMoltEngine(config)

        content = 'BASE_PATH = "/Users/jeremyserna/Truth_Engine/src"'
        transformed, counts = engine.transform_content(content)

        assert 'BASE_PATH = "PROJECT_ROOT/src"' in transformed
        assert counts["paths"] == 1

    def test_transform_content_no_changes(self) -> None:
        """Test content with no matching patterns."""
        config = TransformConfig(
            import_rules=[
                TransformRule(
                    pattern="from Primitive.*",
                    replacement="from truth_forge.*",
                )
            ],
        )
        engine = CodeMoltEngine(config)

        content = "import os\nimport sys\n"
        transformed, counts = engine.transform_content(content)

        assert transformed == content
        assert counts["imports"] == 0

    def test_transform_file_dry_run(self) -> None:
        """Test file transformation in dry run mode."""
        with TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "source.py"
            dest = Path(tmpdir) / "dest.py"

            source.write_text("from Primitive.core import Base")

            config = TransformConfig(
                import_rules=[
                    TransformRule(
                        pattern="from Primitive.core",
                        replacement="from truth_forge.core",
                    )
                ],
            )
            engine = CodeMoltEngine(config)

            changed, counts = engine.transform_file(
                source_file=source,
                dest_file=dest,
                dry_run=True,
            )

            assert changed is True
            assert counts["imports"] == 1
            # Dest should NOT be created in dry run
            assert not dest.exists()

    def test_transform_file_execute(self) -> None:
        """Test actual file transformation."""
        with TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "source.py"
            dest = Path(tmpdir) / "dest.py"

            source.write_text("from Primitive.core import Base")

            config = TransformConfig(
                import_rules=[
                    TransformRule(
                        pattern="from Primitive.core",
                        replacement="from truth_forge.core",
                    )
                ],
            )
            engine = CodeMoltEngine(config)

            changed, counts = engine.transform_file(
                source_file=source,
                dest_file=dest,
                dry_run=False,
            )

            assert changed is True
            assert dest.exists()
            assert "from truth_forge.core import Base" in dest.read_text()

    def test_transform_file_with_archive(self) -> None:
        """Test file transformation with archiving."""
        with TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "source.py"
            dest = Path(tmpdir) / "dest.py"
            archive = Path(tmpdir) / "archive"

            original_content = "from Primitive.core import Base"
            source.write_text(original_content)

            config = TransformConfig(
                import_rules=[
                    TransformRule(
                        pattern="from Primitive.core",
                        replacement="from truth_forge.core",
                    )
                ],
            )
            engine = CodeMoltEngine(config)

            changed, _ = engine.transform_file(
                source_file=source,
                dest_file=dest,
                archive_dir=archive,
                dry_run=False,
            )

            assert changed is True
            # Archive should have original
            archive_file = archive / "source.py"
            assert archive_file.exists()
            assert archive_file.read_text() == original_content

    def test_molt_directory(self) -> None:
        """Test molting an entire directory."""
        with TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "source"
            dest_dir = Path(tmpdir) / "dest"
            source_dir.mkdir()

            # Create test files
            (source_dir / "file1.py").write_text("from Primitive.core import A")
            (source_dir / "file2.py").write_text("import os")  # No changes

            config = TransformConfig(
                import_rules=[
                    TransformRule(
                        pattern="from Primitive.core",
                        replacement="from truth_forge.core",
                    )
                ],
            )
            engine = CodeMoltEngine(config)

            result = engine.molt_directory(
                source_dir=source_dir,
                dest_dir=dest_dir,
                dry_run=True,
            )

            assert result.files_found == 2
            assert result.files_transformed == 1
            assert result.files_unchanged == 1

    def test_molt_directory_nonexistent(self) -> None:
        """Test molting nonexistent directory."""
        engine = CodeMoltEngine()

        result = engine.molt_directory(
            source_dir=Path("/nonexistent"),
            dest_dir=Path("/dest"),
            dry_run=True,
        )

        assert len(result.errors) > 0
        assert "does not exist" in result.errors[0]

    def test_molt_phase(self) -> None:
        """Test molting by phase configuration."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create source structure
            source_dir = base / "Truth_Engine" / "src"
            source_dir.mkdir(parents=True)
            (source_dir / "module.py").write_text("from Primitive.core import Base")

            # Create phase config (mimics molt.yaml structure)
            phase_config = {
                "phase": 1,
                "name": "core",
                "sources": [
                    {
                        "source": "Truth_Engine/src",
                        "destination": "src/truth_forge",
                    }
                ],
            }

            config = TransformConfig(
                import_rules=[
                    TransformRule(
                        pattern="from Primitive.core",
                        replacement="from truth_forge.core",
                    )
                ],
            )
            engine = CodeMoltEngine(config)

            result = engine.molt_phase(
                phase_config=phase_config,
                base_path=base,
                dry_run=True,
            )

            assert result.files_found == 1
            assert result.files_transformed == 1
            assert result.source_name == "phase_core"
