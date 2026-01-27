"""get_session_patterns tool - Detect browsing patterns and focus metrics.

Analyzes browser history to identify research sessions, deep dives,
context switches, and compute focus scores.
"""
from __future__ import annotations

import json
from typing import Any, Dict

from mcp.types import Tool

from ..consent import check_consent
from ..extractor import get_extractor
from ..patterns import PatternDetector
from ..time_utils import period_help, resolve_time_window

# Tool definition
get_session_patterns_tool = Tool(
    name="get_session_patterns",
    description=f"""Analyze browser history to detect patterns and compute focus metrics.

Detects:
- Research sessions: Clustered browsing activity by time and topic
- Deep dives: Extended time (10+ min) on single domains
- Context switches: Rapid domain changes (potential distraction)
- Focus score: Composite metric (0-100) of browsing focus

Time-bounding: {period_help()}

Examples:
- get_session_patterns(hours=4) → Analyze last 4 hours
- get_session_patterns(period="today") → Today's patterns
- get_session_patterns(days=7) → Week's patterns
""",
    inputSchema={
        "type": "object",
        "properties": {
            "period": {
                "type": "string",
                "description": f"Named time period. {period_help()}",
            },
            "hours": {
                "type": "integer",
                "description": "Analyze last N hours",
            },
            "days": {
                "type": "integer",
                "description": "Analyze last N days",
            },
            "include_visits": {
                "type": "boolean",
                "description": "Include individual visits in session details (default: false)",
                "default": False,
            },
        },
    },
)


def handle_get_session_patterns(arguments: Dict[str, Any]) -> str:
    """Handle get_session_patterns tool call."""
    
    # Check consent
    allowed, reason = check_consent()
    if not allowed:
        return json.dumps({
            "error": "consent_required",
            "message": reason,
        }, indent=2)
    
    # Resolve time window
    since, until = resolve_time_window(
        period=arguments.get("period"),
        hours=arguments.get("hours"),
        days=arguments.get("days"),
    )
    
    include_visits = arguments.get("include_visits", False)
    
    # Get history
    extractor = get_extractor()
    visits = extractor.get_all_history(
        since=since,
        until=until,
        limit=5000,  # Need more for pattern detection
    )
    
    if not visits:
        return json.dumps({
            "error": "no_data",
            "message": "No browser history found in time window",
            "time_window": {
                "since": since.isoformat() if since else None,
                "until": until.isoformat() if until else "now",
            },
        }, indent=2)
    
    # Detect patterns
    detector = PatternDetector(visits)
    
    sessions = detector.detect_research_sessions()
    deep_dives = detector.detect_deep_dives()
    switches = detector.detect_context_switches()
    focus = detector.get_focus_score()
    
    # Build result
    sessions_data = []
    for s in sessions:
        session_dict = s.to_dict()
        if include_visits:
            session_dict["visits"] = [v.to_dict() for v in s.visits]
        sessions_data.append(session_dict)
    
    result = {
        "time_window": {
            "since": since.isoformat() if since else None,
            "until": until.isoformat() if until else "now",
        },
        "total_visits_analyzed": len(visits),
        "focus_metrics": focus.to_dict(),
        "research_sessions": sessions_data,
        "deep_dives": [d.to_dict() for d in deep_dives],
        "context_switches": [s.to_dict() for s in switches[:50]],  # Limit switches
        "context_switch_total": len(switches),
    }
    
    return json.dumps(result, indent=2)
