# Lexicon Entity Model - Comprehensive Design

**Author**: Claude Code
**Created**: 2025-11-27
**Version**: 1.0
**Status**: Implementation Ready

---

## 1. Overview

This document defines the complete entity model for parsing Merriam-Webster Dictionary and Thesaurus API responses into a normalized, queryable structure aligned with the Truth Engine's SPINE architecture.

### 1.1 Design Principles

1. **Entity ID Consistency**: Every entity receives a canonical ID following the `architect_central_services.identity_service` pattern
2. **Hierarchical Linking**: Clear parent-child relationships with foreign key references
3. **Metadata vs Columns**: Structured, queryable data in columns; variable/rare data in JSON metadata
4. **No Data Loss**: All API response data is preserved and accessible
5. **Query Optimization**: Clustering and partitioning aligned with common access patterns

### 1.2 Entity Hierarchy

```
lexicon.dictionary_headwords (L8 equivalent - canonical word entry)
├── lexicon.dictionary_entries (L7 equivalent - homograph/entry)
│   ├── lexicon.dictionary_definitions (L6 equivalent - sense/definition)
│   │   ├── lexicon.dictionary_examples (L5 equivalent - verbal illustrations)
│   │   └── lexicon.dictionary_cross_references (L5 equivalent - links)
│   ├── lexicon.dictionary_pronunciations (L5 equivalent)
│   ├── lexicon.dictionary_inflections (L5 equivalent)
│   └── lexicon.dictionary_run_ons (L5 equivalent - derived words)
└── lexicon.thesaurus_entries
    └── lexicon.thesaurus_relations (synonyms, antonyms, related, near)
```

---

## 2. Entity ID Scheme

All IDs follow the pattern defined in `architect_central_services.identity_service`:

### 2.1 ID Format

| Entity | ID Pattern | Example |
|--------|------------|---------|
| Headword | `hw:{word_hash}` | `hw:a1b2c3d4e5f6` |
| Entry | `entry:{headword_hash}:{homograph}` | `entry:a1b2c3d4e5f6:1` |
| Definition | `def:{entry_hash}:{sense_num}` | `def:x1y2z3:1a` |
| Example | `vis:{def_hash}:{seq}` | `vis:m1n2o3:0001` |
| Pronunciation | `pron:{entry_hash}:{seq}` | `pron:x1y2z3:0001` |
| Inflection | `infl:{entry_hash}:{seq}` | `infl:x1y2z3:0001` |
| Run-On | `uro:{entry_hash}:{seq}` | `uro:x1y2z3:0001` |
| Cross-Reference | `xref:{def_hash}:{seq}` | `xref:m1n2o3:0001` |
| Thesaurus Entry | `thes:{headword_hash}:{homograph}` | `thes:a1b2c3:1` |
| Thesaurus Relation | `rel:{thes_hash}:{type}:{seq}` | `rel:t1t2t3:syn:0001` |

### 2.2 Hash Generation

```python
def generate_lexicon_id(prefix: str, *components: str) -> str:
    """Generate deterministic lexicon entity ID.

    Uses MD5 hash of concatenated components for consistency.
    Same input always produces same ID.
    """
    from hashlib import md5
    content = ":".join(str(c) for c in components)
    hash_val = md5(content.encode()).hexdigest()[:12]
    return f"{prefix}:{hash_val}"
```

---

## 3. Column vs Metadata Decision Matrix

### 3.1 Criteria for Column Placement

| Criterion | Column | Metadata |
|-----------|--------|----------|
| Queried frequently | ✅ | ❌ |
| Used for JOINs | ✅ | ❌ |
| Fixed structure | ✅ | ❌ |
| Cardinality known | ✅ | ❌ |
| Variable structure | ❌ | ✅ |
| Rare occurrence (<10%) | ❌ | ✅ |
| Nested/complex objects | ❌ | ✅ |
| Display-only (formatting) | ❌ | ✅ |

### 3.2 Field Classification

