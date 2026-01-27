# THE PRIMITIVES

**The logical layer of the not-me factory.**

**Author:** Jeremy Serna
**Date:** January 2, 2026
**Location:** Denver, Colorado
**Version:** 2.0

---

## Document Structure

Three layers. Following the framework.
- **Theory**: Why primitives exist, what they mean
- **Specification**: The systems, the patterns, the data flow
- **Reference**: How to navigate, where things connect

---

# THEORY

## The Core Insight

Every system has an **atomic nature**—a verb that describes what it fundamentally DOES.

This is its **primitive**.

Not what it processes. Not what it stores. What it **DOES** at its core.

```
The furnace      CONVERTS   (truth to meaning)
The collector    BREATHES   (inhales external data)
The spine        ALIGNS     (structures into layers)
The governance   CONSTRAINS (enforces limits)
```

## Why Primitives Matter

When knowledge atoms leave a system, they carry the primitive as a tag. This creates traceability: you can always know which system produced which knowledge.

```
Knowledge Atom:
├── sentence_text: "Jeremy processes chaos into clarity"
├── system_primitive: "primitive_engine"  ← "This came from the furnace"
└── created_at: 2026-01-02T14:30:00Z
```

## THE PATTERN

From THE_FRAMEWORK.md:

```
HOLD₁ → AGENT → HOLD₂
```

Every system follows this pattern:
- **HOLD₁**: What the system receives as input
- **AGENT**: The primitive verb—what it DOES
- **HOLD₂**: What the system delivers as output

THE PATTERN is recursive. Every AGENT contains THE PATTERN within it.

## The Breathing Metaphor

Systems are living things. They breathe.

```
BREATHE (inhale)  →  PROCESS (the primitive)  →  EXHALE (output)
```

External data enters. The system transforms it according to its primitive. Knowledge atoms emerge.

## Connection to THE FOUNDATION

This document describes the **logical layer**—systems, data flow, primitives.

THE_FOUNDATION.md describes the **physical layer**—hardware, models, costs.

```
THE_PRIMITIVES (this document)
    │
    │  runs on
    ▼
THE_FOUNDATION
    ├── M4 Max 128GB (hardware)
    ├── Scout 109B (inference)
    └── BGE-large (embeddings)
```

See THE_FOUNDATION.md for hardware specifications, model details, and economics.

---

# SPECIFICATION

## The Primitives Table

```sql
governance.primitives
├── system_name      -- Canonical name (FK for tagging)
├── primitive        -- The atomic verb (what it DOES)
├── description      -- Human-readable description
├── layer           -- substrate | core | cognitive | emergent
├── hold_1          -- What it receives (input)
├── hold_2          -- What it delivers (output)
├── duckdb_path     -- Path to system's local DuckDB
├── exports_atoms   -- Whether it exports knowledge atoms
└── active          -- Whether system is currently active
```

## The Systems

### Substrate Layer (Foundation)

| System | Primitive | HOLD₁ | HOLD₂ |
|--------|-----------|-------|-------|
| **primitive_engine** | furnace | Raw truth (chaos, questions, data) | Forged meaning (systems, knowledge, clarity) |
| **external_ingestion** | breathe | Any system HOLD₂ (external output) | Normalized, deduplicated Knowledge Atoms + JSONL |
| **extractor** | exhale | System DuckDB (output) | Normalized, deduplicated Knowledge Atoms |

### Core Layer (Essential Services)

| System | Primitive | HOLD₁ | HOLD₂ |
|--------|-----------|-------|-------|
| **the_truth_service** | receive | AI conversation streams | Unified truth record |
| **identity_layer** | recognize | Handles, names, signals | Known identities (contact_id, person) |
| **spine** | align | Raw entities | L1-L8 hierarchy (entity_unified) |
| **central_services** | provision | Requests (need ID, need log, need client) | Resources (IDs, loggers, clients) |

