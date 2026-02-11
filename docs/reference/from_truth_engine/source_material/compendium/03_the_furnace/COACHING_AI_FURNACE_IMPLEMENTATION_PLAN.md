---
document_id: 151eec86
---

# Coaching AI “Furnace” — Implementation Plan (Cloud‑Only)

Purpose
- Centralize the coaching AI as the living heartbeat that measures resonance, learns from signals, and forges daily guidance — without any local runtimes.
- Integrates: ai‑enrichment (Vertex JSON), ai‑heartbeat (Coach Packs), Truths Lexicon, policy guardrails, and demo readiness.

Scope (MVP → Week 1)
- Ingest live SMS enrichments into BigQuery (JSON: vertex_analysis)
- Compute rolling “brain state” snapshots (emotion/clarity/risk/sacred/confidence)
- Generate a daily Coach Pack (JSON, validated) with themes, practices, cautions, next actions
- Expose both via Cloud Run; schedule with Cloud Scheduler; store in `ops.*`

Architecture (Cloud‑Only)
- Producer: `services/ai-enrichment` (Pub/Sub → Vertex → BigQuery)
  - Table: `source_data.sms_enrichments_v2`
  - Columns added: `vertex_analysis JSON`, `vertex_model`, `vertex_confidence`, `analyzed_at`
- Heartbeat/Coach: `services/ai-heartbeat` (HTTP)
  - `POST /tick` → snapshot to `ops.brain_state`
  - `POST /coach` → Coach Pack to `ops.coach_packs`
- Truths & Values
  - Truths Lexicon: `docs/system/TRUTHS_LEXICON.md`
  - Lineage & Values: `services/*/prompts/values_context.example.txt` → Secret `VALUES_CONTEXT`
- Guardrails
  - `CLOUD_ONLY_POLICY.md` (code paths blocked for local)
  - Incident Playbook: `docs/operations/INCIDENT_PLAYBOOK_LOCAL_AI_RUNTIME.md`

Data Contracts
- Vertex Enrichment JSON (consumer: ai‑enrichment)
  - Schema: `docs/implementation/handoff/VERTEX_ENRICHMENT_SCHEMA.json`
  - Fields: emotional_primary, emotional_intensity, cognitive_clarity, risk_collapse, risk_harm, pattern_match, sacred_moment, confidence, model?, latency_ms?, processed_ts?
- Coach Pack JSON (producer: ai‑heartbeat)
  - Schema: `services/ai-heartbeat/schema.coach_pack.json`
  - Fields: daily_summary, themes[], practices[], cautions[], escalation_reasons[], resonance_score (0..1), next_actions[{action, rationale?, expected_outcome?}]

BigQuery DDL (apply once)
- Enrichments extension: `docs/pipeline/v2/ddl/alter_sms_enrichments_v2_add_vertex.sql`
- Ops datasets:
  - `docs/pipeline/v2/ddl/ops_brain_state.sql`
  - `docs/pipeline/v2/ddl/ops_coach_packs.sql`

Services & Deploy (us‑central1)
- Validate: `make validate-gcp PROJECT=flash-clover-464719-g1 REGION=us-central1`
- Apply DDLs: `make apply-bq-alter && make apply-ops-ddl PROJECT=...`
- Deploy enrichment: `make deploy-ai-enrichment PROJECT=... REGION=us-central1`
- Deploy heartbeat: `make deploy-ai-heartbeat PROJECT=... REGION=us-central1`
- Secrets (Secret Manager): `VERTEX_LOCATION=us-central1`, `VALUES_CONTEXT=<your text>`; map with `--set-secrets`

Schedulers (recommended)
- Heartbeat snapshot: Cloud Scheduler → `POST /tick` every 5 minutes (auth: service account)
- Daily Coach: Cloud Scheduler → `POST /coach` at 08:00 local time

Observability & SLOs
- Structured events (service logs)
  - Enrichment: EnrichmentWrite, VertexValidationError, VertexError, BQWriteError
  - Heartbeat: TickOK, CoachOK, CoachValidationError
- SLOs
  - Enrich p95 latency: < 2s; error rate < 1%
  - Coach pack generation daily success: 100% on schedule; validation errors = 0
