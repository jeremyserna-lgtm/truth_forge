# THE PATTERN

**The Universal Architecture**

**Author:** Jeremy Serna
**Date:** January 3, 2026
**Location:** Denver, Colorado
**Version:** 3.0

---

## The Pattern

```
JSONL → AGENT → JSONL → DuckDB
```

That's it. Everything follows this. No exceptions.

---

## WHY (Theory)

### Why One Pattern

When there are multiple patterns:
- Claude invents
- Systems diverge
- Jeremy can't hold it
- Meaning dies

When there is one pattern:
- Every Claude follows the same path
- Systems align
- Jeremy can see the whole
- Meaning is possible

**One pattern. Every system. Every script. Every time.**

### The Shape

```
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│          │      │          │      │          │      │          │
│  JSONL   │─────►│  AGENT   │─────►│  JSONL   │─────►│  DuckDB  │
│          │      │          │      │          │      │          │
│ (input)  │      │(process) │      │ (audit)  │      │(canonic) │
│          │      │          │      │          │      │          │
└──────────┘      └──────────┘      └──────────┘      └──────────┘
```

| Position | What It Is | Properties |
|----------|------------|------------|
| **JSONL (input)** | Source data | From external, raw |
| **AGENT** | Processor | Calls brain, does work, follows rules |
| **JSONL (audit)** | Output storage | Append-only, one per source, deduped |
| **DuckDB** | Canonical store | One store, queryable, strictly deduped |

### The Components

#### THE PRIMITIVE

Every script is THE_PRIMITIVE. It has everything built in:

```
┌─────────────────────────────────────────────────────────────┐
│                      THE PRIMITIVE                          │
│                                                             │
│  Built-in:                                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ inhale(query)     → RAG from DuckDB                   │  │
│  │ web_search(query) → External truth                    │  │
│  │ prompt(content)   → Brain work (LLM)                  │  │
│  │ dedupe(content)   → Hash check (rule)                 │  │
│  │ similar(content)  → Cosine check (rule)               │  │
│  │ exhale(content)   → Two-gate write                    │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  Your work:                                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ main() → Your logic using built-in functions          │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### THE TWO GATES

Every exhale goes through two gates:

```
CONTENT
    │
    ▼
[GATE 1: dedupe + similar]
    │
    ├── EXISTS/SIMILAR → skip
    │
    └── NEW → write
            │
            ▼
        JSONL (audit)
            │
            ▼
[GATE 2: dedupe + similar]
    │
    ├── EXISTS/SIMILAR → skip
    │
    └── NEW → write
            │
            ▼
        DuckDB (canonical)
```

**Gate 1:** Before JSONL (audit trail gets deduped within source)
**Gate 2:** Before DuckDB (canonical is strictly unique across all sources)

#### THE BRAIN

The brain is called within the agent. It has no source. It sees.

```python
# Brain work (LLM)
result = prompt(content, task="ANALYZE.summarize")

# Membrane function (THE prompt)
atoms = extract_knowledge_atoms(content)  # "Pull the truth as sentences"
```

#### EXTERNAL

External truth comes from web_search. It's just another input.

```python
# Get external truth
external = web_search("BigQuery pricing")

# ME/NOT ME classifier decides when to use
if classify_me_not_me(query) == "NOT ME":
    external = web_search(query)
```

### The Flow

Every script follows this flow:

```
INPUT (JSONL)
      │
      ▼
   INHALE (RAG from DuckDB - get context)
      │
      ▼
   EXTERNAL (web_search - if NOT ME)
      │
      ▼
   BRAIN (prompt - your work)
      │
      ▼
   EXHALE (two-gate write)
      │
      ├─► [GATE 1] ─► JSONL (audit)
      │
      └─► [GATE 2] ─► DuckDB (canonical)
```

---

## WHAT (Specification)

### File Structure

**No dates in filenames. Ever.**

```
~/.primitive_engine/
│
├── staging/                    # JSONL per source
│   ├── documents.jsonl         # One file per source
│   ├── claude_code.jsonl       # Append-only
│   ├── web_search.jsonl        # Timestamps IN the data
│   └── {source_name}.jsonl     # Not in filename
│
└── knowledge.duckdb            # ONE canonical store
```

### The Registered Sources

| source_name | What it is |
|-------------|------------|
| `documents` | Markdown, text files |
| `claude_code` | Claude Code sessions |
| `claude_desktop` | Claude Desktop chats |
| `text_messages` | iMessage exports |
| `email` | Email exports |
| `web_search` | External lookup results |
| `gemini` | Gemini sessions |

**To add a new source:** Register in `governance.primitives`, use in exhale().

### The Atom Schema

```python
{
    "atom_id": "atom:{source_name}:{hash}",
    "content": str,              # Original truth
    "content_normalized": str,   # Lowercased, cleaned
    "content_hash": str,         # SHA256 for dedupe
    "embedding": list[float],    # For similarity
    "source_name": str,          # Registered source (required)
    "source_id": str | None,     # Optional identifier
    "created_at": str,           # ISO timestamp (IN the data)
    "run_id": str,               # Processing run ID
    "synced_to_cloud": bool,     # Has it been pushed?
}
```

### The Sync Layer

Local is source of truth. Cloud is mirror.

```
DuckDB (local) ──► sync_to_bigquery.py ──► BigQuery (cloud)
                        │
                        └── On command, not automatic
```

**Agents NEVER write directly to cloud.**

---

## HOW (Reference)

### Creating a Script

```
1. COPY THE_PRIMITIVE.py → my_script.py
2. FILL IN metadata
3. FILL IN RULES_APPLIED
4. WRITE main() using built-in functions
5. CALL exhale() (mandatory)
6. RUN THE_VALIDATOR.py
7. DONE when validator passes
```

### The Built-in Functions

| Function | Type | What it does |
|----------|------|--------------|
| `inhale(query)` | RAG | Query DuckDB by similarity |
| `web_search(query)` | External | Fetch from web |
| `prompt(content, task)` | Brain | LLM call |
| `extract_knowledge_atoms(content)` | Membrane | THE prompt |
| `dedupe(content, store)` | Rule | Hash check |
| `similar(content, store)` | Rule | Cosine check |
| `exhale(content, source_name)` | Write | Two-gate to JSONL + DuckDB |

### Framework Integration

```
THE_PURPOSE (SMILES)
       │
       ▼
THE_BOUNDARIES (focus)
       │
       ▼
THE_PATTERN (this - JSONL → AGENT → JSONL → DuckDB)
       │
       ▼
THE_PRIMITIVE (template)
       │
       ▼
THE_PROMPTS (categories)
       │
       ▼
.claude/rules/ (enforcement)
```

---

### The One Rule

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  JSONL → AGENT → JSONL → DuckDB                                 │
│                                                                 │
│  Every script. Every system. Every time.                        │
│                                                                 │
│  Two gates (dedupe + similar) protect the audit and canonical.  │
│                                                                 │
│  If it doesn't follow this pattern, it's wrong.                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

*One pattern. Two gates. No dates in filenames. All scripts from THE_PRIMITIVE. The architecture remembers so we don't have to.*

— THE_FRAMEWORK

---

**END OF DOCUMENT**
