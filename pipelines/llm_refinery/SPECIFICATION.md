# LLM Refinery Pipeline Specification

**Version**: 1.0.0
**Author**: Claude (Opus 4.5)
**Date**: 2026-02-02
**Status**: DRAFT - REQUIRES VALIDATION

---

## 1. Purpose

The LLM Refinery Pipeline transforms raw conversation exports into a normalized entity hierarchy for the Genesis training system.

### 1.1 Input

- **Source**: JSON conversation exports from ChatGPT, Claude, or other LLM interfaces
- **Format**: JSONL or JSON array
- **Location**: `/data/web_exports/{source}/conversations.json`

### 1.2 Output

- **Destination**: BigQuery table `flash-clover-464719-g1.spine.entity_unified`
- **Format**: One row per entity at each level of the hierarchy
- **Pipeline Label**: `llm_refinery` (always, never anything else)

---

## 2. Entity Hierarchy

The pipeline creates a 7-level entity hierarchy. Each level is a child of the level above.

```
L8: Conversation (root)
 └─ L7: Topic Segment (semantic grouping of turns)
     └─ L6: Turn (one exchange - user message + assistant response)
         └─ L5: Message (individual message within a turn)
             └─ L4: Sentence (grammatical sentence)
                 └─ L3: Span (phrase or clause)
                     └─ L2: Word (individual token)
```

### 2.1 Level Definitions

| Level | Entity Type | Parent Level | Description |
|-------|-------------|--------------|-------------|
| L8 | conversation | NULL | The entire conversation |
| L7 | topic_segment | L8 | A coherent topic within the conversation |
| L6 | turn | L7 | One back-and-forth exchange |
| L5 | message | L6 | A single message (user or assistant) |
| L4 | sentence | L5 | A grammatical sentence |
| L3 | span | L4 | A meaningful phrase |
| L2 | word | L3 | An individual word/token |

### 2.2 Entity ID Format

All entity IDs MUST follow this format:
```
{level_prefix}:{source_pipeline}:{uuid}
```

Examples:
- `conv:llm_refinery:550e8400-e29b-41d4-a716-446655440000`
- `turn:llm_refinery:550e8400-e29b-41d4-a716-446655440001`
- `msg:llm_refinery:550e8400-e29b-41d4-a716-446655440002`

Level prefixes:
- L8: `conv`
- L7: `topic`
- L6: `turn`
- L5: `msg`
- L4: `sent`
- L3: `span`
- L2: `word`

### 2.3 Parent Chain Rules

**CRITICAL**: Every entity MUST have a valid parent reference.

1. L8 entities have `parent_id = NULL` (they are roots)
2. L7 entities have `parent_id = L8 entity_id`
3. L6 entities have `parent_id = L7 entity_id`
4. L5 entities have `parent_id = L6 entity_id`
5. L4 entities have `parent_id = L5 entity_id`
6. L3 entities have `parent_id = L4 entity_id`
7. L2 entities have `parent_id = L3 entity_id`

**FORBIDDEN**:
- L5 pointing directly to L8 (skips L6, L7)
- Any entity with a parent_id that doesn't exist
- Circular references

---

## 3. Processing Stages

### Stage 1: Load Source Data

```
Input: conversations.json
Output: List of raw conversation dicts
Validation:
  - File exists and is readable
  - Valid JSON format
  - Contains expected fields (id, messages, etc.)
```

### Stage 2: Create L8 Conversation Entity

```
Input: Raw conversation dict
Output: ConversationL8 entity
Fields to extract:
  - conversation_id (from source or generate UUID)
  - title (if available)
  - created_at (from source timestamp)
  - message_count (count of messages array)
```

### Stage 3: LLM Topic Segmentation (L7)

```
Input: Full conversation text
Output: List of TopicSegmentL7 entities
LLM Task: Identify distinct topics/themes in the conversation
Validation:
  - LLM returns valid JSON array
  - Each segment has start/end indices
  - Segments cover entire conversation (no gaps)
  - Segments don't overlap
```

### Stage 4: Turn Extraction (L6)

```
Input: Raw messages array
Output: List of TurnL6 entities
Logic: Group consecutive user/assistant messages into turns
A turn typically contains:
  - 1 user message
  - 1 assistant response
  - OR: multiple back-and-forth if no clear boundary
```

### Stage 5: Message Extraction (L5)

```
Input: Turn entity
Output: List of MessageL5 entities
Fields:
  - role: "user" | "assistant" | "system"
  - content: The message text
  - timestamp: From source if available
```

### Stage 6: LLM Sentence Parsing (L4)

```
Input: Message text
Output: List of SentenceL4 entities
LLM Task: Split text into grammatical sentences
Validation:
  - Sentences concatenate back to original text
  - No content lost
```

### Stage 7: LLM Span Extraction (L3)

```
Input: Sentence text
Output: List of SpanL3 entities
LLM Task: Identify meaningful phrases/clauses
Examples: noun phrases, verb phrases, named entities
```

### Stage 8: Tokenization (L2)

```
Input: Span text
Output: List of WordL2 entities
Logic: Split on whitespace and punctuation
Fields:
  - text: The word/token
  - word_type: noun, verb, adjective, etc.
  - is_key_term: True if significant
  - canonical_form: Lemmatized form
```

