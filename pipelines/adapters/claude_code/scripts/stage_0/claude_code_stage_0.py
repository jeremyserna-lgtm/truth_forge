#!/usr/bin/env python3
"""Stage 0: Assessment - Claude Code Pipeline.

HOLD₁ (JSONL session files) → AGENT (Format Analyzer) → HOLD₂ (Assessment Report)

Analyzes Claude Code session export files to understand structure and quality
before processing. Produces an assessment report with recommendations.

🧠 STAGE FIVE GROUNDING
This stage exists to analyze raw Claude Code exports before pipeline processing.

Structure: Discover files → Parse samples → Analyze structure → Generate report
Purpose: Validate source data is processable, identify potential issues early
Boundaries: Read-only analysis, no data transformation, no BigQuery writes
Control: Manual trigger, outputs assessment report to staging directory

⚠️ WHAT THIS STAGE CANNOT SEE
- Full content of all sessions (samples only for large datasets)
- Runtime context of original Claude Code sessions
- User intent beyond message text
- Whether sessions are complete or truncated

🔥 THE FURNACE PRINCIPLE
- Truth (input): Raw JSONL export files from Claude Code
- Heat (processing): Schema analysis, sample parsing, statistics gathering
- Meaning (output): Assessment report with structure, quality, and recommendations
- Care (delivery): Clear go/no-go decision for pipeline execution

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows Stage 0 of the Universal Pipeline Pattern for claude_code.

RATIONALE:
----------
- Stage 0 is assessment-only: understand what you have before processing
- Enables early detection of format changes or data quality issues
- Produces actionable report for operator decision

Enterprise Governance Standards:
- Uses central services for logging with traceability
- All operations follow universal governance policies
- Comprehensive error handling and validation
- Full audit trail for all operations

Usage:
    python claude_code_stage_0.py [--source-dir PATH] [--sample-size N] [--output PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


# Add paths for imports before importing local modules
_script_dir = Path(__file__).parent
_scripts_dir = _script_dir.parent
_pipeline_dir = _scripts_dir.parent
_project_root = _pipeline_dir.parent.parent
_src_path = _project_root / "src"

sys.path.insert(0, str(_scripts_dir))
sys.path.insert(0, str(_src_path))

# Local imports after path setup (ruff: noqa: E402)
from shared import PIPELINE_NAME, SOURCE_NAME  # noqa: E402
from src.services.central_services.core import (  # noqa: E402
    get_current_run_id,
    get_logger,
)
from src.services.central_services.core.pipeline_tracker import (  # noqa: E402
    PipelineTracker,
)


logger = get_logger(__name__)

# Default source directory for Claude Code exports
DEFAULT_SOURCE_DIR = Path.home() / ".claude" / "projects"
DEFAULT_OUTPUT_DIR = _pipeline_dir / "staging" / "assessment"
DEFAULT_SAMPLE_SIZE = 100


def discover_session_files(source_dir: Path) -> list[Path]:
    """Discover all JSONL session files in source directory.

    Args:
        source_dir: Directory to search for JSONL files.

    Returns:
        List of JSONL file paths sorted by modification time (newest first).
    """
    if not source_dir.exists():
        logger.warning(
            "Source directory does not exist",
            extra={"source_dir": str(source_dir)},
        )
        return []

    jsonl_files = list(source_dir.rglob("*.jsonl"))
    logger.info(
        "Discovered JSONL files",
        extra={"file_count": len(jsonl_files), "source_dir": str(source_dir)},
    )

    return sorted(jsonl_files, key=lambda p: p.stat().st_mtime, reverse=True)


def parse_session_file(
    file_path: Path,
    max_messages: int = 1000,
) -> dict[str, Any]:
    """Parse a single session JSONL file.

    Args:
        file_path: Path to JSONL file.
        max_messages: Maximum messages to parse (for sampling).

    Returns:
        Parsed session data with statistics.
    """
    message_types: dict[str, int] = defaultdict(int)
    models_used: set[str] = set()
    tools_used: dict[str, int] = defaultdict(int)
    timestamps: list[str] = []
    errors: list[str] = []
    sample_messages: list[dict[str, Any]] = []
    message_count = 0
    total_cost_usd = 0.0

    try:
        with open(file_path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= max_messages:
                    break

                try:
                    msg = json.loads(line.strip())
                    message_count += 1

                    msg_type = msg.get("type", "unknown")
                    message_types[msg_type] += 1

                    if msg_type == "summary" and msg.get("model"):
                        models_used.add(msg["model"])

                    if msg_type == "tool_use":
                        tool_name = msg.get("name", "unknown")
                        tools_used[tool_name] += 1

                    if msg.get("cost_usd"):
                        total_cost_usd += float(msg["cost_usd"])

                    if msg.get("timestamp"):
                        timestamps.append(msg["timestamp"])

                    # Keep first few messages as samples
                    if len(sample_messages) < 5:
                        sample_messages.append(msg)

                except json.JSONDecodeError as e:
                    errors.append(f"Line {i}: {e!s}")

    except Exception as e:
        errors.append(f"File error: {e!s}")

    return {
        "file_path": str(file_path),
        "file_size_bytes": file_path.stat().st_size,
        "message_count": message_count,
        "message_types": dict(message_types),
        "models_used": list(models_used),
        "tools_used": dict(tools_used),
        "total_cost_usd": total_cost_usd,
        "timestamps": timestamps,
        "errors": errors,
        "sample_messages": sample_messages,
    }


def generate_assessment_report(
    session_files: list[Path],
    sample_size: int = DEFAULT_SAMPLE_SIZE,
) -> dict[str, Any]:
    """Generate comprehensive assessment report.

    Args:
        session_files: List of session file paths.
        sample_size: Number of files to sample for detailed analysis.

    Returns:
        Assessment report dictionary.
    """
    run_id = get_current_run_id()

    # Initialize aggregates with proper types
    message_types: dict[str, int] = defaultdict(int)
    models_used: set[str] = set()
    tools_used: dict[str, int] = defaultdict(int)
    total_messages = 0
    total_cost_usd = 0.0
    files_with_errors = 0
    files_analyzed: list[dict[str, Any]] = []
    earliest_ts: str | None = None
    latest_ts: str | None = None

    # Sample files for analysis
    files_to_analyze = session_files[:sample_size]

    for file_path in files_to_analyze:
        logger.info(
            "Analyzing session file",
            extra={"file_name": file_path.name},
        )
        session_data = parse_session_file(file_path)
        files_analyzed.append(session_data)

        # Aggregate statistics
        total_messages += session_data["message_count"]
        total_cost_usd += session_data["total_cost_usd"]

        for msg_type, count in session_data["message_types"].items():
            message_types[msg_type] += count

        models_used.update(session_data["models_used"])

        for tool, count in session_data["tools_used"].items():
            tools_used[tool] += count

        if session_data["errors"]:
            files_with_errors += 1

        # Track date range
        for ts in session_data["timestamps"]:
            if earliest_ts is None or ts < earliest_ts:
                earliest_ts = ts
            if latest_ts is None or ts > latest_ts:
                latest_ts = ts

    report: dict[str, Any] = {
        "assessment_timestamp": datetime.now(UTC).isoformat(),
        "run_id": run_id,
        "pipeline": PIPELINE_NAME,
        "source": SOURCE_NAME,
        "summary": {
            "total_files_discovered": len(session_files),
            "files_sampled": min(sample_size, len(session_files)),
            "total_messages": total_messages,
            "total_cost_usd": total_cost_usd,
            "message_types": dict(message_types),
            "models_used": list(models_used),
            "tools_used": dict(tools_used),
            "files_with_errors": files_with_errors,
        },
        "date_range": {"earliest": earliest_ts, "latest": latest_ts},
        "files_analyzed": files_analyzed,
        "recommendations": [],
        "go_no_go": "UNKNOWN",
    }

    # Generate recommendations
    report["recommendations"] = _generate_recommendations(report)

    # Determine go/no-go
    report["go_no_go"] = _determine_go_no_go(report)

    return report


def _generate_recommendations(report: dict[str, Any]) -> list[str]:
    """Generate recommendations based on assessment.

    Args:
        report: The assessment report dictionary.

    Returns:
        List of recommendation strings.
    """
    recommendations: list[str] = []

    summary = report["summary"]

    if summary["total_files_discovered"] == 0:
        recommendations.append("CRITICAL: No JSONL files found. Check source directory.")

    if summary["files_with_errors"] > 0:
        error_rate = summary["files_with_errors"] / max(summary["files_sampled"], 1)
        if error_rate > 0.1:
            recommendations.append(
                f"WARNING: {error_rate:.1%} of files have parse errors. Review data quality."
            )

    if summary["total_messages"] == 0:
        recommendations.append("CRITICAL: No messages found in sampled files.")

    if "user" not in summary["message_types"]:
        recommendations.append("WARNING: No 'user' message type found. Check export format.")

    if "assistant" not in summary["message_types"]:
        recommendations.append("WARNING: No 'assistant' message type found. Check export format.")

    if summary["total_cost_usd"] > 0:
        recommendations.append(f"INFO: Total API cost in sample: ${summary['total_cost_usd']:.2f}")

    if not recommendations:
        recommendations.append("OK: Data appears well-formed and ready for processing.")

    return recommendations


def _determine_go_no_go(report: dict[str, Any]) -> str:
    """Determine if pipeline should proceed.

    Args:
        report: The assessment report dictionary.

    Returns:
        Go/no-go decision string.
    """
    summary = report["summary"]

    # Critical failures
    if summary["total_files_discovered"] == 0:
        return "NO-GO: No source files"

    if summary["total_messages"] == 0:
        return "NO-GO: No messages found"

    # Warnings
    error_rate = summary["files_with_errors"] / max(summary["files_sampled"], 1)
    if error_rate > 0.5:
        return "NO-GO: Too many parse errors"

    if error_rate > 0.1:
        return "CAUTION: Some parse errors, review before proceeding"

    return "GO: Data ready for processing"


def save_report(report: dict[str, Any], output_path: Path) -> None:
    """Save assessment report to JSON file.

    Args:
        report: The assessment report dictionary.
        output_path: Path to save the report.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info(
        "Assessment report saved",
        extra={"output_path": str(output_path)},
    )


