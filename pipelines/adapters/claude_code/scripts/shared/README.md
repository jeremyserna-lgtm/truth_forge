# Claude Code Pipeline - Shared Module Documentation

## Overview

The shared module provides centralized constants, utilities, and configuration for all 17 pipeline stages. Following the Universal Pipeline Pattern, all stages import from this module to ensure consistency and prevent code duplication.

**For Non-Coders**: Think of this as the "common library" that all stages use. Instead of each stage having its own copy of rules and tools, they all share from one place.

## Quick Reference

| Module | What It Does | When to Use It |
|--------|--------------|----------------|
| `constants.py` | Project settings, table names, entity levels | Always - import settings from here |
| `config.py` | Load configuration from TOML files | When you need stage-specific settings |
| `utilities.py` | Common functions (retry, validation, etc.) | When processing data |
| `check_errors.py` | Check pipeline logs for errors | After running a stage |

---

## Module: constants.py

**Purpose**: Single source of truth for all pipeline configuration. NO hardcoded values in stage scripts.

### Key Settings

| Setting | Value | Description |
|---------|-------|-------------|
| `PROJECT_ID` | `flash-clover-464719-g1` | BigQuery project |
| `DATASET_ID` | `spine` | BigQuery dataset |
| `PIPELINE_NAME` | `claude_code` | Pipeline identifier |
| `SOURCE_NAME` | `claude_code` | Data source name |

### Table Names

| Table | Stage | Description |
|-------|-------|-------------|
| `TABLE_STAGE_0` | Stage 0 | Raw import |
| `TABLE_STAGE_1` | Stage 1 | Conversation parsing |
| `TABLE_STAGE_2` | Stage 2 | Message extraction |
| `TABLE_STAGE_3` | Stage 3 | Gate validation |
| `TABLE_STAGE_4` | Stage 4 | Deduplication |
| `TABLE_STAGE_5` | Stage 5 | L8 Conversation + L7 Compaction Segment creation |
| `TABLE_STAGE_6` | Stage 6 | L6 Turn creation |
| `TABLE_STAGE_7` | Stage 7 | L5 Message creation |
| `TABLE_STAGE_8` | Stage 8 | L4 Sentence creation |
| `TABLE_STAGE_9` | Stage 9 | L3 Span creation (NER) |
| `TABLE_STAGE_10` | Stage 10 | L2 Word creation (atomic level) |
| `TABLE_STAGE_11` | Stage 11 | Parent linking |
| `TABLE_STAGE_12` | Stage 12 | Count rollups |
| `TABLE_STAGE_13` | Stage 13 | Validation |
| `TABLE_STAGE_14` | Stage 14 | Entity promotion |
| `TABLE_STAGE_15` | Stage 15 | Final validation |
| `TABLE_ENTITY_UNIFIED` | Stage 16 | Final destination |

### Entity Levels (SPINE Hierarchy)

| Level | Name | Description |
|-------|------|-------------|
| L8 | Conversation | Full session/conversation (Stage 5) |
| L7 | Compaction Segment | Logical groupings within conversation (Stage 5) |
| L6 | Turn | User message + assistant response pair (Stage 6) |
| L5 | Message | Single message - user or assistant (Stage 7) |
| L4 | Sentence | Individual sentences from spaCy (Stage 8) |
| L3 | Span | Named entity spans from NER (Stage 9) |
| L2 | Word | Word tokens - ATOMIC LEVEL (Stage 10) |

**Note**: L2 (Word) is the atomic level. There is no L1 - it was removed to save costs.

### Helper Functions

```python
from shared import get_stage_table, get_full_table_id

# Get table name for a stage
table_name = get_stage_table(5)  # Returns "claude_code_stage_5"

# Get fully qualified table ID
full_id = get_full_table_id("claude_code_stage_5")
# Returns "flash-clover-464719-g1.spine.claude_code_stage_5"
```

---

## Module: config.py

**Purpose**: Load pipeline configuration from TOML file with stage-specific overrides.

### Usage

```python
from shared import get_config, get_stage_config

# Get full configuration
config = get_config()

# Get stage-specific configuration (merged with defaults)
stage_5_config = get_stage_config(5)
```

### Default Configuration Values