#### Dictionary Headwords (L8)
| Field | Placement | Rationale |
|-------|-----------|-----------|
| entity_id | COLUMN | Primary key |
| word | COLUMN | Primary query field |
| word_normalized | COLUMN | Lowercase for matching |
| source | COLUMN | API source tracking |
| entry_count | COLUMN | Quick stats |
| first_known_use | COLUMN | Historical queries |
| is_offensive | COLUMN | Content filtering |
| stems | COLUMN (ARRAY) | Search expansion |
| metadata | JSON | Audio refs, artwork, tables |

#### Dictionary Entries (L7)
| Field | Placement | Rationale |
|-------|-----------|-----------|
| entity_id | COLUMN | Primary key |
| headword_id | COLUMN | Foreign key |
| homograph | COLUMN | Ordering/filtering |
| part_of_speech | COLUMN | Common filter |
| mw_entry_id | COLUMN | API reference |
| mw_uuid | COLUMN | Unique identifier |
| definition_count | COLUMN | Quick stats |
| etymology | COLUMN | Searchable text |
| metadata | JSON | Labels, variants, artwork |

#### Dictionary Definitions (L6)
| Field | Placement | Rationale |
|-------|-----------|-----------|
| entity_id | COLUMN | Primary key |
| entry_id | COLUMN | Foreign key |
| sense_number | COLUMN | Ordering |
| sense_sequence | COLUMN | Full sense path (1a, 2b(1)) |
| definition_text | COLUMN | Primary content, searchable |
| definition_raw | COLUMN | With markup preserved |
| grammatical_label | COLUMN | Transitive/intransitive |
| example_count | COLUMN | Quick stats |
| metadata | JSON | Status labels, subsenses |

#### Dictionary Examples (L5)
| Field | Placement | Rationale |
|-------|-----------|-----------|
| entity_id | COLUMN | Primary key |
| definition_id | COLUMN | Foreign key |
| sequence | COLUMN | Ordering |
| example_text | COLUMN | Searchable |
| attribution | JSON | Author, source, date |

#### Thesaurus Relations
| Field | Placement | Rationale |
|-------|-----------|-----------|
| entity_id | COLUMN | Primary key |
| source_entry_id | COLUMN | Foreign key |
| relation_type | COLUMN | syn/ant/rel/near |
| target_word | COLUMN | The related word |
| target_word_id | COLUMN | FK to headwords (if exists) |
| sequence | COLUMN | Ordering |
| sense_context | COLUMN | Which sense it relates to |

---

## 4. Table Schemas

### 4.1 lexicon.dictionary_headwords

```sql
CREATE TABLE IF NOT EXISTS `{project}.lexicon.dictionary_headwords` (
  -- Identity
  entity_id STRING NOT NULL,              -- hw:{hash}

  -- Core Fields
  word STRING NOT NULL,                   -- Original headword
  word_normalized STRING NOT NULL,        -- Lowercase for matching
  source STRING NOT NULL,                 -- 'mw_collegiate'

  -- Aggregated Stats
  entry_count INT64,                      -- Number of entries (homographs)
  total_definition_count INT64,           -- Sum across all entries

  -- Key Searchable Fields
  first_known_use STRING,                 -- "15th century"
  is_offensive BOOL DEFAULT FALSE,        -- Any entry marked offensive

  -- Search Expansion
  stems ARRAY<STRING>,                    -- All searchable forms

  -- Variable/Complex Data
  metadata JSON,                          -- artwork, audio, table refs

  -- Tracking
  api_response_hash STRING,               -- For change detection
  pulled_at TIMESTAMP,                    -- When retrieved from API
  parsed_at TIMESTAMP,                    -- When parsed
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY word_normalized, entity_id;
```

### 4.2 lexicon.dictionary_entries

```sql
CREATE TABLE IF NOT EXISTS `{project}.lexicon.dictionary_entries` (
  -- Identity
  entity_id STRING NOT NULL,              -- entry:{hash}:{hom}
  headword_id STRING NOT NULL,            -- FK to headwords

  -- Position/Ordering
  homograph INT64 NOT NULL DEFAULT 1,     -- 1, 2, 3 for homographs
  entry_sequence INT64 NOT NULL,          -- Order in response

  -- Core Fields
  word STRING NOT NULL,                   -- May differ from headword
  part_of_speech STRING,                  -- noun, verb, adjective, etc.

  -- MW Identifiers
  mw_entry_id STRING,                     -- meta.id
  mw_uuid STRING,                         -- meta.uuid
  mw_sort STRING,                         -- meta.sort (9-digit)

  -- Key Content
  etymology STRING,                       -- Cleaned etymology text
  first_known_use STRING,                 -- date field

  -- Stats
  definition_count INT64,
  pronunciation_count INT64,
  inflection_count INT64,

  -- Flags
  is_offensive BOOL DEFAULT FALSE,

  -- Variable Data
  metadata JSON,                          -- labels, variants, artwork
  etymology_raw JSON,                     -- Full etymology structure

  -- Tracking
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY headword_id, entity_id;
```

