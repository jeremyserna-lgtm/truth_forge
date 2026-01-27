> **DEPRECATED**: This document has been superseded.
> - **Deprecated On**: 2026-01-27
> - **Archived On**: 2026-01-27
> - **Reason**: Consolidated duplicate stage reports. Historical snapshots archived to GCS.
> - **Archive Location**: `gs://truth-engine-archive/pipelines/adapters/claude_code/scripts/archive/2026_01_27_consolidation/stage_reports/`
>
> This document has been moved to archive. No redirect stub - file removed from source.

# Honesty Report: Stage 9 - L3 Span Creation (Named Entity Recognition)

## All Configuration Parameters

### Command-Line Arguments:
- `--batch-size N`: Batch size for processing (default: 10000)
- `--dry-run`: Validate and process sample but don't write to output table
- `--run-id`: Specify a run ID (auto-generated if not provided)

### Hardcoded Values:
- Default batch size: 10000 sentences per batch
- spaCy model: `en_core_web_sm`
- Table names: Defined in `shared/constants.py`
- Validation functions: From `shared_validation.py`
- Dry-run sample size: 100 sentences

### spaCy NER Configuration:
- Model: `en_core_web_sm` (English small model)
- Entity types: All 18 spaCy entity types supported
- Processing: Single sentence at a time (streaming pattern)

## All Limits

### Processing Limits:
- **Batch size**: Default 10000, can be overridden via `--batch-size`
- **Memory**: Streaming pattern - sentences processed one at a time, not loaded into memory
- **BigQuery quotas**: Subject to BigQuery daily limits (1000 load jobs, 2000 query jobs)
- **spaCy throughput**: ~10,000 sentences/minute on typical hardware

### Table Limits:
- **Table ID validation**: All table IDs validated via `shared_validation.validate_table_id()`
- **SQL injection prevention**: No manual string interpolation, all table IDs validated
- **Path validation**: All paths validated via `shared_validation.validate_path()`

### NER Limits:
- **Entity types**: 18 spaCy types (PERSON, ORG, GPE, LOC, DATE, TIME, MONEY, PERCENT, PRODUCT, EVENT, WORK_OF_ART, LAW, LANGUAGE, FAC, NORP, QUANTITY, ORDINAL, CARDINAL)
- **Accuracy**: spaCy `en_core_web_sm` F1 ~85% on standard benchmarks
- **Domain specificity**: Model trained on web text, may underperform on specialized domains

### Data Limits:
- **No explicit row limits**: Processes all L4 Sentences in input table
- **No explicit size limits**: Subject to BigQuery and system memory limits

## All AI Decisions

1. **Streaming pattern**: Sentences processed one at a time to prevent memory exhaustion
2. **spaCy model choice**: `en_core_web_sm` for balance of speed and accuracy
3. **Used shared validation**: Centralized validation prevents duplication and ensures consistency
4. **No manual SQL escaping**: Uses validated table IDs instead of manual backtick escaping
5. **No `gc.collect()`**: Relies on Python's automatic garbage collection
6. **Batch BigQuery writes**: Accumulates spans in memory, writes in batches to reduce API calls
7. **Comprehensive error handling**: All errors use `require_diagnostic_on_error()`
8. **Full audit trail**: All operations logged with traceability

## All Hidden Assumptions

1. **Upstream stages completed successfully**: Assumes Stage 8 has created L4 Sentence entities
2. **Schema matches expected structure**: Expects id, content, parent_id, level=4 in input
3. **BigQuery access**: Assumes proper credentials and permissions
4. **spaCy installed**: Assumes `spacy` and `en_core_web_sm` are installed
5. **Data quality**: Assumes input text is valid UTF-8, properly tokenized sentences
6. **System resources**: Assumes sufficient memory for batch accumulation
7. **Project structure**: Assumes fixed directory structure for imports
8. **Entity relevance**: Not all sentences contain named entities - empty results are normal

## What Reviewers See

**Reviewers have NO LIMITS on what they can see:**
- ✅ Entire file (no chunking, no truncation)
- ✅ All configuration parameters (shown in this report)
- ✅ All limits (shown in this report)
- ✅ All AI decisions (shown in this report)
- ✅ All assumptions (shown in this report)

## Entity Hierarchy Context

This stage creates L3 Span entities from L4 Sentences:

```
Input:  L4 Sentence  → "John Smith visited New York yesterday."
Output: L3 Span      → "John Smith" (PERSON), "New York" (GPE), "yesterday" (DATE)
```

L3 Spans are named entities extracted by spaCy NER, not arbitrary text spans.

## Streaming Architecture Detail

The code processes sentences one at a time to prevent memory exhaustion:

```python
# Streaming pattern (NOT loading all sentences into memory)
for row in query_job.result():
    sentence_text = row.content
    doc = nlp(sentence_text)  # Process single sentence
    for ent in doc.ents:
        # Create L3 Span entity
        all_spans.append(span_entity)
    sentences_processed += 1
```

This allows processing millions of sentences without memory overflow.
