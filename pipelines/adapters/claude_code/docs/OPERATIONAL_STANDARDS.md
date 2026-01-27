# Operational Standards - Claude Code Pipeline

**Cross-cutting concerns for pipeline hardening. Every stage must comply.**

---

## 1. Loading Strategy: BATCH ONLY

**No streaming. Ever.**

| Method | Cost | Use Case |
|--------|------|----------|
| `load_rows_to_table()` | **FREE** | All bulk inserts |
| `batch_insert_rows()` | **FREE** | Alias for above |
| Streaming insert | $0.012/200MB | **NEVER USE** |

### Why Batch Only

1. **Cost**: Batch loads are FREE. Streaming costs money.
2. **Atomicity**: Batch loads succeed or fail completely. No partial writes.
3. **BigQuery Optimization**: Batch loads bypass quota limits that affect streaming.

### Implementation

```python
from src.services.central_services.core.config import get_bigquery_client

bq = get_bigquery_client()

# CORRECT - Free batch load
bq.load_rows_to_table("spine.entity_unified", rows, tool_name="stage_14")

# WRONG - Never use streaming
# bq.insert_rows_streaming(...)  # This costs money
```

---

## 2. Memory Optimization

**Don't crash the computer. Process in chunks.**

### Batch Size Limits

| Data Type | Max Batch Size | Rationale |
|-----------|----------------|-----------|
| Raw records | 1000 | Memory/processing balance |
| Chunked processing | 500 | Default for heavy transforms |
| LLM enhancement | **10-25** | Prevents hallucination (critical) |
| Embedding generation | 100 | API rate limits |
| BigQuery writes | 10000 | API limit per request |

### The LLM Hallucination Problem

**CRITICAL**: When LLM enhancement stages (text correction, spelling fixes) receive batches that are too large, the LLM hallucinates and **invents new messages that don't exist**.

```python
# DANGEROUS - LLM will hallucinate
batch_size = 100  # Too many messages
for messages in chunk(all_messages, batch_size):
    corrected = llm.correct(messages)  # LLM invents new messages!

# SAFE - Small batches prevent hallucination
LLM_BATCH_SIZE = 10  # Maximum for text enhancement
for messages in chunk(all_messages, LLM_BATCH_SIZE):
    corrected = llm.correct(messages)  # LLM stays grounded
```

### Memory-Safe Processing Pattern

```python
from pipelines.claude_code.scripts.shared.constants import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_CHUNK_SIZE,
)

def process_stage(records: list) -> None:
    """Process records in memory-safe chunks."""
    # Don't load all records at once
    for chunk in batch_generator(records, DEFAULT_CHUNK_SIZE):
        process_chunk(chunk)
        # Allow garbage collection between chunks
        gc.collect()
```

### Constants (from `shared/constants.py`)

```python
DEFAULT_BATCH_SIZE: int = 1000     # General processing
DEFAULT_CHUNK_SIZE: int = 500      # Heavy transforms
DEFAULT_MAX_RETRIES: int = 3       # Retry attempts
DEFAULT_RETRY_DELAYS: tuple = (1, 2, 4)  # Exponential backoff
DEFAULT_TIMEOUT_SECONDS: int = 300  # 5 minutes
```

---

## 3. Schema Validation Between Stages

**Every stage validates its input and output schemas.**

### Input Validation

Before processing, verify:
1. Source table exists
2. Required columns are present
3. Data types match expected schema
4. Row count is non-zero (unless expected empty)

```python
def validate_input(stage: int) -> bool:
    """Validate input from previous stage."""
    source_table = get_stage_table(stage - 1)

    # Check table exists
    if not bq.table_exists(source_table):
        raise ValueError(f"Source table {source_table} does not exist")

    # Check required columns
    schema = bq.get_table_schema(source_table)
    required = get_required_columns_for_stage(stage)
    missing = required - set(schema.keys())
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return True
```

### Output Validation

After processing, verify:
1. Output table was created/updated
2. Row counts match expected (with tolerance for filtering)
3. No NULL values in required columns
4. Entity IDs are valid format

