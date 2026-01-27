# Open Questions Before Migration

**Status**: NEEDS RESOLUTION
**Created**: 2026-01-26

These questions must be resolved before finalizing the migration plan.

---

## 1. Module Naming: Biological vs Practical

**Question**: Do we keep the biological/cognitive naming (soul, consciousness, anima, spirit, will) or consolidate to more practical names?

**Options**:

| Option | Structure | Competitive Advantage |
|--------|-----------|----------------------|
| **A: Keep All** | 6 separate modules (soul, consciousness, cognition, spirit, anima, will) | Maximum uniqueness, but fragmented |
| **B: Consolidate to 3** | mind/cognition, mind/consciousness, mind/values | Balanced - keeps vocabulary, reduces fragmentation |
| **C: Flatten to 1** | mind/ (all combined) | Simplest, but loses nuance |

**My Recommendation**: Option B - keeps the vocabulary that represents your mental architecture, but organizes it practically.

**Your Decision**: _________________

---

## 2. Services Consolidation: Specific Merges

**Question**: Confirm which services merge:

| Proposed Merge | From | To | Confirm? |
|----------------|------|----|----|
| Knowledge consolidation | knowledge_graph_service + search_service | knowledge_service/ | ☐ |
| Identity consolidation | identity_service + relationship_service | identity_service/ | ☐ |
| Quality consolidation | quality_service + testing_service | quality_service/ | ☐ |
| Pipeline consolidation | pipeline_health_service + workflow_service | pipeline_service/ | ☐ |
| Analytics consolidation | analytics_service + cost_service | analytics_service/ | ☐ |

**Your Decision**: _________________

---

## 3. MCP Servers: Which Are Active?

**Current State**:
- Only `official-servers/` has a package.json
- Others appear to be Python-based or incomplete

| Server | Has package.json | Migrate? |
|--------|------------------|----------|
| truth-engine-mcp | NO | ☐ YES / ☐ ARCHIVE |
| governance-git | NO | ☐ YES / ☐ ARCHIVE |
| governance-middleware | NO | ☐ YES / ☐ ARCHIVE |
| orchestration | NO | ☐ YES / ☐ ARCHIVE |
| playwright-logged | NO | ☐ YES / ☐ ARCHIVE |
| sequential-thinking-proxy | NO | ☐ YES / ☐ ARCHIVE |
| truth-browser-logger | NO | ☐ YES / ☐ ARCHIVE |
| official-servers | YES | ☐ YES / ☐ ARCHIVE |

**Your Decision**: _________________

---

## 4. Database Strategy

**Current State**: 10+ DuckDB files scattered across:
- `.truth_engine/atoms.duckdb` (main?)
- `.truth_engine/atoms_cloud.duckdb`
- `.truth_engine/primitive/atom1.duckdb`, `atom2.duckdb`
- `data/test.duckdb`
- `test.duckdb` (root)
- `data/archive/...` (archived)

**Question**: What is the canonical database structure post-migration?

**Options**:
| Option | Structure |
|--------|-----------|
| A: Single DB | `data/knowledge.duckdb` (consolidate all) |
| B: Functional split | `data/atoms.duckdb` + `data/cloud.duckdb` |
| C: Keep as-is | Multiple databases, document purpose of each |

**Your Decision**: _________________

---

## 5. Environment Files

**Current State**: 10+ .env files across projects

**Question**: Post-migration structure?

**Recommendation**:
```
config/
├── base/
│   └── .env.example       # Template (committed)
└── local/
    └── .env               # Actual secrets (gitignored)
```

**Your Decision**: ☐ Accept / ☐ Modify

---

## 6. Test Coverage Requirements

**Current State**:
- 18 test files in tests/
- Unit tests in tests/unit/
- Some service-specific tests (migrated services)

**Question**: What is the minimum test coverage requirement?

| Level | Requirement |
|-------|-------------|
| **Critical services** (core, hold, identity) | ___% coverage |
| **Domain modules** (cognition, governance) | ___% coverage |
| **Apps** | ___% coverage |
| **Pipelines** | ___% coverage |

**Your Decision**: _________________

---

## 7. Framework Inheritance

**Question**: How do primitive_engine and credential_atlas inherit from truth_forge's framework?

**Current Understanding**:
- `framework/` lives ONLY in truth_forge (genesis)
- Children (PE, CA) reference genesis framework via `.seed/sync.py`

**Confirm**:
- ☐ PE and CA should NOT have their own framework/ directory
- ☐ PE and CA read standards from `~/truth_forge/framework/`
- ☐ Sync mechanism pulls updates from genesis

