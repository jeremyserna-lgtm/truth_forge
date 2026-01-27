# Project Structure

**The Standard** | Industry-standard structure, unique thinking. Compete at architecture, not scaffolding.

**Authority**: [07_STANDARDS.md](../../07_STANDARDS.md) | **Status**: CANONICAL

---

## THIS IS THE HUB

```
         ┌───────────────────────────────────────┐
         │   project_structure/INDEX.md          │
         │       ALPHA of this standard          │
         └─────────────────┬─────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
  [UNIVERSAL]        [GENESIS_ONLY]       [PIPELINE]
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                       [FOLDERS]
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [standards/INDEX.md](../INDEX.md) (parent ALPHA) |
| **DOWN** | Primitives within this standard |
| **ACROSS** | Related standards (pipeline/, configuration/) |

---

## Quick Reference

| Requirement | Rule | Details |
|-------------|------|---------|
| Universal Structure | All organisms share same layout | [UNIVERSAL.md](UNIVERSAL.md) |
| Genesis-Only | framework/ only in genesis | [GENESIS_ONLY.md](GENESIS_ONLY.md) |
| Pipeline Architecture | HOLD→AGENT→HOLD for data | [PIPELINE.md](PIPELINE.md) |
| Folder Purposes | What each folder is for | [FOLDERS.md](FOLDERS.md) |
| Naming | snake_case for folders | [FOLDERS.md](FOLDERS.md) |

---

## Layer Definition

For WHY this layer exists and WHAT a project structure primitive IS, see [README.md](README.md).

---

## Documents

| Document | Lines | Purpose |
|----------|-------|---------|
| [UNIVERSAL.md](UNIVERSAL.md) | 90 | Universal folder structure |
| [GENESIS_ONLY.md](GENESIS_ONLY.md) | 80 | Genesis-specific additions |
| [PIPELINE.md](PIPELINE.md) | 80 | Pipeline architecture |
| [FOLDERS.md](FOLDERS.md) | 80 | Folder purposes and git status |

---

## WHY (Theory)

### Compete at Architecture, Not Scaffolding

All organisms use industry-standard folder structures. The differentiation is in THE FRAMEWORK, not in folder naming. This enables:
- Familiarity for new contributors (OTHER)
- Tool compatibility (NOT-ME)
- Focus on what matters: the thinking, not the scaffolding (ME)

### Industry Alignment

| Pattern | Standard | Source |
|---------|----------|--------|
| src layout | Python Packaging Guide | packaging.python.org |
| Modular pipelines | Kedro, Dagster | kedro.org |
| Config-driven adapters | Kedro parameters | kedro.org |
| conf/base + conf/local | Environment separation | Kedro |

---

## Pattern Coverage

### ME:NOT-ME:OTHER

| Aspect | ME (Human) | NOT-ME (AI) | OTHER (Industry) |
|--------|------------|-------------|------------------|
| **Finding files** | Folder hierarchy | Glob patterns | IDE integration |
| **Understanding** | README, visual | INDEX.md files | Standard conventions |
| **Creating files** | Know where things go | Match patterns | Tool compatibility |

### HOLD:AGENT:HOLD

```
data/staging/         → pipelines/core/        → data/output/
(HOLD₁ - input)         (AGENT - process)        (HOLD₂ - output)
```

---

## Convergence

### Bottom-Up Validation

- [STANDARD_STRUCTURE](../STANDARD_STRUCTURE.md) - Folder structure rules
- [STANDARD_NAMING](../STANDARD_NAMING.md) - THE GRAMMAR for folders

### Top-Down Validation

- [00_GENESIS](../../00_GENESIS.md) - THE GRAMMAR for naming
- [04_ARCHITECTURE](../../04_ARCHITECTURE.md) - HOLD:AGENT:HOLD

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [pipeline/](../pipeline/) | Pipeline processing details |
| [configuration/](../configuration/) | Config management |
| [git/](../git/) | Version control patterns |

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-26 | Split into primitives (INDEX + 4 files) | Claude |
| 2026-01-26 | Initial standard | Claude |

---

*Industry-standard structure, unique thinking. Compete at architecture, not scaffolding.*
