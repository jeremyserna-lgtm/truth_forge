# Standard Structure

**A folder IS the thing. It contains what it needs.**

---

## The Rule

Folders are self-contained units. No mandatory substructure. Each folder contains everything necessary to be complete.

---

## The Three Layers

| Layer | What It Contains | Mark | Identity |
|-------|------------------|------|----------|
| **Theory** | Core principles | `:` (colon) | ME (cognitive layer theory) |
| **Meta** | Standards about standards | `-` (hyphen) | ME:NOT-ME:OTHER (joining layer) |
| **Specifics** | Actual standards | `_` (underscore) | NOT-ME (technical implications) |

The meta layer is the **joining layer**. It ensures theory and specifics stay grounded and connected to everything, including each other and OTHERS.

---

## Folder as Unit

```
# A folder IS complete
code_quality/
├── INDEX.md        # The standard itself (ANCHOR + CONTENT + UP)
└── [whatever it needs]

# NOT required subfolders
# NO mandatory examples/
# NO mandatory principles/
```

The folder contains what it needs. Nothing more. Nothing less.

---

## Naming

| Level | Case | Example |
|-------|------|---------|
| Theory docs | `NN_NAME.md` | `00_GENESIS.md` |
| Meta standards | `STANDARD_NAME.md` | `STANDARD_CREATION.md` |
| Specific folders | `lowercase_underscore/` | `code_quality/` |
| Index files | `INDEX.md` | `INDEX.md` |

---

## The Nesting Rule

Every folder is shaped by the layer above:

```
Theory (framework/00_GENESIS.md)
  ↓ shapes
Meta (standards/STANDARD_CREATION.md)
  ↓ shapes
Specifics (standards/code_quality/)
```

---

## Index Files

Every folder with multiple documents MUST have INDEX.md:

```markdown
# [Name]

**[Anchor statement]**

---

[Content]

---

## UP

[INDEX.md](../INDEX.md)
```

---

## The INDEX Rule

**INDEX is START and END. Primitives HOLD standards.**

### INDEX Role: Navigation Waypoint

INDEX is the waypoint you pass through:
- **START**: Enter a layer through its INDEX
- **NAVIGATE**: Move to primitives for content
- **END**: Return via UP links to INDEX to move across/between layers

```
                    ┌─────────┐
        START ──────►  INDEX  ◄────── END (via UP)
                    └────┬────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     [PRIMITIVE]    [PRIMITIVE]    [PRIMITIVE]
```

### INDEX Dual Purpose: Navigation AND Assessment

INDEX serves TWO purposes:

| Purpose | How |
|---------|-----|
| **Navigation** | Know where to go without reading every file |
| **Assessment** | Have enough summary to verify what you find is correct |

### The Three-Layer View

From any INDEX, you can look:
- **DOWN 2**: To primitives of child standards
- **UP 2**: To parent's parent INDEX
- **DOWN 1 + UP 1**: One layer each direction

Each INDEX has enough summary to ASSESS documents within this three-layer range.

```
        UP 2 ──► Parent's Parent INDEX
                         │
        UP 1 ──► Parent INDEX (can assess THIS INDEX)
                         │
      YOU ARE ──► THIS INDEX (can assess primitives AND child INDEX)
                         │
      DOWN 1 ──► Primitives / Child INDEX
                         │
      DOWN 2 ──► Child's Primitives
```

### What INDEX Contains

| INDEX MUST Have | Purpose |
|-----------------|---------|
| Hub diagram | Visual map of what's here |
| Direction table (UP/DOWN/ACROSS) | Navigate to other layers |
| Quick reference with COVERAGE | Know what each primitive SHOULD cover |
| Documents table | What primitives exist |
| Convergence references | Link to meta-standards |
| Changelog | Track evolution |

| INDEX MUST NOT Have | Why Not |
|---------------------|---------|
| The standards themselves (MUST/MUST NOT) | Belongs in primitives |
| Detailed pattern coverage | Meta content, not assessment criteria |
| Full WHY explanations | Primitives hold their own WHY |
| Detailed examples | Live in primitives |

