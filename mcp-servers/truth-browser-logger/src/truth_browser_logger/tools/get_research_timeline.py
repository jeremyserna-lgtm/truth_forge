"""get_research_timeline tool - Build comprehensive research timeline.

Stacked amplification: Combines browser history + AI conversations + knowledge graph.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from mcp.types import Tool

from ..consent import check_consent
from ..extractor import get_extractor
from ..time_utils import resolve_time_window

# Add src to path
_repo_root = Path(__file__).parent.parent.parent.parent.parent.parent
_src_path = _repo_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

# Tool definition
get_research_timeline_tool = Tool(
    name="get_research_timeline",
    description="""Build a comprehensive research timeline for a topic.

This STACKED tool creates a chronological view of learning by combining:
1. Browser history (what you looked up)
2. AI conversations (what you asked/learned)
3. Knowledge graph (entities and relationships)

Perfect for understanding how your knowledge evolved on a topic.

Examples:
- get_research_timeline(topic="kubernetes", days=30) → K8s learning journey
- get_research_timeline(topic="RAG systems", days=7) → RAG research this week
""",
    inputSchema={
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic to build a timeline for",
            },
            "days": {
                "type": "integer",
                "description": "Look back N days (default: 14)",
                "default": 14,
            },
        },
        "required": ["topic"],
    },
)


def handle_get_research_timeline(arguments: Dict[str, Any]) -> str:
    """Handle get_research_timeline tool call."""
    
    # Check consent
    allowed, reason = check_consent()
    if not allowed:
        return json.dumps({
            "error": "consent_required",
            "message": reason,
        }, indent=2)
    
    topic = arguments.get("topic", "").strip()
    if not topic:
        return json.dumps({"error": "topic is required"}, indent=2)
    
    days = arguments.get("days", 14)
    
    # Resolve time window
    since, until = resolve_time_window(days=days)
    
    # Build timeline events
    timeline_events = []
    topic_lower = topic.lower()
    topic_parts = [p for p in topic_lower.split() if len(p) > 3]
    
    # 1. Get browser history
    extractor = get_extractor()
    visits = extractor.get_all_history(
        since=since,
        until=until,
        limit=2000,
    )
    
    # Filter relevant visits
    for visit in visits:
        url_lower = visit.url.lower()
        title_lower = visit.title.lower()
        
        if topic_lower in url_lower or topic_lower in title_lower:
            timeline_events.append({
                "timestamp": visit.visit_time,
                "type": "browser",
                "source": visit.browser,
                "domain": visit.domain,
                "category": visit.category,
                "title": visit.title[:100],
                "url": visit.url,
            })
        elif any(p in url_lower or p in title_lower for p in topic_parts):
            timeline_events.append({
                "timestamp": visit.visit_time,
                "type": "browser",
                "source": visit.browser,
                "domain": visit.domain,
                "category": visit.category,
                "title": visit.title[:100],
                "url": visit.url,
            })
    
    # 2. Get AI conversations
    try:
        from src.services.central_services.truth import TruthService
        truth = TruthService()
        
        for entry in truth.iter_entries(
            since=since,
            until=until,
            limit=1000,
        ):
            content_lower = (entry.content or "").lower()
            if topic_lower in content_lower or any(p in content_lower for p in topic_parts):
                timeline_events.append({
                    "timestamp": entry.timestamp,
                    "type": "ai_conversation",
                    "source": entry.agent,
                    "role": entry.role.value,
                    "content_preview": entry.content[:200] if entry.content else "",
                })
    except Exception as e:
        pass  # Truth service unavailable
    
    # 3. Get knowledge graph context
    graph_entities = []
    try:
        from src.services.central_services.knowledge_graph_service import inhale
        graph_result = inhale(topic)
        if graph_result:
            graph_entities = graph_result.get("nodes", [])[:10]
    except Exception:
        pass
    
    # Sort timeline by timestamp
    timeline_events.sort(key=lambda x: x["timestamp"])
    
    # Group by day for summary
    daily_summary = defaultdict(lambda: {"browser": 0, "ai": 0, "domains": set()})
    for event in timeline_events:
        day = event["timestamp"].strftime("%Y-%m-%d")
        if event["type"] == "browser":
            daily_summary[day]["browser"] += 1
            daily_summary[day]["domains"].add(event.get("domain", ""))
        else:
            daily_summary[day]["ai"] += 1
    
    # Convert sets to lists for JSON
    for day in daily_summary:
        daily_summary[day]["domains"] = list(daily_summary[day]["domains"])
    
    # Format events for output
    formatted_events = []
    for event in timeline_events:
        formatted = {
            **event,
            "timestamp": event["timestamp"].isoformat(),
        }
        formatted_events.append(formatted)
    
    result = {
        "topic": topic,
        "time_window": {
            "since": since.isoformat() if since else None,
            "until": until.isoformat() if until else "now",
            "days": days,
        },
        "summary": {
            "total_events": len(timeline_events),
            "browser_visits": sum(1 for e in timeline_events if e["type"] == "browser"),
            "ai_conversations": sum(1 for e in timeline_events if e["type"] == "ai_conversation"),
            "unique_domains": len(set(e.get("domain") for e in timeline_events if e.get("domain"))),
            "days_active": len(daily_summary),
        },
        "daily_breakdown": dict(daily_summary),
        "knowledge_graph_entities": graph_entities,
        "timeline": formatted_events[:100],  # Limit output
    }
    
    return json.dumps(result, indent=2)
