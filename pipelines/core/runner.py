"""Pipeline Runner - Execute Pipelines.

MOLT LINEAGE:
- Source: Truth_Engine/pipelines/core/runner.py
- Version: 2.0.0
- Date: 2026-01-26

Orchestrates pipeline execution following THE PATTERN:
  ADAPTER (config) → HOLD1 (source) → STAGES → HOLD2 (destination)

BIOLOGICAL METAPHOR:
- Runner = Metabolic pathway controller
- Config = Regulatory factors
- Stages = Enzyme cascade

Example:
    config = PipelineConfig.from_toml(Path("config.toml"))
    runner = PipelineRunner(config)
    results = runner.run()

    # Or run specific stages
    results = runner.run_stages(["stage_0", "stage_1"])
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from pipelines.core.config import PipelineConfig, get_adapter_config_path
from pipelines.core.stage import Stage, StageResult


logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Result of a complete pipeline run.

    Attributes:
        pipeline_name: Name of the pipeline.
        status: Overall status.
        stages: Results for each stage.
        started_at: When pipeline started.
        finished_at: When pipeline finished.
        duration_seconds: Total duration.
        metadata: Additional metadata.
    """

    pipeline_name: str
    status: str = "success"
    stages: dict[str, StageResult] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    duration_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "pipeline_name": self.pipeline_name,
            "status": self.status,
            "stages": {k: v.to_dict() for k, v in self.stages.items()},
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }


class PipelineRunner:
    """Executes pipeline stages in order.

    The runner:
    1. Loads pipeline configuration
    2. Creates stage instances
    3. Executes stages in order
    4. Collects and returns results

    BIOLOGICAL METAPHOR:
    - Runner = Metabolic pathway coordinator
    - Configuration = Gene regulatory network
    - Execution = Metabolic flux

    Example:
        runner = PipelineRunner(config)

        # Run all stages
        result = runner.run()

        # Run specific stages
        result = runner.run_stages(["stage_0", "stage_1"])

        # Dry run
        result = runner.run(dry_run=True)
    """

    def __init__(self, config: PipelineConfig) -> None:
        """Initialize pipeline runner.

        Args:
            config: Pipeline configuration.
        """
        self.config = config
        self._stage_registry: dict[str, type[Stage]] = {}

        logger.info(
            "PipelineRunner initialized",
            extra={"pipeline": config.name, "version": config.version},
        )

    def register_stage(self, stage_name: str, stage_class: type[Stage]) -> None:
        """Register a stage class.

        Args:
            stage_name: Stage identifier.
            stage_class: Stage class to instantiate.
        """
        self._stage_registry[stage_name] = stage_class
        logger.debug("Stage registered", extra={"stage": stage_name})

    def run(
        self,
        dry_run: bool = False,
        stop_on_error: bool = False,
    ) -> PipelineResult:
        """Run the complete pipeline.

        Args:
            dry_run: If True, only validate without executing.
            stop_on_error: If True, stop on first error.

        Returns:
            PipelineResult with all stage results.
        """
        stage_order = self.config.get_stage_order()
        return self.run_stages(stage_order, dry_run=dry_run, stop_on_error=stop_on_error)

    def run_stages(
        self,
        stages: list[str],
        dry_run: bool = False,
        stop_on_error: bool = False,
    ) -> PipelineResult:
        """Run specific stages.

        Args:
            stages: List of stage names to run.
            dry_run: If True, only validate without executing.
            stop_on_error: If True, stop on first error.

        Returns:
            PipelineResult with stage results.
        """
        started_at = datetime.now(UTC)

        logger.info(
            "Pipeline starting",
            extra={
                "pipeline": self.config.name,
                "stages": stages,
                "dry_run": dry_run,
            },
        )

        result = PipelineResult(
            pipeline_name=self.config.name,
            started_at=started_at,
            metadata={"dry_run": dry_run, "requested_stages": stages},
        )

        for stage_name in stages:
            if stage_name not in self.config.stages:
                logger.warning(
                    "Stage not found in config",
                    extra={"stage": stage_name},
                )
                continue

            stage_config = self.config.stages[stage_name]

            if dry_run:
                result.stages[stage_name] = StageResult(
                    stage_name=stage_name,
                    status="dry_run",
                )
                continue

            # Get stage class from registry or use default
            stage_class = self._stage_registry.get(stage_name)
            if stage_class is None:
                logger.warning(
                    "No stage class registered, skipping",
                    extra={"stage": stage_name},
                )
                result.stages[stage_name] = StageResult(
                    stage_name=stage_name,
                    status="skipped",
                    metadata={"reason": "no_class_registered"},
                )
                continue

            try:
                stage = stage_class(stage_config)
                stage_result = stage.run()
                result.stages[stage_name] = stage_result

                if stage_result.status == "failed" and stop_on_error:
                    logger.error(
                        "Stopping pipeline due to error",
                        extra={"stage": stage_name},
                    )
                    result.status = "failed"
                    break

            except Exception as e:
                logger.error(
                    "Stage execution error",
                    extra={"stage": stage_name, "error": str(e)},
                    exc_info=True,
                )
                result.stages[stage_name] = StageResult(
                    stage_name=stage_name,
                    status="failed",
                    metadata={"error": str(e)},
                )
                if stop_on_error:
                    result.status = "failed"
                    break

        finished_at = datetime.now(UTC)
        result.finished_at = finished_at
        result.duration_seconds = (finished_at - started_at).total_seconds()

        # Determine overall status
        if result.status != "failed":
            failed_stages = [s for s, r in result.stages.items() if r.status == "failed"]
            if failed_stages:
                result.status = "partial"
            else:
                result.status = "success"

        logger.info(
            "Pipeline completed",
            extra={
                "pipeline": self.config.name,
                "status": result.status,
                "duration": result.duration_seconds,
            },
        )

        return result


