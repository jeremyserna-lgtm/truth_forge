"""correlate_browser_with_truth tool - Correlate browser visits with AI conversations.

Stacked amplification: Combines browser history with Truth Service conversations.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from mcp.types import Tool

from ..consent import check_consent
from ..extractor import BrowserVisit, get_extractor
from ..time_utils import resolve_time_window

# Add src to path
_repo_root = Path(__file__).parent.parent.parent.parent.parent.parent
_src_path = _repo_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

# Tool definition
correlate_browser_with_truth_tool = Tool(
    name="correlate_browser_with_truth",
    description="""Correlate browser visits with AI conversations from the same time period.

This STACKED tool reveals connections between what you researched and what you
discussed with AI, enabling powerful insights like:
- What you looked up before asking AI
- What AI suggested that you then researched
- Learning patterns across browser + AI

Examples:
- correlate_browser_with_truth(hours=4) → Last 4 hours correlation
- correlate_browser_with_truth(category="coding", hours=8) → Coding research + AI
""",
    inputSchema={
        "type": "object",
        "properties": {
            "hours": {
                "type": "integer",
                "description": "Correlate last N hours (default: 4)",
                "default": 4,
            },
            "category": {
                "type": "string",
                "description": "Filter browser visits by category",
            },
            "correlation_window_minutes": {
                "type": "integer",
                "description": "Time window for correlation (default: 30 min)",
                "default": 30,
            },
        },
    },
)


def handle_correlate_browser_with_truth(arguments: Dict[str, Any]) -> str:
    """Handle correlate_browser_with_truth tool call."""
    
    # Check consent
    allowed, reason = check_consent()
    if not allowed:
        return json.dumps({
            "error": "consent_required",
            "message": reason,
        }, indent=2)
    
    hours = arguments.get("hours", 4)
    category = arguments.get("category")
    window_minutes = arguments.get("correlation_window_minutes", 30)
    
    # Resolve time window
    since, until = resolve_time_window(hours=hours)
    
    # Get browser history
    extractor = get_extractor()
    visits = extractor.get_all_history(
        since=since,
        until=until,
        limit=1000,
        category_filter=category,
    )
    
    # Get AI conversations from Truth Service
    conversations = []
    try:
        from src.services.central_services.truth import TruthService
        truth = TruthService()
        
        for entry in truth.iter_entries(
            since=since,
            until=until,
            limit=500,
        ):
            conversations.append({
                "timestamp": entry.timestamp,
                "agent": entry.agent,
                "role": entry.role.value,
                "content_preview": entry.content[:200] if entry.content else "",
            })
    except Exception as e:
        conversations = []
        truth_error = str(e)
    else:
        truth_error = None
    
    # Correlate: Find browser visits near AI conversations
    correlations = []
    
    from datetime import timedelta
    window = timedelta(minutes=window_minutes)
    
    for visit in visits:
        related_convos = []
        for conv in conversations:
            time_diff = abs((visit.visit_time - conv["timestamp"]).total_seconds())
            if time_diff <= window.total_seconds():
                related_convos.append({
                    **conv,
                    "time_diff_seconds": time_diff,
                    "timestamp": conv["timestamp"].isoformat(),
                })
        
        if related_convos:
            correlations.append({
                "visit": visit.to_dict(),
                "related_conversations": sorted(
                    related_convos,
                    key=lambda x: x["time_diff_seconds"]
                )[:5],  # Top 5 closest
            })
    
    # Build summary
    result = {
        "time_window": {
            "since": since.isoformat() if since else None,
            "until": until.isoformat() if until else "now",
            "hours": hours,
        },
        "correlation_window_minutes": window_minutes,
        "summary": {
            "total_visits": len(visits),
            "total_conversations": len(conversations),
            "correlated_visits": len(correlations),
            "correlation_rate": f"{len(correlations) / len(visits) * 100:.1f}%" if visits else "0%",
        },
        "correlations": correlations[:50],  # Limit output
        "truth_service_error": truth_error,
    }
    
    return json.dumps(result, indent=2, default=str)
