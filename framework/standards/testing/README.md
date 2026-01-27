# Testing Layer

**What testing primitives ARE.**

---

## Why This Layer Exists

Tests are executable specifications. They prove code works and document how it should work. This layer defines the craft of writing tests that provide confidence.

---

## What A Testing Primitive IS

A testing primitive is a **single aspect of verification** that proves some property of the system.

Testing primitives are:
- **Automated**: Runs without human intervention
- **Deterministic**: Same input, same result
- **Fast** (mostly): Quick enough to run frequently

Testing primitives are NOT:
- Manual QA checklists (those are process)
- Code review (that's human verification)
- Monitoring (that's production observation)

---

## The Confidence Principle

Tests exist to give confidence. A test suite that doesn't increase confidence is ceremony, not verification. Testing primitives define WHAT to test and HOW to prove it works.

---

## How Primitives Relate

Testing primitives form a verification system:

```
Scope                │  Practice
────────────────────────────────────
UNIT                 │  FIXTURES
(single units)       │  (test data)
INTEGRATION          │  COVERAGE
(system boundaries)  │  (completeness)
```

Scope defines WHAT to test. Practice defines HOW.

---

## UP

[INDEX.md](INDEX.md)
