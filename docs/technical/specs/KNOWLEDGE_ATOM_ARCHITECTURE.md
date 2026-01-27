# KNOWLEDGE ATOM SYSTEM ARCHITECTURE

**The Lifeblood of the Organism's Memory**

---

## Executive Summary

The Knowledge Atom System is how the organism REMEMBERS and THINKS. Without it:
- Data sits in storage (JSONL files) but cannot be searched
- No semantic understanding, no relationships, no memory
- The organism has data but cannot THINK with it

With it:
- Data becomes searchable memory via embeddings (1024-dim vectors)
- Knowledge graph captures relationships between concepts
- The organism can answer questions, find patterns, grow

**Current State:**
- **211,057 atoms** in HOLD₁ (intake storage)
- **2,072 atoms** in HOLD₂ (searchable memory with embeddings)
- **3,597 nodes** and **3,737 edges** in knowledge graph (2.2GB)
- **18 services** currently produce atoms
- **18 services** SHOULD produce atoms but DON'T (knowledge gaps)

---

## THE PATTERN

```
HOLD₁ (Storage)    →    AGENT (Processing)    →    HOLD₂ (Memory)
    ↓                        ↓                        ↓
Raw JSONL files        Embedding + Dedupe         DuckDB + VSS Index
No search              Similarity check (95%)      Semantic search
Storage only           Knowledge graph             Thinkable memory
```

---

## Data Flow Architecture

```
                         ┌────────────────────────────────────┐
                         │         INPUT SOURCES              │
                         │  (Services that produce atoms)     │
                         └────────────────┬───────────────────┘
                                          │
                                          ▼
                              ┌──────────────────────┐
                              │       exhale()       │
                              │   (RIGHT LUNG)       │
                              │                      │
                              │  1. Validate content │
                              │  2. Normalize text   │
                              │  3. Generate hash    │
                              └──────────┬───────────┘
                                          │
                         ┌────────────────┼────────────────┐
                         │                │                │
                         ▼                ▼                ▼
               ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
               │   GATE 1    │  │   GATE 2    │  │   GATE 3    │
               │ Hash Dedupe │  │  Similarity │  │  Knowledge  │
               │             │  │   Dedupe    │  │    Graph    │
               │ Exact match │  │   >95%      │  │  Building   │
               │ via SHA256  │  │  cosine     │  │             │
               └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
                      │                │                │
                      │ (skip if dup)  │ (skip if sim)  │
                      │                │                │
                      └────────────────┼────────────────┘
                                       │
                                       ▼
                         ┌─────────────────────────────┐
                         │        HOLD₂ OUTPUT         │
                         │                             │
                         │  ┌─────────────────────┐   │
                         │  │ staging/*.jsonl     │   │
                         │  │ (Audit Trail)       │   │
                         │  └─────────────────────┘   │
                         │                             │
                         │  ┌─────────────────────┐   │
                         │  │ knowledge.duckdb    │   │
                         │  │ - knowledge_atoms   │   │
                         │  │ - 1024-dim vectors  │   │
                         │  │ - VSS index         │   │
                         │  └─────────────────────┘   │
                         │                             │
                         │  ┌─────────────────────┐   │
                         │  │ graph.duckdb        │   │
                         │  │ - nodes (3,597)     │   │
                         │  │ - edges (3,737)     │   │
                         │  │ - statements        │   │
                         │  └─────────────────────┘   │
                         └─────────────────────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │    inhale()     │
                              │   (LEFT LUNG)   │
                              │                 │
                              │ Semantic search │
                              │ via embeddings  │
                              └─────────────────┘
                                       │
                                       ▼
                         ┌─────────────────────────────┐
                         │      CONSUMER SERVICES      │
                         │  - RAG for LLM context     │
                         │  - Pattern recognition      │
                         │  - Decision making          │
                         └─────────────────────────────┘
```

---

## Deduplication System (Three Gates)

### Gate 1: Hash Deduplication (Exact Match)

