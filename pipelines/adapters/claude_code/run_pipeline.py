#!/usr/bin/env python3
"""Run the complete Claude Code pipeline.

This script runs all 16 stages of the Universal Pipeline Pattern.

Usage:
    python run_pipeline.py
    python run_pipeline.py --stages 0-4  # Run specific stages
    python run_pipeline.py --test        # Run on test data
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from pipelines.core.runner import PipelineRunner, load_adapter
from pipelines.adapters.claude_code.stages import STAGE_REGISTRY


def setup_logging(verbose: bool = False) -> None:
    """Configure logging.
    
    Args:
        verbose: Enable debug logging.
    """
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main() -> int:
    """Run the pipeline.
    
    Returns:
        Exit code (0 = success, 1 = failure).
    """
    parser = argparse.ArgumentParser(description="Run Claude Code pipeline")
    parser.add_argument(
        "--stages",
        type=str,
        help="Stages to run (e.g., '0-4' or '5,6,7')",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run on test data",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose logging",
    )
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    # Load pipeline configuration
    try:
        config = load_adapter("claude_code")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    # Create runner and register stages
    runner = PipelineRunner(config)
    for stage_name, stage_class in STAGE_REGISTRY.items():
        runner.register_stage(stage_name, stage_class)
    
    # Determine stages to run
    stages_to_run = None
    if args.stages:
        if "-" in args.stages:
            # Range: 0-4
            start, end = map(int, args.stages.split("-"))
            stages_to_run = [f"stage_{i}" for i in range(start, end + 1)]
        else:
            # List: 5,6,7
            stages_to_run = [f"stage_{s.strip()}" for s in args.stages.split(",")]
    
    # Run pipeline
    if stages_to_run:
        result = runner.run_stages(stages_to_run)
    else:
        result = runner.run()
    
    # Print results
    print("\n" + "=" * 60)
    print(f"Pipeline: {result.pipeline_name}")
    print(f"Status: {result.status}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    print("\nStage Results:")
    print("-" * 60)
    
    for stage_name, stage_result in result.stages.items():
        status_symbol = "✓" if stage_result.status == "success" else "✗"
        print(f"{status_symbol} {stage_name}: {stage_result.status}")
        if stage_result.records_in > 0:
            print(f"   → {stage_result.records_in} in, {stage_result.records_out} out")
        if stage_result.errors > 0:
            print(f"   ⚠ {stage_result.errors} errors")
    
    print("=" * 60)
    
    return 0 if result.status == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
