# BigQuery Spine Dataset Analysis MCP Server - Implementation Plan

**Version**: 1.0.0  
**Date**: 2026-01-27  
**Status**: Implementation Ready  
**Purpose**: Robust MCP server for intimate analysis of BigQuery spine dataset with trend detection, concept exploration, and multi-source data tracking

---

## Executive Summary

This MCP server provides deep, intimate access to the Truth Engine spine dataset in BigQuery. It enables trend analysis, concept exploration, and comprehensive data source tracking across Claude (code/web), Gemini (web), Codex, and Cursor data streams.

**Key Capabilities:**
- Intimate data viewing and exploration
- Trend detection across time, entities, and concepts
- Multi-source data tracking and correlation
- L1-L12 spine level analysis
- Concept relationship mapping
- Temporal pattern analysis

---

## Data Sources Being Processed

The spine dataset is continuously expanding through processing of:

### 1. **Claude Code Data**
- Source: Claude AI code generation and analysis sessions
- Content: Code patterns, architectural decisions, implementation strategies
- Processing: Extracted code blocks, comments, refactoring patterns
- Metadata: File paths, languages, complexity metrics

### 2. **Claude Web Data**
- Source: Claude AI web browsing and research sessions
- Content: Web page content, research findings, information synthesis
- Processing: Extracted text, links, citations, research patterns
- Metadata: URLs, domains, access timestamps, relevance scores

### 3. **Gemini Web Data**
- Source: Google Gemini web search and content analysis
- Content: Search results, web content analysis, information extraction
- Processing: Structured data extraction, entity recognition, semantic analysis
- Metadata: Search queries, result rankings, confidence scores

### 4. **Codex Data**
- Source: Codex AI code generation and analysis
- Content: Code generation patterns, codebase understanding, refactoring suggestions
- Processing: Code structure analysis, dependency mapping, pattern recognition
- Metadata: Project contexts, code metrics, generation strategies

### 5. **Cursor Data**
- Source: Cursor IDE interactions and code editing
- Content: Editor commands, code changes, file operations, AI interactions
- Processing: Edit patterns, command sequences, workflow analysis
- Metadata: File operations, timestamps, command types, AI model interactions

**All data sources feed into the unified spine dataset, maintaining source attribution and enabling cross-source correlation analysis.**

---

## Architecture

### MCP Server Structure

```
spine-analysis-mcp/
├── pyproject.toml              # Project configuration
├── README.md                   # Server documentation
├── src/
│   └── spine_analysis_mcp/
│       ├── __init__.py
│       ├── server.py           # Main MCP server
│       ├── config.py           # BigQuery configuration
│       └── tools/
│           ├── __init__.py
│           ├── query_tools.py          # Basic query tools
│           ├── trend_tools.py          # Trend analysis
│           ├── concept_tools.py        # Concept exploration
│           ├── source_tools.py         # Data source tracking
│           ├── spine_level_tools.py    # L1-L12 analysis
│           ├── relationship_tools.py    # Entity relationships
│           ├── temporal_tools.py       # Time-based analysis
│           └── pattern_tools.py         # Pattern detection
```

### BigQuery Configuration

- **Project**: `flash-clover-464719-g1`
- **Dataset**: `spine`
- **Primary Tables**:
  - `entity` - Core entity table (L1-L12)
  - `document` - Document metadata and content
  - `message` - Conversation messages
  - `conversation` - Conversation metadata
  - `turn` - Conversation turns
  - `topic_segment` - Topic segments
  - `phase` - Phase tracking
  - `entity_relationship` - Cross-entity relationships
  - `person` - User identity
  - `persona_evolution` - Persona change tracking
  - `project` - Workspace projects
  - `workspace` - Workspace metadata

---

## Tool Categories

### 1. Query Tools (`query_tools.py`)

**Basic data access and exploration**

