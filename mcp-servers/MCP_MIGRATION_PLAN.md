# MCP Servers Migration & Enhancement Plan

**Date**: 2026-02-06
**Status**: 🔄 **ASSESSMENT COMPLETE - READY FOR MIGRATION**
**Authority**: THE GENESIS (truth_forge)

---

## Executive Summary

**Current State**: 3 MCP servers exist but are on external volume `/Volumes/jeremyserna/`
**Target State**: Fully integrated MCP servers in main truth_forge codebase at `/Users/jeremyserna/`
**Gap**: Location mismatch, incomplete integrations, expansion opportunities

### Critical Issues

| Issue | Severity | Impact |
|-------|----------|--------|
| **Location Split** | 🔴 HIGH | Servers on `/Volumes/` not `/Users/` - fragile setup |
| **Incomplete Tools** | 🟡 MEDIUM | Many tools are placeholders, not fully functional |
| **Missing Integration** | 🟡 MEDIUM | Not integrated with main `src/truth_forge/` services |
| **Documentation Drift** | 🟢 LOW | Assessment docs accurate but not consolidated |

---

## Current MCP Server Inventory

### 1. truth-forge-mcp (v2.0.0)
**Location**: `/Volumes/jeremyserna/truth_forge/mcp-servers/truth-forge-mcp/`
**Tools**: 22 tools across 8 capability areas
**Status**: ✅ Configured in `.mcp.json`, ⚠️ Many tools incomplete

**Tool Categories**:
- ✅ Knowledge Service (3 tools) - `query_knowledge`, `get_knowledge_atom`, `get_knowledge_stats`
- ✅ Cognition Service (2 tools) - `get_cognitive_state`, `query_thoughts`
- ✅ Relationship Service (3 tools) - `get_partnership`, `get_trust_level`, `list_partnerships`
- ✅ Governance Service (3 tools) - `query_events`, `get_recent_events`, `get_governance_stats`
- ✅ BigQuery Tools (2 tools) - `query_entities`, `query_enrichments`
- ✅ Pipeline Tools (2 tools) - `get_pipeline_status`, `get_stage_status`
- ✅ Knowledge Graph (2 tools) - `get_entity_relationships`, `get_graph_stats`
- ✅ DuckDB Tools (3 tools) - `query_duckdb`, `list_duckdb_databases`, `get_duckdb_schema`
- ✅ Built-in Tools (2 tools) - `get_status`, `check_governance`

**Integration Concerns**:
- Uses `setup_project_path()` utility to find truth_forge - brittle
- Imports from `truth_forge.services` - may not work from `/Volumes/`
- No clear molt lineage in code (documented externally)

---

### 2. spine-analysis-mcp (v1.0.0)
**Location**: `/Volumes/jeremyserna/truth_forge/mcp-servers/spine-analysis-mcp/`
**Tools**: 24 tools for deep BigQuery spine analysis
**Status**: ✅ Configured, ✅ Production ready, documented

**Tool Categories**:
- Query Tools (3) - `query_entities`, `query_documents`, `get_table_stats`
- Source Tools (3) - `track_source_data`, `compare_sources`, `find_cross_source_connections`
- Trend Tools (1) - `analyze_temporal_trends`
- Concept Tools (1) - `explore_concept`
- Spine Level Tools (1) - `analyze_spine_level`
- Relationship Tools (4) - Network analysis, path finding, pattern analysis
- Temporal Tools (4) - Pattern detection, clustering, evolution tracking
- Pattern Tools (3) - Recurring patterns, anomalies, sequences
- Semantic Tools (2) - Similarity search, concept clustering
- Cross-Level Tools (2) - Hierarchical distribution and relationships
- **NEW**: Discovery Tools - `hunt_data_ghosts`, `find_anomalous_patterns`
- **NEW**: Not-Me Analytics - Portal-specific analytics

**Strengths**:
- ✅ Comprehensive documentation (COMPLETE.md, NEXT_STEPS.md, QUICK_START.md)
- ✅ Well-structured with 15 tool modules
- ✅ Direct BigQuery integration, no service dependencies
- ✅ Production-grade code quality

**Integration Concerns**:
- Self-contained (good!) - no dependencies on main truth_forge code
- Could benefit from sharing utilities with truth-forge-mcp
- Location on `/Volumes/` makes it fragile

---

### 3. truth-browser-logger (v1.0.0)
**Location**: `/Volumes/jeremyserna/truth_forge/mcp-servers/truth-browser-logger/`
**Tools**: 8 browser history extraction tools
**Status**: ✅ Configured, ✅ Updated to Truth Forge branding

