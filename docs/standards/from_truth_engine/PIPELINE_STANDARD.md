# Pipeline Standard

**The Standard** | The single source of truth for all pipeline development in Truth Engine.

**Status**: CANONICAL
**Version**: 1.0.0
**Created**: 2026-01-25
**Author**: Truth Engine Framework
**Supersedes**:
- `PIPELINE_PATTERN_SPECIFICATION.md` (archived)
- `UNIVERSAL_PIPELINE_PATTERN.md` (archived)

---

## TL;DR

**Every pipeline MUST:**

1. Follow `HOLD → AGENT → HOLD` pattern at every stage
2. Use **batch loading only** - no streaming
3. Connect stages at HOLDs, never at AGENTs
4. Use `identity_service` for all ID generation (THE GATE - Stage 3)
5. Include Stage Five Grounding documentation
6. Register with PipelineTracker for monitoring
7. Apply THE FURNACE PRINCIPLE: Truth → Meaning → Care
8. Use **type hints** on all functions (PEP 484)
9. Implement **retry logic with exponential backoff** for external calls
10. Use **structured logging** with key-value pairs
11. Quarantine failures to **dead letter queue** (never drop data)
12. Pass **mypy, ruff, pytest** before merge

**This is not optional. This is the standard.**

---

## 1. The Universal Pattern

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

## 2. Batch Loading Only

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

## 3. The 16-Stage Pipeline

### Stage Overview

| Stage | Name | Purpose | HOLD₂ Output |
|-------|------|---------|--------------|
| **0** | Assessment | Analyze source format | Assessment report |
| **1** | Extraction | Parse raw exports | `stage_1` (raw) |
| **2** | Cleaning | Normalize, deduplicate | `stage_2` (cleaned) |
| **3** | Validation (THE GATE) | Generate entity_ids | `stage_3` (validated) |
| **4** | Staging | Prepare for entities | `stage_4` (staged) |
| **5** | L1 Tokens | Level 1 token entities | `stage_5` (L1) |
| **6** | L3 Sentences | Level 3 sentence entities | `stage_6` (L3) |
| **7** | L5 Messages | Level 5 message entities | `stage_7` (L5) |
| **8** | L8 Conversations | Level 8 conversation entities | `stage_8` (L8) |
| **9** | Embeddings | Vector representations | `stage_9` (embedded) |
| **10** | LLM Extraction | Entity/concept extraction | `stage_10` (extracted) |
| **11** | Sentiment | Emotional analysis | `stage_11` (sentiment) |
| **12** | Topics | Topic modeling | `stage_12` (topics) |
| **13** | Relationships | Entity linking, graphs | `stage_13` (linked) |
| **14** | Aggregation | Metrics rollup | `stage_14` (aggregated) |
| **15** | Final Validation | Quality gates | `stage_15` (validated) |
| **16** | Promotion | Write to production | `spine.entity_unified` |

### The Four Phases

#### Phase 1: Ingestion (Stages 0-4)

```
Raw Export → Assessment → Extraction → Cleaning → Validation → Staging
```

- **Stage 0**: Understand what you have (format discovery)
- **Stage 1**: Extract structured data from raw format
- **Stage 2**: Normalize and deduplicate
- **Stage 3**: THE GATE - generate entity_ids via identity_service
- **Stage 4**: Prepare data structure for SPINE entity creation

#### Phase 2: Entity Creation (Stages 5-8)

```
Staged Data → L1 Tokens → L3 Sentences → L5 Messages → L8 Conversations
```

| Level | Entity Type | Grain | Example Count |
|-------|-------------|-------|---------------|
| L1 | Token | Word/subword | 39.8M |
| L3 | Sentence | Sentence | 1.2M |
| L5 | Message | User/assistant turn | 31K |
| L8 | Conversation | Full dialogue | 351 |

#### Phase 3: Enrichment (Stages 9-13)

```
Entities → Embeddings → LLM Extract → Sentiment → Topics → Relationships
```

