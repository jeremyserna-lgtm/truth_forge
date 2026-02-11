# THE PRIMITIVE

**The Template of All Scripts**

**Author:** Jeremy Serna
**Date:** January 3, 2026
**Location:** Denver, Colorado
**Version:** 1.0

---

## WHY (Theory)

### The Problem

Freeform scripts create chaos. Each Claude invents. Patterns diverge. No consistency. No validation. No protection.

### The Solution

One template. All scripts start here. Locked sections can't be modified. Your work goes in designated areas. A validator checks compliance.

**THE PRIMITIVE is the template of all scripts.**

### The Shape

```
┌─────────────────────────────────────────────────────────────┐
│                      THE PRIMITIVE                          │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ FRONT MATTER (locked)                                 │  │
│  │ - Links to framework                                  │  │
│  │ - Abridged standards                                  │  │
│  │ - Script metadata                                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ LOCKED SECTION                                        │  │
│  │ - Core functions (dedupe, similar)                    │  │
│  │ - inhale() - RAG from DuckDB                          │  │
│  │ - web_search() - external truth                       │  │
│  │ - prompt() - brain work                               │  │
│  │ - exhale() - two-gate write                           │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ YOUR WORK (fill in)                                   │  │
│  │ - Rules applied                                       │  │
│  │ - Your logic                                          │  │
│  │ - main()                                              │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### The Flow

Every script follows this flow:

```
INPUT (JSONL)
      │
      ▼
   INHALE (RAG from DuckDB)
      │
      ▼
   EXTERNAL (web_search, optional)
      │
      ▼
   BRAIN (prompt, your work)
      │
      ▼
   EXHALE
      │
      ├─► [GATE 1: dedupe + similar]
      │         │
      │         ▼
      │      JSONL (audit)
      │         │
      ├─► [GATE 2: dedupe + similar]
      │         │
      │         ▼
      │      DuckDB (canonical)
      │
      ▼
   OUTPUT
```

---

## WHAT (Specification)

### Built-in Functions

#### CORE (rule-based, no LLM)

| Function | Type | What it does |
|----------|------|--------------|
| `dedupe(content, store)` | Rule | Hash check, returns True if exists |
| `similar(content, store, threshold)` | Rule | Cosine similarity, returns True if similar |

#### INHALE

| Function | Type | What it does |
|----------|------|--------------|
| `inhale(query, limit, source_name)` | RAG | Query canonical DuckDB by similarity |

#### EXTERNAL

| Function | Type | What it does |
|----------|------|--------------|
| `web_search(query)` | External | Fetch truth from outside |

#### BRAIN

| Function | Type | What it does |
|----------|------|--------------|
| `prompt(content, task)` | LLM | Call Claude with a prompt |
| `extract_knowledge_atoms(content)` | LLM | THE membrane function |

#### EXHALE

| Function | Type | What it does |
|----------|------|--------------|
| `exhale(content, source_name, source_id, run_id)` | Write | Two-gate write to JSONL + DuckDB |

### The Two Gates

**Gate 1: Before JSONL (audit trail)**
```
content → dedupe(jsonl) → similar(jsonl) → WRITE JSONL
              │                 │
              │ exists          │ too similar
              ▼                 ▼
            SKIP              SKIP
```

**Gate 2: Before DuckDB (canonical)**
```
content → dedupe(duckdb) → similar(duckdb) → WRITE DuckDB
              │                 │
              │ exists          │ too similar
              ▼                 ▼
            SKIP              SKIP
```

### File Structure

```
~/.primitive_engine/
├── staging/                    # JSONL per source
│   ├── documents.jsonl
│   ├── claude_code.jsonl
│   └── {source_name}.jsonl
│
└── knowledge.duckdb            # Canonical store
```

### Script Metadata

Every script must have:

```python
script_id:      # Unique identifier
script_name:    # Human readable name
source_name:    # Registered source (documents, claude_code, etc.)
created_at:     # ISO timestamp
created_by:     # Author
purpose:        # What this script does