### 4.3 lexicon.dictionary_definitions

```sql
CREATE TABLE IF NOT EXISTS `{project}.lexicon.dictionary_definitions` (
  -- Identity
  entity_id STRING NOT NULL,              -- def:{hash}:{sense}
  entry_id STRING NOT NULL,               -- FK to entries
  headword_id STRING NOT NULL,            -- FK to headwords (denormalized)

  -- Position/Ordering
  sense_number STRING,                    -- "1", "2a", "2b(1)"
  sense_sequence STRING NOT NULL,         -- Full path for ordering
  definition_index INT64 NOT NULL,        -- 0-based index

  -- Core Content
  word STRING NOT NULL,                   -- Denormalized for search
  part_of_speech STRING,                  -- Denormalized
  definition_text STRING NOT NULL,        -- Cleaned text
  definition_raw STRING,                  -- With MW markup

  -- Grammatical Info
  grammatical_label STRING,               -- T (transitive), I (intransitive)
  verb_divider STRING,                    -- "transitive verb", etc.

  -- Short Definition
  short_definition STRING,                -- From shortdef array

  -- Stats
  example_count INT64 DEFAULT 0,
  cross_reference_count INT64 DEFAULT 0,

  -- Variable Data
  metadata JSON,                          -- status labels, subsenses

  -- Extracted Words (for semantic expansion)
  extracted_words ARRAY<STRING>,          -- Words from definition text

  -- Tracking
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY headword_id, entry_id, entity_id;
```

### 4.4 lexicon.dictionary_examples

```sql
CREATE TABLE IF NOT EXISTS `{project}.lexicon.dictionary_examples` (
  -- Identity
  entity_id STRING NOT NULL,              -- vis:{hash}:{seq}
  definition_id STRING NOT NULL,          -- FK to definitions
  entry_id STRING NOT NULL,               -- FK (denormalized)
  headword_id STRING NOT NULL,            -- FK (denormalized)

  -- Position
  sequence INT64 NOT NULL,

  -- Content
  example_text STRING NOT NULL,           -- Cleaned text
  example_raw STRING,                     -- With markup
  word STRING NOT NULL,                   -- Denormalized

  -- Attribution (optional)
  author STRING,
  source_title STRING,
  source_date STRING,

  -- Full Attribution
  attribution JSON,                       -- Complete aq object

  -- Tracking
  created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY headword_id, definition_id;
```

### 4.5 lexicon.dictionary_pronunciations

```sql
CREATE TABLE IF NOT EXISTS `{project}.lexicon.dictionary_pronunciations` (
  -- Identity
  entity_id STRING NOT NULL,              -- pron:{hash}:{seq}
  entry_id STRING NOT NULL,               -- FK to entries
  headword_id STRING NOT NULL,            -- FK (denormalized)

  -- Position
  sequence INT64 NOT NULL,
  context STRING,                         -- "definition", "entry", "run_on"
  context_id STRING,                      -- ID of context entity

  -- Content
  word STRING NOT NULL,
  phonetic_mw STRING,                     -- Merriam-Webster format
  phonetic_ipa STRING,                    -- IPA if available

  -- Labels
  label_before STRING,                    -- "also", "British"
  label_after STRING,

  -- Audio
  audio_file STRING,                      -- Filename
  audio_ref STRING,                       -- Reference code

  -- Full Data
  metadata JSON,                          -- Complete prs object

  -- Tracking
  created_at TIMESTAMP NOT NULL
)
CLUSTER BY headword_id, entry_id;
```

### 4.6 lexicon.dictionary_inflections