**Tool Categories**:
- `get_browser_history` - Chrome/Safari history extraction
- `get_browser_stats` - Browsing statistics
- `get_browser_context_for_entity` - Entity-specific context
- `get_relationship_context` - Relationship context from browsing
- `get_research_timeline` - Research session timeline
- `get_session_patterns` - Session pattern detection
- `correlate_browser_with_truth` - Cross-reference with truth_forge data
- `check_consent` - Privacy/consent verification

**Strengths**:
- ✅ Focused, single-purpose server
- ✅ Privacy-conscious design (consent checking)
- ✅ No external dependencies (reads SQLite directly)

**Integration Concerns**:
- Self-contained (good!)
- Location on `/Volumes/` makes it fragile

---

## Migration Strategy

### Phase 1: Location Consolidation (IMMEDIATE)

**Goal**: Move all MCP servers from `/Volumes/jeremyserna/` to `/Users/jeremyserna/`

**Steps**:
1. ✅ Verify current servers are on `/Volumes/` (confirmed)
2. ⏳ Move `mcp-servers/` directory to main truth_forge location
3. ⏳ Update `.mcp.json` paths to use relative paths
4. ⏳ Test all three servers after migration
5. ⏳ Update documentation to reflect new location

**Commands**:
```bash
# Backup current state
cp -R /Volumes/jeremyserna/truth_forge/mcp-servers /tmp/mcp-servers-backup

# Move to correct location (if not already there)
# Check if already at /Users/jeremyserna/truth_forge/mcp-servers/
ls -la /Users/jeremyserna/truth_forge/mcp-servers/

# Update .mcp.json to use PROJECT_ROOT variable (already done!)
```

**Risk**: LOW - All servers are already configured with `${PROJECT_ROOT}` variable

---

### Phase 2: Code Quality & Integration (HIGH PRIORITY)

**Goal**: Ensure all MCP servers follow truth_forge standards

#### 2.1: truth-forge-mcp Quality Audit

**Issues to Fix**:
```python
# CURRENT (brittle path finding)
def _get_project_root() -> Path:
    return Path(__file__).parent.parent.parent.parent.parent

# SHOULD BE (use federation or env var)
def _get_project_root() -> Path:
    return Path(os.environ.get("TRUTH_FORGE_ROOT", Path.cwd()))
```

**Standards Compliance**:
- ✅ Type hints present
- ✅ Docstrings present (Google style)
- ⚠️ Structured logging - needs audit
- ⚠️ Error handling - needs DLQ pattern for data operations
- ⚠️ Service imports - may fail if services not installed

**Actions**:
1. ⏳ Audit all tool implementations for placeholder vs. real code
2. ⏳ Test integration with `src/truth_forge/services/`
3. ⏳ Add data protection enforcement where tools write data
4. ⏳ Add comprehensive error handling with DLQ pattern
5. ⏳ Create integration tests

---

#### 2.2: spine-analysis-mcp Quality Audit

**Current State**: ✅ Excellent - already production-grade

**Potential Enhancements**:
- ⏳ Add data protection enforcement (currently queries only - safe)
- ⏳ Add caching layer for expensive queries
- ⏳ Add query result limits to prevent memory issues

**Actions**:
1. ✅ No immediate action needed - code quality is high
2. ⏳ Consider adding to `src/truth_forge/mcp/` as canonical location

---

#### 2.3: truth-browser-logger Quality Audit

**Current State**: ✅ Good - focused and working

**Potential Enhancements**:
- ⏳ Add browser history caching to reduce SQLite reads
- ⏳ Add privacy controls (time-based access expiration)

**Actions**:
1. ✅ No immediate action needed
2. ⏳ Consider privacy enhancement options

---

### Phase 3: Expansion & Enhancement (MEDIUM PRIORITY)

Based on `MCP_CAPABILITIES_ASSESSMENT.md`, many services are not yet exposed:

#### 3.1: Priority 0 Expansions (Core Services)

**Missing from truth-forge-mcp**:
- ⏳ `create_knowledge_atom` - Ingest new knowledge with validation
- ⏳ `find_related_atoms` - Semantic similarity search
- ⏳ `query_paradoxes` - Get conflicting knowledge atoms (Stage 5)
- ⏳ `create_plan` - Submit plan for execution
- ⏳ `run_cognitive_diagnostic` - Self-analysis
- ⏳ `update_interaction` - Log interaction (updates trust)
- ⏳ `get_relationship_history` - Interaction timeline
- ⏳ `check_violations` - Governance violations
- ⏳ `get_event_by_id` - Get specific governance event
- ⏳ `query_conversations` - Conversation context from BigQuery
- ⏳ `query_time_travel` - Bitemporal queries

**Estimated Effort**: 2-3 weeks (11 new tools)

---