def main() -> int:
    """Execute Stage 0: Assessment.

    Returns:
        Exit code (0 for GO, 1 for NO-GO or error).
    """
    parser = argparse.ArgumentParser(description="Stage 0: Assess Claude Code session exports")
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help=f"Source directory for JSONL files (default: {DEFAULT_SOURCE_DIR})",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        help=f"Number of files to sample (default: {DEFAULT_SAMPLE_SIZE})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for assessment report",
    )

    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME,
        stage=0,
        stage_name="assessment",
        run_id=run_id,
        metadata={"source_dir": str(args.source_dir), "sample_size": args.sample_size},
    ) as tracker:
        try:
            logger.info(
                "Starting Stage 0: Assessment",
                extra={"run_id": run_id, "source_dir": str(args.source_dir)},
            )

            # HOLD₁: Discover source files
            session_files = discover_session_files(args.source_dir)
            tracker.update_progress(items_total=len(session_files))

            # AGENT: Generate assessment report
            report = generate_assessment_report(session_files, args.sample_size)
            tracker.update_progress(items_processed=len(report["files_analyzed"]))

            # HOLD₂: Save report
            output_path = args.output or (DEFAULT_OUTPUT_DIR / f"assessment_{run_id}.json")
            save_report(report, output_path)

            # Log summary with structured logging
            logger.info(
                "Assessment complete",
                extra={
                    "run_id": run_id,
                    "go_no_go": report["go_no_go"],
                    "files_discovered": report["summary"]["total_files_discovered"],
                    "files_sampled": report["summary"]["files_sampled"],
                    "messages_found": report["summary"]["total_messages"],
                    "output_path": str(output_path),
                },
            )

            # Console output for human readability
            _print_summary(report, output_path)

            return 0 if report["go_no_go"].startswith("GO") else 1

        except Exception as e:
            logger.error(
                "Stage 0 failed",
                extra={
                    "run_id": run_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            tracker.update_progress(items_failed=1)
            return 1


def _print_summary(report: dict[str, Any], output_path: Path) -> None:
    """Print human-readable summary to console.

    Args:
        report: The assessment report dictionary.
        output_path: Path where the report was saved.
    """
    # Using print() here is intentional for human-readable console output
    # This is separate from structured logging which goes to log files
    summary = report["summary"]
    print(f"\n{'=' * 60}")
    print(f"ASSESSMENT RESULT: {report['go_no_go']}")
    print(f"{'=' * 60}")
    print(f"Files discovered: {summary['total_files_discovered']}")
    print(f"Files sampled: {summary['files_sampled']}")
    print(f"Total messages: {summary['total_messages']}")
    models = ", ".join(summary["models_used"]) or "None"
    print(f"Models found: {models}")
    print("\nRecommendations:")
    for rec in report["recommendations"]:
        print(f"  - {rec}")
    print(f"\nFull report: {output_path}")


if __name__ == "__main__":
    sys.exit(main())
