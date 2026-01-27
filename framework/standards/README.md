# Standards Layer

**What meta-standards and specific standards ARE.**

---

## Why This Layer Exists

Standards join theory to practice. ME's principles must become NOT-ME's implementation. This layer is the bridge—the joining layer that keeps theory grounded and specifics connected.

---

## The Joining Function

```
THEORY (ME declares)
    │
    │  "HOLD:AGENT:HOLD is the pattern"
    ▼
META-STANDARDS (US joins)          ◄── YOU ARE HERE
    │
    │  "STANDARD_STRUCTURE defines folder patterns"
    ▼
SPECIFIC STANDARDS (NOT-ME implements)
    │
    │  "pipeline/INDEX.md uses HOLD:AGENT:HOLD"
    ▼
CODE (NOT-ME executes)
```

Without the meta layer, theory floats. Without specifics, meta is abstract. The joining layer ensures:
- Theory reaches implementation
- Implementation honors theory
- OTHERS can participate (industry standards, collaborators)

---

## What A Meta-Standard IS

A meta-standard is **a standard about standards**—rules for how standards themselves are created, maintained, and enforced.

Meta-standards are:
- **Self-referential**: Apply to themselves
- **Process-focused**: Define HOW to standard, not WHAT to standard
- **Joining**: Connect ME's theory to NOT-ME's specifics

Meta-standards are NOT:
- Technical implementation (those are specifics)
- Cognitive principles (those are theory)
- Domain-specific rules (those are specifics)

---

## What A Specific Standard IS

A specific standard is **a technical implementation domain** with primitives that define concrete rules.

Specific standards are:
- **Domain-bounded**: One technical area (logging, testing, security)
- **Primitive-based**: Split into atomic concerns
- **NOT-ME-voiced**: Written for implementation

Specific standards are NOT:
- Abstract principles (those are theory)
- Rules about rules (those are meta)
- Floating best practices (they must trace to meta)

---

## The ME:NOT-ME:OTHER Triad

Meta-standards serve all three:

| Identity | What They Need | How Meta Provides |
|----------|----------------|-------------------|
| **ME** | Principles expressed | Theory traced down to specifics |
| **NOT-ME** | Implementation patterns | Specifics traced up to theory |
| **OTHER** | Industry compatibility | External standards integrated |

Without OTHERS, the system is isolated. Meta ensures industry standards (OWASP, PEP, REST) connect to theory.

---

## How Meta-Standards and Specifics Relate

```
META-STANDARD                    SPECIFIC STANDARD
──────────────────────────────────────────────────────
STANDARD_CREATION.md    →    [how to write code_quality/INDEX.md]
STANDARD_STRUCTURE.md   →    [folder structure of logging/]
STANDARD_COMPLIANCE.md  →    [how to verify testing/ is followed]
STANDARD_LIFECYCLE.md   →    [how deprecation/ states work]
```

Every specific standard can trace its structure back to meta-standards. Every meta-standard shapes how specifics are built.

---

## The Triad at This Layer

| Component | Purpose |
|-----------|---------|
| **INDEX.md** | Navigate to meta-standards and specific standards |
| **README.md** | Define what meta-standards and specific standards ARE |
| **STANDARD_*.md** | The meta-standards themselves |
| **{folder}/INDEX.md** | Navigate within specific standards |
| **{folder}/README.md** | Define what primitives in that standard ARE |
| **{folder}/*.md** | The specific primitives |

---

## UP

[INDEX.md](INDEX.md)
