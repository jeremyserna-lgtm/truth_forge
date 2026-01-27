# Central Services Architecture

**Created**: 2026-01-06
**Status**: P.0 Pre-Assessment (Discovery)
**Purpose**: Document what exists before migration

---

## Overview

All services follow **THE PATTERN**:
```
HOLD₁ (Input) → AGENT (Processing) → HOLD₂ (Output)
```

Location: `src/services/central_services/`

---

## The 13 Services

### 1. TruthExtractor (`truth_service/service.py`)

**What it does**: Extracts knowledge atoms from conversation entries using Ollama.

**Pattern**:
- HOLD₁: `TruthService.iter_entries()` (raw conversation turns)
- AGENT: Ollama (llama3.2) - extracts knowledge atoms as sentences
- HOLD₂: `Primitive/staging/truth_atoms.jsonl` → `truth_atoms.duckdb`

**Interface**:
```python
extractor = TruthExtractor()
result = extractor.exhale(content="Jeremy is Stage 5.", source_name="claude_code")
atoms = extractor.inhale(query="Stage 5", limit=10)
```

**Integrations**:
- Calls `knowledge_graph_service.exhale()` for each atom (builds graph)
- Uses `model_gateway_service` for Ollama calls
- Reads prompts from `prompt_registry`

**Output**: Knowledge atoms with content_hash for deduplication

---

### 2. KnowledgeService (`knowledge_service/knowledge_service.py`)

**What it does**: Pattern-first knowledge atom intake using PrimitivePattern.

**Pattern**:
- HOLD₁: `system_elements/holds/knowledge_atoms/intake/hold1.jsonl`
- AGENT: `_atom_agent()` - generates atom_id, timestamps
- HOLD₂: `system_elements/holds/knowledge_atoms/processed/hold2.jsonl` + `.duckdb`

**Interface**:
```python
ks = get_knowledge_service()
result = ks.exhale(content="text", source_name="extractor")
atoms = ks.inhale(query="search term", limit=100)
```

**Integrations**:
- Pushes atoms to `knowledge_graph_service` (the bridge)
- Uses `PrimitivePattern` from `architect_central_services`

---

### 3. ModelGatewayService (`model_gateway_service/model_gateway_service.py`)

**What it does**: Canonical LLM gateway. Routes requests to FREE providers.

**Pattern**:
- HOLD₁: `system_elements/holds/model_gateway/intake/hold1.jsonl` (requests)
- AGENT: Calls provider (Ollama → Gemini CLI → Claude Code CLI)
- HOLD₂: `system_elements/holds/model_gateway/processed/hold2.jsonl` (responses)

**Providers** (all FREE):
| Provider | Type | Notes |
|----------|------|-------|
| `OLLAMA` | Local | Default, primitive:latest model |
| `GEMINI_CLI` | CLI | Google subscription |
| `CLAUDE_CODE` | CLI | Anthropic subscription |

**Interface**:
```python
gateway = get_model_gateway_service()
result = gateway.exhale(prompt="...", provider=ModelProvider.OLLAMA)
text = gateway.ask(prompt)  # Simple text response
data = gateway.ask_json(prompt)  # Parsed JSON
```

**Integrations**:
- `prompt_registry` for template management
- `convenience.py` has 26+ wrapper functions

---

### 4. KnowledgeGraphService (`knowledge_graph_service/service.py`)

**What it does**: Graph-based knowledge storage. The graph IS the memory.

**Pattern**:
- HOLD₁: `system_elements/holds/knowledge_graph/intake/statements.jsonl` (raw statements)
- AGENT: Parser (spaCy + LLM) - extracts subject/predicate/object triples
- HOLD₂: `system_elements/holds/knowledge_graph/graph.duckdb` (nodes + edges tables)

**Key Insight**: Three atoms saying the same thing collapse to one edge with `source_count=3`.

**Interface**:
```python
service = get_knowledge_graph_service()
result = service.exhale(content="Jeremy builds Truth Engine.", source_atom_id="atom:123")
graph = service.inhale(entity="Jeremy", limit=50)
context = service.get_context_for(["Jeremy", "Truth Engine"])  # For LLM prompts
```

**Tables**:
- `nodes`: entity_id, label, entity_type (PERSON, PRODUCT, CONCEPT...)
- `edges`: subject_id, predicate, object_id, status (believed/contradicted)
- `statements`: raw triples with source tracking

**Integrations**:
- Uses `spacy_extract_triples` (fast, local)
- Uses `llm_extract_triples` via Ollama (better semantic understanding)

---

### 5. ExtractorService (`extractor_service/service.py`)

**What it does**: Universal extractor. "Breathe Anything into Anything."

**Pattern**:
- HOLD₁: Raw source files (JSON, MD, TXT, code)
- AGENT: `universal_extraction_agent()` - dispatches by file type
- HOLD₂: Calls `KnowledgeService.exhale()` for each extracted atom

