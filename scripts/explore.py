#!/usr/bin/env python3
"""Autonomous Explorer CLI - Data exploration with cognitive architecture.

This script runs the ExplorerService for autonomous exploration of
spine data with full cognitive architecture integration:
- Total Resonance tracking (ontological alignment)
- Struggle Filter (keep swimming, discard drowning)
- Stage 5 cognitive compliance
- InsightAtom generation

Usage:
    python scripts/explore.py                              # Default exploration (5 iterations)
    python scripts/explore.py --iterations 10              # More iterations
    python scripts/explore.py --focus "entity patterns"    # Focus exploration
    python scripts/explore.py --depth deep                 # Deep exploration
    python scripts/explore.py --json                       # JSON output

MOLT LINEAGE:
- Source: New creation for ExplorerService CLI
- Version: 1.0.0
- Date: 2026-02-01
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add src to path for development
TRUTH_FORGE_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(TRUTH_FORGE_ROOT / "src"))


def print_banner() -> None:
    """Print Explorer banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                               ║
    ║   ███████╗██╗  ██╗██████╗ ██╗      ██████╗ ██████╗ ███████╗██████╗            ║
    ║   ██╔════╝╚██╗██╔╝██╔══██╗██║     ██╔═══██╗██╔══██╗██╔════╝██╔══██╗           ║
    ║   █████╗   ╚███╔╝ ██████╔╝██║     ██║   ██║██████╔╝█████╗  ██████╔╝           ║
    ║   ██╔══╝   ██╔██╗ ██╔═══╝ ██║     ██║   ██║██╔══██╗██╔══╝  ██╔══██╗           ║
    ║   ███████╗██╔╝ ██╗██║     ███████╗╚██████╔╝██║  ██║███████╗██║  ██║           ║
    ║   ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝           ║
    ║                                                                               ║
    ║   Autonomous Data Exploration with Cognitive Architecture                     ║
    ║   Model: qwen2.5:14b | Context: 500K | Pattern: HOLD -> AGENT -> HOLD         ║
    ║                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_progress(iteration: int, total: int, finding_count: int) -> None:
    """Print progress indicator."""
    progress = (iteration + 1) / total
    bar_len = 40
    filled = int(bar_len * progress)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"\r  [{bar}] {iteration + 1}/{total} | Findings: {finding_count}", end="", flush=True)


def print_findings_summary(findings: list[dict], limit: int = 10) -> None:
    """Print findings summary."""
    print(f"\n  Findings ({len(findings)} total):")

    # Group by significance
    high = [f for f in findings if f.get("significance") == "high"]
    medium = [f for f in findings if f.get("significance") == "medium"]
    low = [f for f in findings if f.get("significance") == "low"]

    print(f"    HIGH: {len(high)} | MEDIUM: {len(medium)} | LOW: {len(low)}")

    # Show top findings
    top_findings = high[:limit] if high else (medium[:limit] if medium else low[:limit])

    if top_findings:
        print("\n  Top Findings:")
        for i, finding in enumerate(top_findings, 1):
            tool = finding.get("tool_name", "unknown")
            analysis = finding.get("analysis", "")[:100]
            stage = finding.get("cognitive_stage", "?")
            emotion = finding.get("emotional_state", "?")
            print(f"    {i}. [{tool}] Stage {stage} / {emotion}")
            print(f"       {analysis}...")


def print_resonance_metrics(metrics: dict) -> None:
    """Print Total Resonance metrics."""
    score = metrics.get("total_resonance_score", 0.0)
    stage_5 = metrics.get("stage_5_findings", 0)
    total = metrics.get("total_findings", 0)
    manifestations = metrics.get("manifestation_count", 0)
    surplus = metrics.get("surplus_value_count", 0)

    # Resonance bar
    bar_len = 30
    filled = int(bar_len * score)
    bar = "█" * filled + "░" * (bar_len - filled)

    exist_now = "YES" if metrics.get("is_exist_now_ready", False) else "NO"

    print(f"""
  ╔═══════════════════════════════════════════════════════════════╗
  ║                    TOTAL RESONANCE                             ║
  ╠═══════════════════════════════════════════════════════════════╣
  ║  Score: [{bar}] {score:.1%}    ║
  ║                                                               ║
  ║  Stage 5 Findings:    {stage_5:>4} / {total:<4}                            ║
  ║  Manifestations:      {manifestations:>4}                                   ║
  ║  Surplus Value:       {surplus:>4}                                   ║
  ║                                                               ║
  ║  Exist-Now Ready:     {exist_now:<4}                                   ║
  ╚═══════════════════════════════════════════════════════════════╝
""")


