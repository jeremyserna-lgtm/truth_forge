# Contract: PRIMITIVE_SERIES_TEMPLATE

**Type**: do-now (documentation pattern)
**Status**: Contract defined
**Created**: 2025-12-30

---

## The Pattern

Every system has a primitive series - the same documents that describe its entire existence.

**The template is universal. The content is specific.**

```
{system}/docs/primitive/
├── 01_WHAT.md      # What it IS
├── 02_WHY.md       # Why it EXISTS
├── 03_HOW.md       # How it WORKS
├── 04_WHERE.md     # Where it LIVES
├── 05_WHEN.md      # When to USE it
└── 06_WHO.md       # Who USES/MAINTAINS it
```

---

## The Six Documents

### 01_WHAT.md - Identity

**Question**: "What IS this system?"

```markdown
# {System Name}: What It Is

## TL;DR
- One sentence: what this system IS
- One sentence: what it IS NOT
- One sentence: its core responsibility

## Definition
{Clear definition in 2-3 sentences}

## Boundaries
- **Includes**: {what's inside the boundary}
- **Excludes**: {what's outside the boundary}

## The Sentence
{System} is a {type} that {does what} for {whom}.
```

---

### 02_WHY.md - Purpose

**Question**: "Why does this system EXIST?"

```markdown
# {System Name}: Why It Exists

## TL;DR
- The problem it solves
- The value it creates
- What breaks without it

## Origin Story
{How/when/why this was created}

## The Gap It Fills
{What was missing before this existed}

## Without This System
{What fails, degrades, or becomes impossible}
```

---

### 03_HOW.md - Mechanics

**Question**: "How does this system WORK?"

```markdown
# {System Name}: How It Works

## TL;DR
- Input: what goes in
- Process: what happens
- Output: what comes out

## The Flow
{Diagram or description of the flow}

## Key Components
| Component | Role |
|-----------|------|
| {name} | {what it does} |

## Dependencies
- **Requires**: {what this depends on}
- **Enables**: {what depends on this}

## Code Entry Point
`path/to/main/file.py:function_name`
```

---

### 04_WHERE.md - Location

**Question**: "Where does this system LIVE?"

```markdown
# {System Name}: Where It Lives

## TL;DR
- Code location
- Data location
- Documentation location

## Code
| Type | Path |
|------|------|
| Source | `path/to/source/` |
| Tests | `path/to/tests/` |
| Config | `path/to/config/` |

## Data
| Type | Location |
|------|----------|
| BigQuery | `dataset.table` |
| Local | `path/to/local/` |
| GCS | `gs://bucket/path/` |

## Documentation
| Type | Path |
|------|------|
| Primitive series | `{system}/docs/primitive/` |
| Specs | `{system}/docs/spec/` |
| Reference | `{system}/docs/ref/` |
```

---

### 05_WHEN.md - Usage

**Question**: "When should you USE this system?"

```markdown
# {System Name}: When To Use It

## TL;DR
- Use when: {conditions}
- Don't use when: {conditions}
- Alternatives: {if not this, then what}

## Use Cases
| Scenario | Use This? | Why |
|----------|-----------|-----|
| {scenario 1} | Yes/No | {reason} |

## Decision Tree
```
Need to {action}?
├── Yes → Does {condition}?
│   ├── Yes → USE THIS SYSTEM
│   └── No → Use {alternative}
└── No → Don't use this
```

## Anti-Patterns
- Don't use for: {wrong use case}
- Instead use: {right choice}
```

---

### 06_WHO.md - Stakeholders

**Question**: "Who USES and MAINTAINS this system?"

```markdown
# {System Name}: Who's Involved

## TL;DR
- Users: who uses this
- Maintainers: who keeps it running
- Stakeholders: who cares about it

## Users
| User Type | How They Use It |
|-----------|-----------------|
| {type} | {usage} |

## Maintainers
| Role | Responsibility |
|------|----------------|
| {role} | {what they do} |

## Contact
- **Owner**: {name/team}
- **Questions**: {where to ask}
- **Issues**: {where to report}

## Related Teams/Systems
| Related | Relationship |
|---------|--------------|
| {system} | {how they connect} |
```

---

## Template Usage

### Creating a New System's Primitive Series

```bash
# 1. Create the folder
mkdir -p {system}/docs/primitive

