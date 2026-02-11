# Contract: SYSTEM_FOLDER_PATTERN

**Type**: exist-now (organizational primitive)
**Status**: Contract defined
**Created**: 2025-12-30

---

## The Pattern

**Every system gets the same folder structure. The folder IS the system's primitive.**

```
{system}/
├── docs/
│   └── primitive/           ← The system's core truth (SAME FOR ALL)
│       ├── INDEX.md         ← Entry point
│       ├── 01_WHAT.md       ← What it IS
│       ├── 02_WHY.md        ← Why it EXISTS
│       ├── 03_HOW.md        ← How it WORKS
│       ├── 04_WHERE.md      ← Where it LIVES
│       ├── 05_WHEN.md       ← When to USE
│       └── 06_WHO.md        ← Who USES it
├── src/                     ← Code
├── tests/                   ← Tests
├── config/                  ← Configuration
└── sql/                     ← Schemas (if applicable)
```

**The folder structure IS the identity. Same shape, different content.**

---

## The Parallel Directory Bank

Every system mirrors the same structure:

```
pipelines/text_messages/docs/primitive/
pipelines/chatgpt/docs/primitive/
pipelines/zoom/docs/primitive/
identity/docs/primitive/
truth/docs/primitive/
knowledge_atom_service/docs/primitive/
```

**Look in ANY system's `docs/primitive/` - you find the same six files.**

---

## What Each File Answers

| File | Question | One Sentence |
|------|----------|--------------|
| `01_WHAT.md` | What IS this? | Definition and boundaries |
| `02_WHY.md` | Why EXIST? | Origin, purpose, gap filled |
| `03_HOW.md` | How WORK? | Input → Process → Output |
| `04_WHERE.md` | Where LIVE? | Code, data, docs locations |
| `05_WHEN.md` | When USE? | Use cases, anti-patterns |
| `06_WHO.md` | Who INVOLVED? | Users, maintainers, contacts |

---

## The INDEX.md Template

Every `primitive/` folder starts with INDEX.md:

```markdown
# {System Name} - Primitive Series

**System**: {system_name}
**Created**: {date}
**Author**: {author}

---

## This System In One Sentence

{System} is a {type} that {does what} for {whom}.

---

## Quick Reference

| Question | Answer |
|----------|--------|
| What? | {one line} |
| Why? | {one line} |
| How? | {one line} |
| Where? | {one line} |
| When? | {one line} |
| Who? | {one line} |

---

## Contents

1. [What It Is](01_WHAT.md)
2. [Why It Exists](02_WHY.md)
3. [How It Works](03_HOW.md)
4. [Where It Lives](04_WHERE.md)
5. [When To Use](05_WHEN.md)
6. [Who's Involved](06_WHO.md)

---

## Related Systems

| System | Relationship |
|--------|--------------|
| {related} | {how connected} |
```

---

## Scaffolding a New System

```bash
#!/bin/bash
# scaffold_system.sh - Create a new system with primitive series

SYSTEM_NAME=$1
SYSTEM_PATH=$2

mkdir -p "$SYSTEM_PATH/docs/primitive"
mkdir -p "$SYSTEM_PATH/src"
mkdir -p "$SYSTEM_PATH/tests"
mkdir -p "$SYSTEM_PATH/config"

# Copy templates
for f in INDEX 01_WHAT 02_WHY 03_HOW 04_WHERE 05_WHEN 06_WHO; do
    cp "docs/primitive/contracts/templates/${f}.template.md" \
       "$SYSTEM_PATH/docs/primitive/${f}.md"
    # Replace placeholder
    sed -i '' "s/{SYSTEM_NAME}/$SYSTEM_NAME/g" "$SYSTEM_PATH/docs/primitive/${f}.md"
done

echo "Created system: $SYSTEM_NAME at $SYSTEM_PATH"
echo "Fill in the primitive series in $SYSTEM_PATH/docs/primitive/"
```

---

## Why This Pattern

1. **Consistency**: Any system, same structure, no learning curve
2. **Completeness**: Six questions cover existence
3. **Discovery**: Know where to look for any system
4. **Comparison**: Easy to compare systems side-by-side
5. **Onboarding**: New person reads primitive/, understands system

---

## The Folder IS the Truth

The folder structure isn't metadata ABOUT the system. It IS the system's documented existence.

```
The folder exists → The system's truth is captured
The folder is empty → The system lacks documentation
The folder is missing → The system isn't properly defined
```

---

## Definition of Done (New System)

A system is NOT properly defined until:

- [ ] `docs/primitive/` folder exists
- [ ] `INDEX.md` has one-sentence definition
- [ ] `01_WHAT.md` defines boundaries
- [ ] `02_WHY.md` explains purpose
- [ ] `03_HOW.md` documents flow
- [ ] `04_WHERE.md` lists locations
- [ ] `05_WHEN.md` describes use cases
- [ ] `06_WHO.md` identifies stakeholders

---

## Related

- [PRIMITIVE_SERIES_TEMPLATE.md](PRIMITIVE_SERIES_TEMPLATE.md) - Document templates
- [DOCUMENT_ROUTING.md](DOCUMENT_ROUTING.md) - Where docs go
- [FILE_TO_ATOM_LINEAGE.md](FILE_TO_ATOM_LINEAGE.md) - File tracking

---

**Every system. Same folder. Same files. Different content. The pattern IS the primitive.**