- **Stage 9**: 3072-dim embeddings (gemini-embedding-001)
- **Stage 10**: Named entity extraction via LLM
- **Stage 11**: GoEmotions 28-class sentiment analysis
- **Stage 12**: KeyBERT topic extraction
- **Stage 13**: Entity-to-entity relationship graph

#### Phase 4: Finalization (Stages 14-16)

```
Enriched Entities → Aggregation → Validation → Promotion
```

- **Stage 14**: Roll up metrics to conversation/session level
- **Stage 15**: Final quality gates (completeness, consistency)
- **Stage 16**: Atomic write to `spine.entity_unified`

---

## 4. THE GATE: Stage 3 Identity Generation

Stage 3 is THE GATE - where system identities are created and registered.

### Required Implementation

```python
from src.services.central_services.identity_service.service import (
    generate_message_id_from_guid,
    register_id,
    sync_to_bigquery,
)

def generate_entity_id(session_id: str, message_index: int, content: str) -> str:
    """Generate deterministic entity_id."""
    import hashlib

    # Create stable fingerprint
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
    guid = f"{session_id}:{message_index}:{content_hash}"

    # Generate via identity_service
    entity_id = generate_message_id_from_guid(guid, message_index)

    # Register
    register_id(
        entity_id=entity_id,
        entity_type="pipeline_message",
        source="stage_3",
        stable=True,
        metadata={
            "pipeline": "pipeline_name",
            "session_id": session_id,
            "message_index": message_index,
        },
    )

    return entity_id
```

### THE GATE Validation

```python
def validate_gate_requirements(data: List[Dict]) -> bool:
    """All records must pass THE GATE validation."""
    for record in data:
        assert record.get("entity_id"), "entity_id required"
        assert record.get("source_name"), "source_name required"
        assert record.get("content_hash"), "content_hash required"
        assert len(record["entity_id"]) == 32, "entity_id must be 32 chars"
    return True
```

---

## 5. Stage Script Template

Every stage script MUST follow this template:

```python
#!/usr/bin/env python3
"""
Stage {N}: {Stage Name} - {Pipeline Name} Pipeline

HOLD₁ ({input_description}) → AGENT ({process_description}) → HOLD₂ ({output_description})

{Detailed description of stage purpose}

🧠 STAGE FIVE GROUNDING
This stage exists to {primary_purpose}.

Structure: {step1} → {step2} → {step3} (sequential flow)
Purpose: {what_problem_does_this_solve}
Boundaries: {what_is_in_scope_and_out_of_scope}
Control: {how_is_execution_controlled}

⚠️ WHAT THIS STAGE CANNOT SEE
- {blind_spot_1}
- {blind_spot_2}
- {blind_spot_3}

🔥 THE FURNACE PRINCIPLE
- Truth (input): {input_description}
- Heat (processing): {processing_description}
- Meaning (output): {output_description}
- Care (delivery): {delivery_description}

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows the canonical Stage {N} specification.

Enterprise Governance Standards:
- Uses central services for logging with traceability
- Uses PipelineTracker for execution monitoring
- All operations follow universal governance policies
- Comprehensive error handling and validation
- Full audit trail for all operations
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

# Standard imports
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

from src.services.central_services.core import (
    get_current_run_id,
    get_logger,
)
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker

logger = get_logger(__name__)

# Pipeline configuration
PIPELINE_NAME = "{pipeline_name}"
STAGE_NUMBER = {N}
STAGE_NAME = "{stage_name}"

# HOLD locations
HOLD_1 = "{project}.{dataset}.{pipeline}_stage_{N-1}"
HOLD_2 = "{project}.{dataset}.{pipeline}_stage_{N}"

# Batch configuration
BATCH_SIZE = 1000


def read_from_hold_1(client) -> List[Dict[str, Any]]:
    """HOLD₁: Read input data from previous stage (batch)."""
    query = f"""
    SELECT * FROM `{HOLD_1}`
    WHERE entity_id NOT IN (
        SELECT entity_id FROM `{HOLD_2}`
    )
    LIMIT {BATCH_SIZE}
    """
    return [dict(row) for row in client.query(query).result()]


def process_batch(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """AGENT: Transform data according to stage purpose."""
    results = []
    for record in data:
        # Process each record
        processed = transform_record(record)
        results.append(processed)
    return results


def transform_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a single record."""
    # Stage-specific transformation logic
    return record


def write_to_hold_2(client, data: List[Dict[str, Any]]) -> None:
    """HOLD₂: Write output data for next stage (batch)."""
    if not data:
        return

    # Batch insert
    table_ref = client.get_table(HOLD_2)
    errors = client.insert_rows_json(table_ref, data)
    if errors:
        raise RuntimeError(f"BigQuery insert errors: {errors}")


def main():
    """Main execution following THE PATTERN."""
    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME,
        stage=STAGE_NUMBER,
        stage_name=STAGE_NAME,
        run_id=run_id,
    ) as tracker:

        try:
            client = get_bigquery_client()
            total_processed = 0

            while True:
                # SEE: Read batch from HOLD₁
                input_data = read_from_hold_1(client)

                if not input_data:
                    logger.info("No more records to process")
                    break

                tracker.update_progress(items_total=len(input_data))

                # MOVE: Process batch (AGENT)
                output_data = process_batch(input_data)

                # HOLD: Write batch to HOLD₂
                write_to_hold_2(client, output_data)

                total_processed += len(output_data)
                tracker.update_progress(items_processed=total_processed)

                logger.info(f"Processed batch: {len(output_data)} records")

            logger.info(f"Stage {STAGE_NUMBER} completed: {total_processed} total records")
            return 0

        except Exception as e:
            logger.error(f"Stage {STAGE_NUMBER} failed: {e}", exc_info=True)
            return 1


if __name__ == "__main__":
    exit(main())
```