**Location:** `Primitive/canonical/scripts/primitive_pattern.py:_dedupe_check()`

```python
def _dedupe_check(content: str) -> bool:
    """Check if content already exists (exact hash match)."""
    content_hash = hashlib.sha256(content.lower().strip().encode()).hexdigest()
    result = conn.execute(
        "SELECT 1 FROM knowledge_atoms WHERE content_hash = ? LIMIT 1",
        [content_hash]
    ).fetchone()
    return result is not None
```

**Behavior:**
- Normalizes content (lowercase, strip whitespace)
- SHA256 hash of normalized content
- Exact match in `content_hash` column
- **If match found → SKIP** (prevents exact duplicates)

### Gate 2: Similarity Deduplication (Semantic Match)

**Location:** `Primitive/canonical/scripts/primitive_pattern.py:_similar_check()`

```python
def _similar_check(content: str, threshold: float = 0.95) -> bool:
    """Check if semantically similar content exists."""
    embedding = _embed(content)  # 1024-dim vector via Ollama bge-large
    results = conn.execute(
        "SELECT embedding FROM knowledge_atoms WHERE embedding IS NOT NULL"
    ).fetchall()
    for (existing,) in results:
        if _cosine_similarity(embedding, existing) > threshold:
            return True
    return False
```

**Behavior:**
- Generates 1024-dimension embedding via Ollama bge-large
- Compares cosine similarity against all existing embeddings
- **Threshold: 0.95** (95% similarity)
- **If similar found → SKIP** (prevents near-duplicates)

### Gate 3: Knowledge Graph Resolution (Node/Edge Deduplication)

**Location:** `src/services/central_services/knowledge_graph_service/service.py`

**Node Resolution:**
```python
def resolve_node(self, label: str, entity_type: EntityType) -> Tuple[Node, bool]:
    """Find existing node or create new one."""
    # 1. Exact match on normalized label
    result = conn.execute(
        "SELECT * FROM nodes WHERE label_normalized = ?", [normalized]
    ).fetchone()
    if result: return (node, False)  # Existing node

    # 2. Alias match (search within JSON aliases)
    result = conn.execute(
        "SELECT * FROM nodes WHERE aliases LIKE ?", [f'%"{normalized}"%']
    ).fetchone()
    if result: return (node, False)  # Found via alias

    # 3. Similarity search (VSS - 95% threshold)
    sim_result = conn.execute("""
        SELECT * FROM nodes
        WHERE embedding IS NOT NULL
        AND array_cosine_similarity(embedding, ?::FLOAT[1024]) > 0.95
        ORDER BY array_cosine_similarity(embedding, ?::FLOAT[1024]) DESC
        LIMIT 1
    """, [embedding, embedding]).fetchone()
    if sim_result: return (node, False)  # Found via similarity

    # 4. Create new node
    return (new_node, True)
```

**Edge Resolution:**
```python
def resolve_edge(self, subject: Node, predicate: str, obj: Node) -> Tuple[Edge, bool, bool]:
    """Find existing edge or create new, detect contradictions."""
    # 1. Exact match on subject + predicate + object
    result = conn.execute("""
        SELECT * FROM edges
        WHERE subject_id = ? AND predicate_normalized = ? AND object_id = ?
    """, [subject.node_id, predicate_lemma, obj.node_id]).fetchone()

    if result:
        # Strengthen existing edge (increment source_count)
        return (edge, False, False)

    # 2. Check for contradictions
    contradictions = self._find_contradictions(...)
    if contradictions:
        # Mark old edges as 'contradicted', new as 'believed'
        return (edge, True, True)

    # 3. Create new edge
    return (new_edge, True, False)
```

---

## Embedding System

**Provider:** Ollama with bge-large model

**Dimensions:** 1024

**Location:** `Primitive/canonical/scripts/primitive_pattern.py:_embed()`