```python
def validate_output(stage: int, expected_count: int) -> bool:
    """Validate output of current stage."""
    output_table = get_stage_table(stage)

    actual_count = bq.get_row_count(output_table)

    # Allow 10% variance for filtering
    if actual_count < expected_count * 0.9:
        raise ValueError(
            f"Output count {actual_count} is less than 90% of "
            f"expected {expected_count}"
        )

    # Verify no NULL entity_ids
    null_count = bq.query(f"""
        SELECT COUNT(*) as nulls
        FROM `{output_table}`
        WHERE entity_id IS NULL
    """)[0]['nulls']

    if null_count > 0:
        raise ValueError(f"Found {null_count} NULL entity_ids")

    return True
```

### Schema Registry

Each stage's expected schema should be defined in `shared/schemas.py`:

```python
STAGE_SCHEMAS = {
    0: ["jsonl_path", "raw_content", "file_hash"],
    1: ["session_id", "conversation_id", "raw_json"],
    2: ["conversation_id", "messages", "metadata"],
    # ... etc
    14: ["entity_id", "level", "text", "parent_id", "conversation_id"],
}
```

---

## 4. Resilience Patterns

**Use central services. Don't reinvent.**

### Circuit Breakers

Prevent cascading failures by opening circuit after N failures.

```python
from src.services.central_services.core.resilience import (
    CircuitBreaker,
    resilient_call,
)

# Option 1: Dedicated circuit breaker
llm_circuit = CircuitBreaker(
    failure_threshold=5,    # Open after 5 failures
    success_threshold=2,    # Close after 2 successes
    timeout_seconds=60.0,   # Try again after 60s
    name="llm_enhancement"
)

def enhance_text(text: str) -> str:
    return llm_circuit.call(llm_client.enhance, text)

# Option 2: Convenience function
result = resilient_call(
    llm_client.enhance,
    circuit_breaker_name="llm_enhancement",
    max_retries=3,
    timeout=30,
    text=text
)
```

### Exponential Backoff with Jitter

Retry with increasing delays plus randomness to prevent thundering herd.

```python
from src.services.central_services.core.resilience import (
    retry_with_backoff,
    RetryConfig,
)

# Using decorator
@retry_with_backoff(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True,  # Prevents thundering herd
    retry_on=(ConnectionError, TimeoutError),
)
def call_external_api():
    return api_client.request()

# Using config object
config = RetryConfig(
    max_attempts=5,
    initial_delay=0.5,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True,
)
```

### Timeout Handling

```python
from src.services.central_services.core.resilience import with_timeout

@with_timeout(timeout_seconds=30.0, default_value=None)
def slow_operation():
    # If this takes > 30s, returns None
    return expensive_computation()
```

### Error Classification

```python
from src.services.central_services.core.resilience import (
    ErrorCategory,
    ErrorSeverity,
    classify_error,
)

try:
    result = api_call()
except Exception as e:
    category = classify_error(e)

    if category == ErrorCategory.TRANSIENT:
        # Retry
        pass
    elif category == ErrorCategory.RATE_LIMIT:
        # Back off
        pass
    elif category == ErrorCategory.PERMANENT:
        # Don't retry
        raise
```

---

## 5. Cost Protection

**Session-wide limits prevent runaway spending.**

### BigQuery Cost Protection (Built-In)

After the $1,090 incident, BigQueryClient has hard limits:

```python
# These are HARD LIMITS - cannot be overridden
SESSION_MAX_BYTES = 5 * 1024**3  # 5GB per session
SESSION_MAX_QUERIES = 500         # 500 queries per session
MAX_BYTES_PER_QUERY = 1 * 1024**3  # 1GB per query

# Warnings
SESSION_WARNING_BYTES = 2 * 1024**3  # Warn at 2GB
```

### Protected Tables

Some tables require explicit opt-in:

```python
PROTECTED_TABLES = frozenset([
    "entity_tokens",
    "spine.entity_tokens",
])

# Querying protected tables requires explicit flag
bq.query(
    "SELECT * FROM spine.entity_tokens",
    allow_protected_tables=True  # Must be explicit
)
```

### Stage Cost Limits

From `shared/constants.py`:

```python
COST_LIMIT_PER_STAGE: float = 5.0   # $5 max per stage
COST_LIMIT_TOTAL: float = 80.0      # $80 max for full pipeline
```

### Dry Run Before Expensive Queries

