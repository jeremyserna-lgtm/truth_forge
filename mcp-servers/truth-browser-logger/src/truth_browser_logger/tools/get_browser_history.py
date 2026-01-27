"""get_browser_history tool - Query browser history with time-bounding and filters.

Examples:
    get_browser_history(hours=1)  # Last hour across all browsers
    get_browser_history(browser="chrome", days=7)  # Last week of Chrome
    get_browser_history(category="coding", hours=4)  # Coding sites, last 4 hours
    get_browser_history(domain="github.com", days=30)  # GitHub visits this month
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from mcp.types import Tool

from ..consent import check_consent
from ..extractor import get_extractor
from ..time_utils import period_help, resolve_time_window

# Tool definition
get_browser_history_tool = Tool(
    name="get_browser_history",
    description=f"""Query browser history from Chrome and Safari with time-bounding and filters.

Requires consent to be enabled in config/browser_history_consent.json.

Time-bounding examples:
- get_browser_history(hours=1) → Last hour of browsing
- get_browser_history(days=7, browser="chrome") → Last week, Chrome only
- get_browser_history(period="today") → Today's browsing

Filter examples:
- get_browser_history(category="coding", hours=4) → Coding sites (GitHub, SO, etc.)
- get_browser_history(domain="github.com") → GitHub visits only

Available browsers: chrome, safari (or omit for both)
Available categories: coding, research, documentation, ai_ml, business, communication, collaboration, learning, finance, news, social, cloud

{period_help()}
""",
    inputSchema={
        "type": "object",
        "properties": {
            "period": {
                "type": "string",
                "description": f"Named time period. {period_help()}",
            },
            "browser": {
                "type": "string",
                "description": "Filter by browser: chrome, safari (default: both)",
                "enum": ["chrome", "safari"],
            },
            "domain": {
                "type": "string",
                "description": "Filter by domain (partial match, e.g., 'github' matches github.com)",
            },
            "category": {
                "type": "string",
                "description": "Filter by category: coding, research, documentation, ai_ml, business, communication, learning, etc.",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum results (default: 100)",
                "default": 100,
            },
            "minutes": {
                "type": "integer",
                "description": "Get history from last N minutes",
            },
            "hours": {
                "type": "integer",
                "description": "Get history from last N hours",
            },
            "days": {
                "type": "integer",
                "description": "Get history from last N days",
            },
            "since": {
                "type": "string",
                "description": "ISO timestamp for start of window",
            },
            "until": {
                "type": "string",
                "description": "ISO timestamp for end of window",
            },
        },
    },
)


def handle_get_browser_history(arguments: Dict[str, Any]) -> str:
    """Handle get_browser_history tool call."""
    
    # Check consent first
    allowed, reason = check_consent()
    if not allowed:
        return json.dumps({
            "error": "consent_required",
            "message": reason,
        }, indent=2)
    
    # Resolve time window
    since, until = resolve_time_window(
        period=arguments.get("period"),
        since=arguments.get("since"),
        until=arguments.get("until"),
        minutes=arguments.get("minutes"),
        hours=arguments.get("hours"),
        days=arguments.get("days"),
    )
    
    # Get parameters
    browser = arguments.get("browser")
    domain_filter = arguments.get("domain")
    category_filter = arguments.get("category")
    limit = arguments.get("limit", 100)
    
    # Extract history
    extractor = get_extractor()
    visits = extractor.get_all_history(
        since=since,
        until=until,
        limit=limit,
        browser=browser,
        domain_filter=domain_filter,
        category_filter=category_filter,
    )
    
    # Format result
    result = {
        "count": len(visits),
        "time_window": {
            "since": since.isoformat() if since else None,
            "until": until.isoformat() if until else "now",
        },
        "filters": {
            "browser": browser,
            "domain": domain_filter,
            "category": category_filter,
        },
        "visits": [v.to_dict() for v in visits],
    }
    
    return json.dumps(result, indent=2)
