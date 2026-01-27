# Architecture Decision Records (ADRs)

**This is ALPHA of decisions. The ONE place for architectural decisions.**

*Canonical record of why we decided what we decided.*

---

## THIS IS THE HUB

```
         ┌───────────────────────────────────────┐
         │        decisions/INDEX.md             │
         │        ALPHA of this layer            │
         └─────────────────┬─────────────────────┘
                           │
                           ▼
                    [ADR-NNNN.md]
                    Individual decisions
                           │
                   ┌───────▼───────┐
                   │  INDEX.md     │
                   │ (return here) │
                   └───────────────┘
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [framework/INDEX.md](../INDEX.md) (parent ALPHA) |
| **DOWN** | Individual ADR documents |

---

## ADR Registry

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](0001-folder-structure-architecture.md) | Folder Structure Architecture | Accepted | 2026-01-25 |
| [0002](0002-code-quality-as-identity.md) | Code Quality as Claude Identity | Accepted | 2026-01-25 |
| [0003](0003-the-grammar-naming-convention.md) | THE GRAMMAR Naming Convention | Accepted | 2026-01-25 |

---

## ADR Format

```markdown
# ADR-NNNN: Title

**Status**: Proposed | Accepted | Deprecated | Superseded
**Date**: YYYY-MM-DD
**Context**: Brief description of what prompted this decision

## Context
[Detailed description of the problem or situation]

## Decision
[What was decided and why]

## Consequences
[What are the implications of this decision]

## Alternatives Considered
[What other options were evaluated]
```

---

## Key Decisions Summary

### ADR-0001: Folder Structure Architecture
- `framework/` at project root (governs, not describes)
- Core framework files at root of `framework/`
- Standards central, compliance reports colocated with code
- ADRs in `framework/decisions/`

### ADR-0002: Code Quality as Claude Identity
- Standards embedded as identity, not rules
- Five identity standards: type hints, logging, DLQ, retry, static analysis
- "I AM these standards" not "I follow these rules"

### ADR-0003: THE GRAMMAR Naming Convention
- ME (colon, ALL CAPS), US (hyphen, Normal Caps), NOT-ME (underscore, no caps)
- Folders use NOT-ME voice: `truth_forge/`, `src/`
- Grammar is ontology, not formatting

---

*daughters inherit these decisions. they do NOT create their own ADRs for framework-level decisions.*
