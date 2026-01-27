# MCP Server Capabilities Assessment

**Date**: 2026-01-27  
**Purpose**: Assess what capabilities would be great additions to truth_forge MCP servers  
**Status**: ✅ **ASSESSMENT COMPLETE**

---

## Executive Summary

**Current State**: 2 MCP servers with basic capabilities  
**Gap Analysis**: Many powerful services exist but aren't exposed via MCP  
**Recommendation**: Expand `truth-forge-mcp` with service-oriented tools following THE PATTERN

**Priority**: HIGH - Exposing existing services via MCP will dramatically increase AI agent effectiveness.

---

## Current MCP Server Capabilities

### truth-forge-mcp (v2.0.0)
**Current Tools**:
- `get_status` - Basic system status
- `check_governance` - Governance status (placeholder)

**Current Resources**:
- `truth-forge://status` - System status
- `truth-forge://claude-md` - CLAUDE.md content

**Gap**: Only exposes 2 basic tools. Many powerful services exist but aren't accessible.

### truth-browser-logger (v1.0.0)
**Current Tools**: 8 browser history tools
- Browser history extraction
- Pattern detection
- Relationship context
- Research timeline

**Status**: ✅ Well-developed, serves specific purpose

---

## Available Services (Not Yet Exposed)

### Core Services Available

| Service | Purpose | MCP Potential | Priority |
|---------|---------|---------------|----------|
| **KnowledgeService** | Knowledge atom intake/query | 🔥 HIGH | P0 |
| **CognitionService** | Thought assembly, planning | 🔥 HIGH | P0 |
| **RelationshipService** | Partnership/trust management | 🔥 HIGH | P0 |
| **GovernanceService** | Event history, audit trail | 🔥 HIGH | P0 |
| **PerceptionService** | External data sensing | ⚠️ MEDIUM | P1 |
| **ActionService** | Command execution | ⚠️ MEDIUM | P1 |
| **LoggingService** | Structured logging | ⚠️ MEDIUM | P2 |
| **IdentityService** | Entity ID management | ⚠️ MEDIUM | P2 |
| **AnalyticsService** | Metrics and analysis | ⚠️ MEDIUM | P2 |

### Pipeline Capabilities (Not Exposed)

| Capability | Description | MCP Potential | Priority |
|------------|-------------|---------------|----------|
| **Time-Travel Queries** | Query any point in time | 🔥 HIGH | P0 |
| **Knowledge Graph** | Entity relationship queries | 🔥 HIGH | P0 |
| **Pipeline Status** | Stage execution status | ⚠️ MEDIUM | P1 |
| **Entity Queries** | BigQuery entity access | 🔥 HIGH | P0 |
| **Bitemporal State** | Historical state reconstruction | 🔥 HIGH | P0 |

### Data Access (Partially Exposed)

| Data Source | Current Access | MCP Potential | Priority |
|-------------|----------------|---------------|----------|
| **BigQuery** | Via GCP MCP (indirect) | 🔥 HIGH | P0 |
| **DuckDB** | Direct file access | ⚠️ MEDIUM | P1 |
| **GCS Buckets** | Via gsutil | ⚠️ MEDIUM | P1 |
| **Knowledge Atoms** | Via services | 🔥 HIGH | P0 |

---

## Recommended Capability Additions

### Priority 0: Core Service Exposure (IMMEDIATE)

#### 1. Knowledge Service Tools
**Why**: Knowledge atoms are the core currency of truth_forge. AI agents need direct access.

**Recommended Tools**:
- `query_knowledge` - Search knowledge atoms by query, filters
- `get_knowledge_atom` - Get specific atom by ID
- `create_knowledge_atom` - Ingest new knowledge (with validation)
- `find_related_atoms` - Semantic similarity search
- `get_knowledge_stats` - Statistics about knowledge base

**Implementation**: Expose `KnowledgeService.query()` and `KnowledgeService.exhale()` via MCP

**Value**: Enables AI agents to:
- Access Jeremy's accumulated knowledge
- Add new knowledge from conversations
- Find related concepts automatically
- Understand context before acting

---

#### 2. Cognition Service Tools
**Why**: Cognition service assembles thoughts and plans. AI agents should query and contribute.

**Recommended Tools**:
- `query_thoughts` - Get active thoughts/plans
- `query_paradoxes` - Get conflicting knowledge atoms (Stage 5)
- `create_plan` - Submit a plan for execution
- `get_cognitive_state` - Current mental state summary
- `run_cognitive_diagnostic` - Self-analysis

