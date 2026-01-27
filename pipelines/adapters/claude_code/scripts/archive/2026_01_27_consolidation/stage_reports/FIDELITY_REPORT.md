> **DEPRECATED**: This document has been superseded.
> - **Deprecated On**: 2026-01-27
> - **Archived On**: 2026-01-27
> - **Reason**: Consolidated duplicate stage reports. Historical snapshots archived to GCS.
> - **Archive Location**: `gs://truth-engine-archive/pipelines/adapters/claude_code/scripts/archive/2026_01_27_consolidation/stage_reports/`
>
> This document has been moved to archive. No redirect stub - file removed from source.

# Fidelity Report: Stage 9 - L3 Span Creation (Named Entity Recognition)

## What Was Requested

Stage 9 (L3 Span Creation) is responsible for:
1. Creates L3 Span entities (Named Entities) from L4 Sentences
2. Uses spaCy NER model (`en_core_web_sm`) for entity extraction
3. Processes input: claude_code_stage_8 (L4 Sentence entities)
4. Produces output: claude_code_stage_9 (L3 Span entities)
5. Extracts named entities: PERSON, ORG, GPE, DATE, TIME, MONEY, etc.
6. Uses shared validation functions for security and consistency
7. No `gc.collect()` calls (anti-pattern removed)
8. Comprehensive error handling with `require_diagnostic_on_error()`
9. Full audit trail and logging

## What Was Implemented

✅ Processes claude_code_stage_8 (L4 Sentence entities)
✅ Produces claude_code_stage_9 (L3 Span entities)
✅ Key features: spaCy NER, Named Entity Extraction, Entity Type Classification
✅ Entity types extracted: PERSON, ORG, GPE, LOC, DATE, TIME, MONEY, PERCENT, PRODUCT, EVENT, WORK_OF_ART, LAW, LANGUAGE, FAC, NORP, QUANTITY, ORDINAL, CARDINAL
✅ Uses `shared_validation.validate_table_id()` for all BigQuery table references
✅ Uses `shared_validation.validate_required_fields()` for record validation
✅ Uses `shared_validation.validate_batch_size()` for batch processing
✅ Comprehensive error handling with `require_diagnostic_on_error()`
✅ Full audit trail and logging
✅ No `gc.collect()` calls
✅ No manual SQL escaping (uses validated table IDs)
✅ Streaming processing pattern (sentences processed one at a time)

## What's Missing

Nothing - all requirements implemented.

## What Assumptions Were Made

1. **Input table exists**: Assumes Stage 8 has created claude_code_stage_8 with L4 Sentence entities
2. **Schema matches**: Assumes input contains: id, content, parent_id, level=4
3. **spaCy model available**: Assumes `en_core_web_sm` is installed and loadable
4. **BigQuery access**: Assumes proper BigQuery credentials and permissions
5. **Batch size**: Default batch size may need adjustment for large datasets
6. **NER accuracy**: spaCy NER accuracy depends on text quality and domain

## Entity Hierarchy Context

```
L8 (Conversation) → L7 (Compaction Segment) → L6 (Turn) → L5 (Message) → L4 (Sentence) → L3 (Span/NER) → L2 (Word - ATOMIC)
                                                                                              ↑
                                                                                         THIS STAGE
```

## Output Schema

Each L3 Span entity contains:
- `id`: Unique identifier (UUID)
- `content`: The named entity text
- `parent_id`: Reference to parent L4 Sentence
- `level`: Always 3 (Span level)
- `entity_type`: spaCy entity label (PERSON, ORG, etc.)
- `start_char`: Character offset start position
- `end_char`: Character offset end position
- `run_id`: Processing run identifier
- `ingestion_date`: Date of processing
- `created_at`: Timestamp of creation

## Verification

Run: `python3 pipelines/claude_code/scripts/stage_9/verify_stage_9.py`
Check: Output table contains L3 Span entities (level=3)
Check: Entity types are valid spaCy NER labels
Check: Parent IDs reference valid L4 Sentence entities
Check: No errors in logs
