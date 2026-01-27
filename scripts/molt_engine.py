#!/usr/bin/env python3
"""
Molt Engine - Automated migration deprecation.

THE PATTERN: HOLD → AGENT → HOLD
- HOLD₁: Source folder (original files)
- AGENT: Molt engine (archives, creates stubs)
- HOLD₂: Archive + Stubs (shrunk source)

Pattern carries burden so entities don't have to.
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path


# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from truth_forge.services.factory import get_service


def create_redirect_stub(original_path: Path, new_location: Path, archive_path: Path) -> str:
    """Create a redirect stub for a deprecated file."""
    title = original_path.stem.replace("_", " ").title()
    return f"""# {title}

> **MOVED**: This document has been molted to truth_forge.
>
> **New Location**: [{new_location.name}]({new_location})
>
> **Archive**: [{archive_path.name}]({archive_path})
>
> **Molted On**: {datetime.now().strftime("%Y-%m-%d")}
"""


def molt_folder(source_dir: Path, dest_dir: Path, archive_dir: Path, dry_run: bool = True) -> dict:
    """
    Molt files from source to archive, creating redirect stubs.

    Args:
        source_dir: Original location (e.g., Truth_Engine/docs/04_technical)
        dest_dir: New location (e.g., truth_forge/docs/technical)
        archive_dir: Where to archive originals (e.g., Truth_Engine/docs/archive/molt_YYYY_MM_DD)
        dry_run: If True, only report what would be done

    Returns:
        Statistics dictionary
    """
    stats = {
        "files_found": 0,
        "files_migrated": 0,
        "files_archived": 0,
        "stubs_created": 0,
        "skipped": 0,
        "errors": [],
    }

    if not source_dir.exists():
        stats["errors"].append(f"Source directory does not exist: {source_dir}")
        return stats

    if not dest_dir.exists():
        stats["errors"].append(f"Destination directory does not exist: {dest_dir}")
        return stats

    # Get all markdown files in source
    source_files = list(source_dir.rglob("*.md"))
    stats["files_found"] = len(source_files)

    knowledge_service = get_service("knowledge")
    mediator = get_service("mediator")

    for source_file in source_files:
        # Skip if already a stub (check for "MOVED" marker)
        try:
            content = source_file.read_text(encoding="utf-8")
            if "> **MOVED**:" in content:
                stats["skipped"] += 1
                continue
        except Exception as e:
            stats["errors"].append(f"Error reading {source_file}: {e}")
            continue

        # Exhale knowledge atom
        record = {"content": content, "source": str(source_file)}
        mediator.publish("knowledge.process", record)
        print(f"Inhaled knowledge atom for {source_file}")

        # Calculate relative path from source_dir
        rel_path = source_file.relative_to(source_dir)

        # Check if file exists in destination
        dest_file = dest_dir / rel_path
        if not dest_file.exists():
            # File wasn't migrated - skip
            stats["skipped"] += 1
            continue

        stats["files_migrated"] += 1

        # Calculate archive path
        archive_file = archive_dir / rel_path

        # Calculate relative paths for stub
        # From source_file location to dest_file
        try:
            rel_to_dest = Path("../../../..") / "docs" / dest_file.relative_to(dest_dir.parent)
        except ValueError:
            rel_to_dest = dest_file

        # From source_file location to archive_file
        try:
            rel_to_archive = Path("../archive") / archive_dir.name / rel_path
        except ValueError:
            rel_to_archive = archive_file

        if dry_run:
            print(f"Would archive: {source_file}")
            print(f"  -> Archive: {archive_file}")
            print(f"  -> Stub pointing to: {rel_to_dest}")
            print()
        else:
            try:
                # Create archive directory
                archive_file.parent.mkdir(parents=True, exist_ok=True)

                # Move file to archive
                shutil.move(str(source_file), str(archive_file))
                stats["files_archived"] += 1

                # Create redirect stub
                stub_content = create_redirect_stub(source_file, rel_to_dest, rel_to_archive)
                source_file.write_text(stub_content, encoding="utf-8")
                stats["stubs_created"] += 1

            except Exception as e:
                stats["errors"].append(f"Error processing {source_file}: {e}")

    return stats


def update_archive_index(archive_dir: Path, stats: dict, source_name: str) -> None:
    """Update the archive INDEX.md with molt statistics."""
    index_path = archive_dir.parent / "INDEX.md"

    if not index_path.exists():
        # Create basic index
        content = f"""# Truth_Engine Docs Archive

**Deprecated documentation - molted to truth_forge.**

---

## Archive Structure

| Batch | Date | Files |
|-------|------|-------|
| {archive_dir.name} | {datetime.now().strftime("%Y-%m-%d")} | {stats["files_archived"]} |

---

## Audit Trail

