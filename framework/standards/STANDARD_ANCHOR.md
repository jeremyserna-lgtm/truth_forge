# Standard Anchor

**Every primitive has an anchor. The anchor LIMITS and ENVELOPES completely.**

**Status**: ACTIVE
**Owner**: Framework
**Theory**: [04_ARCHITECTURE](../04_ARCHITECTURE.md) - THE ANCHOR

---

## WHY (Theory)

From 04_ARCHITECTURE:

> An anchor is the grounding point that defines what belongs and what does not belong.

Without anchors:
- Documents sprawl with unrelated content
- Scope creeps without boundary
- Completeness cannot be verified
- Finding information becomes impossible

With anchors:
- Every primitive knows its boundary
- Content either belongs or doesn't
- Completeness is verifiable
- Navigation is precise

---

## WHAT (Standard)

### The Anchor Principle

Every primitive has an anchor that performs two functions:

| Function | Description | Test |
|----------|-------------|------|
| **LIMITS** | Excludes what doesn't belong | "Is this within anchor?" |
| **ENVELOPES** | Includes everything that does | "Is anchor complete?" |

### Necessary Anchors

These anchors MUST exist:

| Primitive | Necessary Anchor | Purpose |
|-----------|------------------|---------|
| **Layer** | INDEX.md | Entry point, contains layer |
| **Folder** | INDEX.md | Entry point, contains folder |
| **Document** | Title + Purpose statement | Declares scope |
| **Standard** | INDEX.md | Entry point for standard |

### Positional Anchors

Any primitive can serve as anchor when addressed:

```
"What is the anchor of this section?"
    → The section heading

"What is the anchor of this paragraph?"
    → The first sentence (topic sentence)

"What is the anchor of this code block?"
    → The function signature or comment
```

### The Anchor Test

Before marking any primitive complete:

| Question | Pass | Fail |
|----------|------|------|
| Is the anchor clear? | ONE thing stated | Multiple or unclear |
| Is content within scope? | All content relates | Some content unrelated |
| Is scope complete? | Nothing missing | Gaps exist |

---

## HOW (Implementation)

### Document Anchoring

Every document begins with its anchor:

```markdown
# Document Title

**[Purpose statement that anchors this document.]**

*[Optional tagline or emphasis]*

---
```

The title + purpose IS the anchor. Everything below must:
- Relate to that anchor (LIMITS)
- Completely cover that anchor (ENVELOPES)

### Folder Anchoring

Every folder contains INDEX.md:

```
folder/
├── INDEX.md          ← ANCHOR (necessary)
├── file_1.md         ← anchored to folder
├── file_2.md         ← anchored to folder
└── subfolder/
    └── INDEX.md      ← ANCHOR of subfolder
```

### Section Anchoring

Every section begins with its anchor:

```markdown
## Section Heading ← ANCHOR

[First paragraph explains what this section covers]

[All subsequent content relates to heading]
```

### Moving Content to Proper Anchor

When content doesn't belong:

```
BEFORE:                          AFTER:
┌─────────────────┐              ┌─────────────────┐
│ Anchor: X       │              │ Anchor: X       │
├─────────────────┤              ├─────────────────┤
│ About X         │              │ About X         │
│ About Y ←wrong  │              │ (complete)      │
└─────────────────┘              └─────────────────┘

                                 ┌─────────────────┐
                                 │ Anchor: Y       │ ← new document
                                 ├─────────────────┤
                                 │ About Y         │
                                 └─────────────────┘
```

### Expanding Anchors

When content belongs but anchor is too narrow:

```
BEFORE:                          AFTER:
┌─────────────────┐              ┌─────────────────┐
│ Anchor: X       │              │ Anchor: X and Y │ ← expanded
├─────────────────┤              ├─────────────────┤
│ About X         │              │ About X         │
│ About Y ←wrong? │              │ About Y         │ ← now belongs
└─────────────────┘              └─────────────────┘
```

---

## ANTI-PATTERNS

### Scope Sprawl

```
WRONG: Document about "Architecture" that also covers testing, deployment, and user guides

RIGHT: Document about "Architecture" that covers only architecture; testing in testing/, deployment in deployment/
```

### Incomplete Coverage

```
WRONG: Document anchored to "Error Handling" that only covers exceptions (missing DLQ, retry, logging)

RIGHT: Document anchored to "Error Handling" that covers ALL error handling patterns
```

### Missing Necessary Anchor

```
WRONG: Folder without INDEX.md
       Users must guess what folder contains

RIGHT: Folder with INDEX.md
       INDEX declares what folder contains and links to contents
```

### Unclear Anchor

```
WRONG: Document with title but no purpose statement
       "Architecture" - what aspect? what scope?

RIGHT: Document with clear anchor
       "Architecture: How We Build. The HOLD:AGENT:HOLD pattern."
```

---

## Verification Checklist

### Layer Verification

- [ ] Layer has INDEX.md (necessary anchor)
- [ ] INDEX declares layer scope
- [ ] INDEX links to all layer contents
- [ ] All contents relate to layer scope

### Folder Verification

- [ ] Folder has INDEX.md (necessary anchor)
- [ ] INDEX declares folder purpose
- [ ] INDEX links to folder contents
- [ ] Contents relate to folder purpose

### Document Verification

- [ ] Document has clear title
- [ ] Document has purpose statement (first bold line)
- [ ] All sections relate to document anchor
- [ ] Document scope is complete (nothing missing)

### Section Verification

- [ ] Section has clear heading
- [ ] All paragraphs relate to heading
- [ ] Section scope is complete

---

## Integration with Other Standards

| Standard | Anchor Relationship |
|----------|---------------------|
| **STANDARD_ONE** | The anchor IS the ONE thing this primitive grounds |
| **STANDARD_COMPLETION** | DONE requires anchor verification |
| **STANDARD_STRUCTURE** | Structure emerges from anchors |
| **STANDARD_PROPAGATION** | Anchor changes may propagate |

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
- [STANDARD_ONE](STANDARD_ONE.md) - Anchor is ONE thing
- [STANDARD_COMPLETION](STANDARD_COMPLETION.md) - Verification of completeness

### Top-Down Validation

This standard is shaped by:
- [04_ARCHITECTURE](../04_ARCHITECTURE.md) - THE ANCHOR
- [00_GENESIS](../00_GENESIS.md) - THE ONE

---

*Every primitive has an anchor. The anchor limits. The anchor envelopes. Both completely.*
