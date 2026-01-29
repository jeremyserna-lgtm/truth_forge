# Schema Mismatch Analysis - entity_unified Table

**Date**: 2026-01-27  
**Critical Issue**: Stage 16 schema does NOT match actual BigQuery table schema

---

## Problem Summary

The actual `entity_unified` table in BigQuery has a **completely different schema** than what Stage 16 is trying to write. This will cause **data insertion failures**.

---

## Actual BigQuery Schema (34 fields)

```
1. entity_id                      STRING          (NULLABLE)
2. level                          INTEGER         (NULLABLE)
3. entity_type                    STRING          (NULLABLE)
4. entity_mode                    STRING          (NULLABLE)
5. parent_id                      STRING          (NULLABLE)
6. source_ids                     STRING          (REPEATED)
7. conversation_id                STRING          (NULLABLE)
8. topic_segment_id               STRING          (NULLABLE)
9. turn_id                        STRING          (NULLABLE)
10. message_id                     STRING          (NULLABLE)
11. sentence_id                    STRING          (NULLABLE)
12. span_id                        STRING          (NULLABLE)
13. word_id                        STRING          (NULLABLE)
14. text                           STRING          (NULLABLE)
15. source_pipeline                STRING          (NULLABLE)
16. source_file                    STRING          (NULLABLE)
17. source_file_path               STRING          (NULLABLE)
18. source_system                  STRING          (NULLABLE)
19. metadata                       JSON            (NULLABLE)
20. created_at                     TIMESTAMP       (NULLABLE)
21. updated_at                     TIMESTAMP       (NULLABLE)
22. ingestion_job_id               STRING          (NULLABLE)
23. ingestion_timestamp            TIMESTAMP       (NULLABLE)
24. validation_status              STRING          (NULLABLE)
25. source_message_timestamp       TIMESTAMP       (NULLABLE)
26. persona                        STRING          (NULLABLE)
27. content_date                   DATE            (NULLABLE)
28. canonical_form                 STRING          (NULLABLE)
29. l7_count                       INTEGER         (NULLABLE)
30. l6_count                       INTEGER         (NULLABLE)
31. l5_count                       INTEGER         (NULLABLE)
32. l4_count                       INTEGER         (NULLABLE)
33. l3_count                       INTEGER         (NULLABLE)
34. l2_count                       INTEGER         (NULLABLE)
```

---

## Stage 16 Expected Schema (36 fields) - WRONG

Stage 16 is trying to write fields that don't exist in the actual table:
- ❌ source_name (doesn't exist)
- ❌ role (doesn't exist)
- ❌ message_type (doesn't exist)
- ❌ message_index (doesn't exist)
- ❌ word_count (doesn't exist)
- ❌ char_count (doesn't exist)
- ❌ model (doesn't exist)
- ❌ cost_usd (doesn't exist)
- ❌ tool_name (doesn't exist)
- ❌ embedding (doesn't exist)
- ❌ embedding_model (doesn't exist)
- ❌ embedding_dimension (doesn't exist)
- ❌ primary_emotion (doesn't exist)
- ❌ primary_emotion_score (doesn't exist)
- ❌ emotions_detected (doesn't exist)
- ❌ keywords (doesn't exist)
- ❌ top_keyword (doesn't exist)
- ❌ keyword_count (doesn't exist)
- ❌ intent (doesn't exist)
- ❌ task_type (doesn't exist)
- ❌ code_languages (doesn't exist)
- ❌ complexity (doesn't exist)
- ❌ has_code_block (doesn't exist)
- ❌ session_id (doesn't exist)
- ❌ timestamp_utc (doesn't exist)
- ❌ fingerprint (doesn't exist)
- ❌ validation_score (doesn't exist)
- ❌ promoted_at (doesn't exist)
- ❌ run_id (doesn't exist)

---

## Actual Table Has Fields Stage 16 Doesn't Provide

- ✅ entity_type (needs to be derived from level)
- ✅ entity_mode (needs to be set)
- ✅ source_ids (REPEATED - needs to be array)
- ✅ conversation_id (needs to be mapped from session_id or derived)
- ✅ topic_segment_id (may not exist)
- ✅ turn_id (needs to be derived)
- ✅ message_id (needs to be mapped from entity_id when level=5)
- ✅ sentence_id (needs to be mapped from entity_id when level=4)
- ✅ span_id (needs to be mapped from entity_id when level=3)
- ✅ word_id (needs to be mapped from entity_id when level=2)
- ✅ source_file (needs to be mapped)
- ✅ source_file_path (needs to be mapped)
- ✅ source_system (needs to be set)
- ✅ metadata (JSON - can store enrichment data here)
- ✅ created_at (needs to be set)
- ✅ updated_at (needs to be set)
- ✅ ingestion_job_id (needs to be set from run_id)
- ✅ ingestion_timestamp (needs to be set)
- ✅ source_message_timestamp (needs to be mapped from timestamp_utc)
- ✅ persona (may not exist)
- ✅ canonical_form (may not exist)
- ✅ l7_count, l6_count, l5_count, l4_count, l3_count, l2_count (count rollups)

---

## Field Mapping Strategy

### Direct Mappings
- `entity_id` → `entity_id`
- `parent_id` → `parent_id`
- `level` → `level`
- `source_pipeline` → `source_pipeline`
- `text` → `text`
- `content_date` → `content_date`
- `validation_status` → `validation_status`

### Derived Fields
- `entity_type` → Derive from level (e.g., "message" for level=5, "sentence" for level=4)
- `entity_mode` → Set to "active" or derive from validation_status
- `conversation_id` → Map from session_id (when level=8) or derive from parent hierarchy
- `message_id` → Map from entity_id when level=5
- `sentence_id` → Map from entity_id when level=4
- `span_id` → Map from entity_id when level=3
- `word_id` → Map from entity_id when level=2
- `turn_id` → Derive from parent hierarchy when level=6
- `source_file` → Map from source_file field
- `source_file_path` → Map from source_file field
- `source_system` → Set to SOURCE_NAME
- `source_ids` → Create array from source identifiers
- `created_at` → Set to current timestamp
- `updated_at` → Set to current timestamp
- `ingestion_job_id` → Map from run_id
- `ingestion_timestamp` → Set to current timestamp
- `source_message_timestamp` → Map from timestamp_utc

### Metadata Storage
All enrichment fields (role, message_type, embeddings, emotions, keywords, intent, etc.) should be stored in the `metadata` JSON field.

### Count Fields
l7_count, l6_count, l5_count, l4_count, l3_count, l2_count should be populated from count rollups in Stage 12.

---

## Required Fixes

1. **Update Stage 16 schema** to match actual table
2. **Map all fields correctly** from Stage 15 to entity_unified
3. **Store enrichment data in metadata JSON** field
4. **Derive hierarchical IDs** (conversation_id, turn_id, message_id, etc.)
5. **Check all stages** to ensure they provide required data

---

## Impact

**This is a CRITICAL issue** - Stage 16 will fail to insert data because the schemas don't match. All stages need to be updated to align with the actual table schema.