def load_adapter(adapter_name: str) -> PipelineConfig:
    """Load configuration for a pipeline adapter.

    Args:
        adapter_name: Name of the adapter.

    Returns:
        PipelineConfig loaded from the adapter's config file.
    """
    config_path = get_adapter_config_path(adapter_name)
    logger.info(
        "Loading adapter config",
        extra={"adapter": adapter_name, "path": str(config_path)},
    )
    return PipelineConfig.from_toml(config_path)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for pipeline runner.

    Args:
        argv: Command line arguments.

    Returns:
        Exit code.
    """
    parser = argparse.ArgumentParser(description="Universal Pipeline Runner")
    parser.add_argument(
        "--adapter",
        "-a",
        required=True,
        help="Adapter name (e.g., claude_code)",
    )
    parser.add_argument("--stage", "-s", type=int, help="Run a single stage")
    parser.add_argument("--start", type=int, help="Start from stage N")
    parser.add_argument("--end", type=int, help="End at stage N")
    parser.add_argument(
        "--stages",
        type=str,
        help="Comma-separated list of stages to run",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args(argv)

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        config = load_adapter(args.adapter)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    runner = PipelineRunner(config)

    # Determine stages to run
    stages_to_run: list[str] | None = None
    if args.stages:
        stages_to_run = [f"stage_{s.strip()}" for s in args.stages.split(",")]
    elif args.stage is not None:
        stages_to_run = [f"stage_{args.stage}"]
    elif args.start is not None or args.end is not None:
        all_stages = config.get_stage_order()
        start = args.start or 0
        end = args.end or 999
        stages_to_run = [s for s in all_stages if start <= int(s.split("_")[1]) <= end]

    # Run pipeline
    if stages_to_run:
        result = runner.run_stages(stages_to_run, dry_run=args.dry_run)
    else:
        result = runner.run(dry_run=args.dry_run)

    # Print summary
    print("\n=== Pipeline Results ===")
    print(f"Pipeline: {result.pipeline_name}")
    print(f"Status: {result.status}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    print("\nStages:")
    for stage_name, stage_result in result.stages.items():
        print(f"  {stage_name}: {stage_result.status}")
        if stage_result.records_in > 0:
            print(f"    Records: {stage_result.records_in} in, {stage_result.records_out} out")
        if stage_result.errors > 0:
            print(f"    Errors: {stage_result.errors}")

    return 0 if result.status == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
