# ChatGPT Web Pipeline – Situation Snapshot (2025-10-30)

## Current Focus
- Scope: ChatGPT Web ingestion path (watcher → GCS staging → Cloud Run parser job → BigQuery / identity service).
- Objective: Ensure the latest export (hash identical to prior drop) still stages to GCS and runs through Cloud Run so the identity layer handles dedupe, not the watcher.

## State Overview
- Latest export staged manually after watcher dedupe: `gs://conversation-archives/chatgpt_web/staging/2025-10-29/chatgpt_2025-10-29_01.json`.
- Governance manifest: `conversation_pipeline/governance/manifests/chatgpt_web_20251029_200300.json`.
- Cloud Run execution in flight: `conversation-parser-chatgpt-web-jhl4c` (us-central1); one retry recorded, currently running with 2 vCPU / 2 GiB and 60 min timeout.

## Recent Changes
1. **Watcher (`tools/web_ai_watcher_v2.py`)**
   - Dedupe now reuses the local copy but *still* archives and stages, preserving identity service dedupe.
   - Staging retries (x3) with backoff and stdout/stderr surfacing.
2. **Staging helper (`conversation_pipeline/scripts/stage_to_gcs.py`)**
   - Injected central-services package path; added gsutil fallback when `google-cloud-storage` isn’t installed.
   - Common object-key generator ensures consistent GCS layout regardless of upload mechanism.
3. **Central services package scaffold (`architect_central_services/src/architect_central_services/…`)**
   - Added `__init__`, `config_service.py`, `log_service/__init__.py`, and `log_service/central_logger.py` to support clean imports across scripts.

## Monitoring / Todo
- [ ] Watch `conversation-parser-chatgpt-web-jhl4c` until `status.conditions[type=Completed]` is `True`; inspect logs on completion or timeout.
- [ ] After completion, verify:
  - Identity service acknowledged duplicate without creating new records.
  - BigQuery tables reflect expected ingest (no missing data, no double writes).
- [ ] Keep watcher running for future drops (duplicates now safe). Consider installing `google-cloud-storage` in runtime env to avoid gsutil fallback delays.

## Dependencies & Notes
- Manual staging required escalated permissions because sandbox lacks outbound network access.
- Job container image: `gcr.io/flash-clover-464719-g1/conversation-parser-chatgpt-web@sha256:b72291ef58691d27ff0a77ef09c6b3a18e119129ba24fac6959576ba339fb3a1`.
- Service account: `conversation-pipeline@flash-clover-464719-g1.iam.gserviceaccount.com`.
