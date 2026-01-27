# Deprecation

**The Standard** | Deprecation honors lineage. The old contains accumulated learning.

**Authority**: [07_STANDARDS.md](../../07_STANDARDS.md) | **Status**: CANONICAL

---

## THIS IS THE HUB

```
         ┌───────────────────────────────────────┐
         │      deprecation/INDEX.md             │
         │       ALPHA of this standard          │
         └─────────────────┬─────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
   [STATES]           [PROCESS]        [VERIFICATION]
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                  [MOLT_ENFORCEMENT]
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [standards/INDEX.md](../INDEX.md) (parent ALPHA) |
| **DOWN** | Primitives within this standard |
| **ACROSS** | Related standards (planning/, document/) |

---

## Quick Reference

| Requirement | Rule | Details |
|-------------|------|---------|
| States | ACTIVE → DEPRECATED → SUNSET → ARCHIVED | [STATES.md](STATES.md) |
| Process | 6-step deprecation process | [PROCESS.md](PROCESS.md) |
| Verification | SEE:DO confirms completion | [VERIFICATION.md](VERIFICATION.md) |
| Molt Enforcement | Molts must be complete in ALL ways | [MOLT_ENFORCEMENT.md](MOLT_ENFORCEMENT.md) |

---

## Layer Definition

For WHY this layer exists and WHAT a deprecation primitive IS, see [README.md](README.md).

---

## Documents

| Document | Lines | Purpose |
|----------|-------|---------|
| [STATES.md](STATES.md) | 80 | Deprecation lifecycle states |
| [PROCESS.md](PROCESS.md) | 80 | Step-by-step deprecation process |
| [VERIFICATION.md](VERIFICATION.md) | 80 | Verifying deprecation is complete |
| [MOLT_ENFORCEMENT.md](MOLT_ENFORCEMENT.md) | 100 | Ensuring molts are complete |

---

## WHY (Theory)

### The Molt Principle

We do not create from scratch. We transform what exists.

```
Prior Architecture → Discovery → Transformation → New Architecture
                         ↓
                   [DEPRECATED]
                   (Prior marked, not destroyed)
```

**Deprecation honors lineage.** The old contains accumulated learning. We mark it as superseded, not destroyed, so the learning remains accessible.

---

## Pattern Coverage

### ME:NOT-ME:OTHER

| Aspect | ME (Human) | NOT-ME (AI) | OTHER (Future) |
|--------|------------|-------------|----------------|
| **Reading deprecated** | Warning headers | Metadata parsing | Historical context |
| **Finding replacements** | "Superseded By" link | Searchable successors | Lineage trail |
| **Understanding history** | Molt documentation | Archive access | Accumulated learning |

### HOLD:AGENT:HOLD

```
HOLD₁ (Input)           AGENT (Process)           HOLD₂ (Output)
Active document       → Deprecation process      → Archived document
Superseded code       → Archive workflow         → Lineage record
```

### TRUTH:MEANING:CARE

| Phase | Application |
|-------|-------------|
| **TRUTH** | This document is superseded (fact of obsolescence) |
| **MEANING** | It is replaced by X (relationship to successor) |
| **CARE** | Archived with lineage (preserves learning) |

---

## Convergence

### Bottom-Up Validation

- [STANDARD_LIFECYCLE](../STANDARD_LIFECYCLE.md) - State management
- [STANDARD_STRUCTURE](../STANDARD_STRUCTURE.md) - Archive locations
- [STANDARD_RECURSION](../STANDARD_RECURSION.md) - SEE:SEE:DO cycle

### Top-Down Validation

- [05_EXTENSION](../../05_EXTENSION.md) - The Molt principle
- [02_PERCEPTION](../../02_PERCEPTION.md) - SEE:SEE:DO cycle
- [00_GENESIS](../../00_GENESIS.md) - Lineage tracking

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [planning/](../planning/) | Molt planning and gates |
| [document/](../document/) | Document structure for deprecated docs |
| [git/](../git/) | Branch management for molts |

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-26 | Split into primitives, added MOLT_ENFORCEMENT | Claude |
| 2026-01-26 | Initial standard | Claude |

---

*Deprecation honors lineage. The old contains accumulated learning.*