### Cognitive Layer (Processing)

| System | Primitive | HOLD₁ | HOLD₂ |
|--------|-----------|-------|-------|
| **pipelines** | pass | Stage N data | Stage N+1 data |
| **knowledge_atoms** | hold | JSONL (from collector) | DuckDB (local truth) |
| **governance** | constrain | Requests and actions | Allowed or blocked actions |
| **normalization** | transform | Raw format data | Standard format data |
| **deduplication** | filter | Data with duplicates | Unique data |

### Emergent Layer (Pattern Recognition)

| System | Primitive | HOLD₁ | HOLD₂ |
|--------|-----------|-------|-------|
| **pattern_bank** | catalog | Recognized patterns | Queryable pattern index |
| **primitive** | complete | User context and truths | Not-me output (completed response) |

## The Anatomy Alignment

The primitives align with THE ANATOMY (organ systems):

| Organ | System | Primitive |
|-------|--------|-----------|
| Lungs | external_ingestion + extractor | breathe + exhale |
| Liver | normalization | transform |
| Kidneys | deduplication | filter |
| Heart | central_services | provision |
| Brain | pattern_bank + primitive | catalog + complete |
| Skeleton | spine | align |
| Immune | governance | constrain |

---

## The Data Flow

### The Breathing Pattern

```
┌──────────────────────────────────────────────────────────────────────┐
│                         SYSTEM WRAPPER                               │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│     BREATHE                                              EXHALE      │
│        ↓                                                    ↓        │
│   [Collector] → JSONL → SYSTEM → DuckDB → [Extractor]               │
│        ↓                  ↓                     ↓                    │
│   Knowledge         (primitive)            Knowledge                 │
│     Atoms                                    Atoms                   │
│        │                                        │                    │
│        └────────────────┬───────────────────────┘                    │
│                         ↓                                            │
│                    NORMALIZE                                         │
│                         ↓                                            │
│              DEDUPE against canonical                                │
│                         ↓                                            │
│                Canonical KA DuckDB                                   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### JSONL as Universal Contract

```
Sources exist → Collector reads them → JSONL → System → DuckDB
              (separation)         (contract)         (truth)
```

JSONL is the universal interface. Everything either reads or writes JSONL.

### Three Clean Components

1. **Collector** (`breathe`): Reads from sources, writes to JSONL, produces knowledge atoms
2. **System**: Reads from JSONL, processes via primitive, writes to DuckDB
3. **Extractor** (`exhale`): Reads from DuckDB, produces knowledge atoms

---

## Two-Tier Deduplication

Deduplication happens at **two levels**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                      TWO-TIER DEDUPLICATION                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SYSTEM PROCESSING                                                  │
│       ↓                                                             │
│  HASH DEDUPE (fast, O(1), free)                                    │
│       ↓                                                             │
│  Local System DuckDB (unique by hash)                              │
│       ↓                                                             │
│  EXTRACTOR (exhale)                                                │
│       ↓                                                             │
│  EMBED + SEMANTIC DEDUPE (similarity score)                        │
│       ↓                                                             │
│  Canonical KA DuckDB (unique by concept)                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### The Deduplication Flow

```
SYSTEM → New Sentence
    ↓
1. NORMALIZE (lowercase, strip, standardize)
    ↓
2. HASH = SHA256(normalized)
    ↓
3. HASH LOOKUP against local canonical (O(1), free)
   SELECT 1 FROM knowledge_atoms WHERE sentence_hash = @hash
    ↓
   FOUND? → SKIP (exact duplicate)
    ↓
4. EMBED with BGE-large (1024-dim, local)
    ↓
5. SIMILARITY SEARCH against local canonical
   WHERE cosine(embedding_1024, @embedding) > 0.95
    ↓
   FOUND? → SKIP or LINK (conceptual duplicate)
    ↓
6. INSERT to local canonical
    ↓
