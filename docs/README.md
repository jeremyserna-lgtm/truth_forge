# Documentation

**What documentation IS. Theory layer of the docs hierarchy.**

**Layer**: Theory (ME)
**Identity**: ME declares what docs ARE

---

## The Three Layers of Docs

| Layer | Location | Identity | Contains |
|-------|----------|----------|----------|
| **Theory (ME)** | `docs/` | What docs ARE | INDEX.md, README.md, category folders |
| **Meta (ME:NOT-ME:OTHER)** | `docs/{category}/` | Joins theory to specifics | INDEX.md, README.md, topic folders |
| **Specifics (NOT-ME)** | `docs/{category}/{topic}/` | Technical files | INDEX.md, specific files |

### The Pattern Repeats

```
docs/                           ← Theory (ME)
├── INDEX.md                    ← Navigation
├── README.md                   ← You are here
├── technical/                  ← Meta layer folder
│   ├── INDEX.md                ← Navigation
│   ├── README.md               ← Definition
│   └── architecture/           ← Specifics layer folder
│       ├── INDEX.md            ← Navigation
│       └── *.md                ← Specific files
```

---

## What Docs ARE

Documentation is the **bridge** between THE FRAMEWORK (which governs) and the work (which is governed).

| Layer | Contains | Purpose |
|-------|----------|---------|
| **Framework** | Theory, Standards | GOVERNS behavior |
| **Docs** | Guides, Context, Records | EXPLAINS and RECORDS |
| **Code/Work** | Implementation | IMPLEMENTS what's governed |

### Docs vs Framework

| Framework | Docs |
|-----------|------|
| MUST/MUST NOT rules | Explanations, examples |
| Prescriptive | Descriptive |
| Enforced | Referenced |
| Canonical standards | Supporting context |

**If it defines what MUST happen → framework/**
**If it explains, records, or provides context → docs/**

---

## The Three Readers

Every document serves THREE readers:

| Reader | Needs | How Docs Serve |
|--------|-------|----------------|
| **ME (Jeremy)** | Context, history, decisions | Personal/, business/, research/ |
| **NOT-ME (Claude)** | Structured, parseable, concise | INDEX files, clear hierarchy |
| **OTHER (Contributors)** | Onboarding, understanding | guides/, technical/ |

---

## Document Categories

### technical/
System architecture, APIs, data models, technical specifications.
**Identity**: NOT-ME (technical implementation)

### business/
Business strategy, products, branding, revenue.
**Identity**: ME:NOT-ME (business joining technical)

### personal/
Jeremy's identity, relationships, Stage 5 context.
**Identity**: ME (Jeremy's cognitive layer)

### operations/
Procedures, tools, manuals, checklists.
**Identity**: NOT-ME (operational implementation)

### research/
Analysis, assessments, market research.
**Identity**: ME:NOT-ME (research informing decisions)

### guides/
How-to guides, tutorials, onboarding.
**Identity**: OTHER (helping new contributors)

### archive/
Deprecated documentation, old versions.
**Identity**: Historical reference

---

## Document Requirements

Per [STANDARD_LIMIT](../framework/standards/STANDARD_LIMIT.md):
- 300 lines maximum per document
- ONE topic per document
- 7±2 major sections

Per [STANDARD_TRIAD](../framework/standards/STANDARD_TRIAD.md):
- INDEX.md at each folder level
- README.md where folder contains 3+ files

---

## UP

[INDEX.md](INDEX.md)
