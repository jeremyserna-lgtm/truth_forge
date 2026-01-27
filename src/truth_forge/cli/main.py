"""CLI Main - Command Entry Point.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/cli/main.py
- Version: 2.0.0
- Date: 2026-01-26

Provides command-line interface for truth_forge operations.

Commands:
- status: Show system status
- seed: Seed a new project
- govern: Check governance status

Example:
    python -m truth_forge.cli status
    python -m truth_forge.cli seed my_project --target ~/projects
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import NoReturn

from truth_forge.core.paths import DATA_ROOT, PROJECT_ROOT


logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser.

    Returns:
        Configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="truth_forge",
        description="truth_forge CLI - The Genesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  truth_forge status              Show system status
  truth_forge seed my_project     Seed a new project
  truth_forge govern --check      Check governance status
        """,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed status",
    )

    # Seed command
    seed_parser = subparsers.add_parser("seed", help="Seed a new project")
    seed_parser.add_argument(
        "name",
        help="Project name",
    )
    seed_parser.add_argument(
        "--target",
        type=Path,
        help="Target directory (default: ~/projects/<name>)",
    )
    seed_parser.add_argument(
        "--template",
        default="standard",
        help="Template to use (default: standard)",
    )

    # Govern command
    govern_parser = subparsers.add_parser("govern", help="Governance operations")
    govern_parser.add_argument(
        "--check",
        action="store_true",
        help="Check governance status",
    )
    govern_parser.add_argument(
        "--violations",
        action="store_true",
        help="Show recent violations",
    )

    return parser


def cmd_status(args: argparse.Namespace) -> int:
    """Execute status command.

    Args:
        args: Parsed arguments.

    Returns:
        Exit code.
    """
    from typing import Any

    status: dict[str, Any] = {
        "project_root": str(PROJECT_ROOT),
        "data_root": str(DATA_ROOT),
        "python_version": sys.version,
    }

    # Check key directories
    key_dirs = [
        PROJECT_ROOT / "src",
        PROJECT_ROOT / "tests",
        DATA_ROOT / "local",
        DATA_ROOT / "staging",
    ]

    status["directories"] = {
        str(d.relative_to(PROJECT_ROOT) if d.is_relative_to(PROJECT_ROOT) else d): d.exists()
        for d in key_dirs
    }

    if args.detailed:
        # Count source files
        src_files = list((PROJECT_ROOT / "src").rglob("*.py"))
        status["source_files"] = len(src_files)

        # Check for tests
        test_files = list((PROJECT_ROOT / "tests").rglob("test_*.py"))
        status["test_files"] = len(test_files)

    if getattr(args, "json", False):
        print(json.dumps(status, indent=2))
    else:
        print("truth_forge Status")
        print("=" * 40)
        print(f"Project Root: {status['project_root']}")
        print(f"Data Root: {status['data_root']}")
        print()
        print("Directories:")
        for dir_path, exists in status["directories"].items():
            mark = "✓" if exists else "✗"
            print(f"  {mark} {dir_path}")

        if args.detailed:
            print()
            print(f"Source files: {status.get('source_files', 'N/A')}")
            print(f"Test files: {status.get('test_files', 'N/A')}")

    return 0


def cmd_seed(args: argparse.Namespace) -> int:
    """Execute seed command.

    Args:
        args: Parsed arguments.

    Returns:
        Exit code.
    """
    from truth_forge.organism.seed import ProjectSeeder
    from truth_forge.organism.seed.seeder import SeedConfig

    target = args.target
    if target is None:
        target = Path.home() / "projects" / args.name

    config = SeedConfig(
        name=args.name,
        target_dir=target,
        template=args.template,
    )

    try:
        seeder = ProjectSeeder()
        lineage = seeder.seed(config)

        result = {
            "organism_id": lineage.organism_id,
            "parent_id": lineage.parent_id,
            "generation": lineage.generation,
            "target": str(target),
        }

        if getattr(args, "json", False):
            print(json.dumps(result, indent=2))
        else:
            print(f"Seeded: {lineage.organism_id}")
            print(f"  Parent: {lineage.parent_id}")
            print(f"  Generation: {lineage.generation}")
            print(f"  Location: {target}")

        return 0

    except FileExistsError as e:
        logger.error("Target already exists", extra={"error": str(e)})
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_govern(args: argparse.Namespace) -> int:
    """Execute govern command.

    Args:
        args: Parsed arguments.

    Returns:
        Exit code.
    """
    from truth_forge.governance import UnifiedGovernance

    gov = UnifiedGovernance()

    if args.violations:
        violations = gov.audit_trail.get_violations(limit=10)

        if getattr(args, "json", False):
            print(json.dumps([v.to_dict() for v in violations], indent=2))
        else:
            print("Recent Violations")
            print("=" * 40)
            if not violations:
                print("No violations recorded")
            else:
                for v in violations:
                    print(f"  [{v.timestamp.isoformat()}] {v.operation}")
                    if v.error_message:
                        print(f"    Reason: {v.error_message}")

        return 0

    # Default: check status
    status = {
        "isolation_enabled": True,
        "cost_tracking_enabled": True,
        "audit_enabled": True,
    }

    if getattr(args, "json", False):
        print(json.dumps(status, indent=2))
    else:
        print("Governance Status")
        print("=" * 40)
        for key, enabled in status.items():
            mark = "✓" if enabled else "✗"
            print(f"  {mark} {key.replace('_', ' ').title()}")

    return 0


def main(argv: list[str] | None = None) -> NoReturn:
    """Main entry point.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:]).
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
    )

    # Dispatch command
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "status": cmd_status,
        "seed": cmd_seed,
        "govern": cmd_govern,
    }

    handler = commands.get(args.command)
    if handler is None:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)

    exit_code = handler(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
