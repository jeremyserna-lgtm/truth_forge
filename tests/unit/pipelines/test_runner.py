"""Tests for pipeline runner module.

Tests the pipeline execution runner.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

# Add pipelines to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from pipelines.core.config import PipelineConfig, StageConfig
from pipelines.core.runner import PipelineResult, PipelineRunner
from pipelines.core.stage import Stage, StageResult


class TestPipelineResult:
    """Tests for PipelineResult dataclass."""

    def test_default_values(self) -> None:
        """Test default result values."""
        result = PipelineResult(pipeline_name="test")
        assert result.pipeline_name == "test"
        assert result.status == "success"
        assert result.stages == {}
        assert result.duration_seconds == 0.0

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        result = PipelineResult(pipeline_name="test")
        data = result.to_dict()

        assert "pipeline_name" in data
        assert "status" in data
        assert "stages" in data
        assert "started_at" in data
        assert data["pipeline_name"] == "test"


class TestPipelineRunner:
    """Tests for PipelineRunner class."""

    def test_initialization(self) -> None:
        """Test runner initializes with config."""
        config = PipelineConfig(name="test")
        runner = PipelineRunner(config)
        assert runner.config == config

    def test_register_stage(self) -> None:
        """Test registering a stage class."""
        config = PipelineConfig(name="test")
        runner = PipelineRunner(config)

        class TestStage(Stage):
            STAGE_TYPE = "test"

            def transform(self, record: dict[str, Any]) -> dict[str, Any] | None:
                return record

        runner.register_stage("test_stage", TestStage)
        assert "test_stage" in runner._stage_registry

    def test_run_dry_run(self) -> None:
        """Test dry run mode."""
        config = PipelineConfig(
            name="test",
            stages={
                "stage_0": StageConfig(name="Test Stage"),
            },
        )
        runner = PipelineRunner(config)
        result = runner.run(dry_run=True)

        assert result.status == "success"
        assert "stage_0" in result.stages
        assert result.stages["stage_0"].status == "dry_run"

    def test_run_stages_dry_run(self) -> None:
        """Test run_stages with dry run."""
        config = PipelineConfig(
            name="test",
            stages={
                "stage_0": StageConfig(name="Stage 0"),
                "stage_1": StageConfig(name="Stage 1"),
            },
        )
        runner = PipelineRunner(config)
        result = runner.run_stages(["stage_0", "stage_1"], dry_run=True)

        assert result.status == "success"
        assert len(result.stages) == 2
        for stage_result in result.stages.values():
            assert stage_result.status == "dry_run"

    def test_run_stages_missing_stage(self) -> None:
        """Test run_stages with missing stage in config."""
        config = PipelineConfig(name="test")
        runner = PipelineRunner(config)
        result = runner.run_stages(["nonexistent"], dry_run=True)

        # Missing stages are skipped, not failed
        assert result.status == "success"
        assert "nonexistent" not in result.stages

    def test_run_stages_no_class_registered(self) -> None:
        """Test run_stages with no stage class registered."""
        config = PipelineConfig(
            name="test",
            stages={
                "stage_0": StageConfig(name="Test Stage"),
            },
        )
        runner = PipelineRunner(config)
        result = runner.run_stages(["stage_0"], dry_run=False)

        assert "stage_0" in result.stages
        assert result.stages["stage_0"].status == "skipped"
        assert result.stages["stage_0"].metadata["reason"] == "no_class_registered"