**Supported Types**:
| Type | Handling |
|------|----------|
| `.json` | ChatGPT exports, Gemini exports |
| `.md`, `.txt` | Documents, may contain embedded files |
| `.py`, `.js`, `.ts` | Code files |
| `.pdf` | Placeholder (not implemented) |

**Special Feature**: Hunts for embedded documents using `--- START OF FILE ... ---` pattern.

**Interface**:
```python
service = ExtractorService()
result = service.ingest("/path/to/source")
```

---

### 6. ContactsService (`contacts/service.py`)

**What it does**: BigQuery ↔ Local DuckDB sync for contacts.

**Pattern**:
- HOLD₁: `identity.contacts_master` (BigQuery)
- AGENT: Sync logic
- HOLD₂: `system_elements/holds/contacts/processed/hold2.duckdb`

**Interface**:
```python
sync_from_bigquery()  # Pull BQ → local
sync_to_bigquery()  # Push dirty records → BQ
contacts = inhale(query="adam", limit=20)
update_contact(contact_id, nickname="Whiskey")
```

**Fields**: contact_id, display_name, primitive, nickname, nickname_meaning, category_code

---

### 7. AnalysisService (`analysis_service/service.py`)

**What it does**: Synthesizes system state into actionable insights.

**Pattern**:
- HOLD₁: Reads from other service HOLDs (costs, knowledge_atoms)
- AGENT: LLM analysis via ModelGatewayService
- HOLD₂: `system_elements/holds/analysis/processed/hold2.duckdb`

**Interface**:
```python
service = get_analysis_service()
analysis_id = service.run_analysis(category="system_health")
```

**Uses**: `call_prompt("analysis_system_health")` from prompt registry

---

### 8. DocumentService (`document_service/document_service.py`)

**What it does**: Document intake using PrimitivePattern.

**Pattern**:
- HOLD₁: `system_elements/holds/documents/intake/hold1.jsonl`
- AGENT: Generates document_id, content_hash
- HOLD₂: `system_elements/holds/documents/processed/hold2.jsonl` + `.duckdb`

**Interface**:
```python
service = get_document_service()
result = service.exhale("/path/to/document.md")
docs = service.inhale(query="search", limit=100)
```

---

### 9. ScriptService (`script_service/service.py`)

**What it does**: Script storage with frontmatter stamping.

**Pattern**:
- HOLD₁: `system_elements/holds/scripts/intake/hold1.jsonl`
- AGENT: Adds frontmatter (id, issued, qa.status)
- HOLD₂: `system_elements/holds/scripts/processed/hold2.jsonl` + `.duckdb`

**Special Feature**: `stamp()` method adds frontmatter and optionally moves to `docs/Unclassified/`.

**Interface**:
```python
result = stamp_script("/path/to/script.py", force=True)
print(result.script_id)  # script:abc12345
```

---

### 10. FrontmatterService (`frontmatter_service/service.py`)

**What it does**: Document stamping with Ollama enrichment.

**Pattern**:
- HOLD₁: Raw files (MD, PY)
- AGENT: Ollama analysis → category, keywords, summary
- HOLD₂: File with frontmatter (moved to appropriate location)

**Enrichment Flow**:
1. Try Ollama (FREE, local) first
2. Fallback to Claude Code CLI
3. Default values if both fail

**Categories**: protocol, pattern, specification, script, service, identity, cognition, furnace, philosophy, friendship, observation, history, voice, documentation, migration, report, uncategorized

**Interface**:
```python
result = stamp_document("/path/to/doc.md", organize=True)
```

---

### 11. RecommendationService (`recommendation_service/service.py`)

**What it does**: Generates tailored recommendations based on metabolic state.

**Pattern**:
- HOLD₁: User state (Kegan stage, tier, primitives)
- AGENT: ModelGatewayService (LLM call)
- HOLD₂: `system_elements/holds/recommendations/processed/hold2.duckdb`

**Input Factors**:
- Kegan Stage (1-5)
- User Tier (FRIEND, etc.)
- Emotional Primitives (needs tracked)
- Conversation History

**Interface**:
```python
recs = exhale(stage=5, tier="FRIEND", history="...", primitives=["money", "connection"])
existing = inhale(stage=5, category="ECONOMIC")
```

---

### 12. SchemaService (`schema_service/service.py`)

**What it does**: Centralized schema management for all services.

**Pattern**:
- HOLD₁: Schema definitions (JSON)
- AGENT: Registry + SQL generator
- HOLD₂: `system_elements/schema_registry/*.json`

**Registered Schemas**:
| Schema | Table | Purpose |
|--------|-------|---------|
| contacts | contacts | Contact records |
| recommendations | recommendations | Metabolic recommendations |
| knowledge_atoms | hold2_data | Processed atoms |
| documents | hold2_data | Processed documents |
| scripts | hold2_data | Script registry |
| model_requests | model_requests | LLM request log |
| model_responses | model_responses | LLM response log |
| backlog | backlog | Tasks and wants |
| costs | costs | Cost tracking |
| analysis_results | analysis_results | System metrics |

