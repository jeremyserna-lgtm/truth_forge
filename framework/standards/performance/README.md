# Performance Layer

**What performance primitives ARE.**

---

## Why This Layer Exists

Performance is about resource efficiency. Users expect responsive applications. Operations expects predictable costs. This layer defines the craft of making systems fast without premature optimization.

---

## What A Performance Primitive IS

A performance primitive is a **single domain of optimization** that can be measured and improved independently.

Performance primitives are:
- **Measurable**: Has metrics that can be profiled
- **Domain-specific**: Addresses one type of resource (CPU, memory, I/O, network)
- **Evidence-based**: Requires measurement before optimization

Performance primitives are NOT:
- General coding practices (those are code_quality/)
- Architectural patterns (those are architecture)
- Premature optimizations (measure first)

---

## The Knuth Principle

> "Premature optimization is the root of all evil."

Every performance primitive begins with measurement. A primitive that encourages optimization without profiling is incomplete.

---

## How Primitives Relate

Performance primitives form an optimization system:

```
Measurement     │  Optimization Domains
───────────────────────────────────────
PROFILING      │  CACHING (memory/speed tradeoff)
(must come     │  DATABASE (query efficiency)
 first)        │  ASYNC (concurrency/parallelism)
```

PROFILING is prerequisite. The others address specific optimization domains.

---

## UP

[INDEX.md](INDEX.md)
