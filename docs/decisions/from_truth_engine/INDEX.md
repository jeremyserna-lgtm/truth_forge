# Architecture Decision Records (ADRs)

> **MOLT IN PROGRESS**: This ADR registry is being absorbed into truth_forge.
> - **Canonical Location**: [truth_forge/framework/decisions/INDEX.md](../../framework/decisions/INDEX.md)
> - **Status**: Active ADRs migrating to truth_forge

**Location**: `framework/decisions/`
**Purpose**: Permanent record of architectural decisions and their rationale

---

## What Are ADRs?

Architecture Decision Records capture significant architectural decisions along with their context and consequences. They help future developers understand WHY decisions were made, not just WHAT was decided.

---

## Decision Log

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](0001-folder-structure-architecture.md) | Folder Structure Architecture | Accepted | 2026-01-25 |
| [0002](0002-code-quality-as-identity.md) | Code Quality Standards as Claude Identity | **DEPRECATED** → [truth_forge](../../framework/decisions/0002-code-quality-as-identity.md) | 2026-01-25 |
| [0003](0003-the-grammar-naming-convention.md) | THE GRAMMAR Naming Convention | **DEPRECATED** → [truth_forge](../../framework/decisions/0003-the-grammar-naming-convention.md) | 2026-01-25 |

---

## Decision Categories

### Structure & Organization
- **ADR-0001**: Folder structure, framework location, colocated compliance
- **ADR-0003**: THE GRAMMAR naming convention (underscore/lowercase for folders)

### Standards & Quality
- **ADR-0002**: Code quality as identity, verification commands

### Pending Decisions
- Molt strategy from Truth_Engine to truth_forge
- Service API layer requirements
- Identity service architecture (THE GATE)

---

## ADR Lifecycle

| Status | Meaning |
|--------|---------|
| **Proposed** | Under discussion, not yet decided |
| **Accepted** | Decision made, should be followed |
| **Deprecated** | No longer applies, kept for history |
| **Superseded** | Replaced by another ADR (link provided) |

---

## Creating New ADRs

1. Copy template below
2. Use next sequential number: `NNNN-short-description.md`
3. Fill in all sections
4. Update this INDEX
5. Get approval before marking Accepted

### Template

```markdown
# ADR-NNNN: Title

**Status**: Proposed | Accepted | Deprecated | Superseded
**Date**: YYYY-MM-DD
**Context**: Brief description of what prompted this decision

---

## Context
[Detailed description of the problem or situation]

## Decision
[What was decided and why]

## Consequences
[What are the implications of this decision]

## Alternatives Considered
[What other options were evaluated]

## References
[Links to relevant documents, discussions, or external resources]

---

*Decided: YYYY-MM-DD*
*Applies to: [scope of decision]*
```

---

## References

- [ADR GitHub](https://github.com/joelparkerhenderson/architecture-decision-record)
- [MADR - Markdown ADR](https://adr.github.io/madr/)
- [AWS ADR Process](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html)

---

*This index is the authoritative list of all architecture decisions.*
