# THE TRUTH LAYER

**Recursive Convergence to 1 of 1**

**Type**: Specification
**Status**: Active
**Created**: 2026-01-03
**Author**: Jeremy Serna

---

## Document Structure

- **Theory**: Why one prompt, why convergence
- **Specification**: The architecture, the flow
- **Reference**: Operations, schema, code locations

---

# THEORY

## THE PRINCIPLE

One prompt. Every system. Same brain.

```
"Pull the truth from this as sentences."
```

One context window. One blob of text. One convergence.

The LLM decides the shape. Through recursive convergence, similar truths become the same sentence.

**We don't specify the form. We trust the convergence.**

## Why This Works

Same brain + same prompt = same output.

When you feed similar content to the same LLM with the same prompt, it produces the same result. This is the foundation of convergence.

We don't need:
- Shape specifications (NOUN VERB OBJECT)
- Controlled vocabularies
- Entity resolution systems
- Parsing rules

The LLM naturally converges because it's the same brain seeing similar things.

---

# SPECIFICATION

## THE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INTERNAL SYSTEMS                            │
│                                                                     │
│  System 1 (documents)     → "Pull the truth..." → atoms            │
│  System 2 (conversations) → "Pull the truth..." → atoms            │
│  System 3 (emails)        → "Pull the truth..." → atoms            │
│  System 4 (web)           → "Pull the truth..." → atoms            │
│  ...                                                                │
│                                                                     │
│  Each system:                                                       │
│    1. Uses THE_PRIMITIVE pattern                                    │
│    2. Calls exhale() with same prompt                               │
│    3. Does similarity dedupe within itself                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ all atoms merge
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FINAL DATABASE                               │
│                                                                     │
│                    All atoms from all systems                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ similarity search across all
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     CONVERGENCE LAYER                               │
│                                                                     │
│  1. Similarity search groups atoms                                  │
│  2. Concatenate each group into one blob of text                    │
│  3. One context window: "Pull the truth from this as sentences."    │
│  4. LLM produces fewer sentences (convergence)                      │
│  5. New atoms replace old, old marked deprecated                    │
│  6. Repeat until stable (recursive)                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                        1 OF 1
              (One sentence per truth)
```

## THE PROMPT

One prompt. Used everywhere.

```python
EXTRACT_PROMPT = """
Pull the truth from this as sentences.

{content}
"""
```

That's it.

- One context window full of stuff
- No shape specification
- The LLM finds the natural form
- Same brain + same prompt = convergence

## THE CONVERGENCE

### Why It Works

Take similar atoms. Concatenate into one blob. Feed to LLM.

```
Input (one context window):
BigQuery costs $5 per terabyte.
BigQuery charges $5/TB.
BQ pricing is $5 per TB scanned.

Prompt: "Pull the truth from this as sentences."

Output:
BigQuery costs $5 per terabyte.
```

The LLM sees one blob of text with redundant information. It pulls the truth. One sentence.

### The Recursive Loop

```
ALL ATOMS
    │
    ▼
SIMILARITY SEARCH → groups similar atoms
    │
    ▼
FOR EACH GROUP:
    │
    ├── Concatenate into one blob of text
    │
    ├── "Pull the truth from this as sentences."
    │
    ├── LLM outputs (fewer sentences)
    │
    └── Deprecate old, create new
    │
    ▼
REPEAT until no groups have >1 atom
    │
    ▼
STABLE (1 of 1)
```

## TWO LEVELS OF DEDUPLICATION

| Level | When | What | How |
|-------|------|------|-----|
| **Within system** | At exhale() | Each system dedupes its own atoms | Similarity threshold |
| **Across all systems** | Convergence layer | The whole database dedupes against itself | Similarity search → same prompt |

## THE SCHEMA

Simplified. No parsed structure needed.

```python
{
    # Identity
    "atom_id": str,                    # atom:{source}:{hash}

    # Content
    "content": str,                    # The truth sentence
    "content_hash": str,               # SHA256 for exact dedupe
    "embedding": list[float],          # Vector for similarity search

    # Source
    "source_name": str,                # documents, claude_code, web, etc.
    "source_id": str,                  # Optional: specific source identifier

    # Truth state
    "status": str,                     # "active" | "deprecated"
    "deprecated_by": str | None,       # atom_id that superseded this
    "merged_from": list[str] | None,   # atom_ids that merged into this

    # Metadata
    "created_at": str,
    "converged_at": str | None,        # When last convergence happened
}
```

## THE FLOW

### System Level (Each System)

```
Raw content (document, conversation, email, etc.)
        │
        ▼
"Pull the truth from this as sentences."
        │
        ▼
Atoms created
        │
        ▼
Similarity dedupe within system
        │
        ▼
Store in system's atoms
        │
        ▼
Merge to final database
```

### Convergence Level (Final Layer)

```
Final database (all atoms)
        │
        ▼
