# Standard Hierarchy

**When standards conflict, higher-level standards win.**

---

## The Rule

Standards have precedence. Hierarchy determines which standard wins when they conflict.

---

## Hierarchy Levels

| Level | Name | Scope | Examples | Precedence |
|-------|------|-------|----------|------------|
| **L0** | Meta | Standards about standards | STANDARD_CREATION, this doc | Highest |
| **L1** | Core | Universal principles | PLANNING, ERROR_HANDLING | ↑ |
| **L2** | Technical | Technology-specific | CODE_QUALITY, TESTING | ↓ |
| **L3** | Domain | Domain-specific | PIPELINE_STANDARD | ↓ |
| **L4** | Project | Project-specific | Local CLAUDE.md | Lowest |

---

## Conflict Resolution

When standards conflict:

1. **Identify levels** - Which level is each standard?
2. **Higher wins** - Lower level yields to higher
3. **Same level** - More specific wins
4. **Still tied** - Newer standard wins (with documented rationale)

---

## Inheritance

Standards inherit from higher levels:

```
L0: STANDARD_CREATION
    ↓ inherits
L1: ERROR_HANDLING
    ↓ inherits
L2: CODE_QUALITY
    ↓ inherits
L3: PIPELINE_STANDARD
```

Child standards MUST NOT contradict parent standards.

---

## Scope Rules

| Level | Scope Constraint |
|-------|------------------|
| **L0** | All standards |
| **L1** | All code |
| **L2** | Specific technology |
| **L3** | Specific domain |
| **L4** | Specific project |

---

## Example Conflict

```
CODE_QUALITY: "Functions MUST have docstrings"
TESTING: "Test functions SHOULD NOT have docstrings"

Resolution: Both are L2. TESTING is more specific to test context.
Test functions follow TESTING standard.
```

---

## Framework Envelope

This standard is enveloped by:
- [00_GENESIS](../00_GENESIS.md) - THE ONE (hierarchy collapses to one decision)
- [04_ARCHITECTURE](../04_ARCHITECTURE.md) - Scale invariance (hierarchy at every level)

---

## UP

[INDEX.md](INDEX.md)
