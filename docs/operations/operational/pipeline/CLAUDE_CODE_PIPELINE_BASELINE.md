# Claude Code Parser Pipeline Baseline

**Status (2025-10-27):** Cloud-run ready parser with governance instrumentation, serving as the exemplar for unified parser policy.

This document captures the full end-to-end behaviour of the Claude Code conversation pipeline as implemented today. Use it as the authoritative baseline when aligning other parsers to the shared policy surface.

---

## Snapshot
- **Primary entrypoint:** `conversation_pipeline/parsers/ai_agents/claude_code_parser/parser.py`
- **Orchestration:** `conversation_pipeline/scripts/ingest_conversations.py`
- **Shared guardrails:** `conversation_pipeline/parsers/shared/bootstrap.py`, `conversation_pipeline/parsers/shared/policy_guards.py`, `conversation_pipeline/parsers/shared/utils.py`
- **Default sinks:** BigQuery dataset `spine` (`word`, `span`, `sentence`, `message`, `turn`, `topic_segment`, `conversation`)
- **Governance logs:** BigQuery dataset `governance` (`audit_trail`, `data_quality_checks`, `process_costs`)

---

## Flow Overview

1. **Staging and configuration**
   - A JSON config feeds the ingestion orchestrator (`ingest_conversations.py`). Each entry names a parser, GCS `input_uri`, optional manifest, batch sizing, and overrides (project/dataset, BigQuery toggles, cache policy).
   - The orchestrator resolves the parser path (`PARSER_PATHS`), builds a Python invocation, ensures a local staging directory, and records run metadata (run id, staging path) on the config node for downstream audit.

2. **Policy bootstrap**
   - Every parser call flows through `prepare_runtime` which:
     - Enforces cloud execution context (`ensure_execution_context`) unless `--allow-local-run` is set.
     - Rejects non-GCS inputs (`require_gcs_uri`) and materializes them into a staging directory (`materialize_input`).
     - Keeps cache-first deduplication enabled (`enforce_cache_first`) unless explicitly overridden under a local waiver.
     - Sets up a run-scoped `PolicyContext`, structured heartbeat emitter, and logger.

3. **Parsing and identity**
   - `ClaudeCodeParser` loads each staged JSONL file, aggregates records by `sessionId`, validates required fields, and parses message content into normalized text.
   - Canonical IDs come from the identity system:
     - Conversations: `generate_conversation_id` (`conv:claude_code:<hash>` format) plus `register_identity`.
     - Messages: `generate_message_id` (stable compound id) plus `register_identity`.
   - Each conversation produces hierarchical spine layers via shared utilities: `word`, `span`, `sentence`, `turn`, `topic_segment`, `message`, `conversation`.
   - Metadata added per conversation (`model`, `session_id`, `message_count`, platform/model identity mapping, normalized model id).

4. **Deduplication and cache policy**
   - `compute_content_hash` derives a SHA256 over ordered speaker/text pairs.
   - `conversation_exists_cached` checks BigQuery (`spine.conversation`) for an existing row with the same id plus hash, memoized per run. Cache hits trigger a skip and heartbeat update.

5. **BigQuery persistence**
   - When `--enable-bigquery-output` (default), the parser writes batches to BigQuery via `batch_insert_to_bigquery`.
  - Table order honours dependencies (`word -> span -> sentence -> message -> turn -> topic_segment -> conversation`).
   - Each conversation row receives `content_hash` and `run_id` before insert.

6. **Governance instrumentation**
   - On success, the parser emits three governance records:
     - `log_governance_audit_trail`: run metadata, counts, duration, run id.
     - `log_governance_data_quality`: dedupe outcomes (processed versus skipped) plus rate.
     - `log_governance_process_costs`: throughput statistics, cache metrics, duration.
   - Heartbeats are emitted via the shared `HeartbeatEmitter` and also surfaced through `_central_services.log_service` (ingest orchestrator).

7. **Optional instrumentation**
   - `--track-performance` wraps parsing in `ModelPerformanceTracker`, logging reflections and Copilot perspective notes.
   - Dry runs (`--dry-run`) summarise staged artifacts without processing.

