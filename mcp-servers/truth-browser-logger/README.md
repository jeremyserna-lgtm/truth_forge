# Truth Browser Logger MCP Server

MOLT LINEAGE:
- Source: Truth_Engine/mcp-servers/truth-browser-logger/
- Version: 1.0.0
- Date: 2026-01-27

---

## Purpose

MCP server that provides browser history analysis and context tools.
Extracts patterns from Chrome browser history for relationship and research context.

## Tools

| Tool | Purpose |
|------|---------|
| `get_browser_history` | Retrieve browser history entries |
| `get_browser_stats` | Get browsing statistics |
| `get_browser_context_for_entity` | Get context for a specific entity |
| `get_relationship_context` | Get relationship-related browsing context |
| `get_research_timeline` | Get research activity timeline |
| `get_session_patterns` | Analyze browsing session patterns |
| `correlate_browser_with_truth` | Correlate browser data with truth forge |
| `check_consent` | Verify consent for data access |

## Structure

```
truth-browser-logger/
├── pyproject.toml
├── README.md
└── src/
    └── truth_browser_logger/
        ├── __init__.py
        ├── server.py           # MCP server entry point
        ├── extractor.py        # History extraction
        ├── patterns.py         # Pattern detection
        ├── categories.py       # URL categorization
        ├── consent.py          # Consent management
        ├── time_utils.py       # Time utilities
        └── tools/              # MCP tool implementations
            ├── __init__.py
            ├── get_browser_history.py
            ├── get_browser_stats.py
            ├── get_browser_context_for_entity.py
            ├── get_relationship_context.py
            ├── get_research_timeline.py
            ├── get_session_patterns.py
            ├── correlate_browser_with_truth.py
            └── check_consent.py
```

## Installation

```bash
cd mcp-servers/truth-browser-logger
uv pip install -e .
```

## Configuration

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "truth-browser-logger": {
      "command": "uv",
      "args": ["run", "truth-browser-logger"]
    }
  }
}
```
