# Contract: KNOWLEDGE_ATOM_SCHEMA

**Type**: exist-now (data schema)
**Pattern ID**: `pat:atom_schema`
**Status**: Contract defined
**Created**: 2025-12-30

---

## The Pattern

**Every knowledge atom has a growth type.**

When truth unknown is consumed into atoms, those atoms grow either structure, pattern, or both. The atom schema must capture this.

```
Truth Unknown
    │
    ↓ Atomization
    │
Knowledge Atom
    │
    ├── content (what the truth IS)
    │
    ├── growth_type (what it GROWS)
    │   ├── structure → new primitives using existing patterns
    │   ├── pattern → new patterns, new capability
    │   └── both → evolution (new pattern + new primitives)
    │
    └── [other fields...]
```

---

## Core Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `atom_id` | STRING | Yes | Unique identifier (`atm:{hash}`) |
| `content` | STRING | Yes | The atomic truth |
| `content_hash` | STRING | Yes | SHA256 of content |
| `growth_type` | STRING | Yes | `structure`, `pattern`, or `both` |
| `question` | STRING | No | Which of the 6 questions (WHAT/WHY/HOW/WHERE/WHEN/WHO) |
| `source_file_id` | STRING | No | Link to file_registry |
| `source_run_id` | STRING | No | Link to extraction run |
| `created_at` | TIMESTAMP | Yes | When captured |

---

## Growth Type Field

**This is the key insight.**

| Growth Type | What It Describes | How to Identify |
|-------------|-------------------|-----------------|
| `structure` | Content that fits existing patterns | "This pipeline does X" |
| `pattern` | New way of organizing/containing | "Things should be structured as Y" |
| `both` | Evolution - pattern + content together | "This new approach Z enables these things" |

### Examples

**Structure atom:**
```json
{
  "atom_id": "atm:abc123",
  "content": "The text messages pipeline extracts from chat.db",
  "growth_type": "structure",
  "question": "WHAT"
}
```

**Pattern atom:**
```json
{
  "atom_id": "atm:def456",
  "content": "Every primitive should have a series of 6 documents answering WHAT/WHY/HOW/WHERE/WHEN/WHO",
  "growth_type": "pattern",
  "question": null
}
```

**Both atom:**
```json
{
  "atom_id": "atm:ghi789",
  "content": "The metabolism pattern describes how atoms process atoms - and this very contract demonstrates it",
  "growth_type": "both",
  "question": "HOW"
}
```

---

## Question Field (Optional)

When an atom answers one of the six questions, tag it:

| Value | What It Answers |
|-------|-----------------|
| `WHAT` | Identity, definition |
| `WHY` | Purpose, origin |
| `HOW` | Mechanism, flow |
| `WHERE` | Location, path |
| `WHEN` | Timing, conditions |
| `WHO` | Actors, stakeholders |
| `null` | Doesn't answer a specific question |

**Pattern atoms often don't answer a specific question** - they describe the container, not the content.

---

## The Search Pattern

**We look for growth types when processing.**

```python
# Find atoms that could become patterns
pattern_candidates = query("""
    SELECT * FROM knowledge_atoms
    WHERE growth_type IN ('pattern', 'both')
    AND created_at > @since
""")

# Find structure atoms for a specific system
system_atoms = query("""
    SELECT * FROM knowledge_atoms
    WHERE growth_type = 'structure'
    AND content LIKE '%text_messages%'
    ORDER BY question
""")

# Find evolution points
evolution_atoms = query("""
    SELECT * FROM knowledge_atoms
    WHERE growth_type = 'both'
    ORDER BY created_at DESC
""")
```

---

## Sufficiency by Growth Type

For GENERATIVE_PRIMITIVE to work, we need sufficient atoms:

| To Generate | Need These Atoms |
|-------------|------------------|
| New primitive | Structure atoms for all 6 questions |
| New pattern | Pattern atoms describing the container |
| Evolution | Both atoms showing pattern + primitives |

```python
def can_generate_primitive(system_name):
    """Check if enough structure atoms exist."""
    questions = ["WHAT", "WHY", "HOW", "WHERE", "WHEN", "WHO"]
    for q in questions:
        count = count_atoms(
            growth_type="structure",
            question=q,
            content_matches=system_name
        )
        if count < MINIMUM_PER_QUESTION:
            return False
    return True

def can_generate_pattern():
    """Check if enough pattern atoms exist."""
    return count_atoms(growth_type="pattern") >= MINIMUM_PATTERN_ATOMS
```

---

## Tagging During Extraction

When extracting atoms from content, determine growth type:

```python
def classify_growth_type(content: str) -> str:
    """Classify atom growth type from content."""

    # Pattern indicators
    pattern_signals = [
        "should be structured",
        "every system has",
        "pattern for",
        "template",
        "all primitives",
        "the shape of",
    ]

    # Structure indicators
    structure_signals = [
        "this system",
        "the pipeline",
        "it does",
        "located at",
        "used by",
    ]

    has_pattern = any(s in content.lower() for s in pattern_signals)
    has_structure = any(s in content.lower() for s in structure_signals)

    if has_pattern and has_structure:
        return "both"
    elif has_pattern:
        return "pattern"
    else:
        return "structure"
```

---

## BigQuery Schema

```sql
CREATE TABLE IF NOT EXISTS `jeremy-serna.knowledge.knowledge_atoms` (
    atom_id STRING NOT NULL,
    content STRING NOT NULL,
    content_hash STRING NOT NULL,
    growth_type STRING NOT NULL,  -- 'structure', 'pattern', 'both'
    question STRING,              -- 'WHAT', 'WHY', 'HOW', 'WHERE', 'WHEN', 'WHO', or NULL
    source_file_id STRING,
    source_run_id STRING,
    created_at TIMESTAMP NOT NULL,
    metadata JSON
)
PARTITION BY DATE(created_at)
CLUSTER BY growth_type, question, content_hash;
```

---

## The Loop Closes

```
Truth Unknown enters
    │
    ↓ Atomization with growth_type tagging
    │
Atoms tagged (structure/pattern/both)
    │
    ├── Structure atoms → accumulate → generate primitives
    │
    ├── Pattern atoms → accumulate → generate patterns
    │
    └── Both atoms → evolution events → system learns
```

---

## Definition of Done

### Phase 1: Conceptual
- [x] Schema defined
- [x] Growth types specified
- [x] Question field documented

### Phase 2: Implementation
- [ ] BigQuery table created/updated
- [ ] Extraction pipeline tags growth_type
- [ ] Classification function implemented

### Phase 3: Validation
- [ ] Atoms properly tagged
- [ ] Queries by growth_type work
- [ ] Sufficiency checks use growth_type

---

## Related

- [THE_METABOLISM.md](THE_METABOLISM.md) - Growth modes
- [GENERATIVE_PRIMITIVE.md](GENERATIVE_PRIMITIVE.md) - Uses atoms
- [FILE_TO_ATOM_LINEAGE.md](FILE_TO_ATOM_LINEAGE.md) - Traceability

---

**Every atom knows what it grows. Structure, pattern, or both. We look for them. We use them. The system builds itself.**
