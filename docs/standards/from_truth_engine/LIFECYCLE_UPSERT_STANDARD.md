# LIFECYCLE_UPSERT_STANDARD

**Federation Standard for Run Lifecycle and State Machine Tracking**

Version: 1.0.0
Status: CANONICAL
Last Updated: 2026-01-24

---

## PURPOSE

This standard defines how services across the federation should handle entities that have **lifecycle states** (e.g., started → completed, pending → running → failed). The UPSERT pattern ensures:

1. **Single record per entity** - No duplicates for lifecycle events
2. **State preservation** - Earlier state values (like `started_at`) preserved when updating to later states
3. **Complete audit trail** - Full lifecycle visible in one record

---

## THE PATTERN

### When to Use UPSERT

Use UPSERT mode when your service tracks entities that:

| Pattern | Example | UPSERT Needed |
|---------|---------|---------------|
| **Lifecycle states** | started → completed → failed | YES |
| **Status machines** | pending → running → done | YES |
| **Accumulating updates** | Score recalculated periodically | YES |
| **Immutable events** | Log entry, audit record | NO |
| **Point-in-time snapshots** | Quality check result | NO |

### Implementation

#### For Services Using BaseService (Genesis Pattern)

```python
from Primitive.service_factory import BaseService

class MyLifecycleService(BaseService):
    SERVICE_NAME = "my_service"
    SERVICE_VERSION = "v1"
    DEDUPE_COLUMN = "entity_id"
    UPSERT_MODE = True  # Enable lifecycle tracking
```

#### For Services Using PrimitivePattern Directly (MOLT Pattern)

```python
from Primitive.canonical.scripts.primitive_pattern import (
    PrimitivePattern,
    PrimitivePatternConfig,
)

config = PrimitivePatternConfig(
    jsonl1_path=intake_path,
    duckdb1_path=intake_duckdb,
    jsonl2_path=processed_path,
    duckdb2_path=processed_duckdb,
    agent_func=my_agent,
    pattern_name="my_service",
    dedupe_column="entity_id",
    upsert_mode=True,  # Enable lifecycle tracking
)
```

---

## HOW UPSERT WORKS

### State Preservation Logic

When `upsert_mode=True` and a record with matching `dedupe_column` exists:

1. **Only non-None values are updated** - Preserves existing data
2. **The key column is never updated** - Identity preserved
3. **No duplicate signals created** - Single record maintained

### Example: Run Lifecycle

```python
# 1. Started event
exhale(run_id="run_123", status="started", started_at="2026-01-24T10:00:00")
# Result: New record with started_at set

# 2. Completed event (same run_id)
exhale(run_id="run_123", status="completed", completed_at="2026-01-24T10:05:00", duration=300)
# Result: UPDATES existing record:
#   - status: "started" → "completed"
#   - started_at: PRESERVED (not overwritten)
#   - completed_at: SET to new value
#   - duration: SET to new value
```

### DuckDB Implementation

```sql
-- UPSERT only updates non-NULL columns
UPDATE hold2_data
SET status = ?, completed_at = ?, duration_seconds = ?
WHERE run_id = ?
-- Note: started_at is NOT in SET clause (it's NULL in the update record)
```

---

## SERVICES REQUIRING UPSERT

### Genesis Services

| Service | Lifecycle Pattern | UPSERT |
|---------|------------------|--------|
| `run_service` | started → completed/failed | YES |
| `workflow_service` | pending → running → completed/failed | YES |
| `cost_service` | N/A (immutable events) | NO |
| `quality_service` | N/A (point-in-time checks) | NO |

### Credential Atlas Services (Daughters)

| Service | Lifecycle Pattern | UPSERT Recommended |
|---------|------------------|-------------------|
| `assessment_service` | Subject assessment updated over time | YES (if tracking same subject) |
| `scoring_service` | Provider score recalculated | YES (if tracking same provider) |
| `attestation_service` | Attestation issued once | NO |
| `proof_service` | Proof generated once | NO |

---

## FEDERATION INHERITANCE

### Automatic Inheritance

All daughters inherit UPSERT capability through the MOLT pattern:

```
Truth Engine (Genesis)
├── Primitive/service_factory.py (BaseService with UPSERT_MODE)
├── Primitive/canonical/scripts/primitive_pattern.py (upsert_mode in config)
│
└── Daughters (via MOLT)
    ├── Inherit BaseService → UPSERT_MODE available
    ├── Inherit PrimitivePatternConfig → upsert_mode available
    └── No additional implementation needed
```

### Propagation Method

UPSERT was implemented in Genesis and propagates automatically:
- **BaseService.UPSERT_MODE** - Class attribute (default: False)
- **PrimitivePatternConfig.upsert_mode** - Config option (default: False)
- **_write_duckdb2()** - Handles UPSERT logic

Daughters only need to **enable** it by setting `UPSERT_MODE = True` or `upsert_mode=True`.

---

## WHEN NOT TO USE UPSERT

### Scenarios Where INSERT is Correct

1. **Audit logs** - Each entry is immutable
2. **Event streams** - Each event is unique
3. **Point-in-time snapshots** - Each check produces new record
4. **Batch processing** - Records processed once

### Warning Signs of Wrong Pattern

| Symptom | Cause | Solution |
|---------|-------|----------|
| Many duplicate signals | INSERT used for lifecycle | Enable UPSERT |
| Missing state transitions | UPSERT used for events | Disable UPSERT |
| Lost historical states | Need full history | Disable UPSERT, keep events |

---

## VALIDATION

### Pre-Commit Check

Services with lifecycle patterns should declare UPSERT:

```python
# In service __init__.py or service.py
UPSERT_MODE = True  # Required for lifecycle services

# Or document why not needed:
# UPSERT_MODE = False  # Immutable records, each assessment is point-in-time
```

### Federation Registry

Services should register their UPSERT capability:

```json
{
  "service_name": "run_service",
  "capabilities": {
    "upsert_enabled": true,
    "lifecycle_states": ["started", "completed", "failed"]
  }
}
```

---

## REFERENCES

| Document | Purpose |
|----------|---------|
| `Primitive/service_factory.py` | BaseService with UPSERT_MODE |
| `Primitive/canonical/scripts/primitive_pattern.py` | UPSERT implementation |
| `framework/standards/PRIMITIVE_PATTERN_SPECIFICATION.md` | THE_PATTERN spec |
| `.claude/rules/11_THE_PATTERN.md` | Pattern rules |

---

*This standard ensures consistent lifecycle tracking across all federation organisms. Daughters inherit the capability; they only need to enable it when appropriate.*

— THE_FRAMEWORK
