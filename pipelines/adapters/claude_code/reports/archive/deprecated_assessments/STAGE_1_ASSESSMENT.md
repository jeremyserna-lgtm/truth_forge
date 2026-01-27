# Stage 1 Assessment — Extraction

**Stage:** 1 (Extraction)  
**Script:** `scripts/stage_1/claude_code_stage_1.py`  
**Date:** 2026-01-22  
**Status:** Assessment complete. Gaps and recommendations below.

---

## 1. What This Stage Does (Plain English)

**Purpose:** Extract structured message data from raw Claude Code JSONL exports and load it into BigQuery (`claude_code_stage_1`). Stage 1 is HOLD₁ (JSONL files) → AGENT (parser) → HOLD₂ (BigQuery).

- **Input:** JSONL session files from `--source-dir` (default `~/.claude/projects`) **or** manifest-driven via `--manifest` (Stage 0 output). When `--manifest` is used, uses `source.path` and requires `go_no_go` = GO.
- **Processing:** Discovers `.jsonl` files, parses each line as JSON, maps to a flat schema. Handles thinking blocks (yields separate records per block), tool_use/tool_result, summary (session_id/model), and L7 detection fields (uuid, parent_uuid, logical_parent_uuid, subtype, compact_metadata, is_compact_summary). Writes `snapshot_data` / `is_snapshot` for file-history-snapshot messages.
- **Output:** Batched load to `claude_code_stage_1` via `load_rows_to_table` (no streaming). Creates table if missing (partitioned by `content_date`, clustered by `session_id`, `message_type`).

**Key schema fields:** extraction_id, session_id, message_index, message_type, role, persona, content, timestamp, model, cost_usd, tool_*, source_file, content_date, fingerprint, extracted_at, run_id; L7 fields (uuid, parent_uuid, logical_parent_uuid, subtype, compact_metadata, is_compact_summary); context (version, git_branch, cwd, slug, is_sidechain); snapshot_data, is_snapshot.

---

## 2. What Was Reviewed (Code + Structure)

| # | Area | What I Checked | Result |
|---|------|----------------|--------|
| 1 | **Service integrations** | PipelineTracker, Run Service, Identity, Governance | Uses PipelineTracker ✅; Run Service via PipelineTracker ✅. No entity IDs generated (extraction only) → Identity N/A ✅. Uses `require_diagnostic_on_error` ✅. |
| 2 | **Logging** | get_logger, run_id, ensure_stage_logging_context | Uses `logging_bridge` (get_logger, get_current_run_id, ensure_stage_logging_context) ✅. Structured events: stage_started, processing_file, stage_complete, stage_failed ✅. |
| 3 | **Governance** | require_diagnostic_on_error usage | Used in `create_stage_1_table` on exception ✅. Used in main `except` for stage failure ✅. |
| 4 | **Input validation** | source_dir, manifest | `validate_input_source_dir`: exists, is_dir ✅. `load_manifest_and_source_dir`: manifest exists, has source/go_no_go, go_no_go starts with GO, source.path present ✅. |
| 5 | **Manifest-driven mode** | --manifest path, manifest contract | Loads manifest, validates go_no_go, uses source.path as source_dir ✅. Aligns with discovery manifest schema ✅. |
| 6 | **Batch loading** | load_rows_to_table, no streaming | Uses `bq_client.load_rows_to_table` (batch) ✅. OPERATIONAL_STANDARDS: no streaming ✅. |
| 7 | **JSON → BigQuery** | compact_metadata, snapshot_data | `compact_metadata`: converted to JSON string in `load_to_bigquery` when dict ✅. `snapshot_data`: stored via `json.dumps(msg.get("snapshot"))` ✅. |
| 8 | **Error handling** | main except, create_stage_1_table | main: logs stage_failed, calls `require_diagnostic_on_error`, updates tracker items_failed, returns 1 ✅. create_stage_1_table: require_diagnostic_on_error then raise ✅. |
| 9 | **Hashlib usage** | fingerprint, extraction_id, session_id | Used for fingerprint (dedup), extraction_id, `_generate_session_id`. These are **not** spine entity IDs; they are extraction/session identifiers. Acceptable as-is ✅. No Primitive.identity needed here. |
| 10 | **retry_with_backoff** | Import vs usage | Imported from shared ✅. **Not used** ⚠️. BigQuery load has no explicit retry in Stage 1. |
| 11 | **require_diagnostic_on_error order** | main except block | **Fixed.** Main `except` now calls `require_diagnostic_on_error` before `logger.error`, matching Stage 0. |
| 12 | **Thinking blocks** | Separate L5-ready records | Assistant list content: iterates blocks, yields separate records per thinking/text block, sets message_type accordingly ✅. |
| 13 | **L7 / snapshot fields** | Schema and population | Schema includes uuid, parent_uuid, logical_parent_uuid, subtype, compact_metadata, is_compact_summary, snapshot_data, is_snapshot ✅. Populated from raw JSON ✅. |
| 14 | **Dry-run** | --dry-run behaviour | Parses files, batches in memory, `load_to_bigquery(..., dry_run=True)` skips write, logs "dry_run_would_load" ✅. |
| 15 | **Limit-files** | --limit-files | Truncates `session_files` before processing ✅. |

