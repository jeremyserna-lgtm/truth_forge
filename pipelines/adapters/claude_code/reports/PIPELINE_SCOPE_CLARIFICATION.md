# Pipeline Scope Clarification

**Date:** 2026-01-22  
**Status:** ✅ **SCOPE CLARIFIED - ENRICHMENT FIELDS REMOVED**

---

## Pipeline Scope

This pipeline **ONLY** does:

1. ✅ **L2-L8 Spine Processing**
   - L8: Conversations (by session_id)
   - L6: Turns (full interaction rounds)
   - L5: Messages (user/assistant/thinking as separate entities)
   - L4: Sentences (from spaCy sentence segmentation)
   - L3: Spans/NER (named entities from spaCy)
   - L2: Words (tokens from spaCy)

2. ✅ **Text Spelling Correction (Stage 4)**
   - LLM text correction for USER messages ONLY
   - Purpose: Ensure spaCy can process text correctly
   - Uses Gemini CLI (subscription) with API fallback
   - Corrects spelling and grammar, preserves meaning
   - Assistant messages are already clean - not corrected

---

## What This Pipeline Does NOT Do

❌ **NO Enrichments:**
- NO embeddings generation
- NO emotion detection
- NO keyword extraction
- NO intent classification
- NO sentiment analysis
- NO topic modeling
- NO code language detection
- NO complexity analysis

**Enrichments are SEPARATE** and run in a different pipeline AFTER spine processing.

---

## Changes Made

### ✅ Removed Enrichment Fields from Stage 16 Schema

**Removed fields:**
- `embedding`, `embedding_model`, `embedding_dimension`
- `primary_emotion`, `primary_emotion_score`, `emotions_detected`
- `keywords`, `top_keyword`, `keyword_count`
- `intent`, `task_type`, `code_languages`, `complexity`, `has_code_block`

**Kept fields:**
- All spine structure fields (L2-L8 hierarchy)
- Source tracking fields
- Text correction fields (from Stage 4)
- Validation fields (from Stage 15)
- Message metadata (type, index, word_count, char_count, model, cost, tool_name)

---

## Stage-by-Stage Processing

| Stage | What It Does | Enrichments? |
|-------|--------------|--------------|
| **Stage 0** | Discovery - finds all data in source files | ❌ No |
| **Stage 1** | Extraction - extracts raw messages from JSONL | ❌ No |
| **Stage 2** | Normalization - cleans and normalizes data | ❌ No |
| **Stage 3** | THE GATE - generates entity IDs | ❌ No |
| **Stage 4** | **Text Correction** - LLM spelling/grammar correction for USER messages | ✅ **YES** (spelling only) |
| **Stage 5** | Creates L8 Conversation entities | ❌ No |
| **Stage 6** | Creates L6 Turn entities | ❌ No |
| **Stage 7** | Creates L5 Message entities | ❌ No |
| **Stage 8** | Creates L4 Sentence entities (spaCy) | ❌ No |
| **Stage 9** | Creates L3 Span entities (spaCy NER) | ❌ No |
| **Stage 10** | Creates L2 Word entities (spaCy tokens) | ❌ No |
| **Stage 11** | Validates parent-child links | ❌ No |
| **Stage 12** | Count rollups (denormalization) | ❌ No |
| **Stage 13** | Pre-promotion validation | ❌ No |
| **Stage 14** | Promotes to entity_unified (structural) | ❌ No |
| **Stage 15** | Final validation | ❌ No |
| **Stage 16** | Promotes validated entities to entity_unified | ❌ No |

---

## Text Correction Details (Stage 4)

**Purpose:** Ensure spaCy can process text correctly

**What gets corrected:**
- ✅ USER messages only (role='user' or role='human')
- ❌ Assistant messages (already clean, not corrected)

**How it works:**
1. Reads messages from Stage 3
2. For USER messages: Sends to Gemini LLM for spelling/grammar correction
3. For ASSISTANT messages: Uses original text (no correction)
4. Stores corrected text in `text` field
5. Original text preserved in metadata if needed

**LLM Configuration:**
- Primary: Gemini CLI (subscription-based, free)
- Fallback: Gemini API (gemini-2.0-flash-lite)
- API key: From GCP Secret Manager
- Batch processing: Small batches (10-25 messages) to prevent hallucination
- Cost tracking: Integrated with cost service

---

## Architecture

```
Source Data (JSONL)
    ↓
Stage 0: Discovery
    ↓
Stage 1: Extraction
    ↓
Stage 2: Normalization
    ↓
Stage 3: THE GATE (ID generation)
    ↓
Stage 4: Text Correction (LLM spelling/grammar for USER messages)
    ↓
Stage 5: L8 Conversations
    ↓
Stage 6: L6 Turns
    ↓
Stage 7: L5 Messages
    ↓
Stage 8: L4 Sentences (spaCy)
    ↓
Stage 9: L3 Spans (spaCy NER)
    ↓
Stage 10: L2 Words (spaCy tokens)
    ↓
Stage 11: Validation
    ↓
Stage 12: Count Rollups
    ↓
Stage 13: Pre-Promotion Validation
    ↓
Stage 14: Promotion to entity_unified
    ↓
Stage 15: Final Validation
    ↓
Stage 16: Promotion to entity_unified (validated)
    ↓
entity_unified (L2-L8 spine, text-corrected)
```

**After this pipeline:**
- Enrichments can be added in a SEPARATE pipeline
- Enrichments join to entity_unified via entity_id
- Spine structure is complete and ready for enrichment

---

## Conclusion

✅ **Pipeline scope is now clear:**
- ONLY L2-L8 spine processing
- ONLY text spelling correction (for spaCy)
- NO enrichments (embeddings, emotions, keywords, etc.)

✅ **Enrichment fields removed from Stage 16 schema**

✅ **Pipeline is focused and clean**
