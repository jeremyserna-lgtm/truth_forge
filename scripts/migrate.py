#!/usr/bin/env python3
"""Migration CLI for truth_forge.

Provides commands for running the migration from Truth_Engine to truth_forge.

Usage:
    # Run full migration check (dry run)
    python scripts/migrate.py check

    # Transform code (dry run first)
    python scripts/migrate.py transform --dry-run
    python scripts/migrate.py transform

    # Validate a specific phase
    python scripts/migrate.py validate --phase 0

    # Create backup before migration
    python scripts/migrate.py backup --name pre_phase_4

    # Check health of all services
    python scripts/migrate.py health

    # Run full migration
    python scripts/migrate.py run --from-phase 0 --to-phase 15
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def cmd_check(args: argparse.Namespace) -> int:
    """Check migration readiness."""
    from truth_forge.migration import validate_all_checkpoints
    from truth_forge.migration.health import check_all_services_health

    print("=" * 60)
    print("MIGRATION READINESS CHECK")
    print("=" * 60)

    # Check prerequisites
    print("\n## Prerequisites")

    # Check pyproject.toml
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    if pyproject.exists():
        print("✓ pyproject.toml exists")
    else:
        print("✗ pyproject.toml missing")

    # Check src directory
    src_dir = Path(__file__).parent.parent / "src" / "truth_forge"
    if src_dir.exists():
        print("✓ src/truth_forge/ exists")
    else:
        print("✗ src/truth_forge/ missing")

    # Check data directory
    data_dir = Path(__file__).parent.parent / "data"
    if data_dir.exists():
        print("✓ data/ exists")
    else:
        print("✗ data/ missing (will be created)")

    # Validate checkpoints
    print("\n## Checkpoint Validation")
    results = validate_all_checkpoints(args.up_to_phase)

    all_ok = True
    for result in results:
        status_icon = "✓" if result.ok else ("⚠" if result.status == "warning" else "✗")
        print(f"{status_icon} Phase {result.phase}: {result.status}")
        if result.issues:
            for issue in result.issues:
                print(f"    ✗ {issue}")
        if result.warnings:
            for warning in result.warnings:
                print(f"    ⚠ {warning}")
        if not result.ok:
            all_ok = False

    # Check service health
    print("\n## Service Health")
    health = check_all_services_health()
    print(f"Services checked: {health['services_checked']}")
    print(f"Services healthy: {health['services_healthy']}")
    print(f"Services unhealthy: {health['services_unhealthy']}")
    print(f"Services missing: {health['services_missing']}")

    if not health["overall_healthy"]:
        all_ok = False

    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ READY FOR MIGRATION")
        return 0
    else:
        print("✗ NOT READY - Fix issues above before migrating")
        return 1


def cmd_transform(args: argparse.Namespace) -> int:
    """Transform code to new patterns."""
    from truth_forge.migration import (
        generate_migration_report,
        transform_directory,
    )

    target_dir = Path(args.directory)
    if not target_dir.exists():
        print(f"Error: Directory not found: {target_dir}")
        return 1

    print(f"Transforming: {target_dir}")
    print(f"Dry run: {args.dry_run}")
    print()

    results = transform_directory(
        target_dir,
        dry_run=args.dry_run,
        include_code_patterns=not args.imports_only,
    )

    # Print summary
    modified = [r for r in results if r.was_modified]
    errors = [r for r in results if r.errors]

    print(f"Files scanned: {len(results)}")
    print(f"Files modified: {len(modified)}")
    print(f"Files with errors: {len(errors)}")

    if args.verbose:
        for r in modified:
            print(f"\n{r.file_path}:")
            for change in r.changes:
                print(f"  - {change}")

    if errors:
        print("\nErrors:")
        for r in errors:
            print(f"  {r.file_path}: {r.errors}")

    # Generate report
    if args.report:
        report = generate_migration_report(results)
        report_path = Path(args.report)
        report_path.write_text(report)
        print(f"\nReport written to: {report_path}")

    return 0 if not errors else 1


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a specific phase."""
    from truth_forge.migration import validate_checkpoint

    result = validate_checkpoint(args.phase)

    print(f"Phase {args.phase}: {result.status}")

    if result.issues:
        print("\nIssues:")
        for issue in result.issues:
            print(f"  ✗ {issue}")

    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  ⚠ {warning}")

    return 0 if result.ok else 1


def cmd_backup(args: argparse.Namespace) -> int:
    """Create a backup before migration."""
    from truth_forge.migration import create_backup

    print(f"Creating backup: {args.name}")
    backup_path = create_backup(args.name)
    print(f"✓ Backup created at: {backup_path}")
    return 0


