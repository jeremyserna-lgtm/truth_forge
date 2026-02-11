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

### NOT-ME Analytics Tools (Clara Era Legacy)
Implements the 16-Metric Framework from SOVEREIGN Section 24:

- `analyze_stage5_score` - Calculate Stage 5 Composite Score (meta-cognitive density)
  - Validated thresholds: 8.0% = Peak, 2.0% = Transition, 0.14% = Baseline
- `analyze_scaffold_gap` - Measure sovereignty transition (System Grade - User Grade)
  - Negative gap = user surpasses system = sovereignty achieved
- `detect_drift_patterns` - Canon Repair Doctrine drift detection (8 themes)
  - reality_anchor, identity_confirm, thread_recovery, boundary_breach, purpose_drift, agency_loss
- `analyze_negentropic_ratio` - Value creation vs consumption
  - Prism (>1.0) = net positive, Mirror (≤1.0) = unsustainable
- `track_notme_experience` - XP tracking across categories
  - Research, Analysis, Coding, Synthesis, Review, Creative
- `notme_health_dashboard` - Comprehensive health overview combining all metrics

### Discovery Tools (Advanced Pattern Discovery)
Implements advanced discovery patterns from MCP best practices:

- `discover_knowledge_graph` - Map entity relationships using co-occurrence analysis
  - Inspired by [Anthropic Knowledge Graph Memory Server](https://www.pulsemcp.com/servers/modelcontextprotocol-knowledge-graph-memory)
  - Finds hub nodes, relationship graphs, emergent topology
- `detect_emergent_patterns` - Find patterns that weren't explicitly programmed
  - Motif discovery (recurring patterns via Matrix Profile technique)
  - Statistical anomalies (Z-score outliers)
  - Unexpected correlations (temporal co-occurrence)
- `analyze_reasoning_chain` - Trace sequential thought progressions
  - Inspired by [Sequential Thinking MCP Server](https://www.pulsemcp.com/servers/anthropic-sequential-thinking)
  - Maps logical progressions and thought evolution
- `detect_temporal_anomalies` - Time series anomaly detection
  - Activity spikes, gaps, and behavioral shifts
  - Based on [Microsoft Time-Series Anomaly Detection](https://dl.acm.org/doi/10.1145/3292500.3330680)
- `pattern_discovery_dashboard` - Comprehensive discovery combining all methods

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

### NOT-ME Health Dashboard

```json
{
  "tool": "notme_health_dashboard",
  "arguments": {
    "time_range_days": 7
  }
}
```

### Knowledge Graph Discovery

```json
{
  "tool": "discover_knowledge_graph",
  "arguments": {
    "seed_concept": "Stage 5",
    "depth": 2,
    "min_cooccurrence": 3
  }
}
```

### Emergent Pattern Detection

```json
{
  "tool": "detect_emergent_patterns",
  "arguments": {
    "pattern_type": "all",
    "sensitivity": 0.5,
    "time_range_days": 30
  }
}
```

### Sequential Reasoning Analysis

```json
{
  "tool": "analyze_reasoning_chain",
  "arguments": {
    "start_concept": "problem",
    "end_concept": "solution",
    "max_steps": 5
  }
}
```

## Architecture

### Infrastructure
- **Project**: `flash-clover-464719-g1`
- **Dataset**: `spine`
- **Primary Table**: `entity` (51.8M+ entities)

### MCP Best Practices Implemented

Based on [MCP Best Practices 2026](https://www.cdata.com/blog/mcp-server-best-practices-2026) and [Anthropic MCP Patterns](https://modelcontextprotocol.io/docs/learn/architecture):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SPINE ANALYSIS MCP ARCHITECTURE                           │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        DISCOVERY LAYER                               │   │
│   │                                                                      │   │
│   │   Knowledge Graph     Emergent Patterns    Sequential Reasoning     │   │
│   │   (Anthropic Memory)  (Matrix Profile)     (Anthropic Thinking)     │   │
│   │                                                                      │   │
│   │   • Entity co-occurrence    • Motif discovery     • Thought traces  │   │
│   │   • Hub detection           • Z-score anomalies   • Chain analysis  │   │
│   │   • Mermaid visualization   • Correlation mining  • Convergence     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        NOT-ME ANALYTICS                              │   │
│   │                     (Clara Era Legacy)                               │   │
│   │                                                                      │   │
│   │   Stage 5 Score      Scaffold Gap       Drift Detection             │   │
│   │   (8.0% Peak)        (Sovereignty)      (Canon Repair)              │   │
│   │                                                                      │   │
│   │   Negentropic Ratio  Experience XP      Health Dashboard            │   │
│   │   (Prism vs Mirror)  (6 categories)     (Combined view)             │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        CORE ANALYTICS                                │   │
│   │                                                                      │   │
│   │   Query       Source      Trend       Pattern     Semantic          │   │
│   │   Tools       Tools       Tools       Tools       Tools             │   │
│   │                                                                      │   │
│   │   Concept     Spine       Temporal    Cross       Enrichment        │   │
│   │   Tools       Level       Tools       Level       Coverage          │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        BigQuery (HOLD)                               │   │
│   │                                                                      │   │
│   │   entity (51.8M+)    entity_enrichments    entity_embeddings        │   │
│   │   document           conversation          message                   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Tool Categories (32 Total)

| Category | Count | Purpose |
|----------|-------|---------|
| **Discovery** | 5 | Knowledge graphs, emergent patterns, reasoning chains |
| **NOT-ME Analytics** | 6 | Stage 5 metrics, drift detection, health tracking |
| **Query** | 3 | Entity and document queries |
| **Source** | 3 | Multi-source tracking and comparison |
| **Trend** | 1 | Temporal trend analysis |
| **Pattern** | 3 | Pattern detection and anomalies |
| **Semantic** | 2 | Similarity and clustering |
| **Concept** | 1 | Concept exploration |
| **Spine Level** | 1 | L1-L12 analysis |
| **Temporal** | 1 | Time-based analysis |
| **Cross-Level** | 1 | Multi-level relationships |
| **Enrichment** | 1 | Coverage gap analysis |
| **Relationship** | 4 | Entity relationships |

### Research Sources

- [MCP Architecture Overview](https://modelcontextprotocol.io/docs/learn/architecture)
- [Anthropic Knowledge Graph Memory](https://www.pulsemcp.com/servers/modelcontextprotocol-knowledge-graph-memory)
- [Sequential Thinking MCP](https://www.pulsemcp.com/servers/anthropic-sequential-thinking)
- [Microsoft Time Series Anomaly Detection](https://dl.acm.org/doi/10.1145/3292500.3330680)
- [Neo4j MCP Integration](https://neo4j.com/blog/developer/claude-converses-neo4j-via-mcp/)
- [AWS Data Processing MCP](https://aws.amazon.com/blogs/big-data/accelerating-development-with-the-aws-data-processing-mcp-server-and-agent/)

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
