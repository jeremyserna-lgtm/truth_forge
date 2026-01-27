# Architecture Correction Needed

**Date:** 2026-01-22  
**Status:** ⚠️ **REQUIRES IMPLEMENTATION UPDATE**

---

## User Clarification

**Key Requirements:**
1. **Pipeline systems produce knowledge atoms and place them in HOLD₂ of the pipeline holds**
2. **They are stored there until they are retrieved**
3. **Each pipeline script must be a HOLD → AGENT → HOLD pattern**

---

## Current Implementation vs. Required Implementation

### Current Implementation (Incorrect)

```
Pipeline Stage
    │
    ├─► get_knowledge_service().exhale()
    │   └─► Writes directly to Knowledge Atom System HOLD₁
    │
    └─► Router processes immediately
        └─► Moves to Knowledge Atom System HOLD₂
```

**Problem:** Knowledge atoms bypass pipeline HOLD₂ and go directly to knowledge atom system.

### Required Implementation (Correct)

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
            └─► Stored until retrieved by router
                │
                ▼ (Router retrieves)
        Router
            ├─► Reads from pipeline HOLD₂
            ├─► Processes through _atom_agent()
            └─► Writes to Knowledge Atom System HOLD₂
```

---

## Required Changes

### 1. Pipeline Stages Must Follow HOLD → AGENT → HOLD Pattern

**Each script must document:**
```python
"""
HOLD₁ ({input}) → AGENT ({processing}) → HOLD₂ ({output + knowledge atoms})
"""
```

**Knowledge atoms must be written to pipeline HOLD₂, not directly to knowledge atom system.**

### 2. Pipeline HOLD₂ for Knowledge Atoms

**Location:** Pipeline-specific staging area
- Each pipeline has its own HOLD₂
- Knowledge atoms stored alongside pipeline output
- Format: JSONL or DuckDB (pipeline-specific)

**Storage Pattern:**
- Knowledge atoms remain in pipeline HOLD₂ until retrieved
- Router retrieves them periodically or on-demand
- Router moves them to Knowledge Atom System HOLD₂

### 3. Router Retrieval Mechanism

**Router must:**
- Read knowledge atoms from pipeline HOLD₂
- Process through `_atom_agent()` (canonical processing)
- Write to Knowledge Atom System HOLD₂
- Apply deduplication and similarity normalization

**When router runs:**
- On-demand (when knowledge atoms need to be moved)
- Periodic (batch processing)
- After pipeline stage completes (optional)

---

## Validation Status

### ✅ What's Validated (Current Implementation)

- Pipeline stages produce knowledge atoms
- Knowledge service has required methods
- Router functionality exists
- Deduplication works
- Similarity normalization works

### ⚠️ What Needs Correction

- **Knowledge atoms should be written to pipeline HOLD₂, not directly to knowledge atom system**
- **Router should retrieve from pipeline HOLD₂, not process immediately**
- **Each pipeline script must explicitly follow HOLD → AGENT → HOLD pattern for knowledge atoms**

---

## Next Steps

1. **Update pipeline stages** to write knowledge atoms to their own HOLD₂
2. **Implement router retrieval** from pipeline HOLD₂
3. **Verify HOLD → AGENT → HOLD pattern** in all pipeline scripts
4. **Update validation** to check pipeline HOLD₂ storage
5. **Test router retrieval** mechanism

---

## Summary

**The architecture needs to be updated so that:**
- Pipeline stages write knowledge atoms to **pipeline HOLD₂** (not directly to knowledge atom system)
- Knowledge atoms are **stored in pipeline HOLD₂ until retrieved**
- Router **retrieves from pipeline HOLD₂** and moves to knowledge atom system
- Each pipeline script **explicitly follows HOLD → AGENT → HOLD pattern**
