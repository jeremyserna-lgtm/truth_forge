# Standard Lifecycle

**Standards have a lifecycle: Draft → Active → Deprecated → Sunset.**

---

## The Rule

Standards that never change become irrelevant. Standards that change without notice break implementations. The lifecycle provides controlled evolution.

---

## Lifecycle Stages

| Stage | Support | New Adoption |
|-------|---------|--------------|
| **DRAFT** | Experimental | Allowed |
| **ACTIVE** | Full | Required |
| **DEPRECATED** | Maintenance | Prohibited |
| **SUNSET** | None | N/A |

---

## DRAFT

```markdown
**Status**: DRAFT
**Draft Started**: YYYY-MM-DD
```

- MAY change without deprecation notice
- MUST NOT be enforced in CI gates
- SHOULD have estimated activation date

---

## ACTIVE

```markdown
**Status**: ACTIVE
**Effective**: YYYY-MM-DD
```

- MUST be enforced for new code
- MUST receive clarifications when ambiguity discovered
- MUST NOT change requirements without deprecation cycle

---

## DEPRECATED

```markdown
**Status**: DEPRECATED
**Deprecated**: YYYY-MM-DD
**Sunset Date**: YYYY-MM-DD
**Migration Guide**: [Link]
```

- MUST include sunset date (minimum 90 days)
- MUST include migration guide
- New code MUST NOT adopt deprecated standards

---

## SUNSET

```markdown
**Status**: SUNSET
**Sunset**: YYYY-MM-DD
**Archive**: [Link]
```

- MUST be removed from active registry
- MUST be moved to archive
- CI MUST block on sunset patterns

---

## Grace Periods

| Scope | Minimum | Recommended |
|-------|---------|-------------|
| Project-local | 30 days | 60 days |
| Organization-wide | 90 days | 180 days |
| Public/External | 365 days | 18-24 months |

---

## Emergency Deprecation

When critical flaw requires immediate action:

```markdown
# standard:override standard-lifecycle-90-day-minimum - Security vulnerability
**Status**: DEPRECATED (EMERGENCY)
**Sunset**: [accelerated date]
**Approved By**: Security Team + Standards Committee
```

---

## Framework Envelope

This standard is enveloped by:
- [02_PERCEPTION](../02_PERCEPTION.md) - SEE:SEE:DO cycle for transitions
- [03_METABOLISM](../03_METABOLISM.md) - TRUTH→MEANING→CARE for evolution

---

## UP

[INDEX.md](INDEX.md)
