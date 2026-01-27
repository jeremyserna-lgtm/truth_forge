"""Pipeline Stages - Stage Type Registry.

MOLT LINEAGE:
- Source: Truth_Engine/pipelines/core/stages/__init__.py
- Version: 2.0.0
- Date: 2026-01-26

Provides built-in stage types for common pipeline operations.

STAGE TYPES:
- Extract: Read from source
- Transform: Process/modify data
- Load: Write to destination
- Validate: Check data quality
- Enrich: Add derived fields

Example:
    from pipelines.core.stages import ExtractStage, TransformStage

    class MyExtractor(ExtractStage):
        def extract(self) -> list[dict]:
            return self.read_from_source()
"""

from __future__ import annotations

from pipelines.core.stage import PassthroughStage, Stage, StageResult


# Stage type registry
STAGE_TYPES: dict[str, type[Stage]] = {
    "passthrough": PassthroughStage,
}


def register_stage_type(stage_type: str, stage_class: type[Stage]) -> None:
    """Register a stage type globally.

    Args:
        stage_type: Type identifier.
        stage_class: Stage class.
    """
    STAGE_TYPES[stage_type] = stage_class


def get_stage_class(stage_type: str) -> type[Stage] | None:
    """Get a stage class by type.

    Args:
        stage_type: Type identifier.

    Returns:
        Stage class or None if not found.
    """
    return STAGE_TYPES.get(stage_type)


__all__ = [
    "PassthroughStage",
    "STAGE_TYPES",
    "Stage",
    "StageResult",
    "get_stage_class",
    "register_stage_type",
]
