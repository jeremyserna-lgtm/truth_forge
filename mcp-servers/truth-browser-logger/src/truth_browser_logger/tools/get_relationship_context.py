"""MCP Tool: get_relationship_context

THE_PATTERN: Unified relationship context through signal orchestration.

This is the PRIMARY MCP tool for getting relationship context.
It returns orchestrated, priority-weighted context ready for LLM use.

Features:
- Checks pre-loaded cache first (instant response)
- Falls back to real-time signal fusion
- Applies constitutional overrides (highest priority)
- Returns prompt-ready formatted context
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from mcp.types import Tool

logger = logging.getLogger(__name__)

# Add repo root to path for imports
_repo_root = Path(__file__).parent.parent.parent.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))


# Tool definition as MCP Tool object
get_relationship_context_tool = Tool(
    name="get_relationship_context",
    description="""Get comprehensive relationship context for a person or entity.

This tool provides unified, priority-weighted context by orchestrating signals from:
- Pre-loaded cache (instant access from calendar-triggered pre-loading)
- Knowledge graph (historical context and relationships)
- Email signals (response patterns, communication frequency)
- Browser history (research activity, topic depth)
- Constitutional memory (HIGHEST PRIORITY overrides)

Returns formatted context suitable for immediate use in conversations.

Use this tool when:
- About to have a meeting with someone
- Need to understand relationship history
- Want context before reaching out to someone
- Need to check for any constitutional rules about a person/topic""",
    inputSchema={
        "type": "object",
        "properties": {
            "entity": {
                "type": "string",
                "description": "The name or identifier of the person/entity to get context for",
            },
            "entity_type": {
                "type": "string",
                "enum": ["person", "company", "topic", "project"],
                "default": "person",
                "description": "The type of entity",
            },
            "format": {
                "type": "string",
                "enum": ["prompt", "json", "summary"],
                "default": "prompt",
                "description": "Output format: 'prompt' for LLM-ready text, 'json' for structured data, 'summary' for brief overview",
            },
            "include_constitutional": {
                "type": "boolean",
                "default": True,
                "description": "Whether to include constitutional overrides (recommended: always true)",
            },
        },
        "required": ["entity"],
    },
)


async def handle_get_relationship_context(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the get_relationship_context tool call.
    
    Args:
        arguments: Tool arguments
        
    Returns:
        Tool result with relationship context
    """
    entity = arguments.get("entity", "")
    entity_type = arguments.get("entity_type", "person")
    output_format = arguments.get("format", "prompt")
    include_constitutional = arguments.get("include_constitutional", True)
    
    if not entity:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "Error: 'entity' is required",
                }
            ],
            "isError": True,
        }
    
    try:
        # Import orchestrator
        from daemon.signal_orchestrator import get_orchestrator
        
        orchestrator = get_orchestrator()
        context = orchestrator.get_context(entity, entity_type)
        
        # Remove constitutional if not requested
        if not include_constitutional:
            context.constitutional_context = []
        
        # Format output based on requested format
        if output_format == "prompt":
            result_text = context.to_prompt_block()
        elif output_format == "json":
            result_text = json.dumps(context.to_dict(), indent=2)
        elif output_format == "summary":
            result_text = _generate_summary(context)
        else:
            result_text = context.to_prompt_block()
        
        # Add cache indicator
        if context.from_cache:
            result_text = f"[Cached {context.cache_age_seconds}s ago]\n\n{result_text}"
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": result_text,
                }
            ],
        }
        
    except Exception as e:
        logger.error(f"get_relationship_context failed: {e}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error getting context for '{entity}': {str(e)}",
                }
            ],
            "isError": True,
        }


def _generate_summary(context) -> str:
    """Generate a brief summary of the context."""
    lines = [f"**{context.entity}** ({context.entity_type})"]
    
    # Relationship strength
    strength_emoji = "🟢" if context.relationship_strength > 0.7 else "🟡" if context.relationship_strength > 0.4 else "🔴"
    lines.append(f"{strength_emoji} Relationship: {context.engagement_level} ({context.relationship_strength:.0%})")
    
    # Urgency
    if context.urgency > 0.5:
        lines.append(f"⚡ Urgency: High ({context.urgency:.0%})")
    
    # Constitutional
    if context.constitutional_context:
        lines.append(f"⚠️ {len(context.constitutional_context)} constitutional override(s)")
    
    # Signal sources
    if context.signal_sources:
        lines.append(f"📊 Sources: {', '.join(context.signal_sources)}")
    
    # Top insight
    if context.insights:
        lines.append(f"💡 {context.insights[0]}")
    
    return "\n".join(lines)


# For direct invocation
if __name__ == "__main__":
    import asyncio
    
    # Test
    async def test():
        result = await handle_tool_call({
            "entity": "Test Person",
            "format": "prompt",
        })
        print(result["content"][0]["text"])
    
    asyncio.run(test())
