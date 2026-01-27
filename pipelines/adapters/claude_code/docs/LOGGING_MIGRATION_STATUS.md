# Claude Code Pipeline – Logging & Hardening Migration

**Status:** Complete  
**Date:** 2026-01-22

## Summary

All stages (0–16) now use:

- **Structured logging** via `shared.logging_bridge` (Primitive.core when available, else central_services)
- **`ensure_stage_logging_context(stage, run_id, pipeline)`** at main start
- **Event-style logging** (`logger.info("event_name", key=value)`) instead of f-strings
- **Batch loading only** – `load_rows_to_table` (rich BigQuery client); no `insert_rows_json`
- **Input/output validation** where applicable (e.g. Stage 0 source dir, report shape)

## Migration checklist

| Stage | Logging | Batch load | Validation |
|-------|---------|------------|------------|
| 0 | ✅ | N/A (no BQ) | ✅ input + output |
| 1 | ✅ | ✅ | ✅ input |
| 2–4 | ✅ | N/A (SQL) or ✅ | ✅ |
| 5–10 | ✅ | ✅ | ✅ |
| 11–13 | ✅ | N/A (validation/SQL) | ✅ |
| 14–16 | ✅ | ✅ (14: MERGE; 15–16: load_rows_to_table) | ✅ |

## Key files

- `scripts/shared/logging_bridge.py` – central logger + context
- `scripts/stage_*/claude_code_stage_*.py` – all migrated
- `docs/OPERATIONAL_STANDARDS.md` – cross-cutting rules

## How to run

```bash
# From project root
python3 pipelines/claude_code/scripts/stage_0/claude_code_stage_0.py --source-dir ~/.claude/projects --sample-size 5
python3 pipelines/claude_code/scripts/stage_1/claude_code_stage_1.py --source-dir ~/.claude/projects --dry-run --limit-files 2
# … etc.
```

## Tests

- Stage 0: `--source-dir ~/.claude/projects --sample-size 2` ✅
- Stage 1: `--dry-run --limit-files 1` ✅
- Stage 2+ require upstream tables (run 0→1 first for real BQ load).