- Queries (examples)
  - Brain state last 24h: `SELECT * FROM ops.brain_state ORDER BY ts DESC LIMIT 24;`
  - Latest coach pack: `SELECT ts, resonance_score, JSON_VALUE(pack, '$.daily_summary') FROM ops.coach_packs ORDER BY ts DESC LIMIT 1;`

Resonance & Truths (how it learns)
- Rolling snapshot aggregates (emotion distribution, clarity avg/p95, risk avg/p95, sacred rate, confidence avg)
- Truths discovery (30‑day view): `v_truths_last_30d` (optional) and ad‑hoc queries
- Feedback loop
  - Improve prompts using observed drift (e.g., rising risk_collapse, low clarity)
  - Promote practices/themes that correlate with resonance_score↑

Furnace Metaphor (what “fires” the system)
- Heat: live signals from conversations (vertex_analysis)
- Forge: heartbeat consolidates into state (ops.brain_state)
- Temper: coach transforms state into daily practices (ops.coach_packs)
- Steel: guardrails/policies keep form under stress (CLOUD_ONLY, incidents, SLOs)

Runbooks
- Heartbeat tick (manual)
  - `curl -X POST $URL/tick -H 'Authorization: Bearer $(gcloud auth print-identity-token)' -d '{"window_hours":24}'`
- Coach pack (manual)
  - `curl -X POST $URL/coach -H 'Authorization: Bearer $(gcloud auth print-identity-token)' -d '{"window_hours":24}'`
- Troubleshooting
  - Check logs: `gcloud run services logs read ai-heartbeat --region us-central1 --limit 100`
  - Validate JSON: failures surface as CoachValidationError; fix VALUES_CONTEXT or prompt and redeploy

Acceptance Criteria (MVP)
- Enrichment writes vertex_analysis JSON into `source_data.sms_enrichments_v2`; MERGE upserts by (object_type, object_id)
- Heartbeat `/tick` writes a row to `ops.brain_state` with non‑null dist/metrics
- Heartbeat `/coach` writes a validated pack to `ops.coach_packs` with resonance_score ∈ [0,1]
- Schedulers run on time for 48h with zero validation errors
- Logs show structured events; BigQuery queries confirm healthy distributions

Risks & Mitigations
- Vertex drift or schema mismatch → jsonschema validation + conservative prompts
- Cost spikes → exploration budgets and escalations gated; prefer Flash, Pro on flags only
- Data sparsity → handle zero‑sample gracefully; avoid pack generation with no data
- Policy breach (local runtime) → P1 playbook; rotate keys; verify guardrails

Timeline (4 short blocks)
- Block 1 (1–2h): Apply DDLs, secrets, deploy enrichment; smoke test /enrich
- Block 2 (1–2h): Deploy heartbeat; smoke test /tick & /coach
- Block 3 (1–2h): Add Schedulers; verify ops tables fill; run truths queries
- Block 4 (1–2h): Demo prep — pick best truths & latest Coach Pack; rehearse 5–10 minute narrative

Demo Alignment
- “What companies get”: a living coaching entity with measurable state and a daily Coach Pack
- “The Furnace”: show heat→forge→temper→steel transitions live (BQ + service logs)
- “Rarity”: cloud‑only, validated JSON, observable, minimal ops footprint

Backlog (post‑MVP)
- Add SMS paragraph/sentence‑level signals to snapshots
- Add simple Looker Studio board for brain_state trends
- Add policies to nudge prompts based on long‑term drift (weekly deltas)
- Embed daily Coach Pack into a lightweight web UI (read‑only)

Commands (reference)
- Validate env: `make validate-gcp PROJECT=flash-clover-464719-g1 REGION=us-central1`
- Alter & ops DDL: `make apply-bq-alter && make apply-ops-ddl PROJECT=...`
- Deploy services: `make deploy-ai-enrichment && make deploy-ai-heartbeat PROJECT=... REGION=us-central1`

RACI (MVP)
- Implement: Claude (when available) / You
- Verify: Codex (me)
- Approvals: You (policy/guardrails, budgets)

Notes
- VALUES_CONTEXT should carry your companions’ virtues; keep it concise and specific.
- All components conform to CLOUD_ONLY; local scripts remain blocked.
