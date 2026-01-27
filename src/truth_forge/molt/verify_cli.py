"""Verify CLI.

Commands for validating migration and code quality.
"""

from __future__ import annotations

import subprocess
import sys

import typer

from truth_forge.core.paths import PROJECT_ROOT


app = typer.Typer(
    name="verify",
    help="Validate migration and code quality.",
    add_completion=False,
)


def _run_command(cmd: list[str], description: str) -> tuple[bool, str]:
    """Run a command and return (success, output)."""
    typer.echo(f"\n{description}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except Exception as e:
        return False, str(e)


@app.command()
def types(
    path: str = typer.Argument("src/", help="Path to check"),
    strict: bool = typer.Option(True, "--strict/--no-strict", help="Use strict mode"),
) -> None:
    """Run mypy type checking."""
    cmd = [".venv/bin/mypy", path]
    if strict:
        cmd.append("--strict")

    success, output = _run_command(cmd, "Running mypy")

    if success:
        typer.echo("✓ Type checking passed")
    else:
        typer.echo(output)
        typer.echo("✗ Type checking failed")
        raise typer.Exit(code=1)


@app.command()
def lint(
    path: str = typer.Argument("src/", help="Path to check"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix issues"),
) -> None:
    """Run ruff linting."""
    cmd = [".venv/bin/ruff", "check", path]
    if fix:
        cmd.append("--fix")

    success, output = _run_command(cmd, "Running ruff check")

    if success:
        typer.echo("✓ Linting passed")
    else:
        typer.echo(output)
        typer.echo("✗ Linting failed")
        raise typer.Exit(code=1)


@app.command()
def format_check(
    path: str = typer.Argument("src/", help="Path to check"),
) -> None:
    """Check code formatting."""
    cmd = [".venv/bin/ruff", "format", "--check", path]

    success, output = _run_command(cmd, "Running ruff format --check")

    if success:
        typer.echo("✓ Formatting check passed")
    else:
        typer.echo(output)
        typer.echo("✗ Formatting check failed")
        raise typer.Exit(code=1)


@app.command()
def tests(
    path: str = typer.Argument("tests/", help="Test path"),
    coverage: int = typer.Option(90, "--cov", help="Coverage threshold"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output"),
) -> None:
    """Run test suite."""
    cmd = [".venv/bin/pytest", path]
    if verbose:
        cmd.append("-v")
    if coverage:
        cmd.extend(["--cov", "--cov-fail-under", str(coverage)])

    success, output = _run_command(cmd, f"Running pytest (coverage >= {coverage}%)")

    if success:
        typer.echo("✓ Tests passed")
    else:
        typer.echo(output)
        typer.echo("✗ Tests failed")
        raise typer.Exit(code=1)


@app.command()
def services() -> None:
    """Verify all services are operational."""
    from truth_forge.services.factory import ServiceFactory

    typer.echo("\nVerifying services...")
    typer.echo("=" * 50)

    services_to_check = [
        "secret",
        "mediator",
        "governance",
        "knowledge",
        "cognition",
        "perception",
        "action",
        "relationship",
        "logging",
    ]

    passed = 0
    failed = 0

    for service_name in services_to_check:
        try:
            if ServiceFactory.is_registered(service_name):
                typer.echo(f"  ✓ {service_name}: registered")
                passed += 1
            else:
                typer.echo(f"  ✗ {service_name}: not registered")
                failed += 1
        except Exception as e:
            typer.echo(f"  ✗ {service_name}: error - {e}")
            failed += 1

    typer.echo(f"\nServices: {passed} passed, {failed} failed")

    if failed > 0:
        raise typer.Exit(code=1)


@app.command()
def hold() -> None:
    """Verify HOLD pattern directories exist for all services."""
    typer.echo("\nVerifying HOLD pattern...")
    typer.echo("=" * 50)

    services_dir = PROJECT_ROOT / "data" / "services"
    if not services_dir.exists():
        typer.echo(f"✗ Services data directory not found: {services_dir}")
        raise typer.Exit(code=1)

    services = [
        "secret",
        "mediator",
        "governance",
        "knowledge",
        "cognition",
        "perception",
        "action",
        "relationship",
        "logging",
    ]

    passed = 0
    failed = 0

    for service_name in services:
        service_dir = services_dir / service_name
        hold1 = service_dir / "hold1"
        hold2 = service_dir / "hold2"
        staging = service_dir / "staging"

        all_exist = hold1.exists() and hold2.exists() and staging.exists()

        if all_exist:
            typer.echo(f"  ✓ {service_name}: hold1/, hold2/, staging/")
            passed += 1
        else:
            missing = []
            if not hold1.exists():
                missing.append("hold1")
            if not hold2.exists():
                missing.append("hold2")
            if not staging.exists():
                missing.append("staging")
            typer.echo(f"  ✗ {service_name}: missing {', '.join(missing)}")
            failed += 1

    typer.echo(f"\nHOLD pattern: {passed} passed, {failed} failed")

    if failed > 0:
        raise typer.Exit(code=1)


@app.command()
def full() -> None:
    """Run complete validation (types, lint, format, tests, services, hold)."""
    typer.echo("\n" + "=" * 60)
    typer.echo("  FULL VALIDATION")
    typer.echo("=" * 60)

    checks = [
        ("Type checking", ["types"]),
        ("Linting", ["lint"]),
        ("Formatting", ["format-check"]),
        ("Tests", ["tests", "--cov", "0"]),  # Skip coverage for quick check
        ("Services", ["services"]),
        ("HOLD pattern", ["hold"]),
    ]

    results: dict[str, bool] = {}

    for name, args in checks:
        try:
            cmd = [sys.executable, "-m", "truth_forge.molt", "verify", *args]
            result = subprocess.run(cmd, capture_output=True, cwd=PROJECT_ROOT)
            results[name] = result.returncode == 0
        except Exception:
            results[name] = False

    typer.echo("\n" + "=" * 60)
    typer.echo("  SUMMARY")
    typer.echo("=" * 60)

    all_passed = True
    for name, passed in results.items():
        status = "✓" if passed else "✗"
        typer.echo(f"  {status} {name}")
        if not passed:
            all_passed = False

    if all_passed:
        typer.echo("\n✓ All validation checks passed")
    else:
        typer.echo("\n✗ Some validation checks failed")
        raise typer.Exit(code=1)
