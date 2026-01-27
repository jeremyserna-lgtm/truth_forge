# Standard Compliance

**Compliance must be measurable, auditable, and automated where possible.**

---

## The Rule

If you cannot verify compliance, you cannot enforce the standard. Compliance must be measurable, repeatable, automated, and auditable.

---

## Verification Methods

Every requirement MUST have a verification method:

| Method | Description | Example |
|--------|-------------|---------|
| **Automated Tool** | CLI tool or script | `mypy --strict` |
| **Automated Query** | Search/database query | `grep -r "pattern"` |
| **CI Gate** | Pipeline check | GitHub Action |
| **Manual Review** | Human inspection | Code review checklist |
| **Self-Attestation** | Documented assertion | ADR stating compliance |

---

## Automation Tiers

Verification MUST be automated to the highest practical tier:

| Tier | Name | Description | Example |
|------|------|-------------|---------|
| **T1** | Fully Automated | No human input needed | Type checking, linting |
| **T2** | Semi-Automated | Tool assists human | Coverage reports |
| **T3** | Automated Collection | Manual assessment, automated tracking | Security reviews |
| **T4** | Manual | Human-only verification | Architecture review |

---

## Compliance States

| State | Definition |
|-------|------------|
| **Compliant** | All requirements met |
| **Non-Compliant** | One or more requirements not met |
| **Exception** | Non-compliance with documented approval |
| **Unknown** | Compliance not yet verified |

---

## Reporting Requirements

| Report | Frequency | Content |
|--------|-----------|---------|
| **Dashboard** | Real-time | Current compliance state |
| **Summary** | Weekly | Changes, trends, blockers |
| **Audit** | Quarterly | Full compliance analysis |

---

## Remediation

Non-compliance MUST have a path to compliance:

| Element | Required |
|---------|----------|
| Specific finding | What is non-compliant |
| How to fix | Concrete remediation steps |
| Timeline | When compliance expected |
| Owner | Who is responsible |

---

## CI Integration

| Gate Type | Behavior |
|-----------|----------|
| **Blocking** | Pipeline fails on non-compliance |
| **Warning** | Pipeline succeeds with alert |
| **Informational** | Logged but no gate |

---

## Framework Envelope

This standard is enveloped by:
- [06_LAW](../06_LAW.md) - Observability pillar
- [04_ARCHITECTURE](../04_ARCHITECTURE.md) - HOLD:AGENT:HOLD (verification as agent)

---

## UP

[INDEX.md](INDEX.md)
