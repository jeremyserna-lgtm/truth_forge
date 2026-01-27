# Structured Logging

**All logs MUST be structured JSON in production.**

---

## The Rule

```python
# CORRECT - Structured, queryable
logger.info("Order processed", extra={
    "order_id": order.id,
    "customer_id": customer.id,
    "total": order.total,
    "correlation_id": ctx.correlation_id
})

# WRONG - Unstructured, unqueryable
logger.info(f"Order {order.id} processed for customer {customer.id}")
```

---

## Required Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `timestamp` | When (ISO 8601 UTC) | `2025-01-18T14:30:00.000Z` |
| `level` | Severity | `INFO`, `ERROR` |
| `message` | What happened | `"Order processed"` |
| `correlation_id` | Request trace | `"abc123-def456"` |

---

## Log Levels

| Level | Use When | Example |
|-------|----------|---------|
| DEBUG | Development tracing | `DEBUG: Cache lookup key=user_123` |
| INFO | Normal operations | `INFO: Order processed order_id=456` |
| WARNING | Recoverable issues | `WARNING: Rate limit at 80%` |
| ERROR | Failures requiring attention | `ERROR: Payment failed` |
| CRITICAL | System-wide failures | `CRITICAL: DB pool exhausted` |

---

## Sensitive Data

Logs MUST NOT contain:
- Passwords, API keys, tokens
- Credit card numbers, SSNs
- Personal health information
- Any data subject to compliance (PCI, HIPAA, GDPR)

```python
# CORRECT
logger.info("User authenticated", extra={"user_id": user.id})

# WRONG - exposes password
logger.debug(f"Login attempt: {username}:{password}")
```

---

## Error Logging

ERROR and CRITICAL logs MUST include:
- Exception type and message
- Stack trace (in development) or error reference (in production)
- Operation context
- Recovery action taken or recommended

```python
try:
    process_payment(order)
except PaymentError as e:
    logger.error(
        "Payment processing failed",
        extra={
            "order_id": order.id,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "recovery": "Queued for retry",
            "correlation_id": ctx.correlation_id
        },
        exc_info=True  # Include traceback in dev
    )
```

---

## Anti-Patterns

```python
# NEVER Log Then Throw (double logging)
logger.error("Failed")
raise Exception("Failed")  # Will be logged again

# NEVER Use Print
print("Debug output")  # Unstructured noise

# NEVER Block on Logging
logging.FileHandler(...)  # Can block main thread
```

---

## UP

[logging/INDEX.md](INDEX.md)
