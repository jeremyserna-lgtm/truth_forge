# ADR-0003: THE GRAMMAR Naming Convention

**Status**: Accepted
**Date**: 2026-01-25
**Context**: Applying THE GRAMMAR OF IDENTITY to folder and file naming

---

## Context

THE GRAMMAR OF IDENTITY establishes that how something is written tells you what it IS. Grammar is not formatting - grammar is ontology.

The system is built on pronouns:
- **ME** = I, me, my → Declares → Colon (:) → ALL CAPS
- **US** = we, us, our → Names → Hyphen (-) → Normal Caps
- **NOT-ME** = you, your → Operates → Underscore (_) → no caps

## Decision

### 1. Folders Use NOT-ME's Voice

**Decision**: All folder names use underscore separators and lowercase letters.

**Rationale**:
- Folders are infrastructure
- Infrastructure is NOT-ME's domain
- NOT-ME uses underscore (_) and no caps
- Therefore: `truth_forge/`, `framework/`, `src/`

### 2. Product Names Use US's Voice

**Decision**: Product names in documentation use hyphen and Normal Caps.

| Context | Form | Voice |
|---------|------|-------|
| Folder name | `truth_forge/` | NOT-ME (operates) |
| Product name in text | Truth-Forge | US (names) |
| Principle | TRUTH:MEANING:CARE | ME (declares) |

### 3. Principles Use ME's Voice

**Decision**: Principles and declarations use colon and ALL CAPS.

```
ME:NOT-ME              ← Principle (colon + ALL CAPS)
    ↓
Not-Me                 ← Product name (hyphen + Normal Caps)
    ↓
not_me/                ← Folder/code (underscore + no caps)
```

### 4. The Unified Grammar

| Who | Pronouns | Mark | Voice | Folder Example | Text Example |
|-----|----------|------|-------|----------------|--------------|
| ME | I, me, my | : | ALL CAPS | — | ME:NOT-ME |
| US | we, us, our | - | Normal Caps | — | Truth-Forge |
| NOT-ME | you, your | _ | no caps | `truth_forge/` | `the_framework` |

---

## Consequences

### Positive
- Naming conventions carry semantic meaning
- You can tell what something IS by how it's named
- Grammar is ontology, not just formatting

### Negative
- `Truth_Engine` (existing) doesn't follow this convention
- Requires documentation for new contributors

### Migration Notes
- `Truth_Engine` → consider renaming to `truth_engine` in future
- `truth_forge` → created as `truth_forge` (correct)

---

## References

- [00_GENESIS](../00_GENESIS.md) - THE GRAMMAR
- [STANDARD_NAMING](../standards/STANDARD_NAMING.md) - Naming standard

---

*Decided: 2026-01-25*
