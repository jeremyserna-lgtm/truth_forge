# Knowledge Atom System

**The Canonical Atomic Truth Management System**

---

## Executive Summary

The Knowledge Atom System transforms any data source into **atomic knowledge units** - the foundational form of truth in the Truth Engine. It extracts, stores, normalizes, and makes queryable every piece of knowledge from documents, conversations, emails, and system events.

| Metric | Value |
|--------|-------|
| **Total Atoms** | 20,616 |
| **Unique Concepts** | 5,769 |
| **Unique Entities** | 165 |
| **Unique Principles** | 2,647 |
| **Document Runs** | 1,156 |

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [System Architecture](#system-architecture)
3. [The Knowledge Atom](#the-knowledge-atom)
4. [Extraction Pipeline](#extraction-pipeline)
5. [Storage Architecture](#storage-architecture)
6. [L2 Normalization](#l2-normalization)
7. [Service API](#service-api)
8. [BigQuery Schema](#bigquery-schema)
9. [Truth Engine Standards Alignment](#truth-engine-standards-alignment)
10. [Scripts Reference](#scripts-reference)

---

## Core Concepts

### What is a Knowledge Atom?

A **Knowledge Atom** is a complete, bounded unit of knowledge that represents **ONE single whole thing**. It is:

| Property | Description |
|----------|-------------|
| **Complete** | Expresses a full thought that can stand alone |
| **Self-contained** | Understandable without external context |
| **Atomic** | Cannot be split without losing meaning |
| **Bounded** | Has clear start and end boundaries |
| **Traceable** | Full lineage back to source |
| **Queryable** | Searchable via text, concepts, entities, semantic similarity |

### The Foundational Principle

> "Knowledge atoms are the foundational, universal form of truth that anything in the system can become."

Any data - documents, conversations, emails, system events, operations - can be transformed into knowledge atoms. Once transformed, all knowledge lives in the same queryable, traceable format.

### Atom vs Non-Atom

```
✅ GOOD ATOM (complete, self-contained):
"The Hybrid Durability pattern writes to local JSONL first, then syncs
to BigQuery, ensuring no data loss if cloud storage fails."

❌ BAD ATOM (incomplete):
"It's important to save data."
(What data? Why important? Missing context.)

❌ BAD ATOM (multiple truths):
"BigQuery costs $6.25/TB. Use MERGE for updates. Always cluster tables."
(Three separate truths - should be three atoms.)
```

---

## System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       KNOWLEDGE ATOM SYSTEM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐                                                            │
│  │   SOURCES   │                                                            │
│  ├─────────────┤                                                            │
│  │ Documents   │──┐                                                         │
│  │ Conversations│──┤                                                         │
│  │ Emails      │──┼──► ADAPTER LAYER ──► UNIFICATION LAYER ──► STORAGE     │
│  │ Events      │──┤    (shape data)      (extract atoms)       (persist)   │
│  │ Operations  │──┘                                                         │
│  └─────────────┘                                                            │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        ADAPTER LAYER                                 │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  TextAdapter    │  JSONAdapter    │  EventAdapter  │  GenericAdapter │   │
│  │  (strings)      │  (dicts/lists)  │  (events)      │  (anything)     │   │
│  │                 │                 │                │                 │   │
│  │  Shapes source data into LLM-reviewable content (UnifiedShape)      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      UNIFICATION LAYER                               │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  • Receives LLM-reviewable content from any adapter                 │   │
│  │  • Single LLM call (Gemini Flash) extracts atoms uniformly          │   │
│  │  • Returns List[KnowledgeAtom] - uniform shape regardless of source │   │
│  │                                                                      │   │
│  │  "Uniform, robust, cheap, reliable"                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       STORAGE LAYER                                  │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │   LOCAL (always)              CLOUD (selective)                     │   │
│  │   ┌──────────────┐            ┌──────────────┐                      │   │
│  │   │ JSONL Files  │──────────►│   BigQuery   │                      │   │
│  │   │              │  sync      │              │                      │   │
│  │   │ ~/.truth_    │            │ knowledge_   │                      │   │
│  │   │   engine/    │            │   atoms.*    │                      │   │
│  │   └──────────────┘            └──────────────┘                      │   │
│  │                                                                      │   │
│  │   Hybrid Durability: "Write local always, sync to cloud selectively"│   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **Adapter Layer** | Shape any source into LLM-reviewable format |
| **Unification Layer** | Extract atoms uniformly via single LLM call |
| **Local Store** | Persist atoms to JSONL (never fails) |
| **BigQuery Store** | Persist atoms for querying at scale |
| **L2 Normalization** | Link concepts/entities/principles to lookup tables |

---

## The Knowledge Atom

### Complete Field Reference

```python
@dataclass
class KnowledgeAtom:
    """The canonical atomic truth unit."""

    # ═══════════════════════════════════════════════════════════════
    # IDENTITY
    # ═══════════════════════════════════════════════════════════════
    atom_id: str              # "atom:386c440aeba6:2" - unique identifier
    parent_id: str            # Parent document/conversation ID
    content_hash: str         # SHA256 hash for deduplication

    # ═══════════════════════════════════════════════════════════════
    # THE KNOWLEDGE
    # ═══════════════════════════════════════════════════════════════
    content: str              # The atomic truth (complete, self-contained)

    # ═══════════════════════════════════════════════════════════════
    # CLASSIFICATION
    # ═══════════════════════════════════════════════════════════════
    knowledge_type: str       # "statement" | "question"

    # For statements:
    statement_type: str       # fact | decision | definition | rule |
                              # procedure | principle | pattern | answer | reflection

    # For questions:
    question_type: str        # what | how | why | when | where | which | who | can
    question_intent: str      # information_need | knowledge_gap | inquiry | clarification

    # Three-Layer Test (Truth Engine Standard):
    atom_layer: str           # theory | spec | reference
                              # theory = WHY (the reason)
                              # spec = WHAT (the constraint)
                              # reference = HOW (the method)

    domain: str               # technical | architectural | operational | governance | process
    category: str             # storage | pipeline | governance | architecture | etc.

    # ═══════════════════════════════════════════════════════════════
    # L2 RAW DATA (extracted by LLM)
    # ═══════════════════════════════════════════════════════════════
    terms: List[str]          # Technical terms ["BigQuery", "MERGE", "JSONL"]
    concepts: List[str]       # Abstract ideas ["hybrid durability", "cost protection"]
    entities: List[str]       # Named things ["Truth Engine", "Jeremy", "Gemini"]
    principles: List[str]     # Rules/patterns ["fail-safe", "SQL-first"]

    # ═══════════════════════════════════════════════════════════════
    # L2 NORMALIZED IDs (linked to lookup tables)
    # ═══════════════════════════════════════════════════════════════
    concept_ids: List[str]    # ["concept:hybrid_durability", "concept:cost_protection"]
    entity_ids: List[str]     # ["entity:primitive_engine", "entity:bigquery"]
    principle_ids: List[str]  # ["principle:fail_safe", "principle:sql_first"]

    # ═══════════════════════════════════════════════════════════════
    # SPINE CONNECTION
    # ═══════════════════════════════════════════════════════════════
    spine_level: int = 4      # Always 4 (sentence level in spine hierarchy)
    spine_parent_id: str      # Parent entity in spine.entity_unified
    source_entity_id: str     # Direct link to source entity

    # ═══════════════════════════════════════════════════════════════
    # PROVENANCE (where it came from)
    # ═══════════════════════════════════════════════════════════════
    source_type: str          # document | conversation | email | system_event
    source_category: str      # docs/reference | docs/ops | chatgpt_web | etc.
    source_file_path: str     # Original file path
    source_file_name: str     # Original file name

    extraction_model: str     # "gemini-1.5-flash" | "gemini-2.5-flash-lite"
    extraction_confidence: float  # 0.0 - 1.0
    extraction_prompt_version: str
    run_id: str               # Extraction run ID

    # ═══════════════════════════════════════════════════════════════
    # RELATIONSHIPS
    # ═══════════════════════════════════════════════════════════════
    related_atoms: List[str]      # Related atom IDs
    parent_atom_id: str           # Parent atom (if hierarchical)
    child_atoms: List[str]        # Child atoms

    # Question-Answer relationships:
    answer_to_question_id: str    # If this atom answers a question
    verified_by_answer_id: str    # If this question was verified by answer
    inquiry_direction: str        # user_asks | assistant_asks
    answer_provider: str          # user_answers | assistant_answers

    # ═══════════════════════════════════════════════════════════════
    # QUALITY METRICS
    # ═══════════════════════════════════════════════════════════════
    completeness_score: float     # How complete (0.0-1.0)
    clarity_score: float          # How clear (0.0-1.0)
    importance_score: float       # How important (0.0-1.0)
    truth_formation_score: float  # Decision-making quality

    # ═══════════════════════════════════════════════════════════════
    # EMBEDDINGS
    # ═══════════════════════════════════════════════════════════════
    embedding_similarity: List[float]  # 3072-dimensional semantic vector

    # ═══════════════════════════════════════════════════════════════
    # TEMPORAL
    # ═══════════════════════════════════════════════════════════════
    created_at: datetime
    updated_at: datetime
    extracted_at: datetime
    ingestion_date: date

    # ═══════════════════════════════════════════════════════════════
    # METADATA
    # ═══════════════════════════════════════════════════════════════
    metadata: Dict[str, Any]      # Additional metadata
    semantic_group: str           # Group ID for similar atoms
```

### Classification Types

#### By Knowledge Type

| Type | Description | Example |
|------|-------------|---------|
| **statement** | Declares something true | "BigQuery charges $6.25 per TB scanned" |
| **question** | Asks something | "How should errors be handled in pipelines?" |

#### By Statement Type

| Type | What It Is | Example |
|------|------------|---------|
| **fact** | Objective truth | "The project ID is flash-clover-464719-g1" |
| **decision** | Choice that was made | "We chose JSONL over SQLite for local storage" |
| **definition** | What something means | "A knowledge atom is a complete unit of truth" |
| **rule** | Must/should constraint | "All scripts must use get_bigquery_client()" |
| **procedure** | How to do something | "Run `--dry-run` first, then execute" |
| **principle** | Guiding philosophy | "Write local always, sync to cloud selectively" |
| **pattern** | Recurring structure | "The adapter pattern enables universal extraction" |
| **answer** | Response to question | "The cost was $1,493 from three incidents" |
| **reflection** | Meta-observation | "This pattern keeps appearing across pipelines" |

#### By Layer (Three-Layer Test)

| Layer | Question Answered | Example |
|-------|-------------------|---------|
| **theory** | WHY | "Hybrid durability prevents data loss because local storage can't fail" |
| **spec** | WHAT | "Scripts must use SessionCostLimiter with max_cost_usd=5.0" |
| **reference** | HOW | "Run: `python scripts/knowledge/normalize_l2.py`" |

---

## Extraction Pipeline

### The Extraction Prompt

The system uses a comprehensive prompt that instructs Gemini Flash to extract atoms with specific characteristics:

```
KNOWLEDGE ATOM DEFINITION:
A knowledge atom is a complete, bounded unit of knowledge that represents
ONE single whole thing. It may contain:
- A SINGLE TRUTH: One complete truth expressed in one or more sentences
- MULTIPLE TRUTHS COMBINED: When multiple truths together create a profound,
  meaningful whole - the COMBINATION itself becomes the atomic unit

BOUNDARY DETECTION:
- Having LESS than that whole renders it INCOMPLETE
- Having MORE than that whole renders it BEYOND ITS BOUNDARY

EXTRACTION TARGETS:
- ENTITIES: Tools, platforms, systems, libraries, people, organizations
- CONCEPTS: Abstract ideas, patterns, themes, domains (2-4 per atom)
- PRINCIPLES: Rules, patterns, best practices (0-2 per atom)
- TERMS: Technical vocabulary, keywords (3-5 per atom)
```

### Extraction Flow

```
┌───────────────────────────────────────────────────────────────────────────┐
│                         EXTRACTION PIPELINE                                │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  1. SOURCE IDENTIFICATION                                                  │
│     ┌──────────────────────────────────────────────────────────────┐      │
│     │ Document/Conversation/Email/Event arrives                     │      │
│     │ System determines source_type and creates document_run record │      │
│     │ Status: PENDING                                               │      │
│     └──────────────────────────────────────────────────────────────┘      │
│                              │                                             │
│                              ▼                                             │
│  2. ADAPTER SELECTION                                                      │
│     ┌──────────────────────────────────────────────────────────────┐      │
│     │ AdapterRegistry.get_adapter(source)                          │      │
│     │ Returns: TextAdapter | JSONAdapter | EventAdapter | Generic  │      │
│     └──────────────────────────────────────────────────────────────┘      │
│                              │                                             │
│                              ▼                                             │
│  3. SHAPE TO UNIFIED FORMAT                                                │
│     ┌──────────────────────────────────────────────────────────────┐      │
│     │ adapter.adapt(source, context) → LLMReviewableContent        │      │
│     │ Any shape is fine - just needs to be LLM-understandable      │      │
│     └──────────────────────────────────────────────────────────────┘      │
│                              │                                             │
│                              ▼                                             │
│  4. LLM EXTRACTION (Uniform)                                               │
│     ┌──────────────────────────────────────────────────────────────┐      │
│     │ UnificationLayer.unify_to_atoms(reviewable_content)          │      │
│     │ Single Gemini Flash call with extraction prompt              │      │
│     │ Returns: List[KnowledgeAtom] (uniform shape)                 │      │
│     └──────────────────────────────────────────────────────────────┘      │
│                              │                                             │
│                              ▼                                             │
│  5. LOCAL STORAGE (Always)                                                 │
│     ┌──────────────────────────────────────────────────────────────┐      │
│     │ LocalAtomStore.write_atoms(atoms)                            │      │
│     │ Writes to: ~/.primitive_engine/knowledge_atoms/YYYY-MM/*.jsonl   │      │
│     │ This NEVER fails (filesystem is reliable)                    │      │
│     └──────────────────────────────────────────────────────────────┘      │
│                              │                                             │
│                              ▼                                             │
│  6. BIGQUERY STORAGE (Queryable)                                           │
│     ┌──────────────────────────────────────────────────────────────┐      │
│     │ BigQuery.insert_rows_json(knowledge_atoms table, atoms)      │      │
│     │ document_run status updated to: COMPLETED                    │      │
│     └──────────────────────────────────────────────────────────────┘      │
│                              │                                             │
│                              ▼                                             │
│  7. MARK SYNCED                                                            │
│     ┌──────────────────────────────────────────────────────────────┐      │
│     │ LocalAtomStore.mark_synced(atom_ids)                         │      │
│     │ Updates .atom_sync_state.json with synced IDs                │      │
│     └──────────────────────────────────────────────────────────────┘      │
│                              │                                             │
│                              ▼                                             │
│  8. L2 NORMALIZATION (Batch)                                               │
│     ┌──────────────────────────────────────────────────────────────┐      │
│     │ normalize_l2_concepts_entities_principles.py                 │      │
│     │ Links raw strings to normalized IDs in lookup tables         │      │
│     │ concepts → concept_ids, entities → entity_ids, etc.          │      │
│     └──────────────────────────────────────────────────────────────┘      │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Storage Architecture

### Hybrid Durability Pattern

**Truth Engine Standard**: "Write local always, sync to cloud selectively."

```
Human <─── Local (JSONL) <───> Cloud (BigQuery)
           (always)           (selective)
```

| Layer | Reliability | Purpose |
|-------|-------------|---------|
| **Local JSONL** | Never fails (filesystem) | Ensure no data loss |
| **BigQuery** | May fail (network, quota) | Enable queries at scale |

### Local Storage Structure

```
~/.primitive_engine/knowledge_atoms/
├── 2025-12/
│   ├── atoms_2025-12-28.jsonl
│   ├── atoms_2025-12-29.jsonl
│   └── atoms_2025-12-30.jsonl
├── 2025-11/
│   ├── atoms_2025-11-26.jsonl
│   └── atoms_2025-11-27.jsonl
└── .atom_sync_state.json      ← Tracks which atoms synced to BigQuery
```

### Sync State Tracking

Per `JSONL_TO_BIGQUERY_PATTERN.md`:
- JSONL files are **append-only** (never modified)
- Sync state tracked in separate `.atom_sync_state.json` file
- Contains list of atom_ids that have been synced to BigQuery

```json
{
  "synced_ids": ["atom:abc123:1", "atom:abc123:2", ...],
  "updated_at": "2025-12-30T09:00:00Z"
}
```

### Recovery Flow

If BigQuery fails, recover from local:

```python
# Get atoms that haven't been synced
unsynced = local_store.get_unsynced_atoms(limit=1000)

# Retry sync to BigQuery
for atom in unsynced:
    service.store_atoms([atom])
```

---

## L2 Normalization

### The Problem

Raw concept/entity/principle strings have variations:

```
Atom 1: concepts = ["Hybrid Durability", "cost protection"]
Atom 2: concepts = ["hybrid durability", "Cost Protection"]
Atom 3: concepts = ["HYBRID_DURABILITY", "COST_PROTECTION"]
```

These are the same concepts but with different casing/formatting.

### The Solution

Normalize to lookup tables with canonical IDs:

```
Raw concepts:
  ["Hybrid Durability", "hybrid durability", "HYBRID_DURABILITY"]
           ↓
Normalized:
  concept_ids = ["concept:hybrid_durability"]
           ↓
Linked to:
  knowledge_concepts table (concept_id, concept_name, created_at)
```

### L2 Lookup Tables

| Table | Purpose | Records |
|-------|---------|---------|
| `knowledge_concepts` | Deduplicated concept names | 5,769 |
| `knowledge_entities` | Named entities | 165 |
| `knowledge_principles` | Rules, patterns, best practices | 2,647 |

### Normalization Script

```bash
python scripts/knowledge/normalize_l2_concepts_entities_principles.py
```

This script:
1. Inserts new concepts/entities/principles into lookup tables
2. Updates atoms with normalized IDs (concept_ids, entity_ids, principle_ids)
3. Uses SQL MERGE pattern for efficiency

---

## Service API

### Getting the Service

```python
from architect_central_services.knowledge_service import (
    KnowledgeAtomService,
    get_knowledge_atom_service,
    get_local_atom_store,
)

# Singleton access
service = get_knowledge_atom_service()
local_store = get_local_atom_store()
```

### Extraction Methods

| Method | Input | Use Case |
|--------|-------|----------|
| `extract_from_document()` | File path | Markdown, text files |
| `extract_from_conversation()` | Conversation ID | ChatGPT/Claude conversations |
| `extract_from_any_source()` | Any data | Universal (uses adapters) |
| `extract_from_audit_trail()` | Audit events | System events |
| `extract_from_central_service_event()` | Service events | Operations |
| `extract_from_negative_indicators()` | Errors | Failure learning |

### Example: Extract from Document

```python
from architect_central_services.knowledge_service import get_knowledge_atom_service

service = get_knowledge_atom_service()

# Extract and auto-store
result = service.extract_from_document(
    file_path="/path/to/document.md",
    source_type="document",
)

print(f"Extracted {len(result.atoms)} atoms")
for atom in result.atoms[:3]:
    print(f"  - {atom.content[:80]}...")
```

### Example: Extract from Any Source

```python
# Works with any data type
data = {
    "event": "pipeline_completed",
    "pipeline": "chatgpt_web",
    "stage": 16,
    "atoms_created": 1500,
}

result = service.extract_from_any_source(
    source=data,
    source_type="system_event",
    source_id="event:pipeline:123",
)
```

### Example: Store Atoms Manually

```python
from architect_central_services.knowledge_service.models import KnowledgeAtom

atom = KnowledgeAtom(
    atom_id="atom:manual:1",
    parent_id="doc:manual",
    content="This is a manually created knowledge atom.",
    knowledge_type="statement",
    statement_type="fact",
)

stored_ids = service.store_atoms([atom])
```

---

## BigQuery Schema

### Tables

| Table | Purpose |
|-------|---------|
| `knowledge_atoms.document_runs` | Tracks extraction runs per document |
| `knowledge_atoms.knowledge_atoms` | The atomic knowledge units |
| `knowledge_atoms.knowledge_concepts` | L2 concept lookup |
| `knowledge_atoms.knowledge_entities` | L2 entity lookup |
| `knowledge_atoms.knowledge_principles` | L2 principle lookup |
| `knowledge_atoms.improvement_atoms` | Suggested improvements |

### Key Queries

#### Find Atoms by Concept

```sql
SELECT atom_id, content, concepts
FROM `knowledge_atoms.knowledge_atoms`
WHERE 'cost protection' IN UNNEST(concepts)
ORDER BY created_at DESC
LIMIT 10
```

#### Find Atoms by Entity

```sql
SELECT atom_id, content, entities
FROM `knowledge_atoms.knowledge_atoms`
WHERE 'BigQuery' IN UNNEST(entities)
```

#### Find Rules/Specs

```sql
SELECT atom_id, content, atom_layer
FROM `knowledge_atoms.knowledge_atoms`
WHERE statement_type = 'rule'
  AND atom_layer = 'spec'
```

#### Check Normalization Status

```sql
SELECT
    COUNTIF(ARRAY_LENGTH(concept_ids) > 0) as normalized,
    COUNTIF(ARRAY_LENGTH(concept_ids) = 0 AND ARRAY_LENGTH(concepts) > 0) as needs_normalization
FROM `knowledge_atoms.knowledge_atoms`
```

---

## Truth Engine Standards Alignment

| Standard | Implementation |
|----------|----------------|
| **exist-now** | `generate_knowledge_atom_id()` - gives atoms identity |
| **see/hold** | `get_logger()` with full traceability |
| **hold** | Hybrid Durability - BigQuery + Local JSONL |
| **move** | `source_entity_id`, `spine_parent_id` for lineage |
| **the furnace** | `@harden_service_method`, cost protection |
| **three-layer test** | `atom_layer` field (theory/spec/reference) |

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `assess_knowledge_system_readiness.py` | Full system health check (score out of 100) |
| `normalize_l2_concepts_entities_principles.py` | Link atoms to normalized L2 IDs |
| `process_documents_to_atoms.py` | Batch extract atoms from documents |
| `deduplicate_knowledge_atoms.py` | Remove duplicate atoms |
| `generate_knowledge_atom_embeddings.py` | Create semantic embeddings |
| `assess_atom_quality.py` | Evaluate atom quality |
| `assess_atom_completeness.py` | Check atom completeness |
| `daily_knowledge_processing_job.py` | Daily batch processing |

### Running Assessment

```bash
python scripts/knowledge/assess_knowledge_system_readiness.py
```

Output:
```
======================================================================
KNOWLEDGE ATOMS SYSTEM READINESS ASSESSMENT
======================================================================

1. Checking table existence... ✅ All tables exist
2. Checking table schemas... ✅ All required fields present
3. Checking data state... 📊 20,616 atoms
4. Checking pipeline health... ⚠️ 9,878 atoms not normalized
5. Checking integrations... ✅ 3/4 enabled

Readiness Score: 70/100
Status: MOSTLY READY (minor issues)
```

---

## Key Files

| File | Location | Purpose |
|------|----------|---------|
| `models.py` | `knowledge_service/` | KnowledgeAtom dataclass |
| `service.py` | `knowledge_service/` | Main service class |
| `local_store.py` | `knowledge_service/` | Hybrid Durability local storage |
| `adapters.py` | `knowledge_service/` | Universal source adapters |
| `unified_shape.py` | `knowledge_service/` | Intermediate format for extraction |
| `__init__.py` | `knowledge_service/` | Public API exports |

---

## The Recursive Pattern

```
Documents → Knowledge Atoms → Insights → New Documents
                ↓                              ↓
            BigQuery ◄─────────────────────────┘
```

Knowledge atoms are both **input** (extracted from sources) and **output** (generate new understanding). The system feeds itself - atoms extracted today become the foundation for tomorrow's insights.

---

**The atom is the primitive. Everything else is built on atoms.**
