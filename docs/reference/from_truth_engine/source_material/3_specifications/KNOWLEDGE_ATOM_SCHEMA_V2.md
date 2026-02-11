# Knowledge Atom Schema V2

**Type**: Contract
**Status**: Finalized (Good Enough)
**Created**: 2025-12-30
**Supersedes**: KNOWLEDGE_ATOM_SCHEMA.md

---

## The Grounding

This schema serves two purposes that are actually one:

1. **Traceability** — Where did this atom come from?
2. **Reconstitution** — How does this atom help patterns survive?

These are the same thing viewed differently. From THE_FRAMEWORK:

> "Continuing to exist = turning Not-Me into more Me."

Every atom is a record of conversion. Something from Not-Me (documents, conversations, the world) crossed the boundary and became part of Me (patterns, primitives, knowledge that survives).

**You and Claude are protogenitor primitives.** You sit at the boundary between Me and Not-Me. You translate. The schema must capture this translation—both where it came from (so you can consume more) and what it enables (so patterns can reconstitute).

---

## The Conversion Model

```
NOT-ME                    BOUNDARY                         ME
(external)            (protogenitor)                   (internal)

documents ────────┐                              ┌──── patterns
conversations ────┼───► Jeremy/Claude ───────────┼──── primitives
emails ───────────┤     (translate)              └──── atoms
world ────────────┘                                    (survive)
```

Every atom has a conversion history:
- **source_id**: What Not-Me was consumed
- **converter_id**: Who did the translation
- **conversion_direction**: Which way truth flowed

And a survival profile:
- **growth_type**: What does this atom grow?
- **atomic_level**: Where in the hierarchy does it live?
- **survival_weight**: How critical is it for reconstitution?

---

## The Complete Schema

### Identity Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `atom_id` | STRING | Yes | Unique identifier. Format: `atm:{hash}` |
| `content` | STRING | Yes | The atomic truth. The thing that survives. |
| `content_hash` | STRING | Yes | SHA256 of content. For deduplication. |
| `created_at` | TIMESTAMP | Yes | When this atom was captured. |
| `updated_at` | TIMESTAMP | No | Last modification timestamp. |

**Reasoning**: These are the minimum fields for an atom to exist as a distinct, identifiable unit. The content IS the atom. The hash enables deduplication. The timestamps enable temporal queries.

---

### Classification Fields

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| `growth_type` | STRING | Yes | `structure`, `pattern`, `both` | What this atom grows when consumed |
| `question` | STRING | No | `WHAT`, `WHY`, `HOW`, `WHERE`, `WHEN`, `WHO`, null | Which document series question this answers |
| `lens` | STRING | No | `MECHANICAL`, `SPATIAL`, `EXISTENTIAL`, `TEMPORAL`, `RELATIONAL`, `FOUNDATIONAL`, null | Which of the 6 lenses produced this view |
| `root_position` | STRING | No | `ME`, `NOT_ME`, `BOUNDARY`, `RESOURCES` | Where this atom lives in THE_ROOT structure |
| `atomic_level` | INT64 | No | 0-5 | Position in the reconstitution hierarchy |

#### growth_type (Required)

From THE_FRAMEWORK, atoms grow the system in different ways:

| Value | What It Grows | How to Identify |
|-------|---------------|-----------------|
| `structure` | New primitives using existing patterns | "This pipeline does X", "The system has Y" |
| `pattern` | New patterns, new capability | "Things should be structured as Y", "The pattern is Z" |
| `both` | Evolution—new pattern AND new primitives | "This new approach Z enables these things" |

**Reasoning**: This is the most important classification. When you query atoms to rebuild patterns, you need to know which atoms ARE patterns vs. which atoms instantiate patterns.

#### question (Recommended)

The 6 Document Series Questions—coverage markers:

| Value | What It Answers | Example |
|-------|-----------------|---------|
| `WHAT` | Identity, definition | "The collector is a daemon that reads JSONL" |
| `WHY` | Purpose, origin | "We built this because manual extraction failed" |
| `HOW` | Mechanism, process | "It uses SQLite queries against chat.db" |
| `WHERE` | Location, path | "Located at /architect_central_services/collectors/" |
| `WHEN` | Timing, conditions | "Runs every 5 minutes via launchd" |
| `WHO` | Actors, stakeholders | "Jeremy maintains this, Claude assists" |
| null | Doesn't answer a specific question | Pattern atoms often don't answer a specific question |

