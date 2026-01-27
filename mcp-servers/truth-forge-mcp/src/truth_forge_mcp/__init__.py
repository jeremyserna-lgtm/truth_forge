"""Truth Forge MCP Server.

MOLT LINEAGE:
- Source: Truth_Engine/mcp-servers/truth-engine-mcp/src/truth_engine_mcp/__init__.py
- Version: 2.0.0
- Date: 2026-01-26

MCP (Model Context Protocol) server for truth_forge.

Exposes truth_forge functionality to any MCP-compatible client:
- Claude Code
- Claude Desktop
- Custom MCP clients

Example:
    # Run the server
    python -m truth_forge_mcp.server

    # Or via uvx
    uvx truth-forge-mcp
"""

from __future__ import annotations

__version__ = "2.0.0"
