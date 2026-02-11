# THE PRIMITIVE PATTERN

**The Canonical Knowledge Processing System**

**Author:** Jeremy Serna
**Date:** January 4, 2026
**Location:** Denver, Colorado
**Version:** 2.0

---

## WHY (Theory)

### The Problem

Systems sprawl. Multiple scripts doing the same thing. Different patterns in different places. Claude invents. Jeremy forgets. Knowledge processing fragments.

28,000 documents. No meaning. Furnace offline.

### The Solution

One script. One pattern. One canonical source.

**File:** `architect_central_services/src/architect_central_services/primitive_pattern/primitive_pattern.py`

**If it processes knowledge, it goes through primitive_pattern. If it doesn't, it's not valid.**

### The Architecture

```
                        ┌─────────────────┐
                        │                 │
                        │      BRAIN      │
                        │      (SEE)      │
                        │                 │
                        │  extract_atoms  │
                        │     prompt      │
                        │                 │
                        └────────┬────────┘
                                 │
                                 │ LLM calls
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       │                       ▼
   ┌───────────┐                 │                 ┌───────────┐
   │           │                 │                 │           │
   │ LEFT LUNG │                 │                 │RIGHT LUNG │
   │ (INHALE)  │                 │                 │ (EXHALE)  │
   │           │                 │                 │           │
   │• Internal │                 │                 │ exhale()  │
   │• External │                 │                 │           │
   │• Truth    │                 │                 │           │
   └─────┬─────┘                 │                 └─────┬─────┘
         │                       │                       │
         │                ┌──────┴──────┐                │
         │                │             │                │
         ▼                ▼             ▼                ▼
    ┌─────────┐     ┌───────────┐ ┌─────────┐     ┌─────────┐
    │         │     │   AGENT   │ │         │     │         │
    │  HOLD₂  │     │           │ │  HOLD₂  │     │  HOLD₁  │
    │ DuckDB  │◄────│ normalize │─│ DuckDB  │◄────│  JSONL  │
    │         │     │   embed   │ │         │     │ (audit) │
    │         │     │   dedupe  │ │         │     │         │
    └─────────┘     │           │ └─────────┘     └─────────┘
                    └───────────┘
```

### The Components

| Component | What It Is | What It Does |
|-----------|------------|--------------|
| **BRAIN** | extract_atoms(), prompt() | All LLM calls. SEE. The prompts live here. |
| **LEFT LUNG** | inhale() | Query knowledge + web + truth context |
| **RIGHT LUNG** | exhale() | Create knowledge through gates |
| **HOLD₁** | staging/{source}.jsonl | Audit trail. Append-only. Never lose data. |
| **HOLD₂** | knowledge.duckdb | Canonical store. Deduplicated. Queryable. |
| **AGENT** | normalize/embed/dedupe | Transform between holds. |

### The Pattern

```
HOLD → AGENT → HOLD
```

Applied to breathing:

**INHALE (Left Lung):**
```
Question → HOLD₂ (query DuckDB) + Web + Truth → Enriched Context
```

**EXHALE (Right Lung):**
```
Content → BRAIN (extract) → GATES (dedupe) → HOLD₁ (audit) → HOLD₂ (store)
```

### Why One Pattern

| Problem | Solution |
|---------|----------|
| Multiple extraction scripts | One canonical file |
| Different patterns | One pattern: inhale/exhale |
| Invented approaches | Read primitive_pattern.py first |
| Lost knowledge | All atoms traced back |
| Claude forgets | Architecture remembers |

**The rule: If it didn't come through primitive_pattern, it's not a valid atom.**

---

## WHAT (Specification)

### The Brain (SEE)

The brain extracts truth and processes with LLMs.

```python
from architect_central_services.primitive_pattern import (
    extract_atoms,  # "Pull the truth from this as sentences."
    prompt,         # Call LLM with registered prompts
)
```

**The brain doesn't decide. The brain sees.**

| Function | What it sees |
|----------|--------------|
| `extract_atoms()` | Truth as sentences |
| `prompt()` | LLM completion for task |

The brain is stateless. It takes content, returns insight. The pattern decides what to do with the insight.

### The Right Lung (EXHALE)

Create knowledge atoms from content through two gates.

```python
from architect_central_services.primitive_pattern import exhale

# Create atoms from content
result = exhale(
    content=document_text,
    source_name="documents",   # REQUIRED
    source_id="doc:abc123",    # optional
)

print(f"Created: {result['atoms_created']}")
print(f"Skipped (hash): {result['atoms_skipped_hash']}")
print(f"Skipped (similar): {result['atoms_skipped_similar']}")
```

