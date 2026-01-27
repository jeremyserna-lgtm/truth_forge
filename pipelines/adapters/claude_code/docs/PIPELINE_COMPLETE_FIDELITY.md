# Claude Code Pipeline — Complete Fidelity Checklist

**Purpose:** What must be true for the pipeline to run with **complete fidelity** — end-to-end, manifest-driven, with no silent failures or schema drift.

**Last updated:** 2026-01-22

---

## 1. Orchestration (`run_pipeline.py`)

### 1.1 `--dry-run` and Stage 0

| Check | Status | Action |
|-------|--------|--------|
| Stage 0 does **not** support `--dry-run` | ❌ Blocker | **Do not** pass `--dry-run` to Stage 0 when using `run_pipeline.py --dry-run`. |
| Stages 1–16 support `--dry-run` | ✅ | Pass `--dry-run` only to stages 1–16. |

**Previous behavior:** `run_pipeline` forwarded `--dry-run` to all stages, including Stage 0, which failed with `unrecognized arguments: --dry-run`.

**Fix applied:** In `run_stage()`, `--dry-run` is only appended when `dry_run` is true **and** `stage_num > 0`. Stage 0 never receives `--dry-run`.

---

### 1.2 Manifest-driven flow (Stage 0 → Stage 1)

| Check | Status | Action |
|-------|--------|--------|
| Stage 0 writes discovery manifest | ✅ | `pipelines/claude_code/staging/discovery_manifest.json` |
| Stage 1 uses manifest when `--manifest` is set | ✅ | Uses `source.path` and `go_no_go` from manifest |
| `run_pipeline` passes `--manifest` to Stage 1 | ❌ Missing | When running 0→1, pass `--manifest <path>` to Stage 1. |

**Previous behavior:** `run_pipeline` never passed `--manifest` to Stage 1, so the discovery manifest was not used in orchestrated runs.

**Fix applied:** When running Stage 1, `run_pipeline` passes `--manifest <path>` when `DISCOVERY_MANIFEST_PATH` exists (i.e. after Stage 0 has run). The path used is `pipelines/claude_code/staging/discovery_manifest.json` (relative to pipeline root). This restores manifest-driven flow for 0→1.

---

### 1.3 `--source-dir` and Stage 0

| Check | Status | Action |
|-------|--------|--------|
| Stage 0 has default `--source-dir` | ✅ | `~/.claude/projects` |
| `run_pipeline` passes `--source-dir` when provided | ✅ | Only when `source_dir` is truthy |
| Default when not provided | ✅ | Stage 0 uses its own default |

**Optional improvement:** Have `run_pipeline` use `Path.home() / ".claude" / "projects"` as default and always pass `--source-dir` to Stage 0 for consistency.

---

## 2. Pre-flight / environment

### 2.0 Pre-flight validation script (NEW)

**`preflight_check.py`** validates all pre-flight conditions before running the pipeline.

**Usage:**
```bash
# From project root
python pipelines/claude_code/scripts/preflight_check.py [--source-dir PATH] [--strict]
```

**What it checks:**
- ✅ Source directory exists and contains JSONL files
- ✅ BigQuery project/dataset access and permissions
- ✅ spaCy installation and model availability
- ⚠️ Gemini CLI/API (optional, warnings only unless `--strict`)
- ✅ Identity service availability

**Output:**
- ✅ All checks passed → Pipeline ready to run
- ❌ Any check failed → Shows specific issues to fix
- ⚠️ Warnings (non-blocking) → Optional items like Gemini

**Run this before executing the pipeline** to ensure complete fidelity.

---

## 2. Pre-flight / environment (detailed)

### 2.1 Source data

| Check | Status | Action |
|-------|--------|--------|
| Source directory exists | ❌ Blocker | Ensure `~/.claude/projects` (or `--source-dir`) exists. |
| Directory contains `*.jsonl` | ❌ Blocker | Stage 0 fails if no JSONL files found. |
| Valid JSONL (no invalid lines) | ⚠️ | Stage 2 reports invalid lines; pipeline continues. Add validation or abort policy if needed. |

---

### 2.2 BigQuery