Similarity search → group similar atoms
        │
        ▼
For each group:
    │
    ├── Concatenate into one blob
    │
    └── "Pull the truth from this as sentences."
        │
        ▼
LLM outputs (fewer sentences)
        │
        ▼
Create new atoms, deprecate old
        │
        ▼
Repeat until stable
        │
        ▼
1 of 1
```

## TRUTH RULES

```
1. ACTIVE means true NOW
2. DEPRECATED means was true, superseded by another
3. One prompt: "Pull the truth from this as sentences."
4. One context window. One blob. One convergence.
5. Recursive until stable.
6. Primitives receive only active atoms via inhale()
```

---

# REFERENCE

## THE OPERATIONS

### Similarity Search

```python
def find_similar_groups(atoms: list, threshold: float = 0.85) -> list[list]:
    """
    Group atoms by similarity.
    Returns list of groups where each group has similar atoms.
    """
    groups = []
    used = set()

    for atom in atoms:
        if atom["atom_id"] in used:
            continue

        group = [atom]
        for other in atoms:
            if other["atom_id"] in used:
                continue
            if cosine_similarity(atom["embedding"], other["embedding"]) > threshold:
                group.append(other)
                used.add(other["atom_id"])

        used.add(atom["atom_id"])
        groups.append(group)

    return groups
```

### Converge Group

```python
def converge_group(group: list[dict]) -> list[dict]:
    """
    Take a group of similar atoms.
    Concatenate into one blob.
    Feed to LLM.
    Return converged atoms (usually fewer).
    """
    if len(group) == 1:
        return group  # Nothing to converge

    # One blob of text
    blob = "\n".join([atom["content"] for atom in group])

    # One prompt
    result = llm(f"Pull the truth from this as sentences.\n\n{blob}")

    # Parse result into sentences
    new_atoms = create_atoms(result, merged_from=[a["atom_id"] for a in group])

    # Deprecate old atoms
    for atom in group:
        deprecate(atom["atom_id"], by=new_atoms[0]["atom_id"])

    return new_atoms
```

### Recursive Convergence

```python
def run_convergence():
    """
    Run convergence until stable.
    """
    while True:
        atoms = get_active_atoms()
        groups = find_similar_groups(atoms)

        # Filter to groups with >1 atom (need convergence)
        multi_groups = [g for g in groups if len(g) > 1]

        if not multi_groups:
            break  # Stable

        for group in multi_groups:
            converge_group(group)
```

## FILE LOCATIONS

```
architect_central_services/src/architect_central_services/
├── the_extractor.py           # exhale() and inhale()
└── truth_layer/
    ├── __init__.py
    ├── similarity.py          # find_similar_groups()
    ├── converge.py            # converge_group(), run_convergence()
    └── deprecate.py           # Mark atoms deprecated
```

## DUCKDB TABLES

```sql
CREATE TABLE knowledge_atoms (
    atom_id VARCHAR PRIMARY KEY,

    -- Content
    content VARCHAR NOT NULL,
    content_hash VARCHAR NOT NULL,
    embedding FLOAT[],

    -- Source
    source_name VARCHAR NOT NULL,
    source_id VARCHAR,

    -- Truth state
    status VARCHAR DEFAULT 'active',  -- 'active' | 'deprecated'
    deprecated_by VARCHAR,
    merged_from JSON,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    converged_at TIMESTAMP,

    -- Indexes
    FOREIGN KEY (deprecated_by) REFERENCES knowledge_atoms(atom_id)
);

CREATE INDEX idx_status ON knowledge_atoms(status);
CREATE INDEX idx_content_hash ON knowledge_atoms(content_hash);
CREATE INDEX idx_source ON knowledge_atoms(source_name);
```

## RELATED DOCUMENTS

| Document | Relationship |
|----------|--------------|
| [THE_FRAMEWORK.md](../../1_core/00_THE_FRAMEWORK.md) | The foundation |
| [THE_PRIMITIVE.md](../../1_core/14_THE_PRIMITIVE.md) | The script template |
| [THE_EXTRACTOR.md](../../1_core/12_THE_EXTRACTOR.md) | The canonical implementation |
| [THE_METABOLISM.md](THE_METABOLISM.md) | How atoms process atoms |

---

## SUMMARY

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ONE PROMPT: "Pull the truth from this as sentences."               │
│                                                                     │
│  ONE CONTEXT WINDOW. ONE BLOB. ONE CONVERGENCE.                     │
│                                                                     │
│  Every system uses the same prompt.                                 │
│  Every system does similarity dedupe.                               │
│  All atoms merge to final database.                                 │
│  Final layer: similarity search → concatenate → same prompt.        │
│  Recursive until stable.                                            │
│                                                                     │
│  Result: 1 of 1.                                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

*One prompt. One context window. Recursive convergence. 1 of 1.*

— THE_FRAMEWORK
