"""check_consent tool - Check browser history consent status.

Reports consent configuration without extracting any data.
"""
from __future__ import annotations

import json
from typing import Any, Dict

from mcp.types import Tool

from ..consent import get_consent_status

# Tool definition
check_consent_tool = Tool(
    name="check_browser_consent",
    description="""Check the current consent status for browser history extraction.

Returns:
- Whether consent is granted
- Number of excluded domains
- Paths to configuration files

Use this before attempting to access browser history.
""",
    inputSchema={
        "type": "object",
        "properties": {},
    },
)


def handle_check_consent(arguments: Dict[str, Any]) -> str:
    """Handle check_consent tool call."""
    status = get_consent_status()
    return json.dumps(status, indent=2)