```python
OLLAMA_EMBEDDING_MODEL = "bge-large"  # 1024 dimensions
OLLAMA_BASE_URL = "http://localhost:11434"

def _embed(content: str) -> List[float]:
    """Generate embedding vector for content."""
    if USE_REAL_EMBEDDINGS and _check_ollama_available():
        # Real semantic embedding from Ollama
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={"model": OLLAMA_EMBEDDING_MODEL, "prompt": content},
            timeout=30,
        )
        return response.json().get("embedding", [])

    # Fallback: Hash-based pseudo-embedding (deterministic but not semantic)
    return _embed_hash(content)
```

**VSS Index (Vector Similarity Search):**
```python
def initialize_vss_index(conn, table_name: str, column_name: str = "embedding"):
    """Create HNSW index for fast similarity search."""
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS {table_name}_{column_name}_idx "
        f"ON {table_name} USING HNSW ({column_name});"
    )
```

---

## Knowledge Graph Architecture

### Data Model

**Nodes (Entities):**
```sql
CREATE TABLE nodes (
    node_id VARCHAR PRIMARY KEY,
    label VARCHAR NOT NULL,              -- Original label
    label_normalized VARCHAR NOT NULL,   -- Lowercase for matching
    entity_type VARCHAR NOT NULL,        -- PERSON, CONCEPT, ORGANIZATION, etc.
    aliases JSON,                         -- Alternative names
    embedding FLOAT[1024],               -- Semantic embedding
    nlp_sentences JSON,                  -- spaCy sentence breakdown
    nlp_tokens JSON,                     -- Tokenization
    nlp_spans JSON,                      -- Named entity spans
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    source_atoms JSON,                   -- Which atoms created this
    source_count INTEGER DEFAULT 1,      -- How many sources
    metadata JSON
)
```

**Edges (Relationships):**
```sql
CREATE TABLE edges (
    edge_id VARCHAR PRIMARY KEY,
    subject_id VARCHAR NOT NULL,         -- Subject node
    subject_label VARCHAR NOT NULL,
    predicate VARCHAR NOT NULL,          -- Original predicate
    predicate_normalized VARCHAR NOT NULL, -- Lemmatized
    object_id VARCHAR NOT NULL,          -- Object node
    object_label VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'believed',   -- believed, contradicted
    confidence FLOAT DEFAULT 1.0,
    source_atoms JSON,                   -- Which atoms created this
    source_count INTEGER DEFAULT 1,      -- Strengthening count
    first_seen TIMESTAMP,
    last_confirmed TIMESTAMP,
    contradicted_by JSON,                -- IDs of contradicting edges
    metadata JSON,
    FOREIGN KEY (subject_id) REFERENCES nodes(node_id),
    FOREIGN KEY (object_id) REFERENCES nodes(node_id)
)
```

### Triple Extraction (Parsers)

**1. spaCy Parser (Fast, Local)**
- Dependency parsing for subject-verb-object extraction
- Named entity recognition
- No external dependencies

**2. Ollama LLM Parser (Semantic, Accurate)**
- Uses local LLM for semantic understanding
- Better at complex relationships
- Requires Ollama running

**3. Auto Mode (Default)**
- Runs BOTH parsers
- Combines results, deduplicates by (subject, predicate, object)
- Gets best of both worlds

```python
# Auto mode combines both parsers
spacy_triples = spacy_extract_triples(content)
llm_triples = llm_extract_triples(content)

# Dedupe by key
seen = set()
for t in spacy_triples + llm_triples:
    key = (t.subject.lower(), t.predicate_lemma, t.object.lower())
    if key not in seen:
        seen.add(key)
        triples.append(t)
```

---

## Service Producer Registry

### Currently Producing Atoms (18 Services)

