# Pipeline HOLD → AGENT → HOLD Pattern for Knowledge Atoms

**Date:** 2026-01-22  
**Status:** ✅ **REQUIREMENT CLARIFIED**

---

## Correct Architecture

### Key Principle

**Pipeline systems produce knowledge atoms and place them in HOLD₂ of the pipeline holds. They are stored there until they are retrieved. Each pipeline script must be a HOLD → AGENT → HOLD pattern.**

---

## The Pattern

### Each Pipeline Script Must Follow:

```
HOLD₁ (Input) → AGENT (Script) → HOLD₂ (Output)
```

**For Knowledge Atoms:**
- **HOLD₁:** Pipeline input data (e.g., `claude_code_stage_0` → `claude_code_stage_1`)
- **AGENT:** Pipeline stage processing + knowledge atom production
- **HOLD₂:** Pipeline output data + **knowledge atoms stored in pipeline HOLD₂**

---

## Knowledge Atom Flow

### Current Understanding (Needs Implementation)

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE STAGE (HOLD → AGENT → HOLD)        │
│                                                                 │
│  HOLD₁: Pipeline input data                                     │
│    (e.g., claude_code_stage_0 output)                          │
│                                                                 │
│  AGENT:                                                          │
│    1. Process pipeline data                                     │
│    2. Produce knowledge atoms locally (in memory)              │
│    3. Write knowledge atoms to pipeline HOLD₂                   │
│                                                                 │
│  HOLD₂:                                                          │
│    - Pipeline output data (for next stage)                      │
│    - Knowledge atoms (stored in pipeline HOLD₂)                  │
│      Location: Pipeline-specific staging area                  │
│      Format: JSONL or DuckDB                                    │
│      Status: Stored until retrieved by router                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ (Router retrieves)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ROUTER (Retrieval & Processing)               │
│                                                                 │
│  1. Reads knowledge atoms from pipeline HOLD₂                   │
│  2. Processes through _atom_agent() (AGENT):                    │
│     - Generates atom_id                                         │
│     - Generates embedding                                       │
│     - Generates hash                                            │
│     - Disaggregates (spaCy)                                     │
│  3. Writes to Knowledge Atom System HOLD₂                       │
│     - Deduplication: Column-based + similarity                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         KNOWLEDGE ATOM SYSTEM HOLD₂ (Canonical Store)           │
│                                                                 │
│  Location: Primitive/system_elements/holds/                     │
│            knowledge_atoms/processed/hold2.jsonl + hold2.duckdb│
│                                                                 │
│  - Canonical knowledge atom store                               │
│  - Ready for RAG and knowledge graph                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Requirements

### 1. Each Pipeline Script Must Be HOLD → AGENT → HOLD

**Required Documentation:**
```python
"""
Script Name - Brief Description

HOLD₁ ({input_type}) → AGENT ({what_script_does}) → HOLD₂ ({output_type})

{Detailed description}
"""
```

**Example:**
```python
"""
Stage 0: Discovery - Claude Code Pipeline

HOLD₁ (JSONL session files) → AGENT (Format Analyzer) → HOLD₂ (Assessment Report + Knowledge Atoms)

Discovers and analyzes source files, produces discovery manifest,
and stores knowledge atoms in pipeline HOLD₂.
"""
```

### 2. Knowledge Atoms Stored in Pipeline HOLD₂

**Location:** Pipeline-specific staging area
- Each pipeline has its own HOLD₂ for knowledge atoms
- Knowledge atoms are stored alongside pipeline output data
- Format: JSONL or DuckDB (pipeline-specific)

**Storage:**
- Knowledge atoms remain in pipeline HOLD₂ until retrieved
- Router retrieves them and moves to knowledge atom system
- Pipeline HOLD₂ serves as temporary storage

### 3. Router Retrieval

**Router Function:**
- Reads knowledge atoms from pipeline HOLD₂
- Processes through `_atom_agent()` (canonical processing)
- Writes to Knowledge Atom System HOLD₂ (canonical store)
- Applies deduplication and similarity normalization

**When Router Runs:**
- On-demand (when knowledge atoms need to be moved)
- Periodic (batch processing of pipeline HOLD₂)
- Automatic (after pipeline stage completes)

---

## Implementation Status

### Current Implementation

**Issue:** Pipeline stages currently call `get_knowledge_service().exhale()` which writes directly to Knowledge Atom System HOLD₁.

**Required Change:**
1. Pipeline stages should write knowledge atoms to their own HOLD₂
2. Router should retrieve from pipeline HOLD₂
3. Router should move to Knowledge Atom System HOLD₂

### Validation Checklist

- [ ] Each pipeline script documents HOLD → AGENT → HOLD pattern
- [ ] Knowledge atoms are written to pipeline HOLD₂ (not directly to knowledge atom system)
- [ ] Router can retrieve from pipeline HOLD₂
- [ ] Router moves atoms to Knowledge Atom System HOLD₂
- [ ] Deduplication works at both pipeline HOLD₂ and knowledge atom system HOLD₂
- [ ] Similarity normalization works at knowledge atom system HOLD₂

---

## Summary

**Pipeline systems produce knowledge atoms and place them in HOLD₂ of the pipeline holds. They are stored there until they are retrieved. Each pipeline script must be a HOLD → AGENT → HOLD pattern.**

- **Pipeline HOLD₂:** Where knowledge atoms are stored (temporary)
- **Router:** Retrieves from pipeline HOLD₂ and moves to knowledge atom system
- **Knowledge Atom System HOLD₂:** Canonical store (permanent)
