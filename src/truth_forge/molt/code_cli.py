"""Code Molt CLI.

Commands for code transformation during migration.
"""

from __future__ import annotations

from pathlib import Path

import typer
import yaml

from truth_forge.core.paths import PROJECT_ROOT
from truth_forge.molt.code_molt import CodeMoltEngine, CodeMoltResult, TransformConfig


app = typer.Typer(
    name="code",
    help="Transform and migrate code.",
    add_completion=False,
)


def _load_transform_config() -> TransformConfig:
    """Load transform configuration from molt.yaml or use defaults."""
    molt_file = PROJECT_ROOT / "molt.yaml"

    if molt_file.exists():
        with open(molt_file) as f:
            data = yaml.safe_load(f)

        code_config = data.get("code", {})
        transforms = code_config.get("transforms", {})

        if transforms:
            return TransformConfig.from_dict(transforms)

    return TransformConfig.default()


def _print_result(result: CodeMoltResult, dry_run: bool) -> None:
    """Print molt result summary."""
    prefix = "[DRY RUN] " if dry_run else ""
    typer.echo(f"\n{prefix}Molt Result: {result.source_name}")
    typer.echo("=" * 50)
    typer.echo(f"  Files found:       {result.files_found}")
    typer.echo(f"  Files transformed: {result.files_transformed}")
    typer.echo(f"  Files unchanged:   {result.files_unchanged}")

    if result.errors:
        typer.echo(f"\n  Errors ({len(result.errors)}):")
        for error in result.errors:
            typer.echo(f"    - {error}")

    if result.success:
        typer.echo("\n✓ Success")
    else:
        typer.echo("\n✗ Failed")


@app.command()
def transform(
    source: str = typer.Argument(..., help="Source file or directory"),
    dest: str = typer.Argument(..., help="Destination file or directory"),
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Simulate or execute"),
    archive: str = typer.Option(None, "--archive", "-a", help="Archive directory for originals"),
) -> None:
    """Transform code from source to destination."""
    source_path = Path(source)
    dest_path = Path(dest)
    archive_path = Path(archive) if archive else None

    config = _load_transform_config()
    engine = CodeMoltEngine(config)

    if source_path.is_file():
        changed, counts = engine.transform_file(
            source_file=source_path,
            dest_file=dest_path,
            archive_dir=archive_path,
            dry_run=dry_run,
        )
        prefix = "[DRY RUN] " if dry_run else ""
        if changed:
            typer.echo(f"{prefix}Transformed: {source_path.name}")
            typer.echo(f"  Imports: {counts.get('imports', 0)}")
            typer.echo(f"  Paths:   {counts.get('paths', 0)}")
            typer.echo(f"  Env:     {counts.get('env', 0)}")
        else:
            typer.echo(f"{prefix}No changes: {source_path.name}")

    elif source_path.is_dir():
        result = engine.molt_directory(
            source_dir=source_path,
            dest_dir=dest_path,
            archive_dir=archive_path,
            dry_run=dry_run,
        )
        _print_result(result, dry_run)

    else:
        typer.echo(f"Error: Source not found: {source}")
        raise typer.Exit(code=1)


@app.command()
def phase(
    phase_number: int = typer.Argument(..., help="Phase number to execute"),
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Simulate or execute"),
) -> None:
    """Execute code molt for a specific migration phase."""
    molt_file = PROJECT_ROOT / "molt.yaml"

    if not molt_file.exists():
        typer.echo("Error: molt.yaml not found in project root")
        raise typer.Exit(code=1)

    with open(molt_file) as f:
        data = yaml.safe_load(f)

    # Find phase configuration
    phases = data.get("code", {}).get("phases", [])
    phase_config = None

    for p in phases:
        if p.get("phase") == phase_number:
            phase_config = p
            break

    if not phase_config:
        typer.echo(f"Error: Phase {phase_number} not found in molt.yaml")
        typer.echo(f"Available phases: {[p.get('phase') for p in phases]}")
        raise typer.Exit(code=1)

    typer.echo(f"\nExecuting Phase {phase_number}: {phase_config.get('name', 'unnamed')}")
    typer.echo("=" * 50)

    config = _load_transform_config()
    engine = CodeMoltEngine(config)

    result = engine.molt_phase(
        phase_config=phase_config,
        base_path=PROJECT_ROOT,
        dry_run=dry_run,
    )

    _print_result(result, dry_run)


@app.command()
def show_rules() -> None:
    """Show the current transformation rules."""
    config = _load_transform_config()

    typer.echo("\n## Import Rules")
    for rule in config.import_rules:
        regex_flag = " (regex)" if rule.is_regex else ""
        typer.echo(f"  {rule.pattern} → {rule.replacement}{regex_flag}")

    typer.echo("\n## Path Rules")
    for rule in config.path_rules:
        regex_flag = " (regex)" if rule.is_regex else ""
        typer.echo(f"  {rule.pattern} → {rule.replacement}{regex_flag}")

    typer.echo("\n## Environment Rules")
    for rule in config.env_rules:
        regex_flag = " (regex)" if rule.is_regex else ""
        typer.echo(f"  {rule.pattern} → {rule.replacement}{regex_flag}")