**Implementation**: Expose `CognitionService.query_thoughts()` and related methods

**Value**: Enables AI agents to:
- Understand what the system is thinking
- Contribute to planning
- See paradoxes (Stage 5 cognitive architecture)
- Understand system awareness

---

#### 3. Relationship Service Tools
**Why**: Relationships are core to truth_forge. AI agents need context about partnerships.

**Recommended Tools**:
- `get_partnership` - Get relationship context for entity
- `get_trust_level` - Get trust score for entity
- `update_interaction` - Log interaction (updates trust)
- `list_partnerships` - List all known relationships
- `get_relationship_history` - Interaction timeline

**Implementation**: Expose `RelationshipService.get_partnership()` and related methods

**Value**: Enables AI agents to:
- Understand relationship context
- Make relationship-aware decisions
- Update trust based on interactions
- Provide personalized responses

---

#### 4. Governance Service Tools
**Why**: Governance tracks all events. AI agents need audit trail access.

**Recommended Tools**:
- `query_events` - Query event history with filters
- `get_recent_events` - Recent activity summary
- `check_violations` - Governance violations
- `get_event_by_id` - Get specific event
- `get_governance_stats` - Statistics about system behavior

**Implementation**: Expose `GovernanceService.query_events()` and related methods

**Value**: Enables AI agents to:
- Understand system history
- Detect anomalies
- Verify actions
- Provide accountability

---

#### 5. Entity Query Tools (BigQuery)
**Why**: BigQuery contains 240K+ conversation messages. AI agents need direct access.

**Recommended Tools**:
- `query_entities` - Query unified entity table (already documented!)
- `query_enrichments` - Get NLP enrichments (sentiment, topics)
- `query_embeddings` - Get vector embeddings for similarity
- `query_conversations` - Get conversation context
- `query_time_travel` - Query historical state (bitemporal)

**Implementation**: Wrap BigQuery client with MCP tools, following existing `query_entities` pattern

**Value**: Enables AI agents to:
- Access conversation history
- Find similar messages
- Understand context
- Query across time

**Note**: `query_entities` tool is already documented in `docs/operations/tools/mcp_query_entities.md` but may not be implemented yet.

---

### Priority 1: Pipeline & Data Access (HIGH)

#### 6. Pipeline Status Tools
**Why**: AI agents should know pipeline execution status.

**Recommended Tools**:
- `get_pipeline_status` - Current pipeline execution state
- `get_stage_status` - Status of specific stage
- `list_pipelines` - Available pipelines
- `get_pipeline_history` - Execution history
- `trigger_pipeline` - Trigger pipeline execution (with validation)

**Implementation**: Query pipeline tracking system

**Value**: Enables AI agents to:
- Monitor pipeline health
- Understand data freshness
- Trigger processing when needed

---

#### 7. Knowledge Graph Tools
**Why**: Knowledge graph contains relationships. AI agents need graph queries.

**Recommended Tools**:
- `query_graph` - Graph traversal queries
- `get_entity_relationships` - Relationships for entity
- `find_path` - Find path between entities
- `get_graph_stats` - Graph statistics
- `add_relationship` - Add new relationship (with validation)

**Implementation**: Expose knowledge graph service queries

**Value**: Enables AI agents to:
- Understand entity connections
- Discover relationships
- Navigate knowledge structure

---

#### 8. DuckDB Query Tools
**Why**: Many services use DuckDB. AI agents need query access.

**Recommended Tools**:
- `query_duckdb` - Execute SQL on DuckDB files
- `list_databases` - Available DuckDB files
- `get_schema` - Schema for database
- `query_service_db` - Query service-specific DuckDB (knowledge, governance, etc.)

**Implementation**: Wrap DuckDB with safe query interface

**Value**: Enables AI agents to:
- Query local knowledge bases
- Access service state
- Perform analytical queries

---

### Priority 2: Advanced Capabilities (MEDIUM)

#### 9. Identity Service Tools
**Why**: Entity IDs are fundamental. AI agents should query identity registry.

**Recommended Tools**:
- `resolve_entity_id` - Get ID for entity
- `get_entity_by_id` - Get entity by ID
- `list_entities` - List entities with filters
- `register_entity` - Register new entity (with validation)

**Implementation**: Expose `IdentityService` methods

---

#### 10. Analytics Service Tools
**Why**: Analytics provide insights. AI agents should access metrics.

**Recommended Tools**:
- `get_metrics` - Get system metrics
- `get_analytics` - Analytical insights
- `query_analytics` - Custom analytics queries