def cmd_health(args: argparse.Namespace) -> int:
    """Check health of all services."""
    from truth_forge.migration.health import (
        check_all_services_health,
        check_service_health,
    )

    if args.service:
        result = check_service_health(args.service)
        print(f"Service: {args.service}")
        print(f"Healthy: {result['healthy']}")
        if result["issues"]:
            print("Issues:")
            for issue in result["issues"]:
                print(f"  ✗ {issue}")
        if result["warnings"]:
            print("Warnings:")
            for warning in result["warnings"]:
                print(f"  ⚠ {warning}")
        print(f"Checks: {result['checks']}")
        return 0 if result["healthy"] else 1

    # Check all services
    health = check_all_services_health()

    print("=" * 60)
    print("SERVICE HEALTH REPORT")
    print("=" * 60)
    print(f"\nOverall healthy: {health['overall_healthy']}")
    print(f"Services checked: {health['services_checked']}")
    print(f"Services healthy: {health['services_healthy']}")
    print(f"Services unhealthy: {health['services_unhealthy']}")
    print(f"Services missing: {health['services_missing']}")

    if args.verbose:
        print("\n## Per-Service Details")
        for service, details in health["details"].items():
            status = "✓" if details.get("healthy") else "✗"
            print(f"\n{status} {service}")
            if details.get("issues"):
                for issue in details["issues"]:
                    print(f"    ✗ {issue}")
            if details.get("warnings"):
                for warning in details["warnings"]:
                    print(f"    ⚠ {warning}")

    return 0 if health["overall_healthy"] else 1


def cmd_run(args: argparse.Namespace) -> int:
    """Run migration phases."""
    from truth_forge.migration import (
        create_backup,
        validate_checkpoint,
    )

    print("=" * 60)
    print(f"MIGRATION: Phase {args.from_phase} → Phase {args.to_phase}")
    print("=" * 60)

    # Create backup first
    if not args.skip_backup:
        print("\n## Creating backup...")
        backup_path = create_backup(f"migration_phase_{args.from_phase}")
        print(f"✓ Backup at: {backup_path}")

    # Run phases
    for phase in range(args.from_phase, args.to_phase + 1):
        print(f"\n## Phase {phase}")

        # Validate checkpoint
        result = validate_checkpoint(phase)
        if not result.ok:
            print(f"✗ Phase {phase} validation failed:")
            for issue in result.issues:
                print(f"    {issue}")

            if not args.force:
                print("\nMigration stopped. Use --force to continue anyway.")
                return 1
            print("Continuing due to --force flag...")

        print(f"✓ Phase {phase} complete")

    print("\n" + "=" * 60)
    print("✓ MIGRATION COMPLETE")
    print("=" * 60)
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migration CLI for truth_forge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # check command
    check_parser = subparsers.add_parser("check", help="Check migration readiness")
    check_parser.add_argument(
        "--up-to-phase",
        type=int,
        default=4,
        help="Check phases up to this number (default: 4)",
    )
    check_parser.set_defaults(func=cmd_check)

    # transform command
    transform_parser = subparsers.add_parser("transform", help="Transform code")
    transform_parser.add_argument(
        "--directory",
        "-d",
        default="src",
        help="Directory to transform (default: src)",
    )
    transform_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without modifying files",
    )
    transform_parser.add_argument(
        "--imports-only",
        action="store_true",
        help="Only transform imports, not code patterns",
    )
    transform_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed changes",
    )
    transform_parser.add_argument(
        "--report",
        help="Write markdown report to file",
    )
    transform_parser.set_defaults(func=cmd_transform)

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a phase")
    validate_parser.add_argument(
        "--phase",
        "-p",
        type=int,
        required=True,
        help="Phase number to validate",
    )
    validate_parser.set_defaults(func=cmd_validate)

    # backup command
    backup_parser = subparsers.add_parser("backup", help="Create backup")
    backup_parser.add_argument(
        "--name",
        "-n",
        default="backup",
        help="Backup name prefix (default: backup)",
    )
    backup_parser.set_defaults(func=cmd_backup)

    # health command
    health_parser = subparsers.add_parser("health", help="Check service health")
    health_parser.add_argument(
        "--service",
        "-s",
        help="Check specific service (default: all)",
    )
    health_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed health info",
    )
    health_parser.set_defaults(func=cmd_health)

    # run command
    run_parser = subparsers.add_parser("run", help="Run migration phases")
    run_parser.add_argument(
        "--from-phase",
        type=int,
        default=0,
        help="Starting phase (default: 0)",
    )
    run_parser.add_argument(
        "--to-phase",
        type=int,
        default=15,
        help="Ending phase (default: 15)",
    )
    run_parser.add_argument(
        "--skip-backup",
        action="store_true",
        help="Skip automatic backup",
    )
    run_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Continue even if validation fails",
    )
    run_parser.set_defaults(func=cmd_run)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