---

## 6. Pipeline Configuration

Every pipeline MUST have a `pipeline_config.yaml`:

```yaml
# pipelines/{pipeline_name}/config/pipeline_config.yaml

pipeline:
  name: pipeline_name
  version: 1.0.0
  source_type: jsonl  # or json, csv, etc.
  description: Pipeline description

  # Cost controls
  cost_limit_per_stage_usd: 5.0
  cost_limit_total_usd: 50.0

  # Execution (BATCH ONLY)
  batch_size: 1000
  parallel_workers: 4
  timeout_minutes: 60

stages:
  0:
    name: assessment
    script: scripts/stage_0/pipeline_stage_0.py
    hold_1: local files
    hold_2: assessment report

  1:
    name: extraction
    script: scripts/stage_1/pipeline_stage_1.py
    hold_1: local files
    hold_2: spine.pipeline_stage_1

  2:
    name: cleaning
    script: scripts/stage_2/pipeline_stage_2.py
    hold_1: spine.pipeline_stage_1
    hold_2: spine.pipeline_stage_2

  3:
    name: validation_gate
    script: scripts/stage_3/pipeline_stage_3.py
    hold_1: spine.pipeline_stage_2
    hold_2: spine.pipeline_stage_3
    uses_identity_service: true

  # ... stages 4-16 follow same pattern

bigquery:
  project: flash-clover-464719-g1
  dataset: spine
  partition_field: content_date
  clustering_fields:
    - source_name
    - level
    - content_date

monitoring:
  register_with_central_service: true
  alert_on_stage_failure: true
  metrics_to_bigquery: true
```

---

## 7. Quality Gates

### Stage 3: THE GATE (Mandatory)

All records must have:
- `entity_id` (32 characters)
- `source_name`
- `content_hash`

### Stage 15: Final Validation (Mandatory)

```python
def validate_final_requirements(data: List[Dict]) -> bool:
    """Final validation before promotion."""
    required_fields = [
        "entity_id", "source_name", "level", "text",
        "content_date", "created_at", "embedding", "sentiment"
    ]

    for record in data:
        for field in required_fields:
            assert record.get(field) is not None, f"{field} required"

    # Completeness check
    levels = {r["level"] for r in data}
    assert levels == {1, 3, 5, 8}, f"All levels required, got {levels}"

    return True
```

