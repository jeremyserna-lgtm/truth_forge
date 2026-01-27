# Stage 2 Assessment — Cleaning

**Stage:** 2 (Cleaning)  
**Script:** `scripts/stage_2/claude_code_stage_2.py`  
**Date:** 2026-01-22  
**Status:** Assessment complete. Diagnostic order fixed. **Persona restored.** Full tests run — see `STAGE_2_TEST_REPORT.md`.

---

## 1. What This Stage Does (Plain English)

**Purpose:** Clean and normalize extracted data from Stage 1. Read `claude_code_stage_1` → normalize timestamps, clean content, mark duplicates by fingerprint → write `claude_code_stage_2`. Prepares data for THE GATE (Stage 3).

- **Input:** `claude_code_stage_1` (validated via `validate_input_table_exists`).
- **Processing:** Single BigQuery `CREATE OR REPLACE TABLE ... AS SELECT` with:
  - Content cleaning (trim, collapse whitespace, content_length, word_count)
  - Timestamp kept as-is (timestamp_utc = timestamp; normalization is minimal here)
  - Duplicates: `ROW_NUMBER() OVER (PARTITION BY fingerprint ORDER BY extracted_at) > 1 AS is_duplicate`
  - All L7, context, snapshot fields preserved (uuid, parent_uuid, logical_parent_uuid, subtype, compact_metadata, is_compact_summary, version, git_branch, cwd, slug, is_sidechain, snapshot_data, is_snapshot)
- **Output:** `claude_code_stage_2` (partitioned by content_date, clustered by session_id, message_type, is_duplicate).

**Dry-run:** Counts rows from stage_1 only; no write.

---

## 2. What Was Reviewed (Code + Structure)

| # | Area | What I Checked | Result |
|---|------|----------------|--------|
| 1 | **Service integrations** | PipelineTracker, Run Service, Governance | PipelineTracker ✅; Run Service via tracker ✅. No entity IDs → Identity N/A ✅. `require_diagnostic_on_error` ✅. |
| 2 | **Logging** | get_logger, run_id, ensure_stage_logging_context | Uses logging_bridge ✅. Events: stage_started, cleaning_transformation_start, stage_complete, stage_failed ✅. |
| 3 | **Governance** | require_diagnostic_on_error | Used in `create_stage_2_table` on exception ✅. Main except: **fixed** — now calls diagnostic **before** logger.error ✅. |
| 4 | **Input validation** | Stage 1 table | `validate_input_table_exists(bq.client, TABLE_STAGE_1)` before processing ✅. |
| 5 | **Schema** | Stage 2 vs Stage 1 | Preserves extraction_id, session_id, message_*, role, **persona**, content, content_cleaned, content_length, word_count, timestamps, model, cost, tool_*, source_file, content_date, fingerprint, is_duplicate, extracted_at, cleaned_at, run_id; all L7, context, snapshot fields ✅. **Persona** restored and preserved. |
| 6 | **SQL transform** | CREATE OR REPLACE, PARTITION, CLUSTER | Matches `create_stage_2_table` spec ✅. Docstring notes partition/cluster alignment ✅. |
| 7 | **Error handling** | main except, create_stage_2_table | Both use require_diagnostic_on_error; main order fixed ✅. |
| 8 | **retry_with_backoff** | BigQuery job | Not used. Single query job; retry could wrap it. Low priority. |

---

## 3. Gaps and Recommendations

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| **require_diagnostic_on_error order** | ~~Low~~ Done | Main except now calls diagnostic before log. **Applied.** |
| **persona dropped** | ~~Low~~ Done | **Restored.** `persona` added to Stage 2 schema and cleaning SQL. Preserved from Stage 1. |
| **retry on query job** | Low | Optional: wrap `client.query(cleaning_query)` in `retry_with_backoff` for transient BigQuery failures. |

---

## 4. Quality Summary

| Aspect | Assessment |
|--------|------------|
| **Structure** | ✅ Aligned with Stage 0/1: PipelineTracker, run_id, structured logging, governance. |
| **Input validation** | ✅ Validates Stage 1 table exists before running. |
| **Output** | ✅ Single overwrite of Stage 2; stats (total, duplicate, unique) reported. |
| **Error handling** | ✅ Diagnostic on create-table and stage failure; order consistent. |
| **Schema / L7** | ✅ Preserves L7, context, snapshot fields for downstream. |

---

## 5. Tests

- **Full tests executed.** See `STAGE_2_TEST_REPORT.md` for dry-run, full run, and BigQuery verification (including `persona`).

---

## 6. Conclusion

Stage 2 is **structurally sound** and consistent with Stage 0/1. **Persona** is restored and preserved. The main `except` calls `require_diagnostic_on_error` before logging. **Ready to proceed to Stage 3.**
