# Spine Analysis MCP Server - Installation & Setup

## Prerequisites

1. **Python 3.12+** installed
2. **Google Cloud credentials** configured
3. **BigQuery access** to `flash-clover-464719-g1.spine` dataset

## Installation

### 1. Activate Virtual Environment

```bash
cd /Users/jeremyserna/truth_forge
source .venv/bin/activate
```

### 2. Install the Server

```bash
cd mcp-servers/spine-analysis-mcp
pip install -e .
```

### 3. Verify Installation

```bash
python test_server.py
```

Expected output:
```
✅ BigQuery client created successfully
✅ Query tools: 3 tools
✅ Source tools: 3 tools
✅ Total tools tested: 6
✅ Testing tool: query_entities
✅ Query executed successfully
```

## Configuration

### Environment Variables

Set these in your shell or MCP client configuration:

```bash
export BQ_PROJECT_ID="flash-clover-464719-g1"
export BQ_DATASET_ID="spine"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### Verify BigQuery Access

```bash
python -c "from spine_analysis_mcp.config import get_bigquery_client; client = get_bigquery_client(); print('✅ Connected to', client.project)"
```

## Running the Server

### Standalone Test

```bash
python -m spine_analysis_mcp.server
```

The server will start and wait for MCP protocol messages on stdin/stdout.

### With MCP Client (Cursor/Codex)

Add to your MCP client configuration:

**For Cursor** (`~/.cursor/mcp.json` or project config):
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

**For Codex** (`~/.codex/config.toml`):
```toml
[mcp_servers.spine-analysis]
command = "python"
args = ["-m", "spine_analysis_mcp.server"]
env = {
  GOOGLE_APPLICATION_CREDENTIALS = "/path/to/service-account.json"
  BQ_PROJECT_ID = "flash-clover-464719-g1"
  BQ_DATASET_ID = "spine"
}
```

## Available Tools

The server provides **30+ tools** across 10 categories:

### Query Tools (3)
- `query_entities` - Query entities with filters
- `query_documents` - Query document metadata
- `get_table_stats` - Get table statistics

### Source Tools (3)
- `track_source_data` - Track data by source
- `compare_sources` - Compare patterns across sources
- `find_cross_source_connections` - Find entities across sources

### Trend Tools (1)
- `analyze_temporal_trends` - Analyze trends over time

### Concept Tools (1)
- `explore_concept` - Deep dive into concepts

### Spine Level Tools (1)
- `analyze_spine_level` - Analyze specific spine levels

### Relationship Tools (4)
- `find_entity_relationships` - Find all relationships for an entity
- `map_relationship_network` - Map relationship networks (multi-hop)
- `find_relationship_paths` - Find paths between entities
- `analyze_relationship_patterns` - Analyze common patterns

### Temporal Tools (4)
- `analyze_temporal_patterns` - Analyze patterns in time
- `find_temporal_clusters` - Find activity bursts
- `analyze_activity_cycles` - Analyze cyclical patterns
- `track_temporal_evolution` - Track metric evolution

### Pattern Tools (3)
- `detect_patterns` - Detect patterns in data
- `identify_pattern_anomalies` - Identify outliers
- `find_repeating_patterns` - Find repeating sequences

### Semantic Tools (2)
- `find_similar_entities` - Find semantically similar entities
- `extract_concept_clusters` - Identify concept clusters

### Cross-Level Tools (2)
- `analyze_cross_level_distribution` - Analyze distribution across levels
- `find_level_relationships` - Find relationships between levels

## Troubleshooting

### BigQuery Authentication Error

```
Error: google.auth.exceptions.DefaultCredentialsError
```

**Solution**: Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### Import Errors

```
ModuleNotFoundError: No module named 'spine_analysis_mcp'
```

**Solution**: Install in editable mode:
```bash
pip install -e .
```

### Query Timeout

If queries are timing out, increase the timeout in `config.py` or optimize queries with filters.

## Next Steps

1. **Test with sample queries** using the MCP client
2. **Explore the dataset** using `query_entities` and `get_table_stats`
3. **Track data sources** using `track_source_data`
4. **Analyze trends** using `analyze_temporal_trends`
5. **Explore concepts** using `explore_concept`

## Support

For issues or questions, see:
- Plan: `/docs/technical/mcp-servers/SPINE_ANALYSIS_MCP_PLAN.md`
- README: `README.md`