```python
# Estimate before executing
estimate = bq.dry_run(expensive_query)
print(f"Query will scan {estimate.total_bytes_processed / 1e9:.2f} GB")

if estimate.total_bytes_processed > MAX_BYTES_PER_QUERY:
    raise ValueError("Query too expensive")
```

---

## 6. Entity ID Consistency

**Entity IDs must be consistent across the entire pipeline.**

### Entity ID Format

```
{level_prefix}_L{level:02d}_S_{content_hash}

Examples:
- conv_L08_S_abc123def456  (L8 conversation)
- msg_L05_S_def456ghi789   (L5 message)
- sent_L04_S_ghi789jkl012  (L4 sentence)
```

### Validation

```python
import re

ENTITY_ID_PATTERN = re.compile(
    r'^(conv|turn|msg|sent|span|word|tok)_L(\d{2})_S_[a-f0-9]{12,}$'
)

def validate_entity_id(entity_id: str, expected_level: int) -> bool:
    """Validate entity ID format and level."""
    match = ENTITY_ID_PATTERN.match(entity_id)
    if not match:
        return False

    level = int(match.group(2))
    return level == expected_level
```

### Parent-Child Consistency

- Every entity (except L8) must have a valid parent_id
- parent_id must exist in the same table or previous stage
- Level hierarchy: L8 → L6 → L5 → L4 → L3/L2

---

## 7. Logging Standards

**Use the NEW structured logging from Primitive.core.**

### IMPORTANT: Two Logging Implementations Exist

| Location | Type | Status |
|----------|------|--------|
| `Primitive.core.get_logger` | Structured (JSON, context) | **USE THIS** |
| `src.services.central_services.core.core.get_logger` | Basic Python logging | DEPRECATED |

The observability layer was updated to use structured logging with JSON output and context propagation. **Pipeline stages should use the new logger.**

### Use Primitive Core Logger

```python
# CORRECT - New structured logging
from Primitive.core import get_logger, bind_context, set_run_id

logger = get_logger(__name__)

# Set context once at stage start
set_run_id(run_id)
bind_context(stage=stage, pipeline="claude_code")

# Structured logging - event name + kwargs
logger.info("stage_started", input_table=source_table, output_table=target_table)

# Progress (all context automatically included)
logger.info("processing_progress", count=count, total=total, pct=count/total*100)

# Completion
logger.info("stage_complete", records_processed=count, duration_seconds=duration)
```

### OLD Way (Do Not Use)

```python
# DEPRECATED - Old basic logging
from src.services.central_services.core import get_logger  # Gets OLD logger

logger = get_logger(__name__)
logger.info(f"Stage {stage} starting")  # String formatting, no structure
```

### Structured Logging Benefits

| Feature | Old Logger | New Logger |
|---------|------------|------------|
| Output format | Human-readable string | JSON |
| Context propagation | Manual `extra={}` | Automatic via `bind_context` |
| Run ID tracking | Manual | Automatic |
| Machine parsing | Difficult | Native |
| OpenTelemetry | None | Optional integration |

### Log Levels

| Level | Use For |
|-------|---------|
| DEBUG | Detailed debugging (not in production) |
| INFO | Normal operation milestones |
| WARNING | Recoverable issues |
| ERROR | Failures that need attention |
| CRITICAL | Pipeline-stopping failures |

### Migration Pattern

If updating an existing stage:

```python
# Before (OLD)
from src.services.central_services.core import get_logger
logger = get_logger(__name__)
logger.info(f"Processing {count} records", extra={"count": count})

# After (NEW)
from Primitive.core import get_logger, bind_context, set_run_id
logger = get_logger(__name__)
set_run_id(get_current_run_id())  # Once at start
logger.info("processing_records", count=count)  # Structured!
```

---

## 8. Graceful Degradation

**Fail gracefully, not catastrophically.**

### Partial Success Handling

If some records fail, process the rest:

```python
def process_batch_with_fallback(records: list) -> tuple[list, list]:
    """Process records, returning successes and failures separately."""
    successes = []
    failures = []

    for record in records:
        try:
            result = process_record(record)
            successes.append(result)
        except Exception as e:
            logger.warning(f"Record failed: {e}", extra={
                "record_id": record.get("id"),
                "error": str(e),
            })
            failures.append({
                "record": record,
                "error": str(e),
            })

    # Log failure rate
    failure_rate = len(failures) / len(records) * 100
    if failure_rate > 10:
        logger.warning(f"High failure rate: {failure_rate:.1f}%")

    return successes, failures
```

