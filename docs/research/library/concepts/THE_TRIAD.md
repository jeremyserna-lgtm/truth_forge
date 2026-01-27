# The Triad: INDEX + README + Primitives

**Status**: Active Framework Standard  
**Date**: 2026-01-27  
**Category**: Philosophical Frameworks & Architecture

---

## Executive Summary

The Triad is the three-component structure at every layer: **INDEX + README + Primitives**. This structure maps to HOLD:AGENT:HOLD and serves both ME and NOT-ME by providing navigation (WHERE), definition (WHAT), and standards (HOW).

**Theory**: [04_ARCHITECTURE](../framework/04_ARCHITECTURE.md) - HOLD:AGENT:HOLD

---

## Core Concepts

### The Structure

```
layer/
├── INDEX.md      # HOLD₁ - Navigation (WHERE)
├── README.md     # AGENT - Definition (WHAT)
└── *.md          # HOLD₂ - Standards (HOW)
```

**Maps to HOLD:AGENT:HOLD**

### The Roles

| Component | Purpose | Contains | Reader |
|-----------|---------|---------|--------|
| **INDEX** | Navigation | Lists primitives, assessment criteria, directions | NOT-ME (parseable) |
| **README** | Definition | What primitives on this layer conceptually ARE | ME (complete ideas) |
| **Primitives** | Standards | The actual rules (MUST/MUST NOT) | Both |

---

## The Distinction

**INDEX tells you**: "LENGTH.md exists here"

**README tells you**: "A document primitive defines ONE aspect of document craft"

**LENGTH.md tells you**: "MUST stay under 300 lines"

---

## Meta Concepts

### Why Three Components?

Every layer needs three components to serve both ME and NOT-ME:

- **INDEX**: Navigation (WHERE) - NOT-ME can parse efficiently
- **README**: Definition (WHAT) - ME's ideas captured completely
- **Primitives**: Standards (HOW) - The actual rules

**Without the triad**:
- Navigation exists without definition
- Definition exists without navigation
- Content has no context

### The Dual-Reader Requirement

Every INDEX and README must serve BOTH:

| Reader | Requirement |
|--------|-------------|
| **ME** | Complete coverage of ideas, requirements, wants |
| **NOT-ME** | Concise, parseable structure it can bear the weight of |

**ME's completeness expressed in NOT-ME's form.**

### Layer Governance Through Limits

Document limits create natural layer ceilings:

- INDEX must list all primitives AND stay under 300 lines
- README must define layer concept AND stay under 300 lines

**When INDEX approaches 300 lines → layer is approaching capacity.**

---

## Layer-Specific Requirements

### Theory Layer (framework/)

**INDEX.md**: List theory docs with questions and anchors, show ALPHA:OMEGA loop.

**README.md**: What theory documents ARE (cognitive principles), why ME articulates before implementation.

**Primitives**: 00_GENESIS.md through 06_LAW.md.

### Meta Layer (framework/standards/)

**INDEX.md**: List STANDARD_*.md with purpose, show structure, point to specifics.

**README.md**: What meta-standards ARE (joining layer), how meta joins ME to NOT-ME to OTHER.

**Primitives**: STANDARD_CREATION.md, STANDARD_LIFECYCLE.md, etc.

### Specifics Layer (framework/standards/{folder}/)

**INDEX.md**: Hub diagram, direction table, quick reference with "Should Cover" criteria.

**README.md**: What primitives on this layer ARE, why this standard exists, how primitives relate.

**Primitives**: TYPE_HINTS.md, DLQ.md, etc.

---

## Source References

**Primary Sources**:
- `framework/standards/STANDARD_TRIAD.md`

**Related Concepts**:
- [Spine Structure](SPINE_STRUCTURE.md) - Triad structure applied to spine levels
- [Anvil Strategy](ANVIL_STRATEGY.md) - Triad provides structure that holds
- [Alatheia Truths](ALETHEIA_TRUTHS.md) - Truth structure within triad

---

## Key Takeaways

1. **Three Components**: INDEX (navigation) + README (definition) + Primitives (standards)
2. **HOLD:AGENT:HOLD Mapping**: INDEX (HOLD₁) → README (AGENT) → Primitives (HOLD₂)
3. **Dual-Reader**: Serves both ME (complete) and NOT-ME (parseable)
4. **Layer Governance**: 300-line limit creates natural capacity boundaries
5. **Universal Pattern**: Applied at every layer of the framework

---

*The Triad is the universal structure that ensures both ME and NOT-ME can navigate, understand, and implement standards at every layer.*