#### 3.2: Priority 1 Expansions (Pipeline & Data)

**Missing Tools**:
- ⏳ `list_pipelines` - Available pipelines
- ⏳ `get_pipeline_history` - Execution history
- ⏳ `trigger_pipeline` - Trigger with validation (DANGEROUS - needs approval)
- ⏳ `query_graph` - Graph traversal queries
- ⏳ `find_path` - Find path between entities
- ⏳ `add_relationship` - Add new relationship with validation

**Estimated Effort**: 1-2 weeks (6 new tools)

---

#### 3.3: Priority 2 Expansions (Advanced)

**Missing Tools**:
- ⏳ Identity Service tools (4 tools)
- ⏳ Analytics Service tools (3 tools)
- ⏳ Action Service tools (4 tools) - REQUIRES APPROVAL SYSTEM

**Estimated Effort**: 2-3 weeks (11 new tools)

---

### Phase 4: Federation & Architecture (ADVANCED)

**Goal**: Create canonical MCP architecture for all truth_forge daughters

#### 4.1: Consolidate into src/

**Current**: MCP servers in `mcp-servers/` directory
**Target**: Move to `src/truth_forge/mcp/` as canonical source

**Structure**:
```
src/truth_forge/mcp/
├── __init__.py
├── servers/
│   ├── __init__.py
│   ├── truth_forge_server.py    # Main server (from truth-forge-mcp)
│   ├── spine_analysis_server.py # Spine server
│   └── browser_logger_server.py # Browser logger
├── tools/
│   ├── __init__.py
│   ├── knowledge_tools.py
│   ├── cognition_tools.py
│   ├── relationship_tools.py
│   ├── governance_tools.py
│   ├── bigquery_tools.py
│   ├── pipeline_tools.py
│   ├── knowledge_graph_tools.py
│   ├── duckdb_tools.py
│   ├── spine_analysis_tools.py
│   └── browser_tools.py
└── utils/
    ├── __init__.py
    ├── registry.py         # Tool registration
    ├── enforcement.py      # Data protection
    └── federation.py       # Cross-server communication
```

**Benefits**:
- ✅ Canonical source of truth
- ✅ Shared utilities across servers
- ✅ Easier to maintain and test
- ✅ Follows src layout standard (ADR-0001)
- ✅ Can be imported by daughters (primitive_engine, credential_atlas)

---

#### 4.2: Create Federation Pattern

**Goal**: Allow daughter projects to extend MCP servers

**Pattern**:
```python
# In primitive_engine/.claude/mcp.json
{
  "mcpServers": {
    "primitive-engine": {
      "command": "python",
      "args": ["-m", "primitive_engine.mcp.server"],
      "env": {
        "TRUTH_FORGE_MCP_FEDERATION": "true",
        "TRUTH_FORGE_ROOT": "/Users/jeremyserna/truth_forge"
      }
    }
  }
}

# In primitive_engine/src/primitive_engine/mcp/server.py
from truth_forge.mcp.servers import TruthForgeServer
from truth_forge.mcp.utils.registry import register_tool

class PrimitiveEngineServer(TruthForgeServer):
    """Primitive Engine MCP server - extends Truth Forge."""

    def __init__(self):
        super().__init__()
        self.register_primitive_engine_tools()

    def register_primitive_engine_tools(self):
        # Add primitive_engine-specific tools
        register_tool(build_architecture_tool, handle_build_architecture)
```

**Benefits**:
- ✅ Daughters inherit all genesis tools
- ✅ Can extend with daughter-specific tools
- ✅ Single source of truth for core tools
- ✅ Follows THE PATTERN: genesis governs, daughters extend

---

## Recommended Next Steps

### Immediate (This Week)

1. **✅ Verify Location**
   ```bash
   ls -la /Users/jeremyserna/truth_forge/mcp-servers/
   ls -la /Volumes/jeremyserna/truth_forge/mcp-servers/
   ```
   - If servers are on `/Volumes/`, migrate to `/Users/`
   - Update `.mcp.json` if needed

2. **⏳ Test All Servers**
   ```bash
   cd /Users/jeremyserna/truth_forge
   source .venv/bin/activate

   # Test truth-forge-mcp
   cd mcp-servers/truth-forge-mcp
   python -m truth_forge_mcp.server --test

   # Test spine-analysis-mcp
   cd ../spine-analysis-mcp
   python test_server.py

   # Test truth-browser-logger
   cd ../truth-browser-logger
   python -m truth_browser_logger.server --test
   ```

3. **⏳ Document Current State**
   - Create inventory of working vs. placeholder tools
   - Document service dependencies
   - List expansion priorities

---

### Short Term (Next 2 Weeks)

