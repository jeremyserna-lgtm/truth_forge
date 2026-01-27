"""Knowledge Service MCP Tools.

Exposes KnowledgeService capabilities via MCP tools.

THE PATTERN:
- HOLD₁: Tool arguments (query, filters)
- AGENT: KnowledgeService.query() / KnowledgeService.exhale()
- HOLD₂: Tool results (knowledge atoms)
"""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.types import Tool

logger = logging.getLogger(__name__)


def get_knowledge_tools() -> list[tuple[Tool, Any]]:
    """Get all knowledge service tools.

    Returns:
        List of (Tool, handler) tuples.
    """
    tools: list[tuple[Tool, Any]] = []

    # Query knowledge atoms
    query_tool = Tool(
        name="query_knowledge",
        description="Query knowledge atoms by search term, filters, and limits",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to match against knowledge atom content",
                },
                "source": {
                    "type": "string",
                    "description": "Filter by source name (optional)",
                },
                "model": {
                    "type": "string",
                    "description": "Filter by LLM model used (optional)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of atoms to return",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100,
                },
            },
            "required": ["query"],
        },
    )

    def handle_query_knowledge(arguments: dict[str, Any]) -> str:
        """Handle query_knowledge tool.

        Args:
            arguments: Tool arguments containing query, filters, and limit.

        Returns:
            Markdown-formatted results.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.services.factory import get_service

            knowledge_service = get_service("knowledge")
            query = arguments.get("query", "")
            source = arguments.get("source")
            model = arguments.get("model")
            limit = arguments.get("limit", 10)

            atoms = knowledge_service.query(query=query, source=source, model=model, limit=limit)

            lines = [f"# Knowledge Atoms: {query}", ""]
            if not atoms:
                lines.append("No knowledge atoms found.")
            else:
                lines.append(f"Found {len(atoms)} knowledge atom(s):\n")
                for i, atom in enumerate(atoms, 1):
                    atom_data = atom.get("data", atom) if isinstance(atom.get("data"), dict) else atom
                    content = atom_data.get("content", "N/A")
                    source_name = atom_data.get("source", "unknown")
                    llm_model = atom_data.get("llm_model", "N/A")

                    lines.append(f"## Atom {i}")
                    lines.append(f"**Content**: {content[:200]}{'...' if len(content) > 200 else ''}")
                    lines.append(f"**Source**: {source_name}")
                    lines.append(f"**LLM Model**: {llm_model}")
                    lines.append("")

            return "\n".join(lines)

        except Exception as e:
            logger.error("query_knowledge_failed", error=str(e), exc_info=True)
            return f"Error querying knowledge: {type(e).__name__}: {e!s}"

    tools.append((query_tool, handle_query_knowledge))

    # Get specific knowledge atom
    get_atom_tool = Tool(
        name="get_knowledge_atom",
        description="Get a specific knowledge atom by ID",
        inputSchema={
            "type": "object",
            "properties": {
                "atom_id": {
                    "type": "string",
                    "description": "Knowledge atom ID",
                },
            },
            "required": ["atom_id"],
        },
    )

    def handle_get_knowledge_atom(arguments: dict[str, Any]) -> str:
        """Handle get_knowledge_atom tool.

        Args:
            arguments: Tool arguments containing atom_id.

        Returns:
            Markdown-formatted atom details.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.services.factory import get_service

            knowledge_service = get_service("knowledge")
            atom_id = arguments["atom_id"]

            # Query with atom_id as query term (approximate match)
            atoms = knowledge_service.query(query=atom_id, limit=1)

            if not atoms:
                return f"# Knowledge Atom: {atom_id}\n\nAtom not found."

            atom = atoms[0]
            atom_data = atom.get("data", atom) if isinstance(atom.get("data"), dict) else atom

            lines = [f"# Knowledge Atom: {atom_id}", ""]
            lines.append(f"**Content**: {atom_data.get('content', 'N/A')}")
            lines.append(f"**Source**: {atom_data.get('source', 'unknown')}")
            lines.append(f"**LLM Model**: {atom_data.get('llm_model', 'N/A')}")
            lines.append(f"**Status**: {atom_data.get('knowledge_status', 'unknown')}")

            if "extraction" in atom_data:
                lines.append("\n## Extraction")
                lines.append(f"```json\n{json.dumps(atom_data['extraction'], indent=2)}\n```")

            return "\n".join(lines)

        except Exception as e:
            logger.error("get_knowledge_atom_failed", error=str(e), exc_info=True)
            return f"Error getting knowledge atom: {type(e).__name__}: {e!s}"

    tools.append((get_atom_tool, handle_get_knowledge_atom))

    # Get knowledge stats
    stats_tool = Tool(
        name="get_knowledge_stats",
        description="Get statistics about the knowledge base",
        inputSchema={
            "type": "object",
            "properties": {
                "detailed": {
                    "type": "boolean",
                    "description": "Include detailed breakdowns",
                    "default": False,
                },
            },
        },
    )

    def handle_get_knowledge_stats(arguments: dict[str, Any]) -> str:
        """Handle get_knowledge_stats tool.

        Args:
            arguments: Tool arguments.

        Returns:
            Markdown-formatted statistics.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.services.factory import get_service

            knowledge_service = get_service("knowledge")
            detailed = arguments.get("detailed", False)

            # Get session stats
            session_stats = knowledge_service.get_session_stats()

            lines = ["# Knowledge Service Statistics", ""]
            lines.append("## Session Statistics")
            lines.append(f"- **Session Cost**: ${session_stats.get('session_cost', 0):.4f}")
            lines.append(f"- **Session Calls**: {session_stats.get('session_calls', 0)}")
            lines.append(f"- **Max Cost**: ${session_stats.get('max_cost', 0):.2f}")
            lines.append(f"- **Remaining Budget**: ${session_stats.get('remaining_budget', 0):.4f}")
            lines.append(f"- **LLM Model**: {session_stats.get('llm_model', 'N/A')}")

            if detailed:
                # Query for detailed stats
                all_atoms = knowledge_service.query(query="", limit=1000)
                if all_atoms:
                    sources: dict[str, int] = {}
                    models: dict[str, int] = {}
                    statuses: dict[str, int] = {}

                    for atom in all_atoms:
                        atom_data = atom.get("data", atom) if isinstance(atom.get("data"), dict) else atom
                        source = atom_data.get("source", "unknown")
                        model = atom_data.get("llm_model", "unknown")
                        status = atom_data.get("knowledge_status", "unknown")

                        sources[source] = sources.get(source, 0) + 1
                        models[model] = models.get(model, 0) + 1
                        statuses[status] = statuses.get(status, 0) + 1

                    lines.append("\n## Knowledge Base Statistics")
                    lines.append(f"- **Total Atoms**: {len(all_atoms)}")

                    if sources:
                        lines.append("\n### By Source")
                        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                            lines.append(f"- {source}: {count}")

                    if models:
                        lines.append("\n### By LLM Model")
                        for model, count in sorted(models.items(), key=lambda x: x[1], reverse=True):
                            lines.append(f"- {model}: {count}")

                    if statuses:
                        lines.append("\n### By Status")
                        for status, count in sorted(statuses.items(), key=lambda x: x[1], reverse=True):
                            lines.append(f"- {status}: {count}")

            return "\n".join(lines)

        except Exception as e:
            logger.error("get_knowledge_stats_failed", error=str(e), exc_info=True)
            return f"Error getting knowledge stats: {type(e).__name__}: {e!s}"

    tools.append((stats_tool, handle_get_knowledge_stats))

    return tools
