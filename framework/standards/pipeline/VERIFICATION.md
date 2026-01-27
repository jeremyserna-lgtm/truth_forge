# Pipeline Verification

**Testing, data quality, and reference implementation.**

**Status**: ACTIVE
**Owner**: Framework
**Parent**: [INDEX.md](INDEX.md)

---

## Testing Requirements

### Test Structure

```
pipelines/{pipeline}/
└── tests/
    ├── conftest.py           # Shared fixtures
    ├── test_stage_0.py       # Stage 0 tests
    ├── test_stage_3_gate.py  # THE GATE tests
    └── test_integration.py   # Full pipeline tests
```

### Required Tests Per Stage

```python
def test_read_from_hold_1_returns_batch():
    """HOLD₁ read returns list of dicts."""
    data = read_from_hold_1(mock_client)
    assert isinstance(data, list)
    assert all(isinstance(r, dict) for r in data)

def test_process_batch_transforms_correctly():
    """AGENT transforms input correctly."""
    input_data = [{"entity_id": "abc", "content": "test"}]
    result = process_batch(input_data)
    assert len(result) == len(input_data)

def test_write_to_hold_2_calls_bigquery():
    """HOLD₂ write calls BigQuery correctly."""
    write_to_hold_2(mock_client, [{"entity_id": "abc"}])
    mock_client.insert_rows_json.assert_called_once()

def test_empty_input_handled_gracefully():
    """Empty input doesn't raise."""
    result = process_batch([])
    assert result == []
```

### THE GATE (Stage 3) Specific Tests

```python
def test_entity_id_is_32_characters():
    """Entity IDs must be exactly 32 characters."""
    entity_id = generate_entity_id("session", 0, "content")
    assert len(entity_id) == 32

def test_entity_id_is_deterministic():
    """Same input produces same entity_id."""
    id1 = generate_entity_id("session", 0, "content")
    id2 = generate_entity_id("session", 0, "content")
    assert id1 == id2

def test_entity_id_registered():
    """Entity ID is registered with identity_service."""
    with patch("identity_service.register_id") as mock:
        generate_entity_id("session", 0, "content")
        mock.assert_called_once()
```

---

## Data Quality

### Validation Checks

| Check | Rule | Action |
|-------|------|--------|
| entity_id | 32 characters, not null | Reject |
| content_hash | Not null | Reject |
| timestamp | Valid ISO 8601 | Reject |
| source_name | Not null | Reject |

### Validation Function

```python
def validate_record(record: dict) -> tuple[bool, list[str]]:
    """Validate record against quality rules."""
    errors = []

    if not record.get("entity_id"):
        errors.append("entity_id required")
    elif len(record["entity_id"]) != 32:
        errors.append("entity_id must be 32 chars")

    if not record.get("content_hash"):
        errors.append("content_hash required")

    if not record.get("source_name"):
        errors.append("source_name required")

    return (len(errors) == 0, errors)
```

### Stage 15 Final Validation

```python
def final_validation(data: list[dict]) -> dict:
    """Final quality gates before promotion."""
    total = len(data)
    valid = sum(1 for r in data if validate_record(r)[0])

    return {
        "total_records": total,
        "valid_records": valid,
        "invalid_records": total - valid,
        "pass_rate": valid / total if total else 0,
        "gate_passed": (valid / total) >= 0.99 if total else False,
    }
```

---

## Reference Implementation

**Pipeline**: `chatgpt_web`
**Status**: Production (all 16 stages complete)
**Total Entities**: 51.8M in `spine.entity_unified`
**Case Study**: The Clara Arc (31,021 messages, 66 days)

### Industry Alignment

| Industry Standard | Implementation | Status |
|-------------------|----------------|--------|
| Batch Processing | Batch-only, no streaming | ✅ |
| Idempotency | entity_id deduplication | ✅ |
| Observability | PipelineTracker, structured logging | ✅ |
| Fault Tolerance | Retry with backoff, DLQ | ✅ |
| Modular Architecture | 16-stage HOLD→AGENT→HOLD | ✅ |
| Quality Gates | THE GATE (Stage 3), Final Validation | ✅ |
| Type Hints | Required per PEP 484 | ✅ |

---

## Convergence

### Bottom-Up Validation

This document requires:
- [INDEX.md](INDEX.md) - Parent standard
- [testing/](../testing/) - Testing standards
- [QUALITY.md](QUALITY.md) - Quality gates

### Top-Down Validation

This document is shaped by:
- [02_PERCEPTION](../../02_PERCEPTION.md) - SEE:SEE:DO for verification
- [06_LAW](../../06_LAW.md) - Hardening

---

*Test it. Validate it. Verify it. Then verify again.*
