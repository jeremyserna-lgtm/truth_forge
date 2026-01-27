"""Tests for pipeline configuration module.

Tests the pipeline configuration loading and validation.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import pytest

# Add pipelines to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from pipelines.core.config import PipelineConfig, StageConfig


class TestStageConfig:
    """Tests for StageConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default stage config values."""
        config = StageConfig(name="test")
        assert config.name == "test"
        assert config.stage_type == "transform"
        assert config.batch_size == 1000
        assert config.model is None

    def test_custom_values(self) -> None:
        """Test custom stage config values."""
        config = StageConfig(
            name="extract",
            stage_type="extract",
            input_path="/input",
            output_path="/output",
            batch_size=500,
            model="haiku",
        )
        assert config.name == "extract"
        assert config.stage_type == "extract"
        assert config.input_path == "/input"
        assert config.output_path == "/output"
        assert config.batch_size == 500
        assert config.model == "haiku"

    def test_from_dict(self) -> None:
        """Test creating from dictionary."""
        data: dict[str, Any] = {
            "name": "Test Stage",
            "type": "load",
            "input": "/data/input.jsonl",
            "output": "/data/output.jsonl",
            "batch_size": 100,
            "model": "sonnet",
            "extra_key": "extra_value",
        }
        config = StageConfig.from_dict("stage_0", data)

        assert config.name == "Test Stage"
        assert config.stage_type == "load"
        assert config.input_path == "/data/input.jsonl"
        assert config.output_path == "/data/output.jsonl"
        assert config.batch_size == 100
        assert config.model == "sonnet"
        assert config.extra["extra_key"] == "extra_value"

    def test_from_dict_defaults(self) -> None:
        """Test from_dict uses defaults for missing keys."""
        config = StageConfig.from_dict("stage_0", {})
        assert config.name == "stage_0"
        assert config.stage_type == "transform"
        assert config.batch_size == 1000


class TestPipelineConfig:
    """Tests for PipelineConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default pipeline config values."""
        config = PipelineConfig(name="test")
        assert config.name == "test"
        assert config.version == "1.0.0"
        assert config.stages == {}

    def test_get_stage_order_empty(self) -> None:
        """Test get_stage_order with no stages."""
        config = PipelineConfig(name="test")
        order = config.get_stage_order()
        assert order == []

    def test_get_stage_order_sorted(self) -> None:
        """Test get_stage_order sorts stages."""
        config = PipelineConfig(
            name="test",
            stages={
                "stage_2": StageConfig(name="Stage 2"),
                "stage_0": StageConfig(name="Stage 0"),
                "stage_1": StageConfig(name="Stage 1"),
            },
        )
        order = config.get_stage_order()
        assert order == ["stage_0", "stage_1", "stage_2"]

    def test_from_toml(self, tmp_path: Path) -> None:
        """Test loading from TOML file."""
        toml_content = '''
[pipeline]
name = "test_pipeline"
version = "2.0.0"
description = "Test pipeline"

[stages.stage_0]
name = "Extract"
type = "extract"
'''
        toml_file = tmp_path / "config.toml"
        toml_file.write_text(toml_content)

        config = PipelineConfig.from_toml(toml_file)

        assert config.name == "test_pipeline"
        assert config.version == "2.0.0"
        assert config.description == "Test pipeline"
        assert "stage_0" in config.stages
        assert config.stages["stage_0"].stage_type == "extract"

    def test_from_toml_not_found(self, tmp_path: Path) -> None:
        """Test from_toml raises for missing file."""
        with pytest.raises(FileNotFoundError):
            PipelineConfig.from_toml(tmp_path / "nonexistent.toml")