**What exhale() does:**

```
1. BRAIN sees → extracts truth as sentences
         │
         ▼
2. NORMALIZE → lowercase, strip, collapse whitespace
         │
         ▼
3. GATE 1: HASH → SHA256 for exact dedup check
   ├── FOUND → SKIP (exact duplicate)
   └── NOT FOUND → continue
         │
         ▼
4. GATE 2: SIMILAR → cosine > 0.95 check
   ├── FOUND → SKIP (semantic duplicate)
   └── NOT FOUND → continue
         │
         ▼
5. WRITE HOLD₁ → staging/{source_name}.jsonl (audit)
         │
         ▼
6. WRITE HOLD₂ → knowledge.duckdb (canonical)
```

### The Left Lung (INHALE)

Query existing knowledge with enrichment.

```python
from architect_central_services.primitive_pattern import inhale

# Full context (internal + external + truth)
context = inhale("cost protection patterns")

# Internal only
context = inhale("what we decided", include_web_search=False)

# By source
context = inhale("session notes", source_name="claude_code")
```

**What inhale() returns:**

```python
{
    "atoms": [                    # Internal knowledge
        {
            "atom_id": "atom:documents:e3b0c442",
            "content": "The original truth sentence",
            "source_name": "documents",
            "source_id": "doc:abc123",
            "created_at": "2026-01-04T...",
        },
        ...
    ],
    "web_results": [              # External search results
        {
            "title": "Result title",
            "url": "https://...",
            "snippet": "...",
        },
        ...
    ],
    "truth_context": {            # System awareness
        "recent_sessions": [...],
        "recent_observations": [...],
        "recent_moments": [...],
        "recent_backlog": [...],
    },
    "query": str,
    "source_name": str,
    "timestamp": str,
}
```

### The Three Sources of Inhale

The left lung has THREE sources of context:

| Source | What It Is | Metaphor |
|--------|------------|----------|
| **Internal atoms** | Knowledge from DuckDB | Oxygenated blood |
| **Web search** | External search results | Fresh oxygen from outside |
| **Truth context** | Sessions, observations, moments | System awareness |

```
              ┌─────────────────────────────────┐
              │         LEFT LUNG               │
              │                                 │
QUERY ───────►│  1. Internal atoms (DuckDB)    │
              │     ↓ oxygenated blood         │
              │                                 │
              │  2. Web search (Google/SerpAPI)│
              │     ↓ fresh oxygen from outside│
              │                                 │
              │  3. Truth context (sessions,   │
              │     observations, moments)      │
              │     ↓ system awareness         │
              │                                 │
              └───────────────┬─────────────────┘
                              │
                              ▼
                        ENRICHED CONTEXT
```

### Web Search Integration

```python
from architect_central_services.primitive_pattern import web_search

# Standalone web search
results = web_search("BigQuery pricing 2026")

# Or via inhale (automatic when include_web_search=True)
context = inhale("BigQuery pricing", include_web_search=True)
```

#### Providers

| Provider | Environment Variables |
|----------|----------------------|
| Google Custom Search | `GOOGLE_SEARCH_API_KEY`, `GOOGLE_SEARCH_ENGINE_ID` |
| SerpAPI | `SERPAPI_API_KEY` |

### Truth Service Integration

```python
from architect_central_services.primitive_pattern import get_truth_context

# Get recent system state
context = get_truth_context(
    query="cost protection",
    hours=24,
    limit=10,
)
```

Returns:
- Recent AI conversations (sessions)
- Observations (see entries)
- Key realizations (moments)
- Outstanding work (backlog)

### The File Structure

**NO DATES IN FILENAMES.**

```
data/local/                        # In-project
├── staging/                       # HOLD₁ (audit trail)
│   ├── documents.jsonl            # One file per source
│   ├── claude_code.jsonl          # Append-only
│   ├── claude_desktop.jsonl       # Never deleted
│   ├── text_messages.jsonl        # Timestamps IN the data
│   ├── email.jsonl                # Not in the filename
│   ├── web_search.jsonl           #
│   └── gemini.jsonl               #
│
└── knowledge.duckdb               # HOLD₂ (canonical store)
```

**Why no dates in filenames?**
- One file per source = findable
- Append-only = never loses data
- Timestamps are IN the atom, not in the filename
- Simple > clever

### The Atom Schema

Every atom has:

