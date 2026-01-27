"""Pipeline Configuration.

MOLT LINEAGE:
- Source: Truth_Engine/pipelines/core/base_config.py
- Version: 2.0.0
- Date: 2026-01-26

Provides dataclasses for loading and validating pipeline configurations.

THE PATTERN:
- Config = HOLD1 (instruction set)
- Loader = AGENT (parser)
- PipelineConfig = HOLD2 (validated configuration)

Example:
    config = PipelineConfig.from_toml(Path("config.toml"))
    print(config.name, config.version)
    for stage in config.stages.values():
        print(f"  {stage.name}: {stage.stage_type}")
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class StageConfig:
    """Configuration for a single pipeline stage.

    Attributes:
        name: Human-readable stage name.
        stage_type: Type of stage (extract, transform, load, etc.).
        input_path: Path or pattern for input data.
        output_path: Path for output data.
        batch_size: Number of records per batch.
        model: Optional model to use for LLM stages.
        extra: Additional stage-specific configuration.
    """

    name: str
    stage_type: str = "transform"
    input_path: str = ""
    output_path: str = ""
    batch_size: int = 1000
    model: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> StageConfig:
        """Create from dictionary.

        Args:
            name: Stage identifier.
            data: Stage configuration dictionary.

        Returns:
            StageConfig instance.
        """
        reserved_keys = {"name", "type", "input", "output", "batch_size", "model"}

        return cls(
            name=data.get("name", name),
            stage_type=data.get("type", "transform"),
            input_path=data.get("input", ""),
            output_path=data.get("output", ""),
            batch_size=data.get("batch_size", 1000),
            model=data.get("model"),
            extra={k: v for k, v in data.items() if k not in reserved_keys},
        )


@dataclass
class PipelineConfig:
    """Configuration for a complete pipeline.

    Attributes:
        name: Pipeline name.
        version: Pipeline version.
        description: Human-readable description.
        source_name: Name of the data source.
        target_table: Destination table name.
        stages: Ordered dict of stage configurations.
        source: Source-specific configuration.
        destination: Destination-specific configuration.
        models: Model name mappings.
        governance: Governance settings.
    """

    name: str
    version: str = "1.0.0"
    description: str = ""
    source_name: str = ""
    target_table: str = ""
    stages: dict[str, StageConfig] = field(default_factory=dict)
    source: dict[str, Any] = field(default_factory=dict)
    destination: dict[str, Any] = field(default_factory=dict)
    models: dict[str, str] = field(default_factory=dict)
    governance: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def from_toml(cls, path: Path) -> PipelineConfig:
        """Load pipeline configuration from TOML file.

        Args:
            path: Path to TOML configuration file.

        Returns:
            PipelineConfig instance.

        Raises:
            FileNotFoundError: If config file doesn't exist.
            ValueError: If configuration is invalid.
        """
        with open(path, "rb") as f:
            data = tomllib.load(f)

        pipeline = data.get("pipeline", {})
        stages_data = data.get("stages", {})

        # Parse stages
        stages: dict[str, StageConfig] = {}
        for stage_key, stage_val in stages_data.items():
            if isinstance(stage_val, dict):
                stages[stage_key] = StageConfig.from_dict(stage_key, stage_val)

        return cls(
            name=pipeline.get("name", "unknown"),
            version=pipeline.get("version", "1.0.0"),
            description=pipeline.get("description", ""),
            source_name=pipeline.get("source_name", ""),
            target_table=pipeline.get("target_table", ""),
            stages=stages,
            source=data.get("source", {}),
            destination=data.get("destination", data.get("bigquery", {})),
            models=data.get("models", {}),
            governance=data.get("governance", {}),
        )

    def get_stage_order(self) -> list[str]:
        """Get stages in execution order.

        Returns:
            List of stage keys sorted by stage number.
        """
        numbered = [k for k in self.stages if k.startswith("stage_")]
        return sorted(numbered, key=lambda x: int(x.split("_")[1]))


def get_adapter_config_path(adapter_name: str, base_path: Path | None = None) -> Path:
    """Get the path to an adapter's config file.

    Args:
        adapter_name: Name of the adapter.
        base_path: Base path to search from.

    Returns:
        Path to the config file.

    Raises:
        FileNotFoundError: If no config file found.
    """
    if base_path is None:
        base_path = Path(__file__).parent.parent / "adapters"

    adapter_dir = base_path / adapter_name

    for config_name in ("config.toml", "pipeline_config.toml"):
        config_path = adapter_dir / config_name
        if config_path.exists():
            return config_path

    raise FileNotFoundError(f"No config file found for adapter: {adapter_name}")


__all__ = [
    "PipelineConfig",
    "StageConfig",
    "get_adapter_config_path",
]
