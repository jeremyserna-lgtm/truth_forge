# Pipeline Service Integration Assessment

**Purpose:** Identify which **Primitive / central services** pipelines should use, what is integrated today, and what is missing.

**Canonical services (use these):**
- **Identity:** `Primitive.identity` — ID generation (conv, turn, msg, sent, span, word, run, etc.). Core to all projects; seeded.
- **Run Service:** `Primitive.central_services.run_service.RunService` — Track every execution (script, stage): started, completed, failed; metrics; run_id.
- **Relationship Service:** `Primitive.central_services.relationship_service.RelationshipService` — Track entity relationships (e.g. parent→child "contains" for spine).
- **Cost Service:** `Primitive.central_services.cost_service.CostService` — Track API/compute/storage costs (LLM, BigQuery, etc.).
- **Logging:** `Primitive.core` (get_logger, get_current_run_id, set_run_id) — Structured logging with run_id. Pipelines use `logging_bridge`, which delegates to Primitive when available.

**Do not use:** `architect_central_services` (deprecated). Prefer `Primitive` over `src.services.central_services` for ID, run, relationship, cost.

---

## 1. Service × pipeline matrix

| Service | Claude Code | Gemini Web | Text Messages |
|--------|-------------|------------|---------------|
| **Identity** | Partial (Stage 3: `identity_service`; 5–10: hashlib) | Partial (Stage 3: `identity_service`) | Not assessed |
| **Run Service** | No | No | Partial (`CentralRunService` in stage 4 only) |
| **Relationship Service** | Utility only (`register_spine_entities`) | No | No |
| **Cost Service** | No | No | Yes (stages 4, 5, 6: `src` cost_service) |
| **Logging / run_id** | Yes (logging_bridge, PipelineTracker) | Yes (src) | Yes (Primitive.core + src) |

---

## 2. Claude Code pipeline — detail

### 2.1 Identity

| Where | Current | Gap | Action |
|-------|---------|-----|--------|
| Stage 3 (THE GATE) | `src...identity_service`: `generate_message_id_from_guid`, `register_id`, `sync_to_bigquery` | Uses deprecated path; should use **Primitive.identity** | Migrate to `Primitive.identity.generate_message_id`; keep registry sync (or use identity_service only for registry if it stays). |
| Stages 5, 6, 7, 8, 9, 10 | Local `hashlib` for conv, turn, msg, sent, span, word IDs | Not using canonical ID service | Use `Primitive.identity` generators (`generate_conversation_id`, `generate_turn_id`, etc.). |
| `register_spine_entities` | Uses `Primitive.identity.generate_run_id`; MERGE into `identity.id_registry` | — | OK. |

### 2.2 Run Service

| Where | Current | Gap | Action |
|-------|---------|-----|--------|
| All stages 0–16 | `PipelineTracker` (writes to `logs/pipelines/*.jsonl`) | No Run Service exhale | **Integrate Run Service** into pipeline execution. When a stage runs, exhale `started` and `completed`/`failed` via `RunService.exhale()`. |
| `register_spine_entities` | Exhales run events via Run Service | — | OK. |

**Recommendation:** Have **PipelineTracker** (or a thin wrapper used by all stages) also call **Run Service** on enter/exit. All stages using `PipelineTracker` then get run tracking without per-stage changes.

### 2.3 Relationship Service

| Where | Current | Gap | Action |
|-------|---------|-----|--------|
| Pipeline stages | None | Stages build L8→L6→L5→… but don’t exhale relationships | Optional: exhale parent→child “contains” as entities are created. |
| `register_spine_entities --with-relationships` | Exhales parent_id→entity_id “contains” from `entity_unified` | — | OK. |

**Recommendation:** Keep relationship tracking in `register_spine_entities` as the primary integration. Per-stage exhale can be added later if needed.

### 2.4 Cost Service

| Where | Current | Gap | Action |
|-------|---------|-----|--------|
| Stage 4 | No cost tracking | Stage 4 may add LLM text correction; BigQuery used | Add **Cost Service** when LLM is introduced; optionally for heavy BQ usage. |
| Other stages | BigQuery only | No cost tracking | Optional: exhale BQ cost for large/scanned bytes. |

---

## 3. Gemini Web pipeline — detail

- **Identity:** Stage 3 uses `src...identity_service`. Migrate to **Primitive.identity**.
- **Run Service:** No integration. Add run tracking (e.g. via shared PipelineTracker + Run Service if adopted).
- **Relationship / Cost:** Not integrated. Add as needed (e.g. Cost when using LLM/BQ).

---

## 4. Text Messages pipeline — detail

- **Run Service:** `CentralRunService` (src) used in stage 4 only. Prefer **Primitive** Run Service and use consistently across stages.
- **Cost Service:** Stages 4, 5, 6 use `src` cost_service. Prefer **Primitive** Cost Service.
- **Identity:** Uses BigQuery/config; not clearly using Primitive.identity. Assess and align if producing spine-like entities.

---

## 5. Implementation checklist

- [x] **Run Service in PipelineTracker:** PipelineTracker __enter__ / __exit__ calls `RunService.exhale` (started / completed | failed). All Claude Code stages gain run tracking. **Done.** Exhale failures (e.g. Run Service DuckDB STRUCT schema issue) are caught and logged; tracking continues.
- [x] **Stage 3 → Primitive.identity:** Replaced `identity_service` with `Primitive.identity.generate_message_id`; registration now via `register_spine_entities`. **Done.**
- [x] **Stages 5–10 → Primitive.identity:** Replaced hashlib-based IDs with `Primitive.identity` generators (conversation, turn, sentence, span, word). **Done.**
- [ ] **Relationship Service:** No change required; `register_spine_entities --with-relationships` remains the integration point.
- [ ] **Cost Service (Claude Code):** Add when Stage 4 gains LLM; optionally for high-cost BQ.
- [ ] **Gemini Web:** Identity migration; Run Service (and optionally Cost) when structure allows.
- [ ] **Text Messages:** Migrate to Primitive Run Service and Cost Service; unify usage across stages.

---

## 6. See also

- `Primitive/identity/README.md` — Canonical ID service.
- `Primitive/central_services/run_service/`, `relationship_service/`, `cost_service/` — Service APIs.
- `pipelines/claude_code/docs/ENTITY_UNIFIED_ID_ALIGNMENT.md` — ID alignment and `register_spine_entities`.
- `Primitive/central_services/COMPLETE_SERVICE_SUITE.md` — Full service suite and use cases.