**Interface**:
```python
service = get_schema_service()
sql = service.generate_sql("contacts")  # CREATE TABLE ...
schema = service.get_schema("knowledge_atoms")
```

---

### 13. SentimentService (`sentiment_service/service.py`)

**What it does**: Enriches knowledge atoms with GoEmotions-compatible sentiment.

**Pattern**:
- HOLD₁: Knowledge atoms from `knowledge_atoms/processed/hold2.jsonl`
- AGENT: Ollama (primitive:latest) sentiment analysis
- HOLD₂: `system_elements/holds/sentiment/processed/hold2.jsonl`

**Output Fields** (GoEmotions-compatible):
- `goemotions_primary_emotion`: One of 28 emotions
- `goemotions_primary_score`: Confidence 0.0-1.0
- `sentiment_valence`: -1.0 (negative) to 1.0 (positive)
- `sentiment_arousal`: 0.0 (calm) to 1.0 (excited)

**Interface**:
```python
service = SentimentService()
stats = service.process_pending(limit=100)
enriched = service.get_enriched_atoms(emotion_filter="joy")
```

---

## Service Dependency Graph

```
                    ┌─────────────────────┐
                    │  model_gateway_     │
                    │  service            │
                    │  (LLM routing)      │
                    └─────────┬───────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ truth_service │    │ analysis_     │    │ recommendation│
│ (extraction)  │    │ service       │    │ _service      │
└───────┬───────┘    └───────────────┘    └───────────────┘
        │
        ▼
┌───────────────┐    ┌───────────────┐
│ knowledge_    │◄───│ extractor_    │
│ service       │    │ service       │
└───────┬───────┘    └───────────────┘
        │
        ▼
┌───────────────┐    ┌───────────────┐
│ knowledge_    │    │ sentiment_    │
│ graph_service │    │ service       │
└───────────────┘    └───────────────┘

┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ contacts_     │    │ document_     │    │ script_       │
│ service       │    │ service       │    │ service       │
│ (BQ sync)     │    │               │    │               │
└───────────────┘    └───────────────┘    └───────────────┘

┌───────────────┐    ┌───────────────┐
│ schema_       │    │ frontmatter_  │
│ service       │    │ service       │
│ (shared)      │    │               │
└───────────────┘    └───────────────┘
```

---

## Storage Locations

| Service | HOLD₁ (Intake) | HOLD₂ (Processed) |
|---------|----------------|-------------------|
| truth_service | TruthService.iter_entries() | `staging/truth_atoms.jsonl` → `truth_atoms.duckdb` |
| knowledge_service | `holds/knowledge_atoms/intake/` | `holds/knowledge_atoms/processed/` |
| knowledge_graph_service | `holds/knowledge_graph/intake/` | `holds/knowledge_graph/graph.duckdb` |
| contacts | BigQuery `identity.contacts_master` | `holds/contacts/processed/hold2.duckdb` |
| model_gateway_service | `holds/model_gateway/intake/` | `holds/model_gateway/processed/` |
| analysis_service | Other service HOLDs | `holds/analysis/processed/hold2.duckdb` |
| document_service | `holds/documents/intake/` | `holds/documents/processed/` |
| script_service | `holds/scripts/intake/` | `holds/scripts/processed/` |
| sentiment_service | `holds/knowledge_atoms/processed/` | `holds/sentiment/processed/` |
| recommendation_service | User state (runtime) | `holds/recommendations/processed/` |
| schema_service | Schema definitions | `system_elements/schema_registry/*.json` |
| frontmatter_service | Raw files | File with frontmatter (moved) |
| extractor_service | File paths | KnowledgeService.exhale() |

---

## Key Patterns

### Canonical inhale/exhale Interface

All services should implement:
- `exhale(content, **kwargs) → Dict` - Push data in
- `inhale(query, limit) → List[Dict]` - Pull data out

### Deduplication

Each service specifies a `dedupe_column`:
- `atom_id` for knowledge atoms
- `document_id` for documents
- `contact_id` for contacts
- `content_hash` for content-based dedup

### Cost Governance

All LLM calls go through ModelGatewayService which:
- Uses FREE providers (Ollama, CLI tools)
- Logs every request/response to HOLDs
- Tracks cost ($0 for local, logged for observability)

---

## Migration Status

| Service | HOLD Pattern | Status |
|---------|--------------|--------|
| truth_service | ✅ | Documented |
| knowledge_service | ✅ | Documented |
| model_gateway_service | ✅ | Documented |
| knowledge_graph_service | ✅ | Documented |
| extractor_service | ✅ | Documented |
| contacts | ✅ | Documented |
| analysis_service | ✅ | Documented |
| document_service | ✅ | Documented |
| script_service | ✅ | Documented |
| frontmatter_service | ✅ | Documented |
| recommendation_service | ✅ | Documented |
| schema_service | ✅ | Documented |
| sentiment_service | ✅ | Documented |

---

*P.0 Pre-Assessment complete. Ready for S.0 DISCOVER phase.*
