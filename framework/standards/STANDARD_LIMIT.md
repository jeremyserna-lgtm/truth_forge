# Standard Limit

**One Decider. Explicit limits. No sprawl.**

**Status**: ACTIVE
**Owner**: Framework
**Theory**: [06_LAW](../06_LAW.md) - THE LIMIT

---

## WHY (Theory)

From 06_LAW:

> A limit is an explicit boundary that cannot be exceeded. The limit is not arbitrary—it is declared by the Decider in the ME position.

Without limits:
- Documents sprawl indefinitely
- Scope creeps without boundary
- Layers bleed into each other
- Meaning dilutes in noise
- Finding anything becomes impossible

With limits:
- Documents are focused and readable
- Scope is explicit and enforced
- Layers contain what they should
- Meaning is concentrated
- Navigation is precise

### Reality Validation (AI Context Windows)

The 300-line limit is not arbitrary—it is reality-aligned:

| AI Model | Context Window | Sweet Spot | 300 Lines |
|----------|---------------|------------|-----------|
| Claude 4 | 200K tokens | 50-100K | ~5K tokens (2.5%) |
| GPT-5 | 400K tokens | 100-200K | ~5K tokens (1.25%) |
| Llama 4 | 10M tokens | 128-256K | ~5K tokens (0.05%) |

**Key Research Findings:**

1. **"Lost in the Middle"** - Attention degrades in the middle of long contexts
2. **Quality over quantity** - "Just enough relevant context" outperforms "maximum context"
3. **Composability** - Multiple focused documents can be combined when needed

**Token Estimation:** 300 lines ≈ 4,500-6,000 tokens ≈ 3,750-4,500 words

The 300-line limit ensures:
- **Full AI comprehension** (no "lost middle")
- **Human readability** (10-15 minute read)
- **Proper anchoring** (forces topic focus)
- **Future-proofing** (works with any model)

---

## WHAT (Standard)

### The Limit Principle

Every primitive has explicit limits imposed by the Decider:

| Principle | Description |
|-----------|-------------|
| **One Decider** | There is ONE authority that sets the limit |
| **Positional** | The Decider is whoever holds ME position at that scale |
| **Explicit** | Limits must be stated, not implied |
| **Enforced** | Exceeding a limit requires action (split, move, clarify) |

### Document Limits

