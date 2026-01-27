# Pipeline Core Pattern

**The foundational HOLD:AGENT:HOLD pattern for all pipeline development.**

**Status**: ACTIVE
**Owner**: Framework
**Parent**: [INDEX.md](INDEX.md)

---

## The Universal Pattern

### HOLD → AGENT → HOLD

This is THE STRUCTURE from The Seed, applied at pipeline scale:

```
HOLD₁ (input)  →  AGENT (process)  →  HOLD₂ (output)
```

**Every stage. Every pipeline. Every time.**

### Scale Invariance

The pattern applies at every level:

| Scale | HOLD₁ | AGENT | HOLD₂ |
|-------|-------|-------|-------|
| Function | String | `normalize()` | Cleaned string |
| Script | `input.jsonl` | `my_script.py` | `staging.jsonl` |
| Stage | `stage_N-1` table | Stage N script | `stage_N` table |
| Pipeline | Raw export | All 16 stages | `entity_unified` |

### Connection Rules

**Rule 1**: Stages connect at HOLDs only

```
✅ CORRECT:
Stage N:   HOLD₁ → AGENT → HOLD₂
                           ↓
Stage N+1: HOLD₁ → AGENT → HOLD₂
           (HOLD₁ = Stage N's HOLD₂)

❌ WRONG:
Stage N:   HOLD₁ → AGENT → HOLD₂
                      ↓
Stage N+1: HOLD₁ → AGENT → HOLD₂
           (direct AGENT-to-AGENT)
```

**Rule 2**: Explicit HOLD identification

```python
HOLD_1 = "spine.claude_code_stage_2"   # Previous stage output
HOLD_2 = "spine.claude_code_stage_3"   # This stage output
```

**Rule 3**: No direct stage-to-stage communication

```python
# ✅ CORRECT
input_data = read_from_hold_1(client)
output_data = process(input_data)
write_to_hold_2(client, output_data)

# ❌ WRONG
result = call_next_stage_directly(data)
```

---

## Batch Loading Only

**CRITICAL**: All pipelines use batch loading. No streaming.

### Required Pattern

```python
# BATCH LOADING (CORRECT)
batch_size = 1000

# Read batch from HOLD₁
query = f"""
SELECT * FROM `{HOLD_1}`
WHERE NOT EXISTS (
    SELECT 1 FROM `{HOLD_2}` h2
    WHERE h2.entity_id = source.entity_id
)
LIMIT {batch_size}
"""
rows = list(client.query(query).result())

# Process batch
results = []
for row in rows:
    result = process_record(row)
    results.append(result)

# Write batch to HOLD₂
if results:
    write_batch_to_bigquery(client, HOLD_2, results)
```

### What NOT To Do

```python
# ❌ STREAMING (FORBIDDEN)
for row in client.query(query).result():  # Streaming iterator
    process_and_write_one_at_a_time(row)  # Per-record I/O

# ❌ PER-RECORD FILE I/O (FORBIDDEN)
for record in records:
    open_file()       # Opens 286,706 times!
    write_record()
    close_file()
```

### Performance Impact

| Records | Per-Record I/O | Batch I/O (1000/batch) |
|---------|----------------|------------------------|
| 1,000 | 30 seconds | 0.03 seconds |
| 100,000 | 50 minutes | 3 seconds |
| 286,706 | 14+ hours | ~9 seconds |

---

## Folder Structure

```
pipelines/{pipeline_name}/
├── __init__.py
├── config.yaml               # Pipeline configuration
├── stage_0_assessment.py     # Stage 0
├── stage_1_extraction.py     # Stage 1
├── ...
├── stage_16_promotion.py     # Stage 16
├── run_pipeline.py           # Orchestrator
└── tests/                    # Pipeline-specific tests
```

---

## Convergence

### Bottom-Up Validation

This document requires:
- [INDEX.md](INDEX.md) - Parent standard

### Top-Down Validation

This document is shaped by:
- [04_ARCHITECTURE](../../04_ARCHITECTURE.md) - HOLD:AGENT:HOLD
- [06_LAW](../../06_LAW.md) - Idempotency, No Magic

---

*HOLD₁ (input) → AGENT (process) → HOLD₂ (output). Every stage. Every time.*