---

## 8. Anti-Patterns

### ❌ Streaming Instead of Batch

```python
# WRONG: Streaming
for row in client.query(query).result():
    process_one(row)
    write_one(row)
```

### ❌ Per-Record File I/O

```python
# WRONG: Opens file 286,706 times
for record in records:
    register_id(record)  # Each call opens/reads/writes/closes file
```

### ❌ Direct Stage-to-Stage Communication

```python
# WRONG: Bypasses HOLDs
result = stage_2_process(stage_1_output)
```

### ❌ Missing HOLD Identification

```python
# WRONG: HOLDs not explicit
def process():
    data = get_data()      # Where from?
    save_result(result)    # Where to?
```

### ❌ Skipping Framework Documentation

```python
# WRONG: No Stage Five Grounding, no Furnace Principle
def process():
    pass
```

### ❌ Missing Type Hints

```python
# WRONG: No type hints
def process_batch(data, batch_size=1000):
    return [transform(r) for r in data]

# CORRECT: With type hints
def process_batch(data: List[Dict[str, Any]], batch_size: int = 1000) -> List[Dict[str, Any]]:
    return [transform(r) for r in data]
```

### ❌ Swallowing Errors

```python
# WRONG: Silent failure
try:
    result = transform(record)
except Exception:
    pass  # Data lost forever!

# CORRECT: Quarantine to DLQ
try:
    result = transform(record)
except Exception as e:
    quarantine_to_dlq(record, error=e)
    logger.warning("Record quarantined", extra={"error": str(e)})
```

### ❌ No Retry Logic

```python
# WRONG: Single attempt
result = client.query(query).result()  # Fails on transient error

# CORRECT: Retry with backoff
@retry(stop=stop_after_attempt(5), wait=wait_exponential())
def query_with_retry(client, query):
    return client.query(query).result()
```

### ❌ Unstructured Logging

```python
# WRONG: Unstructured
logger.info(f"Processed {count} records in {time}ms")

# CORRECT: Structured
logger.info("Batch processed", extra={"count": count, "duration_ms": time})
```

---

## 9. Folder Structure

```
pipelines/{pipeline_name}/
├── config/
│   └── pipeline_config.yaml
├── scripts/
│   ├── stage_0/
│   │   └── {pipeline}_stage_0.py
│   ├── stage_1/
│   │   └── {pipeline}_stage_1.py
│   ├── stage_2/
│   │   └── {pipeline}_stage_2.py
│   ├── stage_3/
│   │   └── {pipeline}_stage_3.py    # THE GATE
│   └── ...
├── tests/
│   └── test_{pipeline}_stages.py
└── README.md
```

---

## 10. Implementation Checklist

### For Every New Pipeline

**Architecture:**
- [ ] Pipeline config YAML created
- [ ] Stage 0: Assessment implemented
- [ ] Stage 1: Extraction implemented (batch)
- [ ] Stage 2: Cleaning implemented (batch)
- [ ] Stage 3: THE GATE implemented with identity_service
- [ ] All stages use batch loading (no streaming)
- [ ] HOLD₂ of Stage N = HOLD₁ of Stage N+1

**Documentation:**
- [ ] All stages have Stage Five Grounding
- [ ] All stages have Furnace Principle
- [ ] All functions have docstrings with Args/Returns/Raises

**Code Quality:**
- [ ] All functions have type hints (PEP 484)
- [ ] Code passes `mypy` type checking
- [ ] Code passes `ruff` linting
- [ ] Code formatted with `black` or `ruff format`

**Resilience:**
- [ ] Retry logic with exponential backoff on external calls
- [ ] Dead letter queue for failed records
- [ ] Checkpointing for long-running stages
- [ ] Structured logging with key-value pairs

**Observability:**
- [ ] All stages use PipelineTracker
- [ ] Required log events at each stage
- [ ] Data lineage tracking