### The Quick Reference Pattern

Quick Reference tells you WHAT a primitive SHOULD COVER (assessment) and WHERE to find it (navigation):

```markdown
# RIGHT - Assessment criteria (what SHOULD be covered)
| Primitive | Should Cover | Go Here |
|-----------|--------------|---------|
| LENGTH | Line limits, split patterns, compress vs expand | [LENGTH.md](LENGTH.md) |
| ANCHOR | One topic rule, limits/envelopes, exclusion test | [ANCHOR.md](ANCHOR.md) |

# Now you can ASSESS:
# - Does LENGTH.md cover line limits? ✓/✗
# - Does LENGTH.md cover split patterns? ✓/✗
# - Does LENGTH.md cover compress vs expand? ✓/✗

# WRONG - Defines the standard in INDEX
| Primitive | Rule |
|-----------|------|
| Length | MUST stay under 300 lines |  ← This IS the standard
| Anchor | MUST have ONE topic |         ← This IS the standard
```

**The difference:**
- **Assessment criteria**: "LENGTH should cover: line limits, split patterns, compress vs expand"
- **The standard itself**: "MUST stay under 300 lines"

INDEX holds criteria. Primitives hold standards.

### The Assessment Test

From any INDEX, you can:
1. Pick a primitive from Quick Reference
2. Read that primitive
3. Verify it covers what INDEX said it SHOULD cover

```
INDEX says: "LENGTH | Should Cover: line limits, split patterns, compress vs expand"

You read LENGTH.md and check:
□ Line limits? → Yes, "300 lines maximum"
□ Split patterns? → Yes, "The Split Pattern" section
□ Compress vs expand? → Yes, "Compress inward, Expand outward"

Assessment: LENGTH.md is COMPLETE
```

### The Navigation Test

If you can read INDEX and get the standard without reading primitives, **INDEX is holding content it shouldn't.**

```
# WRONG - INDEX holds the standard
INDEX.md contains: "MUST stay under 300 lines"
→ Why read LENGTH.md?

# RIGHT - INDEX holds assessment criteria
INDEX.md contains: "LENGTH | Should Cover: line limits, split patterns"
→ LENGTH.md holds the standard, INDEX lets you verify it's there
```

### Folder Validity

| Situation | Valid? | Reason |
|-----------|--------|--------|
| INDEX.md + primitives | Yes | INDEX navigates to primitives |
| INDEX.md only | **No** | INDEX has nothing to navigate to |
| Single file (no folder) | Yes | No navigation needed |

```
# CORRECT - INDEX navigates
code_quality/
├── INDEX.md           # START/END waypoint
├── TYPE_HINTS.md      # ← holds the standard
├── DOCSTRINGS.md      # ← holds the standard
└── STATIC_ANALYSIS.md # ← holds the standard

# WRONG - INDEX holds content
empty_standard/
└── INDEX.md           # Should be a file, not a folder
```

**INDEX IS the relationship.** It does not hold what it relates.

---

## The Layer Triad

**INDEX + README + Primitives. Three components at each layer.**

See [STANDARD_TRIAD](STANDARD_TRIAD.md) for:
- The three-component structure (INDEX, README, Primitives)
- Layer-specific requirements (Theory, Meta, Specifics)
- README content by layer type
- Dual-reader requirement (ME and NOT-ME)
- Layer governance through limits

---

## Anti-Patterns

| Pattern | Problem |
|---------|---------|
| Flat structure | No navigation hierarchy |
| Missing INDEX | No entry point |
| **INDEX-only folder** | **Folder serves no purpose; INDEX has nothing to relate** |
| Mandatory subfolders | Over-engineering |
| Deep nesting | Complexity without value |

---

## Framework Envelope

This standard is enveloped by:
- [00_GENESIS](../00_GENESIS.md) - THE GRAMMAR (naming)
- [04_ARCHITECTURE](../04_ARCHITECTURE.md) - HOLD:AGENT:HOLD (folder is HOLD)

---

## UP

[INDEX.md](INDEX.md)