- `query_entities` - Query entities with filters
- `query_documents` - Query document metadata and content
- `query_messages` - Query conversation messages
- `query_conversations` - Query conversation metadata
- `query_relationships` - Query entity relationships
- `get_entity_details` - Get detailed entity information
- `get_table_schema` - Get BigQuery table schemas
- `get_table_stats` - Get table statistics (row counts, sizes)

### 2. Trend Tools (`trend_tools.py`)

**Temporal and volume trend analysis**

- `analyze_temporal_trends` - Analyze trends over time
- `analyze_entity_growth` - Track entity creation over time
- `analyze_source_volume` - Compare data volumes by source
- `analyze_concept_frequency` - Track concept mentions over time
- `analyze_domain_activity` - Track activity by domain
- `detect_anomalies` - Detect unusual patterns or spikes
- `compare_periods` - Compare metrics across time periods

### 3. Concept Tools (`concept_tools.py`)

**Deep concept exploration and mapping**

- `explore_concept` - Deep dive into a specific concept
- `find_concept_mentions` - Find all mentions of a concept
- `map_concept_relationships` - Map relationships around a concept
- `analyze_concept_evolution` - Track how concepts evolve
- `find_similar_concepts` - Find semantically similar concepts
- `extract_concept_clusters` - Identify concept clusters
- `analyze_concept_cooccurrence` - Find concepts that appear together

### 4. Source Tools (`source_tools.py`)

**Multi-source data tracking and correlation**

- `track_source_data` - Track data by source (Claude code/web, Gemini web, Codex, Cursor)
- `compare_sources` - Compare patterns across sources
- `correlate_sources` - Find correlations between sources
- `analyze_source_patterns` - Analyze patterns specific to each source
- `track_source_evolution` - Track how each source's data evolves
- `find_cross_source_connections` - Find connections across sources
- `analyze_source_quality` - Assess data quality by source

### 5. Spine Level Tools (`spine_level_tools.py`)

**L1-L12 hierarchical analysis**

- `analyze_spine_level` - Analyze entities at a specific spine level
- `traverse_spine_hierarchy` - Navigate up/down spine levels
- `analyze_level_distribution` - Distribution of entities across levels
- `find_level_relationships` - Relationships between levels
- `analyze_level_evolution` - How entities move between levels
- `get_level_statistics` - Statistics for each spine level

### 6. Relationship Tools (`relationship_tools.py`)

**Entity relationship analysis**

- `find_entity_relationships` - Find all relationships for an entity
- `map_relationship_network` - Map relationship networks
- `analyze_relationship_strength` - Analyze relationship strength
- `find_relationship_paths` - Find paths between entities
- `analyze_relationship_patterns` - Common relationship patterns
- `track_relationship_evolution` - How relationships change over time

### 7. Temporal Tools (`temporal_tools.py`)

**Time-based analysis and patterns**

- `analyze_temporal_patterns` - Patterns in time
- `find_temporal_clusters` - Clusters of activity in time
- `analyze_activity_cycles` - Cyclical patterns (daily, weekly, etc.)
- `compare_time_periods` - Compare different time periods
- `track_temporal_evolution` - Track changes over time
- `predict_temporal_trends` - Predict future trends (if applicable)

### 8. Pattern Tools (`pattern_tools.py`)

**Pattern detection and analysis**

- `detect_patterns` - Detect patterns in data
- `find_repeating_patterns` - Find repeating sequences
- `analyze_pattern_frequency` - How often patterns occur
- `identify_pattern_anomalies` - Unusual pattern occurrences
- `map_pattern_relationships` - Relationships between patterns
- `track_pattern_evolution` - How patterns change over time

---

## Implementation Details

### Technology Stack

- **Language**: Python 3.12+
- **MCP Framework**: `mcp>=1.0.0`
- **BigQuery Client**: `google-cloud-bigquery>=3.0.0`
- **Data Analysis**: `pandas>=2.0.0` (for result processing)
- **Type Checking**: `mypy>=1.0` (strict mode)
- **Linting**: `ruff>=0.4`

