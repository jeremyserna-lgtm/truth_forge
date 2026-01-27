"""Molt Service CLI.

Commands for migrating and scaffolding services.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Any

import typer
import yaml


sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from truth_forge.core.paths import PROJECT_ROOT


app = typer.Typer(
    name="service",
    help="Migrate and scaffold services.",
    add_completion=False,
)

SERVICE_TEMPLATE = '''"""${service_title} Service.

Implements HOLD pattern for ${service_name} domain.
"""

from __future__ import annotations

from typing import Any

from truth_forge.services.base import BaseService
from truth_forge.services.factory import register_service


@register_service()
class ${class_name}(BaseService):
    """${service_title} service implementing HOLD pattern."""

    service_name = "${service_name}"

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Process a single record (AGENT logic)."""
        return {
            **record,
            "_processed": True,
            "_service": self.service_name,
        }

    def create_schema(self) -> str:
        """Create DuckDB schema for HOLD₂."""
        return """
            CREATE TABLE IF NOT EXISTS ${service_name}_records (
                id VARCHAR PRIMARY KEY,
                data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
'''


def load_molt_config() -> dict[str, Any]:
    """Load the molt.yaml configuration file."""
    molt_file = PROJECT_ROOT / "molt.yaml"
    if not molt_file.exists():
        typer.echo("molt.yaml not found in project root.", err=True)
        raise typer.Exit(code=1)
    with open(molt_file) as f:
        config = yaml.safe_load(f)
        if not isinstance(config, dict):
            typer.echo("Invalid YAML format in molt.yaml; expected a dictionary.", err=True)
            raise typer.Exit(code=1)
        return config


@app.command()
def generate(
    service_name: str = typer.Argument(..., help="Name of the service (e.g., 'knowledge')"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file"),
) -> None:
    """Generate a new service from a template."""
    service_name_lower = service_name.lower()
    class_name = "".join(word.title() for word in service_name_lower.split("_")) + "Service"
    service_title = service_name_lower.replace("_", " ").title()

    # Generate content from template
    content = SERVICE_TEMPLATE
    content = content.replace("${service_name}", service_name_lower)
    content = content.replace("${class_name}", class_name)
    content = content.replace("${service_title}", service_title)

    # Determine output path
    output_dir = PROJECT_ROOT / "src" / "truth_forge" / "services"
    output_file = output_dir / f"{service_name_lower}.py"

    if output_file.exists() and not force:
        typer.echo(f"Error: {output_file} already exists. Use --force to overwrite.")
        raise typer.Exit(code=1)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file.write_text(content)
    typer.echo(f"✓ Generated: {output_file}")

    # Also create __init__.py entry hint
    typer.echo("\nAdd to src/truth_forge/services/__init__.py:")
    typer.echo(f"    from truth_forge.services.{service_name_lower} import {class_name}")


@app.command()
def analyze(service_path: str) -> bool:
    """Analyze a legacy service for migration."""
    file_path = Path(service_path)
    if not file_path.exists():
        typer.echo(f"Error: File not found: {file_path}")
        return False

    content = file_path.read_text()

    typer.echo(f"Analyzing: {file_path}")
    typer.echo("=" * 60)

    # Parse AST
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        typer.echo(f"Error: Cannot parse file: {e}")
        return False

    # Find classes
    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    typer.echo(f"\n## Classes Found: {len(classes)}")
    for cls in classes:
        typer.echo(f"  - {cls.name}")
        methods = [n.name for n in cls.body if isinstance(n, ast.FunctionDef)]
        typer.echo(f"    Methods: {', '.join(methods)}")

    # Find functions
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    typer.echo(f"\n## Top-Level Functions: {len(functions)}")
    for func in functions:
        typer.echo(f"  - {func.name}")

    # Find imports
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(module)

    typer.echo(f"\n## Imports ({len(imports)})")
    legacy_imports = []
    for imp in imports:
        is_legacy = any(
            pattern in imp
            for pattern in ["Primitive", "central_services", "Truth_Engine", "src.services"]
        )
        if is_legacy:
            legacy_imports.append(imp)
            typer.echo(f"  ⚠ LEGACY: {imp}")

    # Find hardcoded paths
    path_patterns = [
        r'/Users/[^"\']+',
        r'/tmp/[^"\']+',
        r"Path\.home\(\)",
    ]
    hardcoded_paths = []
    for pattern in path_patterns:
        matches = re.findall(pattern, content)
        hardcoded_paths.extend(matches)

    if hardcoded_paths:
        typer.echo(f"\n## Hardcoded Paths ({len(hardcoded_paths)})")
        for path in set(hardcoded_paths):
            typer.echo(f"  ⚠ {path}")

    # Find environment variables
    env_pattern = r'os\.environ(?:\.get)?\(["\']([^"\']+)["\']'
    env_vars = re.findall(env_pattern, content)
    if env_vars:
        typer.echo(f"\n## Environment Variables ({len(env_vars)})")
        for var in set(env_vars):
            typer.echo(f"  - {var}")

    # Migration recommendations
    typer.echo("\n## Migration Recommendations")
    typer.echo("=" * 60)

    if legacy_imports:
        typer.echo("\n1. Update imports:")
        for imp in legacy_imports:
            typer.echo(f"   - Replace '{imp}' with 'truth_forge.*'")

    if hardcoded_paths:
        typer.echo("\n2. Replace hardcoded paths:")
        typer.echo("   - Use truth_forge.core.paths.PROJECT_ROOT")
        typer.echo("   - Use truth_forge.core.paths.get_service_root()")

    if env_vars:
        typer.echo("\n3. Use centralized settings:")
        typer.echo("   - Import: from truth_forge.core.settings import settings")
        for var in set(env_vars):
            typer.echo(f"   - Replace os.environ['{var}'] with settings.{var.lower()}")

    if classes:
        typer.echo("\n4. Inherit from BaseService:")
        typer.echo("   - from truth_forge.services.base import BaseService")
        typer.echo("   - class MyService(BaseService):")
        typer.echo("   -     service_name = 'my_service'")
        typer.echo("   -     def process(self, record): ...")

    return True


@app.command(name="migrate")
def migrate_services(
    service_name: str = typer.Argument(None, help="Name of the service to migrate"),
    all_services: bool = typer.Option(
        False, "--all", help="Migrate all services defined in molt.yaml"
    ),
) -> None:
    """Generate a migration plan for a legacy service based on molt.yaml."""
    config = load_molt_config()
    service_mappings = {s["name"]: s for s in config.get("services", {}).get("mappings", [])}

    if all_services:
        for name, mapping in service_mappings.items():
            _migrate_service(name, mapping)
    elif service_name:
        if service_name not in service_mappings:
            typer.echo(f"Error: Service '{service_name}' not found in molt.yaml")
            raise typer.Exit(code=1)
        _migrate_service(service_name, service_mappings[service_name])
    else:
        typer.echo("Either a service name or --all must be provided.")
        raise typer.Exit(code=1)


def _migrate_service(service_name: str, service_config: dict[str, Any]) -> None:
    """Helper function to migrate a single service."""
    typer.echo(f"\n--- Migrating service: {service_name} ---")
    typer.echo(f"  Destination: {service_config['destination']}")

    legacy_sources = service_config.get("sources", [])
    if not legacy_sources:
        typer.echo("No legacy sources found in molt.yaml for this service.")
        return

    # For simplicity, we'll analyze the first source
    source_path = Path(legacy_sources[0])
    if not source_path.exists():
        typer.echo(f"Error: Legacy source path does not exist: {source_path}")
        return

    # Find the main service file to analyze
    main_file = None
    if source_path.is_dir():
        py_files = list(source_path.rglob("*.py"))
        # Heuristic to find the main file
        for f in py_files:
            if service_name in f.name and "service" in f.name:
                main_file = f
                break
        if not main_file and py_files:
            main_file = py_files[0]
    elif source_path.is_file():
        main_file = source_path

    if not main_file:
        typer.echo(f"Error: No Python files found in legacy source: {source_path}")
        return

    if not analyze(str(main_file)):
        typer.echo(f"Analysis failed for {main_file}, continuing...")
        return

    typer.echo("\n## Next Steps")
    typer.echo("1. Run `generate` to create the new service file")
    typer.echo("2. Manually copy business logic into the new `process` method")
    typer.echo("3. Define the correct `create_schema` method")
