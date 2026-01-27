# Standard Propagation

**How changes flow through layers. No layer constrains another.**

**Status**: ACTIVE
**Owner**: Framework
**Theory**: [04_ARCHITECTURE](../04_ARCHITECTURE.md) - Holographic Completeness

---

## WHY (Theory)

From 04_ARCHITECTURE:

> Layers are not ceilings or floors. They are **translation surfaces**.
> When ANY layer changes, all layers may change.

The framework is holographic. Each part contains the whole. Changes at any level propagate to all levels.

---

## WHAT (Standard)

### The Propagation Principle

When a change occurs at ANY layer, evaluate propagation to ALL layers:

| If Change At | Ask About Theory | Ask About Meta | Ask About Specifics |
|--------------|------------------|----------------|---------------------|
| **Theory** | Is principle clear? | Do meta-standards reflect it? | Do specifics implement it? |
| **Meta** | Is there underlying principle? | Is rule well-formed? | Do specifics follow it? |
| **Specifics** | Is there missing principle? | Is there missing meta-rule? | Is implementation correct? |

### Compression Rules

**Invoking a higher layer includes all lower layers:**

| Invocation | Compression Level | Includes |
|------------|-------------------|----------|
| "Align to the framework" | Maximum | All theory + meta + specifics |
| "Follow the standards" | High | All meta + specifics |
| "Implement code_quality" | Medium | Specific standard + implied meta |
| "Fix this line" | Low | Specific code + all implied context |

### Expansion Rules

**Invoking a lower layer may expand upper layers:**

| Situation | Expansion Required |
|-----------|-------------------|
| New pattern emerges in specifics | Meta-standard may need creation |
| Meta-standard lacks principle | Theory may need new section |
| Edge case not covered | All layers may need growth |
| Industry standard adopted | Theory, meta, specifics all update |

### The Accommodation Test

Before marking any change "done," verify:

```
ACCOMMODATION CHECKLIST:
[ ] Theory accommodates this change (or grows to)
[ ] Meta-standards accommodate this change (or grow to)
[ ] Specific standards accommodate this change (or grow to)
[ ] No layer is blocked by another layer
[ ] Change is visible from any position (holographic)
```

---

## HOW (Implementation)

### When Making Changes

1. **Identify the layer** of the change (theory, meta, specific)
2. **Check propagation upward** - does any higher layer need to grow?
3. **Check propagation downward** - do any lower layers need to implement?
4. **Update all affected layers** in the same iteration
5. **Verify holographic visibility** - is the change visible from any position?

### When Reviewing Changes

Ask at each layer:

| Layer | Question |
|-------|----------|
| **Theory** | Does this change have a principle? Is it stated? |
| **Meta** | Does this change have a rule? Is it documented? |
| **Specifics** | Does this change have implementation guidance? |

### Trigger Phrase Handling

Trigger phrases are compression interfaces. When handling them:

1. **Recognize the compression level** (see Compression Rules)
2. **Expand to all included layers**
3. **Execute at each layer**
4. **Report at the compression level** (don't overwhelm with details)

**Example**: "Is it aligned to the framework?"
- Expands to: all theory checks + all meta checks + all specific checks
- Execute: verify each applicable item
- Report: "Yes, aligned" or "No, [specific violations]"

---

## ANTI-PATTERNS

### Layer Blocking

```
WRONG: "We can't add this because theory doesn't cover it"
RIGHT: "Theory needs to grow to accommodate this"

WRONG: "This violates the meta-standard"
RIGHT: "Either the change or the meta-standard needs adjustment"

WRONG: "The specific standard is the ceiling"
RIGHT: "Specifics inform meta and theory growth"
```

### Partial Propagation

```
WRONG: Change theory, ignore meta and specifics
WRONG: Add specific standard, ignore missing meta-rule
WRONG: Create meta-standard without theory principle

RIGHT: Every change considers all layers
RIGHT: Layers grow together or flag incompleteness
```

### Over-Expansion

```
WRONG: "Fix this typo" expands to full framework review
RIGHT: "Fix this typo" includes only relevant implied context

The expansion is real but proportional.
```

---

## Convergence

### Bottom-Up Validation

This standard requires:
- [STANDARD_RECURSION](STANDARD_RECURSION.md) - Bidirectional validation
- [STANDARD_COMPLETION](STANDARD_COMPLETION.md) - Definition of done at each layer

### Top-Down Validation

This standard is shaped by:
- [04_ARCHITECTURE](../04_ARCHITECTURE.md) - Holographic Completeness, Non-Constraining Hierarchy
- [01_IDENTITY](../01_IDENTITY.md) - Positional Completeness

---

*Compression includes expansion. Expansion includes compression. All layers grow together.*
