# Configuration Layer

**What configuration primitives ARE.**

---

## Why This Layer Exists

Configuration externalizes decisions. Code should be constant; behavior should be configurable. This layer defines the craft of separating what changes from what doesn't.

---

## What A Configuration Primitive IS

A configuration primitive is a **single aspect of externalization** that allows runtime behavior change without code modification.

Configuration primitives are:
- **External**: Lives outside code, can be changed independently
- **Environment-aware**: Varies by deployment context
- **Validated**: Fails fast on invalid configuration

Configuration primitives are NOT:
- Code constants (those are code)
- Feature flags (those are product decisions)
- Hardcoded values (anti-pattern)

---

## The Externalization Principle

If a value might change between deployments, it's configuration. If it's part of business logic, it's code. Configuration primitives define WHERE that boundary is and HOW values cross it.

---

## How Primitives Relate

Configuration primitives form an externalization system:

```
Sources              │  Processing
────────────────────────────────────
ENVIRONMENTS (.env)  │  VALIDATION (fail fast)
FILES (yaml/toml)    │  HIERARCHY (layering)
```

Sources define WHERE config comes from. Processing defines HOW it's consumed.

---

## UP

[INDEX.md](INDEX.md)
