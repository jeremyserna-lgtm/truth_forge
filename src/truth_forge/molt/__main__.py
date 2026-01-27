"""Molt CLI.

Unified migration and code transformation tool for truth_forge.

Usage:
    python -m truth_forge.molt service generate knowledge
    python -m truth_forge.molt code transform src/ dest/
    python -m truth_forge.molt verify full
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer


sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from truth_forge.molt import code_cli, service, verify_cli


app = typer.Typer(
    name="molt",
    help="Unified migration and code transformation tool for truth_forge.",
    add_completion=False,
)

# Add subcommands
app.add_typer(service.app, name="service")
app.add_typer(code_cli.app, name="code")
app.add_typer(verify_cli.app, name="verify")


@app.command()
def status() -> None:
    """Show molt status and available commands."""
    typer.echo("\n" + "=" * 60)
    typer.echo("  MOLT - Migration & Transformation Tool")
    typer.echo("=" * 60)

    typer.echo("\nAvailable commands:")
    typer.echo("  molt service generate <name>   - Generate new service")
    typer.echo("  molt service migrate <name>    - Analyze legacy service")
    typer.echo("  molt service migrate --all     - Analyze all services")
    typer.echo("")
    typer.echo("  molt code transform <src> <dest>  - Transform code")
    typer.echo("  molt code phase <N>               - Execute migration phase")
    typer.echo("  molt code show-rules              - Show transformation rules")
    typer.echo("")
    typer.echo("  molt verify types [path]       - Run mypy")
    typer.echo("  molt verify lint [path]        - Run ruff check")
    typer.echo("  molt verify format-check       - Check formatting")
    typer.echo("  molt verify tests [path]       - Run pytest")
    typer.echo("  molt verify services           - Check service registration")
    typer.echo("  molt verify hold               - Check HOLD directories")
    typer.echo("  molt verify full               - Run all checks")


@app.command()
def history() -> None:
    """Show molt operation history."""
    from truth_forge.core.paths import PROJECT_ROOT
    from truth_forge.molt.tracking import MoltTracker

    history_file = PROJECT_ROOT / ".molt" / "history.jsonl"
    tracker = MoltTracker(history_file)

    records = tracker.get_history()
    summary = tracker.get_summary()

    typer.echo("\n" + "=" * 60)
    typer.echo("  MOLT HISTORY")
    typer.echo("=" * 60)

    typer.echo(f"\nTotal operations: {summary['total_operations']}")
    typer.echo(f"  Executed: {summary['executed_operations']}")
    typer.echo(f"  Dry runs: {summary['dry_runs']}")
    typer.echo(f"  Files archived: {summary['total_files_archived']}")
    typer.echo(f"  Errors: {summary['total_errors']}")

    if records:
        typer.echo("\nRecent operations:")
        for record in records[-5:]:
            status = "dry-run" if record.dry_run else "executed"
            typer.echo(f"  [{record.timestamp[:19]}] {record.source_name} ({status})")
            typer.echo(
                f"    Files: {record.files_migrated} migrated, {record.files_archived} archived"
            )


def main() -> None:
    """Typer app runner."""
    app()


if __name__ == "__main__":
    main()
