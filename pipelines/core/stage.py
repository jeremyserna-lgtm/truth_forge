"""Pipeline Stage - Base Stage Implementation.

MOLT LINEAGE:
- Source: Truth_Engine/pipelines/core/stages/__init__.py
- Version: 2.0.0
- Date: 2026-01-26

Each stage implements THE PATTERN:
  HOLD1 (input) → STAGE (transform) → HOLD2 (output)

BIOLOGICAL METAPHOR:
- Stage = Enzyme
- Input = Substrate
- Output = Product
- Transform = Catalysis

Example:
    class ExtractStage(Stage):
        def transform(self, record: dict[str, Any]) -> dict[str, Any]:
            # Extract fields from record
            return {"id": record["id"], "content": record["text"]}

    stage = ExtractStage(config)
    result = stage.run()
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar


if TYPE_CHECKING:
    from pipelines.core.config import StageConfig


logger = logging.getLogger(__name__)


@dataclass
class StageResult:
    """Result of a stage execution.

    Attributes:
        stage_name: Name of the stage.
        status: Execution status (success, failed, skipped).
        records_in: Number of input records.
        records_out: Number of output records.
        errors: Number of errors encountered.
        duration_seconds: Execution duration.
        started_at: When execution started.
        finished_at: When execution finished.
        metadata: Additional result metadata.
    """

    stage_name: str
    status: str = "success"
    records_in: int = 0
    records_out: int = 0
    errors: int = 0
    duration_seconds: float = 0.0
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "stage_name": self.stage_name,
            "status": self.status,
            "records_in": self.records_in,
            "records_out": self.records_out,
            "errors": self.errors,
            "duration_seconds": self.duration_seconds,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "metadata": self.metadata,
        }


class Stage(ABC):
    """Base class for pipeline stages.

    Each stage implements THE PATTERN:
    - read_input(): HOLD1 access
    - transform(): AGENT processing
    - write_output(): HOLD2 delivery

    Subclasses must implement:
    - transform(record) -> transformed record

    Can override:
    - read_input() -> records from HOLD1
    - write_output(records) -> write to HOLD2
    """

    # Stage type identifier
    STAGE_TYPE: ClassVar[str] = "base"

    def __init__(self, config: StageConfig) -> None:
        """Initialize stage.

        Args:
            config: Stage configuration.
        """
        self.config = config
        self.name = config.name
        self._errors: list[dict[str, Any]] = []

        logger.debug(
            "Stage initialized",
            extra={"name": self.name, "type": self.STAGE_TYPE},
        )

    @abstractmethod
    def transform(self, record: dict[str, Any]) -> dict[str, Any] | None:
        """Transform a single record.

        This is the AGENT function - the core transformation logic.

        Args:
            record: Input record from HOLD1.

        Returns:
            Transformed record for HOLD2, or None to skip.
        """
        ...

    def read_input(self) -> list[dict[str, Any]]:
        """Read records from HOLD1.

        Override this to customize input reading.

        Returns:
            List of input records.
        """
        input_path = Path(self.config.input_path)
        if not input_path.exists():
            logger.warning("Input path does not exist", extra={"path": str(input_path)})
            return []

        # Default: read JSONL
        records = []
        import json

        with open(input_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))

        return records

    def write_output(self, records: list[dict[str, Any]]) -> int:
        """Write records to HOLD2.

        Override this to customize output writing.

        Args:
            records: Records to write.

        Returns:
            Number of records written.
        """
        output_path = Path(self.config.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        import json

        with open(output_path, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")

        return len(records)

    def run(self) -> StageResult:
        """Execute the stage.

        Implements THE PATTERN:
        1. HOLD1: Read input
        2. AGENT: Transform each record
        3. HOLD2: Write output

        Returns:
            StageResult with execution details.
        """
        started_at = datetime.now(UTC)
        self._errors.clear()

        logger.info("Stage starting", extra={"name": self.name})

        # HOLD1: Read input
        input_records = self.read_input()
        records_in = len(input_records)

        # AGENT: Transform
        output_records: list[dict[str, Any]] = []
        for record in input_records:
            try:
                transformed = self.transform(record)
                if transformed is not None:
                    output_records.append(transformed)
            except Exception as e:
                self._errors.append({"record": record, "error": str(e)})
                logger.warning(
                    "Transform error",
                    extra={"stage": self.name, "error": str(e)},
                )

        # HOLD2: Write output
        records_out = self.write_output(output_records)

        finished_at = datetime.now(UTC)
        duration = (finished_at - started_at).total_seconds()

        result = StageResult(
            stage_name=self.name,
            status="success" if not self._errors else "partial",
            records_in=records_in,
            records_out=records_out,
            errors=len(self._errors),
            duration_seconds=duration,
            started_at=started_at,
            finished_at=finished_at,
        )

        logger.info(
            "Stage completed",
            extra={
                "name": self.name,
                "status": result.status,
                "records_in": records_in,
                "records_out": records_out,
                "errors": len(self._errors),
                "duration": duration,
            },
        )

        return result


class PassthroughStage(Stage):
    """Stage that passes records through unchanged.

    Useful for testing and as a base for simple transformations.
    """

    STAGE_TYPE: ClassVar[str] = "passthrough"

    def transform(self, record: dict[str, Any]) -> dict[str, Any]:
        """Pass through unchanged.

        Args:
            record: Input record.

        Returns:
            Same record unchanged.
        """
        return record


__all__ = [
    "PassthroughStage",
    "Stage",
    "StageResult",
]