**Testing:**
- [ ] Unit tests for transform functions
- [ ] Integration tests for HOLD-to-HOLD flow
- [ ] Tests pass in CI/CD pipeline

**Quality Gates:**
- [ ] THE GATE validation (Stage 3)
- [ ] Final validation (Stage 15)
- [ ] Data quality checks at each stage

### Completion Criteria

A pipeline is complete when:

1. ✅ All stages follow `HOLD → AGENT → HOLD`
2. ✅ All stages use batch loading only
3. ✅ All stages have framework documentation
4. ✅ All stages connect at HOLDs
5. ✅ All stages registered with PipelineTracker
6. ✅ End-to-end execution verified
7. ✅ Data flows correctly through all HOLDs
8. ✅ Type hints on all functions
9. ✅ Retry logic implemented
10. ✅ DLQ pattern implemented
11. ✅ All tests passing
12. ✅ CI/CD pipeline passing

---

## 11. Code Quality Standards

**You are learning to code. This code is your textbook.**

### Type Hints (Required)

All pipeline code MUST use type hints per PEP 484:

```python
from typing import Any, Dict, List, Optional

def process_batch(
    data: List[Dict[str, Any]],
    batch_size: int = 1000,
) -> List[Dict[str, Any]]:
    """Process a batch of records.

    Args:
        data: List of records to process.
        batch_size: Maximum records per batch.

    Returns:
        List of processed records.

    Raises:
        ValueError: If data is empty.
    """
    if not data:
        raise ValueError("Data cannot be empty")
    return [transform_record(record) for record in data]
```

### Docstrings (Required)

Every function MUST have a docstring explaining:
- **What** it does (first line)
- **Args**: Parameters with types
- **Returns**: What it returns
- **Raises**: What exceptions it raises

### Static Analysis (Required)

All pipeline code must pass:
- `mypy` - Type checking
- `ruff` - Linting (replaces flake8, isort, etc.)
- `black` - Formatting (or ruff format)

---

## 12. Error Handling & Retry Logic

**"In production, failure isn't if, but when."**

### Retry with Exponential Backoff (Required)

Use `tenacity` for all external calls:

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from google.api_core.exceptions import ServiceUnavailable, TooManyRequests

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type((ServiceUnavailable, TooManyRequests)),
    before_sleep=lambda retry_state: logger.warning(
        f"Retry {retry_state.attempt_number}/5 after error: {retry_state.outcome.exception()}"
    ),
)
def query_bigquery_with_retry(client, query: str) -> List[Dict[str, Any]]:
    """Execute BigQuery query with exponential backoff."""
    return [dict(row) for row in client.query(query).result()]
```

### Backoff Strategies

| Strategy | Wait Pattern | Use Case |
|----------|--------------|----------|
| **Fixed** | 1s, 1s, 1s | Simple retries |
| **Exponential** | 1s, 2s, 4s, 8s | API rate limits |
| **Exponential + Jitter** | Random(1-2s), Random(2-4s) | Prevent thundering herd |

### Dead Letter Queue Pattern (Required)

Bad records MUST be quarantined, not dropped:

```python
def process_batch_with_dlq(
    data: List[Dict[str, Any]],
    dlq_table: str,
) -> tuple[List[Dict[str, Any]], int]:
    """Process batch, quarantine failures to DLQ.

    Returns:
        Tuple of (successful records, failure count).
    """
    successes: List[Dict[str, Any]] = []
    failures: List[Dict[str, Any]] = []

    for record in data:
        try:
            processed = transform_record(record)
            successes.append(processed)
        except Exception as e:
            # Quarantine with error metadata
            failures.append({
                **record,
                "_error": str(e),
                "_error_type": type(e).__name__,
                "_failed_at": datetime.utcnow().isoformat(),
                "_stage": STAGE_NUMBER,
            })
            logger.warning(f"Record quarantined: {e}")

    # Write failures to DLQ (don't lose data)
    if failures:
        write_to_dlq(failures, dlq_table)

    return successes, len(failures)