# 2. Copy templates
cp docs/primitive/contracts/templates/01_WHAT.template.md {system}/docs/primitive/01_WHAT.md
cp docs/primitive/contracts/templates/02_WHY.template.md {system}/docs/primitive/02_WHY.md
cp docs/primitive/contracts/templates/03_HOW.template.md {system}/docs/primitive/03_HOW.md
cp docs/primitive/contracts/templates/04_WHERE.template.md {system}/docs/primitive/04_WHERE.md
cp docs/primitive/contracts/templates/05_WHEN.template.md {system}/docs/primitive/05_WHEN.md
cp docs/primitive/contracts/templates/06_WHO.template.md {system}/docs/primitive/06_WHO.md

# 3. Fill in the templates
# 4. Register the documents
```

---

## The Recursion: Files ARE Primitives AND Follow Patterns

**Critical insight**: The primitive series files are themselves primitives.

```
Primitive Series Files
    │
    ├── ARE exist-now primitives
    │   ├── file_id (from file_registry)
    │   ├── doc_id (from DOCUMENT_METADATA)
    │   └── content_hash (for lineage)
    │
    └── FOLLOW a pattern (this contract)
        └── Pattern is also a primitive (pat:prim_series)
```

| Aspect | The File | The Pattern |
|--------|----------|-------------|
| **What it IS** | An exist-now document | An exist-now pattern contract |
| **Tracked as** | Primitive in file_registry | Pattern in pattern_contracts |
| **Identity** | `doc:{system}:primitive:0X:{question}` | `pat:prim_series` |
| **Content** | System-specific answers | Universal template |

**The recursion closes**: Patterns define how primitives are documented. The pattern itself is a primitive. Primitives following patterns become more primitives.

---

## Systems That Need Primitive Series

| System | Path | Status |
|--------|------|--------|
| Text Messages Pipeline | `pipelines/text_messages/docs/primitive/` | ✅ Complete |
| ChatGPT Pipeline | `pipelines/chatgpt/docs/primitive/` | TODO |
| Zoom Pipeline | `pipelines/zoom/docs/primitive/` | TODO |
| Knowledge Atom Service | `knowledge_atom_service/primitive/` | TODO |
| Truth Service | `truth/primitive/` | TODO |
| Identity Service | `identity/docs/primitive/` | ✅ Complete |
| Embedding Service | `embedding_service/primitive/` | TODO |
| File Registry | `knowledge/primitive/` | TODO |

---

## The Index (Every Primitive Series Has One)

Every primitive folder also has an INDEX.md:

```markdown
# {System Name} - Primitive Series

**Purpose**: Core documentation for {system name}.

## Contents

| # | Document | Question |
|---|----------|----------|
| 01 | [WHAT](01_WHAT.md) | What IS this? |
| 02 | [WHY](02_WHY.md) | Why does it EXIST? |
| 03 | [HOW](03_HOW.md) | How does it WORK? |
| 04 | [WHERE](04_WHERE.md) | Where does it LIVE? |
| 05 | [WHEN](05_WHEN.md) | When to USE it? |
| 06 | [WHO](06_WHO.md) | Who USES/MAINTAINS it? |

## Quick Answer

- **What**: {one line}
- **Why**: {one line}
- **How**: {one line}
- **Where**: {one line}
- **When**: {one line}
- **Who**: {one line}
```

---

## Definition of Done

### Phase 1: Created
- [x] Template contract defined
- [ ] Template files created in `docs/primitive/contracts/templates/`
- [ ] Script to scaffold new primitive series

### Phase 2: Adopted
- [ ] Text Messages Pipeline has primitive series
- [ ] ChatGPT Pipeline has primitive series
- [ ] At least 3 services have primitive series

### Phase 3: Enforced
- [ ] New systems MUST have primitive series before deployment
- [ ] CI check: primitive series exists for registered systems

---

## Related

- [DOCUMENT_ROUTING.md](DOCUMENT_ROUTING.md) - Where docs go
- [DOCUMENT_METADATA.md](DOCUMENT_METADATA.md) - Doc classification
- [DOCUMENT_SERIES_FRAMEWORK.md](../../../standards/DOCUMENT_SERIES_FRAMEWORK.md) - Series structure

---

**Every system has the same six questions answered. Different answers, same structure.**
