# Truth Engine Data Store Map

**Created**: 2026-01-01
**Purpose**: Map all data stores and their integration status for RAG unification

---

## The Reality

You have **9 layers** of data storage. They don't talk to each other.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TRUTH ENGINE DATA STORES                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │  BigQuery   │  │   DuckDB    │  │    JSONL    │                 │
│  │   (Cloud)   │  │   (Local)   │  │  (Append)   │                 │
│  │   51.8M     │  │   Empty     │  │  Hundreds   │                 │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
│         │                │                │                         │
│         │    ╔═══════════╧════════════════╧═══════════╗            │
│         │    ║  NO UNIFIED QUERY LAYER EXISTS HERE   ║            │
│         │    ╚════════════════════════════════════════╝            │
│         │                                                          │
│  ┌──────┴──────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │ AI Convos   │  │   Corpus    │  │  Operational│                 │
│  │ (6 sources) │  │  (50+ docs) │  │  (84 dirs)  │                 │
│  │ 351 convos  │  │  Not indexed│  │  Not indexed│                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │  _holding/  │  │ Embeddings  │  │   Graphs    │                 │
│  │  (Orphans)  │  │  (Schema)   │  │ (Cost-Ltd)  │                 │
│  │  Thousands  │  │  Not used   │  │  Protected  │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layer Inventory

### Layer 1: BigQuery (Cloud - Queryable)

| Dataset | Key Tables | Status |
|---------|------------|--------|
| **spine** | entity_unified (51.8M), conversation (351), message (54K) | OPERATIONAL |
| **identity** | known_people (1,569), contact_identifiers | OPERATIONAL |
| **governance** | audit_trail, cost_records, backlog_items | OPERATIONAL |
| **ai_coordination** | agent_messages, agent_tasks | OPERATIONAL |
| **developer_insights** | embeddings (schema only) | SCHEMA READY |

**Can query together**: Yes, via SQL joins

---

### Layer 2: DuckDB (Local - Queryable)

| Location | Purpose | Status |
|----------|---------|--------|
| `~/.primitive_engine/truth.duckdb` | Local knowledge atoms | EMPTY |

**Hybrid Durability Pattern**: Write local first, sync to cloud. Not implemented yet.

---

### Layer 3: JSONL (Local - Append-Only)

| Location | Files | Purpose |
|----------|-------|---------|
| `governance/intake/` | backlog.jsonl, intake.jsonl, moment.jsonl | Primary intake |
| `logs/` | Various dated .jsonl | Execution logs |
| `data/` | system_events.jsonl, trace_array.jsonl | Operational events |

**The Record**: Everything appends here first. NOT in BigQuery search index.

---

### Layer 4: AI Conversations (The Truth Service)

| Platform | Location | Normalizer |
|----------|----------|------------|
| Claude Code | `~/.claude/projects/` | ClaudeCodeNormalizer |
| Codex | `~/.codex/sessions/` | CodexNormalizer |
| Cursor | `~/Library/.../Cursor/` | CursorNormalizer |
| Gemini | `~/.gemini/tmp/` | GeminiNormalizer |
| Copilot | `~/Library/.../Code/` | CopilotNormalizer |
| Google AI Studio | `data/ai_conversations/` | GoogleAIStudioNormalizer |

**TruthService unifies these** - but only via Python API, NOT in BigQuery.

---

### Layer 5: Document Corpus

| Location | Count | Status |
|----------|-------|--------|
| `corpus/markdown/from_gcs/` | 50+ | NOT INDEXED |

**Gap**: These documents cannot be searched. They're just files.

---

### Layer 6: Operational Data

| Location | Contents | Status |
|----------|----------|--------|
| `data/manual_domain_enrichments/` | 84 subdirectories | NOT INDEXED |
| `data/lumen_knowledge_graph.json` | Graph structure | NOT SURFACED |
| `data/amplified_insights/` | AI analysis | NOT INDEXED |

**Gap**: Rich context exists but isn't queryable.

