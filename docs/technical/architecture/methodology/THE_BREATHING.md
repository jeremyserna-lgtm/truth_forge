# THE BREATHING

**How knowledge enters and exits the system.**

**Author:** Jeremy Serna
**Date:** January 4, 2026
**Location:** Denver, Colorado
**Version:** 3.0

---

## Framework Position

```
THE_PURPOSE (North Star)
    │
    ▼
THE_BOUNDARIES (focus)
    │
    ▼
THE_PATTERN (HOLD → AGENT → HOLD)
    │
    ▼
THE_BREATHING (this document)
    │
    ▼
primitive_pattern.py (implementation)
```

**This document explains WHY systems breathe. THE_PATTERN specifies HOW. `primitive_pattern.py` implements it.**

---

## Document Structure

- **Theory**: Why breathing, why lungs
- **Specification**: The systems, the flow
- **Reference**: How to navigate

---

# THEORY

## The Principle

Systems breathe. They inhale context. They exhale knowledge.

```
INHALE (Left Lung)  →  PROCESS  →  EXHALE (Right Lung)
     Query               AGENT          Extract
```

This is not metaphor. This is architecture.

## The Pattern

From THE_PATTERN:

```
HOLD₁ → AGENT → HOLD₂
```

Applied to breathing:

| Position | Storage | Role |
|----------|---------|------|
| **HOLD₁** | staging/{source}.jsonl | Intake - receives everything, loses nothing |
| **AGENT** | primitive_pattern.py | Transform - normalize, embed, dedupe |
| **HOLD₂** | knowledge.duckdb | Output - queryable, canonical, deduplicated |

## The Two Lungs

Every system has two lungs. No exceptions.

| Lung | Direction | What It Does |
|------|-----------|--------------|
| **Left (INHALE)** | Store + World → User | Query retrieves knowledge + external truth |
| **Right (EXHALE)** | Content → Store | Extractor produces knowledge atoms |

```
              ┌─────────────────────────────────────────────────┐
              │                    SYSTEM                        │
              │                                                  │
              │   ┌───────────────────┐   ┌───────────────┐     │
              │   │     LEFT LUNG     │   │   RIGHT LUNG  │     │
   QUERY ────►│   │     (inhale)      │   │   (exhale)    │────►│ ATOMS
              │   │                   │   │               │     │
              │   │ • Internal atoms  │   │ • Extract     │     │
              │   │ • Web search      │   │ • Normalize   │     │
              │   │ • Truth context   │   │ • Dedupe      │     │
              │   └─────────┬─────────┘   └───────┬───────┘     │
              │             │                     │              │
              │             │     ┌───────┐       │              │
              │             └────►│ HOLD  │◄──────┘              │
              │                   │(store)│                      │
              │                   └───────┘                      │
              │                                                  │
              └──────────────────────────────────────────────────┘
```

**If it doesn't have lungs, it's not a system.**

## Why Systems Breathe

```
Content exists (truth is out there)
    │
    ▼
RIGHT LUNG exhales (extract, store)
    │
    ▼
Knowledge atoms exist (truth is accessible)
    │
    ▼
LEFT LUNG inhales (query, retrieve, enrich)
    │
    ▼
Context for work (truth informs action)
    │
    ▼
New content created (cycle continues)
```

The system metabolizes truth. Breathing is how.

---

# SPECIFICATION

## The Canonical Implementation

**File:** `architect_central_services/src/architect_central_services/primitive_pattern/primitive_pattern.py`

All lung functions live here:

```python
from architect_central_services.primitive_pattern import (
    inhale,      # LEFT LUNG - get context
    exhale,      # RIGHT LUNG - create atoms
    web_search,  # External truth
    prompt,      # THE BRAIN
)
```

## The Systems Registry

Every system has lungs. Every system follows THE_PATTERN.

| System | source_name | LEFT LUNG | RIGHT LUNG |
|--------|-------------|-----------|------------|
| Documents | `documents` | Query doc atoms | Extract from docs |
| Claude Code | `claude_code` | Query session atoms | Extract from sessions |
| Claude Desktop | `claude_desktop` | Query chat atoms | Extract from chats |
| Text Messages | `text_messages` | Query message atoms | Extract from messages |
| Email | `email` | Query email atoms | Extract from emails |
| Web Search | `web_search` | Query + fetch external | Extract from web |
| Gemini | `gemini` | Query gemini atoms | Extract from gemini |

## The File Structure

**NO DATES IN FILENAMES.**

