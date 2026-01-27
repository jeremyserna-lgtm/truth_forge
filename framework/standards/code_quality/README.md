# Code Quality Layer

**What code quality primitives ARE.**

---

## Why This Layer Exists

Code is read more than written. Quality code communicates intent to future readers. This layer defines the craft of writing code that others can understand and maintain.

---

## What A Code Quality Primitive IS

A code quality primitive is a **single aspect of code craftsmanship** that improves readability, maintainability, or correctness.

Code quality primitives are:
- **Tool-verifiable**: Can be checked by static analysis
- **Convention-based**: Follows established patterns
- **Reader-focused**: Optimizes for understanding, not cleverness

Code quality primitives are NOT:
- Performance optimizations (those are performance/)
- Architectural patterns (those are architecture)
- Business logic (those are domain)

---

## The Reader Principle

Write code for the reader who comes after. They don't have your context. Code quality primitives ensure they don't need it.

---

## How Primitives Relate

Code quality primitives form a craftsmanship system:

```
Type Safety          │  Documentation
────────────────────────────────────
TYPE_HINTS           │  DOCSTRINGS
(compiler catches)   │  (human reads)
                     │
Static Analysis      │
────────────────────────────────────
STATIC_ANALYSIS      │
(tools enforce)      │
```

Type hints catch errors. Docstrings explain intent. Static analysis enforces both.

---

## UP

[INDEX.md](INDEX.md)
