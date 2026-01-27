# Pipeline Layer

**What pipeline primitives ARE.**

---

## Why This Layer Exists

Pipelines are THE PATTERN made manifest. HOLD → AGENT → HOLD. Data enters, transforms, exits. This layer defines the craft of building data flows that embody the pattern.

---

## What A Pipeline Primitive IS

A pipeline primitive is a **single aspect of data flow** that ensures reliable, observable, recoverable processing.

Pipeline primitives are:
- **Pattern-aligned**: Follows HOLD → AGENT → HOLD
- **Stage-isolated**: Each stage is independent
- **Failure-aware**: Nothing is silently lost

Pipeline primitives are NOT:
- General code patterns (those are code_quality/)
- API endpoints (those are api_design/)
- Database queries (those are persistence)

---

## The Pattern Principle

Every pipeline is HOLD → AGENT → HOLD. The input HOLD receives. The AGENT transforms. The output HOLD delivers. Pipeline primitives ensure each role is honored.

---

## How Primitives Relate

Pipeline primitives form a data flow system:

```
Structure            │  Reliability
────────────────────────────────────
STAGES               │  RECOVERY
(HOLD→AGENT→HOLD)    │  (nothing lost)
CONTRACTS            │  OBSERVABILITY
(data shape)         │  (visibility)
```

Structure defines HOW data flows. Reliability ensures it arrives.

---

## UP

[INDEX.md](INDEX.md)
