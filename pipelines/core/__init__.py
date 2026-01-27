"""Pipeline Core - Universal Pipeline Infrastructure.

MOLT LINEAGE:
- Source: Truth_Engine/pipelines/core/__init__.py
- Version: 2.0.0
- Date: 2026-01-26

THE PATTERN at scale: ADAPTER (config) → HOLD1 → PIPELINE → HOLD2
"""

from __future__ import annotations

from pipelines.core.config import PipelineConfig, StageConfig
from pipelines.core.runner import PipelineRunner
from pipelines.core.stage import Stage, StageResult


__all__ = [
    "PipelineConfig",
    "PipelineRunner",
    "Stage",
    "StageConfig",
    "StageResult",
]