```
data/local/                        # In-project
├── staging/                       # HOLD₁ (audit trail)
│   ├── documents.jsonl            # One file per source
│   ├── claude_code.jsonl          # Append-only
│   ├── claude_desktop.jsonl       # Never deleted
│   ├── text_messages.jsonl        # Timestamps IN the data
│   ├── email.jsonl                # Not in filename
│   ├── web_search.jsonl           #
│   └── gemini.jsonl               #
│
└── knowledge.duckdb               # HOLD₂ (canonical store)
```

**Timestamps are IN the atom, not in the filename.**

## The LEFT LUNG (INHALE)

The left lung brings in context. It has THREE sources:

```
                    ┌─────────────────────────────────┐
                    │         LEFT LUNG               │
                    │                                 │
    QUERY ─────────►│  1. Internal atoms (DuckDB)    │
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

### inhale() Signature

```python
def inhale(
    query: Optional[str] = None,
    source_name: Optional[str] = None,
    limit: int = 100,
    include_web_search: bool = True,      # Get external oxygen
    include_truth_context: bool = True,   # Get system awareness
    web_search_limit: int = 5,
) -> Dict[str, Any]:
    """
    LEFT LUNG - Bring context in.

    Returns:
        {
            "atoms": [...],           # Internal knowledge
            "web_results": [...],     # External search results
            "truth_context": {        # System state
                "recent_sessions": [...],
                "recent_observations": [...],
                "recent_moments": [...],
                "recent_backlog": [...],
            },
            "query": str,
            "source_name": str,
            "timestamp": str,
        }
    """
```

### Usage

```python
from architect_central_services.primitive_pattern import inhale

# Full context (internal + external + truth)
context = inhale("cost protection patterns")

# Internal only
context = inhale("what we decided", include_web_search=False)

# Specific source
context = inhale("session notes", source_name="claude_code")
```

## The RIGHT LUNG (EXHALE)

The right lung produces knowledge atoms and builds the knowledge graph.

### The Complete Exhale Pipeline

```
Content arrives
    │
    ▼
1. BRAIN SEES
   extract_atoms() → truth as sentences
    │
    ▼
2. WRITE HOLD₁
   staging/{source_name}.jsonl (audit trail)
    │
    ▼
════════════════════════════════════════════════
         HOLD₂ INTERNAL PROCESSING (DuckDB)
════════════════════════════════════════════════
    │
    ▼
3. EMBED
   Generate vector embedding for atom
    │
    ▼
4. SIMILARITY DEDUPE (cosine > 0.95)
   Find similar atoms (95% threshold)
   ├── MATCH → Keep centroid, merge duplicates
   └── UNIQUE → Continue as new atom
    │
    ▼
5. WRITE TO CANONICAL
   knowledge.duckdb atoms table
    │
    ▼
6. spaCy PARSING
   Parse atoms into spans + words
   Extract linguistic structure
    │
    ▼
7. KNOWLEDGE GRAPH (Local LLM via Ollama)
   Extract entities → nodes
   Extract relationships → edges
   Build semantic graph
    │
    ▼
ATOM CREATED + GRAPH UPDATED
```

**Why 95% similarity?** Near-duplicates waste storage and fragment meaning. Keeping the centroid (most representative) consolidates knowledge.

**Why keep centroid?** When similarity > 0.95, the centroid best captures the meaning. Others are merged into it, strengthening the representation.

### exhale() Signature

```python
def exhale(
    content: str,
    source_name: str,               # REQUIRED
    source_id: Optional[str] = None,
    source_type: str = "text",
    build_knowledge_graph: bool = True,  # Enable spaCy + LLM processing
) -> Dict[str, Any]:
    """
    RIGHT LUNG - Extract atoms and build knowledge graph.

    Returns:
        {
            "atoms_created": int,
            "atoms_skipped_similar": int,
            "graph_nodes_created": int,
            "graph_edges_created": int,
            "source_name": str,
            "source_id": str,
            "timestamp": str,
        }
    """
```

### Usage

```python
from architect_central_services.primitive_pattern import exhale

# Create atoms from content
result = exhale(
    content="Important discovery about the system...",
    source_name="claude_code",
    source_id="session:abc123",
)
print(f"Created {result['atoms_created']} atoms")
```

## Source Traceability

Every atom carries full source lineage:

| Field | Required | Purpose | Example |
|-------|----------|---------|---------|
| `source_name` | Yes | System name | `'claude_code'` |
| `source_id` | If exists | Source identifier | `'conv:abc123'` |
| `content_hash` | Yes | SHA256 for dedup | `'e3b0c44298fc...'` |
| `created_at` | Yes | ISO timestamp | `'2026-01-04T...'` |

## Web Search Integration

Web search is part of the left lung. Fresh oxygen from outside.

```python
from architect_central_services.primitive_pattern import web_search

