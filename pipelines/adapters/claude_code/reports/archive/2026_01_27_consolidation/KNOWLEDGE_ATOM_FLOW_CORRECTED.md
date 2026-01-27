> **DEPRECATED**: This document has been superseded.
> - **Superseded By**: [CANONICAL_KNOWLEDGE_ATOMS_COMPLETE.md](CANONICAL_KNOWLEDGE_ATOMS_COMPLETE.md) or [ID_SYSTEM_IMPLEMENTATION_COMPLETE.md](ID_SYSTEM_IMPLEMENTATION_COMPLETE.md) or [ID_SYSTEM_FEDERATION_UPGRADE_COMPLETE.md](ID_SYSTEM_FEDERATION_UPGRADE_COMPLETE.md)
> - **Deprecated On**: 2026-01-27
> - **Archived On**: 2026-01-27
> - **Reason**: Consolidated into complete implementation documents.
>
> This document has been moved to archive. See archive location below.

---

# Knowledge Atom Flow - Corrected Understanding

**Date:** 2026-01-22  
**Status:** ✅ **CORRECTED**

---

## Correct Understanding

### Knowledge Atoms Are Produced Locally at Agent Sites

**Key Principle:** Knowledge atoms are produced locally at the site of the agents (pipeline stages) and moved to the knowledge atom system holds by the router.

### The Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE STAGE (Agent Site)                  │
│                                                                 │
│  1. Stage processes pipeline data                               │
│     (HOLD₁ → AGENT → HOLD₂ for pipeline data)                   │
│                                                                 │
│  2. Stage produces knowledge atoms LOCALLY (in memory)          │
│     - Content: Stage-specific discoveries, insights, metrics   │
│     - Metadata: Stage number, run_id, transformations            │
│                                                                 │
│  3. Stage calls get_knowledge_service().exhale()               │
│     (Breathing function - writes to knowledge atom system)     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│           KNOWLEDGE ATOM SYSTEM HOLD₁ (Intake)                  │
│                                                                 │
│  Location: Primitive/system_elements/holds/                     │
│            knowledge_atoms/intake/hold1.jsonl                   │
│                                                                 │
│  - Receives atoms from all agents (pipeline stages)            │
│  - Deduplication: Content hash (exact matches)                 │
│  - This is the "pipeline hold" - where atoms land first         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ROUTER (execute())                           │
│                                                                 │
│  Moves atoms from HOLD₁ to HOLD₂                                │
│                                                                 │
│  1. Reads from Knowledge Atom System HOLD₁                      │
│  2. Processes through _atom_agent() (AGENT):                     │
│     - Generates atom_id                                         │
│     - Generates embedding                                       │
│     - Generates hash (first 16 chars)                          │
│     - Disaggregates (spaCy)                                     │
│  3. Writes to Knowledge Atom System HOLD₂                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         KNOWLEDGE ATOM SYSTEM HOLD₂ (Processed)                 │
│                                                                 │
│  Location: Primitive/system_elements/holds/                     │
│            knowledge_atoms/processed/hold2.jsonl + hold2.duckdb│
│                                                                 │
│  - Canonical knowledge atom store                               │
│  - Deduplication: Column-based (atom_id) + similarity (0.95)   │
│  - Ready for RAG and knowledge graph                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Two Separate HOLD Systems

### 1. Pipeline HOLDs (Pipeline Data)

**Purpose:** Store pipeline data as it flows through stages

**Example:**
- `claude_code_stage_0` → `claude_code_stage_1` (discovery → extraction)
- `claude_code_stage_1` → `claude_code_stage_2` (extraction → normalization)
- etc.

**Location:** Pipeline-specific staging areas (BigQuery tables, JSONL files)

### 2. Knowledge Atom System HOLDs (Meta-Knowledge)

**Purpose:** Store knowledge atoms about pipeline execution itself

**HOLD₁ (Intake):**
- Location: `Primitive/system_elements/holds/knowledge_atoms/intake/hold1.jsonl`
- Receives atoms from all agents (pipeline stages, other systems)
- This is where atoms land when agents exhale

**HOLD₂ (Processed):**
- Location: `Primitive/system_elements/holds/knowledge_atoms/processed/hold2.jsonl + hold2.duckdb`
- Canonical store after router processing
- Ready for RAG and knowledge graph

---

## Router Functionality

**Router:** `PrimitivePattern.execute()`

**What It Does:**
1. Reads from Knowledge Atom System HOLD₁ (intake)
2. Processes each atom through `_atom_agent()`:
   - Generates canonical atom_id
   - Generates embedding for similarity search
   - Generates hash for deduplication
   - Disaggregates content (spaCy) for NLP features
3. Writes to Knowledge Atom System HOLD₂ (processed)
   - Applies column-based deduplication (by `atom_id`)
   - Applies similarity-based deduplication (0.95 threshold)

**When It Runs:**
- Automatically when `exhale()` is called (immediate processing)
- Manually via `sync()` (process pending atoms without new input)

---

## Validation Confirmation

✅ **Pipeline stages produce knowledge atoms locally** (in memory at agent site)  
✅ **Atoms are written to Knowledge Atom System HOLD₁** (intake)  
✅ **Router moves atoms from HOLD₁ to HOLD₂** (processed)  
✅ **Deduplication works at both HOLD₁ and HOLD₂**  
✅ **Similarity normalization works at HOLD₂** (0.95 threshold)

---

## Summary

**The router moves knowledge atoms from the pipeline holds (Knowledge Atom System HOLD₁) to the knowledge atom system holds (Knowledge Atom System HOLD₂).**

- **Pipeline holds** = Knowledge Atom System HOLD₁ (intake)
- **Knowledge atom system holds** = Knowledge Atom System HOLD₂ (processed)
- **Router** = `execute()` method that moves atoms HOLD₁ → HOLD₂

Knowledge atoms are produced locally at the site of the agents (pipeline stages) and moved by the router to the canonical knowledge atom store.