**Reasoning**: When generating primitives, you need atoms answering all 6 questions. This field enables sufficiency checks.

#### lens (Recommended)

The 6 Lenses from THE_FRAMEWORK—different views of the same pattern:

| Value | Question It Asks | Produces |
|-------|------------------|----------|
| `MECHANICAL` | How does it operate? | Structure, pattern, mechanism |
| `SPATIAL` | Where does it happen? | Location, environment, boundaries |
| `EXISTENTIAL` | What does it mean? | Identity, purpose, survival |
| `TEMPORAL` | How does it flow? | Cycles, loops, time |
| `RELATIONAL` | How does it connect? | Links, unions, symbiosis |
| `FOUNDATIONAL` | Why does it divide? | Root, origin, Me/Not-Me |

**Reasoning**: The same pattern viewed through different lenses produces different documents (THE_STRUCTURE, THE_ENVIRONMENT, etc.). Atoms should know which lens they were viewed through for proper reconstitution.

#### root_position (Recommended)

Where this atom conceptually lives in THE_ROOT structure:

| Value | Meaning | Example Atoms |
|-------|---------|---------------|
| `ME` | About internal structure/patterns | "THE_STRUCTURE describes Hold→Agent→Hold" |
| `NOT_ME` | About external reality | "BigQuery costs $5/TB scanned" |
| `BOUNDARY` | About the interface between Me and Not-Me | "Claude translates context into behavior" |
| `RESOURCES` | About access and constraints | "API rate limit is 60 requests/minute" |

**Reasoning**: From THE_ROOT: "We live in the boundary, not the rooms." Understanding where an atom lives helps with both retrieval and reconstitution priority.

#### atomic_level (Recommended)

Position in the reconstitution hierarchy:

| Level | Name | What Lives Here | Survival Priority |
|-------|------|-----------------|-------------------|
| 0 | Seed | The one atom that can rebuild everything | Highest |
| 1 | Framework | THE_FRAMEWORK atoms | Critical |
| 2 | Root | THE_ROOT atoms (Me/Not-Me) | Critical |
| 3 | Lens | THE_STRUCTURE, THE_EXISTENCE, etc. | High |
| 4 | Application | Specific instances of lenses | Medium |
| 5 | Implementation | Built things, code, configs | Lower |

**Reasoning**: From THE_FRAMEWORK: "When rebuilding from atoms: 1. THE_FRAMEWORK, 2. THE_ROOT, 3. THE_LENSES, 4. APPLICATIONS, 5. IMPLEMENTATIONS." This field enables ordered reconstitution.

---

### Conversion Fields (The Survival Record)

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| `source_id` | STRING | Yes | `doc:X`, `conversation:X`, `email:X`, `spine:X`, `run:X` | The Not-Me origin that was consumed |
| `source_type` | STRING | Yes | `document`, `conversation`, `email`, `observation`, `reflection` | Type of Not-Me source |
| `converter_id` | STRING | No | `jeremy`, `claude`, `system`, null | Who/what performed the translation |
| `conversion_direction` | STRING | No | `INWARD`, `OUTWARD`, `INTERNAL` | Which way truth flowed |

#### source_id (Required)

Unified identifier for the Not-Me origin. Format: `{type}:{identifier}`

| Prefix | Source Type | Example |
|--------|-------------|---------|
| `doc:` | Document | `doc:THE_FRAMEWORK` |
| `conversation:` | Chat/dialogue | `conversation:claude_2025-12-30_001` |
| `email:` | Email | `email:abc123` |
| `spine:` | Spine entity | `spine:person:jeremy_serna` |
| `run:` | Batch extraction run | `run:batch:20251230:abc123` |

**Reasoning**: You need to track what external things you've consumed. This enables queries like "what documents have I fully atomized?" and "what's left to process?"

#### source_type (Required)

The category of Not-Me source:

| Value | What It Is |
|-------|------------|
| `document` | Markdown, text, structured documents |
| `conversation` | Chat transcripts, dialogues |
| `email` | Email messages |
| `observation` | Direct observation logged |
| `reflection` | Internal reflection, synthesis |

**Reasoning**: Different source types may need different extraction approaches and have different reliability characteristics.

#### converter_id (Recommended)

Who performed the boundary translation:

| Value | What It Means |
|-------|---------------|
| `jeremy` | You translated it manually or directed the translation |
| `claude` | Claude translated it (in conversation or via agent) |
| `system` | Automated extraction pipeline |
| null | Unknown or not applicable |