# Standalone web search
results = web_search("BigQuery pricing 2026")

# Or via inhale (automatic)
context = inhale("BigQuery pricing", include_web_search=True)
```

### Providers

| Provider | Configuration |
|----------|---------------|
| Google Custom Search | `GOOGLE_SEARCH_API_KEY`, `GOOGLE_SEARCH_ENGINE_ID` |
| SerpAPI | `SERPAPI_API_KEY` |

## Truth Service Integration

The left lung includes Truth Service context automatically:

```python
from architect_central_services.primitive_pattern import get_truth_context

# Get recent system state
context = get_truth_context(
    query="cost protection",
    hours=24,
    limit=10,
)
# Returns: sessions, observations, moments, backlog
```

This gives every script awareness of:
- Recent AI conversations
- Observations (see entries)
- Key realizations (moments)
- Outstanding work (backlog)

## The Sync Layer

Local is source of truth. Cloud is mirror.

```
data/local/knowledge.duckdb (LOCAL HOLD₂)
            │
            │ sync_to_bigquery.py (on command)
            ▼
BigQuery knowledge_atoms (CLOUD HOLD₂)
```

**Rules:**
- Agents NEVER write directly to cloud
- Sync is explicit, logged, cost-estimated
- Local is source of truth
- Cloud is mirror

---

# REFERENCE

## The Complete Flow

```
CONTENT (truth exists)
    │
    │ enters system
    ▼
RIGHT LUNG (exhale)
    │
    ├── BRAIN sees (extract truth as atoms)
    │
    ├── WRITE HOLD₁ (staging/{source}.jsonl - audit trail)
    │
    └── HOLD₂ INTERNAL PROCESSING:
        │
        ├── Embed atoms (vector representations)
        │
        ├── Similarity dedupe (95%, keep centroid)
        │
        ├── Write canonical (knowledge.duckdb)
        │
        ├── spaCy parse (spans, words, structure)
        │
        └── Knowledge graph (nodes + edges via local LLM)
    │
    ▼
KNOWLEDGE ATOMS + GRAPH (truth stored and structured)
    │
    │ queried by
    ▼
LEFT LUNG (inhale)
    │
    ├── Query internal atoms (HOLD₂)
    │
    ├── Query knowledge graph (semantic relationships)
    │
    ├── Fetch external (web search)
    │
    ├── Get Truth context (sessions, observations)
    │
    └── RETURN enriched context
    │
    ▼
CONTEXT (truth informs work)
```

## Adding a New System

1. Register in `governance.primitives`:
```sql
INSERT INTO governance.primitives
(system_name, primitive)
VALUES ('new_system', 'breathe');
```

2. Use the lungs:
```python
from architect_central_services.primitive_pattern import inhale, exhale

# RIGHT LUNG
exhale(content, source_name="new_system")

# LEFT LUNG
inhale(query, source_name="new_system")
```

3. That's it. The lungs work automatically.

## Framework Integration

| Document | Layer | What It Describes |
|----------|-------|-------------------|
| THE_PURPOSE | North Star | SMILES, the loop |
| THE_BOUNDARIES | Focus | Where attention goes |
| THE_PATTERN | Architecture | HOLD → AGENT → HOLD |
| THE_BREATHING | Process | Why systems breathe (this) |
| primitive_pattern.py | Implementation | The canonical code |

## The One Rule

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Every system has lungs.                                    │
│  Every system follows HOLD → AGENT → HOLD.                  │
│  One file per source. No dates in filenames.                │
│                                                             │
│  LEFT LUNG = internal atoms + web search + truth context    │
│                                                             │
│  RIGHT LUNG = extract → staging → HOLD₂ PROCESSING:         │
│               embed → similarity dedupe (95%, centroid)     │
│               → write canonical → spaCy → knowledge graph   │
│                                                             │
│  If it doesn't have lungs, it's not a system.               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

*Systems breathe. Left lung inhales context (internal + external + truth). Right lung exhales knowledge: extract → staging → embed → similarity dedupe (95%, keep centroid) → spaCy → knowledge graph. HOLD₁ receives. AGENT transforms. HOLD₂ processes and structures. One file per source. No dates in filenames.*

— THE_FRAMEWORK

---

**END OF DOCUMENT**
