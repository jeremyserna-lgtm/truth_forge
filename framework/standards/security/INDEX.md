# Security

**The Standard** | Security is not optional. OTHERS demand it.

**Authority**: [07_STANDARDS.md](../../07_STANDARDS.md) | **Status**: CANONICAL

---

## THIS IS THE HUB

```
         ┌───────────────────────────────────────┐
         │        security/INDEX.md              │
         │     START/END for security layer      │
         └─────────────────┬─────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
[INPUT_VALIDATION]  [AUTHENTICATION]      [SECRETS]
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                       [OWASP]
                           │
                      UP → INDEX
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [standards/INDEX.md](../INDEX.md) (parent layer) |
| **DOWN** | Four primitives (see Quick Reference) |
| **ACROSS** | [error_handling/](../error_handling/), [logging/](../logging/), [configuration/](../configuration/) |

---

## Quick Reference

| Primitive | What It Covers | Go Here |
|-----------|----------------|---------|
| Input Validation | Validation boundaries, sanitization, injection prevention | [INPUT_VALIDATION.md](INPUT_VALIDATION.md) |
| Authentication | Auth methods, password hashing, JWT, OAuth | [AUTHENTICATION.md](AUTHENTICATION.md) |
| Secrets | Environment variables, .gitignore, secret detection | [SECRETS.md](SECRETS.md) |
| OWASP | Top 10 awareness, threat checklist | [OWASP.md](OWASP.md) |

---

## Layer Definition

For WHY this layer exists and WHAT a security primitive IS, see [README.md](README.md).

---

## Documents

| Document | Lines | Purpose |
|----------|-------|---------|
| [INPUT_VALIDATION.md](INPUT_VALIDATION.md) | 90 | Input validation patterns |
| [AUTHENTICATION.md](AUTHENTICATION.md) | 110 | Authentication best practices |
| [SECRETS.md](SECRETS.md) | 128 | Secrets management |
| [OWASP.md](OWASP.md) | 110 | OWASP Top 10 awareness |

---

## OTHER-Demanded Context

From [STANDARD_DEMAND](../STANDARD_DEMAND.md): Security exists because OTHERS demand it:

| OTHER | What They Demand |
|-------|------------------|
| Attackers | Exploit any weakness (see OWASP.md) |
| Regulations | GDPR, PCI, HIPAA compliance |
| Users | Their data protected |
| Employers | Secure code |

For threat details and prevention patterns, see individual primitives.

---

## Convergence

### Bottom-Up (requires)

- [STANDARD_DEMAND](../STANDARD_DEMAND.md) - OTHER demands security

### Top-Down (shaped by)

- [06_LAW](../../06_LAW.md) - Fail-Safe pillar

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [error_handling/](../error_handling/) | Secure error messages |
| [logging/](../logging/) | No secrets in logs |
| [configuration/](../configuration/) | Secrets management |

---

## Industry Alignment

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-26 | Reduced to navigation per STANDARD_STRUCTURE | Claude |
| 2026-01-26 | Initial standard with 4 primitives | Claude |

---

*Security is not optional. OTHERS demand it.*
