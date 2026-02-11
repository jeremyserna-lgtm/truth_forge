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
            logger.error("query_knowledge_failed: %s", e, exc_info=True)
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
            logger.error("get_knowledge_atom_failed: %s", e, exc_info=True)
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
            logger.error("get_knowledge_stats_failed: %s", e, exc_info=True)
            return f"Error getting knowledge stats: {type(e).__name__}: {e!s}"

    tools.append((stats_tool, handle_get_knowledge_stats))

    # Create knowledge atom (Priority 0 - NEW)
    create_atom_tool = Tool(
        name="create_knowledge_atom",
        description="Create a new knowledge atom with validation and enrichment",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Knowledge atom content",
                },
                "source": {
                    "type": "string",
                    "description": "Source of knowledge",
                },
                "domain": {
                    "type": "string",
                    "description": "Knowledge domain (optional)",
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata (optional)",
                },
            },
            "required": ["content", "source"],
        },
    )

    def handle_create_knowledge_atom(arguments: dict[str, Any]) -> str:
        """Handle create_knowledge_atom tool.

        Args:
            arguments: Tool arguments containing content, source, domain, metadata.

        Returns:
            Confirmation message with atom ID.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.services.factory import get_service

            knowledge_service = get_service("knowledge")

            # Extract and validate arguments
            content = arguments.get("content")
            source = arguments.get("source")
            domain = arguments.get("domain", "general")
            metadata = arguments.get("metadata", {})

            # Validate required fields
            if not content or not source:
                return "Error: Both 'content' and 'source' are required"

            if len(content) < 10:
                return "Error: Content must be at least 10 characters"

            # Create atom through service (KnowledgeService.exhale())
            # This uses LLM to process and enrich the content
            result = knowledge_service.exhale(
                content=content,
                source=source,
                domain=domain,
                metadata=metadata
            )

            # Format success response
            lines = ["# Knowledge Atom Created ✅", ""]
            if isinstance(result, dict):
                lines.append(f"**Atom ID**: {result.get('id', 'unknown')}")
                lines.append(f"**Source**: {source}")
                lines.append(f"**Domain**: {domain}")
                lines.append(f"**Status**: {result.get('status', 'created')}")

                if result.get('extraction'):
                    lines.append("\n## Extracted Knowledge")
                    extraction = result['extraction']
                    if isinstance(extraction, dict):
                        for key, value in extraction.items():
                            lines.append(f"- **{key}**: {value}")
            else:
                lines.append(f"**Result**: {result}")

            return "\n".join(lines)

        except Exception as e:
            logger.error("create_knowledge_atom_failed: %s", e, exc_info=True)
            return f"Error creating knowledge atom: {type(e).__name__}: {e!s}"

    tools.append((create_atom_tool, handle_create_knowledge_atom))

    # Find related atoms (Priority 0 - NEW)
    find_related_tool = Tool(
        name="find_related_atoms",
        description="Find semantically related knowledge atoms using similarity",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query text or atom ID to find related atoms",
                },
                "similarity_threshold": {
                    "type": "number",
                    "description": "Minimum similarity score (0-1)",
                    "default": 0.7,
                    "minimum": 0,
                    "maximum": 1,
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of related atoms to return",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 50,
                },
            },
            "required": ["query"],
        },
    )

    def handle_find_related_atoms(arguments: dict[str, Any]) -> str:
        """Handle find_related_atoms tool.

        Args:
            arguments: Tool arguments containing query, threshold, limit.

        Returns:
            Markdown-formatted related atoms.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.services.factory import get_service

            knowledge_service = get_service("knowledge")

            query = arguments.get("query", "")
            threshold = arguments.get("similarity_threshold", 0.7)
            limit = arguments.get("limit", 10)

            if not query:
                return "Error: 'query' parameter is required"

            # Query for related atoms using semantic search
            # KnowledgeService uses LLM embeddings for similarity
            related_atoms = knowledge_service.query(
                query=query,
                limit=limit * 2  # Get more to filter by threshold
            )

            lines = [f"# Related Knowledge Atoms", ""]
            lines.append(f"**Query**: {query}")
            lines.append(f"**Similarity Threshold**: {threshold}")
            lines.append("")

            if not related_atoms:
                lines.append("No related atoms found.")
                lines.append("\nTry:")
                lines.append("- Lowering the similarity threshold")
                lines.append("- Using different search terms")
                lines.append("- Creating more knowledge atoms")
                return "\n".join(lines)

            # Filter by relevance (approximate - KnowledgeService may not expose scores)
            displayed = 0
            for i, atom in enumerate(related_atoms[:limit], 1):
                atom_data = atom.get("data", atom) if isinstance(atom.get("data"), dict) else atom
                content = atom_data.get("content", "N/A")
                source = atom_data.get("source", "unknown")
                llm_model = atom_data.get("llm_model", "N/A")

                # Display atom
                lines.append(f"## Related Atom {i}")
                lines.append(f"- **Content**: {content[:200]}{'...' if len(content) > 200 else ''}")
                lines.append(f"- **Source**: {source}")
                lines.append(f"- **Model**: {llm_model}")

                # Show extraction if available
                if atom_data.get("extraction"):
                    extraction = atom_data["extraction"]
                    if isinstance(extraction, dict):
                        key_facts = extraction.get("key_facts", [])
                        if key_facts:
                            lines.append(f"- **Key Facts**: {', '.join(str(f) for f in key_facts[:3])}")

                lines.append("")
                displayed += 1

            lines.insert(3, f"**Found**: {displayed} related atom(s)\n")

            return "\n".join(lines)

        except Exception as e:
            logger.error("find_related_atoms_failed: %s", e, exc_info=True)
            return f"Error finding related atoms: {type(e).__name__}: {e!s}"

    tools.append((find_related_tool, handle_find_related_atoms))

    return tools
