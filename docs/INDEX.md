# Documentation Index

**This is ALPHA of documentation. Theory layer (ME) - defines what docs ARE.**

**Layer**: Theory (ME) → Meta folders (ME:NOT-ME:OTHER) → Specifics folders (NOT-ME)

---

## THIS IS THE HUB

```
         ┌───────────────────────────────────────┐
         │            docs/INDEX.md              │
         │        ALPHA of this layer            │
         └─────────────────┬─────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
  [TECHNICAL]         [BUSINESS]         [PERSONAL]
  technical/          business/          personal/
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                   ┌───────▼───────┐
                   │  INDEX.md     │
                   │ (return here) │
                   └───────────────┘
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [truth_forge/](../) (project root) |
| **DOWN** | Technical, Business, Personal, Operations, Research |
| **ACROSS** | [framework/](../framework/) (governs this layer) |

---

## Layer Definition

For WHY this layer exists and WHAT documentation primitives ARE, see [README.md](README.md).

---

## Structure

```
docs/
├── INDEX.md              # You are here
├── README.md             # What docs ARE
│
├── technical/            # Technical documentation
│   ├── INDEX.md
│   └── *.md
│
├── business/             # Business documentation
│   ├── INDEX.md
│   └── *.md
│
├── personal/             # Personal context (Jeremy's identity, relationships)
│   ├── INDEX.md
│   └── *.md
│
├── operations/           # Operational documentation
│   ├── INDEX.md
│   └── *.md
│
├── research/             # Research and analysis
│   ├── INDEX.md
│   ├── analysis/         # Research analysis
│   ├── foundation/       # Core research foundation
│   ├── exercises/        # Research exercises
│   ├── observations/     # Research observations
│   ├── source_materials/ # Original research materials
│   ├── theoretical/      # Theoretical research
│   └── validation/       # Validation research
│
├── guides/               # How-to guides
│   ├── INDEX.md
│   └── study_guide/      # Study guide materials
│
└── archive/              # Deprecated documentation
    └── INDEX.md
```

---

## Document Categories

| Category | Purpose | Status |
|----------|---------|--------|
| [technical/](technical/) | System architecture, APIs, data models | **Migrated** (118 files) |
| [business/](business/) | Business strategy, products, branding | **Migrated** (189 files) |
| [personal/](personal/) | Jeremy's identity, relationships, context | **Migrated** (36 files) |
| [operations/](operations/) | Operational procedures, tools, manuals | **Migrated** (46 files) |
| [research/](research/) | Research, analysis, assessments | **Migrated** (104 files) |
| [guides/](guides/) | How-to guides, tutorials | **Migrated** (15 files) |
| [archive/](archive/) | Deprecated documentation | INDEX only |

---

## Molt Lineage

```
Truth_Engine/docs/ (1231 files)
    └── truth_forge/docs/ (Molt - 2026-01-26)
        ├── Migrated: 508 files
        └── Remaining: MOLT phase (deprecate sources)
```

---

## The Loop

### Navigation

| Position | Document |
|----------|----------|
| **UP** | [truth_forge/](../) |
| **ACROSS** | [framework/](../framework/) |

---

*Documentation hub. ALPHA of this layer.*
