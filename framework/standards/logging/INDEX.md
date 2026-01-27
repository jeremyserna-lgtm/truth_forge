# Logging

**The Standard** | Every significant event is captured with structured, searchable, actionable data.

**Authority**: [07_STANDARDS.md](../../07_STANDARDS.md) | **Status**: CANONICAL

---

## THIS IS THE HUB

```
         ┌───────────────────────────────────────┐
         │       logging/INDEX.md                │
         │       ALPHA of this standard          │
         └─────────────────┬─────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
 [STRUCTURED]        [CORRELATION]     [CONFIGURATION]
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                  [PIPELINE_LOGGING]
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [standards/INDEX.md](../INDEX.md) (parent ALPHA) |
| **DOWN** | Primitives within this standard |
| **ACROSS** | Related standards (error_handling/, pipeline/) |

---

## Quick Reference

| Requirement | Rule | Details |
|-------------|------|---------|
| Structured Format | JSON in production | [STRUCTURED.md](STRUCTURED.md) |
| Correlation IDs | Every request traced | [CORRELATION.md](CORRELATION.md) |
| Pipeline Logging | Stage transitions, progress | [PIPELINE_LOGGING.md](PIPELINE_LOGGING.md) |
| Configuration | structlog or stdlib | [CONFIGURATION.md](CONFIGURATION.md) |
| Sensitive Data | Never log credentials, PII | [STRUCTURED.md](STRUCTURED.md) |

---

## Layer Definition

For WHY this layer exists and WHAT a logging primitive IS, see [README.md](README.md).

---

## Documents

| Document | Lines | Purpose |
|----------|-------|---------|
| [STRUCTURED.md](STRUCTURED.md) | 100 | Structured logging format and rules |
| [CORRELATION.md](CORRELATION.md) | 90 | Correlation ID implementation |
| [PIPELINE_LOGGING.md](PIPELINE_LOGGING.md) | 120 | Pipeline-specific patterns |
| [CONFIGURATION.md](CONFIGURATION.md) | 110 | Logger configuration |

---

## WHY (Theory)

### The Observability Imperative

From 06_LAW: *"Every action, every state change, every decision must be observable."*

Logs are the primary mechanism for observability. Without proper logging:
- Debugging becomes archaeology
- Incidents become mysteries
- Audits become impossible
- Costs become invisible

### The Cost Connection

Every log line has a cost (storage, processing, attention). Every missing log line has a cost (debugging time, incident duration, compliance risk). The standard optimizes this tradeoff.

---

## WHAT (Specification)

### Log Levels

| Level | Use When | Example |
|-------|----------|---------|
| DEBUG | Development tracing | `Cache lookup key=user_123` |
| INFO | Normal operations | `Order processed order_id=456` |
| WARNING | Recoverable issues | `Rate limit at 80%` |
| ERROR | Failures requiring attention | `Payment failed reason=declined` |
| CRITICAL | System-wide failures | `Database pool exhausted` |

### Core Rules

| Level | Rule |
|-------|------|
| **MUST** | Use structured JSON format in production |
| **MUST** | Include correlation_id in all logs |
| **MUST** | Never log credentials, PII, or secrets |
| **MUST** | Use ISO 8601 UTC timestamps |
| **MUST NOT** | Use print() for logging |
| **MUST NOT** | Log then throw (double logging) |
| **MUST NOT** | Block on logging in production |

---

## Escape Hatch

```python
# standard:override logging-level - Temporary debug for incident #123
logging.getLogger('module').setLevel(logging.DEBUG)
```

---

## Enforcement

| Tool | Check | Severity |
|------|-------|----------|
| Custom linter | No `print()` statements | error |
| Custom linter | Structured logging format | warning |
| Log scanner | Sensitive data patterns | error |
| CI pipeline | Log configuration present | error |

---

## Pattern Coverage

### ME:NOT-ME

| Aspect | ME (Human) | NOT-ME (AI) |
|--------|------------|-------------|
| **Reading logs** | Linear scan, visual patterns | JSON parsing, field extraction |
| **Searching** | Grep by message text | Query by structured fields |
| **Understanding** | Contextual narrative | Correlation IDs, trace graphs |

### HOLD:AGENT:HOLD

```
HOLD₁ (Input)           AGENT (Process)           HOLD₂ (Output)
Event occurs          → Log formatter            → Structured log entry
Raw data             → Context enrichment       → Observability data
```

### TRUTH:MEANING:CARE

| Phase | Application |
|-------|-------------|
| **TRUTH** | The event occurred (timestamp, what happened) |
| **MEANING** | Context added (correlation_id, operation, severity) |
| **CARE** | Delivered for observability (searchable, actionable) |

---

## Convergence

### Bottom-Up Validation

- [STANDARD_CREATION](../STANDARD_CREATION.md) - Template structure
- [STANDARD_NAMING](../STANDARD_NAMING.md) - Field naming conventions

### Top-Down Validation

- [01_IDENTITY](../../01_IDENTITY.md) - ME:NOT-ME dual-reader principle
- [03_METABOLISM](../../03_METABOLISM.md) - TRUTH:MEANING:CARE for events
- [06_LAW](../../06_LAW.md) - Observability pillar

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [error_handling/](../error_handling/) | Error context for logs |
| [pipeline/](../pipeline/) | Pipeline-specific logging |
| [code_quality/](../code_quality/) | Type hints for logging functions |

---

## Industry Alignment

- [structlog](https://www.structlog.org/) - Modern structured logging
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [12 Factor App: Logs](https://12factor.net/logs)
- [OpenTelemetry Logging](https://opentelemetry.io/docs/concepts/signals/logs/)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-26 | Split into primitives (INDEX + 4 files) | Claude |
| 2026-01-25 | Added structlog patterns, pipeline logging | Claude |

---

*Every significant event captured. Structured. Searchable. Actionable.*
