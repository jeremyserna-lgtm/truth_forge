# MCP Servers - Implementation Checklist

**Quick reference for tracking MCP server migration and enhancement progress.**

---

## Phase 1: Installation & Validation

### File Sync & Verification
- [ ] Compare `/Users/` vs `/Volumes/` for missing files
  ```bash
  diff -r /Users/jeremyserna/truth_forge/mcp-servers/ /Volumes/jeremyserna/truth_forge/mcp-servers/ | grep "Only in /Volumes"
  ```
- [ ] Sync any missing files if found
  ```bash
  rsync -av --ignore-existing /Volumes/jeremyserna/truth_forge/mcp-servers/ mcp-servers/
  ```
- [ ] Archive `/Volumes/` version after sync
  ```bash
  tar -czf ~/Archives/mcp-servers-volumes-$(date +%Y%m%d).tar.gz /Volumes/jeremyserna/truth_forge/mcp-servers/
  ```

### Installation
- [ ] Install truth-forge-mcp
  ```bash
  cd /Users/jeremyserna/truth_forge
  source .venv/bin/activate
  pip install -e mcp-servers/truth-forge-mcp
  ```
- [ ] Install spine-analysis-mcp
  ```bash
  pip install -e mcp-servers/spine-analysis-mcp
  ```
- [ ] Install truth-browser-logger
  ```bash
  pip install -e mcp-servers/truth-browser-logger
  ```
- [ ] Test imports
  ```bash
  python -c "import truth_forge_mcp; print('✅ truth-forge-mcp')"
  python -c "import spine_analysis_mcp; print('✅ spine-analysis-mcp')"
  python -c "import truth_browser_logger; print('✅ truth-browser-logger')"
  ```

### Server Testing
- [ ] Test truth-forge-mcp starts
  ```bash
  /usr/local/bin/python3.12 -m truth_forge_mcp.server
  ```
- [ ] Test spine-analysis-mcp starts
  ```bash
  /usr/local/bin/python3.12 -m spine_analysis_mcp.server
  ```
- [ ] Test truth-browser-logger starts
  ```bash
  /usr/local/bin/python3.12 -m truth_browser_logger.server
  ```

---

## Phase 2: Code Audit & Quality

### truth-forge-mcp Audit
- [ ] Search for placeholders
  ```bash
  cd mcp-servers
  grep -r "NotImplementedError" truth-forge-mcp/src/ > audit_not_impl.txt
  grep -r "placeholder" truth-forge-mcp/src/ > audit_placeholder.txt
  grep -r "TODO\|FIXME" truth-forge-mcp/src/ > audit_todos.txt
  ```
- [ ] Create tool inventory (working vs. placeholder)
- [ ] Document service dependencies
- [ ] Test service imports
  ```bash
  python << 'EOF'
  import sys
  from pathlib import Path
  sys.path.insert(0, "src")

  services = [
      "truth_forge.services.knowledge",
      "truth_forge.services.cognition",
      "truth_forge.services.relationship",
      "truth_forge.services.governance",
  ]

  for service in services:
      try:
          __import__(service)
          print(f"✅ {service}")
      except ImportError as e:
          print(f"❌ {service}: {e}")
  EOF
  ```

### Code Quality Checks
- [ ] Run mypy on all servers
  ```bash
  mypy mcp-servers/truth-forge-mcp/src/ --strict
  mypy mcp-servers/spine-analysis-mcp/src/ --strict
  mypy mcp-servers/truth-browser-logger/src/ --strict
  ```
- [ ] Run ruff on all servers
  ```bash
  ruff check mcp-servers/*/src/
  ```
- [ ] Check for data protection violations
  ```bash
  grep -r "insert_rows\|WRITE_TRUNCATE" mcp-servers/*/src/
  ```

---

## Phase 3: Implementation - Priority 0 (Core Tools)

### Knowledge Service Tools
- [ ] Verify `query_knowledge` works
- [ ] Verify `get_knowledge_atom` works
- [ ] Verify `get_knowledge_stats` works
- [ ] **NEW**: Implement `create_knowledge_atom`
- [ ] **NEW**: Implement `find_related_atoms`
- [ ] Add data protection to write operations
- [ ] Add integration tests

