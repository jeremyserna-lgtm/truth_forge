# Error Handling

**The Standard** | Every failure is anticipated, caught, logged, and recoverable. Never drop data.

**Authority**: [07_STANDARDS.md](../../07_STANDARDS.md) | **Status**: CANONICAL

---

## THIS IS THE HUB

```
         ┌───────────────────────────────────────┐
         │    error_handling/INDEX.md            │
         │       ALPHA of this standard          │
         └─────────────────┬─────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
 [EXCEPTIONS]          [RETRY]              [DLQ]
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                       [BATCH]
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [standards/INDEX.md](../INDEX.md) (parent ALPHA) |
| **DOWN** | Primitives within this standard |
| **ACROSS** | Related standards (logging/, pipeline/) |

---

## Quick Reference

| Requirement | Rule | Details |
|-------------|------|---------|
| Custom Exceptions | Domain-specific hierarchy | [EXCEPTIONS.md](EXCEPTIONS.md) |
| Retry Logic | Exponential backoff with tenacity | [RETRY.md](RETRY.md) |
| Dead Letter Queue | Failed records quarantined | [DLQ.md](DLQ.md) |
| Batch Isolation | One failure doesn't kill batch | [BATCH.md](BATCH.md) |
| Specific Catches | Catch specific, not generic | Below |
| Context | Include operation context in errors | Below |
| Logging | All errors logged with structured data | [../logging/](../logging/) |

---

## Layer Definition

For WHY this layer exists and WHAT an error handling primitive IS, see [README.md](README.md).

---

## Documents

| Document | Lines | Purpose |
|----------|-------|---------|
| [EXCEPTIONS.md](EXCEPTIONS.md) | 80 | Custom exception hierarchy |
| [RETRY.md](RETRY.md) | 100 | Retry patterns with tenacity |
| [DLQ.md](DLQ.md) | 110 | Dead Letter Queue pattern |
| [BATCH.md](BATCH.md) | 100 | Batch error isolation |

---

## WHY (Theory)

### The Fail-Safe Pillar

From 06_LAW: *"Assume every component will fail."*

Errors are not exceptions—they are expectations. Every external call can fail. Every file can be missing. Every network can timeout. The question is not *if* failure happens, but *when* and *how we respond*.

---

## WHAT (Specification)

### Requirements

| Level | Rule |
|-------|------|
| **MUST** | Wrap all external calls in try/catch |
| **MUST** | Catch specific exceptions, not generic |
| **MUST** | Include context (IDs, operation) in errors |
| **MUST** | Log before handling with structured data |
| **MUST** | Preserve stack traces (`raise ... from`) |
| **SHOULD** | Use custom exception classes |
| **SHOULD** | Implement retry with backoff for transient failures |
| **SHOULD** | Use DLQ for batch processing |
| **MUST NOT** | Silent failures (`except: pass`) |
| **MUST NOT** | Expose internal details to users |

### The Pattern

```python
def process_data(document_id: str) -> dict:
    """Process document with proper error handling."""
    try:
        result = external_service.fetch(document_id)
        return transform(result)

    except ConnectionError as e:
        logger.error("Connection failed", extra={
            "document_id": document_id,
            "error": str(e),
        })
        raise TruthEngineError(
            f"Failed to fetch document {document_id}"
        ) from e

    except ValidationError as e:
        logger.warning("Validation failed", extra={
            "document_id": document_id,
            "error": str(e),
        })
        return {"status": "skipped", "reason": str(e)}

    except Exception as e:
        logger.critical("Unexpected error", extra={
            "document_id": document_id,
            "error": str(e),
            "traceback": traceback.format_exc(),
        })
        raise  # Re-raise unexpected errors
```

---

## Escape Hatch

```python
# standard:disable error-handling-specific-exception - Legacy code migration
try:
    legacy_operation()
except Exception as e:  # noqa: broad-except
    handle_legacy_error(e)
```

---

## Enforcement

### Code Review Checklist

- [ ] All external calls have try/catch
- [ ] Exceptions are specific, not generic
- [ ] Error messages include context (IDs, operation)
- [ ] Structured logging before handling
- [ ] No silent failures
- [ ] Transient failures use retry with backoff
- [ ] Batch processing uses DLQ

---

## Pattern Coverage

### ME:NOT-ME

| Aspect | ME (Human) | NOT-ME (AI) |
|--------|------------|-------------|
| **Error messages** | Human-readable context | Structured fields |
| **Stack traces** | Visual debugging | Traceback strings |
| **Recovery** | Manual intervention | Automatic retry/DLQ |

### HOLD:AGENT:HOLD

```
HOLD₁ (Input)           AGENT (Process)           HOLD₂ (Output)
Failed record         → Retry logic              → Success OR
                      → Error capture            → DLQ (quarantine)
```

### TRUTH:MEANING:CARE

| Phase | Application |
|-------|-------------|
| **TRUTH** | The error occurred (raw exception) |
| **MEANING** | Diagnosis (what failed, why) |
| **CARE** | Recovery (retry, DLQ, graceful degradation) |

---

## Convergence

### Bottom-Up Validation

- [STANDARD_CREATION](../STANDARD_CREATION.md) - Template structure
- [STANDARD_RECURSION](../STANDARD_RECURSION.md) - SEE:SEE:DO verification

### Top-Down Validation

- [04_ARCHITECTURE](../../04_ARCHITECTURE.md) - HOLD:AGENT:HOLD pattern
- [06_LAW](../../06_LAW.md) - Fail-Safe pillar
- [03_METABOLISM](../../03_METABOLISM.md) - TRUTH:MEANING:CARE

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [logging/](../logging/) | Errors must use structured logging |
| [pipeline/](../pipeline/) | Pipeline error handling requirements |
| [code_quality/](../code_quality/) | Exception types must be explicit |
| [testing/](../testing/) | Error paths must be tested |

---

## Industry Alignment

- [Tenacity](https://tenacity.readthedocs.io/) - Retry library
- [AWS DLQ Pattern](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [Google SRE Book](https://sre.google/sre-book/embracing-risk/)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-26 | Split into primitives (INDEX + 4 files) | Claude |
| 2026-01-25 | Added DLQ, retry, batch isolation | Claude |

---

*Every failure anticipated. Every record preserved. Never drop data.*