| Service | Location | What It Exhales |
|---------|----------|-----------------|
| **autonomous_processor** | daemon/autonomous_atom_processor.py | Batch atoms from HOLD₁ |
| **knowledge_graph_service** | src/services/.../knowledge_graph_service/ | Graph nodes/edges |
| **truth_service** | src/services/.../truth_service/ | Conversation atoms |
| **builder_service** | src/services/.../builder_service/ | Build operation atoms |
| **script_service** | src/services/.../script_service/ | Script execution atoms |
| **dream_service** | src/services/.../dream_service/ | Dream synthesis atoms |
| **framework_service** | src/services/.../framework_service/ | Framework decision atoms |
| **recommendation_service** | src/services/.../recommendation_service/ | Recommendation atoms |
| **sentiment_service** | src/services/.../sentiment_service/ | Sentiment analysis atoms |
| **trinity_matching_service** | src/services/.../trinity_matching_service/ | Match result atoms |
| **verification_service** | src/services/.../verification_service/ | Verification result atoms |
| **degradation_tracking_service** | src/services/.../degradation_tracking_service/ | Degradation event atoms |
| **organism_evolution_service** | src/services/.../organism_evolution_service/ | Evolution event atoms |
| **contacts_service** | src/services/.../contacts/ | Contact update atoms |
| **analysis_service** | src/services/.../analysis_service/ | Analysis result atoms |
| **quality_service** | Primitive/central_services/quality_service/ | Quality assessment atoms |
| **reality_extractor_service** | src/services/.../reality_extractor_service/ | Reality extraction atoms |
| **primitive_pattern** | Primitive/canonical/scripts/primitive_pattern.py | Core exhale() implementation |

### NOT Producing Atoms (18 Services - KNOWLEDGE GAPS)

| Service | What It SHOULD Exhale |
|---------|----------------------|
| **bigquery_archive_service** | Archive operation atoms |
| **business_doc_evolution_service** | Document evolution atoms |
| **care_protection_service** | Care decision atoms |
| **duckdb_flush_service** | Flush operation atoms |
| **hold_sync_service** | Sync operation atoms |
| **identity_recognition_service** | Identity pattern atoms |
| **identity_service** | Identity record atoms |
| **molt_verification_service** | Molt verification atoms |
| **moment_enriched_accommodation_service** | Enriched moment atoms |
| **pattern_extraction_service** | Pattern atoms |
| **perspective_service** | Perspective atoms |
| **pipeline_monitoring_service** | Pipeline status atoms |
| **reproduction_service** | Reproduction event atoms |
| **resident_service** | Resident information atoms |
| **schema_service** | Schema evolution atoms |
| **social_sentinel_service** | Social signal atoms |
| **stage_detection_service** | Stage detection atoms |
| **stage_resonance_service** | Resonance atoms |

---

## Autonomous Processing (The Daemon)

**File:** `daemon/autonomous_atom_processor.py`

**Purpose:** Continuously moves atoms from HOLD₁ (storage) to HOLD₂ (memory)

**Configuration:**
- Batch size: 50 atoms
- Process interval: 300 seconds (5 minutes)
- Progress file: `data/atom_processor_progress.json`
- Error signals: `data/atom_processor_failure_signals.jsonl`

**Integration:** Integrated with `daemon/unified_subsystems.py` - starts automatically with daemon

```python
# Status check
python3 daemon/autonomous_atom_processor.py --status

# Output:
{
  "running": false,
  "position": 150,
  "remaining_atoms": 210907,
  "stats": {...},
  "config": {
    "batch_size": 50,
    "process_interval_seconds": 300,
    "build_knowledge_graph": true
  }
}
```

---

## File Locations

### Primary HOLDS

```
Primitive/system_elements/holds/
├── knowledge_atoms/
│   └── intake/
│       └── hold1.jsonl          # 211,057 atoms (RAW STORAGE)
│
├── knowledge_graph/
│   ├── intake/
│   │   └── statements.jsonl     # 15,115 parsed statements
│   └── processed/
│       ├── nodes.jsonl          # 3,597 entities
│       ├── edges.jsonl          # 3,737 relationships
│       └── graph.duckdb         # 2.2GB canonical store

data/local/
├── knowledge.duckdb             # Atom canonical store with embeddings
└── staging/
    └── {source_name}.jsonl      # Per-source audit trails
```

