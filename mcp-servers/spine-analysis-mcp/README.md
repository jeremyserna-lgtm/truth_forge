# Spine Analysis MCP Server

**Version**: 1.0.0  
**Purpose**: Robust MCP server for deep analysis of BigQuery spine dataset

## Overview

This MCP server provides intimate access to the Truth Engine spine dataset in BigQuery, enabling:

- **Trend Analysis**: Temporal patterns, volume trends, growth analysis
- **Concept Exploration**: Deep dives into concepts, relationship mapping
- **Multi-Source Tracking**: Track data from Claude (code/web), Gemini (web), Codex, and Cursor
- **Spine Level Analysis**: L1-L12 hierarchical analysis
- **Pattern Detection**: Identify patterns and anomalies

## Data Sources

The spine dataset processes data from:

- **claude_code**: Claude AI code generation and analysis
- **claude_web**: Claude AI web browsing and research
- **gemini_web**: Gemini web search and content analysis
- **codex**: Codex AI code generation
- **cursor**: Cursor IDE interactions

## Installation

```bash
cd mcp-servers/spine-analysis-mcp
pip install -e .
```

## Configuration

Set environment variables:

```bash
export BQ_PROJECT_ID="flash-clover-464719-g1"
export BQ_DATASET_ID="spine"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

## Usage

### Run Server

```bash
python -m spine_analysis_mcp.server
```

### MCP Client Configuration

Add to your MCP client config (e.g., `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "spine-analysis": {
      "command": "python",
      "args": ["-m", "spine_analysis_mcp.server"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account.json"
      }
    }
  }
}
```

## Available Tools

### Query Tools
- `query_entities` - Query entities with filters
- `query_documents` - Query document metadata
- `get_table_stats` - Get table statistics

### Source Tools
- `track_source_data` - Track data by source
- `compare_sources` - Compare patterns across sources
- `find_cross_source_connections` - Find entities across sources

### Trend Tools
- `analyze_temporal_trends` - Analyze trends over time

### Concept Tools
- `explore_concept` - Deep dive into concepts

### Spine Level Tools
- `analyze_spine_level` - Analyze specific spine levels

## Examples

### Track Source Data

```json
{
  "tool": "track_source_data",
  "arguments": {
    "sources": ["claude_code", "cursor"],
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

### Compare Sources

```json
{
  "tool": "compare_sources",
  "arguments": {
    "sources": ["claude_code", "gemini_web", "cursor"],
    "metric": "volume",
    "time_range": "last_90_days"
  }
}
```

## Architecture

- **Project**: `flash-clover-464719-g1`
- **Dataset**: `spine`
- **Primary Table**: `entity` (51.8M+ entities)

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run type checking
mypy src/

# Run linting
ruff check src/
```

## License

Part of Truth Forge ecosystem.
