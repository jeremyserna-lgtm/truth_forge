# Stage 4 Assessment — Staging

**Stage:** 4 (Staging)  
**Script:** `scripts/stage_4/claude_code_stage_4.py`  
**Date:** 2026-01-22  
**Status:** Assessment complete. Persona restored. Partition/cluster fix applied. Full tests run — see `STAGE_4_TEST_REPORT.md`.

---

## 1. What This Stage Does (Plain English)

**Purpose:** Prepare data structure for SPINE entity creation. Read `claude_code_stage_3` → transform to SPINE format (adds `source_name`, `source_pipeline`, `level`, `parent_id`, `metadata`) → write `claude_code_stage_4`.

- **Input:** `claude_code_stage_3` (validated via `validate_input_table_exists`).
- **Processing:** Single BigQuery `CREATE OR REPLACE TABLE ... AS SELECT` that:
  - Adds SPINE fields: `source_name`, `source_pipeline`, `level` (L5 = Message), `parent_id` (NULL for L5), `metadata` (JSON)
  - Maps `content_cleaned` → `text`
  - Preserves: `entity_id`, `session_id`, `message_index`, `message_type`, `role`, **persona**, `content_length`, `word_count`, `model`, `cost_usd`, `tool_*`, `source_file`, `content_date`, `timestamp_utc`, `fingerprint`, `run_id`
- **Output:** `claude_code_stage_4` (partitioned by `content_date`, clustered by `source_name`, `level`, `session_id`).

**Options:** `--dry-run` (count rows only; no write).

**Note:** Stage 4 docstring mentions LLM text correction for user messages (TODO). Currently does schema transformation only.

---

## 2. What Was Reviewed (Code + Structure)

| # | Area | What I Checked | Result |
|---|------|----------------|--------|
| 1 | **Service integrations** | PipelineTracker, Run Service, Governance | Uses PipelineTracker ✅; Run Service via tracker ✅. `require_diagnostic_on_error` ✅. |
| 2 | **Logging** | get_logger, run_id, ensure_stage_logging_context | Uses logging_bridge ✅. Events: stage_started, staging_transformation_start, stage_complete, stage_failed ✅. |
| 3 | **Governance** | require_diagnostic_on_error usage | Used in `create_stage_4_table` on exception ✅. Used in main `except` for stage failure ✅. Order: diagnostic before logger.error ✅. |
| 4 | **Input validation** | Stage 3 table | `validate_input_table_exists(bq.client, TABLE_STAGE_3)` before processing ✅. |
| 5 | **Schema** | Stage 4 vs Stage 3 | Adds SPINE fields (source_name, source_pipeline, level, parent_id, metadata). Preserves entity_id, session_id, message_*, role, **persona**, content_length, word_count, model, cost, tool_*, source_file, content_date, timestamp_utc, fingerprint, run_id ✅. Maps content_cleaned → text ✅. |
| 6 | **SQL transform** | CREATE OR REPLACE, PARTITION, CLUSTER | **Fixed.** Now includes `PARTITION BY content_date CLUSTER BY source_name, level, session_id` to match `create_stage_4_table` ✅. |
| 7 | **Error handling** | main except, create_stage_4_table | Both use require_diagnostic_on_error; main order fixed ✅. |
| 8 | **Persona** | Field preservation | **Restored.** `persona` added to schema, SELECT query, and metadata STRUCT ✅. |

---

## 3. Gaps and Recommendations

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| **LLM text correction** | Info | Docstring mentions LLM correction for user messages (typos). Not implemented. If needed for spaCy accuracy, add before schema transformation. |
| **retry_with_backoff** | Low | BigQuery query has no explicit retry. Optional: wrap in `retry_with_backoff` for transient failures. |

---

## 4. Quality Summary

| Aspect | Assessment |
|--------|------------|
| **Structure** | ✅ Aligned with Stage 0/1/2/3: PipelineTracker, run_id, structured logging, governance. |
| **Input validation** | ✅ Validates Stage 3 table exists before running. |
| **Output** | ✅ Single overwrite of Stage 4; SPINE fields added; persona preserved. |
| **Error handling** | ✅ Diagnostic on create-table and stage failure; order consistent. |
| **Partition/cluster** | ✅ Fixed to match table creation spec. |

---

## 5. Tests

- **Full tests executed.** See `STAGE_4_TEST_REPORT.md` for dry-run, full run, and BigQuery verification (including `persona`).

---

## 6. Conclusion

Stage 4 is **structurally sound** and consistent with Stage 0/1/2/3. **Persona** is restored and preserved. Partition/cluster spec fixed. **Ready to proceed to Stage 5.**

---

*Assessment from code review + full tests. Persona restored. Partition/cluster fix applied.*
