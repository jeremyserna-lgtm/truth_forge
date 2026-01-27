# Git

**The Standard** | Git is the memory of transformation. Commits are truth artifacts.

**Authority**: [07_STANDARDS.md](../../07_STANDARDS.md) | **Status**: CANONICAL

---

## THIS IS THE HUB

```
         ┌───────────────────────────────────────┐
         │           git/INDEX.md                │
         │     START/END for git layer           │
         └─────────────────┬─────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
  [BRANCHING]          [COMMITS]        [CODE_REVIEW]
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                      [HISTORY]
                           │
                      UP → INDEX
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [standards/INDEX.md](../INDEX.md) (parent layer) |
| **DOWN** | Four primitives (see Quick Reference) |
| **ACROSS** | [planning/](../planning/), [deprecation/](../deprecation/) |

---

## Quick Reference

| Primitive | What It Covers | Go Here |
|-----------|----------------|---------|
| Branching | GitHub Flow, branch naming, lifecycle | [BRANCHING.md](BRANCHING.md) |
| Commits | Conventional commits, message format, WHY principle | [COMMITS.md](COMMITS.md) |
| Code Review | PR requirements, reviewer responsibilities, automation | [CODE_REVIEW.md](CODE_REVIEW.md) |
| History | Clean history, rebase vs merge, protected branches | [HISTORY.md](HISTORY.md) |

---

## Layer Definition

For WHY this layer exists and WHAT a git primitive IS, see [README.md](README.md).

---

## Documents

| Document | Lines | Purpose |
|----------|-------|---------|
| [BRANCHING.md](BRANCHING.md) | 90 | Branching strategies |
| [COMMITS.md](COMMITS.md) | 100 | Commit message conventions |
| [CODE_REVIEW.md](CODE_REVIEW.md) | 90 | PR and review standards |
| [HISTORY.md](HISTORY.md) | 80 | Git history management |

---

## OTHER-Demanded Context

From [STANDARD_DEMAND](../STANDARD_DEMAND.md): Git standards exist because OTHERS demand them:

| OTHER | What They Demand |
|-------|------------------|
| Collaborators | Clear commit history |
| Employers | Code review process |
| Future maintainers | Understandable diffs |

For specific rules and patterns, see individual primitives.

---

## Convergence

### Bottom-Up (requires)

- [STANDARD_DEMAND](../STANDARD_DEMAND.md) - OTHER demands collaboration

### Top-Down (shaped by)

- [03_METABOLISM](../../03_METABOLISM.md) - TRUTH artifacts
- [05_EXTENSION](../../05_EXTENSION.md) - Molt tracking

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [planning/](../planning/) | Branch planning |
| [deprecation/](../deprecation/) | Molt branches |

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-26 | Reduced to navigation per STANDARD_STRUCTURE | Claude |
| 2026-01-26 | Initial standard with 4 primitives | Claude |

---

*Git is the memory of transformation. Commits are truth artifacts.*
