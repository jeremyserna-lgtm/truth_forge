# API Design Layer

**What API design primitives ARE.**

---

## Why This Layer Exists

APIs are contracts. Consumers depend on them. Breaking changes break trust. This layer defines the craft of designing stable, predictable interfaces.

---

## What An API Primitive IS

An API primitive is a **single aspect of contract design** that affects how consumers interact with the system.

API primitives are:
- **Contract-focused**: Defines expectations between parties
- **Consumer-centric**: Designed for those who consume, not produce
- **Stable**: Changes follow predictable lifecycle

API primitives are NOT:
- Implementation details (those are internal)
- Internal service calls (those are architecture)
- Database schemas (those are data)

---

## The Contract Principle

An API is a promise. Breaking a promise breaks trust. API primitives define HOW to make promises that can be kept and evolved without betrayal.

---

## How Primitives Relate

API primitives form a contract system:

```
Design               │  Lifecycle
────────────────────────────────────
REST (conventions)   │  VERSIONING (evolution)
ERRORS (failure)     │  DOCUMENTATION (discovery)
```

Design defines HOW contracts work. Lifecycle defines HOW contracts evolve.

---

## UP

[INDEX.md](INDEX.md)