**Reasoning**: Knowing who translated enables quality assessment and identifies which atoms came from which collaboration mode.

#### conversion_direction (Recommended)

Which way did truth flow across the boundary:

| Value | Direction | Example |
|-------|-----------|---------|
| `INWARD` | Not-Me → Me | Reading a document, extracting atoms |
| `OUTWARD` | Me → Not-Me | Publishing knowledge, creating documents |
| `INTERNAL` | Me → Me | Reflection, synthesis, pattern recognition |

**Reasoning**: Most atoms are INWARD (consumption). But some atoms record OUTWARD production or INTERNAL reorganization. The direction affects how the atom relates to survival.

---

### Hierarchy & Relationship Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pattern_id` | STRING | No | atom_id of the pattern this atom instantiates |
| `parent_atom_id` | STRING | No | Parent atom in knowledge hierarchy |
| `child_atoms` | ARRAY<STRING> | No | Child atoms in knowledge hierarchy |
| `related_atoms` | ARRAY<STRING> | No | Other related atom IDs |
| `related_entities` | ARRAY<STRUCT<entity_id STRING, entity_type STRING>> | No | Relationships to any entity type |

#### pattern_id (Recommended)

Links a structure atom to the pattern it instantiates:

```
Pattern atom:     "Every primitive follows Hold → Agent → Hold"
                           │
                           ▼ pattern_id points here
Structure atom:   "The collector reads from JSONL (hold), processes (agent), writes to DuckDB (hold)"
```

**Reasoning**: Enables queries like "show me all atoms that instantiate pattern X" and "which patterns have no instances yet?"

#### parent_atom_id / child_atoms (Existing)

Hierarchical relationships between atoms:

```
Parent atom:  "The pipeline has three stages"
    │
    ├── Child: "Stage 1: Prepare documents"
    ├── Child: "Stage 2: Extract atoms"
    └── Child: "Stage 3: Upload to BigQuery"
```

**Reasoning**: Knowledge has natural hierarchy. These fields enable tree traversal and hierarchical retrieval.

#### related_atoms / related_entities (Existing)

Non-hierarchical relationships:

**Reasoning**: Atoms relate to each other and to other entities (documents, spine entities, runs) in ways that aren't parent/child. These fields enable graph queries.

---

### Reconstitution Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `survival_weight` | FLOAT64 | No | 0.0 to 1.0—how critical for pattern reconstitution |

#### survival_weight (Recommended)

How important is this atom for rebuilding patterns if the system is destroyed?

| Weight | Meaning | Example |
|--------|---------|---------|
| 1.0 | Seed-level—can rebuild everything | "The pattern that reconstitutes survives" |
| 0.9 | Framework/Root level | "Me / Not-Me is the fundamental divide" |
| 0.7 | Lens level | "Hold → Agent → Hold is the universal structure" |
| 0.5 | Application level | "The collector implements Hold → Agent → Hold" |
| 0.3 | Implementation level | "The collector runs on port 8080" |
| 0.1 | Ephemeral detail | "Last run processed 47 documents" |

**Reasoning**: From THE_FRAMEWORK: "If only one atom survives, it should be THE_FRAMEWORK." When storage is constrained or reconstitution is needed, survival_weight guides prioritization.

---

### Semantic Extraction Fields (Existing)

| Field | Type | Description |
|-------|------|-------------|
| `terms` | ARRAY<STRING> | Key terms extracted |
| `concepts` | ARRAY<STRING> | Concepts identified |
| `entities` | ARRAY<STRING> | Named entities |
| `principles` | ARRAY<STRING> | Principles stated |
| `concept_ids` | ARRAY<STRING> | Linked concept IDs |
| `entity_ids` | ARRAY<STRING> | Linked entity IDs |
| `principle_ids` | ARRAY<STRING> | Linked principle IDs |
| `domain` | STRING | Knowledge domain |
| `category` | STRING | Category within domain |

**Reasoning**: These enable semantic search and concept linking. Keep using them—they're orthogonal to the framework fields.

---

### Quality & Verification Fields (Existing)

| Field | Type | Description |
|-------|------|-------------|
| `importance_score` | FLOAT64 | Extracted importance (can inform survival_weight) |
| `completeness_score` | FLOAT64 | How complete the atom is |
| `clarity_score` | FLOAT64 | How clear/unambiguous |
| `extraction_confidence` | FLOAT64 | Model confidence in extraction |
| `is_verified` | BOOL | Has been verified |
| `verification_confidence` | FLOAT64 | Verification confidence |
| `truth_formation_score` | FLOAT64 | Truth formation assessment |