| Date | Action | Source | Files |
|------|--------|--------|-------|
| {datetime.now().strftime("%Y-%m-%d")} | MOLT | {source_name} | {stats["files_archived"]} |
"""
        index_path.write_text(content, encoding="utf-8")
    else:
        # Append to existing index
        content = index_path.read_text(encoding="utf-8")
        audit_entry = f"| {datetime.now().strftime('%Y-%m-%d')} | MOLT | {source_name} | {stats['files_archived']} |\n"

        # Find audit trail section and append
        if "## Audit Trail" in content:
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("| ") and "MOLT" not in line and "Date" not in line:
                    # Insert before this line
                    lines.insert(i, audit_entry.strip())
                    break
            content = "\n".join(lines)

        index_path.write_text(content, encoding="utf-8")


def main():
    # --- Initialize Services ---
    import os

    from truth_forge.core.settings import get_settings

    os.environ["GCP_PROJECT"] = "flash-clover-464719-g1"
    os.environ["ANTHROPIC_API_KEY"] = "sk-mock-anthropic-key"

    settings = get_settings()
    parser = argparse.ArgumentParser(
        description="Molt Engine - Automated migration deprecation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (see what would happen)
  python molt_engine.py --source Truth_Engine/docs/04_technical --dest docs/technical

  # Actually perform the molt
  python molt_engine.py --source Truth_Engine/docs/04_technical --dest docs/technical --execute

  # Molt all docs folders
  python molt_engine.py --all --execute
""",
    )

    parser.add_argument("--source", type=Path, help="Source directory to molt")
    parser.add_argument(
        "--dest", type=Path, help="Destination directory (where files were migrated)"
    )
    parser.add_argument(
        "--archive",
        type=Path,
        help="Archive directory (default: source/../archive/molt_YYYY_MM_DD)",
    )
    parser.add_argument(
        "--execute", action="store_true", help="Actually perform the molt (default is dry run)"
    )
    parser.add_argument("--all", action="store_true", help="Molt all standard docs folders")

    args = parser.parse_args()

    # Base paths
    base = Path(__file__).parent.parent
    truth_engine_docs = base / "Truth_Engine" / "docs"
    truth_forge_docs = base / "docs"

    # Default archive
    today = datetime.now().strftime("%Y_%m_%d")
    default_archive = truth_engine_docs / "archive" / f"molt_{today}"

    if args.all:
        # Molt all standard mappings
        mappings = [
            ("00_onboarding", "guides"),
            ("03_business", "business"),
            ("04_technical", "technical"),
            ("05_personal", "personal"),
            ("06_research", "research"),
            ("08_operations", "operations"),
        ]

        total_stats = {
            "files_found": 0,
            "files_migrated": 0,
            "files_archived": 0,
            "stubs_created": 0,
            "skipped": 0,
            "errors": [],
        }

        for source_name, dest_name in mappings:
            source = truth_engine_docs / source_name
            dest = truth_forge_docs / dest_name
            archive = default_archive / source_name

            if not source.exists():
                print(f"Skipping {source_name} (not found)")
                continue

            print(f"\n{'=' * 60}")
            print(f"Molting: {source_name} -> {dest_name}")
            print(f"{'=' * 60}")

            stats = molt_folder(source, dest, archive, dry_run=not args.execute)

            # Aggregate stats
            for key in total_stats:
                if key == "errors":
                    total_stats[key].extend(stats[key])
                else:
                    total_stats[key] += stats[key]

            print(f"  Found: {stats['files_found']}")
            print(f"  Migrated: {stats['files_migrated']}")
            print(f"  Archived: {stats['files_archived']}")
            print(f"  Stubs: {stats['stubs_created']}")
            print(f"  Skipped: {stats['skipped']}")

            if args.execute and stats["files_archived"] > 0:
                update_archive_index(archive, stats, source_name)

        print(f"\n{'=' * 60}")
        print("TOTAL SUMMARY")
        print(f"{'=' * 60}")
        print(f"  Found: {total_stats['files_found']}")
        print(f"  Migrated: {total_stats['files_migrated']}")
        print(f"  Archived: {total_stats['files_archived']}")
        print(f"  Stubs: {total_stats['stubs_created']}")
        print(f"  Skipped: {total_stats['skipped']}")

        if total_stats["errors"]:
            print(f"\nErrors ({len(total_stats['errors'])}):")
            for err in total_stats["errors"][:10]:
                print(f"  - {err}")

        if not args.execute:
            print("\n** DRY RUN - No changes made. Use --execute to perform molt. **")

    elif args.source and args.dest:
        source = base / args.source if not args.source.is_absolute() else args.source
        dest = base / args.dest if not args.dest.is_absolute() else args.dest
        archive = args.archive or (default_archive / args.source.name)

        print(f"Source: {source}")
        print(f"Destination: {dest}")
        print(f"Archive: {archive}")
        print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")
        print()

        stats = molt_folder(source, dest, archive, dry_run=not args.execute)

        print("\nSummary:")
        print(f"  Found: {stats['files_found']}")
        print(f"  Migrated: {stats['files_migrated']}")
        print(f"  Archived: {stats['files_archived']}")
        print(f"  Stubs: {stats['stubs_created']}")
        print(f"  Skipped: {stats['skipped']}")

        if stats["errors"]:
            print(f"\nErrors ({len(stats['errors'])}):")
            for err in stats["errors"]:
                print(f"  - {err}")

        if args.execute and stats["files_archived"] > 0:
            update_archive_index(archive, stats, str(args.source))

        if not args.execute:
            print("\n** DRY RUN - No changes made. Use --execute to perform molt. **")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
    # After all files have been inhaled, trigger the sync to process the batch.
    from truth_forge.services.factory import get_service

    knowledge_service = get_service("knowledge")
    knowledge_service.sync()
