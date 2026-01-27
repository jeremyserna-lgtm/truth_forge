# Molt Standard

**The Standard** | Archive original → Create redirect stub → Shrink source. Never delete without trace.

**Status**: ACTIVE
**Owner**: Framework (DNA)
**Last Updated**: 2026-01-26

---

## Purpose

This standard defines how organisms transform through molt. Molt is **DNA**—every organism inherits this capability. It enables growth by shedding old architecture while preserving lineage.

---

## Quick Reference

**Every molt MUST:**

1. Archive original files before creating stubs
2. Create redirect stubs pointing to new location AND archive
3. Update audit trail (archive/INDEX.md)
4. Verify source folder shrunk (stubs << original size)
5. Preserve complete lineage (who → where → when)
6. Be repeatable (same input → same output)
7. Be reversible (archive enables restoration)

**This is DNA. This is non-negotiable.**

---

## Layer Definition

For WHY this layer exists and WHAT a molt primitive IS, see [README.md](README.md).

---

## Documents

| Document | Purpose | Lines |
|----------|---------|-------|
| [PROCESS.md](PROCESS.md) | Step-by-step molt execution | ~100 |
| [CONFIGURATION.md](CONFIGURATION.md) | molt.yaml specification | ~100 |
| [VERIFICATION.md](VERIFICATION.md) | How to verify molt success | ~80 |

---

## The Molt Pattern

```
HOLD₁ (source)  →  AGENT (molt engine)  →  HOLD₂ (archive + stubs)
```

**The source shrinks. The archive grows. Nothing is lost.**

---

## Molt Triggers

| Trigger | Description |
|---------|-------------|
| **Volume Exceeds Capacity** | Content outgrows container |
| **Pattern Conflict** | New patterns conflict with old |
| **Crisis Reveals Flaw** | Crisis reveals structural weakness |
| **Growth Demands Form** | Growth requires new shape |

---

## Folder Structure

```
truth_forge/
├── src/truth_forge/molt/     # Implementation (DNA)
│   ├── __init__.py
│   ├── engine.py             # Core molt logic
│   ├── config.py             # Configuration loading
│   ├── cli.py                # Command-line interface
│   └── tracking.py           # Lineage tracking
│
├── framework/standards/molt/ # You are here
│   ├── INDEX.md
│   ├── README.md
│   ├── PROCESS.md
│   ├── CONFIGURATION.md
│   └── VERIFICATION.md
│
└── {organism}/archive/       # Where molted content lives
    ├── INDEX.md              # Audit trail
    └── molt_YYYY_MM_DD/      # Dated batches
```

---

## Pattern Coverage

### ME:NOT-ME

Molt serves both:
- **ME** (human): Clear lineage, reversibility, audit trail
- **NOT-ME** (AI): Consistent patterns, machine-readable stubs

### HOLD:AGENT:HOLD

This standard IS THE PATTERN. Source (HOLD₁) → Engine (AGENT) → Archive+Stubs (HOLD₂).

### TRUTH:MEANING:CARE

| Phase | Application |
|-------|-------------|
| **TRUTH** | Content exists in source |
| **MEANING** | Content belongs elsewhere |
| **CARE** | Transformation preserves lineage |

---

## Convergence

### Top-Down (Theory Shapes This)

- [05_EXTENSION](../../05_EXTENSION.md) - THE MOLT, DNA CAPABILITIES
- [03_METABOLISM](../../03_METABOLISM.md) - Transformation patterns

### Bottom-Up (This Requires)

- [STANDARD_MIGRATION](../STANDARD_MIGRATION.md) - Migration lifecycle
- [STANDARD_CARE](../STANDARD_CARE.md) - Pattern carries burden

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [deprecation/](../deprecation/) | Deprecation patterns |
| [document/](../document/) | Document standards |
| [STANDARD_MIGRATION](../STANDARD_MIGRATION.md) | Full migration lifecycle |

---

*Archive original → Create stub → Shrink source. DNA capability.*
