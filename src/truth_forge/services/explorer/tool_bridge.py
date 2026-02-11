"""Tool Bridge - MCP tool invocation layer for Explorer.

Provides direct invocation of spine-analysis-mcp tools without going
through the MCP protocol. More efficient for internal exploration.

THE PATTERN:
- HOLD₁: Tool invocation request with arguments
- AGENT: Tool handler execution
- HOLD₂: Tool result with metadata

MOLT LINEAGE:
- Source: New creation for Explorer autonomous data exploration
- Version: 1.0.0
- Date: 2026-02-01
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from typing import Any

from .models import ToolResult


logger = logging.getLogger(__name__)


# =============================================================================
# TOOL CATEGORIES
# =============================================================================

TOOL_CATEGORIES: dict[str, str] = {
    # Query Tools
    "query_entities": "entity",
    "query_documents": "entity",
    "query_messages": "entity",
    "query_conversations": "entity",
    # Source Tools
    "get_source_summary": "source",
    "compare_sources": "source",
    "get_source_timeline": "source",
    # Trend Tools
    "analyze_temporal_trends": "trend",
    # Concept Tools
    "extract_concepts": "concept",
    "analyze_concept_evolution": "concept",
    "find_concept_connections": "concept",
    # Spine Level Tools
    "analyze_spine_level": "spine",
    "compare_spine_levels": "spine",
    "get_level_distribution": "spine",
    # Relationship Tools
    "find_entity_relationships": "relationship",
    "trace_relationship_paths": "relationship",
    "analyze_relationship_network": "relationship",
    # Temporal Tools
    "analyze_activity_patterns": "temporal",
    "find_temporal_clusters": "temporal",
    "compare_time_periods": "temporal",
    # Pattern Tools
    "detect_patterns": "pattern",
    "identify_pattern_anomalies": "pattern",
    "find_repeating_patterns": "pattern",
    # Semantic Tools
    "find_similar_entities": "semantic",
    "extract_concept_clusters": "semantic",
    # Cross Level Tools
    "trace_entity_lineage": "cross_level",
    "find_cross_level_connections": "cross_level",
    # Enrichment Tools
    "get_enrichment_coverage": "enrichment",
    # Not-Me Analytics Tools
    "analyze_cognitive_patterns": "notme",
    "analyze_emotional_trajectory": "notme",
    "identify_stage_markers": "notme",
    # Discovery Tools
    "discover_knowledge_graph": "discovery",
    "discover_emergent_patterns": "discovery",
    "discover_reasoning_chains": "discovery",
}


# =============================================================================
# TOOL BRIDGE
# =============================================================================


class ToolBridge:
    """Bridge for invoking MCP spine-analysis tools.

    Loads tool handlers directly from the MCP server modules
    for efficient internal invocation.
    """

    def __init__(self) -> None:
        """Initialize tool bridge."""
        self._handlers: dict[str, Callable[..., str]] = {}
        self._tool_names: list[str] = []
        self._loaded = False

    def _load_tools(self) -> None:
        """Load tools from MCP server modules."""
        if self._loaded:
            return

        try:
            # Import tool modules from spine-analysis-mcp
            from spine_analysis_mcp.tools import (
                concept_tools,
                cross_level_tools,
                discovery_tools,
                enrichment_tools,
                notme_analytics_tools,
                pattern_tools,
                query_tools,
                relationship_tools,
                semantic_tools,
                source_tools,
                spine_level_tools,
                temporal_tools,
                trend_tools,
            )

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
                notme_analytics_tools,
                discovery_tools,
            ]

            for module in modules:
                if hasattr(module, "get_tools"):
                    tools = module.get_tools()
                    for tool, handler in tools:
                        self._handlers[tool.name] = handler
                        self._tool_names.append(tool.name)

            self._loaded = True
            logger.info(
                "tool_bridge_loaded",
                extra={"tool_count": len(self._handlers)},
            )

        except ImportError as e:
            logger.warning(
                "tool_bridge_import_failed",
                extra={"error": str(e)},
            )
            # Provide stub handlers for testing
            self._loaded = True

    def get_tool_names(self) -> list[str]:
        """Get list of available tool names.

        Returns:
            List of tool names.
        """
        self._load_tools()
        return self._tool_names.copy()

    def get_tool_category(self, tool_name: str) -> str:
        """Get category for a tool.

        Args:
            tool_name: Name of the tool.

        Returns:
            Tool category string.
        """
        return TOOL_CATEGORIES.get(tool_name, "unknown")

    def invoke(self, tool_name: str, arguments: dict[str, Any]) -> ToolResult:
        """Invoke a tool synchronously.

        Args:
            tool_name: Name of the tool to invoke.
            arguments: Tool arguments.

        Returns:
            ToolResult with output.
        """
        self._load_tools()

        start_time = time.time()

        handler = self._handlers.get(tool_name)
        if handler is None:
            return ToolResult(
                tool_name=tool_name,
                category="unknown",
                content=f"Unknown tool: {tool_name}. Available: {', '.join(self._tool_names[:10])}...",
                success=False,
                error=f"Tool not found: {tool_name}",
            )

        try:
            # Handle both sync and async handlers
            if asyncio.iscoroutinefunction(handler):
                # Run async handler in event loop
                try:
                    loop = asyncio.get_running_loop()
                    result = loop.run_until_complete(handler(arguments))
                except RuntimeError:
                    # No running loop, create one
                    result = asyncio.run(handler(arguments))
            else:
                result = handler(arguments)

            latency_ms = (time.time() - start_time) * 1000

            # Extract entity IDs if present in result
            entities = self._extract_entities(str(result))

            return ToolResult(
                tool_name=tool_name,
                category=self.get_tool_category(tool_name),
                content=str(result),
                entities=entities,
                success=True,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = f"{type(e).__name__}: {e!s}"

            logger.error(
                "tool_invocation_failed",
                extra={
                    "tool": tool_name,
                    "error": error_msg,
                    "latency_ms": latency_ms,
                },
            )

            return ToolResult(
                tool_name=tool_name,
                category=self.get_tool_category(tool_name),
                content=f"Error: {error_msg}",
                success=False,
                error=error_msg,
                latency_ms=latency_ms,
            )

    async def invoke_async(self, tool_name: str, arguments: dict[str, Any]) -> ToolResult:
        """Invoke a tool asynchronously.

        Args:
            tool_name: Name of the tool to invoke.
            arguments: Tool arguments.

        Returns:
            ToolResult with output.
        """
        self._load_tools()

        start_time = time.time()

        handler = self._handlers.get(tool_name)
        if handler is None:
            return ToolResult(
                tool_name=tool_name,
                category="unknown",
                content=f"Unknown tool: {tool_name}",
                success=False,
                error=f"Tool not found: {tool_name}",
            )

        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(arguments)
            else:
                result = handler(arguments)

            latency_ms = (time.time() - start_time) * 1000
            entities = self._extract_entities(str(result))

            return ToolResult(
                tool_name=tool_name,
                category=self.get_tool_category(tool_name),
                content=str(result),
                entities=entities,
                success=True,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = f"{type(e).__name__}: {e!s}"

            return ToolResult(
                tool_name=tool_name,
                category=self.get_tool_category(tool_name),
                content=f"Error: {error_msg}",
                success=False,
                error=error_msg,
                latency_ms=latency_ms,
            )

    def invoke_batch(
        self,
        tool_invocations: list[tuple[str, dict[str, Any]]],
    ) -> list[ToolResult]:
        """Invoke multiple tools in batch.

        Args:
            tool_invocations: List of (tool_name, arguments) tuples.

        Returns:
            List of ToolResults.
        """
        return [self.invoke(name, args) for name, args in tool_invocations]

    async def invoke_batch_async(
        self,
        tool_invocations: list[tuple[str, dict[str, Any]]],
        parallel: bool = True,
    ) -> list[ToolResult]:
        """Invoke multiple tools in batch asynchronously.

        Args:
            tool_invocations: List of (tool_name, arguments) tuples.
            parallel: If True, invoke tools in parallel.

        Returns:
            List of ToolResults.
        """
        if parallel:
            tasks = [self.invoke_async(name, args) for name, args in tool_invocations]
            return await asyncio.gather(*tasks)
        else:
            results = []
            for name, args in tool_invocations:
                result = await self.invoke_async(name, args)
                results.append(result)
            return results

    def _extract_entities(self, text: str) -> list[str]:
        """Extract entity IDs from tool output.

        Looks for patterns like entity_id, ID: xxx, etc.

        Args:
            text: Tool output text.

        Returns:
            List of extracted entity IDs.
        """
        import re

        entities: list[str] = []

        # Pattern: entity_id: xxx or **ID**: xxx
        patterns = [
            r"entity_id[:\s]+([a-zA-Z0-9_-]+)",
            r"\*\*ID\*\*[:\s]+([a-zA-Z0-9_-]+)",
            r"ID[:\s]+([a-zA-Z0-9_-]+)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.extend(matches)

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for e in entities:
            if e not in seen:
                seen.add(e)
                unique.append(e)

        return unique[:50]  # Limit to 50 entities

    def get_exploration_tools(self) -> list[str]:
        """Get tools suitable for exploration.

        Returns subset of tools that are good for autonomous exploration.

        Returns:
            List of tool names for exploration.
        """
        exploration_tools = [
            # Discovery tools - best for autonomous exploration
            "discover_knowledge_graph",
            "discover_emergent_patterns",
            "discover_reasoning_chains",
            # Pattern detection
            "detect_patterns",
            "find_repeating_patterns",
            "identify_pattern_anomalies",
            # Concept analysis
            "extract_concepts",
            "find_concept_connections",
            # Relationship mapping
            "find_entity_relationships",
            "analyze_relationship_network",
            # Semantic similarity
            "find_similar_entities",
            "extract_concept_clusters",
            # Temporal analysis
            "analyze_temporal_trends",
            "analyze_activity_patterns",
            # Cross-level tracing
            "trace_entity_lineage",
            "find_cross_level_connections",
            # Cognitive analysis (Not-Me)
            "analyze_cognitive_patterns",
            "identify_stage_markers",
        ]

        # Filter to only available tools
        available = set(self.get_tool_names())
        return [t for t in exploration_tools if t in available]


__all__ = [
    "TOOL_CATEGORIES",
    "ToolBridge",
]