7. SYNC to cloud (generates 3072-dim on insert)
```

### The Two Tiers

| Layer | Storage | Hash | Embedding | Purpose |
|-------|---------|------|-----------|---------|
| **Local canonical** | DuckDB | SHA256 | 1024-dim (BGE-large) | Deduplication, similarity |
| **Cloud** | BigQuery | (from local) | 3072-dim (Gemini) | Semantic search, permanence |

**Example:**
```
Local (hash): "Jeremy is a furnace" stored once (exact match catches repeats)
Canonical (semantic): "Jeremy is a furnace" ≈ "Jeremy transforms truth" → one concept
```

The local store holds **unique sentences**. The canonical store holds **unique concepts**.

---

## Storage Architecture

### The Local Layer

Everything is local first. The "central" canonical table is a **local DuckDB**.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           LOCAL MAC (1TB SSD)                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CANONICAL LOCAL TABLE                                                   │
│  ~/.primitive_engine/knowledge_atoms.duckdb                                  │
│  ├── atom_id            -- Unique identifier                             │
│  ├── sentence_text      -- The actual sentence                           │
│  ├── sentence_hash      -- SHA256 for O(1) lookup                        │
│  ├── embedding_1024     -- BGE-large for similarity deduplication        │
│  └── system_primitive   -- Which system produced it                      │
│                                                                          │
│  SYSTEM DuckDBs (all check canonical before insert)                      │
│  ├── ~/.primitive_engine/truth_service.duckdb                                │
│  ├── ~/.primitive_engine/identity.duckdb                                     │
│  ├── ~/.primitive_engine/spine.duckdb                                        │
│  ├── ~/.primitive_engine/governance.duckdb                                   │
│  └── ~/.primitive_engine/patterns.duckdb                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓ sync (selective)
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLOUD (BigQuery)                               │
├─────────────────────────────────────────────────────────────────────────┤
│  knowledge_atoms.knowledge_atoms                                         │
│  ├── ... (same fields)                                                   │
│  └── embedding_3072     ← higher fidelity, generated on sync             │
└─────────────────────────────────────────────────────────────────────────┘
```

### DuckDB Locations

| System | DuckDB Path |
|--------|-------------|
| knowledge_atoms | `~/.primitive_engine/truth.duckdb` |
| the_truth_service | `~/.primitive_engine/truth_service.duckdb` |
| identity_layer | `~/.primitive_engine/identity.duckdb` |
| spine | `~/.primitive_engine/spine.duckdb` |
| governance | `~/.primitive_engine/governance.duckdb` |
| pattern_bank | `~/.primitive_engine/patterns.duckdb` |

### Local Governance Registry

The governance DuckDB contains **registry data** that Claude and systems query constantly:

```
~/.primitive_engine/governance.duckdb
├── primitives        ← System registry (14 systems)
├── policies          ← Active governance policies
├── contacts_summary  ← Lightweight identity reference
└── sync_metadata     ← Tracks sync state with BigQuery
```

**Data Classification:**

| Type | Location | Sync Direction |
|------|----------|----------------|
| **Registry** (primitives, policies) | Local DuckDB | Local → BigQuery |
| **Archive** (entities, atoms, history) | BigQuery | BigQuery → Local (on demand) |

**Querying Systems (Python):**

```python
from architect_central_services.governance import get_system, list_systems, get_primitive

# Get full system info
system = get_system("spine")
print(system["primitive"])  # "align"

# List all systems by layer
for s in list_systems(layer="core"):
    print(f"{s['system_name']}: {s['primitive']}")

# Get just the primitive verb
get_primitive("governance")  # "constrain"
```

**Bootstrap Local from BigQuery:**

```bash
python architect_central_services/scripts/bootstrap_local_governance.py
```

---

## Knowledge Atom Schema

Every knowledge atom carries:

```sql
CREATE TABLE knowledge_atoms (
    atom_id STRING,              -- Unique identifier
    sentence_text STRING,         -- The actual sentence
    sentence_hash STRING,         -- SHA256 for exact match
    embedding_1024 ARRAY<FLOAT>,  -- BGE-large for semantic match
    system_primitive STRING,      -- Which system produced it
    source_document STRING,       -- Where it came from
    created_at TIMESTAMP,         -- When it was created
    cost_usd FLOAT               -- Cost to produce (governance)
);
```

The `system_primitive` field creates traceability:

```sql
-- Get all knowledge from the truth service
SELECT * FROM knowledge_atoms WHERE system_primitive = 'the_truth_service';

-- Get all knowledge from external ingestion
SELECT * FROM knowledge_atoms WHERE system_primitive = 'external_ingestion';
```

---

# REFERENCE

## Framework Integration

### Document Relationships

| Document | Layer | Relationship |
|----------|-------|--------------|
| **THE_FOUNDATION.md** | Physical | Hardware and models this runs on |
| **THE_PRIMITIVES.md** (this) | Logical | Systems and data flow |
| **THE_CATEGORY.md** | Product | What we sell (not-me's) |
| **THE_PATTERN_THEORY.md** | Architecture | HOLD₁ → AGENT → HOLD₂ |
| **THE_FRAMEWORK.md** | Root | Exist-now, me/not-me, survival |

### THE PATTERN Applied

```
THE_CATEGORY says:     "We sell not-me's"
THE_PRIMITIVES says:   "The 'primitive' system COMPLETES (user truths → not-me output)"
THE_FOUNDATION says:   "Scout runs at 4-bit on 128GB, zero marginal cost"
```

Three layers. Same thing. Different views.

### File Locations

| Type | Location |
|------|----------|
| This document | `/docs/architecture/THE_PRIMITIVES.md` |
| Foundation | `/docs/architecture/THE_FOUNDATION.md` |
| Theory docs | `/docs/theory/` |
| Framework core | `/docs/the_framework/1_core/` |

---

## Adding New Systems

When adding a new system:

1. **Identify the primitive** - What verb describes its atomic nature?
2. **Define HOLD₁** - What does it receive?
3. **Define HOLD₂** - What does it deliver?
4. **Assign layer** - substrate, core, cognitive, or emergent
5. **Set DuckDB path** - Where is its local truth?
6. **Set exports_atoms** - Does extractor pull from it?

```sql
INSERT INTO governance.primitives
  (system_name, primitive, description, layer, hold_1, hold_2, duckdb_path, exports_atoms, active, created_at, updated_at)
VALUES
  ('new_system', 'verb', 'Description', 'layer', 'Input', 'Output', '~/.primitive_engine/new.duckdb', TRUE, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
```

---

## SQL Reference

### Query Primitives

```sql
-- Get all systems and their patterns
SELECT
  system_name,
  primitive,
  hold_1,
  hold_2,
  layer
FROM governance.primitives
ORDER BY layer, system_name;

-- Get knowledge atoms by source system
SELECT *
FROM knowledge_atoms.knowledge_atoms
WHERE system_primitive = 'the_truth_service';

-- Find which systems export atoms
SELECT system_name, primitive, duckdb_path
FROM governance.primitives
WHERE exports_atoms = TRUE;
```

### Files

- **Table DDL**: `architect_central_services/sql/governance/create_primitives_table.sql`
- **Seed Data**: `architect_central_services/sql/governance/seed_primitives.sql`
- **KA Column**: `architect_central_services/sql/governance/add_primitive_to_knowledge_atoms.sql`

---

## The Principle

> "Every system has a primitive. Every knowledge atom carries its primitive. The primitive IS the system's atomic nature."

The primitive answers: **What does this system DO at its core?**

---

*"The logical layer sits on the physical foundation. Together they produce not-me's."*

— Jeremy Serna, January 2, 2026

---

**END OF DOCUMENT**