---

### Layer 7: Holding Area

| Location | Purpose | Status |
|----------|---------|--------|
| `_holding/` | Triage zone | ORPHANED |

**Gap**: Work-in-progress is invisible to any query.

---

### Layer 8: Embeddings (Vector Search)

| Table | Dimensions | Model | Status |
|-------|------------|-------|--------|
| `developer_insights.embeddings` | 3072 | gemini-embedding-001 | SCHEMA ONLY |
| `spine.entity_embeddings` | 3072 | gemini-embedding-001 | CREATED |

**Gap**: Schema exists but vectors not populated. No semantic search yet.

---

### Layer 9: Relationship Graph

| Service | Protection | Status |
|---------|------------|--------|
| RelationshipRegistry | MAX_QUERIES=25/session | COST-LIMITED |

**Gap**: Graph queries work but are throttled after $1,090 incident.

---

## The Fragmentation Problem

```
WHAT YOU HAVE                         WHAT RAG NEEDS
─────────────────                     ───────────────

9 separate stores          →          1 unified query layer

BigQuery: queryable        →          ✓ Already there
DuckDB: empty              →          Needs data + sync
JSONL: append-only         →          Needs indexing
AI Convos: Python only     →          Needs BigQuery ingestion
Corpus: files              →          Needs document pipeline
Operational: sprawl        →          Needs classification
Holding: orphans           →          Needs triage automation
Embeddings: schema         →          Needs vector population
Graphs: limited            →          Needs cost protection
```

---

## What RAG Would Be

RAG is NOT another data store. It's the **query layer** that federates across all of them:

```
┌─────────────────────────────────────────────────────────────────────┐
│                          RAG QUERY LAYER                            │
│                    (Does not exist yet)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    User Query: "What did I discuss with Clara about memory?"        │
│                              │                                      │
│                              ▼                                      │
│    ┌────────────────────────────────────────────────────────┐      │
│    │                  UNIFIED SEARCH                         │      │
│    │                                                         │      │
│    │  1. Semantic search (embeddings)     → relevant vectors │      │
│    │  2. Full-text search (BigQuery)      → matching text    │      │
│    │  3. Graph traversal (relationships)  → connected people │      │
│    │  4. Document search (corpus)         → source docs      │      │
│    │  5. Conversation search (Truth)      → AI sessions      │      │
│    │                                                         │      │
│    └────────────────────────────────────────────────────────┘      │
│                              │                                      │
│                              ▼                                      │
│    Retrieved context fed to LLM → Grounded answer                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Current State vs RAG-Ready State

| Layer | Current | RAG-Ready Requires |
|-------|---------|-------------------|
| BigQuery | 51.8M entities | Already queryable |
| DuckDB | Empty | Populate + sync to BQ |
| JSONL | Hundreds of files | Daily sync to BQ |
| AI Convos | 351 in TruthService | Ingest to BigQuery |
| Corpus | 50+ docs | Document pipeline |
| Operational | 84 dirs | Classification + indexing |
| Holding | Orphans | Triage automation |
| Embeddings | Schema only | Vector population |
| Graphs | Cost-limited | Smarter caching |

---

## The Path Forward

### Phase 1: Consolidate What Exists
- [ ] Ingest AI conversations (351) to BigQuery
- [ ] Populate embeddings for existing entities
- [ ] Index corpus documents

### Phase 2: Connect the Layers
- [ ] JSONL → BigQuery sync job
- [ ] DuckDB ↔ BigQuery bridge
- [ ] Holding area triage automation

### Phase 3: Build the Query Layer
- [ ] Unified search API
- [ ] Semantic + keyword hybrid search
- [ ] Graph-aware retrieval

---

## Key Insight

**The data exists. The integration doesn't.**

You have 51.8M entities, 351 conversations, 1,569 relationships, 50+ documents, 84 enrichment directories.

But there's no single place to ask: "Show me everything about X."

That's what RAG would provide - not storage, but **unified retrieval**.