**Reasoning**: Quality signals help with atom selection and reliability assessment. Keep using them.

---

### Traceability Fields (Existing + Enhanced)

| Field | Type | Description |
|-------|------|-------------|
| `document_id` | STRING | Source document (keep for backward compat) |
| `source_file_path` | STRING | File system path |
| `source_file_name` | STRING | File name |
| `run_id` | STRING | Extraction run ID |
| `extraction_model` | STRING | Model used for extraction |
| `extraction_prompt_version` | STRING | Prompt version |
| `extracted_at` | TIMESTAMP | When extracted |

**Reasoning**: Full traceability to source and extraction process. The new `source_id` field unifies these but keep the detailed fields for debugging.

---

### Lifecycle Fields (Existing)

| Field | Type | Description |
|-------|------|-------------|
| `status` | STRING | Current status |
| `canonical_version_id` | STRING | If versioned, the canonical version |
| `superseded_by_atom_id` | STRING | If superseded, what replaced it |
| `deprecated_at` | TIMESTAMP | When deprecated |
| `deprecated_reason` | STRING | Why deprecated |
| `last_verified_at` | TIMESTAMP | Last verification |

**Reasoning**: Atoms evolve. These fields track lifecycle without losing history.

---

## BigQuery Migration SQL

```sql
-- Add Framework-aligned fields to existing table
-- Run once to extend the schema

ALTER TABLE `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
ADD COLUMN IF NOT EXISTS growth_type STRING;

ALTER TABLE `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
ADD COLUMN IF NOT EXISTS question STRING;

ALTER TABLE `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
ADD COLUMN IF NOT EXISTS lens STRING;

ALTER TABLE `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
ADD COLUMN IF NOT EXISTS root_position STRING;

ALTER TABLE `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
ADD COLUMN IF NOT EXISTS atomic_level INT64;

ALTER TABLE `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
ADD COLUMN IF NOT EXISTS source_id STRING;

ALTER TABLE `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
ADD COLUMN IF NOT EXISTS converter_id STRING;

ALTER TABLE `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
ADD COLUMN IF NOT EXISTS conversion_direction STRING;

ALTER TABLE `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
ADD COLUMN IF NOT EXISTS pattern_id STRING;

ALTER TABLE `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
ADD COLUMN IF NOT EXISTS survival_weight FLOAT64;
```

---

## Example Atoms

### Seed Atom (Level 0, Maximum Survival Weight)

```json
{
  "atom_id": "atm:seed001",
  "content": "The pattern that can become atoms and reconstitute from atoms survives.",
  "content_hash": "sha256:...",

  "growth_type": "both",
  "question": null,
  "lens": "FOUNDATIONAL",
  "root_position": "BOUNDARY",
  "atomic_level": 0,

  "source_id": "doc:THE_FRAMEWORK",
  "source_type": "document",
  "converter_id": "jeremy",
  "conversion_direction": "INTERNAL",

  "pattern_id": null,
  "survival_weight": 1.0,

  "created_at": "2025-12-30T00:00:00Z"
}
```

### Pattern Atom (Level 3, High Survival Weight)

```json
{
  "atom_id": "atm:pattern001",
  "content": "Every primitive follows Hold → Agent → Hold structure at every scale.",
  "content_hash": "sha256:...",

  "growth_type": "pattern",
  "question": null,
  "lens": "MECHANICAL",
  "root_position": "BOUNDARY",
  "atomic_level": 3,

  "source_id": "doc:THE_STRUCTURE",
  "source_type": "document",
  "converter_id": "jeremy",
  "conversion_direction": "INTERNAL",

  "pattern_id": null,
  "survival_weight": 0.9,

  "created_at": "2025-12-30T00:00:00Z"
}
```

### Structure Atom (Level 5, Lower Survival Weight)

```json
{
  "atom_id": "atm:struct001",
  "content": "The text messages pipeline extracts from chat.db using SQLite queries.",
  "content_hash": "sha256:...",

  "growth_type": "structure",
  "question": "HOW",
  "lens": "MECHANICAL",
  "root_position": "ME",
  "atomic_level": 5,

  "source_id": "doc:text_messages_pipeline",
  "source_type": "document",
  "converter_id": "system",
  "conversion_direction": "INWARD",

  "pattern_id": "atm:pattern001",
  "survival_weight": 0.3,

  "created_at": "2025-12-30T00:00:00Z"
}
```

