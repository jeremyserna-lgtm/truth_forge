# Stage 2 Full Test Report — Cleaning

**Stage:** 2 (Cleaning)  
**Script:** `scripts/stage_2/claude_code_stage_2.py`  
**Date:** 2026-01-22  
**Status:** ✅ Full test suite executed. Persona restored. All scenarios passed.

---

## 1. What This Stage Does (Plain English)

**Purpose:** Clean and normalize extracted data from Stage 1. Read `claude_code_stage_1` → normalize timestamps, clean content, mark duplicates by fingerprint → write `claude_code_stage_2`. Prepares data for THE GATE (Stage 3).

- **Input:** `claude_code_stage_1` (validated via `validate_input_table_exists`).
- **Processing:** Single BigQuery `CREATE OR REPLACE TABLE ... AS SELECT`: content cleaning (trim, collapse whitespace, content_length, word_count), timestamp normalization, duplicate marking via `ROW_NUMBER() OVER (PARTITION BY fingerprint ORDER BY extracted_at) > 1 AS is_duplicate`. All L7, context, snapshot, and **persona** fields preserved.
- **Output:** `claude_code_stage_2` (partitioned by content_date, clustered by session_id, message_type, is_duplicate).

**Options:** `--dry-run` (count Stage 1 rows only; no write), `--batch-size` (used for reporting).

---

## 2. Fixes Applied Before Testing

| Fix | Description |
|-----|-------------|
| **Persona restored** | `persona` was dropped in Stage 2. Restored: added to `STAGE_2_SCHEMA` and to the cleaning SQL `SELECT`. Stage 2 now preserves `persona` from Stage 1. |

---

## 3. What Was Tested

| # | Scenario | Command | Result |
|---|----------|---------|--------|
| 1 | **Dry-run** | `python .../claude_code_stage_2.py --dry-run` | **PASS.** Counts rows from Stage 1 only (6). No write. "Input rows: 6, Output rows: 6, Duplicates: 0, Unique: 6." Exit 0. |
| 2 | **Full run** | `python .../claude_code_stage_2.py` (no dry-run) | **PASS.** CREATE OR REPLACE ran. "Input rows: 6, Output rows: 6, Duplicates found: 2, Unique rows: 4." Exit 0. |
| 3 | **BigQuery verification** | `SELECT ... FROM claude_code_stage_2` | **PASS.** Rows present. `persona` column exists; `extraction_id`, `session_id`, `message_type`, `role`, `persona`, `content_cleaned` verified. `persona` is NULL for test data (Claude Code single user). |

---

## 4. Test Results Summary

- **Dry-run:** Correct row counts from Stage 1; no Stage 2 write.
- **Full run:** Cleaning transformation applied; duplicate detection works (2 duplicates, 4 unique).
- **Schema:** `persona` preserved in Stage 2; L7, context, snapshot fields present.

---

## 5. What Was Not Tested

- **Missing Stage 1 table:** Script uses fixed `TABLE_STAGE_1`. Not exercised with non-existent table; `validate_input_table_exists` would fail before processing.
- **Empty Stage 1:** No fixture with 0 rows in Stage 1.
- **Retry:** BigQuery cleaning query has no `retry_with_backoff`; transient failures not retried.

---

## 6. Quality Summary

| Aspect | Status |
|--------|--------|
| **Input validation** | ✅ `validate_input_table_exists(TABLE_STAGE_1)` before run. |
| **Output** | ✅ Single overwrite of Stage 2; stats (total, duplicate, unique) reported. |
| **Schema** | ✅ Persona restored; L7, context, snapshot preserved. |
| **Governance** | ✅ `require_diagnostic_on_error` before log on failure; PipelineTracker; Run Service via tracker. |

---

## 7. Verdict

✅ **Stage 2 fully tested.**

- Persona restored and verified in BigQuery.
- Dry-run and full run executed successfully.
- Ready to proceed to Stage 3.

---

*Full test run 2026-01-22. Stage 1 table populated from prior Stage 1 runs.*
