# Standard Triad

**INDEX + README + Primitives. The three-component structure at every layer.**

**Status**: ACTIVE
**Owner**: Framework
**Theory**: [04_ARCHITECTURE](../04_ARCHITECTURE.md) - HOLD:AGENT:HOLD

---

## WHY (Theory)

Every layer needs three components to serve both ME and NOT-ME:
- **INDEX**: Navigation (WHERE) - NOT-ME can parse efficiently
- **README**: Definition (WHAT) - ME's ideas captured completely
- **Primitives**: Standards (HOW) - The actual rules

Without the triad:
- Navigation exists without definition
- Definition exists without navigation
- Content has no context

---

## The Structure

```
layer/
├── INDEX.md      # HOLD₁ - Navigation (WHERE)
├── README.md     # AGENT - Definition (WHAT)
└── *.md          # HOLD₂ - Standards (HOW)
```

Maps to HOLD:AGENT:HOLD.

---

## The Roles

| Component | Purpose | Contains |
|-----------|---------|----------|
| **INDEX** | Navigation | Lists primitives, assessment criteria, directions |
| **README** | Definition | What primitives on this layer conceptually ARE |
| **Primitives** | Standards | The actual rules (MUST/MUST NOT) |

---

## The Distinction

```
INDEX tells you: "LENGTH.md exists here"
README tells you: "A document primitive defines ONE aspect of document craft"
LENGTH.md tells you: "MUST stay under 300 lines"
```

---

## Layer-Specific Requirements

### Theory Layer (framework/)

**INDEX.md:** List theory docs with questions and anchors, show ALPHA:OMEGA loop.

**README.md:** What theory documents ARE (cognitive principles), why ME articulates before implementation.

**Primitives:** 00_GENESIS.md through 06_LAW.md.

### Meta Layer (framework/standards/)

**INDEX.md:** List STANDARD_*.md with purpose, show structure, point to specifics.

**README.md:** What meta-standards ARE (joining layer), how meta joins ME to NOT-ME to OTHER.

**Primitives:** STANDARD_CREATION.md, STANDARD_LIFECYCLE.md, etc.

### Specifics Layer (framework/standards/{folder}/)

**INDEX.md:** Hub diagram, direction table, quick reference with "Should Cover" criteria.

**README.md:** What primitives on this layer ARE, why this standard exists, how primitives relate.

**Primitives:** TYPE_HINTS.md, DLQ.md, etc.

---

## README Content by Layer

| Layer | Identity | README Explains |
|-------|----------|-----------------|
| **Theory** | ME | Cognitive principles, what ME sees |
| **Meta** | ME:NOT-ME:OTHER | Joining function, grounding |
| **Specifics** | NOT-ME | Technical domain, implementation |

---

## The Dual-Reader Requirement

Every INDEX and README must serve BOTH:

| Reader | Requirement |
|--------|-------------|
| **ME** | Complete coverage of ideas, requirements, wants |
| **NOT-ME** | Concise, parseable structure it can bear the weight of |

ME's completeness expressed in NOT-ME's form.

---

## Layer Governance Through Limits

Document limits create natural layer ceilings. See [STANDARD_LIMIT](STANDARD_LIMIT.md).

INDEX and README constrained to 300 lines:
- INDEX must list all primitives AND stay under limit
- README must define layer concept AND stay under limit

**When INDEX approaches 300 lines → layer is approaching capacity.**

Growth directions:

| Direction | Meaning | Allowed? |
|-----------|---------|----------|
| **Outward** | More primitives | Yes, until INDEX limit |
| **Inward** | Compression | Yes, always |
| **Sprawl** | Past 300 lines | No, split |
| **Redundancy** | Duplicate content | No, canonical |

---

## When README Is Optional

| Situation | Required? |
|-----------|-----------|
| 3+ primitives | Yes |
| 1-2 primitives | Optional |
| Single file | No |

---

## Verification

- [ ] INDEX lists all primitives
- [ ] INDEX has assessment criteria ("Should Cover")
- [ ] README defines what primitives ARE
- [ ] README is layer-appropriate (theory/meta/specifics)
- [ ] Each primitive has UP link to INDEX
- [ ] INDEX under 300 lines
- [ ] README under 300 lines

---

## Integration

| Standard | Relationship |
|----------|--------------|
| [STANDARD_STRUCTURE](STANDARD_STRUCTURE.md) | Folder structure where triad lives |
| [STANDARD_LIMIT](STANDARD_LIMIT.md) | Document limits that govern triad |
| [STANDARD_ANCHOR](STANDARD_ANCHOR.md) | ONE topic per document |

---

## UP

[INDEX.md](INDEX.md)
