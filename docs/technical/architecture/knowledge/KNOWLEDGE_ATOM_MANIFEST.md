# Knowledge Atom Manifest

Generated: 2025-12-25
Last Updated: 2025-12-25T23:45:00Z

This manifest tracks high-value documents that should be processed for knowledge atoms.

## Summary

| Tier | Documents | Atoms | Status |
|------|-----------|-------|--------|
| Tier 1 | 15 processed | 199 atoms | Complete |
| Tier 2 | 8 pending | - | Pending |
| Tier 3 | ~21 pending | - | Pending |

## Processing Priority

### Tier 1: HIGHEST (System Philosophy & Behavioral Substrate)

These documents define how the system thinks and operates. They should be processed first and kept up to date.

#### docs/product/ (5 files processed → 110 atoms)

| File | Status | Description |
|------|--------|-------------|
| THE_COMPLETE_SYSTEM.md | 🟢 Complete (42 atoms) | Full layer stack (L0-L4) |
| THE_OPERATING_FRAMEWORK.md | 🟢 Complete (18 atoms) | DOD, Good Enough, Optimization |
| SUBSTRATE_INVARIANTS.md | 🟢 Complete (16 atoms) | Physical reality constraints (L0) |
| THE_SEEING_PRIMITIVE.md | 🟢 Complete (22 atoms) | Core observation pattern |
| CLAUDE_MEMBRANE_PATTERN.md | 🟢 Complete (12 atoms) | Context injection patterns |
| SYSTEM_INVARIANTS.md | 🔴 Pending | What never changes (L1-L3) |
| DESIGN_PRINCIPLES.md | 🔴 Pending | Why decisions are made |
| THE_BECOMING.md | 🔴 Pending | System evolution philosophy |
| TRUTH_ENGINE_VISION.md | 🔴 Pending | Overall vision |
| SYSTEM_ARCHITECTURE.md | 🔴 Pending | Technical architecture |
| DATA_MODELS.md | 🔴 Pending | Entity structures |
| SCRIPT_EXECUTION_LAYER.md | 🔴 Pending | How scripts run |
| AUDIENCE_EXPERIENCES.md | 🔴 Pending | User journeys |
| IMPLEMENTATION_ROADMAP.md | 🔴 Pending | Future plans |
| README.md | 🔴 Pending | Index |

#### .claude/rules/ (10 files processed → 89 atoms)

| File | Status | Description |
|------|--------|-------------|
| 00-README.md | 🟢 Complete (6 atoms) | Rules index |
| 01-cost-protection.md | 🟢 Complete (12 atoms) | $1,493+ incident prevention |
| 02-bigquery-patterns.md | 🟢 Complete (10 atoms) | SQL-first patterns |
| 03-central-services.md | 🟢 Complete (9 atoms) | Required imports |
| 04-code-review.md | 🟢 Complete (8 atoms) | 8-pattern checklist |
| 05-stage-five.md | 🟢 Complete (10 atoms) | Cognitive isomorphism |
| 06-pipelines.md | 🟢 Complete (8 atoms) | Universal Pipeline Pattern |
| 07-file-org.md | 🟢 Complete (10 atoms) | Sprawl prevention |
| 08-substrate-awareness.md | 🟢 Complete (10 atoms) | Operating FROM substrate |
| 09-operating-framework.md | 🟢 Complete (6 atoms) | DOD, Good Enough, Optimization |

### Tier 2: HIGH (Technical Architecture)

Core architectural patterns and specifications.

#### docs/architecture/ (Selected high-value)

| File | Status | Description |
|------|--------|-------------|
| IDENTITY_LAYER_ARCHITECTURE.md | 🔴 Pending | Identity system design |
| LAYERED_PRIMITIVE_ARCHITECTURE.md | 🔴 Pending | Layer abstraction patterns |
| CORE_PATTERNS.md | 🔴 Pending | Reusable patterns |
| RAG_SYSTEM_ARCHITECTURE.md | 🔴 Pending | Retrieval system |
| MULTI_TIER_LLM_ENRICHMENT_ARCHITECTURE.md | 🔴 Pending | LLM integration |
| SEEING_ARCHITECTURE.md | 🔴 Pending | Observation patterns |
| DATA_SOURCE_UNIVERSAL_BLUEPRINT.md | 🔴 Pending | Ingestion patterns |
| UNIFIED_ENRICHMENT_PIPELINE.md | 🔴 Pending | Enrichment flow |

### Tier 3: MEDIUM (Specialized Docs)

Domain-specific documentation that provides context.

- Zoom architecture docs (14 files)
- Identity layer docs (7 files)
- Pipeline-specific docs

---

## Processing Notes

### What to Extract as Knowledge Atoms

1. **Definitions**: What terms mean in this system
2. **Patterns**: Reusable approaches
3. **Decisions**: Why things are the way they are
4. **Constraints**: What can't change
5. **Relationships**: How things connect

### Processing Approach

1. Read document
2. Extract discrete facts (atoms)
3. Tag with source, category, confidence
4. Store in BigQuery `knowledge.atoms`
5. Update manifest status

### Status Key

- 🔴 Pending - Not yet processed
- 🟡 Processing - Currently being extracted
- 🟢 Complete - Atoms extracted
- ⚫ Skipped - Not applicable

---

## Related

- [KNOWLEDGE_ATOM_GOVERNANCE_SYSTEM.md](./KNOWLEDGE_ATOM_GOVERNANCE_SYSTEM.md)
- [KNOWLEDGE_ATOM_QUALITY_FRAMEWORK.md](./KNOWLEDGE_ATOM_QUALITY_FRAMEWORK.md)
