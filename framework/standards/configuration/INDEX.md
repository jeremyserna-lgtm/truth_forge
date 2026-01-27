# Configuration

**The Standard** | Configuration externalizes decisions. Code stays constant.

**Authority**: [07_STANDARDS.md](../../07_STANDARDS.md) | **Status**: CANONICAL

---

## THIS IS THE HUB

```
         ┌───────────────────────────────────────┐
         │      configuration/INDEX.md           │
         │   START/END for configuration layer   │
         └─────────────────┬─────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
[ENVIRONMENTS]         [FILES]            [VALIDATION]
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                      [HIERARCHY]
                           │
                      UP → INDEX
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [standards/INDEX.md](../INDEX.md) (parent layer) |
| **DOWN** | Four primitives (see Quick Reference) |
| **ACROSS** | [security/](../security/), [project_structure/](../project_structure/) |

---

## Quick Reference

| Primitive | What It Covers | Go Here |
|-----------|----------------|---------|
| Environments | Env vars, .env files, environment separation | [ENVIRONMENTS.md](ENVIRONMENTS.md) |
| Files | YAML/TOML formats, config structure, loading | [FILES.md](FILES.md) |
| Validation | Startup validation, Pydantic, fail fast | [VALIDATION.md](VALIDATION.md) |
| Hierarchy | Base → env → local layering, deep merge | [HIERARCHY.md](HIERARCHY.md) |

---

## Documents

| Document | Lines | Purpose |
|----------|-------|---------|
| [ENVIRONMENTS.md](ENVIRONMENTS.md) | 90 | Environment variables and separation |
| [FILES.md](FILES.md) | 80 | Config file formats and patterns |
| [VALIDATION.md](VALIDATION.md) | 80 | Config validation at startup |
| [HIERARCHY.md](HIERARCHY.md) | 80 | Config layering and override patterns |

---

## Layer Definition

For WHY this layer exists and WHAT a configuration primitive IS, see [README.md](README.md).

---

## OTHER-Demanded Context

From [STANDARD_DEMAND](../STANDARD_DEMAND.md): Configuration standards exist because OTHERS demand them:

| OTHER | What They Demand |
|-------|------------------|
| Operations | Environment separation (dev/staging/prod) |
| Security | Secrets externalization |
| Developers | Local override capability |

For specific rules and patterns, see individual primitives.

---

## Convergence

### Bottom-Up (requires)

- [STANDARD_DEMAND](../STANDARD_DEMAND.md) - OTHER demands operational clarity

### Top-Down (shaped by)

- [06_LAW](../../06_LAW.md) - No Magic pillar (explicit config)
- [06_LAW](../../06_LAW.md) - Fail-Safe pillar (validate at startup)

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [security/](../security/) | Secrets management |
| [project_structure/](../project_structure/) | Config folder locations |

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-26 | Reduced to navigation per STANDARD_STRUCTURE | Claude |
| 2026-01-26 | Initial standard with 4 primitives | Claude |

---

*Configuration externalizes decisions. Code stays constant.*