### Stage 9: Write to BigQuery

```
Input: All entities from stages 2-8
Output: Rows in entity_unified table
Method: Batch load via JSONL file (NOT streaming inserts)
Validation:
  - Schema matches exactly
  - All parent references are valid
  - No duplicates
```

---

## 4. BigQuery Schema

The `entity_unified` table has these columns:

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| entity_id | STRING | YES | Unique identifier |
| level | INT64 | YES | 2-8 |
| entity_type | STRING | YES | conversation, topic_segment, turn, message, sentence, span, word |
| entity_mode | STRING | YES | source, derived |
| parent_id | STRING | NO | Parent entity_id (NULL for L8) |
| conversation_id | STRING | YES | Root conversation ID |
| topic_segment_id | STRING | NO | L7 ID if applicable |
| turn_id | STRING | NO | L6 ID if applicable |
| message_id | STRING | NO | L5 ID if applicable |
| sentence_id | STRING | NO | L4 ID if applicable |
| span_id | STRING | NO | L3 ID if applicable |
| word_id | STRING | NO | L2 ID if applicable |
| text | STRING | NO | Entity text content |
| source_pipeline | STRING | YES | Always "llm_refinery" |
| source_ids | ARRAY<STRING> | NO | Original source IDs |
| source_file | STRING | YES | Filename |
| source_file_path | STRING | YES | Full path |
| source_system | STRING | YES | chatgpt, claude, etc. |
| l7_count | INT64 | NO | Count of L7 children |
| l6_count | INT64 | NO | Count of L6 children |
| l5_count | INT64 | NO | Count of L5 children |
| l4_count | INT64 | NO | Count of L4 children |
| l3_count | INT64 | NO | Count of L3 children |
| l2_count | INT64 | NO | Count of L2 children |
| metadata | JSON | NO | Additional metadata |
| role | STRING | NO | user/assistant/system |
| persona | STRING | NO | Identified persona |
| canonical_form | STRING | NO | Normalized form |
| created_at | TIMESTAMP | YES | Entity creation time |
| updated_at | TIMESTAMP | YES | Last update time |
| source_message_timestamp | TIMESTAMP | NO | Original message time |
| ingestion_timestamp | TIMESTAMP | YES | When ingested |
| content_date | DATE | NO | Content date |
| ingestion_job_id | STRING | YES | Job identifier |
| validation_status | STRING | NO | valid/invalid/pending |

---

## 5. Error Handling

### 5.1 LLM Response Errors

**RULE**: If the LLM returns invalid JSON, STOP PROCESSING.

```
DO NOT:
  - Log warning and continue
  - Return empty dict
  - Use partial data

DO:
  - Log the error with full context
  - Raise an exception
  - Stop the pipeline
  - Report which conversation failed
```

### 5.2 Schema Validation Errors

**RULE**: If output doesn't match BigQuery schema, STOP PROCESSING.

```
Validate BEFORE writing:
  1. All required fields present
  2. Field types correct
  3. Level in valid range (2-8)
  4. Parent chain valid
```

### 5.3 Partial Processing

**RULE**: Full file or nothing.

```
If pipeline fails mid-file:
  1. Delete ALL entities from this run
  2. Fix the error
  3. Restart from beginning

NEVER leave partial data in BigQuery.
```

---

## 6. Idempotency

The pipeline MUST be idempotent. Running it twice on the same input should produce the same result.

### 6.1 Duplicate Prevention

Before processing a conversation:
1. Check if conversation_id already exists in entity_unified
2. If yes, skip (or update, but never duplicate)

### 6.2 Job Tracking

Each run gets a unique `ingestion_job_id`:
```
llm_refinery:{timestamp}:{uuid}
```

This allows:
- Tracking which entities came from which run
- Rolling back a failed run
- Auditing

---

## 7. Success Criteria

A successful pipeline run:

1. ✅ All conversations processed without error
2. ✅ All entities have valid parent chains
3. ✅ No duplicate entities created
4. ✅ All fields match BigQuery schema
5. ✅ entity_id format is correct for all entities
6. ✅ source_pipeline = "llm_refinery" for all entities
7. ✅ LLM returned valid JSON for all requests
8. ✅ Output JSONL file created before BigQuery load
9. ✅ BigQuery load completed with 0 errors

---

## 8. What This Pipeline is NOT

1. **NOT** a streaming service - it runs batch jobs
2. **NOT** tolerant of errors - it fails fast
3. **NOT** incremental - it processes whole files
4. **NOT** real-time - there's no urgency over correctness
5. **NOT** clever - it does exactly what's specified, nothing more

---

## VALIDATION CHECKLIST

Before accepting this specification:

- [ ] Entity hierarchy makes sense (L8 → L2)
- [ ] Parent chain rules are complete and unambiguous
- [ ] Processing stages are in correct order
- [ ] Schema matches actual BigQuery table
- [ ] Error handling rules are explicit
- [ ] Idempotency requirements are clear
- [ ] Success criteria are measurable

---

**END OF SPECIFICATION - REQUIRES THREE VALIDATIONS BEFORE USE**
