"""MCP Tools - Tool Definitions.

MOLT LINEAGE:
- Source: Truth_Engine/mcp-servers/truth-engine-mcp/src/truth_engine_mcp/tools/__init__.py
- Version: 2.0.0
- Date: 2026-01-26

Custom tools for the truth_forge MCP server.

Tools follow THE PATTERN:
- Input = HOLD1 (arguments)
- Processing = AGENT (handler)
- Output = HOLD2 (result)

All tool modules are imported here for registration.
"""

from __future__ import annotations

from typing import Any

from truth_forge_mcp.tools.bigquery_tools import get_bigquery_tools
from truth_forge_mcp.tools.cognition_tools import get_cognition_tools
from truth_forge_mcp.tools.duckdb_tools import get_duckdb_tools
from truth_forge_mcp.tools.governance_tools import get_governance_tools
from truth_forge_mcp.tools.knowledge_graph_tools import get_knowledge_graph_tools
from truth_forge_mcp.tools.knowledge_tools import get_knowledge_tools
from truth_forge_mcp.tools.pipeline_tools import get_pipeline_tools
from truth_forge_mcp.tools.relationship_tools import get_relationship_tools

__all__: list[str] = [
    "get_knowledge_tools",
    "get_cognition_tools",
    "get_relationship_tools",
    "get_governance_tools",
    "get_bigquery_tools",
    "get_pipeline_tools",
    "get_knowledge_graph_tools",
    "get_duckdb_tools",
]


def get_all_tools() -> list[tuple[Any, Any]]:
    """Get all available tools from all modules.

    Returns:
        List of (Tool, handler) tuples.
    """
    all_tools: list[tuple[Any, Any]] = []
    all_tools.extend(get_knowledge_tools())
    all_tools.extend(get_cognition_tools())
    all_tools.extend(get_relationship_tools())
    all_tools.extend(get_governance_tools())
    all_tools.extend(get_bigquery_tools())
    all_tools.extend(get_pipeline_tools())
    all_tools.extend(get_knowledge_graph_tools())
    all_tools.extend(get_duckdb_tools())
    return all_tools
