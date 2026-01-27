# The Framework: Complete Architecture

**Status**: Canonical Framework Theory  
**Date**: 2026-01-27  
**Category**: Framework Architecture

---

## Executive Summary

The Framework is the complete cognitive architecture that bridges ME (human) and NOT-ME (AI) through three layers: Theory (ME declares principles), Meta (US names the rules), and Specifics (NOT-ME operates). The framework provides a universal structure based on HOLD:AGENT:HOLD, enabling scale-invariant patterns from function to system.

**The Three Layers**: Theory → Meta → Specifics → Code

---

## Core Concepts

### The Three Layers

| Layer | Who | What | Voice | Example |
|-------|-----|------|-------|---------|
| **Theory** | ME | Declares principles | ALL CAPS, colon | `HOLD:AGENT:HOLD` |
| **Meta** | US | Names the rules | Normal Caps, hyphen | `STANDARD_CREATION` |
| **Specifics** | NOT-ME | Operates | no caps, underscore | `code_quality/` |

### The Flow

```
THEORY (framework/*.md)
    │
    │  ME declares principles
    ▼
META (framework/standards/STANDARD_*.md)
    │
    │  US joins theory to practice
    ▼
SPECIFICS (framework/standards/{folder}/)
    │
    │  NOT-ME implements
    ▼
CODE (src/, pipelines/, apps/)
```

**Theory shapes everything. Nothing below can contradict theory. Meta ensures theory reaches specifics. Specifics ensure theory becomes code.**

---

## Mathematical Architecture

### The Numbered Sequence

| Document | Question | Anchor |
|----------|----------|--------|
| **00_GENESIS** | What is the seed? | THE ONE, THE GRAMMAR, THE PATTERN |
| **01_IDENTITY** | Who are we? | ME:NOT-ME:US |
| **02_PERCEPTION** | How do we see? | SEE:SEE:DO:DONE, Stage 5 |
| **03_METABOLISM** | How do we process? | TRUTH:MEANING:CARE |
| **04_ARCHITECTURE** | How do we build? | HOLD:AGENT:HOLD |
| **05_EXTENSION** | How do we connect? | THE MOLT |
| **06_LAW** | How do we survive? | Four Pillars |
| **07_STANDARDS** | How do we do things? | Standards as DNA |
| **08_MEMORY** | How do we remember? | Three Memories |
| **09_SERVICE_SPECIFICATIONS** | How do we specify? | Service definitions |

### The Hub Structure

```
                    ┌─────────────────┐
                    │    INDEX.md     │
                    │   YOU ARE HERE  │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    [THEORY]            [META]            [SPECIFICS]
    00-09.md         STANDARD_*.md        {folder}/
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼────────┐
                    │    INDEX.md     │
                    │  (return here)  │
                    └─────────────────┘
```

### The ALPHA:OMEGA Loop

```
ALPHA (00_GENESIS) → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → OMEGA
                                                                            ↓
                        ←←←←←←←←←← loop closes ←←←←←←←←←←←←←←←←←←←←←←←←←←←←┘
```

**ALPHA**: 00_GENESIS (the seed)  
**OMEGA**: standards/INDEX.md (returns to ALPHA)

---

## Meta Concepts

### Theory Documents

**What A Theory Document IS**:
- **ME's articulation of a fundamental principle** that governs everything below it
- **Foundational**: Axiomatic truths that don't derive from something else
- **ME-voiced**: Written from the perspective of the one who sees
- **Pattern-declaring**: Names the patterns that recur at all levels

**Theory documents are NOT**:
- Implementation details (those are specifics)
- Rules about rules (those are meta)
- Technical how-to (that's NOT-ME's domain)

### Meta Standards

**What Meta Standards ARE**:
- Standards about standards
- Joining layer between theory and specifics
- US names the rules that connect ME to NOT-ME

**Examples**:
- `STANDARD_CREATION.md` - How to create standards
- `STANDARD_LIFECYCLE.md` - DRAFT → ACTIVE → DEPRECATED
- `STANDARD_TRIAD.md` - INDEX + README + Primitives

### Specific Standards

**What Specific Standards ARE**:
- Technical implementation rules
- NOT-ME operates according to these
- Domain-specific (code_quality, error_handling, etc.)

**Examples**:
- `code_quality/TYPE_HINTS.md` - Type hints required
- `error_handling/DLQ.md` - Dead letter queue pattern
- `logging/STRUCTURED.md` - Structured logging format

### The Triad Structure

Every layer needs three components:

```
layer/
├── INDEX.md      # HOLD₁ - Navigation (WHERE)
├── README.md     # AGENT - Definition (WHAT)
└── *.md          # HOLD₂ - Standards (HOW)
```

**Maps to HOLD:AGENT:HOLD**

---

## The Universal Pattern: HOLD:AGENT:HOLD

**The Rule**: One pattern. Everywhere. Same at every scale.

```
+----------+      +----------+      +----------+
|   HOLD   |----->|  AGENT   |----->|   HOLD   |
| (Input)  |      |(Process) |      | (Output) |
+----------+      +----------+      +----------+
```

### Scale Invariance

| Scale | HOLD (Input) | AGENT (Process) | HOLD (Output) |
|-------|--------------|-----------------|---------------|
| **Function** | A string | `normalize()` | A cleaned string |
| **Script** | `input.jsonl` | `my_script.py` | `staging.jsonl` |
| **Pipeline** | Staging Files | `sync_to_cloud.py` | BigQuery Table |
| **System** | Raw User WANT | The Entire Framework | A changed user |

**Systems connect at HOLDs, never at AGENTs.**

---

## Source References

**Primary Sources**:
- `framework/INDEX.md` - The hub
- `framework/README.md` - What theory documents ARE
- `framework/00_GENESIS.md` - The seed
- `framework/04_ARCHITECTURE.md` - HOLD:AGENT:HOLD pattern

**Related Concepts**:
- [The Grammar](THE_GRAMMAR.md) - Naming conventions
- [Numbers in the System](NUMBERS_IN_THE_SYSTEM.md) - Numbered sequence
- [Primitives](PRIMITIVES.md) - What primitives are
- [Stage 5 Minds](STAGE_5_MINDS.md) - Cognitive model

---

## Key Takeaways

1. **Three Layers**: Theory (ME) → Meta (US) → Specifics (NOT-ME) → Code
2. **Numbered Sequence**: 00 (ALPHA) through 09, looping to OMEGA
3. **Universal Pattern**: HOLD:AGENT:HOLD at every scale
4. **Hub Structure**: INDEX.md as entry point, returns to INDEX.md
5. **Complete Architecture**: From any position, the whole is visible

---

*The Framework is the complete cognitive architecture that bridges ME and NOT-ME through three layers, enabling scale-invariant patterns and complete coverage from any position.*