### Cognition Service Tools
- [ ] Verify `get_cognitive_state` works
- [ ] Verify `query_thoughts` works (may be placeholder)
- [ ] **NEW**: Implement `query_paradoxes`
- [ ] **NEW**: Implement `create_plan`
- [ ] **NEW**: Implement `run_cognitive_diagnostic`
- [ ] Add integration tests

### Relationship Service Tools
- [ ] Verify `get_partnership` works
- [ ] Verify `get_trust_level` works
- [ ] Verify `list_partnerships` works
- [ ] **NEW**: Implement `update_interaction`
- [ ] **NEW**: Implement `get_relationship_history`
- [ ] Add data protection to write operations
- [ ] Add integration tests

### Governance Service Tools
- [ ] Verify `query_events` works
- [ ] Verify `get_recent_events` works
- [ ] Verify `get_governance_stats` works
- [ ] **NEW**: Implement `check_violations`
- [ ] **NEW**: Implement `get_event_by_id`
- [ ] Add integration tests

### BigQuery Tools
- [ ] Verify `query_entities` works
- [ ] Verify `query_enrichments` works
- [ ] **NEW**: Implement `query_conversations`
- [ ] **NEW**: Implement `query_embeddings`
- [ ] **NEW**: Implement `query_time_travel` (complex!)
- [ ] Add query validation and limits
- [ ] Add integration tests

---

## Phase 4: Implementation - Priority 1 (Data Access)

### Pipeline Tools
- [ ] Verify `get_pipeline_status` works
- [ ] Verify `get_stage_status` works
- [ ] **NEW**: Implement `list_pipelines`
- [ ] **NEW**: Implement `get_pipeline_history`
- [ ] **NEW**: Implement `trigger_pipeline` (WITH APPROVAL SYSTEM!)
- [ ] Add approval workflow
- [ ] Add data protection
- [ ] Add integration tests

### Knowledge Graph Tools
- [ ] Verify `get_entity_relationships` works
- [ ] Verify `get_graph_stats` works
- [ ] **NEW**: Implement `query_graph`
- [ ] **NEW**: Implement `find_path`
- [ ] **NEW**: Implement `add_relationship` (with validation)
- [ ] Add data protection to write operations
- [ ] Add integration tests

### DuckDB Tools
- [ ] Verify `query_duckdb` works
- [ ] Verify `list_duckdb_databases` works
- [ ] Verify `get_duckdb_schema` works
- [ ] Add query safety limits (SELECT only, row limits)
- [ ] Add integration tests

---

## Phase 5: Implementation - Priority 2 (Advanced)

### Identity Service Tools
- [ ] Implement `resolve_entity_id`
- [ ] Implement `get_entity_by_id`
- [ ] Implement `list_entities`
- [ ] Implement `register_entity` (with validation)
- [ ] Add data protection
- [ ] Add integration tests

### Analytics Service Tools
- [ ] Implement `get_metrics`
- [ ] Implement `get_analytics`
- [ ] Implement `query_analytics`
- [ ] Add integration tests

### Action Service Tools (CAREFUL!)
- [ ] Implement `prepare_briefing` (read-only, safe)
- [ ] Implement `list_actions` (read-only, safe)
- [ ] Implement `get_action_history` (read-only, safe)
- [ ] Implement `trigger_action` (REQUIRES APPROVAL SYSTEM!)
- [ ] Build approval workflow
- [ ] Add comprehensive logging
- [ ] Add integration tests

---

## Phase 6: Architecture & Federation

### Move to src/ Layout
- [ ] Create `src/truth_forge/mcp/` directory structure
- [ ] Move server implementations to `src/truth_forge/mcp/servers/`
- [ ] Move tool modules to `src/truth_forge/mcp/tools/`
- [ ] Create shared utilities in `src/truth_forge/mcp/utils/`
- [ ] Update `pyproject.toml` for all servers
- [ ] Update `.mcp.json` configurations
- [ ] Test all servers after migration