```

### Checkpointing (Required for Long-Running Stages)

Enable resume from failure:

```python
def process_with_checkpoint(
    client,
    checkpoint_key: str,
) -> int:
    """Process with checkpoint for resumability."""
    # Load checkpoint
    last_processed_id = load_checkpoint(checkpoint_key)

    query = f"""
    SELECT * FROM `{HOLD_1}`
    WHERE entity_id > '{last_processed_id}'
    ORDER BY entity_id
    LIMIT {BATCH_SIZE}
    """

    rows = query_bigquery_with_retry(client, query)
    if not rows:
        return 0

    # Process batch
    results = process_batch(rows)
    write_to_hold_2(client, results)

    # Save checkpoint (last processed ID)
    save_checkpoint(checkpoint_key, rows[-1]["entity_id"])

    return len(results)
```

---

## 13. Structured Logging

**Logs are your debugging lifeline.**

### Required Log Format

Use structured logging with key-value pairs:

```python
from src.services.central_services.core import get_logger

logger = get_logger(__name__)

# ✅ CORRECT: Structured logging
logger.info(
    "Batch processed",
    extra={
        "run_id": run_id,
        "stage": STAGE_NUMBER,
        "records_processed": len(results),
        "records_failed": failure_count,
        "batch_duration_ms": duration_ms,
    }
)

# ❌ WRONG: Unstructured logging
logger.info(f"Processed {len(results)} records in {duration_ms}ms")
```

### Required Log Events

Every stage MUST log:

| Event | Level | Required Fields |
|-------|-------|-----------------|
| Stage start | INFO | run_id, stage, hold_1, hold_2 |
| Batch start | DEBUG | batch_number, batch_size |
| Batch complete | INFO | records_processed, duration_ms |
| Error | ERROR | error_type, error_message, record_id |
| Retry | WARNING | attempt_number, max_attempts, error |
| Stage complete | INFO | total_processed, total_failed, total_duration_ms |

---

## 14. Data Quality & Validation

### Automated Validation (Required)

Every stage MUST validate data before writing:

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

def validate_record(record: Dict[str, Any], stage: int) -> ValidationResult:
    """Validate a single record for stage requirements."""
    errors: List[str] = []
    warnings: List[str] = []

    # Required fields vary by stage
    required_fields = get_required_fields(stage)
    for field in required_fields:
        if field not in record or record[field] is None:
            errors.append(f"Missing required field: {field}")

    # Type checks
    if "entity_id" in record and len(record["entity_id"]) != 32:
        errors.append(f"Invalid entity_id length: {len(record['entity_id'])}")

    # Warnings (non-fatal)
    if "content" in record and len(record["content"]) > 1_000_000:
        warnings.append(f"Large content field: {len(record['content'])} chars")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
```

### Data Lineage Tracking

Track data provenance through the pipeline:

```python
def add_lineage_metadata(
    record: Dict[str, Any],
    stage: int,
    run_id: str,
) -> Dict[str, Any]:
    """Add lineage tracking metadata to record."""
    return {
        **record,
        "_lineage": {
            "source_stage": stage - 1,
            "current_stage": stage,
            "run_id": run_id,
            "processed_at": datetime.utcnow().isoformat(),
            "pipeline_version": PIPELINE_VERSION,
        }
    }
```

---

## 15. Testing Requirements

### Required Tests

Every stage MUST have:

```python
# tests/test_{pipeline}_stage_{N}.py

import pytest
from unittest.mock import Mock, patch

class TestStageN:
    """Tests for Stage N of the pipeline."""

    def test_transform_record_valid_input(self):
        """Transform should handle valid input correctly."""
        record = {"entity_id": "a" * 32, "content": "test"}
        result = transform_record(record)
        assert result["entity_id"] == record["entity_id"]

    def test_transform_record_missing_field(self):
        """Transform should raise on missing required field."""
        record = {"content": "test"}  # Missing entity_id
        with pytest.raises(ValueError, match="entity_id required"):
            transform_record(record)

    def test_process_batch_empty_input(self):
        """Process batch should handle empty input gracefully."""
        result = process_batch([])
        assert result == []

    def test_process_batch_with_failures(self):
        """Process batch should quarantine failures to DLQ."""
        # Test that bad records go to DLQ, not lost

    @patch("src.services.central_services.core.config.get_bigquery_client")
    def test_integration_hold_to_hold(self, mock_client):
        """Integration test: HOLD₁ → AGENT → HOLD₂."""
        # Test full stage flow
```