---

## Detailed Stage Notes

### 1. Staging and invocation (`conversation_pipeline/scripts/ingest_conversations.py`)
- Resolves parser binaries, enforces manifest presence when supplied, and provisions a staging directory per parser entry (defaults to `tmp_output/<parser>`).
- CLI surface: `--config`, `--default-staging`, `--heartbeat`, `--batch-size`.
- Each parser entry in the config supports overrides (`bigquery_project`, `bigquery_dataset`, `heartbeat`, `batch_size`, `allow_local_run`, `enable_bigquery_output`, `governance_logging`, `cache_first`, `dry_run`, `log_level`).

### 2. Guardrail bootstrap (`conversation_pipeline/parsers/shared/bootstrap.py`, `policy_guards.py`)
- `PolicyContext` carries parser name, run id, and override flag through the lifecycle.
- Guard functions raise `PolicyViolation` unless `--allow-local-run` is present; orchestrator propagates exit code and structured log events.
- `materialize_input` downloads objects from GCS using the Python storage client, recreating prefix structure under the staging directory.
- `HeartbeatEmitter` enforces five-second plus cadence, merges progress metrics into structured log payloads, and prevents log spam with interval gating.

### 3. Parsing logic (`conversation_pipeline/parsers/ai_agents/claude_code_parser/parser.py`)
- `ClaudeCodeParser` inherits `BaseParser` and consumes `ClaudeConfig` (batch size, timezone-aware timestamps).
- Message validation covers presence of `uuid`, `timestamp`, `message.role`, and ensures timestamps parse.
- Text extraction flattens the Claude Code `content` array; token usage metadata (when present) is appended under a `--- Usage ---` divider.
- Hierarchical layers leverage shared extractors (`extract_words`, `extract_spans`, `extract_sentences`, `extract_turns`, `extract_topic_segments`).
- Identity mapping uses `identity_for('claude_code', model)` to align model, company, product, and platform ids.
- No enrichment is performed at this stage; embedding fields are explicitly removed before insert.

### 4. Execution loop and governance
- Loader iterates discovered JSONL files, aggregates conversation batches, enforces deduplication, parses, and writes.
- Errors per conversation increment an error counter and are logged; the process continues unless a fatal error arises while loading staged files.
- Final summary logs counts, errors, and duration; process returns `0` when error-free.
- Audit and logging routines run only when `governance_logging` is enabled (default true).

### 5. Optional features
- `--allow-local-run` bypasses execution-context and cache requirements, intended for smoke tests.
- `--disable-bigquery-output` routes parsed data exclusively to stdout or logs (no disk artifact currently produced).
- `--manifest` is retained on the parser entry for downstream auditing but not currently parsed within the Claude parser.

---

## Data Contracts

| Table | Cardinality | Key fields | Notes |
| ----- | ----------- | ---------- | ----- |
| `spine.conversation` | 1 per session | `conversation_id`, `run_id`, `content_hash` | Metadata includes platform and model ids, counts, timestamps. |
| `spine.message` | 1 per message | `message_id`, `conversation_id`, `speaker`, `timestamp` | Text flattened, usage info appended inline; source metadata currently disabled. |
| `spine.turn` | roughly messages / 2 | `turn_id`, `conversation_id`, `speaker_sequence` | Derived alternating runs of user and assistant dialogue. |
| `spine.topic_segment` | variable | `topic_segment_id`, `conversation_id` | Produced by heuristic segmentation in shared utils. |
| `spine.sentence` | sentences | `sentence_id`, `conversation_id`, `message_id` | Extracted via shared NLP heuristics (TextBlob). |
| `spine.span` | spans | `span_id`, `conversation_id`, `message_id` | Word-span grouping used by sentiment and entity enrichers. |
| `spine.word` | tokens | `word_id`, `conversation_id`, `message_id` | Basis for downstream statistical enrichments. |

Governance tables capture run metadata; each insert is a single record keyed by UUID (`audit_id`, `check_id`, `process_id`).