---

## 3. Gaps and Recommendations

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| **retry_with_backoff unused** | Low | Use `retry_with_backoff` around `load_to_bigquery` (or around the BigQuery client call inside it) for transient BigQuery failures. Alternatively, remove the import if retry is handled inside `get_bigquery_client` / `load_rows_to_table`. |
| **require_diagnostic_on_error order** | ~~Low~~ Done | In main `except`, call `require_diagnostic_on_error` before `logger.error`. **Applied.** |
| **Memory / large runs** | Low | For very large `--source-dir`, batching limits memory per load but all parsed records for a batch are in memory. Consider documenting recommended batch_size or source scale limits. |
| **Stage 0 → Stage 1 contract** | Info | When using `--manifest`, Stage 1 correctly relies on Stage 0’s manifest. Ensure Stage 0 always writes `source.path` and `go_no_go` as expected. |

---

## 4. Quality Summary

| Aspect | Assessment |
|--------|------------|
| **Structure** | ✅ Aligned with Stage 0 and other stages: PipelineTracker, run_id, structured logging, governance. |
| **Input validation** | ✅ Source dir and manifest validated; manifest-driven path and go_no_go enforced. |
| **Output** | ✅ Batch load to BigQuery; schema includes L7, context, and snapshot fields. |
| **Error handling** | ✅ Diagnostic required on create-table and stage failure; minor reorder suggested. |
| **Identity / Run / Relationship** | ✅ No spine entity IDs; Run via PipelineTracker. Nothing to add for this stage. |
| **Operational standards** | ✅ Batch load, no streaming. Optional: add retry around BigQuery load. |

---

## 5. What Was Not Run (Tests)

- **No automated or manual test runs** were executed for this assessment. The above is based on **code and structure review** only.
- **Suggested tests** (when you run them):
  1. `--dry-run` with `--source-dir` and with `--manifest` (Stage 0 manifest).
  2. `--manifest` with NO-GO manifest → must fail with clear error.
  3. `--manifest` with missing `source.path` → must fail.
  4. Real `--source-dir` run: verify row counts, presence of L7/snapshot columns, thinking blocks as separate rows.
  5. `--limit-files 1` and `--limit-files 0` to check boundary behaviour.
  6. Invalid JSONL lines: expect parse warnings, no crash; check that `load_to_bigquery` still runs for valid records.

---

## 6. Conclusion

Stage 1 is **structurally sound** and aligned with Stage 0 and pipeline conventions. **(1)** `require_diagnostic_on_error` is now called before logging in the main `except`. **(2)** Optional: use `retry_with_backoff` around BigQuery load or document that retry is handled elsewhere. Stage 1 is **ready to move on from** for Stage 2.

---

*Assessment produced from code review. No test executions performed.*