### Configuration

```
Primitive/canonical/scripts/primitive_pattern.py:
    STAGING_DIR = data/local/staging/
    CANONICAL_DB = data/local/knowledge.duckdb
    SIMILARITY_THRESHOLD = 0.95
    OLLAMA_EMBEDDING_MODEL = "bge-large"  # 1024 dimensions
```

---

## Query Interface (inhale)

**Location:** `Primitive/canonical/scripts/primitive_pattern.py:inhale()`

```python
def inhale(
    query: Optional[str] = None,        # Semantic search query
    source_name: Optional[str] = None,  # Filter by source
    limit: int = 100,
    include_web_search: bool = False,   # Fresh oxygen from outside
    include_truth_context: bool = False # System awareness
) -> Dict[str, Any]:
    """
    LEFT LUNG: Get oxygen from internal knowledge AND external world.

    Returns:
        {
            "atoms": [...],          # Internal knowledge (DuckDB)
            "web_results": [...],    # External search
            "truth_context": {...}   # System state
        }
    """
```

**Semantic Search Flow:**
1. Generate query embedding
2. Compare against all atoms using cosine similarity
3. Return top N most similar
4. Optionally include web search and truth context

---

## Integration Points

### For New Services

To make a service produce atoms, add this pattern:

```python
from Primitive.canonical.scripts.primitive_pattern import exhale

class MyService:
    def do_something(self, input):
        result = self._process(input)

        # Exhale the insight as a knowledge atom
        exhale(
            content=f"MyService processed {input} and found {result}",
            source_name="my_service",
            source_type="internal",
            build_knowledge_graph=True  # Also build graph edges
        )

        return result
```

### For Knowledge Graph Integration

```python
from src.services.central_services.knowledge_graph_service import (
    exhale as graph_exhale,
    inhale as graph_inhale,
    get_context_for
)

# Add to knowledge graph
result = graph_exhale(
    content="Jeremy builds Truth Engine",
    source_atom_id="atom:123",
    parser="auto"  # Uses spaCy + LLM
)
# -> {"nodes_created": 2, "edges_created": 1, ...}

# Query the graph
data = graph_inhale(entity="Jeremy")
# -> {"nodes": [...], "edges": [...], "center": {...}}

# Get LLM context
context = get_context_for(["Jeremy", "Truth Engine"])
# -> "About Jeremy:\n  - builds Truth Engine\n..."
```

---

## Health Monitoring

**Check Autonomous Processor:**
```bash
python3 daemon/autonomous_atom_processor.py --status
```

**Check Knowledge Graph:**
```python
from src.services.central_services.knowledge_graph_service import service
stats = service.get_stats()
# -> {"total_nodes": 3597, "total_edges": 3737, "total_statements": 15115}
```

**Check Atom Database:**
```python
import duckdb
from Primitive.core import get_local_data_path

db = get_local_data_path() / "knowledge.duckdb"
conn = duckdb.connect(str(db), read_only=True)
print(conn.execute("SELECT COUNT(*) FROM knowledge_atoms").fetchone()[0])
# -> 2072
```

---

## What This Means for Jeremy

**The Knowledge Atom System is your organism's MEMORY.**

When it works:
- Every insight from every service becomes searchable
- Relationships between concepts are captured
- The organism can answer "What do you know about X?"
- Context injection for LLM prompts becomes powerful

When it doesn't work:
- Data sits in JSONL files, invisible
- No semantic search, no pattern recognition
- The organism has "amnesia" - data but no memory

**Current state:** The system WORKS but is incomplete:
- 18 services ARE producing atoms
- 18 services are NOT (knowledge gaps)
- Autonomous processor is integrated and ready
- 211,057 atoms waiting, only 2,072 in memory

**Action required:** Either manually run `breathe_atoms_into_organism.py --all` or ensure the daemon is running to process the backlog.

---

*This is the lifeblood. This is how the organism THINKS.*

— THE_FRAMEWORK