---

## CLI Surface (cloud policy aligned)

| Flag | Default | Purpose |
| ---- | ------- | ------- |
| `--input-uri` | required | GCS prefix containing staged Claude Code JSONL exports. |
| `--staging-dir` | `/tmp/parser_staging` | Local scratch path used by `materialize_input`. |
| `--run-id` | autogenerated (`parser_name:epoch`) | Propagated to governance logs and conversation rows. |
| `--allow-local-run` | off | Bypasses execution-context and cache policies for local testing. |
| `--batch-size` | `50` | Controls per-batch aggregation during parsing. |
| `--heartbeat-interval` | `30` | Seconds between heartbeats (minimum five enforced). |
| `--cache-first` and `--no-cache-first` | on | Deduplication enforcement; disabling requires local override. |
| `--enable-bigquery-output` and `--disable-bigquery-output` | on | Governs BigQuery writes. |
| `--bigquery-project` | `flash-clover-464719-g1` | Target project for spine and governance tables. |
| `--bigquery-dataset` | `spine` | Target dataset for core tables. |
| `--governance-logging` and `--disable-governance-logging` | on | Enables audit, data-quality, and process-cost logging. |
| `--dry-run` | off | Summarises staged files and exits. |
| `--track-performance` | off | Enables ModelPerformanceTracker instrumentation. |

---

## Governance Coverage
- **Execution context:** `ensure_execution_context` enforces Cloud Run or Cloud Build environment variables; local runs must declare overrides.
- **Input source control:** `require_gcs_uri` ensures all production runs originate from GCS staging with manifest-driven provenance.
- **Deduplication:** `compute_content_hash` plus `conversation_exists_cached` enforce idempotent loads into `spine`.
- **Identity integrity:** Conversations and messages obtain deterministic IDs; `validate_identity_coverage` guards against missing keys.
- **Audit and quality logs:** All runs emit audit, dedupe-quality, and process-cost records into `governance` tables (unless explicitly disabled).
- **Heartbeat monitoring:** Structured heartbeats expose processed, skipped, and error counts plus file progress for operational dashboards.
- **Central logging:** Orchestrator pipes stdout through `_central_services.log_service`, standardising log format and retaining run metadata.

---

## Known Gaps and Follow-ups
1. **Config alignment:** `ClaudeCodeParser` still pulls `DEFAULT_CONFIGS['claude']` instead of a distinct `claude_code` entry; consider adding a dedicated config to avoid cross-parser side effects.
2. **Attachment capture:** Attachment and tool outputs are not yet emitted (config `include_thinking` is false and attachments limited to metadata); confirm policy stance on including side-channel artefacts.
3. **Manifest consumption:** `--manifest` is recorded but unused inside the parser; governance baseline may want manifest validation (checksum, counts).
4. **Retry and backoff:** BigQuery inserts are single-shot; introduce retries or exponential backoff and partial failure reporting for robustness.
5. **Schema drift detection:** Parser trusts BigQuery schema; add automated schema validation against `platform_identity_mapping` or a local schema definition.
6. **Governance table existence:** Logging assumes `governance.*` tables exist; missing tables currently log errors but do not fail the run. Decide if policy requires hard failure.
7. **Telemetry:** Heartbeat currently logs to console or central logger; consider emitting structured metrics via Cloud Logging or Pub/Sub for fleet monitoring.

---

## Related Artifacts
- `docs/pipeline/CLAUDE_CODE_PARSING_EXPLAINED.md` — raw format deep dive.
- `docs/pipeline/CLAUDE_CODE_PIPELINE_QUICKSTART.md` — legacy local-run instructions.
- `conversation_pipeline/docs/PARSER_EXECUTION_STANDARDS.md` — fleet-wide heartbeat and CLI standard (this parser complies).
- `conversation_pipeline/docs/PARSER_CLOUD_MIGRATION_AUDIT.md` — prior audit of cloud compliance tasks.

Use this baseline to evaluate other parsers (Codex, Copilot, Gemini) and converge on a common policy-compliant implementation surface.
