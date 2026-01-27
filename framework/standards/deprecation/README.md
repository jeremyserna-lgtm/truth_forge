# Deprecation Layer

**What deprecation primitives ARE.**

---

## Why This Layer Exists

Nothing lives forever. Code, APIs, features—all have lifecycles. This layer defines the craft of ending things gracefully, without breaking what depends on them.

---

## What A Deprecation Primitive IS

A deprecation primitive is a **single aspect of lifecycle management** that ensures smooth transitions from old to new.

Deprecation primitives are:
- **Timeline-aware**: Has clear end dates
- **Migration-friendly**: Path from old to new exists
- **Warning-visible**: Consumers know before it breaks

Deprecation primitives are NOT:
- Bug fixes (that's maintenance)
- Feature removal (that's the end, not the process)
- Versioning (that's api_design/)

---

## The Graceful Exit Principle

Deprecation is a promise: "This will end, but you'll have time." Deprecation primitives ensure that promise is kept through clear warnings, migration paths, and sunset timelines.

---

## How Primitives Relate

Deprecation primitives form a lifecycle system:

```
Warning              │  Transition
────────────────────────────────────
SIGNALS              │  MIGRATION
(advance notice)     │  (path forward)
TIMELINE             │  REMOVAL
(when it ends)       │  (clean exit)
```

Warning announces. Transition guides. Both honor the promise.

---

## UP

[INDEX.md](INDEX.md)
