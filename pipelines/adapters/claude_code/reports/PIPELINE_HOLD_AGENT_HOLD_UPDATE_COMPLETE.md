# Pipeline HOLD → AGENT → HOLD Pattern Update - Complete

**Date:** 2026-01-22  
**Status:** ✅ **IMPLEMENTATION COMPLETE**

---

## Summary

All pipeline stages have been updated to follow the correct HOLD → AGENT → HOLD pattern where:
1. **Pipeline systems produce knowledge atoms and place them in HOLD₂ of the pipeline holds**
2. **They are stored there until they are retrieved**
3. **Each pipeline script follows the HOLD → AGENT → HOLD pattern**

---

## Changes Made

### 1. Created Utility Function (`shared/utilities.py`)

**Function:** `write_knowledge_atom_to_pipeline_hold2()`

- Writes knowledge atoms to pipeline-specific HOLD₂
- Location: `pipelines/claude_code/staging/knowledge_atoms/stage_{N}/hold2.jsonl`
- Deduplication: Content hash (exact matches)
- Status: `"pending"` (until retrieved by router)

**Function:** `get_pipeline_hold2_path()`

- Returns path to pipeline HOLD₂ for a specific stage
- Creates directory structure if needed

### 2. Updated All 17 Pipeline Stages (0-16)

**Changed from:**
```python
get_knowledge_service().exhale(
    content=content,
    source_name="claude_code_pipeline",
    source_id=run_id,
    metadata=metadata,
)
```

**Changed to:**
```python
from shared import write_knowledge_atom_to_pipeline_hold2

write_knowledge_atom_to_pipeline_hold2(
    content=content,
    stage=N,
    run_id=run_id,
    source_name="claude_code_pipeline",
    source_id=run_id,
    metadata=metadata,
)
```

**All stages updated:**
- ✅ Stage 0: Discovery
- ✅ Stage 1: Extraction
- ✅ Stage 2: Cleaning
- ✅ Stage 3: Identity Generation
- ✅ Stage 4: Text Correction
- ✅ Stage 5: L8 Conversation Creation
- ✅ Stage 6: L6 Turn Creation
- ✅ Stage 7: L5 Message Creation
- ✅ Stage 8: L4 Sentence Creation
- ✅ Stage 9: L3 Span Creation
- ✅ Stage 10: L2 Word Creation
- ✅ Stage 11: Link Validation
- ✅ Stage 12: Count Denormalization
- ✅ Stage 13: Final Validation
- ✅ Stage 14: Promotion to entity_unified
- ✅ Stage 15: Final Validation
- ✅ Stage 16: Final Promotion

### 3. Created Router Script (`router_knowledge_atoms.py`)

**Purpose:** Retrieve knowledge atoms from pipeline HOLD₂ and move to Knowledge Atom System HOLD₂

**Functionality:**
- Reads from all pipeline stage HOLD₂ files
- Processes atoms through canonical knowledge service
- Marks atoms as "retrieved" in pipeline HOLD₂
- Moves atoms to Knowledge Atom System HOLD₂ (canonical store)

**Usage:**
```bash
# Process all stages
python router_knowledge_atoms.py --all

# Process specific stage
python router_knowledge_atoms.py --stage 0
```

---

## Architecture Flow

### Pipeline Stage Execution

```
Pipeline Stage (HOLD → AGENT → HOLD)
    │
    ├─► HOLD₁: Pipeline input data
    │
    ├─► AGENT:
    │   ├─► Process pipeline data
    │   └─► Produce knowledge atoms locally
    │
    └─► HOLD₂:
        ├─► Pipeline output data (for next stage)
        └─► Knowledge atoms (stored in pipeline HOLD₂)
            └─► Location: pipelines/claude_code/staging/knowledge_atoms/stage_{N}/hold2.jsonl
            └─► Status: "pending" (until retrieved)
```

### Router Execution

```
Router (HOLD → AGENT → HOLD)
    │
    ├─► HOLD₁: Pipeline HOLD₂ files (all stages)
    │
    ├─► AGENT:
    │   ├─► Read atoms from pipeline HOLD₂
    │   ├─► Process through canonical knowledge service
    │   └─► Mark atoms as "retrieved"
    │
    └─► HOLD₂: Knowledge Atom System HOLD₂
        └─► Location: Primitive/system_elements/holds/knowledge_atoms/processed/hold2.jsonl + hold2.duckdb
        └─► Deduplication: Column-based + similarity (0.95 threshold)
```

---

## File Locations

### Pipeline HOLD₂ (Per Stage)
- **Location:** `pipelines/claude_code/staging/knowledge_atoms/stage_{N}/hold2.jsonl`
- **Format:** JSONL (one atom per line)
- **Status Field:** `"pending"` (not yet retrieved) or `"retrieved"` (already processed)

### Knowledge Atom System HOLD₂ (Canonical)
- **Location:** `Primitive/system_elements/holds/knowledge_atoms/processed/hold2.jsonl + hold2.duckdb`
- **Format:** JSONL (audit) + DuckDB (queryable)
- **Deduplication:** Column-based (`atom_id`) + similarity (0.95 threshold)

---

## Verification

### ✅ All Stages Updated
- All 17 stages (0-16) now use `write_knowledge_atom_to_pipeline_hold2()`
- No stages call `get_knowledge_service().exhale()` directly

### ✅ HOLD → AGENT → HOLD Pattern
- Each stage documents HOLD₁ → AGENT → HOLD₂ pattern
- Knowledge atoms are written to pipeline HOLD₂ (not directly to knowledge atom system)
- Router retrieves from pipeline HOLD₂ and moves to canonical store

### ✅ Router Created
- Router script exists: `router_knowledge_atoms.py`
- Can process all stages or specific stage
- Marks atoms as "retrieved" after processing

---

## Next Steps

1. **Test pipeline execution** - Verify knowledge atoms are written to pipeline HOLD₂
2. **Test router execution** - Verify router retrieves and moves atoms correctly
3. **Verify deduplication** - Ensure deduplication works at both pipeline HOLD₂ and canonical HOLD₂
4. **Verify similarity normalization** - Ensure similarity checks work in canonical HOLD₂

---

## Summary

**✅ Pipeline updated to accommodate HOLD → AGENT → HOLD pattern**

- Knowledge atoms are produced locally at pipeline stages
- Knowledge atoms are stored in pipeline HOLD₂ (per stage)
- Router retrieves from pipeline HOLD₂ and moves to Knowledge Atom System HOLD₂
- Each pipeline script follows HOLD → AGENT → HOLD pattern