```sql
CREATE TABLE IF NOT EXISTS `{project}.lexicon.dictionary_inflections` (
  -- Identity
  entity_id STRING NOT NULL,              -- infl:{hash}:{seq}
  entry_id STRING NOT NULL,               -- FK to entries
  headword_id STRING NOT NULL,            -- FK (denormalized)

  -- Position
  sequence INT64 NOT NULL,

  -- Content
  word STRING NOT NULL,                   -- Base word
  inflection_form STRING NOT NULL,        -- "running", "ran"
  inflection_cutback STRING,              -- Ending only "-ning"
  inflection_label STRING,                -- "also", "or", "plural"

  -- Tracking
  created_at TIMESTAMP NOT NULL
)
CLUSTER BY headword_id, entry_id;
```

### 4.7 lexicon.dictionary_run_ons

```sql
CREATE TABLE IF NOT EXISTS `{project}.lexicon.dictionary_run_ons` (
  -- Identity
  entity_id STRING NOT NULL,              -- uro:{hash}:{seq} or dro:{hash}:{seq}
  entry_id STRING NOT NULL,               -- FK to entries
  headword_id STRING NOT NULL,            -- FK (denormalized)

  -- Position
  sequence INT64 NOT NULL,
  run_on_type STRING NOT NULL,            -- 'undefined' (uro) or 'defined' (dro)

  -- Content
  run_on_word STRING NOT NULL,            -- The derived word/phrase
  part_of_speech STRING,                  -- Required for uros
  definition_text STRING,                 -- For dros only

  -- Links back to headwords table if this word exists
  linked_headword_id STRING,              -- FK if word has own entry

  -- Variable Data
  metadata JSON,                          -- pronunciations, inflections

  -- Tracking
  created_at TIMESTAMP NOT NULL
)
CLUSTER BY headword_id, entry_id;
```

### 4.8 lexicon.dictionary_cross_references

```sql
CREATE TABLE IF NOT EXISTS `{project}.lexicon.dictionary_cross_references` (
  -- Identity
  entity_id STRING NOT NULL,              -- xref:{hash}:{seq}
  definition_id STRING NOT NULL,          -- FK to definitions
  entry_id STRING NOT NULL,               -- FK (denormalized)
  headword_id STRING NOT NULL,            -- FK (denormalized)

  -- Position
  sequence INT64 NOT NULL,

  -- Reference Info
  reference_type STRING NOT NULL,         -- 'synonym', 'compare', 'see_also'
  target_word STRING NOT NULL,            -- Referenced word
  target_entry_id STRING,                 -- MW entry ID if provided
  display_text STRING,                    -- How it appears in definition

  -- Link to our headword if exists
  linked_headword_id STRING,              -- FK if we have this word

  -- Tracking
  created_at TIMESTAMP NOT NULL
)
CLUSTER BY headword_id, target_word;
```

### 4.9 lexicon.thesaurus_entries

```sql
CREATE TABLE IF NOT EXISTS `{project}.lexicon.thesaurus_entries` (
  -- Identity
  entity_id STRING NOT NULL,              -- thes:{hash}:{hom}
  headword_id STRING,                     -- FK to dictionary_headwords if exists

  -- Core Fields
  word STRING NOT NULL,
  word_normalized STRING NOT NULL,
  part_of_speech STRING,
  homograph INT64 DEFAULT 1,

  -- Short Definition
  definition STRING,

  -- Stats
  synonym_count INT64 DEFAULT 0,
  antonym_count INT64 DEFAULT 0,
  related_count INT64 DEFAULT 0,
  near_antonym_count INT64 DEFAULT 0,

  -- MW Identifiers
  mw_entry_id STRING,

  -- Tracking
  pulled_at TIMESTAMP,
  parsed_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
)
CLUSTER BY word_normalized, entity_id;
```

### 4.10 lexicon.thesaurus_relations

