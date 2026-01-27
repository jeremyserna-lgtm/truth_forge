# Standard Creation

**Standards must be clear, actionable, and verifiable.**

---

## The Rule

If different readers interpret differently, the standard has failed. Standards must bridge "what" to "how" with verifiable requirements.

---

## Required Elements

Every standard MUST have:

| Element | Purpose |
|---------|---------|
| **Anchor statement** | One-line summary |
| **The Rule** | Core principle |
| **Requirements** | Specific, verifiable rules |
| **Framework Envelope** | How theory layer envelopes this |
| **UP link** | Navigation to INDEX |

---

## Requirement Language

Use RFC 2119 keywords:

| Keyword | Meaning |
|---------|---------|
| **MUST** | Absolute requirement |
| **MUST NOT** | Absolute prohibition |
| **SHOULD** | Recommended, exceptions allowed |
| **SHOULD NOT** | Discouraged, exceptions allowed |
| **MAY** | Optional |

---

## Quality Checks

| Property | Test |
|----------|------|
| **Clarity** | Single interpretation by different readers |
| **Actionable** | Developer can implement without asking |
| **Verifiable** | Can write a test or check for compliance |
| **Scoped** | One concern per standard |

---

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Vague language | "Be secure" means nothing | Specify exactly what |
| No verification | Can't enforce | Add testable criteria |
| Kitchen sink | Too many concerns | Split into multiple standards |
| No escape hatch | Reality requires exceptions | Add override mechanism |

---

## Escape Hatches

Every standard MUST include exception mechanism:

```python
# standard:override [standard]-[requirement] - [justification]
```

See [STANDARD_EXCEPTIONS](STANDARD_EXCEPTIONS.md).

---

## Framework Envelope

This standard is enveloped by:
- [00_GENESIS](../00_GENESIS.md) - THE GRAMMAR (naming)
- [06_LAW](../06_LAW.md) - No Magic principle

---

## UP

[INDEX.md](INDEX.md)