### CI/CD Integration

Pipelines must pass in CI before merge:

```yaml
# .github/workflows/pipeline-tests.yml
name: Pipeline Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Type check
        run: mypy pipelines/
      - name: Lint
        run: ruff check pipelines/
      - name: Test
        run: pytest pipelines/ -v --cov
```

---

## 16. Reference Implementation

**Pipeline**: `chatgpt_web`
**Status**: Production (all 16 stages complete)
**Total Entities**: 51.8M in `spine.entity_unified`
**Case Study**: The Clara Arc (31,021 messages, 66 days)

---

## Appendix A: Industry Standards Alignment

This standard aligns with industry best practices from:
- [dbt Labs: Data Pipelines](https://www.getdbt.com/blog/data-pipelines)
- [Airbyte: Idempotency in Data Pipelines](https://airbyte.com/data-engineering-resources/idempotency-in-data-pipelines)
- [Dagster: Data Pipeline Architecture](https://dagster.io/guides/data-pipeline-architecture-5-design-patterns-with-examples)
- [Real Python: Code Quality](https://realpython.com/python-code-quality/)
- [Meta: Python Typing Survey 2025](https://engineering.fb.com/2025/12/22/developer-tools/python-typing-survey-2025-code-quality-flexibility-typing-adoption/)

### Alignment Summary

| Industry Standard | Truth Engine Implementation | Status |
|-------------------|----------------------------|--------|
| **Batch Processing** | Batch-only, no streaming | ✅ Aligned |
| **Idempotency** | entity_id deduplication, LEFT JOIN skip | ✅ Aligned |
| **Observability** | PipelineTracker, structured logging | ✅ Aligned |
| **Fault Tolerance** | Retry with backoff, DLQ | ✅ Aligned |
| **Modular Architecture** | 16-stage HOLD→AGENT→HOLD | ✅ Aligned |
| **Quality Gates** | THE GATE (Stage 3), Final Validation | ✅ Aligned |
| **Type Hints** | Required per PEP 484 | ✅ Aligned |
| **Checkpointing** | Resume from last processed ID | ✅ Aligned |
| **Data Lineage** | _lineage metadata tracking | ✅ Aligned |
| **CI/CD Testing** | mypy, ruff, pytest required | ✅ Aligned |

### What Makes Truth Engine Unique

| Truth Engine Feature | Industry Equivalent |
|---------------------|---------------------|
| **HOLD → AGENT → HOLD** | ETL staging pattern (formalized) |
| **THE GATE (Stage 3)** | Identity resolution / deduplication |
| **Stage Five Grounding** | Documentation standards (enhanced) |
| **THE FURNACE PRINCIPLE** | No direct equivalent (novel) |
| **16-Stage Pipeline** | Comprehensive but not industry standard |

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [PRIMITIVE_PATTERN_SPECIFICATION.md](PRIMITIVE_PATTERN_SPECIFICATION.md) | Script-level HOLD→AGENT→HOLD |
| [../06_THE_STRUCTURE.md](../06_THE_STRUCTURE.md) | Framework foundation |
| [../05_THE_FURNACE.md](../05_THE_FURNACE.md) | Furnace Principle |
| [SERVICE_API_LAYER.md](SERVICE_API_LAYER.md) | Service integration |
| [ERROR_HANDLING.md](ERROR_HANDLING.md) | Error handling standards |
| [LOGGING.md](LOGGING.md) | Logging standards |
| [TESTING.md](TESTING.md) | Testing standards |

---

*This is the single source of truth for pipeline standards. All pipelines MUST follow this specification.*