### Checkpoint and Resume

For long-running stages, save progress:

```python
def process_with_checkpoints(records: list, checkpoint_file: Path):
    """Process with checkpoint support for resume."""
    # Load checkpoint
    processed_ids = set()
    if checkpoint_file.exists():
        processed_ids = set(json.loads(checkpoint_file.read_text()))

    # Filter already processed
    remaining = [r for r in records if r["id"] not in processed_ids]

    for batch in chunk(remaining, BATCH_SIZE):
        process_batch(batch)

        # Update checkpoint
        processed_ids.update(r["id"] for r in batch)
        checkpoint_file.write_text(json.dumps(list(processed_ids)))
```

---

## 9. Standard Stage Template

Every stage script should follow this structure:

```python
"""Stage N: [Description]

OPERATIONAL STANDARDS COMPLIANCE:
- [x] Batch loading only (no streaming)
- [x] Memory-optimized chunking
- [x] Schema validation (input/output)
- [x] Circuit breaker for external calls
- [x] Retry with exponential backoff
- [x] Cost limits enforced
- [x] Entity ID validation
- [x] Consistent logging
"""

from src.services.central_services.core import (
    BigQueryClient,
    get_logger,
)
from src.services.central_services.core.resilience import (
    CircuitBreaker,
    retry_with_backoff,
)
from pipelines.claude_code.scripts.shared.constants import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_CHUNK_SIZE,
    COST_LIMIT_PER_STAGE,
)

logger = get_logger(__name__)

def run_stage(dry_run: bool = False) -> dict:
    """Run stage with full operational compliance."""

    # 1. Validate input schema
    validate_input_schema()

    # 2. Load data in batches
    records = load_in_batches()

    # 3. Process with circuit breaker and retry
    results = process_with_resilience(records)

    # 4. Write output (batch only)
    if not dry_run:
        write_batch_output(results)

    # 5. Validate output schema
    validate_output_schema()

    # 6. Log completion
    logger.info("Stage complete", extra={"records": len(results)})

    return {"success": True, "count": len(results)}
```

---

## Quick Reference

### Import Checklist

```python
# Primitive Core - NEW structured logging (use this!)
from Primitive.core import (
    get_logger,
    get_current_run_id,
    bind_context,
    set_run_id,
    log_event,
    log_cost,
    chunk,  # Memory-safe batching utility
)

# Central services - Config and tracking
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker

# Central services - Resilience (for hardening)
from src.services.central_services.core.resilience import (
    CircuitBreaker,
    RetryConfig,
    retry_with_backoff,
    with_timeout,
    resilient_call,
    ErrorCategory,
    ErrorSeverity,
    get_circuit_breaker,
)

# Central services - Governance (cost limits)
from src.services.central_services.governance.governance import (
    CostGovernance,
    enforce_cost_limits,
)

# Pipeline shared
from pipelines.claude_code.scripts.shared.constants import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAYS,
    DEFAULT_TIMEOUT_SECONDS,
    COST_LIMIT_PER_STAGE,
    COST_LIMIT_TOTAL,
    get_stage_table,
)
from pipelines.claude_code.scripts.shared.config import (
    get_config,
    get_stage_config,
)
```

### Critical Limits

| Limit | Value | Consequence |
|-------|-------|-------------|
| LLM batch size | 10-25 | Hallucination if exceeded |
| Session bytes | 5GB | Query blocked |
| Session queries | 500 | Query blocked |
| Query bytes | 1GB | Query blocked |
| Stage cost | $5 | Stage stopped |
| Total cost | $80 | Pipeline stopped |

### Files Reference

| File | Purpose |
|------|---------|
| `pipelines/claude_code/scripts/shared/constants.py` | All pipeline constants |
| `pipelines/claude_code/scripts/shared/config.py` | Config loader |
| `src/services/central_services/core/resilience.py` | Circuit breakers, retry |
| `src/services/central_services/core/bigquery_client.py` | Cost-protected BQ client |
| `Primitive/core/structured_logging.py` | NEW structured logging |
| `Primitive/core/__init__.py` | Core utilities including batching |

---

*Every stage must comply with these standards. No exceptions.*