| Setting | Default | Description |
|---------|---------|-------------|
| `batch_size` | 1000 | Records per batch |
| `parallel_workers` | 4 | Concurrent workers |
| `timeout_minutes` | 60 | Stage timeout |
| `cost_limit_per_stage_usd` | 5.0 | Max cost per stage |
| `cost_limit_total_usd` | 80.0 | Max total cost |

---

## Module: utilities.py

**Purpose**: Common functions used across all pipeline stages.

### Retry Logic

**For Non-Coders**: When a network error happens, this automatically retries instead of failing immediately.

```python
from shared import retry_with_backoff, is_retryable_error

# Check if an error can be retried
if is_retryable_error(some_error):
    # It's a temporary error, can retry
    pass

# Wrap a function with automatic retry
@retry_with_backoff
def my_function():
    # This will automatically retry on transient failures
    pass
```

### Validation Functions

| Function | What It Checks |
|----------|---------------|
| `validate_input_table_exists()` | Input table exists and has data |
| `validate_gate_no_null_identity()` | No rows have null entity IDs (THE GATE) |
| `verify_row_counts()` | Source/target row counts match expected ratio |

### Data Utilities

| Function | What It Does |
|----------|--------------|
| `create_fingerprint()` | Create deterministic hash from values |
| `chunk_list()` | Split list into smaller chunks |
| `safe_json_loads()` | Parse JSON safely with fallback |
| `merge_rows_to_table()` | Insert/update rows with deduplication |

### Knowledge Atom Utilities

```python
from shared import write_knowledge_atom_to_pipeline_hold2

# Write observation from a stage
write_knowledge_atom_to_pipeline_hold2(
    content="Stage 5 processed 1000 conversations successfully",
    stage=5,
    run_id="run_2026_01_23",
    metadata={"type": "observation"}
)
```

---

## Module: check_errors.py

**Purpose**: Check pipeline logs for errors in a non-coder-friendly way.

### Usage

```bash
# Check for errors in stage 5
python3 pipelines/claude_code/scripts/shared/check_errors.py 5

# Check for errors in stage 5 with a specific run ID
python3 pipelines/claude_code/scripts/shared/check_errors.py 5 --run-id run_2026_01_23
```

### Output Examples

**No errors found:**
```
Checking for Stage 5 errors...
No errors found for Stage 5.
```

**Errors found:**
```
Checking for Stage 5 errors...
Found 3 errors for Stage 5:

1. [2026-01-23 10:15:32] TableNotFoundError: Input table does not exist
2. [2026-01-23 10:15:35] SchemaError: Column 'content_date' has wrong type
3. [2026-01-23 10:15:40] QuotaExceeded: Daily BigQuery quota exceeded

Recommendation: Check the error details above and fix before re-running.
```

---

## How to Import

All modules can be imported from the `shared` package:

```python
# Import constants
from shared import PROJECT_ID, DATASET_ID, PIPELINE_NAME

# Import table names
from shared import TABLE_STAGE_5, TABLE_ENTITY_UNIFIED

# Import entity levels
from shared import LEVEL_CONVERSATION, LEVEL_MESSAGE, LEVEL_SENTENCE

# Import utilities
from shared import (
    retry_with_backoff,
    validate_input_table_exists,
    create_fingerprint,
    merge_rows_to_table,
)

# Import configuration
from shared import get_config, get_stage_config
```

---

## Architecture Notes

### The HOLD Pattern

All utilities follow the HOLD -> AGENT -> HOLD pattern:

```
HOLD₁ (Input)     →  AGENT (Processing)  →  HOLD₂ (Output)
BigQuery table       Stage script            BigQuery table
Previous stage       Transform data          Current stage
```

### Why Shared Modules?

1. **Consistency**: All stages use the same settings
2. **No Duplication**: Change once, apply everywhere
3. **Easy Testing**: Test utilities once, use everywhere
4. **Safe Defaults**: Includes cost limits and validation
5. **Documentation**: One place to understand the system

---

## Common Questions

### Q: How do I add a new constant?

Add it to `constants.py` and export it in `__init__.py`.

### Q: How do I change a setting for one stage?

Use `get_stage_config()` which merges stage-specific settings with defaults.

### Q: How do I check if a stage ran successfully?

Use `check_errors.py`:
```bash
python3 pipelines/claude_code/scripts/shared/check_errors.py [stage_number]
```

### Q: How do I prevent duplicates when re-running a stage?

Use `merge_rows_to_table()` instead of direct INSERT. It uses MERGE (upsert) to prevent duplicates.