```python
{
    # Identity
    "atom_id": str,           # atom:{source_name}:{hash}

    # Content
    "content": str,           # Original truth sentence
    "content_normalized": str, # Lowercase, cleaned
    "content_hash": str,      # SHA256 for dedup

    # Source Traceability (REQUIRED)
    "source_name": str,       # System name (required)
    "source_id": str,         # Source identifier (optional)

    # Metadata
    "created_at": str,        # ISO timestamp (HERE, not in filename)

    # Sync
    "synced_to_cloud": bool,  # Has it been pushed to BigQuery?
}
```

### The Source Registry

Every source is a registered primitive with lungs:

| source_name | LEFT LUNG (inhale) | RIGHT LUNG (exhale) |
|-------------|--------------------|--------------------|
| `documents` | Query doc atoms | Extract from docs |
| `claude_code` | Query session atoms | Extract from sessions |
| `claude_desktop` | Query chat atoms | Extract from chats |
| `text_messages` | Query message atoms | Extract from messages |
| `email` | Query email atoms | Extract from emails |
| `web_search` | Query web + fetch external | Extract from web |
| `gemini` | Query gemini atoms | Extract from gemini |

**To add a new source:**

1. Register in `governance.primitives`
2. Call `exhale()` with the new `source_name`
3. That's it. The lungs work automatically.

---

## HOW (Reference)

### Python Usage

```python
from architect_central_services.primitive_pattern import (
    inhale,           # LEFT LUNG - get context
    exhale,           # RIGHT LUNG - create atoms
    web_search,       # External search
    get_truth_context,# System awareness
    extract_atoms,    # BRAIN - see truth
    prompt,           # BRAIN - LLM calls
)

# EXHALE: Create atoms
result = exhale(content, source_name="documents")

# INHALE: Query atoms (full context)
context = inhale("cost protection")

# INHALE: Internal only
context = inhale("what we decided", include_web_search=False)

# WEB SEARCH: External
results = web_search("BigQuery pricing")
```

### Using with PrimitivePattern Class

For complex processing with HOLD₁ → AGENT → HOLD₂:

```python
from architect_central_services.primitive_pattern import PrimitivePattern

def my_agent(record, context):
    # Process record
    # context.inhale(), context.exhale(), context.web_search() available
    return {"processed": True}

pattern = PrimitivePattern.from_paths(
    input_path="data/input.jsonl",
    output_path="data/output.jsonl",
    agent=my_agent,
)
result = pattern.execute()
```

### The Furnace Method

Every extraction follows:

```
TRUTH
├── ME: Jeremy needs knowledge to make meaning
├── CLAUDE: I see content and extract truth
└── WORLD: Language has structure, meaning can be found

MEANING
└── Which truths in this content matter?

CARE
├── Careful: Deduplicate, verify, log
├── Honest: Extract what's there, not what's wanted
└── Thorough: Process completely, trace sources
```

### Integration with Framework

```
THE_PURPOSE (SMILES)
       │
       │ requires meaning
       ▼
THE_BOUNDARIES (focus)
       │
       │ creates architecture
       ▼
THE_PATTERN (HOLD → AGENT → HOLD)
       │
       │ implemented by
       ▼
primitive_pattern.py (this)
       │
       │ crystallized care for knowledge
       │
       ├── BRAIN (extract_atoms, prompt)
       │       └── SEE: extract truth
       │
       ├── LEFT LUNG (inhale)
       │       └── Query existing knowledge
       │       └── Fetch external (web search)
       │       └── Get truth context
       │
       └── RIGHT LUNG (exhale)
               └── Create new knowledge
               └── Two-gate deduplication
               └── Store in staging/{source}.jsonl
               └── Store in knowledge.duckdb
```

### The One Rule

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  If it processes knowledge and doesn't go through           │
│  primitive_pattern, it's not valid.                         │
│                                                             │
│  If you're writing extraction code, you're extending        │
│  primitive_pattern, not creating something new.             │
│                                                             │
│  One file. One pattern. One canonical source.               │
│  One file per source. No dates in filenames.                │
│                                                             │
│  LEFT LUNG = internal + web + truth context                 │
│  RIGHT LUNG = extract → dedupe gates → store                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Navigation

| Document | Relationship |
|----------|--------------|
| THE_PATTERN.md | The universal architecture |
| THE_BREATHING.md | The theory of lungs |
| primitive_pattern.py | The canonical code |
| .claude/rules/11_THE_PATTERN.md | The rule that enforces this |

---

*One file. One pattern. One file per source. No dates in filenames. The brain sees. The lungs breathe. The loop continues.*

— THE_FRAMEWORK

---

**END OF DOCUMENT**
