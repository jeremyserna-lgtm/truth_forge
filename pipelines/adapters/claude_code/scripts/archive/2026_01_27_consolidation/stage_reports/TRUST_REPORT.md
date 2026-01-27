> **DEPRECATED**: This document has been superseded.
> - **Deprecated On**: 2026-01-27
> - **Archived On**: 2026-01-27
> - **Reason**: Consolidated duplicate stage reports. Historical snapshots archived to GCS.
> - **Archive Location**: `gs://truth-engine-archive/pipelines/adapters/claude_code/scripts/archive/2026_01_27_consolidation/stage_reports/`
>
> This document has been moved to archive. No redirect stub - file removed from source.

# Trust Report: Stage 9 - L3 Span Creation (Named Entity Recognition)

## What This Stage Does

Stage 9 creates **Level 3 (L3) Span entities** using Named Entity Recognition (NER). It identifies people, places, organizations, dates, and other entities within each sentence.

**In Plain Language**: Stage 9 finds the "important things" in your text. If a sentence says "I met John at Google on Tuesday", it will identify:
- "John" as a PERSON
- "Google" as an ORGANIZATION
- "Tuesday" as a DATE

These become L3 Span entities, linked to their parent sentence (L4).

## SPINE Hierarchy Context

```
L8: Conversation (Stage 5)
  └── L7: Compaction Segment (Stage 5)
      └── L6: Turn (Stage 6)
          └── L5: Message (Stage 7)
              └── L4: Sentence (Stage 8)
                  ├── L3: Span/Entity (THIS STAGE) ← You are here
                  └── L2: Word (Stage 10)
```

**Note**: L3 (Spans) and L2 (Words) are **siblings** - both are children of L4 (Sentence).

## How to Verify It Works

### 1. Run Stage 9
```bash
# Run from project root directory
python3 pipelines/claude_code/scripts/stage_9/claude_code_stage_9.py
```

### 2. Check Output Table
```bash
python3 pipelines/claude_code/scripts/stage_9/verify_stage_9.py
```

### 3. Verify No Errors
```bash
# Check logs for errors (no command-line knowledge required)
python3 pipelines/claude_code/scripts/shared/check_errors.py 9
```

The script will scan the logs and tell you if there are any errors in plain language.

## What Could Go Wrong

### 1. Input Table Missing
**Problem**: Stage 8 (L4 Sentence creation) didn't complete
**Symptom**: `TableNotFoundError` or "stage_8 table not found"
**Impact**: Stage fails, no spans created
**Fix**: Run Stage 8 first, then retry Stage 9

### 2. spaCy Model Not Found
**Problem**: The spaCy NER model isn't installed
**Symptom**: `OSError: Can't find model 'en_core_web_sm'`
**Impact**: Can't identify named entities
**Fix**: Install spaCy model: `python -m spacy download en_core_web_sm`

### 3. No Entities Found (Expected!)
**Problem**: Some sentences have no named entities
**Symptom**: Fewer L3 entities than L4 sentences
**Impact**: This is **normal and expected** - not every sentence has entities
**Fix**: No fix needed. "Hello, how are you?" has no entities, and that's fine.

### 4. BigQuery Quota Exceeded
**Problem**: Daily BigQuery quota limits reached
**Symptom**: `QuotaExceeded` error
**Impact**: Stage fails, no output produced
**Fix**: Wait for quota reset or request quota increase

### 5. Memory Issues
**Problem**: Very long sentences cause memory exhaustion
**Symptom**: `MemoryError` or system slowdown
**Impact**: Stage fails or runs very slowly
**Fix**: Reduce batch size or process fewer sentences at once

## How to Rollback

### If Stage 9 Causes Problems:

**Easy Rollback (No Coding Required):**

Run the universal rollback script:
```bash
python3 pipelines/claude_code/scripts/shared/rollback.py --stage 9 --run-id YOUR_RUN_ID
```

The script will:
1. Show you how many L3 Span records will be deleted
2. Ask for confirmation (type 'yes' to confirm)
3. Delete all Stage 9 data for that run_id
4. Give you clear feedback about what happened

**What this means**: All L3 Span entities created by Stage 9 for that specific run will be removed.

**What to do**: After rollback, you can re-run Stage 9 if needed.

## How to Test It

### Test 1: Dry Run
```bash
python3 pipelines/claude_code/scripts/stage_9/claude_code_stage_9.py --dry-run
```
Should validate and process but not write to output table.

### Test 2: Verify Output
```bash
python3 pipelines/claude_code/scripts/stage_9/verify_stage_9.py
```

### Test 3: Check All Levels Are Correct
The verification script will confirm:
- All records are Level 3 (not any other level)
- All records have a parent_id pointing to a valid L4 Sentence
- All records have the required fields (text, span_label)

## Trust Indicators

**You can trust this if:**
- Output table contains L3 entities (level = 3)
- Each span has a valid parent_id to an L4 Sentence
- No errors in logs
- Span labels are valid NER types (PERSON, ORG, DATE, GPE, etc.)

**You should NOT trust this if:**
- Output table has wrong level (anything other than 3)
- Spans are missing parent links
- Errors occur but aren't logged
- Span labels are invalid or missing

## Entity Types You'll See

spaCy's NER identifies these entity types:
- **PERSON** - Names of people ("John", "Dr. Smith")
- **ORG** - Organizations ("Google", "United Nations")
- **GPE** - Geopolitical entities ("New York", "France")
- **DATE** - Dates ("Tuesday", "January 2024")
- **TIME** - Times ("3pm", "morning")
- **MONEY** - Money amounts ("$50", "five dollars")
- **PERCENT** - Percentages ("50%", "ten percent")
- **PRODUCT** - Products ("iPhone", "Windows")
- And more...

## Questions to Ask

1. **"Did it find entities?"** - Check that some sentences have L3 spans (not all will)
2. **"Are spans linked correctly?"** - Verify parent_id points to valid L4 Sentences
3. **"Are the labels correct?"** - Spot-check that "John" is PERSON, "Google" is ORG, etc.
4. **"Why are there fewer spans than sentences?"** - Normal! Not every sentence has named entities.

## Denormalized Fields

Stage 9 copies these fields from L4 Sentences to L3 Spans (so you can query at span level):
- `role` - "user" or "assistant" (from L5 via L4)
- `persona` - who is speaking (from L5 via L4)
- `l5_type` - "message", "thinking", etc. (from L5 via L4)
- `source_message_timestamp` - when the message was sent (from L5 via L4)

This means you can run queries like "all PERSON entities where role='user'" without joining back to L4 or L5.
