# Pipeline Status Digest — 2025-10-30

**Scope**: conversational ingest (ChatGPT/Claude/Gemini web), watcher hand-offs, document ingest (document_service), and downstream Cloud Run deployments. This snapshot captures the fixes incorporated today and the verification still in flight.

---

## 1. High-Level Summary
- **Watchers**: `tools/web_ai_watcher_v2.py` handles all three web exports. Hash-based dedupe now archives/clears `latest/` but still triggers staging so the identity service governs duplicates. Staging retries with backoff are in place.
- **Staging utility**: `conversation_pipeline/scripts/stage_to_gcs.py` works without `google-cloud-storage` installed; falls back to `gsutil` and keeps governance manifests. Verified with `python3 scripts/stage_to_gcs.py --help`.
- **ChatGPT Web Cloud Run job**: Execution `conversation-parser-chatgpt-web-jhl4c` is running against the freshly staged `chatgpt_2025-10-29_01.json`. Awaiting completion signal; Claude is walking through step-by-step checks.
- **Central services imports**: Conversation pipeline scripts now import `log_service` from the root package with defensive `sys.path` setup to support both root and `src/` layouts (parity with Copilot’s fixes).
- **Document service**: Blocker (package imports) resolved by Copilot; expect dry run to succeed once editable install is applied. No ingest executed yet today.

---

## 2. Pipeline-by-Pipeline Notes

### 2.1 ChatGPT Web Pipeline
- **Source watcher**: `tools/web_ai_watcher_v2.py`
  - Archives drop, writes manifest, clears `latest/`.
  - On duplicate hashes, reuses prior copy but still calls `stage_to_gcs.py`.
  - Logs stored under `data/logs/watcher_YYYYMMDD.log`.
- **Staging**: `conversation_pipeline/scripts/stage_to_gcs.py`
  - Fallback to `gsutil` confirmed; manifest written to `conversation_pipeline/governance/manifests/chatgpt_web_20251029_200300.json`.
- **Cloud Run job**: `conversation-parser-chatgpt-web`
  - Latest execution: `conversation-parser-chatgpt-web-jhl4c` (us-central1).
  - Status: running (1 retry counted, still within 60‑minute timeout).
  - Logs: <https://console.cloud.google.com/run/jobs/executions/details/us-central1/conversation-parser-chatgpt-web-jhl4c>.
- **Next checks**:
  1. Verify execution completion (`gcloud run jobs executions describe conversation-parser-chatgpt-web-jhl4c --region=us-central1`).
  2. Inspect Cloud Logging for dedupe behavior (identity service skip vs. insert).
  3. Confirm BigQuery table `spine.conversation` shows expected row counts / no duplicates.

### 2.2 Claude Web Pipeline
- **Watcher**: same `web_ai_watcher_v2.py` path; dedupe + staging logic shared.
- **Staging**: `stage_to_gcs.py` invoked automatically with Claude-specific prefixes.
- **Parser**: `parsers/ai_web/claude_web_parser/parser.py` under canonical runner.
- **Status**: No new drop since dedupe fix; ready for next export. Claude is validating canonical runner interaction; no outstanding code issues logged.
- **Suggested test**: `python parsers/ai_web/claude_web_parser/parser.py --help` followed by a dry-run manifest once an export lands.

### 2.3 Gemini Web Pipeline
- Mirrors Claude pipeline (different JSON schema). Watcher and staging identical.
- **Status**: Last export processed earlier; no pending retries.
- **Suggested test**: once Claude clears conversation pipelines, execute canonical runner on staged Gemini data to ensure schema alignment.

### 2.4 Agent Code Pipelines (Claude Code, Codex, Copilot, Gemini Code)
- **Common runtime**: `parsers/shared/canonical_runner.py` + `parsers/shared/utils.py`.
- **Fixes**: Updated imports to root `log_service`. Added path injection so canonical runner and utilities discover `architect_central_services` regardless of layout.
- **Status**: Ready for Claude’s round-trip tests. No recent failures in logs.
- **Suggested test**: For each agent, run `python parsers/ai_agents/<agent>_parser/parser.py --dry-run --input-uri <gs://...>` using the canonical runner to confirm identity service dedupe.

### 2.5 Document Service (Markdown Genesis Run)
- **Entry point**: `architect_central_services/document_service/ingest_service.py`.
- **Blocker resolved**: Imports now point to root-level services; path injection mirrors conversation pipeline approach.
- **Pending**: Run `pip install -e ./architect_central_services` (per Copilot plan), execute `python ingest_service.py --dry-run`, then plan the full ingestion.
- **Claude dependency**: Needs schema details from document_service to finalize Context System; coordinate run order post dry-run.

---

## 3. Verification Timeline
| Step | Owner | Command / Check | Status |
|------|-------|-----------------|--------|
| Watcher duplicate handling | Codex (complete) | `python tools/web_ai_watcher_v2.py --once chatgpt_web` (duplicate drop) | ✅ |
| Stage helper import path | Codex (complete) | `python3 scripts/stage_to_gcs.py --help` | ✅ |
| Cloud Run job | Claude monitoring | `gcloud run jobs executions describe conversation-parser-chatgpt-web-jhl4c --region=us-central1` | ⏳ running |
| Document service dry-run | Copilot pending | `python ingest_service.py --dry-run` (after editable install) | ⏳ |
| Context System planning | Claude | Wait for BigQuery schema confirmation post-ingest | ⏳ |

---

## 4. Outstanding Risks
- **Network sandbox**: Uploads/Cloud Run describes require escalated permissions; plan approvals ahead.
- **Cloud Run timeout**: Job limited to 3600 s. If timeouts persist, consider splitting staging batches or increasing timeout via `gcloud run jobs update`.
- **Package layout drift**: Both root and `src` directories exist. Until the `src/` folder is officially removed, keep the temporary `sys.path` injections.
- **Document ingest dependency**: Without document_service genesis run, Context System cannot query documents in BigQuery; coordinate with Copilot before Claude proceeds further.

---

## 5. Next Steps
1. **Monitor ChatGPT Web job** — capture completion, review logs, confirm dedupe (Codex/Claude).
2. **Enable document_service dry-run** — install package editable, run `--dry-run`, report results (Copilot).
3. **Share BigQuery schema references** — once ingest verified, document dataset/table names for Claude’s Context System.
4. **Schedule end-to-end regression** — after both conversation and document ingest succeed, trigger a combined run to validate the context aggregation prerequisites.
