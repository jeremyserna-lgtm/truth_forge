# MCP Servers - Immediate Action Plan

**Date**: 2026-02-06
**Status**: 🔧 **READY TO EXECUTE**

---

## Current State Summary

### ✅ Good News
- All 3 MCP servers exist at correct location: `/Users/jeremyserna/truth_forge/mcp-servers/`
- All 3 are configured in `.mcp.json`
- Duplicate copy exists on `/Volumes/` (can be archived)
- Code structure looks solid

### ⚠️ Issues Found
- MCP modules not installed (ModuleNotFoundError when importing)
- `/Volumes/` version is 1.6M vs. `/Users/` version is 688K (missing files?)
- Integration with `src/truth_forge/` may be incomplete
- Many tools may be placeholders

---

## Recommended Next Steps

### Step 1: Verify & Sync (IMMEDIATE)

**Check for missing files:**
```bash
cd /Users/jeremyserna/truth_forge

# Compare directories to find what's missing
diff -r mcp-servers/ /Volumes/jeremyserna/truth_forge/mcp-servers/ | grep "Only in /Volumes"

# If there are important missing files, sync them
rsync -av --ignore-existing /Volumes/jeremyserna/truth_forge/mcp-servers/ mcp-servers/
```

---

### Step 2: Install MCP Servers (CRITICAL)

The servers need to be installed as Python packages for the `.mcp.json` configuration to work.

**Option A: Install in Development Mode (Recommended)**
```bash
cd /Users/jeremyserna/truth_forge
source .venv/bin/activate  # Or create venv if needed

# Install each MCP server in editable mode
cd mcp-servers/truth-forge-mcp
pip install -e .

cd ../spine-analysis-mcp
pip install -e .

cd ../truth-browser-logger
pip install -e .

# Test imports
python -c "import truth_forge_mcp; print('truth-forge-mcp: OK')"
python -c "import spine_analysis_mcp; print('spine-analysis-mcp: OK')"
python -c "import truth_browser_logger; print('truth-browser-logger: OK')"
```

**Option B: Use uv (Faster)**
```bash
cd /Users/jeremyserna/truth_forge
uv pip install -e mcp-servers/truth-forge-mcp
uv pip install -e mcp-servers/spine-analysis-mcp
uv pip install -e mcp-servers/truth-browser-logger
```

---

### Step 3: Test Each Server (VALIDATION)

**Test truth-forge-mcp:**
```bash
cd mcp-servers/truth-forge-mcp
/usr/local/bin/python3.12 -m truth_forge_mcp.server
# Should start without errors (press Ctrl+C to stop)
```

**Test spine-analysis-mcp:**
```bash
cd mcp-servers/spine-analysis-mcp
/usr/local/bin/python3.12 -m spine_analysis_mcp.server
# Should start without errors
```

**Test truth-browser-logger:**
```bash
cd mcp-servers/truth-browser-logger
/usr/local/bin/python3.12 -m truth_browser_logger.server
# Should start without errors
```

---

### Step 4: Audit Tool Implementations (CODE REVIEW)

Check which tools are placeholders vs. real implementations:

```bash
cd /Users/jeremyserna/truth_forge/mcp-servers

# Search for placeholder patterns
grep -r "NotImplementedError" truth-forge-mcp/src/
grep -r "placeholder" truth-forge-mcp/src/
grep -r "TODO" truth-forge-mcp/src/
grep -r "FIXME" truth-forge-mcp/src/

# Check tool implementations
for tool in truth-forge-mcp/src/truth_forge_mcp/tools/*.py; do
    echo "=== $tool ==="
    grep -A 5 "def handle_" "$tool" | head -20
done
```

**Create audit report:**
```bash
# Create list of working vs. placeholder tools
cat > MCP_TOOL_AUDIT.md << 'EOF'
# MCP Tool Implementation Audit

## truth-forge-mcp

### Working Tools
- [ ] get_status
- [ ] check_governance
- [ ] query_knowledge
- [ ] get_knowledge_atom
- [ ] get_knowledge_stats
- [ ] get_cognitive_state
- [ ] query_thoughts
- [ ] get_partnership
- [ ] get_trust_level
- [ ] list_partnerships
- [ ] query_events
- [ ] get_recent_events
- [ ] get_governance_stats
- [ ] query_entities
- [ ] query_enrichments
- [ ] get_pipeline_status
- [ ] get_stage_status
- [ ] get_entity_relationships
- [ ] get_graph_stats
- [ ] query_duckdb
- [ ] list_duckdb_databases
- [ ] get_duckdb_schema

### Placeholder/Incomplete Tools
(To be filled after audit)

## spine-analysis-mcp
(Already documented as production-ready)

## truth-browser-logger
(Already documented as working)
EOF
```