1. **⏳ Implement Priority 0 Tools**
   - Focus on knowledge atom creation
   - Add relationship interaction tracking
   - Expose governance violation checking

2. **⏳ Add Data Protection**
   - Audit all write operations
   - Add enforcement decorators
   - Implement DLQ pattern for failures

3. **⏳ Create Integration Tests**
   - Test each tool with real services
   - Verify error handling
   - Validate data protection rules

---

### Medium Term (Next Month)

1. **⏳ Move to src/ Layout**
   - Create `src/truth_forge/mcp/` structure
   - Migrate servers to canonical location
   - Update build configuration

2. **⏳ Implement Federation Pattern**
   - Create base server class
   - Add tool registry system
   - Document federation for daughters

3. **⏳ Expand spine-analysis-mcp**
   - Add write capabilities (with protection)
   - Add caching layer
   - Optimize expensive queries

---

### Long Term (Next Quarter)

1. **⏳ Full Service Exposure**
   - Complete Priority 1 tools
   - Complete Priority 2 tools
   - Add action approval system

2. **⏳ Daughter Integration**
   - Configure primitive_engine MCP
   - Configure credential_atlas MCP
   - Test federation inheritance

3. **⏳ Advanced Capabilities**
   - Multi-hop graph queries
   - Time-travel query optimization
   - Cross-server tool composition

---

## Success Metrics

### Phase 1: Location Consolidation
- ✅ All servers at `/Users/jeremyserna/truth_forge/mcp-servers/`
- ✅ All servers start successfully
- ✅ `.mcp.json` uses relative paths

### Phase 2: Code Quality
- ✅ All tools implemented (no placeholders)
- ✅ 100% type hint coverage
- ✅ Data protection enforcement on all writes
- ✅ Integration tests passing

### Phase 3: Expansion
- ✅ 11 Priority 0 tools implemented
- ✅ 6 Priority 1 tools implemented
- ✅ 50+ total tools across all servers

### Phase 4: Federation
- ✅ Servers in `src/truth_forge/mcp/`
- ✅ Daughters can extend base servers
- ✅ Shared utilities across servers
- ✅ Tool registry system operational

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Service import failures** | MEDIUM | HIGH | Add service availability checks, graceful degradation |
| **Path resolution issues** | LOW | MEDIUM | Use env vars, test thoroughly |
| **Data corruption from new tools** | MEDIUM | CRITICAL | Enforce data protection rules, comprehensive testing |
| **Performance degradation** | LOW | MEDIUM | Add caching, query optimization |
| **Federation complexity** | MEDIUM | MEDIUM | Start simple, iterate based on need |

---

## Open Questions

1. **Should we consolidate all three servers into one mega-server?**
   - Pro: Simpler configuration
   - Con: Loss of modularity, harder to test
   - **Recommendation**: Keep separate, add federation layer

2. **Should MCP servers have write access to BigQuery?**
   - Pro: Enables powerful workflows
   - Con: Data corruption risk
   - **Recommendation**: Yes, but with STRICT enforcement and approval

3. **How should daughters extend genesis MCP tools?**
   - Option A: Inherit and extend base server class
   - Option B: Separate servers with federation
   - **Recommendation**: Option A (inheritance) for simplicity

4. **Should we create a unified tool registry?**
   - Pro: Easier to discover and manage tools
   - Con: Added complexity
   - **Recommendation**: Yes, for Phase 4 federation

---

## Appendix: File Locations

### Current Locations (On External Volume)
```
/Volumes/jeremyserna/truth_forge/mcp-servers/
├── MCP_CAPABILITIES_ASSESSMENT.md
├── MCP_SERVERS_ASSESSMENT.md
├── spine-analysis-mcp/
│   ├── COMPLETE.md
│   ├── NEXT_STEPS.md
│   ├── QUICK_START.md
│   ├── src/spine_analysis_mcp/
│   └── pyproject.toml
├── truth-browser-logger/
│   ├── src/truth_browser_logger/
│   └── pyproject.toml
└── truth-forge-mcp/
    ├── IMPLEMENTATION_SUMMARY.md
    ├── ERRORS_FIXED.md
    ├── src/truth_forge_mcp/
    └── pyproject.toml
```

### Target Location (Main truth_forge)
```
/Users/jeremyserna/truth_forge/
├── .mcp.json                     # ← Already configured!
├── mcp-servers/                  # ← Should be here
│   ├── [same as above]
└── src/truth_forge/mcp/          # ← Future: canonical location
    ├── servers/
    ├── tools/
    └── utils/
```

---

**Status**: 📋 **PLAN COMPLETE - READY FOR EXECUTION**

*Follow THE PATTERN: HOLD (plan) → AGENT (execute) → HOLD (validate)*