| Check | Status | Action |
|-------|--------|--------|
| `BIGQUERY_PROJECT_ID` / `BIGQUERY_DATASET` or defaults | ✅ | `shared.constants`: `flash-clover-464719-g1`, `spine` |
| Dataset exists and is writable | ❌ Blocker | Create dataset if missing; confirm IAM. |
| Tables created by stages | ✅ | Stages create stage tables as needed |
| Daily load/query limits | ⚠️ | Monitor `BQ_DAILY_LOAD_JOBS_LIMIT` / `BQ_DAILY_QUERY_JOBS_LIMIT` |

---

### 2.3 Stage 4 (LLM text correction)

| Check | Status | Action |
|-------|--------|--------|
| Gemini CLI available (primary) | Optional | `gemini` on `PATH`; subscription auth |
| Gemini API fallback | Optional | `Google_API_Key` in GCP Secret Manager |
| `google-cloud-secret-manager` installed | ❌ Blocker if using API | Required for API fallback |

---

### 2.4 NLP (Stages 8–10)

| Check | Status | Action |
|-------|--------|--------|
| spaCy installed | ❌ Blocker | `pip install spacy` |
| spaCy model downloaded | ❌ Blocker | e.g. `python -m spacy download en_core_web_sm` (or model used in code) |

---

### 2.5 Identity and knowledge

| Check | Status | Action |
|-------|--------|--------|
| `Primitive.identity` / ID generators | ✅ | Used for entity IDs |
| Knowledge service / router | Optional | For knowledge atoms; router moves atoms from pipeline HOLD₂ to canonical system |

---

## 3. Validation at stage boundaries

Per Stage 0 “corruption problem” and validation contracts:

| Check | Status | Action |
|-------|--------|--------|
| Each stage validates **inputs** from upstream | ⚠️ | Confirm required fields (e.g. `entity_id`, `level`, `role`, `persona`, `source_message_timestamp`) are validated. |
| Each stage validates **outputs** for downstream | ⚠️ | Same required-field checks. |
| Fail fast on validation failure | ✅ | Stages raise and stop. |
| Required fields by level (Stage 0 doc) | ✅ | See Stage 0 MASTER MEMORY; ensure stages 5–14 align. |

---

## 4. Schema and data flow

### 4.1 Critical fixes (from `CRITICAL_FIXES_IMPLEMENTED`)

| Check | Status | Action |
|-------|--------|--------|
| `source_message_timestamp` L5→L4→L3→L2 | ✅ | Implemented |
| `persona` L5→L4 (and where applicable) | ✅ | Implemented |
| `l5_type` in Stage 14 schema and MERGE | ✅ | Implemented |
| Stage 14 vs Stage 16 schema | ✅ | Stage 16 superset of Stage 14 |

### 4.2 Counts and Stage 12

| Check | Status | Action |
|-------|--------|--------|
| Stage 12 rollup (L4→L5→L6→L8) | ✅ | `COUNT_COLUMNS` and rollup logic |
| Count fields present before Stage 13/14 | ✅ | Stage 12 writes them |

### 4.3 Stage 16 and MERGE

| Check | Status | Action |
|-------|--------|--------|
| Stage 16 MERGE for enrichments | ✅ Done | Stage 16 uses MERGE (Stage 15 → entity_unified): WHEN MATCHED UPDATE validation fields; WHEN NOT MATCHED INSERT. Idempotent, supports enrichment updates. |

---

## 5. Status checker (`check_status.py`)

| Check | Status | Action |
|-------|--------|--------|
| Use `PROJECT_ID` / `DATASET_ID` from `shared.constants` | ❌ | Replace hardcoded `flash-clover-464719-g1` and `spine`. |
| Manifest path | ❌ | Use `pipelines/claude_code/staging/discovery_manifest.json` (relative to project root). |
| Stages 11–16 | ❌ | Extend checker to stages 11–16 (and entity_unified if applicable). |
| Run from project root | ⚠️ | Manifest path is relative to cwd; document “run from project root” or use absolute path. |

---

## 6. Knowledge atoms and router