---

### Step 5: Fix Integration Issues (IF NEEDED)

**Check service imports:**
```bash
cd mcp-servers/truth-forge-mcp

# Test if services can be imported
/usr/local/bin/python3.12 << 'EOF'
import sys
from pathlib import Path

# Add truth_forge to path
sys.path.insert(0, str(Path(__file__).parent / "../../src"))

try:
    from truth_forge.services.knowledge import get_knowledge_service
    print("✅ KnowledgeService import: OK")
except ImportError as e:
    print(f"❌ KnowledgeService import: FAILED - {e}")

try:
    from truth_forge.services.cognition import get_cognition_service
    print("✅ CognitionService import: OK")
except ImportError as e:
    print(f"❌ CognitionService import: FAILED - {e}")

try:
    from truth_forge.services.relationship import get_relationship_service
    print("✅ RelationshipService import: OK")
except ImportError as e:
    print(f"❌ RelationshipService import: FAILED - {e}")

try:
    from truth_forge.services.governance import get_governance_service
    print("✅ GovernanceService import: OK")
except ImportError as e:
    print(f"❌ GovernanceService import: FAILED - {e}")
EOF
```

**If services don't exist, tools will fail. Two options:**

**Option 1: Create stub services (temporary)**
```python
# src/truth_forge/services/knowledge.py
class KnowledgeService:
    def query(self, query: str, limit: int = 10, **filters):
        return {"status": "placeholder", "message": "Service not implemented"}

def get_knowledge_service():
    return KnowledgeService()
```

**Option 2: Disable tools that need missing services**
```python
# In truth-forge-mcp/src/truth_forge_mcp/server.py
def register_optional_tools():
    """Register tools only if their dependencies are available."""
    try:
        from truth_forge.services.knowledge import get_knowledge_service
        register_knowledge_tools()
    except ImportError:
        logger.warning("KnowledgeService not available, skipping tools")
```

---

### Step 6: Archive External Volume (CLEANUP)

Once everything is working from `/Users/`:

```bash
# Create dated archive
tar -czf /tmp/mcp-servers-volumes-backup-$(date +%Y%m%d).tar.gz \
    /Volumes/jeremyserna/truth_forge/mcp-servers/

# Verify archive
tar -tzf /tmp/mcp-servers-volumes-backup-*.tar.gz | head -20

# Move archive to safe location
mv /tmp/mcp-servers-volumes-backup-*.tar.gz ~/Archives/

# (Optional) Remove from /Volumes/ after confirming backup
# rm -rf /Volumes/jeremyserna/truth_forge/mcp-servers/
```

---

## Expansion Priorities

Based on the capabilities assessment, here are the most valuable additions:

### Priority 0: Core Functionality (Implement First)

**Knowledge Service Enhancements:**
- `create_knowledge_atom` - Allow AI agents to add knowledge
- `find_related_atoms` - Semantic search for related concepts
- Implementation effort: ~1 day

**Relationship Service Enhancements:**
- `update_interaction` - Log interactions to update trust scores
- `get_relationship_history` - View interaction timeline
- Implementation effort: ~1 day

**Governance Service Enhancements:**
- `check_violations` - Detect governance rule violations
- `get_event_by_id` - Retrieve specific events
- Implementation effort: ~0.5 day

**Total Priority 0**: ~2.5 days

---

### Priority 1: Data Access (High Value)

**BigQuery Enhancements:**
- `query_conversations` - Access conversation context
- `query_time_travel` - Bitemporal queries (requires implementation)
- Implementation effort: ~2-3 days

**Pipeline Tools:**
- `list_pipelines` - Show available pipelines
- `get_pipeline_history` - Execution history
- `trigger_pipeline` - Manual pipeline execution (WITH APPROVAL ONLY)
- Implementation effort: ~2 days