### Error Handling

- All tools return structured error messages
- Logging to stderr (MCP requirement)
- Query validation before execution
- Rate limiting considerations for BigQuery
- Graceful degradation for large result sets

### Performance Considerations

- Query result pagination (default 100 rows, max 1000)
- Efficient BigQuery queries (use partitioning/clustering)
- Result caching for frequently accessed data
- Query optimization (avoid full table scans)
- Timeout handling (30s default)

### Security

- BigQuery authentication via service account
- Query parameterization (prevent SQL injection)
- Access control (read-only queries)
- Sensitive data filtering (PII considerations)

---

## Usage Examples

### Example 1: Explore a Concept

```python
# Tool: explore_concept
{
  "concept": "cognitive isomorphism",
  "depth": "deep",
  "include_relationships": true,
  "time_range": "last_30_days"
}
```

### Example 2: Track Data Sources

```python
# Tool: track_source_data
{
  "sources": ["claude_code", "cursor"],
  "time_range": "last_7_days",
  "metrics": ["volume", "entities", "domains"]
}
```

### Example 3: Analyze Trends

```python
# Tool: analyze_temporal_trends
{
  "metric": "entity_creation",
  "time_range": "last_90_days",
  "granularity": "daily",
  "group_by": "source_system"
}
```

### Example 4: Spine Level Analysis

```python
# Tool: analyze_spine_level
{
  "level": 8,  # Document level
  "include_children": true,
  "include_parents": true,
  "filters": {
    "domain": "framework"
  }
}
```

---

## Future Enhancements

1. **Machine Learning Integration**
   - Predictive trend analysis
   - Anomaly detection using ML models
   - Concept similarity using embeddings

2. **Real-time Analysis**
   - Streaming query support
   - Live dashboard updates
   - Real-time alerting

3. **Advanced Visualization**
   - Graph visualization for relationships
   - Time series charts
   - Heatmaps for patterns

4. **Export Capabilities**
   - CSV/JSON export
   - Report generation
   - Data pipeline integration

---

## Testing Strategy

1. **Unit Tests**: Test individual tool functions
2. **Integration Tests**: Test BigQuery connectivity
3. **Query Tests**: Validate SQL query generation
4. **Performance Tests**: Test with large datasets
5. **Error Handling Tests**: Test error scenarios

---

## Deployment

### Local Development

```bash
cd mcp-servers/spine-analysis-mcp
pip install -e .
python -m spine_analysis_mcp.server
```

### MCP Client Configuration

```toml
[mcp_servers.spine-analysis]
command = "python"
args = ["-m", "spine_analysis_mcp.server"]
env = {
  "GOOGLE_APPLICATION_CREDENTIALS" = "/path/to/service-account.json"
}
```

---

## Success Metrics

- **Query Performance**: < 5s for standard queries
- **Tool Coverage**: 40+ tools across 8 categories
- **Data Source Tracking**: 5 sources (Claude code/web, Gemini web, Codex, Cursor)
- **Spine Level Support**: All 12 levels (L1-L12)
- **Error Rate**: < 1% query failures
- **Usage**: Active analysis of 51.8M+ entities

---

---

## Entity Enrichments & Coverage

- **Table**: `spine.entity_enrichments` — typed enrichment metrics (sentiment, readability, emotion, keywords, etc.).
- **Coverage report**: [ENRICHMENT_COVERAGE_GAPS_REPORT.md](../../enrichment/ENRICHMENT_COVERAGE_GAPS_REPORT.md) — column coverage, gaps, and a prioritised completion checklist.
- **MCP tool**: `get_enrichment_coverage` — live coverage snapshot (table stats, entity-level coverage vs `entity_unified`, optional per-column coverage).
- **Script**: `mcp-servers/spine-analysis-mcp/scripts/analyze_enrichment_coverage.py` — full coverage run; use `--out <path>` to write a summary file.

---

**END OF PLAN**
