# 07_STANDARDS

**How We Do Things. Standards as Crystallized Decisions.**

*The Genetic Code of the Organism.*

---

## WHY (Theory)

### Standards as DNA

Standards are the **genetic memory** of the organism (see [08_MEMORY](08_MEMORY.md)).

```
DNA → Protein Synthesis → Consistent Cell Behavior
Standards → Agent Execution → Consistent System Behavior
```

| Biological | Framework |
|------------|-----------|
| Gene | Individual standard (code_quality, logging) |
| Chromosome | Standard category (Meta, Specifics) |
| Genome | Complete standards corpus (standards/INDEX.md) |
| Gene expression | Standard application in context |
| Mutation | Standard evolution via deprecation |

### The Pattern That Repeats

Standards exist because patterns repeat. Every time someone asks "how should I name this?" or "where does this file go?" — that's a pattern. Without standards, each instance requires a decision. Decisions consume cognitive capacity.

**Standards are crystallized decisions. Make the decision once, apply it forever.**

### The Relationship to Law

[06_LAW](06_LAW.md) defines **what must be protected**. Standards define **how to protect it**.

| Law Says | Standards Implement |
|----------|---------------------|
| Fail-Safe | error_handling/, DLQ pattern |
| No Magic | configuration/, explicit settings |
| Observability | logging/, structured logging |
| Idempotency | pipeline/, verification gates |

Standards are Law made operational.

---

## WHAT (Specification)

### The Two Standard Layers

| Layer | What It Contains | Location |
|-------|------------------|----------|
| **Meta (L2)** | Standards about standards | `standards/STANDARD_*.md` |
| **Specifics (L3)** | Technical implementations | `standards/{folder}/` |

See [standards/INDEX.md](standards/INDEX.md) for the complete registry.

### The Standard Lifecycle

```
DRAFT → ACTIVE → DEPRECATED → SUNSET
```

| Status | Meaning | Enforcement |
|--------|---------|-------------|
| **DRAFT** | Under development | None |
| **ACTIVE** | Enforced | Required |
| **DEPRECATED** | Being phased out | Warning |
| **SUNSET** | Archived | None |

See [STANDARD_LIFECYCLE](standards/STANDARD_LIFECYCLE.md) for full policy.

### The Three Layers of Truth

Every standard operates at three layers:

| Layer | Question | Expression |
|-------|----------|------------|
| **Theory** | WHY does this standard exist? | The principle it protects |
| **Specification** | WHAT are the rules? | The constraints (MUST/MUST NOT) |
| **Reference** | HOW do we implement? | The patterns and tooling |

A standard missing any layer is incomplete.

---

## HOW (Reference)

### Creating a New Standard

1. **Identify the pattern** — What decision keeps recurring?
2. **Map to 06_LAW** — Which pillar does this protect?
3. **Follow STANDARD_CREATION** — Use the template
4. **Create folder** — `standards/{name}/` with INDEX.md
5. **Add primitives** — One per topic (respecting STANDARD_LIMIT)
6. **Update INDEX** — Add to `standards/INDEX.md`

### The Escape Hatch

Every standard must have an escape hatch. Standards are guardrails, not prison walls.

```python
# standard:disable [standard-name] - [justification]
# standard:override [rule] - [reason]
```

Escape hatches must be:
- **Explicit** — In code, not just discussed
- **Justified** — Reason documented
- **Reviewable** — Visible in PR

See [STANDARD_EXCEPTIONS](standards/STANDARD_EXCEPTIONS.md) for escape hatch protocol.

### Gene Mutation (Deprecation)

Standards evolve through deprecation—never deletion. The archive preserves the organism's **genetic fossil record**.

```
Active Standard → Deprecated Standard → Archived Standard
    (expressing)       (warning)           (historical)
```

See [deprecation/](standards/deprecation/) for the mutation protocol.

---

## The Principle

> **Standards are crystallized decisions. Make the decision once, apply it forever.**

Standards are the DNA of the organism. They protect cognitive capacity by eliminating repeated decisions. They protect the codebase by ensuring consistency. They protect the future by making patterns explicit and evolvable.

A good standard is invisible when followed and loud when violated.

---

## The Loop

### Navigation

| Position | Document |
|----------|----------|
| **ALPHA** | [00_GENESIS](00_GENESIS.md) |
| **PREVIOUS** | [06_LAW](06_LAW.md) |
| **NEXT** | [08_MEMORY](08_MEMORY.md) |
| **UP** | [INDEX.md](INDEX.md) |

---

## Convergence

### Bottom-Up Validation

This document requires:
- [standards/INDEX.md](standards/INDEX.md) - Registry of all standards
- [STANDARD_LIFECYCLE](standards/STANDARD_LIFECYCLE.md) - How standards evolve

### Top-Down Validation

This document is shaped by:
- [06_LAW](06_LAW.md) - What must be protected
- [00_GENESIS](00_GENESIS.md) - THE GRAMMAR, THE PATTERN

---

*Standards are crystallized decisions. The genetic code. Complete.*
