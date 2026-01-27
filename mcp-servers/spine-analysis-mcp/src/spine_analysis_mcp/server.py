"""Spine Analysis MCP Server - Main Server Implementation.

MCP server for deep BigQuery spine dataset analysis.

THE PATTERN:
- Tools = AGENT capabilities exposed to clients
- Resources = HOLD2 content served to clients
- Protocol = JSON-RPC over stdio

Usage:
    python -m spine_analysis_mcp.server
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import signal
import sys
import time
from pathlib import Path
from typing import Any

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

from spine_analysis_mcp import __version__
from spine_analysis_mcp.tools import (
    concept_tools,
    cross_level_tools,
    enrichment_tools,
    pattern_tools,
    query_tools,
    relationship_tools,
    semantic_tools,
    source_tools,
    spine_level_tools,
    temporal_tools,
    trend_tools,
)

# CRITICAL: MCP servers MUST use stderr for logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

_shutdown_event: asyncio.Event | None = None
TOOL_HANDLERS: dict[str, Any] = {}
TOOL_DEFINITIONS: list[Tool] = []


def _register_all_tools() -> None:
    """Register all tool modules."""
    if not MCP_AVAILABLE:
        return

    # Register tools from each module
    modules = [
        query_tools,
        source_tools,
        trend_tools,
        concept_tools,
        spine_level_tools,
        relationship_tools,
        temporal_tools,
        pattern_tools,
        semantic_tools,
        cross_level_tools,
        enrichment_tools,
    ]

    for module in modules:
        if hasattr(module, "get_tools"):
            tools = module.get_tools()
            for tool, handler in tools:
                TOOL_DEFINITIONS.append(tool)
                TOOL_HANDLERS[tool.name] = handler
                logger.info(f"Registered tool: {tool.name}")


def create_server() -> Any:
    """Create and configure MCP server.

    Returns:
        Configured MCP server instance.
    """
    if not MCP_AVAILABLE:
        raise ImportError("MCP package not available. Install with: pip install mcp")

    _register_all_tools()

    server = Server("spine-analysis-mcp")

    @server.list_tools()  # type: ignore[no-untyped-call, untyped-decorator]
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return TOOL_DEFINITIONS

    @server.call_tool()  # type: ignore[untyped-decorator]
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls."""
        start_time = time.time()
        logger.info(f"Tool call: {name}")

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
            logger.info(f"Tool completed: {name} ({duration_ms:.2f}ms)")

            return [TextContent(type="text", text=str(result))]

        except Exception as e:
            error_msg = f"Error in {name}: {type(e).__name__}: {e!s}"
            logger.error(error_msg, exc_info=True)
            return [TextContent(type="text", text=error_msg)]

    @server.list_resources()  # type: ignore[no-untyped-call, untyped-decorator]
    async def list_resources() -> list[Resource]:
        """List available resources."""
        return [
            Resource(
                uri="spine://schema",  # type: ignore[arg-type]
                name="Spine Schema",
                description="BigQuery spine dataset schema information",
                mimeType="text/markdown",
            ),
            Resource(
                uri="spine://sources",  # type: ignore[arg-type]
                name="Data Sources",
                description="Information about data sources (Claude, Gemini, Codex, Cursor)",
                mimeType="text/markdown",
            ),
            Resource(
                uri="spine://enrichment-gaps",  # type: ignore[arg-type]
                name="Enrichment Coverage Gaps",
                description="Entity enrichments coverage and gaps report (what to complete for analyses)",
                mimeType="text/markdown",
            ),
        ]

    @server.read_resource()  # type: ignore[no-untyped-call, untyped-decorator]
    async def read_resource(uri: str) -> ReadResourceResult:
        """Serve MCP resources."""
        content = f"Unknown resource: {uri}"

        if uri == "spine://schema":
            from spine_analysis_mcp.config import SPINE_LEVELS

            content = "# Spine Dataset Schema\n\n"
            content += "## Spine Levels (L1-L12)\n\n"
            for level, name in SPINE_LEVELS.items():
                content += f"- **L{level}**: {name}\n"
            content += "\n## Primary Tables\n\n"
            content += "- `entity` - Core entity table (L1-L12)\n"
            content += "- `document` - Document metadata and content\n"
            content += "- `message` - Conversation messages\n"
            content += "- `conversation` - Conversation metadata\n"
            content += "- `entity_relationship` - Cross-entity relationships\n"

        elif uri == "spine://sources":
            from spine_analysis_mcp.config import DATA_SOURCES

            content = "# Data Sources\n\n"
            content += "The spine dataset processes data from multiple sources:\n\n"
            for source_id, description in DATA_SOURCES.items():
                content += f"- **{source_id}**: {description}\n"

        elif uri == "spine://enrichment-gaps":
            gap_path = Path(__file__).resolve().parents[4] / "docs" / "technical" / "enrichment" / "ENRICHMENT_COVERAGE_GAPS_REPORT.md"
            if gap_path.exists():
                content = gap_path.read_text(encoding="utf-8")
            else:
                content = "# Enrichment Coverage Gaps\n\nUse `get_enrichment_coverage` tool for a live report. Full report: `docs/technical/enrichment/ENRICHMENT_COVERAGE_GAPS_REPORT.md`."

        return ReadResourceResult(
            contents=[TextResourceContents(uri=uri, mimeType="text/markdown", text=content)],  # type: ignore[arg-type]
        )

    return server


def _setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown."""
    global _shutdown_event
    _shutdown_event = asyncio.Event()

    def handle_signal(signum: int, frame: Any) -> None:
        logger.info(f"Received signal {signum}, initiating shutdown")
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

    logger.info(f"Spine Analysis MCP Server starting (v{__version__})")
    logger.info(f"Available tools: {len(TOOL_DEFINITIONS)}")

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

    logger.info("Spine Analysis MCP Server stopped")


def main() -> None:
    """CLI entry point."""
    _setup_signal_handlers()

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down")


if __name__ == "__main__":
    main()
