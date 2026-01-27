# Central Services Architecture

**Layer**: Specification (WHAT)
**Purpose**: Understand how the 13 central services implement The Framework's philosophy

---

## 🎓 LEARNING: What Are Central Services?

Central Services are the **canonical implementations** of The Framework's patterns. They are the concrete expression of The Structure (HOLD → AGENT → HOLD) and The Cycle (WANT → CHOOSE → EXIST:NOW → SEE → HOLD → MOVE).

### The Core Pattern

All services follow **THE PATTERN**:

```
HOLD₁ (Input) → AGENT (Processing) → HOLD₂ (Output)
```

**Location**: `src/services/central_services/`

---

## 💡 CONCEPT: The Universal Interface

All services implement a **canonical interface**:

```python
# Push data in
result = service.exhale(content="...", **kwargs)

# Pull data out
data = service.inhale(query="...", limit=100)
```

**Why this matters**: This consistency makes the system predictable. Every service works the same way, so you only need to learn the pattern once.

---

## The 13 Services

### 1. KnowledgeService

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

**Philosophy**: Knowledge atoms are the indivisible units of truth. They are the "atoms" that can be combined to create any "molecule" of understanding.

---

### 2. KnowledgeGraphService

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
context = service.get_context_for(["Jeremy", "Truth Engine"])
```

**Philosophy**: Knowledge is not just stored—it's connected. The graph represents relationships, and relationships create meaning.

---

### 3. ModelGatewayService

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

**Philosophy**: All LLM calls go through one gateway. This ensures consistency, cost control, and observability.

---

### 4. TruthService

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

**Philosophy**: Truth is extracted, not created. The service finds the truth that already exists in the data.

---

### 5. ContactsService

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

**Philosophy**: Contacts are the bridge between Me (The Architect) and Not-Me (The World). They represent relationships, and relationships are the foundation of identity.

---

### 6. DocumentService

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

**Philosophy**: Documents are containers of truth. They hold knowledge that can be extracted and transformed.

---

### 7. ScriptService

**What it does**: Script storage with frontmatter stamping.

**Pattern**:
- HOLD₁: `system_elements/holds/scripts/intake/hold1.jsonl`
- AGENT: Adds frontmatter (id, issued, qa.status)
- HOLD₂: `system_elements/holds/scripts/processed/hold2.jsonl` + `.duckdb`

**Interface**:
```python
result = stamp_script("/path/to/script.py", force=True)
print(result.script_id)  # script:abc12345
```

**Philosophy**: Scripts are agents. They transform data, and their identity (script_id) enables traceability.

---

### 8. AnalysisService

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

**Philosophy**: Analysis creates meaning from data. It's The Furnace in action—transforming raw data into actionable insights.

---

### 9. RecommendationService

**What it does**: Generates tailored recommendations based on metabolic state.

**Pattern**:
- HOLD₁: User state (Kegan stage, tier, primitives)
- AGENT: ModelGatewayService (LLM call)
- HOLD₂: `system_elements/holds/recommendations/processed/hold2.duckdb`

**Interface**:
```python
recs = exhale(stage=5, tier="FRIEND", history="...", primitives=["money", "connection"])
existing = inhale(stage=5, category="ECONOMIC")
```

**Philosophy**: Recommendations are care in action. They transform understanding (truth) into action (care).

---

### 10. SchemaService

**What it does**: Centralized schema management for all services.

**Pattern**:
- HOLD₁: Schema definitions (JSON)
- AGENT: Registry + SQL generator
- HOLD₂: `system_elements/schema_registry/*.json`

**Interface**:
```python
service = get_schema_service()
sql = service.generate_sql("contacts")  # CREATE TABLE ...
schema = service.get_schema("knowledge_atoms")
```

**Philosophy**: Schemas are structure. They define the shape of data, and shape enables meaning.

---

### 11. SentimentService

**What it does**: Enriches knowledge atoms with GoEmotions-compatible sentiment.

**Pattern**:
- HOLD₁: Knowledge atoms from `knowledge_atoms/processed/hold2.jsonl`
- AGENT: Ollama (primitive:latest) sentiment analysis
- HOLD₂: `system_elements/holds/sentiment/processed/hold2.jsonl`

**Interface**:
```python
service = SentimentService()
stats = service.process_pending(limit=100)
enriched = service.get_enriched_atoms(emotion_filter="joy")
```

**Philosophy**: Sentiment adds emotional truth to factual truth. It's the bridge between data and meaning.

---

### 12. FrontmatterService

**What it does**: Document stamping with Ollama enrichment.

**Pattern**:
- HOLD₁: Raw files (MD, PY)
- AGENT: Ollama analysis → category, keywords, summary
- HOLD₂: File with frontmatter (moved to appropriate location)

**Interface**:
```python
result = stamp_document("/path/to/doc.md", organize=True)
```

**Philosophy**: Frontmatter creates identity. It gives documents structure and enables organization.

---

### 13. ExtractorService

**What it does**: Universal extractor. "Breathe Anything into Anything."

**Pattern**:
- HOLD₁: Raw source files (JSON, MD, TXT, code)
- AGENT: `universal_extraction_agent()` - dispatches by file type
- HOLD₂: Calls `KnowledgeService.exhale()` for each extracted atom

**Interface**:
```python
service = ExtractorService()
result = service.ingest("/path/to/source")
```

**Philosophy**: Extraction is transformation. It takes raw data and turns it into knowledge atoms.

---

## 🎯 PRACTICE: Using Services

Try this exercise:

1. Pick a service (start with KnowledgeService)
2. Read its documentation
3. Find an example of its use in the codebase
4. Try using it yourself in a simple script

---

## ⚠️ WARNING: Common Mistakes

1. **Don't bypass services** - Always use the canonical service interface
2. **Don't create ad-hoc solutions** - Use existing services when possible
3. **Don't skip HOLD₂** - Always write to staging before canonical store
4. **Don't ignore errors** - Services handle errors gracefully, but you must check results

---

## 🚀 MOMENTUM: Service Dependency Graph

Services depend on each other:

```
ModelGatewayService (LLM routing)
    │
    ├─ TruthService
    ├─ AnalysisService
    ├─ RecommendationService
    └─ SentimentService

KnowledgeService
    │
    └─ KnowledgeGraphService

ExtractorService
    │
    └─ KnowledgeService
```

**Understanding dependencies helps you understand the system architecture.**

---

## 📚 Next Steps

Now that you understand Central Services, read:
- **[Governance System](./02_GOVERNANCE.md)** - How services enforce universal policies
- **[Data Flow Patterns](./03_DATA_FLOW.md)** - How data moves through services

---

**Remember**: Services are the concrete expression of The Framework's philosophy. They implement The Structure and The Cycle, transforming raw data into structured truth.
