"""DuckDB Query MCP Tools.

Exposes DuckDB database query capabilities via MCP tools.

THE PATTERN:
- HOLD₁: Tool arguments (sql query, database path)
- AGENT: DuckDB execution
- HOLD₂: Tool results (query results)
"""

from __future__ import annotations

import logging
from typing import Any

import duckdb

from mcp.types import Tool

logger = logging.getLogger(__name__)


def get_duckdb_tools() -> list[tuple[Tool, Any]]:
    """Get all DuckDB query tools.

    Returns:
        List of (Tool, handler) tuples.
    """
    tools: list[tuple[Tool, Any]] = []

    # Query DuckDB
    query_duckdb_tool = Tool(
        name="query_duckdb",
        description="Execute SQL query on a DuckDB database",
        inputSchema={
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Service name (e.g., 'knowledge', 'governance')",
                },
                "sql": {
                    "type": "string",
                    "description": "SQL query to execute",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum rows to return (safety limit)",
                    "default": 1000,
                    "minimum": 1,
                    "maximum": 10000,
                },
            },
            "required": ["service_name", "sql"],
        },
    )

    def handle_query_duckdb(arguments: dict[str, Any]) -> str:
        """Handle query_duckdb tool.

        Args:
            arguments: Tool arguments containing service_name and sql.

        Returns:
            Markdown-formatted query results.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.core.paths import get_duckdb_file

            service_name = arguments["service_name"]
            sql = arguments["sql"]
            limit = arguments.get("limit", 1000)

            # Safety: Ensure SELECT query and add limit if not present
            sql_upper = sql.strip().upper()
            if not sql_upper.startswith("SELECT"):
                return "Error: Only SELECT queries are allowed for safety."

            # Add limit if not present
            if "LIMIT" not in sql_upper:
                sql = f"{sql.rstrip(';')} LIMIT {limit}"

            db_path = get_duckdb_file(service_name)
            if not db_path.exists():
                return f"# DuckDB Query\n\nDatabase not found: {db_path}"

            conn = duckdb.connect(str(db_path), read_only=True)
            try:
                result = conn.execute(sql).fetchall()
                columns = [desc[0] for desc in conn.description] if conn.description else []

                lines = [f"# DuckDB Query: {service_name}", ""]
                lines.append(f"**Query**: `{sql}`\n")

                if not result:
                    lines.append("No results found.")
                else:
                    lines.append(f"Found {len(result)} row(s):\n")

                    # Format as table
                    if columns:
                        # Header
                        lines.append("| " + " | ".join(columns) + " |")
                        lines.append("|" + "|".join(["---"] * len(columns)) + "|")

                        # Rows (limit display)
                        for row in result[:50]:  # Show first 50
                            row_str = " | ".join(str(val)[:50] for val in row)
                            lines.append(f"| {row_str} |")

                        if len(result) > 50:
                            lines.append(f"\n... and {len(result) - 50} more rows")

            finally:
                conn.close()

            return "\n".join(lines)

        except Exception as e:
            logger.error("query_duckdb_failed", error=str(e), exc_info=True)
            return f"Error querying DuckDB: {type(e).__name__}: {e!s}"

    tools.append((query_duckdb_tool, handle_query_duckdb))

    # List databases
    list_databases_tool = Tool(
        name="list_duckdb_databases",
        description="List available DuckDB databases",
        inputSchema={
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Optional: Filter by service name",
                },
            },
        },
    )

    def handle_list_databases(arguments: dict[str, Any]) -> str:
        """Handle list_duckdb_databases tool.

        Args:
            arguments: Tool arguments.

        Returns:
            Markdown-formatted database list.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.core.paths import SERVICES_ROOT

            service_filter = arguments.get("service_name")

            lines = ["# DuckDB Databases", ""]

            services_root = SERVICES_ROOT
            if not services_root.exists():
                return "# DuckDB Databases\n\nServices root not found."

            databases: list[tuple[str, Path]] = []

            # Find all .duckdb files in service hold2 directories
            for service_dir in services_root.iterdir():
                if not service_dir.is_dir():
                    continue

                service_name = service_dir.name
                if service_filter and service_name != service_filter:
                    continue

                db_file = service_dir / "hold2" / f"{service_name}.duckdb"
                if db_file.exists():
                    size = db_file.stat().st_size
                    databases.append((service_name, db_file))

            if not databases:
                lines.append("No DuckDB databases found.")
            else:
                lines.append(f"Found {len(databases)} database(s):\n")
                for service_name, db_path in sorted(databases):
                    size_mb = db_path.stat().st_size / (1024 * 1024)
                    lines.append(f"- **{service_name}**: {db_path} ({size_mb:.2f} MB)")

            return "\n".join(lines)

        except Exception as e:
            logger.error("list_databases_failed", error=str(e), exc_info=True)
            return f"Error listing databases: {type(e).__name__}: {e!s}"

    tools.append((list_databases_tool, handle_list_databases))

    # Get schema
    get_schema_tool = Tool(
        name="get_duckdb_schema",
        description="Get schema for a DuckDB database",
        inputSchema={
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Service name",
                },
            },
            "required": ["service_name"],
        },
    )

    def handle_get_schema(arguments: dict[str, Any]) -> str:
        """Handle get_duckdb_schema tool.

        Args:
            arguments: Tool arguments containing service_name.

        Returns:
            Markdown-formatted schema.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.core.paths import get_duckdb_file

            service_name = arguments["service_name"]

            db_path = get_duckdb_file(service_name)
            if not db_path.exists():
                return f"# DuckDB Schema: {service_name}\n\nDatabase not found: {db_path}"

            conn = duckdb.connect(str(db_path), read_only=True)
            try:
                # Get all tables
                tables = conn.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
                ).fetchall()

                lines = [f"# DuckDB Schema: {service_name}", ""]

                if not tables:
                    lines.append("No tables found.")
                else:
                    for table_name, in tables:
                        lines.append(f"## Table: {table_name}")
                        # Get columns
                        columns = conn.execute(
                            f"PRAGMA table_info('{table_name}')"
                        ).fetchall()

                        if columns:
                            lines.append("| Column | Type | Null | Default |")
                            lines.append("|--------|------|------|---------|")
                            for col in columns:
                                col_name = col[1]
                                col_type = col[2]
                                not_null = "NO" if col[3] else "YES"
                                default = col[4] or ""
                                lines.append(f"| {col_name} | {col_type} | {not_null} | {default} |")
                        lines.append("")

            finally:
                conn.close()

            return "\n".join(lines)

        except Exception as e:
            logger.error("get_schema_failed", error=str(e), exc_info=True)
            return f"Error getting schema: {type(e).__name__}: {e!s}"

    tools.append((get_schema_tool, handle_get_schema))

    return tools
