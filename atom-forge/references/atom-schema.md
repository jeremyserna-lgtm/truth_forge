# Knowledge Atom Schema Reference

## Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | STRING | YES | SHA-256 hash of normalized content |
| content | STRING | YES | The knowledge statement (irreducible unit) |
| source_file | STRING | YES | Source file reference |
| metadata | AtomMetadata | YES | 12-dimensional metadata object |
| embedding | ARRAY<FLOAT64> | NO | 3072-dim vector (Gemini text-embedding-004) |
| embedding_status | STRING | YES | pending, success, or failed |
| created_at | INT64 | YES | Unix timestamp in milliseconds |

## ID Generation

```
id = sha256(normalize(content)).hexdigest()
```

Where `normalize()`:
1. Lowercase the content
2. Strip leading/trailing whitespace
3. Collapse multiple whitespace to single space
4. Remove trailing punctuation variance

## The 12 Metadata Dimensions

### 1. Semantic
- `theme` (STRING): Primary topic
- `domain` (STRING): Knowledge domain
- `abstraction_level` (ENUM): concrete | conceptual | abstract | meta

### 2. Significance
- `tier` (ENUM): Foundational | Structural | Insight | Nuance | Detail
- `novelty` (FLOAT): 0.0-1.0
- `actionability` (FLOAT): 0.0-1.0

### 3. Epistemic
- `certainty` (ENUM): fact | consensus | claim | speculation | hypothesis
- `evidence_strength` (FLOAT): 0.0-1.0
- `verifiability` (ENUM): observable | testable | logical | intuitive

### 4. Temporal
- `scope` (ENUM): universal | historical | current | emerging | future
- `durability` (ENUM): permanent | durable | transient | ephemeral

### 5. Relational
- `entities` (ARRAY<STRING>): Related entities
- `concepts` (ARRAY<STRING>): Related concepts
- `dependencies` (ARRAY<STRING>): Prerequisites
- `implications` (ARRAY<STRING>): Consequences

### 6. Dialectical
- `supports` (ARRAY<STRING>): Ideas supported
- `contradicts` (ARRAY<STRING>): Ideas contradicted
- `tensions` (ARRAY<STRING>): Unresolved tensions
- `synthesis_potential` (STRING): Possible synthesis

### 7. Affective
- `sentiment` (FLOAT): -1.0 to 1.0
- `intensity` (FLOAT): 0.0-1.0
- `stakes` (ENUM): existential | high | medium | low | trivial
- `urgency` (FLOAT): 0.0-1.0

### 8. Pragmatic
- `action_items` (ARRAY<STRING>): What to do
- `preconditions` (ARRAY<STRING>): What must be true first
- `consequences` (ARRAY<STRING>): Expected outcomes
- `audience` (ARRAY<STRING>): Who should know

### 9. Structural
- `type` (ENUM): claim | definition | comparison | causation | sequence | classification
- `complexity` (ENUM): atomic | compound | nested
- `completeness` (FLOAT): 0.0-1.0

### 10. Ontological
- `entity_type` (ENUM): thing | process | relation | property | state
- `categories` (ARRAY<STRING>): Classifications
- `is_a` (ARRAY<STRING>): Taxonomic parents
- `has_parts` (ARRAY<STRING>): Components

### 11. Normative
- `type` (ENUM): descriptive | prescriptive | evaluative
- `values_invoked` (ARRAY<STRING>): Values referenced
- `should_statements` (ARRAY<STRING>): Prescriptions

### 12. Enrichment Tracking
- `enrichment_coverage` (FLOAT): 0.0-100.0 (% of dimensions populated)
- `last_enriched` (INT64): Timestamp of last enrichment pass

## Embedding Configuration

- **Model**: gemini-embedding-001 (text-embedding-004)
- **Dimensions**: 3,072
- **Task types**: RETRIEVAL_DOCUMENT, RETRIEVAL_QUERY, SEMANTIC_SIMILARITY, CLUSTERING, CLASSIFICATION, QUESTION_ANSWERING

## 3-Gate Deduplication

1. **Hash Gate**: SHA-256 exact match → reject
2. **Similarity Gate**: Cosine similarity >= 0.95 → merge/consolidate
3. **Knowledge Graph Gate**: Entity relationship equivalence → resolve

## BigQuery Table

```
flash-clover-464719-g1.knowledge_atoms
```

Write method: SafeBigQueryWriter with WRITE_APPEND only.