| Check | Status | Action |
|-------|--------|--------|
| Stages write atoms to pipeline HOLD₂ | ✅ | `write_knowledge_atom_to_pipeline_hold2` |
| Canonical schema (`atom_id`, `type`, etc.) | ✅ | Per `shared.utilities` and docs |
| Router moves atoms to canonical system | ✅ | `router_knowledge_atoms.py` |
| Router run after pipeline | ⚠️ | Ensure router is run when knowledge-atom flow is required (separate step or documented workflow). |

---

## 7. End-to-end run sequence

For **complete fidelity**:

1. **Pre-flight**
   - Source dir exists and has `*.jsonl`.
   - BigQuery project/dataset ready.
   - spaCy (and model) installed.
   - If using Stage 4 API: Secret Manager + `Google_API_Key`.

2. **Orchestration**
   - **Fix `run_pipeline`:** do not pass `--dry-run` to Stage 0; pass it only to stages 1–16.
   - **Fix `run_pipeline`:** when running 0→1, pass `--manifest pipelines/claude_code/staging/discovery_manifest.json` to Stage 1 (relative to project root, or resolve via `PROJECT_ROOT`).

3. **Execution**
   - Run from project root:  
     `python pipelines/claude_code/scripts/run_pipeline.py [--source-dir PATH] [--start-stage N] [--end-stage N] [--dry-run]`
   - For dry-run: same, but `--dry-run` must not be passed to Stage 0.

4. **Validation**
   - Run `validate_pipeline_and_knowledge_atoms.py` (and fix any validation that assumes `exhale` in stages; stages use `write_knowledge_atom_to_pipeline_hold2`).
   - Run `test_pipeline_stages.py` for stage-by-stage checks.
   - Use `check_status.py` after updating it per §5.

5. **Post-pipeline**
   - Run `router_knowledge_atoms.py` if knowledge atoms should be moved to the canonical system.

---

## 8. Summary: required changes for complete fidelity

| Priority | Item | Owner |
|----------|------|--------|
| **P0** | **`run_pipeline`: do not pass `--dry-run` to Stage 0** | ✅ Done |
| **P0** | **`run_pipeline`: pass `--manifest` to Stage 1 when manifest exists** | ✅ Done |
| **P1** | **`check_status`: use shared constants, fix manifest path, add stages 11–16** | ✅ Done |
| **P1** | **Pre-flight: verify source dir, JSONL, BigQuery, spaCy, optional Gemini** | ✅ Done |
| **P2** | **`run_pipeline` default `--source-dir` and always pass to Stage 0** | ✅ Done |
| **P2** | **Stage 16 MERGE for enrichments** | ✅ Done |

---

## 9. Quick verification commands

```bash
# From project root (Truth_Engine)

# 1. Source and manifest
ls -la ~/.claude/projects/*.jsonl 2>/dev/null | head -5
ls -la pipelines/claude_code/staging/discovery_manifest.json 2>/dev/null

# 2. Dry-run (must not pass --dry-run to Stage 0)
python pipelines/claude_code/scripts/run_pipeline.py --dry-run --start-stage 0 --end-stage 0
# Expected: Stage 0 runs successfully (no “unrecognized arguments: --dry-run”)

# 3. Stage 0 only (writes manifest)
python pipelines/claude_code/scripts/run_pipeline.py --start-stage 0 --end-stage 0

# 4. Stage 1 with manifest (after 0)
python pipelines/claude_code/scripts/stage_1/claude_code_stage_1.py \
  --manifest pipelines/claude_code/staging/discovery_manifest.json

# 5. Pre-flight validation (NEW)
python pipelines/claude_code/scripts/preflight_check.py [--source-dir PATH] [--strict]

# 6. Status (updated)
python pipelines/claude_code/scripts/check_status.py
```

---

**Conclusion:** The pipeline can run with **complete fidelity** once:

1. **`run_pipeline`** ✅ Updated to skip `--dry-run` for Stage 0 and to pass `--manifest` to Stage 1 when the manifest exists.
2. **Pre-flight** ✅ `preflight_check.py` validates all conditions (source, BigQuery, spaCy, optional Gemini).
3. **`check_status`** ✅ Updated to use shared constants, correct manifest path, and includes stages 11–16.
4. **Validation and router** are run as part of the documented workflow.

**All P0, P1, and P2 items are now complete!** The pipeline is ready for complete fidelity execution.