rules_applied:  # List of rules from /.claude/rules/
uses_external:  # True if using web_search
uses_brain:     # True if using prompt()
```

### Validation Checklist

When a new script is created from THE_PRIMITIVE, the validator checks:

| Check | Requirement |
|-------|-------------|
| □ METADATA | script_id, source_name, created_at present |
| □ LOCKED | Locked section unmodified |
| □ RULES | RULES_APPLIED list populated |
| □ EXHALE | main() calls exhale() |
| □ SOURCE | source_name is registered |
| □ PATTERN | Follows JSONL → AGENT → JSONL → DuckDB |

---

## HOW (Reference)

### Prompts Table

Prompts are organized by category:

#### CORE (rule-based, no LLM)

| Prompt ID | Function | Description |
|-----------|----------|-------------|
| `CORE.dedupe` | `dedupe()` | Hash comparison |
| `CORE.similar` | `similar()` | Cosine similarity |
| `CORE.embed` | `_embed()` | Generate embedding |
| `CORE.normalize` | `_normalize()` | Normalize text |
| `CORE.hash` | `_hash()` | SHA256 hash |

#### EXTRACT (membrane)

| Prompt ID | Function | Description |
|-----------|----------|-------------|
| `EXTRACT.atoms` | `extract_knowledge_atoms()` | "Pull the truth from this as sentences." |

#### ANALYZE

| Prompt ID | Function | Description |
|-----------|----------|-------------|
| `ANALYZE.summarize` | `summarize()` | Summarize content |
| `ANALYZE.review` | `review_output()` | Review quality |
| `ANALYZE.evaluate` | `evaluate()` | Evaluate against criteria |
| `ANALYZE.compare` | `compare()` | Compare two contents |

#### GENERATE

| Prompt ID | Function | Description |
|-----------|----------|-------------|
| `GENERATE.tags` | `generate_tags()` | Generate relevant tags |
| `GENERATE.metadata` | `extract_metadata()` | Extract metadata |
| `GENERATE.title` | `generate_title()` | Generate title |
| `GENERATE.questions` | `generate_questions()` | Generate questions from content |

#### TRANSFORM

| Prompt ID | Function | Description |
|-----------|----------|-------------|
| `TRANSFORM.rewrite` | `rewrite()` | Rewrite content |
| `TRANSFORM.translate` | `translate()` | Translate content |
| `TRANSFORM.simplify` | `simplify()` | Simplify content |
| `TRANSFORM.expand` | `expand()` | Expand content |

#### CLASSIFY

| Prompt ID | Function | Description |
|-----------|----------|-------------|
| `CLASSIFY.sentiment` | `classify_sentiment()` | Sentiment analysis |
| `CLASSIFY.topic` | `classify_topic()` | Topic classification |
| `CLASSIFY.intent` | `classify_intent()` | Intent classification |
| `CLASSIFY.me_not_me` | `classify_me_not_me()` | ME/NOT ME classification |

### Framework Integration

```
THE_PURPOSE (SMILES)
       │
       ▼
THE_BOUNDARIES (focus)
       │
       ▼
THE_PATTERN (JSONL → AGENT → JSONL)
       │
       ▼
THE_PRIMITIVE (this - the template)
       │
       ├── THE_PRIMITIVE.py (code)
       ├── THE_PRIMITIVE.md (spec)
       └── THE_VALIDATOR.py (hook)
```

### Usage

#### Create a new script

```bash
# Copy the template
cp THE_PRIMITIVE.py my_script.py

# Edit YOUR WORK section
# Fill in metadata
# Fill in rules
# Fill in logic

# Validator runs automatically (hook)
# Or run manually:
python THE_VALIDATOR.py my_script.py
```

#### Example script

```python
# In YOUR WORK section:

RULES_APPLIED = [
    "01_SEE_COST",
    "11_THE_PATTERN",
]

def main(input_jsonl: Path, source_name: str):
    run_id = str(uuid.uuid4())[:8]

    with open(input_jsonl, "r") as f:
        records = [json.loads(line) for line in f]

    all_atoms = []

    for record in records:
        content = record.get("content", "")

        # INHALE: Get context
        context = inhale(content[:100], limit=5)

        # BRAIN: Your work
        result = prompt(content, task="ANALYZE.summarize")

        # EXTRACT: Get atoms
        atoms = extract_knowledge_atoms(content)
        all_atoms.extend(atoms)

    # EXHALE: Write through gates
    stats = exhale(all_atoms, source_name)

    return stats
```

---

### The One Rule

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  All scripts start from THE_PRIMITIVE.                      │
│  Locked sections cannot be modified.                        │
│  Your work goes in designated areas.                        │
│  The validator checks compliance.                           │
│                                                             │
│  No freeform scripts. Ever.                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

*One template. Locked sections. Your work in designated areas. The validator checks. No freeform scripts.*

— THE_FRAMEWORK

---

**END OF DOCUMENT**
