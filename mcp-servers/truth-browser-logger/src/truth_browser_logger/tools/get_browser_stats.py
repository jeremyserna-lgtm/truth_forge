"""get_browser_stats tool - Statistics about available browser history.

Provides overview of history without extracting individual visits.
"""
from __future__ import annotations

import json
from collections import Counter
from typing import Any, Dict

from mcp.types import Tool

from ..consent import check_consent
from ..extractor import get_extractor
from ..time_utils import resolve_time_window

# Tool definition
get_browser_stats_tool = Tool(
    name="get_browser_stats",
    description="""Get statistics about available browser history without extracting individual visits.

Returns:
- Total visit counts per browser
- Unique domain counts
- Top domains by visit frequency
- Category breakdown (coding, research, etc.)
- Date range of available history

Useful for understanding browsing patterns before detailed queries.
""",
    inputSchema={
        "type": "object",
        "properties": {
            "period": {
                "type": "string",
                "description": "Named time period: today, yesterday, this_week, this_month, last_hour",
            },
            "browser": {
                "type": "string",
                "description": "Specific browser: chrome, safari (default: both)",
                "enum": ["chrome", "safari"],
            },
            "days": {
                "type": "integer",
                "description": "Get stats from last N days (default: 7)",
                "default": 7,
            },
        },
    },
)


def handle_get_browser_stats(arguments: Dict[str, Any]) -> str:
    """Handle get_browser_stats tool call."""
    
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
        days=arguments.get("days", 7),
    )
    
    browser = arguments.get("browser")
    
    # Get extractor
    extractor = get_extractor()
    
    # Check available browsers
    available = extractor.get_available_browsers()
    
    # Get visits for stats (use higher limit for stats)
    visits = extractor.get_all_history(
        since=since,
        until=until,
        limit=5000,
        browser=browser,
    )
    
    if not visits:
        return json.dumps({
            "available_browsers": available,
            "total_visits": 0,
            "message": "No visits found in time window",
            "time_window": {
                "since": since.isoformat() if since else None,
                "until": until.isoformat() if until else "now",
            },
        }, indent=2)
    
    # Calculate stats
    domains = Counter(v.domain for v in visits)
    categories = Counter(v.category for v in visits if v.category)
    browsers = Counter(v.browser for v in visits)
    
    # Get date range
    visit_times = [v.visit_time for v in visits]
    earliest = min(visit_times)
    latest = max(visit_times)
    
    result = {
        "available_browsers": available,
        "total_visits": len(visits),
        "unique_domains": len(domains),
        "date_range": {
            "earliest": earliest.isoformat(),
            "latest": latest.isoformat(),
        },
        "visits_by_browser": dict(browsers),
        "top_domains": dict(domains.most_common(20)),
        "category_breakdown": dict(categories),
        "time_window": {
            "since": since.isoformat() if since else None,
            "until": until.isoformat() if until else "now",
        },
    }
    
    return json.dumps(result, indent=2)
