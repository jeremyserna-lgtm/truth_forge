# Stage 14 vs Stage 16 Schema Resolution

## Problem
Stage 14 and Stage 16 both write to `entity_unified` but have incompatible schemas:
- **Stage 14:** Promotes structural entities (L8, L6, L5, L4, L3, L2) with structural schema
- **Stage 16:** Tries to promote enriched entities but skips existing ones, so enrichments never get added

## Current Architecture
1. **Stage 14:** Uses MERGE to upsert structural entities to `entity_unified`
2. **Stage 15:** Validates entities
3. **Stage 16:** Skips entities that already exist (from Stage 14), so enrichments are never added

## Solution
**Stage 16 should use MERGE to UPDATE existing entities with enrichment fields**, not skip them.

## Required Changes
1. **Make Stage 16's schema a SUPERSET of Stage 14's schema** (include all Stage 14 fields + enrichment fields)
2. **Change Stage 16 from `load_rows_to_table` to MERGE** to UPDATE existing entities
3. **Ensure field compatibility** between Stage 14 and Stage 16

## Field Mapping

### Stage 14 Fields (must be in Stage 16):
- entity_id, level, source_pipeline, text, content_date
- fingerprint, source_file, extracted_at, run_id
- parent_id, conversation_id, turn_id, message_id, sentence_id
- word_id, span_id, span_label, role, persona, l5_type, source_message_timestamp
- l6_count, l5_count, l4_count, l3_count, l2_count
- promoted_at

### Stage 16 Enrichment Fields (add to Stage 14 schema):
- message_type, message_index, word_count, char_count
- model, cost_usd, tool_name
- embedding, embedding_model, embedding_dimension
- primary_emotion, emotions_detected, keywords, intent, task_type
- code_languages, complexity, has_code_block
- session_id, timestamp_utc
- validation_status, validation_score

## Implementation Plan
1. Add missing Stage 14 fields to Stage 16 schema
2. Add missing Stage 16 enrichment fields to Stage 14 schema (optional - can be NULL)
3. Change Stage 16 to use MERGE instead of skipping duplicates
4. Test that enrichments are properly added to existing entities
