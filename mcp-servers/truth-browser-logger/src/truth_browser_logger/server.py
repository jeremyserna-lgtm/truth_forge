#!/usr/bin/env python3
"""Truth Browser Logger MCP Server.

Exposes browser history extraction tools to Claude instances with
consent-based access, domain categorization, and pattern detection.

Usage:
    python -m truth_browser_logger.server

Part of Truth Forge - Enterprise Grade AI Coordination.
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# Add src to path for central_services imports
_repo_root = Path(__file__).parent.parent.parent.parent.parent
_src_path = _repo_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Server version
__version__ = "1.0.0"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("truth-browser-logger")

# Tool registry
TOOL_HANDLERS: Dict[str, Callable] = {}
TOOL_DEFINITIONS: List[Tool] = []


def _safe_import_tool(
    module_name: str,
    tool_attr: str,
    handler_attr: str,
) -> Optional[Tuple[Tool, Callable]]:
    """Safely import a tool and its handler."""
    try:
        module = __import__(module_name, fromlist=[tool_attr, handler_attr])
        tool = getattr(module, tool_attr)
        handler = getattr(module, handler_attr)
        return (tool, handler)
    except Exception as e:
        logger.warning(f"Failed to import {module_name}: {e}")
        return None


def _register_tools():
    """Register all available tools."""
    
    tools_to_import = [
        # Core browser history tools
        ("truth_browser_logger.tools.get_browser_history", "get_browser_history_tool", "handle_get_browser_history"),
        ("truth_browser_logger.tools.get_browser_stats", "get_browser_stats_tool", "handle_get_browser_stats"),
        ("truth_browser_logger.tools.check_consent", "check_consent_tool", "handle_check_consent"),
        # Stacked amplification tools
        ("truth_browser_logger.tools.get_browser_context_for_entity", "get_browser_context_for_entity_tool", "handle_get_browser_context_for_entity"),
        ("truth_browser_logger.tools.correlate_browser_with_truth", "correlate_browser_with_truth_tool", "handle_correlate_browser_with_truth"),
        ("truth_browser_logger.tools.get_research_timeline", "get_research_timeline_tool", "handle_get_research_timeline"),
        # Pattern detection tools
        ("truth_browser_logger.tools.get_session_patterns", "get_session_patterns_tool", "handle_get_session_patterns"),
        # Unified relationship context (Signal Orchestrator)
        ("truth_browser_logger.tools.get_relationship_context", "get_relationship_context_tool", "handle_get_relationship_context"),
    ]

    for module_name, tool_attr, handler_attr in tools_to_import:
        result = _safe_import_tool(module_name, tool_attr, handler_attr)
        if result:
            tool, handler = result
            TOOL_HANDLERS[tool.name] = handler
            TOOL_DEFINITIONS.append(tool)
            logger.info(f"Registered tool: {tool.name}")
        else:
            logger.warning(f"Skipping tool from {module_name}")

    logger.info(f"Registered {len(TOOL_DEFINITIONS)} tools")


# Register tools on module load
_register_tools()


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return TOOL_DEFINITIONS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls with logging and error handling."""
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
        logger.info(f"Tool {name} completed in {duration_ms:.2f}ms")

        return [TextContent(type="text", text=str(result))]

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        error_msg = f"Error in {name}: {type(e).__name__}: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def _run_server():
    """Run the MCP server."""
    logger.info(f"Starting Truth Browser Logger MCP Server v{__version__}")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    """Entry point."""
    asyncio.run(_run_server())


if __name__ == "__main__":
    main()