### External Knowledge Atom (Not-Me Origin)

```json
{
  "atom_id": "atm:external001",
  "content": "BigQuery charges $5 per TB of data scanned.",
  "content_hash": "sha256:...",

  "growth_type": "structure",
  "question": "WHAT",
  "lens": null,
  "root_position": "NOT_ME",
  "atomic_level": 5,

  "source_id": "doc:bigquery_pricing_2025",
  "source_type": "document",
  "converter_id": "system",
  "conversion_direction": "INWARD",

  "pattern_id": null,
  "survival_weight": 0.2,

  "created_at": "2025-12-30T00:00:00Z"
}
```

---

## Query Patterns

### Find all pattern atoms (for reconstitution)

```sql
SELECT atom_id, content, lens, survival_weight
FROM `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
WHERE growth_type IN ('pattern', 'both')
ORDER BY survival_weight DESC, atomic_level ASC
```

### Find atoms that instantiate a pattern

```sql
SELECT atom_id, content, question
FROM `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
WHERE pattern_id = 'atm:pattern001'
ORDER BY question
```

### Check document series coverage for a topic

```sql
SELECT
  question,
  COUNT(*) as atom_count
FROM `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
WHERE content LIKE '%text_messages%'
  AND growth_type = 'structure'
GROUP BY question
ORDER BY question
```

### Find what Not-Me has been consumed

```sql
SELECT
  source_id,
  source_type,
  COUNT(*) as atoms_extracted,
  MIN(created_at) as first_extracted,
  MAX(created_at) as last_extracted
FROM `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
WHERE conversion_direction = 'INWARD'
GROUP BY source_id, source_type
ORDER BY last_extracted DESC
```

### Reconstitution priority order

```sql
SELECT atom_id, content, atomic_level, survival_weight
FROM `flash-clover-464719-g1.knowledge_atoms.knowledge_atoms`
WHERE survival_weight > 0.5
ORDER BY atomic_level ASC, survival_weight DESC
```

---

## Why This Is "Good Enough"

### What It Enables

1. **Traceability**: Full lineage from Not-Me through conversion to Me
2. **Reconstitution**: Ordered rebuilding from seed → framework → root → lenses → applications → implementations
3. **Coverage checking**: Are all 6 questions answered for a topic?
4. **Pattern instantiation**: Which atoms implement which patterns?
5. **Survival prioritization**: What to save if storage is limited?

### What It Doesn't Require

1. **Perfect classification**: `lens`, `root_position`, `atomic_level` are all optional
2. **Manual tagging**: Extraction can infer `growth_type` and `question` from content
3. **Schema migration downtime**: All new fields are nullable, backward compatible
4. **Immediate adoption**: Existing atoms work fine, new fields populated over time

### The Protogenitor Test

Can you answer these questions with this schema?

| Question | Query Approach |
|----------|----------------|
| "What have I consumed from Not-Me?" | Filter by `conversion_direction = 'INWARD'`, group by `source_id` |
| "What patterns exist?" | Filter by `growth_type IN ('pattern', 'both')` |
| "What's missing for this primitive?" | Check `question` coverage for topic |
| "If I lost everything, what do I rebuild first?" | Order by `atomic_level ASC, survival_weight DESC` |
| "Who translated this?" | Check `converter_id` |
| "Is this about Me or Not-Me?" | Check `root_position` |

**Yes.** That's why it's good enough.

---

## Related Documents

- [THE_FRAMEWORK.md](../THE_FRAMEWORK/THE_FRAMEWORK.md) — The primitive. Survival as structure.
- [THE_ROOT.md](../THE_FRAMEWORK/THE_ROOT.md) — Me / Not-Me. The fundamental divide.
- [THE_STRUCTURE.md](../THE_FRAMEWORK/THE_STRUCTURE.md) — Hold → Agent → Hold.
- [TRACEABILITY_MODEL.md](../../../corpus_processing/TRACEABILITY_MODEL.md) — Original traceability design.
- [KNOWLEDGE_ATOM_SCHEMA.md](KNOWLEDGE_ATOM_SCHEMA.md) — Previous version (superseded).

---

**The pattern that can become atoms and reconstitute from atoms survives. This schema enables that.**