```sql
CREATE TABLE IF NOT EXISTS `{project}.lexicon.thesaurus_relations` (
  -- Identity
  entity_id STRING NOT NULL,              -- rel:{hash}:{type}:{seq}
  thesaurus_entry_id STRING NOT NULL,     -- FK to thesaurus_entries

  -- Source Word Info (denormalized)
  source_word STRING NOT NULL,
  source_headword_id STRING,              -- FK to dictionary_headwords

  -- Relation Info
  relation_type STRING NOT NULL,          -- 'synonym', 'antonym', 'related', 'near_antonym'
  sequence INT64 NOT NULL,
  sense_number STRING,                    -- Which sense this relates to

  -- Target Word
  target_word STRING NOT NULL,
  target_word_normalized STRING NOT NULL,

  -- Links
  target_headword_id STRING,              -- FK if target has dictionary entry
  target_thesaurus_id STRING,             -- FK if target has thesaurus entry

  -- Tracking
  created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY source_word, relation_type, target_word;
```

---

## 5. Query Patterns

### 5.1 Get Complete Word Entry

```sql
-- Get headword with all entries and definitions
SELECT
  h.word,
  h.first_known_use,
  e.part_of_speech,
  e.etymology,
  d.sense_number,
  d.definition_text,
  d.short_definition
FROM lexicon.dictionary_headwords h
JOIN lexicon.dictionary_entries e ON e.headword_id = h.entity_id
JOIN lexicon.dictionary_definitions d ON d.entry_id = e.entity_id
WHERE h.word_normalized = 'truth'
ORDER BY e.homograph, d.definition_index;
```

### 5.2 Find All Synonyms

```sql
SELECT
  r.source_word,
  r.relation_type,
  r.target_word,
  CASE WHEN r.target_headword_id IS NOT NULL THEN 'has_definition' ELSE 'no_definition' END as status
FROM lexicon.thesaurus_relations r
WHERE r.source_word = 'truth'
  AND r.relation_type = 'synonym'
ORDER BY r.sequence;
```

### 5.3 Semantic Network Expansion

```sql
-- Get words to add to master_word_list
WITH definition_words AS (
  SELECT DISTINCT word
  FROM lexicon.dictionary_definitions,
  UNNEST(extracted_words) as word
  WHERE headword_id IN (SELECT entity_id FROM lexicon.dictionary_headwords WHERE word_normalized IN ('truth', 'meaning'))
),
relation_words AS (
  SELECT DISTINCT target_word as word
  FROM lexicon.thesaurus_relations
  WHERE source_word IN ('truth', 'meaning')
)
SELECT * FROM definition_words
UNION DISTINCT
SELECT * FROM relation_words;
```

---

## 6. Processing Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│ Stage 1: API Ingestion (dictionary_api_stage_1.py)               │
│ - Pull raw JSON from MW API                                      │
│ - Store in dictionary_api_stage_1 / thesaurus_api_stage_1        │
│ - Track pull status in master_word_list                          │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 2: Parsing (lexicon_parser.py)                             │
│ - Parse JSON into normalized entities                            │
│ - Generate entity IDs                                            │
│ - Extract words from definitions                                 │
│ - Create cross-references                                        │
│ - Populate all lexicon.* tables                                  │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 3: Linking (lexicon_linker.py)                             │
│ - Link cross-references to existing headwords                    │
│ - Link thesaurus relations to dictionary entries                 │
│ - Update master_word_list with expansion words                   │
│ - Calculate priority scores for new words                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 7. Integration with master_word_list

### 7.1 Updated master_word_list Schema

```sql
ALTER TABLE lexicon.master_word_list
ADD COLUMN IF NOT EXISTS dictionary_headword_id STRING,  -- FK to headwords
ADD COLUMN IF NOT EXISTS thesaurus_entry_id STRING,      -- FK to thesaurus
ADD COLUMN IF NOT EXISTS definition_count INT64,
ADD COLUMN IF NOT EXISTS synonym_count INT64,
ADD COLUMN IF NOT EXISTS antonym_count INT64;
```

### 7.2 Expansion Priority

Words are prioritized for API pulls based on:

1. **Depth** (lower = higher priority)
2. **Source Type Priority**:
   - core: 1.0
   - synonym: 0.9
   - antonym: 0.8
   - definition_word: 0.7
3. **Parent Word Rank** (if depth > 0)

```python
priority_score = (1.0 / (depth + 1)) * source_type_weight * (1.0 / parent_rank)
```

---

## 8. Change Log

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-11-27 | 1.0 | Claude Code | Initial design |
