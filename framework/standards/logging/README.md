# Logging Layer

**What logging primitives ARE.**

---

## Why This Layer Exists

Logs are the system's memory. When something goes wrong at 3am, logs are all you have. This layer defines the craft of creating logs that answer questions before they're asked.

---

## What A Logging Primitive IS

A logging primitive is a **single aspect of observability** that makes system behavior visible and queryable.

Logging primitives are:
- **Structured**: Machine-parseable, not just human-readable
- **Leveled**: Appropriate severity for appropriate audiences
- **Contextual**: Includes correlation IDs, request context

Logging primitives are NOT:
- Print debugging (remove before commit)
- Metrics (those are numbers over time)
- Traces (those are request paths)

---

## The 3am Principle

Design logs for the engineer at 3am who doesn't know this codebase. They need to understand what happened, when, and why—without reading code.

---

## How Primitives Relate

Logging primitives form an observability system:

```
Format               │  Practice
────────────────────────────────────
STRUCTURED           │  LEVELS
(machine-readable)   │  (severity)
                     │  CONTEXT
                     │  (correlation)
```

Format defines HOW to log. Practice defines WHAT and WHEN.

---

## UP

[INDEX.md](INDEX.md)
