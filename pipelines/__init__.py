"""Pipelines - Universal HOLD→AGENT→HOLD Processing.

MOLT LINEAGE:
- Source: Truth_Engine/pipelines/__init__.py
- Version: 2.0.0
- Date: 2026-01-26

The pipeline system implements THE PATTERN at scale:
  HOLD1 (source) → STAGES (agents) → HOLD2 (destination)

Each stage is itself a mini-pipeline:
  HOLD1 (input) → STAGE (transform) → HOLD2 (output)

BIOLOGICAL METAPHOR:
- Pipelines = Metabolic pathways
- Stages = Enzyme reactions
- Config = Metabolic regulation

Example:
    from pipelines.core import PipelineRunner, PipelineConfig

    config = PipelineConfig.from_toml("config.toml")
    runner = PipelineRunner(config)
    runner.run()
"""

from __future__ import annotations

from pipelines.core import (
    PipelineConfig,
    PipelineRunner,
    Stage,
    StageConfig,
    StageResult,
)


__all__ = [
    "PipelineConfig",
    "PipelineRunner",
    "Stage",
    "StageConfig",
    "StageResult",
]