**Implementation**: Expose `AnalyticsService` methods

---

#### 11. Action Service Tools
**Why**: Actions execute commands. AI agents should trigger actions (carefully).

**Recommended Tools**:
- `prepare_briefing` - Create briefing for user (safe)
- `list_actions` - Available actions
- `get_action_history` - Action audit log
- `trigger_action` - Execute action (with approval)

**Implementation**: Expose `ActionService` with safety controls

**Security Note**: Actions should require explicit approval or be read-only.

---

### Priority 3: External Integrations (LOW)

#### 12. GCS Tools
**Why**: GCS stores archives. AI agents should access archived data.

**Recommended Tools**:
- `list_gcs_bucket` - List files in bucket
- `get_gcs_file` - Download file from GCS
- `upload_to_gcs` - Upload file (with validation)
- `query_gcs_archive` - Query archived data

**Implementation**: Wrap `gsutil` or GCS client

---

## Implementation Strategy

### Phase 1: Core Service Exposure (Week 1-2)
1. Add Knowledge Service tools
2. Add Cognition Service tools
3. Add Relationship Service tools
4. Add Governance Service tools
5. Add Entity Query tools (BigQuery)

**Impact**: AI agents can access core truth_forge capabilities

### Phase 2: Pipeline & Data (Week 3-4)
1. Add Pipeline Status tools
2. Add Knowledge Graph tools
3. Add DuckDB Query tools

**Impact**: AI agents can monitor and query data pipelines

### Phase 3: Advanced & External (Week 5+)
1. Add Identity Service tools
2. Add Analytics Service tools
3. Add Action Service tools (read-only initially)
4. Add GCS tools

**Impact**: Complete truth_forge ecosystem access

---

## Design Principles

### THE PATTERN Alignment
All tools follow `HOLD₁ → AGENT → HOLD₂`:
- **Input** (HOLD₁): Tool arguments
- **Processing** (AGENT): Service method calls
- **Output** (HOLD₂): Tool results

### Security & Governance
- **Read Operations**: Generally safe, expose freely
- **Write Operations**: Require validation, approval, or audit
- **Action Execution**: Require explicit approval
- **All Operations**: Logged via GovernanceService

### Error Handling
- **Fail-Safe**: All tools handle errors gracefully
- **Observability**: All operations logged with structured logging
- **Idempotency**: Write operations are idempotent where possible

---

## Example: Knowledge Service Tool Implementation

```python
# In truth-forge-mcp/src/truth_forge_mcp/tools/knowledge.py

from truth_forge.services.knowledge import get_knowledge_service
from mcp.types import Tool

knowledge_query_tool = Tool(
    name="query_knowledge",
    description="Query knowledge atoms by search term, filters, and limits",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "limit": {"type": "integer", "default": 10, "maximum": 100},
            "filters": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "domain": {"type": "string"},
                    "knowledge_type": {"type": "string"},
                },
            },
        },
        "required": ["query"],
    },
)

def handle_query_knowledge(arguments: dict[str, Any]) -> str:
    """Handle query_knowledge tool."""
    service = get_knowledge_service()
    query = arguments["query"]
    limit = arguments.get("limit", 10)
    filters = arguments.get("filters", {})
    
    atoms = service.inhale(query=query, limit=limit, **filters)
    
    # Format as markdown
    lines = [f"# Knowledge Atoms: {query}", ""]
    for atom in atoms:
        lines.append(f"## {atom.get('id', 'unknown')}")
        lines.append(f"**Content**: {atom.get('content', '')}")
        lines.append(f"**Source**: {atom.get('source', 'unknown')}")
        lines.append("")
    
    return "\n".join(lines)
```

---

## Success Metrics

### Quantitative
- **Tool Count**: 2 → 25+ tools
- **Service Coverage**: 0% → 80%+ of core services
- **Query Capability**: Basic → Full knowledge graph + BigQuery

### Qualitative
- **AI Agent Effectiveness**: Can access truth_forge knowledge
- **Context Awareness**: Agents understand relationships and history
- **Autonomy**: Agents can query and understand without human intervention

---

## Next Steps

1. ✅ **Assessment Complete** - This document
2. ⏳ **Prioritize Tools** - Review with Jeremy
3. ⏳ **Implement Phase 1** - Core service exposure
4. ⏳ **Test & Iterate** - Validate with real AI agent usage
5. ⏳ **Document** - Update tool references

---

*Assessment complete. Ready for implementation planning.*