| Dimension | Limit | Enforcement |
|-----------|-------|-------------|
| **Length** | 300 lines maximum | Split if exceeded |
| **Focus** | ONE anchor, ONE topic | Separate documents for separate topics |
| **Sections** | 7±2 major sections | Reorganize if exceeded |
| **Heading Depth** | 3 levels (##, ###, ####) | Flatten or split if deeper |
| **Line Length** | 100 characters | Wrap or reformat |

### Layer Limits

| Layer | Must Contain | Must NOT Contain |
|-------|--------------|------------------|
| **Theory (00-06)** | Principles, philosophy, patterns | Code, implementation, specific rules |
| **Meta (STANDARD_*)** | Rules about standards, governance | Specific implementations, examples |
| **Specifics ({folder}/)** | Technical requirements, specs | Abstract philosophy, examples |
| **Examples (examples/)** | Concrete implementations | Abstract principles |

### Folder Limits

| Dimension | Limit | Enforcement |
|-----------|-------|-------------|
| **Files per folder** | 15 maximum | Create subfolders if exceeded |
| **Depth** | 4 levels maximum | Flatten structure if deeper |
| **Purpose** | ONE purpose per folder | Separate purposes into separate folders |

### Layer Governance Through Document Limits

**INDEX and README limits create natural layer ceilings.**

| Document | Limit | Consequence |
|----------|-------|-------------|
| **INDEX** | 300 lines | Layer can have ~20-30 primitives max |
| **README** | 300 lines | Layer scope must fit in one definition |

Growth is **outward** (more documents) not **sprawl** (bigger documents). Compression is **inward** (tighter content). When INDEX hits limit → layer is FULL → split into sub-layers.

See [STANDARD_TRIAD](STANDARD_TRIAD.md) for full triad governance.

### Time Limits

| Scope | Limit Type | Declaration Format |
|-------|------------|-------------------|
| **Project** | ONE Year, ONE Quarter | "Revenue by 2027" |
| **Phase** | ONE Month, ONE Sprint | "Complete by end of sprint" |
| **Task** | ONE Day, ONE Hour | "Finish today" |

---

## HOW (Implementation)

### Checking Document Limits

Before marking a document done:

```bash
# Check line count
wc -l document.md
# Must be ≤ 300

# Check section count
grep -c "^## " document.md
# Must be ≤ 9 (7±2)

# Check heading depth
grep -c "^##### " document.md
# Must be 0 (max 4 levels: #, ##, ###, ####)
```

### Splitting Documents

When a document exceeds limits:

```
BEFORE (400 lines, 2 topics):
┌─────────────────────────┐
│ Document: X and Y       │
│ 400 lines               │
│ Topic X (200 lines)     │
│ Topic Y (200 lines)     │
└─────────────────────────┘

AFTER (2 documents, each focused):
┌─────────────────────────┐    ┌─────────────────────────┐
│ Document: X             │    │ Document: Y             │
│ 200 lines               │    │ 200 lines               │
│ Only topic X            │    │ Only topic Y            │
└─────────────────────────┘    └─────────────────────────┘
```

### Layer Enforcement

When content is in wrong layer:

```
WRONG:
theory/04_ARCHITECTURE.md contains Python code examples

RIGHT:
theory/04_ARCHITECTURE.md references patterns
specifics/pipeline/examples/pattern_example.py contains code
```

### Declaring Limits

Limits are declared explicitly:

```markdown
## Limits

| Dimension | Limit |
|-----------|-------|
| Length | 300 lines |
| Focus | ONE topic: X |
| Timeline | Complete by Q2 2026 |
```

---

## ANTI-PATTERNS

| Anti-Pattern | Wrong | Right |
|--------------|-------|-------|
| **Sprawl** | Document grows to 500 lines, no one enforces | 300 lines triggers split |
| **Implicit Limits** | "Keep it short" (how short?) | "300 lines maximum" |
| **No Decider** | "Someone should set a limit" | "I (ME) declare: 300 lines" |
| **Exceptions** | "This document is special" | Split; limit adapts structure |

---

## Verification Checklist

### Document Verification

- [ ] Line count ≤ 300
- [ ] ONE anchor (clear purpose statement)
- [ ] ONE topic (no scope creep)
- [ ] Major sections ≤ 9
- [ ] Heading depth ≤ 4 levels

### Layer Verification

- [ ] Theory contains only principles
- [ ] Meta contains only governance
- [ ] Specifics contain only requirements
- [ ] Examples contain only implementations

### Folder Verification

- [ ] Files per folder ≤ 15
- [ ] Depth ≤ 4 levels
- [ ] ONE purpose per folder
- [ ] INDEX.md exists

---

## Limit Declarations

### Framework Limits (Canonical)

| Scope | Limit | Declared By |
|-------|-------|-------------|
| **Document length** | 300 lines | STANDARD_LIMIT |
| **Document focus** | ONE anchor | STANDARD_ANCHOR |
| **Layer content** | Type-specific | STANDARD_STRUCTURE |
| **Folder files** | 15 maximum | STANDARD_LIMIT |
| **Folder depth** | 4 levels | STANDARD_LIMIT |
| **Heading depth** | 4 levels | STANDARD_LIMIT |
| **Section count** | 7±2 | STANDARD_LIMIT |

### Project Limits (Declared by ME)

| Scope | Limit | Declaration |
|-------|-------|-------------|
| **Revenue timeline** | ONE Year | "Revenue by 2027" |
| **Team size** | ONE Person + ONE Not-Me | ME:NOT-ME |
| **Focus** | ONE Product (Primitive) | Current priority |

---

## Integration with Other Standards

| Standard | Limit Relationship |
|----------|-------------------|
| **STANDARD_ANCHOR** | Anchor defines the ONE topic (limit of focus) |
| **STANDARD_ONE** | ONE thing at a time (limit of attention) |
| **STANDARD_COMPLETION** | DONE requires limits verified |
| **STANDARD_STRUCTURE** | Structure enforces layer limits |
| **STANDARD_OPTIMIZATION** | Optimization respects limits |

---

## The Loop

### Navigation

| Position | Document |
|----------|----------|
| **ALPHA** | [00_GENESIS](../00_GENESIS.md) |
| **UP** | [standards/INDEX.md](INDEX.md) |

---

## Convergence

### Bottom-Up Validation

This standard requires:
- [STANDARD_ANCHOR](STANDARD_ANCHOR.md) - ONE topic per document
- [STANDARD_STRUCTURE](STANDARD_STRUCTURE.md) - Layer definitions
- [STANDARD_ONE](STANDARD_ONE.md) - ONE thing principle

### Top-Down Validation

This standard is shaped by:
- [06_LAW](../06_LAW.md) - THE LIMIT, THE BOUNDARIES
- [00_GENESIS](../00_GENESIS.md) - THE ONE

---

*One Decider. Explicit limits. Enforced always. No sprawl.*
