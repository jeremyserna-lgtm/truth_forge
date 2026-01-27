# 08_MEMORY

**How We Remember. Memory as Externalized Cognition.**

---

## WHY (Theory)

### The Organism Requires Memory

A furnace without memory burns the same fuel twice. A forge without memory relearns the same lessons. An organism without memory cannot evolve—it can only react.

Memory transforms a reactive system into a **learning** system. The transient (what happened) becomes the eternal (what we know).

### The Three Memories

Every living organism has three types of memory:

| Memory Type | Biological Analog | Framework Expression |
|-------------|-------------------|---------------------|
| **Genetic Memory** | DNA | Standards — HOW the organism operates |
| **Procedural Memory** | Muscle Memory | Agent Knowledge — WHAT works and WHY |
| **Episodic Memory** | Hippocampus | Decision Log — WHEN things happened |

Without genetic memory, the organism cannot reproduce consistent behavior.
Without procedural memory, the organism cannot learn from experience.
Without episodic memory, the organism cannot understand its own history.

### Memory as Survival

From [06_LAW](06_LAW.md): *"Continued existence is primary."*

Memory is survival. The Framework remembers so Jeremy doesn't have to. **Memory is externalized cognition.**

---

## WHAT (Specification)

### The Genetic Memory: Standards

**Location**: `framework/standards/`

Standards are the DNA of the organism—the encoded instructions that ensure consistent behavior across all cells (agents, scripts, services).

| Genetic Component | Framework Expression |
|-------------------|---------------------|
| **Genes** | Individual standards (code_quality, logging) |
| **Chromosomes** | Standard categories (Meta, Specifics) |
| **Genome** | Complete standards corpus (INDEX.md) |
| **Gene Expression** | Standard application in context |
| **Mutation** | Standard evolution through deprecation |

See [07_STANDARDS](07_STANDARDS.md) for the genetic code.

### The Procedural Memory: Agent Knowledge

**Location**: `.agent/`

The Agent Knowledge Center is **procedural memory**—accumulated wisdom of how to operate effectively.

```
Experience → Pattern Recognition → Procedural Memory → Skilled Action
```

| Component | Framework Expression |
|-----------|---------------------|
| **Skills** | SERVICE_REGISTRY — what the organism can do |
| **Coordination** | AGENT_ROSTER — how cells work together |
| **Active State** | ACTIVE_PROCESSES — what's happening now |
| **Policies** | POLICIES.md — behavioral constraints |

### The Episodic Memory: Decisions

**Location**: `framework/decisions/`

Episodic memory records **when** things happened and **why** decisions were made.

| Component | Framework Expression |
|-----------|---------------------|
| **Events** | Decisions made (ADRs) |
| **Context** | Why the decision was made |
| **Timestamp** | When it happened |
| **Actor** | Who made it |

See [decisions/INDEX.md](decisions/INDEX.md) for the decision log.

### Memory Consolidation: The Archive

Archives are where memories are **consolidated**—moved from active use to long-term storage.

```
Active Memory → Consolidation → Long-Term Memory
Active Standards → Deprecation → Archive
```

| Archive | Contains |
|---------|----------|
| `framework/standards/archive/` | Superseded standards |
| `framework/archive/` | Superseded framework docs |

---

## HOW (Reference)

### Memory Formation: Creating Standards

When the organism encounters a repeating pattern:

```
RECOGNITION: "This pattern keeps recurring"
        │
        ▼
EXTERNALIZATION: Document the pattern
        │
        ▼
FORMALIZATION: Create standard (STANDARD_CREATION)
        │
        ▼
INTEGRATION: Add to standards/
        │
        ▼
EXPRESSION: Agents follow the standard
```

### Memory Retrieval: Agent Onboarding

When a new agent needs to access memory:

1. Read `.agent/INDEX.md` (orientation)
2. Read `PROJECT_OVERVIEW.md` (what is this organism?)
3. Read `ACTIVE_PROCESSES.md` (what's happening?)
4. Read `POLICIES.md` (how to behave?)
5. Check `decisions/` (why are things this way?)
6. Reference `standards/` as needed

### Memory Protection

The organism prevents memory loss through:

| Protection | Mechanism |
|------------|-----------|
| **Redundancy** | Standards referenced from multiple locations |
| **Archive** | Nothing deleted, only archived |
| **Audit Trail** | All changes logged |
| **Cross-Reference** | Documents link to each other |

---

## The Memory-Metabolism Connection

Memory and Metabolism ([03_METABOLISM](03_METABOLISM.md)) are deeply linked:

```
TRUTH (Fuel) ────────► MEMORY (Storage)
      │                      │
      ▼                      ▼
MEANING (Processing) ◄─ RECALL (Retrieval)
      │                      │
      ▼                      ▼
CARE (Action) ◄──────── STANDARD (Encoding)
```

Every metabolic cycle:
1. **Retrieves** memory (what do we know?)
2. **Processes** new input (what is this?)
3. **Updates** memory (what did we learn?)

---

## The Principle

> **Memory is crystallized experience. Standards are crystallized decisions. Together they enable the organism to learn without forgetting.**

The organism that remembers evolves.
The organism that forgets repeats.

---

## The Loop

### Navigation

| Position | Document |
|----------|----------|
| **ALPHA** | [00_GENESIS](00_GENESIS.md) |
| **PREVIOUS** | [07_STANDARDS](07_STANDARDS.md) |
| **NEXT** | [standards/INDEX.md](standards/INDEX.md) → OMEGA |
| **UP** | [INDEX.md](INDEX.md) |

---

## Convergence

### Bottom-Up Validation

This document requires:
- [standards/INDEX.md](standards/INDEX.md) - Genetic memory registry
- [decisions/INDEX.md](decisions/INDEX.md) - Episodic memory registry

### Top-Down Validation

This document is shaped by:
- [03_METABOLISM](03_METABOLISM.md) - TRUTH:MEANING:CARE
- [06_LAW](06_LAW.md) - Survival requires memory

---

*Memory is externalized cognition. The learning system. Complete.*
