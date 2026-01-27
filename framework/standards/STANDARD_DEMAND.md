# Standard Demand

**Standards exist because THREE audiences demand them: ME, NOT-ME, and OTHER.**

---

## The Rule

We do not choose which standards to have. Standards are demanded by reality.

---

## The Three Audiences

| Audience | WHO | DEMANDS |
|----------|-----|---------|
| **ME** | Jeremy, the human | Clarity, consistency, teachability |
| **NOT-ME** | Claude, the AI | Explicit rules, verifiable patterns, no ambiguity |
| **OTHER** | Industry, users, employers, collaborators | Compliance, interoperability, trust |

---

## Why Standards Are Not Optional

```
ME decides what to build.
NOT-ME builds it.
OTHER validates that it was built correctly.
```

**OTHER is the external validation axis.** Without OTHER:
- Code has no reviewers
- Products have no users
- Systems have no auditors
- Practices have no industry alignment

**OTHERS demand standards we might not choose.** Security exists not because ME finds it interesting, but because OTHERS will reject insecure systems. API design standards exist not because NOT-ME needs them, but because OTHER systems must integrate.

---

## The Completeness Requirement

| If Missing | OTHER Consequence |
|------------|------------------|
| Security standards | Vulnerabilities, breaches, liability |
| API standards | Integration failures, frustrated consumers |
| Testing standards | Unreliable software, lost trust |
| Documentation standards | Unusable systems, support burden |
| Git standards | Merge chaos, lost history, broken CI |

**A missing standard is a gap that OTHERS will expose.**

---

## Standard Categories by Demand Source

| Category | Primary Demander | Why |
|----------|------------------|-----|
| **Code Quality** | ME + NOT-ME | Readable, maintainable code |
| **Testing** | ME + OTHER | Reliability proof for all parties |
| **Security** | **OTHER** | External threat landscape |
| **API Design** | **OTHER** | External consumers need consistency |
| **Git/VCS** | ME + OTHER | Team collaboration, audit trail |
| **Documentation** | **OTHER** | Users/maintainers need guidance |
| **Logging** | ME + OTHER | Debugging + audit requirements |
| **Error Handling** | ME + NOT-ME | Internal reliability |
| **Performance** | **OTHER** | User experience expectations |
| **Configuration** | ME + NOT-ME | Deployment consistency |

---

## The Industry Alignment Imperative

From OWASP, Google, Microsoft, AWS - OTHERS have already defined what standards matter:

| Domain | Industry Source | Implication |
|--------|-----------------|-------------|
| Security | OWASP Top 10, NIST | Non-negotiable baseline |
| API | OpenAPI, REST conventions | Interoperability requirement |
| Git | GitHub Flow, Conventional Commits | Team collaboration standard |
| Testing | pytest, coverage | Quality verification |
| Code Quality | PEP 8, type hints | Language community expectation |

**We don't invent standards. We adopt and adapt what OTHERS have established.**

---

## The Completeness Check

Before claiming standards are "done," verify:

```
□ Does ME have what ME needs? (clarity, teachability)
□ Does NOT-ME have what NOT-ME needs? (explicit rules)
□ Does OTHER have what OTHER demands? (industry alignment)
```

**If any audience is unserved, standards are incomplete.**

---

## Framework Envelope

This standard is enveloped by:
- [01_IDENTITY](../01_IDENTITY.md) - ME:NOT-ME:OTHER triad
- [06_LAW](../06_LAW.md) - Standards are law, not suggestion

---

## UP

[INDEX.md](INDEX.md)
