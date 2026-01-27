# API Design

**The Standard** | APIs are contracts. Contracts demand clarity.

**Authority**: [07_STANDARDS.md](../../07_STANDARDS.md) | **Status**: CANONICAL

---

## THIS IS THE HUB

```
         ┌───────────────────────────────────────┐
         │        api_design/INDEX.md            │
         │    START/END for api_design layer     │
         └─────────────────┬─────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
    [REST]            [ERRORS]          [VERSIONING]
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                   [DOCUMENTATION]
                           │
                      UP → INDEX
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [standards/INDEX.md](../INDEX.md) (parent layer) |
| **DOWN** | Four primitives (see Quick Reference) |
| **ACROSS** | [error_handling/](../error_handling/), [security/](../security/) |

---

## Quick Reference

| Primitive | What It Covers | Go Here |
|-----------|----------------|---------|
| REST | Resource URLs, HTTP methods, status codes, naming | [REST.md](REST.md) |
| Errors | Error response format, error codes, security | [ERRORS.md](ERRORS.md) |
| Versioning | URL path versioning, lifecycle, deprecation | [VERSIONING.md](VERSIONING.md) |
| Documentation | OpenAPI requirements, auto-generation | [DOCUMENTATION.md](DOCUMENTATION.md) |

---

## Documents

| Document | Lines | Purpose |
|----------|-------|---------|
| [REST.md](REST.md) | 100 | RESTful conventions |
| [ERRORS.md](ERRORS.md) | 90 | Error response patterns |
| [VERSIONING.md](VERSIONING.md) | 80 | API versioning strategies |
| [DOCUMENTATION.md](DOCUMENTATION.md) | 80 | API documentation standards |

---

## OTHER-Demanded Context

From [STANDARD_DEMAND](../STANDARD_DEMAND.md): API standards exist because OTHERS demand them:

| OTHER | What They Demand |
|-------|------------------|
| Consumers | Predictable interfaces |
| Integrators | Clear documentation |
| Teams | Consistent patterns |

For specific rules and patterns, see individual primitives.

---

## Convergence

### Bottom-Up (requires)

- [STANDARD_DEMAND](../STANDARD_DEMAND.md) - OTHER demands clarity

### Top-Down (shaped by)

- [06_LAW](../../06_LAW.md) - No Magic pillar (explicit contracts)

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [error_handling/](../error_handling/) | Error response patterns |
| [security/](../security/) | Authentication, input validation |

---

## Industry Alignment

- [OpenAPI Specification](https://spec.openapis.org/)
- [JSON:API](https://jsonapi.org/)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-26 | Reduced to navigation per STANDARD_STRUCTURE | Claude |
| 2026-01-26 | Initial standard with 4 primitives | Claude |

---

*APIs are contracts. Contracts demand clarity.*
