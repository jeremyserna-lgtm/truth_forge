# Error Handling Layer

**What error handling primitives ARE.**

---

## Why This Layer Exists

Errors are inevitable. How we handle them determines whether systems are trustworthy. This layer defines the craft of failing gracefully.

---

## What An Error Handling Primitive IS

An error handling primitive is a **single aspect of failure management** that ensures errors are visible, recoverable, and informative.

Error handling primitives are:
- **Visible**: Errors surface, never silently disappear
- **Recoverable**: System continues or fails safely
- **Informative**: Errors explain what happened and why

Error handling primitives are NOT:
- Happy path logic (that's normal flow)
- Validation rules (that's input)
- Logging (that's observability, though they connect)

---

## The Visibility Principle

A silent error is worse than a loud crash. Error handling primitives ensure every failure is visible to someone who can act on it.

---

## How Primitives Relate

Error handling primitives form a failure management system:

```
Patterns             │  Boundaries
────────────────────────────────────
PATTERNS             │  BOUNDARIES
(how to fail)        │  (where to catch)
                     │
Recovery             │
────────────────────────────────────
DLQ                  │
(nothing lost)       │
```

Patterns define HOW to fail. Boundaries define WHERE. DLQ ensures NOTHING is lost.

---

## UP

[INDEX.md](INDEX.md)
