# Quick Start Guide - Spine Analysis MCP Server

## ✅ Installation Complete

The server is installed and ready to use with **24 tools** for deep BigQuery spine dataset analysis.

## 🚀 Quick Start

### 1. Verify Installation

```bash
cd /Users/jeremyserna/truth_forge
source .venv/bin/activate
cd mcp-servers/spine-analysis-mcp
python test_server.py
```

### 2. Configure MCP Client

**For Cursor** - Add to project or global MCP config:

```json
{
  "mcpServers": {
    "spine-analysis": {
      "command": "python",
      "args": ["-m", "spine_analysis_mcp.server"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account.json",
        "BQ_PROJECT_ID": "flash-clover-464719-g1",
        "BQ_DATASET_ID": "spine"
      }
    }
  }
}
```

### 3. Start Using Tools

Once configured, you can use tools like:

- **`track_source_data`** - Track data from Claude, Gemini, Codex, Cursor
- **`explore_concept`** - Deep dive into concepts like "cognitive isomorphism"
- **`analyze_temporal_trends`** - See trends over time
- **`map_relationship_network`** - Map entity relationships
- **`find_cross_source_connections`** - Find entities across sources

## 📊 All 24 Tools

See `DEPLOYMENT_SUMMARY.md` for complete list.

## 🎯 Example Queries

### Track All Data Sources
```json
{
  "tool": "track_source_data",
  "arguments": {
    "sources": ["claude_code", "claude_web", "gemini_web", "codex", "cursor"],
    "time_range": "last_30_days",
    "metrics": ["volume", "entities", "domains"]
  }
}
```

### Explore a Concept
```json
{
  "tool": "explore_concept",
  "arguments": {
    "concept": "cognitive isomorphism",
    "limit": 50
  }
}
```

### Analyze Trends
```json
{
  "tool": "analyze_temporal_trends",
  "arguments": {
    "metric": "entity_creation",
    "time_range": "last_90_days",
    "granularity": "daily",
    "group_by": "source_system"
  }
}
```

## 📚 Documentation

- **Plan**: `/docs/technical/mcp-servers/SPINE_ANALYSIS_MCP_PLAN.md`
- **Installation**: `INSTALLATION.md`
- **Deployment Summary**: `DEPLOYMENT_SUMMARY.md`
- **README**: `README.md`

---

**Status**: ✅ Ready for production use
