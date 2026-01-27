"""Enrichment orchestrator - Coordinate running multiple enrichment scripts.

THE PATTERN:
- HOLD₁: Enrichment scripts and configuration
- AGENT: Orchestrator (coordinates execution)
- HOLD₂: Complete enrichment pipeline execution

Purpose: Coordinate running multiple enrichment scripts in correct order with
dependency management, progress tracking, and error handling.
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)

# Enrichment phases and dependencies
ENRICHMENT_PHASES = {
    "p0": [
        "enrichment_triage",
        "enrichment_coverage_expander",
    ],
    "p1": [
        "enrichment_textblob",
        "enrichment_textstat",
        "enrichment_nrclx",
        "enrichment_goemotions",
        "enrichment_roberta_hate",
    ],
    "p2": [
        "enrichment_keybert",
        "enrichment_bertopic",
        "enrichment_clustering",
        "enrichment_taxonomy",
    ],
    "p3": [
        "enrichment_claims",
        "enrichment_resonance",
        "enrichment_fine_grained",
        "enrichment_quality",
    ],
}

# Enrichment groups
ENRICHMENT_GROUPS = {
    "a": ["enrichment_textblob", "enrichment_textstat"],  # CPU-only
    "b": ["enrichment_goemotions", "enrichment_roberta_hate"],  # Classification
    "c": ["enrichment_keybert", "enrichment_bertopic"],  # Embedding-based
}

# Dependencies (script needs these to run)
DEPENDENCIES = {
    "enrichment_keybert": ["sentence_embedding"],  # Needs embeddings
    "enrichment_bertopic": ["sentence_embedding"],  # Needs embeddings
    "enrichment_clustering": ["sentence_embedding"],  # Needs embeddings
    "enrichment_resonance": ["sentence_embedding"],  # Needs embeddings
}


def run_enrichment_script(script_name: str, args: list[str] | None = None) -> dict[str, Any]:
    """Run a single enrichment script.

    Args:
        script_name: Name of enrichment script (without .py)
        args: Additional arguments to pass to script

    Returns:
        Dictionary with execution results
    """
    script_path = Path(__file__).parent / f"{script_name}.py"

    if not script_path.exists():
        logger.error(f"Script not found: {script_path}")
        return {"success": False, "error": f"Script not found: {script_name}"}

    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    logger.info(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600,  # 1 hour timeout
        )

        if result.returncode == 0:
            logger.info(f"✅ {script_name} completed successfully")
            return {
                "success": True,
                "script": script_name,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        else:
            logger.error(f"❌ {script_name} failed with return code {result.returncode}")
            logger.error(f"Stderr: {result.stderr}")
            return {
                "success": False,
                "script": script_name,
                "returncode": result.returncode,
                "stderr": result.stderr,
            }

    except subprocess.TimeoutExpired:
        logger.error(f"❌ {script_name} timed out after 1 hour")
        return {"success": False, "script": script_name, "error": "timeout"}
    except Exception as e:
        logger.error(f"❌ {script_name} raised exception: {e}")
        return {"success": False, "script": script_name, "error": str(e)}


def run_phase(phase: str, common_args: list[str] | None = None) -> dict[str, Any]:
    """Run all scripts in a phase.

    Args:
        phase: Phase name (p0, p1, p2, p3)
        common_args: Common arguments for all scripts

    Returns:
        Dictionary with phase execution results
    """
    if phase not in ENRICHMENT_PHASES:
        return {"success": False, "error": f"Unknown phase: {phase}"}

    scripts = ENRICHMENT_PHASES[phase]
    results = []

    logger.info(f"Running phase {phase} with {len(scripts)} scripts...")

    for script in scripts:
        result = run_enrichment_script(script, common_args)
        results.append(result)

        if not result["success"]:
            logger.warning(f"Script {script} failed, continuing with next script...")

    success_count = sum(1 for r in results if r.get("success"))
    logger.info(f"Phase {phase} complete: {success_count}/{len(scripts)} scripts succeeded")

    return {
        "phase": phase,
        "scripts": scripts,
        "results": results,
        "success_count": success_count,
        "total_count": len(scripts),
    }


def run_group(group: str, common_args: list[str] | None = None) -> dict[str, Any]:
    """Run all scripts in an enrichment group.

    Args:
        group: Group name (a, b, c)
        common_args: Common arguments for all scripts

    Returns:
        Dictionary with group execution results
    """
    if group not in ENRICHMENT_GROUPS:
        return {"success": False, "error": f"Unknown group: {group}"}

    scripts = ENRICHMENT_GROUPS[group]
    results = []

    logger.info(f"Running group {group} with {len(scripts)} scripts...")

    for script in scripts:
        result = run_enrichment_script(script, common_args)
        results.append(result)

    success_count = sum(1 for r in results if r.get("success"))
    logger.info(f"Group {group} complete: {success_count}/{len(scripts)} scripts succeeded")

    return {
        "group": group,
        "scripts": scripts,
        "results": results,
        "success_count": success_count,
        "total_count": len(scripts),
    }


def run_all(common_args: list[str] | None = None) -> dict[str, Any]:
    """Run all phases in sequence.

    Args:
        common_args: Common arguments for all scripts

    Returns:
        Dictionary with all phase results
    """
    all_results = {}

    for phase in ["p0", "p1", "p2", "p3"]:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Starting Phase {phase.upper()}")
        logger.info(f"{'=' * 60}\n")

        phase_result = run_phase(phase, common_args)
        all_results[phase] = phase_result

        if phase_result.get("success_count", 0) < phase_result.get("total_count", 1):
            logger.warning(f"Phase {phase} had failures. Review results before proceeding.")

    total_success = sum(r.get("success_count", 0) for r in all_results.values())
    total_scripts = sum(r.get("total_count", 0) for r in all_results.values())

    logger.info(f"\n{'=' * 60}")
    logger.info(f"All phases complete: {total_success}/{total_scripts} scripts succeeded")
    logger.info(f"{'=' * 60}\n")

    return {
        "phases": all_results,
        "total_success": total_success,
        "total_scripts": total_scripts,
    }


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Enrichment orchestrator - Coordinate enrichment script execution"
    )
    parser.add_argument(
        "--phase",
        type=str,
        choices=["p0", "p1", "p2", "p3"],
        help="Run specific phase only",
    )
    parser.add_argument(
        "--group",
        type=str,
        choices=["a", "b", "c"],
        help="Run specific enrichment group only",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all phases in sequence",
    )
    parser.add_argument(
        "--script",
        type=str,
        help="Run specific script only",
    )
    parser.add_argument(
        "--common-args",
        type=str,
        help="Common arguments to pass to all scripts (space-separated)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be run without executing",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Parse common args
    common_args = []
    if args.common_args:
        common_args = args.common_args.split()

    if args.dry_run:
        common_args.append("--dry-run")

    # Execute based on mode
    if args.script:
        result = run_enrichment_script(args.script, common_args)
        if not result.get("success"):
            sys.exit(1)

    elif args.group:
        result = run_group(args.group, common_args)
        if result.get("success_count", 0) < result.get("total_count", 1):
            sys.exit(1)

    elif args.phase:
        result = run_phase(args.phase, common_args)
        if result.get("success_count", 0) < result.get("total_count", 1):
            sys.exit(1)

    elif args.all:
        result = run_all(common_args)
        if result.get("total_success", 0) < result.get("total_scripts", 1):
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
