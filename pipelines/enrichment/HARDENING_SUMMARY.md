# Enrichment pipeline hardening summary

**Date**: 2026-01-27  
**Scope**: `pipelines/enrichment/` only.

---

## Standards applied

| Standard | Implementation |
|----------|----------------|
| **Type hints** | All params and returns; `mypy --strict` passes on `pipelines/enrichment/`. |
| **Structured logging** | `logger.info/error(..., extra={...})` only; no f-strings in logs. |
| **DLQ** | `pipelines/enrichment/dlq.py`; failed records sent to DLQ, never dropped. |
| **Retry** | `tenacity` on BQ query and insert; exponential backoff for ConnectionError, TimeoutError, OSError. |
| **Ruff** | `ruff check` and `ruff format` pass. |
| **Tests** | `tests/unit/pipelines/enrichment/`: 11 tests for dlq, config, utils, base_enrichment. |

---

## Changes made

1. **DLQ**
   - Added `dlq.py` with `DeadLetterQueue` (send, count).
   - BaseEnrichment sends failed records to DLQ in `run()`.

2. **Retry**
   - `_query_bq` and `_batch_load` use `@retry` (stop=3, wait exponential, retry on ConnectionError/TimeoutError/OSError).

3. **Batch Loading (not Streaming)**
   - Changed from `insert_rows_json` (streaming) to `load_table_from_file` with temp NDJSON files.
   - No streaming buffer issues, immediate data availability for UPDATEs.
   - Follows codebase standard: "We don't do streaming batches in this codebase".

4. **Structured logging**
   - Replaced f-strings in log calls with `extra={}` in base_enrichment, utils, dlq.

5. **Type fixes**
   - `enriched: list[dict[str, Any]]` and `out` for per-row dict in run overrides (taxonomy, quality, fine_grained, claims).
   - `metadata` → `out_meta` in quality to avoid overwriting row metadata; explicit `dict[str, Any]`.
   - Optional deps (textblob, nrclex, etc.) covered by mypy overrides in `pyproject.toml`.

5. **Ruff**
   - Imports, E741 (`l`→`lev`), SIM108 ternary, RUF059 unused vars, B905 `zip(..., strict=True)`, W291 trailing whitespace, F841 unused assignments, etc.

6. **Tests**
   - `test_dlq`, `test_config`, `test_utils`, `test_base_enrichment` under `tests/unit/pipelines/enrichment/`.

---

## Verification

```bash
.venv/bin/mypy pipelines/enrichment/ --strict
.venv/bin/ruff check pipelines/enrichment/
.venv/bin/ruff format --check pipelines/enrichment/
.venv/bin/pytest tests/unit/pipelines/enrichment/ -v
```

All of the above pass.

---

## References

- `framework/standards/error_handling/` (DLQ, retry, batch)
- `framework/standards/logging/STRUCTURED.md`
- `framework/standards/code_quality/` (type hints, docstrings, static analysis)
- `CLAUDE.md` (quick quality check)