**Total Priority 1**: ~4-5 days

---

### Priority 2: Advanced Features (Nice to Have)

**Knowledge Graph:**
- `query_graph` - Graph traversal
- `find_path` - Path finding between entities
- Implementation effort: ~3 days

**Identity & Analytics:**
- Identity service tools (4 tools) - ~2 days
- Analytics service tools (3 tools) - ~2 days

**Total Priority 2**: ~7 days

---

## Decision Points

### 1. Consolidate or Keep Separate?

**Current**: 3 separate MCP servers
- truth-forge-mcp (22 tools)
- spine-analysis-mcp (24 tools)
- truth-browser-logger (8 tools)

**Options**:
- **Keep Separate** (Recommended) - Modular, easier to test, clear separation of concerns
- **Consolidate** - Simpler config, but harder to maintain

**Recommendation**: **Keep separate** - they serve distinct purposes

---

### 2. Move to src/ or Keep in mcp-servers/?

**Current**: `mcp-servers/` directory at root
**Alternative**: `src/truth_forge/mcp/`

**Pros of src/**:
- ✅ Canonical source of truth
- ✅ Follows src layout (ADR-0001)
- ✅ Easier imports
- ✅ Can be published as package

**Cons of src/**:
- ❌ Requires restructuring
- ❌ More complex build
- ❌ Breaks current .mcp.json

**Recommendation**: **Keep in mcp-servers/ for now**, migrate to `src/` in Phase 4 (federation)

---

### 3. Expand truth-forge-mcp or Create New Servers?

**For new capabilities**, two options:
- **Expand truth-forge-mcp** - Add more tools to existing server
- **Create specialized servers** - e.g., "truth-forge-pipeline-mcp"

**Recommendation**: **Expand truth-forge-mcp** - it's designed as the main server

---

## Timeline Estimate

### Week 1: Installation & Validation
- Day 1: Install all servers, test basic functionality
- Day 2: Audit tool implementations, create inventory
- Day 3: Fix integration issues, test with real services
- Day 4-5: Implement Priority 0 enhancements

### Week 2: Data Access
- Day 6-8: Implement Priority 1 enhancements
- Day 9: Testing and validation
- Day 10: Documentation and cleanup

### Week 3+: Advanced Features (Optional)
- Implement Priority 2 enhancements as needed
- Begin federation planning

---

## Success Criteria

### Phase 1: Installation ✅
- [ ] All 3 servers installed without errors
- [ ] All servers start successfully
- [ ] Basic tool calls work (get_status, get_table_stats, get_browser_history)

### Phase 2: Validation ✅
- [ ] Tool audit complete (working vs. placeholder inventory)
- [ ] Service integration tested
- [ ] Missing dependencies identified and resolved

### Phase 3: Enhancement ✅
- [ ] Priority 0 tools implemented and tested
- [ ] Data protection enforcement added
- [ ] Integration tests passing

---

## Quick Start Commands

**Install everything:**
```bash
cd /Users/jeremyserna/truth_forge
source .venv/bin/activate

# Install MCP servers
pip install -e mcp-servers/truth-forge-mcp
pip install -e mcp-servers/spine-analysis-mcp
pip install -e mcp-servers/truth-browser-logger

# Test
python -c "import truth_forge_mcp, spine_analysis_mcp, truth_browser_logger; print('All imports OK')"
```

**Run audit:**
```bash
cd mcp-servers
grep -r "NotImplementedError\|placeholder\|TODO\|FIXME" truth-forge-mcp/src/ > tool_audit.txt
cat tool_audit.txt
```

**Test servers:**
```bash
# Each in separate terminal
cd mcp-servers/truth-forge-mcp && /usr/local/bin/python3.12 -m truth_forge_mcp.server
cd mcp-servers/spine-analysis-mcp && /usr/local/bin/python3.12 -m spine_analysis_mcp.server
cd mcp-servers/truth-browser-logger && /usr/local/bin/python3.12 -m truth_browser_logger.server
```

---

**Status**: 📋 **ACTION PLAN READY**

*Next: Execute Step 1 (Verify & Sync)*
