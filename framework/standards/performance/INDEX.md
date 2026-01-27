# Performance

**The Standard** | Measure first. Optimize what matters.

**Authority**: [07_STANDARDS.md](../../07_STANDARDS.md) | **Status**: CANONICAL

---

## THIS IS THE HUB

```
         ┌───────────────────────────────────────┐
         │       performance/INDEX.md            │
         │    START/END for performance layer    │
         └─────────────────┬─────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
  [PROFILING]          [CACHING]          [DATABASE]
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                       [ASYNC]
                           │
                      UP → INDEX
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [standards/INDEX.md](../INDEX.md) (parent layer) |
| **DOWN** | Four primitives (see Quick Reference) |
| **ACROSS** | [logging/](../logging/), [testing/](../testing/) |

---

## Quick Reference

| Primitive | What It Covers | Go Here |
|-----------|----------------|---------|
| Profiling | Measurement tools, timing, production profiling | [PROFILING.md](PROFILING.md) |
| Caching | Cache layers, invalidation strategies, TTL | [CACHING.md](CACHING.md) |
| Database | N+1 prevention, indexing, query optimization | [DATABASE.md](DATABASE.md) |
| Async | async/await patterns, concurrent I/O, event loop | [ASYNC.md](ASYNC.md) |

---

## Documents

| Document | Lines | Purpose |
|----------|-------|---------|
| [PROFILING.md](PROFILING.md) | 90 | Measurement and profiling patterns |
| [CACHING.md](CACHING.md) | 90 | Caching strategies and invalidation |
| [DATABASE.md](DATABASE.md) | 90 | Database performance patterns |
| [ASYNC.md](ASYNC.md) | 80 | Async/await patterns |

---

## Layer Definition

For WHY this layer exists and WHAT a performance primitive IS, see [README.md](README.md).

---

## OTHER-Demanded Context

From [STANDARD_DEMAND](../STANDARD_DEMAND.md): Performance standards exist because OTHERS demand them:

| OTHER | What They Demand |
|-------|------------------|
| Users | Responsive applications |
| Operations | Predictable resource usage |
| Business | Efficient compute costs |

For specific rules and patterns, see individual primitives.

---

## The Knuth Principle

> "Premature optimization is the root of all evil."

See [PROFILING.md](PROFILING.md) for the measure-first approach.

---

## Convergence

### Bottom-Up (requires)

- [STANDARD_DEMAND](../STANDARD_DEMAND.md) - OTHER demands responsiveness

### Top-Down (shaped by)

- [06_LAW](../../06_LAW.md) - Observability pillar (metrics)

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [logging/](../logging/) | Performance metrics logging |
| [testing/](../testing/) | Performance regression tests |

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-26 | Reduced to navigation per STANDARD_STRUCTURE | Claude |
| 2026-01-26 | Initial standard with 4 primitives | Claude |

---

*Measure first. Optimize what matters.*