### Federation Pattern
- [ ] Create base `TruthForgeServer` class
- [ ] Create tool registry system
- [ ] Create federation utilities
- [ ] Document federation pattern for daughters
- [ ] Create example daughter server extension
- [ ] Test federation with primitive_engine
- [ ] Test federation with credential_atlas

---

## Documentation

### Server Documentation
- [ ] Document all truth-forge-mcp tools
- [ ] Document all spine-analysis-mcp tools (already done!)
- [ ] Document all truth-browser-logger tools
- [ ] Create tool reference guide
- [ ] Create usage examples
- [ ] Document federation pattern

### Compliance Documentation
- [ ] Document data protection enforcement
- [ ] Document approval workflows
- [ ] Create compliance checklist
- [ ] Document tool safety ratings

---

## Testing

### Unit Tests
- [ ] Create tests for knowledge tools
- [ ] Create tests for cognition tools
- [ ] Create tests for relationship tools
- [ ] Create tests for governance tools
- [ ] Create tests for BigQuery tools
- [ ] Create tests for pipeline tools
- [ ] Create tests for knowledge graph tools
- [ ] Create tests for DuckDB tools

### Integration Tests
- [ ] Test truth-forge-mcp with real services
- [ ] Test spine-analysis-mcp with BigQuery
- [ ] Test truth-browser-logger with browser DBs
- [ ] Test cross-tool workflows
- [ ] Test error handling
- [ ] Test data protection enforcement

### Performance Tests
- [ ] Benchmark BigQuery query performance
- [ ] Benchmark DuckDB query performance
- [ ] Test with large result sets
- [ ] Test concurrent tool calls

---

## Deployment

### Production Readiness
- [ ] All critical tools implemented
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Data protection enforced
- [ ] Performance validated

### Configuration
- [ ] Update `.mcp.json` if paths changed
- [ ] Configure environment variables
- [ ] Set up BigQuery credentials
- [ ] Test with Claude Code
- [ ] Test with Cursor
- [ ] Test with other MCP clients

---

## Success Metrics

### Installation Phase
- [ ] All 3 servers installed without errors
- [ ] All 3 servers start successfully
- [ ] Basic tools work (get_status, get_table_stats, get_browser_history)

### Implementation Phase
- [ ] 11 Priority 0 tools implemented (core services)
- [ ] 6 Priority 1 tools implemented (data access)
- [ ] 11 Priority 2 tools implemented (advanced)
- [ ] **Total: 50+ tools** across all servers

### Quality Phase
- [ ] 100% type hint coverage
- [ ] All tests passing (90%+ coverage)
- [ ] Data protection enforced on all writes
- [ ] mypy --strict passes
- [ ] ruff check passes

### Federation Phase
- [ ] Servers in `src/truth_forge/mcp/`
- [ ] Base classes created
- [ ] Tool registry operational
- [ ] Daughters can extend genesis
- [ ] Documentation complete

---

## Quick Commands Reference

```bash
# Install all servers
cd /Users/jeremyserna/truth_forge
source .venv/bin/activate
pip install -e mcp-servers/truth-forge-mcp
pip install -e mcp-servers/spine-analysis-mcp
pip install -e mcp-servers/truth-browser-logger

# Test installations
python -c "import truth_forge_mcp, spine_analysis_mcp, truth_browser_logger"

# Run quality checks
mypy mcp-servers/*/src/ --strict
ruff check mcp-servers/*/src/

# Search for issues
grep -r "NotImplementedError\|placeholder\|TODO" mcp-servers/truth-forge-mcp/src/

# Test servers
/usr/local/bin/python3.12 -m truth_forge_mcp.server
/usr/local/bin/python3.12 -m spine_analysis_mcp.server
/usr/local/bin/python3.12 -m truth_browser_logger.server

# Run tests (once created)
pytest mcp-servers/truth-forge-mcp/tests/ -v
pytest mcp-servers/spine-analysis-mcp/tests/ -v
pytest mcp-servers/truth-browser-logger/tests/ -v
```

---

**Track progress by checking boxes as you complete each item.**

*Last updated: 2026-02-06*
