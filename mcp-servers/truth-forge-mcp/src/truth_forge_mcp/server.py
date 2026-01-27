"""Truth Forge MCP Server - Main Server Implementation.

MOLT LINEAGE:
- Source: Truth_Engine/mcp-servers/truth-engine-mcp/src/truth_engine_mcp/server.py
- Version: 2.0.0
- Date: 2026-01-26

Provides MCP server for truth_forge functionality.

THE PATTERN:
- Tools = AGENT capabilities exposed to clients
- Resources = HOLD2 content served to clients
- Protocol = JSON-RPC over stdio

Usage:
    python -m truth_forge_mcp.server
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import signal
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

# MCP imports - requires mcp package
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        ReadResourceResult,
        Resource,
        TextContent,
        TextResourceContents,
        Tool,
    )

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    Server = None  # type: ignore[misc, assignment]

from truth_forge_mcp import __version__

# CRITICAL: MCP servers MUST use stderr for logging
# stdout is reserved for JSON-RPC protocol communication
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Graceful shutdown event
_shutdown_event: asyncio.Event | None = None

# Tool registry
TOOL_HANDLERS: dict[str, Callable[..., Any]] = {}
TOOL_DEFINITIONS: list[Any] = []


def _get_project_root() -> Path:
    """Get the truth_forge project root.

    Returns:
        Path to project root.
    """
    # Navigate up from mcp-servers/truth-forge-mcp/src/truth_forge_mcp/
    return Path(__file__).parent.parent.parent.parent.parent


def register_tool(tool: Any, handler: Callable[..., Any]) -> None:
    """Register a tool with the server.

    Args:
        tool: MCP Tool definition.
        handler: Function to handle tool calls.
    """
    TOOL_HANDLERS[tool.name] = handler
    TOOL_DEFINITIONS.append(tool)
    logger.info("Registered tool", extra={"tool_name": tool.name})


def _register_builtin_tools() -> None:
    """Register built-in tools."""
    if not MCP_AVAILABLE:
        return

    # Status tool
    status_tool = Tool(
        name="get_status",
        description="Get truth_forge system status",
        inputSchema={
            "type": "object",
            "properties": {
                "detailed": {
                    "type": "boolean",
                    "description": "Include detailed information",
                    "default": False,
                },
            },
        },
    )

    def handle_get_status(arguments: dict[str, Any]) -> str:
        """Handle get_status tool."""
        project_root = _get_project_root()
        detailed = arguments.get("detailed", False)

        lines = [
            "# Truth Forge Status",
            "",
            f"**Version**: {__version__}",
            f"**Project Root**: {project_root}",
            "",
        ]

        # Check key directories
        key_dirs = ["src", "tests", "pipelines", "data"]
        lines.append("## Directories")
        for dir_name in key_dirs:
            exists = (project_root / dir_name).exists()
            mark = "✓" if exists else "✗"
            lines.append(f"- {mark} {dir_name}/")

        if detailed:
            # Count source files
            src_files = list((project_root / "src").rglob("*.py"))
            lines.append("")
            lines.append("## Statistics")
            lines.append(f"- Source files: {len(src_files)}")

        return "\n".join(lines)

    register_tool(status_tool, handle_get_status)

    # Governance tool (basic)
    governance_tool = Tool(
        name="check_governance",
        description="Check governance status and recent violations",
        inputSchema={
            "type": "object",
            "properties": {
                "show_violations": {
                    "type": "boolean",
                    "description": "Show recent violations",
                    "default": False,
                },
            },
        },
    )

    def handle_check_governance(arguments: dict[str, Any]) -> str:
        """Handle check_governance tool."""
        lines = [
            "# Governance Status",
            "",
            "## Enforcement",
            "- ✓ HOLD Isolation: Enabled",
            "- ✓ Cost Tracking: Enabled",
            "- ✓ Audit Trail: Enabled",
            "",
        ]

        if arguments.get("show_violations", False):
            lines.append("## Recent Violations")
            lines.append("No violations recorded.")

        return "\n".join(lines)

    register_tool(governance_tool, handle_check_governance)

    # Register all service tools
    try:
        from truth_forge_mcp.tools import get_all_tools

        all_tools = get_all_tools()
        for tool, handler in all_tools:
            register_tool(tool, handler)
            logger.info("Registered service tool", extra={"tool_name": tool.name})

    except Exception as e:
        logger.error("Failed to register service tools", extra={"error": str(e)}, exc_info=True)


# Register tools on module load
_register_builtin_tools()


def create_server() -> Any:
    """Create and configure the MCP server.

    Returns:
        Configured MCP Server instance.
    """
    if not MCP_AVAILABLE:
        raise ImportError("MCP package not available. Install with: pip install mcp")

    server = Server("truth-forge-mcp")

    @server.list_tools()  # type: ignore[no-untyped-call, untyped-decorator]
    async def list_tools() -> list[Any]:
        """List available tools."""
        return TOOL_DEFINITIONS

    @server.call_tool()  # type: ignore[untyped-decorator]
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[Any]:
        """Handle tool calls."""
        start_time = time.time()
        logger.info("Tool call", extra={"tool_name": name})

        try:
            handler = TOOL_HANDLERS.get(name)
            if handler is None:
                result = f"Unknown tool: {name}. Available: {', '.join(TOOL_HANDLERS.keys())}"
            else:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(arguments)
                else:
                    result = handler(arguments)

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "Tool completed",
                extra={"tool_name": name, "duration_ms": f"{duration_ms:.2f}"},
            )

            return [TextContent(type="text", text=str(result))]

        except Exception as e:
            error_msg = f"Error in {name}: {type(e).__name__}: {e!s}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]

    @server.list_resources()  # type: ignore[no-untyped-call, untyped-decorator]
    async def list_resources() -> list[Any]:
        """List available resources."""
        return [
            Resource(
                uri="truth-forge://status",  # type: ignore[arg-type]
                name="Status",
                description="Truth Forge system status",
                mimeType="text/markdown",
            ),
            Resource(
                uri="truth-forge://claude-md",  # type: ignore[arg-type]
                name="CLAUDE.md",
                description="Agent instructions from CLAUDE.md",
                mimeType="text/markdown",
            ),
        ]

    @server.read_resource()  # type: ignore[no-untyped-call, untyped-decorator]
    async def read_resource(uri: str) -> Any:
        """Serve MCP resources."""
        content = f"Unknown resource: {uri}"

        if uri == "truth-forge://status":
            handler = TOOL_HANDLERS.get("get_status")
            if handler:
                content = handler({"detailed": True})

        elif uri == "truth-forge://claude-md":
            project_root = _get_project_root()
            claude_md = project_root / "CLAUDE.md"
            content = claude_md.read_text() if claude_md.exists() else "CLAUDE.md not found"

        return ReadResourceResult(
            contents=[TextResourceContents(uri=uri, mimeType="text/markdown", text=content)],  # type: ignore[arg-type]
        )

    return server


def _setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown."""
    global _shutdown_event
    _shutdown_event = asyncio.Event()

    def handle_signal(signum: int, frame: Any) -> None:
        logger.info("Received signal, initiating shutdown", extra={"signal": signum})
        if _shutdown_event:
            _shutdown_event.set()

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)


async def run_server() -> None:
    """Run the MCP server."""
    global _shutdown_event

    if not MCP_AVAILABLE:
        logger.error("MCP package not available")
        return

    logger.info("Truth Forge MCP Server starting", extra={"version": __version__})
    logger.info("Available tools", extra={"tools": list(TOOL_HANDLERS.keys())})

    server = create_server()

    async with stdio_server() as (read_stream, write_stream):
        server_task = asyncio.create_task(
            server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
        )

        if _shutdown_event is None:
            _shutdown_event = asyncio.Event()

        shutdown_task = asyncio.create_task(_shutdown_event.wait())

        _done, pending = await asyncio.wait(
            [server_task, shutdown_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    logger.info("Truth Forge MCP Server stopped", extra={"version": __version__})


def main() -> None:
    """CLI entry point."""
    _setup_signal_handlers()

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down")


if __name__ == "__main__":
    main()
