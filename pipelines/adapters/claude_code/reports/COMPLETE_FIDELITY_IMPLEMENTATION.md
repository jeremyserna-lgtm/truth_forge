# Complete Fidelity Implementation - Complete

**Date:** 2026-01-22  
**Status:** ✅ **ALL P0 AND P1 ITEMS COMPLETE**

---

## Summary

All critical (P0) and high-priority (P1) items for complete pipeline fidelity have been implemented. The pipeline is now ready for end-to-end execution with complete fidelity.

---

## Completed Items

### ✅ P0: Critical Orchestration Fixes

#### 1. `run_pipeline.py` - `--dry-run` handling
**Issue:** `run_pipeline --dry-run` passed `--dry-run` to Stage 0, which doesn't support it, causing failures.

**Fix:**
- Modified `run_stage()` to only append `--dry-run` when `dry_run and stage_num > 0`
- Stage 0 never receives `--dry-run` flag
- Verified: `python run_pipeline.py --dry-run --start-stage 0 --end-stage 0` completes successfully

**Files Modified:**
- `pipelines/claude_code/scripts/run_pipeline.py`

---

#### 2. `run_pipeline.py` - Manifest-driven flow (0→1)
**Issue:** `run_pipeline` never passed `--manifest` to Stage 1, breaking the discovery manifest contract.

**Fix:**
- Added `DISCOVERY_MANIFEST_PATH = PIPELINE_ROOT.parent / "staging" / "discovery_manifest.json"`
- Modified `run_stage()` to pass `--manifest <path>` to Stage 1 when manifest exists
- Stage 1 now uses discovery manifest when available (after Stage 0 runs)

**Files Modified:**
- `pipelines/claude_code/scripts/run_pipeline.py`

---

### ✅ P1: Status Checker and Pre-flight Validation

#### 3. `check_status.py` - Complete rewrite
**Issues:**
- Hardcoded project/dataset (`flash-clover-464719-g1.spine`)
- Wrong manifest path (`staging/discovery_manifest.json` relative to cwd)
- Missing stages 11-16

**Fix:**
- Uses `PROJECT_ID` and `DATASET_ID` from `shared.constants`
- Uses `get_stage_table()` for table names
- Correct manifest path: `pipelines/claude_code/staging/discovery_manifest.json` (resolved from script location)
- Added all stages 0-16 (including entity_unified for Stage 16)
- Better error handling and output formatting

**Files Modified:**
- `pipelines/claude_code/scripts/check_status.py` (complete rewrite)

---

#### 4. `preflight_check.py` - NEW pre-flight validation script
**Purpose:** Validate all pre-flight conditions before running the pipeline.

**Features:**
- ✅ Source directory exists and contains JSONL files
- ✅ BigQuery project/dataset access and permissions
- ✅ spaCy installation and model availability
- ⚠️ Gemini CLI/API (optional, warnings only unless `--strict`)
- ✅ Identity service availability

**Usage:**
```bash
python pipelines/claude_code/scripts/preflight_check.py [--source-dir PATH] [--strict]
```

**Output:**
- ✅ All checks passed → Pipeline ready to run
- ❌ Any check failed → Shows specific issues to fix
- ⚠️ Warnings (non-blocking) → Optional items like Gemini

**Files Created:**
- `pipelines/claude_code/scripts/preflight_check.py` (new file)

---

## Documentation Updates

### `PIPELINE_COMPLETE_FIDELITY.md`
- Updated to reflect all completed items
- Added section on `preflight_check.py`
- Updated quick verification commands
- Marked P0 and P1 items as complete

**Files Modified:**
- `pipelines/claude_code/docs/PIPELINE_COMPLETE_FIDELITY.md`

---

## Verification

### Test 1: `--dry-run` with Stage 0
```bash
python3 pipelines/claude_code/scripts/run_pipeline.py --dry-run --start-stage 0 --end-stage 0
```
**Result:** ✅ Stage 0 completes successfully (no "unrecognized arguments: --dry-run")

### Test 2: Manifest-driven flow
```bash
# Run Stage 0 (creates manifest)
python3 pipelines/claude_code/scripts/run_pipeline.py --start-stage 0 --end-stage 0

# Run Stage 1 (should use manifest)
python3 pipelines/claude_code/scripts/run_pipeline.py --start-stage 1 --end-stage 1
```
**Result:** ✅ Stage 1 receives `--manifest` when manifest exists

### Test 3: Status checker
```bash
python3 pipelines/claude_code/scripts/check_status.py
```
**Result:** ✅ Shows all stages 0-16, uses shared constants, correct manifest path

### Test 4: Pre-flight validation
```bash
python3 pipelines/claude_code/scripts/preflight_check.py
```
**Result:** ✅ Validates all pre-flight conditions

---

## P2 Items (Complete)

| Priority | Item | Status |
|----------|------|--------|
| **P2** | **`run_pipeline` default `--source-dir` and always pass to Stage 0** | ✅ Done |
| **P2** | **Stage 16 MERGE for enrichments** | ✅ Done |

### P2.1: `run_pipeline` default `--source-dir`
- Added `DEFAULT_SOURCE_DIR = Path.home() / ".claude" / "projects"`.
- `--source-dir` now defaults to `DEFAULT_SOURCE_DIR` instead of `None`.
- Stage 0 always receives `--source-dir` when it is set (including default).

### P2.2: Stage 16 MERGE
- Replaced skip+insert logic with a single MERGE query.
- **WHEN MATCHED:** UPDATE only `validation_status`, `validation_score`, `run_id`, `promoted_at` (avoids overwriting structural columns with NULL).
- **WHEN NOT MATCHED:** INSERT full row (Stage 15 columns + NULLs for structural fields not in Stage 15).
- MERGE is idempotent and supports enrichment updates on existing entities.

**Note:** Stage 16 requires the Stage 15 table to exist. Running `stage_16 --dry-run` in isolation will fail with "Input table ... claude_code_stage_15 does not exist"; run stages 0–15 first (or at least 15).

---

## Complete Fidelity Workflow

### 1. Pre-flight
```bash
python pipelines/claude_code/scripts/preflight_check.py [--source-dir PATH]
```

### 2. Run Pipeline
```bash
python pipelines/claude_code/scripts/run_pipeline.py [--source-dir PATH] [--dry-run]
```

### 3. Check Status
```bash
python pipelines/claude_code/scripts/check_status.py
```

### 4. Validate (optional)
```bash
python pipelines/claude_code/scripts/test_pipeline_stages.py
python pipelines/claude_code/scripts/validate_pipeline_and_knowledge_atoms.py
```

### 5. Router (optional)
```bash
python pipelines/claude_code/scripts/router_knowledge_atoms.py
```

---

## Conclusion

**All P0 and P1 items for complete fidelity are now complete!**

The pipeline is ready for end-to-end execution with:
- ✅ Proper `--dry-run` handling (Stage 0 excluded)
- ✅ Manifest-driven flow (Stage 0 → Stage 1)
- ✅ Complete status checking (all stages 0-16)
- ✅ Pre-flight validation (all conditions checked)

**The pipeline can now run with complete fidelity.**