def print_patterns(patterns: list[dict]) -> None:
    """Print discovered patterns."""
    if not patterns:
        print("\n  No patterns discovered.")
        return

    print(f"\n  Patterns Discovered ({len(patterns)}):")
    for i, pattern in enumerate(patterns, 1):
        name = pattern.get("name", "unnamed")
        confidence = pattern.get("confidence", 0.0)
        description = pattern.get("description", "")[:80]
        print(f"    {i}. {name} (confidence: {confidence:.0%})")
        print(f"       {description}...")


def print_report(report: dict, verbose: bool = False) -> None:
    """Print exploration report."""
    print("\n" + "=" * 70)
    print("  EXPLORATION COMPLETE")
    print("=" * 70)

    # Basic stats
    session_id = report.get("session_id", "unknown")[:16]
    iterations = report.get("iterations_completed", 0)
    duration = report.get("duration_seconds", 0)
    cost = report.get("total_cost", 0)
    findings_count = len(report.get("findings", []))
    patterns_count = len(report.get("patterns_discovered", []))

    print(f"""
  Session:     {session_id}...
  Iterations:  {iterations}
  Duration:    {duration:.1f}s
  Cost:        ${cost:.4f}
  Findings:    {findings_count}
  Patterns:    {patterns_count}
""")

    # Resonance metrics
    resonance = report.get("resonance_metrics", {})
    if resonance:
        print_resonance_metrics(resonance)

    # Findings summary
    if verbose:
        print_findings_summary(report.get("findings", []))

    # Patterns
    if verbose and report.get("patterns_discovered"):
        print_patterns(report.get("patterns_discovered", []))

    # Synthesis
    synthesis = report.get("synthesis", "")
    if synthesis:
        print("\n  Synthesis:")
        print(f"    {synthesis[:200]}...")

    # Recommendations
    recommendations = report.get("recommendations", [])
    if recommendations:
        print("\n  Recommendations:")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"    {i}. {rec[:60]}...")


def run_exploration(
    iterations: int,
    focus_area: str | None,
    depth: str,
    json_output: bool,
    verbose: bool,
) -> int:
    """Run autonomous exploration."""
    from truth_forge.services.factory import get_service
    from truth_forge.services.explorer.models import ExplorationConfig, ExplorationDepth

    if not json_output:
        print_banner()
        print(f"\n  Starting exploration...")
        print(f"    Iterations: {iterations}")
        print(f"    Depth: {depth}")
        if focus_area:
            print(f"    Focus: {focus_area}")
        print()

    # Create config
    config = ExplorationConfig(
        iterations=iterations,
        focus_area=focus_area,
        depth=ExplorationDepth(depth),
    )

    # Get explorer service
    try:
        explorer = get_service("explorer")
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e), "success": False}))
        else:
            print(f"\n  ERROR: Failed to initialize ExplorerService: {e}")
        return 1

    # Run exploration
    try:
        report = explorer.explore(config)

        if json_output:
            print(json.dumps(report.model_dump(), indent=2, default=str))
        else:
            print_report(report.model_dump(), verbose=verbose)

        return 0

    except KeyboardInterrupt:
        if not json_output:
            print("\n\n  Exploration interrupted by user.")
        return 130

    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e), "success": False}))
        else:
            print(f"\n  ERROR: Exploration failed: {e}")
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous Explorer - Data exploration with cognitive architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/explore.py                           # Default (5 iterations, medium depth)
  python scripts/explore.py -i 10                     # 10 iterations
  python scripts/explore.py -f "entity patterns"     # Focus on entity patterns
  python scripts/explore.py -d deep -i 20            # Deep exploration, 20 iterations
  python scripts/explore.py --json                   # JSON output for pipelines

Cognitive Architecture:
  Total Resonance:   Tracks ontological alignment (0.0 - 1.0)
  Struggle Filter:   Keeps SWIMMING, discards DROWNING, prioritizes SURPLUS
  Stage 5:           Self-transforming baseline (not remarkable)
  InsightAtom:       Atomic knowledge units for pipeline integration
        """,
    )

    parser.add_argument(
        "-i", "--iterations",
        type=int,
        default=5,
        help="Number of exploration iterations (default: 5)",
    )
    parser.add_argument(
        "-f", "--focus",
        type=str,
        default=None,
        help="Focus area for exploration",
    )
    parser.add_argument(
        "-d", "--depth",
        choices=["shallow", "medium", "deep"],
        default="medium",
        help="Exploration depth (default: medium)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (for pipeline integration)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output with findings details",
    )

    args = parser.parse_args()

    return run_exploration(
        iterations=args.iterations,
        focus_area=args.focus,
        depth=args.depth,
        json_output=args.json,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    sys.exit(main())
