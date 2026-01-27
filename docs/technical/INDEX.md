# Technical Documentation

**System architecture, data models, infrastructure, integrations.**

**Layer**: Meta (ME:NOT-ME:OTHER) - joins docs theory to technical specifics

---

## THIS IS THE HUB

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [docs/INDEX.md](../INDEX.md) |
| **DOWN** | Architecture, Infrastructure, Integrations, Observability, Specs |

---

## Structure

```
technical/
├── INDEX.md              # You are here
├── README.md             # What technical docs ARE
├── architecture/         # System architecture (specifics)
│   ├── INDEX.md
│   ├── identity/
│   ├── knowledge/
│   ├── methodology/
│   ├── pipelines/
│   ├── services/
│   ├── system/
│   └── zoom/
├── infrastructure/       # Cloud and deployment (specifics)
│   └── INDEX.md
├── integrations/         # External systems (specifics)
│   └── INDEX.md
├── observability/        # Logging and monitoring (specifics)
│   └── INDEX.md
├── specs/                # Technical specifications (specifics)
│   └── INDEX.md
└── *.md                  # Root technical documents
```

---

## Subfolders (Specifics Layer)

| Folder | Purpose | Files |
|--------|---------|-------|
| [architecture/](architecture/) | System architecture - identity, services, pipelines, knowledge | 60+ |
| [infrastructure/](infrastructure/) | BigQuery, cloud, deployment | 15 |
| [integrations/](integrations/) | External system pipelines | 6 |
| [observability/](observability/) | Logging, monitoring, metrics | 8 |
| [specs/](specs/) | Technical specifications | 11 |

---

## Root Documents

| Document | Purpose |
|----------|---------|
| [AI_TRAINING_SYNTHESIS.md](AI_TRAINING_SYNTHESIS.md) | AI training synthesis |
| [CLAUDE_INFRASTRUCTURE.md](CLAUDE_INFRASTRUCTURE.md) | Claude infrastructure |
| [CUSTOM_LLM_DESIGN.md](CUSTOM_LLM_DESIGN.md) | Custom LLM design |
| [MCP_KNOWLEDGE_ATOMS.md](MCP_KNOWLEDGE_ATOMS.md) | MCP knowledge atoms |
| [NOT_ME_UNIFIED_INTERFACE.md](NOT_ME_UNIFIED_INTERFACE.md) | NOT-ME unified interface |
| [THE_SOVEREIGN_DIGITAL_SELF.md](THE_SOVEREIGN_DIGITAL_SELF.md) | Sovereign digital self |
| [VERIFICATION_PATTERN.md](VERIFICATION_PATTERN.md) | Verification patterns |

---

## Quick Reference

| Need | Go To |
|------|-------|
| System architecture overview | [architecture/system/](architecture/system/) |
| Identity resolution | [architecture/identity/](architecture/identity/) |
| Service definitions | [architecture/services/](architecture/services/) |
| Data pipelines | [architecture/pipelines/](architecture/pipelines/) |
| Knowledge systems | [architecture/knowledge/](architecture/knowledge/) |
| Zoom capture | [architecture/zoom/](architecture/zoom/) |
| BigQuery schemas | [infrastructure/](infrastructure/) |

---

## Molt Lineage

```
Truth_Engine/docs/04_technical/ (133 files)
    └── truth_forge/docs/technical/ (Molt - 2026-01-26)
```

---

## UP

[docs/INDEX.md](../INDEX.md)
