"""get_browser_context_for_entity tool - Get browser context for a person/entity.

Stacked amplification: Combines browser history with knowledge graph context.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

from mcp.types import Tool

from ..consent import check_consent
from ..extractor import get_extractor
from ..time_utils import resolve_time_window

# Add src to path for knowledge graph imports
_repo_root = Path(__file__).parent.parent.parent.parent.parent.parent
_src_path = _repo_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

# Tool definition
get_browser_context_for_entity_tool = Tool(
    name="get_browser_context_for_entity",
    description="""Get browser context for a person, company, or topic.

Searches browser history for visits related to the entity and combines
with knowledge graph context for comprehensive understanding.

This is a STACKED tool that amplifies by combining:
1. Browser history search for entity-related domains
2. Knowledge graph context for the entity
3. Pattern analysis of research behavior

Examples:
- get_browser_context_for_entity(entity="John Smith") → Research about John
- get_browser_context_for_entity(entity="Anthropic", days=30) → Month of Anthropic research
- get_browser_context_for_entity(entity="machine learning") → ML learning patterns
""",
    inputSchema={
        "type": "object",
        "properties": {
            "entity": {
                "type": "string",
                "description": "The person, company, or topic to get context for",
            },
            "days": {
                "type": "integer",
                "description": "Look back N days (default: 30)",
                "default": 30,
            },
            "include_graph_context": {
                "type": "boolean",
                "description": "Include knowledge graph context (default: true)",
                "default": True,
            },
        },
        "required": ["entity"],
    },
)


def handle_get_browser_context_for_entity(arguments: Dict[str, Any]) -> str:
    """Handle get_browser_context_for_entity tool call."""
    
    # Check consent
    allowed, reason = check_consent()
    if not allowed:
        return json.dumps({
            "error": "consent_required",
            "message": reason,
        }, indent=2)
    
    entity = arguments.get("entity", "").strip()
    if not entity:
        return json.dumps({"error": "entity is required"}, indent=2)
    
    days = arguments.get("days", 30)
    include_graph = arguments.get("include_graph_context", True)
    
    # Resolve time window
    since, until = resolve_time_window(days=days)
    
    # Get browser history
    extractor = get_extractor()
    all_visits = extractor.get_all_history(
        since=since,
        until=until,
        limit=5000,
    )
    
    # Filter visits that might be related to entity
    # Search in URL and title
    entity_lower = entity.lower()
    entity_parts = entity_lower.split()
    
    related_visits = []
    for visit in all_visits:
        # Check URL
        url_lower = visit.url.lower()
        title_lower = visit.title.lower()
        
        # Match if entity or any part appears
        if entity_lower in url_lower or entity_lower in title_lower:
            related_visits.append(visit)
        elif any(part in url_lower or part in title_lower for part in entity_parts if len(part) > 3):
            related_visits.append(visit)
    
    # Get knowledge graph context if requested
    graph_context = None
    if include_graph:
        try:
            from src.services.central_services.knowledge_graph_service import get_context_for
            graph_context = get_context_for(entity)
        except Exception as e:
            graph_context = {"error": f"Knowledge graph unavailable: {e}"}
    
    # Analyze patterns in related visits
    if related_visits:
        from ..patterns import PatternDetector
        detector = PatternDetector(related_visits)
        focus = detector.get_focus_score()
        sessions = detector.detect_research_sessions()
        
        pattern_summary = {
            "total_visits": len(related_visits),
            "unique_domains": len(set(v.domain for v in related_visits)),
            "research_sessions": len(sessions),
            "time_invested_minutes": sum(s.duration_minutes for s in sessions),
            "categories_touched": list(focus.time_by_category.keys()),
        }
    else:
        pattern_summary = {
            "total_visits": 0,
            "message": "No browser history found related to this entity",
        }
    
    result = {
        "entity": entity,
        "time_window": {
            "since": since.isoformat() if since else None,
            "until": until.isoformat() if until else "now",
            "days": days,
        },
        "browser_research": {
            "pattern_summary": pattern_summary,
            "recent_visits": [v.to_dict() for v in related_visits[:20]],
            "domains_researched": list(set(v.domain for v in related_visits))[:20],
        },
        "knowledge_graph_context": graph_context,
    }
    
    return json.dumps(result, indent=2)