**Your Decision**: _________________

---

## 8. Data Migration

**Current State**: `data/` has 80+ subdirectories including:
- `staging/` (multiple)
- `services/*/staging/` (per-service staging)
- `local/`
- `archive/`
- Various project data

**Question**: What data moves vs. stays as reference?

| Category | Action |
|----------|--------|
| `data/staging/` | MOVE (active) |
| `data/local/` | MOVE (active) |
| `data/services/*/staging/` | CONSOLIDATE to `data/staging/` |
| `data/archive/` | KEEP IN ARCHIVE (reference) |
| Project-specific data | EVALUATE per project |

**Your Decision**: _________________

---

## 9. Pipelines: Active vs Deprecated

**Current Pipelines**:
| Pipeline | Status | Migrate? |
|----------|--------|----------|
| core/ | Active | ☐ YES |
| adapters/ | Active | ☐ YES |
| claude_code/ | Active? | ☐ YES / ☐ ARCHIVE |
| gemini_web/ | Active? | ☐ YES / ☐ ARCHIVE |
| text_messages/ | Active? | ☐ YES / ☐ ARCHIVE |
| docs/ | Documentation | ☐ YES / ☐ ARCHIVE |

**Your Decision**: _________________

---

## 10. Scripts: Which Are Essential?

**Current State**: 113 items in scripts/

**Question**: Which script categories are essential for migration?

| Category | Essential? | Notes |
|----------|------------|-------|
| daemon/ | ☐ YES | Background services |
| deployment/ | ☐ YES | Deployment scripts |
| automation/ | ☐ YES | Automation tools |
| analysis/ | ☐ MAYBE | Analysis scripts |
| compliance/ | ☐ YES | Compliance checks |
| monitoring/ | ☐ YES | Monitoring scripts |
| _archive/ | ☐ NO | Already archived |
| _deprecated/ | ☐ NO | Already deprecated |

**Your Decision**: _________________

---

## 11. Quality Gates

**Confirm these are the quality gates for EVERY migrated item**:

```bash
# Must ALL pass before item is "OPERATIONAL"
.venv/bin/pytest tests/ -k "{module}" -v          # Tests pass
.venv/bin/mypy src/truth_forge/{module}/ --strict  # Type checking
.venv/bin/ruff check src/truth_forge/{module}/     # Linting
.venv/bin/ruff format --check src/truth_forge/{module}/  # Formatting
python -c "from truth_forge.{module} import *"     # Imports work
```

**Your Decision**: ☐ Confirmed / ☐ Modify

---

## 12. Dependency Order Verification

**Question**: Is this the correct dependency order for services?

```
Phase 1: Core (no dependencies)
    └── core.py, result.py, logger.py, core/, config/, schema/

Phase 2: Foundation Services
    ├── identity_service (depends on: core)
    ├── config_service (depends on: identity)
    ├── hold_service (depends on: config)
    └── version_service (depends on: core)

Phase 3: Knowledge Services
    ├── knowledge_service (depends on: hold)
    ├── search_service (depends on: knowledge)
    └── knowledge_graph_service (depends on: knowledge)

Phase 4: Operational Services
    ├── run_service (depends on: core)
    ├── cost_service (depends on: core)
    ├── analytics_service (depends on: knowledge)
    └── monitoring_service (depends on: core)

Phase 5: Domain Services
    ├── care_service (depends on: knowledge)
    ├── relationship_service (depends on: identity)
    ├── quality_service (depends on: core)
    └── remaining services...
```

**Your Decision**: ☐ Confirmed / ☐ Modify

---

## Summary: Decisions Needed

| # | Question | Status |
|---|----------|--------|
| 1 | Module naming (biological vs practical) | ☐ PENDING |
| 2 | Services consolidation (specific merges) | ☐ PENDING |
| 3 | MCP servers (which are active) | ☐ PENDING |
| 4 | Database strategy | ☐ PENDING |
| 5 | Environment files structure | ☐ PENDING |
| 6 | Test coverage requirements | ☐ PENDING |
| 7 | Framework inheritance model | ☐ PENDING |
| 8 | Data migration scope | ☐ PENDING |
| 9 | Pipelines (active vs deprecated) | ☐ PENDING |
| 10 | Scripts (which are essential) | ☐ PENDING |
| 11 | Quality gates | ☐ PENDING |
| 12 | Dependency order | ☐ PENDING |

---

*Once all questions are resolved, the migration plan will be finalized with concrete, executable steps.*

— Open Questions v1.0, 2026-01-26
