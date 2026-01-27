# Standard Governance

**Standards must have owners, reviewers, and clear approval authority.**

---

## The Rule

Standards without owners become orphans. Clear governance defines who can do what.

---

## Roles

| Role | Responsibility | Authority |
|------|----------------|-----------|
| **Owner** | Maintain, clarify, evolve | Final technical decisions |
| **Reviewer** | Validate clarity and correctness | Block approval if issues |
| **Approver** | Authorize lifecycle transitions | Activate, deprecate, sunset |
| **Stakeholder** | Provide input | Request changes |

---

## Ownership Rules

Every standard MUST have exactly one owner:

```markdown
# CORRECT
**Owner**: Platform Team

# WRONG: Multiple owners
**Owner**: Platform Team, Security Team

# WRONG: No owner
**Owner**: [None]
```

When multiple teams have interest, one owns, others are stakeholders.

---

## Approval Process

| Change Type | Approver | Process |
|-------------|----------|---------|
| Typo/formatting | Owner | Direct commit |
| Clarification | Owner | PR + 1 review |
| Addition | Owner | PR + 2 reviews |
| Breaking change | Standards Committee | Full review cycle |

---

## Decision Process

- Rough consensus (general agreement, not unanimity)
- Blocking concerns must be documented and addressed
- Same-level ties: more specific wins
- Still tied: newer standard wins

---

## Orphan Prevention

If owner is unresponsive (>5 business days) or team dissolved:
1. Standards Committee identifies orphan
2. Temporary owner assigned
3. New permanent owner within 30 days
4. If no owner found, standard enters deprecation

---

## Framework Envelope

This standard is enveloped by:
- [00_GENESIS](../00_GENESIS.md) - THE GRAMMAR (naming)
- [06_LAW](../06_LAW.md) - Observability (who owns what)

---

## UP

[INDEX.md](INDEX.md)
