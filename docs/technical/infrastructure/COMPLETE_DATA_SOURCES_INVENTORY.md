# Complete Data Sources Inventory

**Last Updated**: 2026-01-06
**Purpose**: Comprehensive catalog of all data sources, ingestion points, and data flows in Truth Engine

---

## 🎯 Executive Summary

Truth Engine integrates data from **multiple sources** across **local storage**, **cloud databases**, **external APIs**, and **file-based exports**. This document catalogs every data source, its location, format, purpose, and how it's accessed.

### Data Source Categories

1. **Local File-Based Storage** (DuckDB, JSONL, JSON, CSV)
2. **Cloud Storage** (BigQuery, GCS)
3. **External Data Exports** (Google Takeout, Web Exports, Text Messages)
4. **API Data Sources** (Ollama, Gemini, Claude, BigQuery API)
5. **HOLD Pattern Storage** (Service-specific HOLD₁/HOLD₂)
6. **Pipeline Data** (Text Messages, Gemini Web)
7. **System Registries** (Service Catalog, Schema Registry)
8. **Browser Storage** (DuckDB WASM in-memory)

**Total Data Sources**: 100+ individual sources across all categories

---

## 📊 Data Source Categories

### 1. Local File-Based Storage

#### 1.1 DuckDB Databases (25+ databases)

**Location Pattern**: `Primitive/system_elements/holds/{service}/{intake|processed}/{name}.duckdb`

| Database | Location | Tables | Rows | Purpose | Accessed By |
|----------|----------|--------|------|---------|-------------|
| **Knowledge Graph** | `knowledge_graph/graph.duckdb` | nodes, edges, statements | 1,532 nodes, 1,556 edges | Graph-based knowledge storage | Knowledge Graph Service |
| **Knowledge Atoms** | `knowledge_atoms/processed/atoms.duckdb` | atoms | 59 | Knowledge atoms storage | Truth Service |
| **Atoms Embedded** | `knowledge_atoms/processed/atoms_embedded.duckdb` | embedded_atoms | 3,736 | Atoms with vector embeddings | Search Service |
| **Atoms Cloud** | `knowledge_atoms/processed/atoms_cloud.duckdb` | atoms | 59 | Cloud-synced atoms | Cloud Service |
| **Atom2** | `knowledge_atoms/processed/atom2.duckdb` | atoms, knowledge_atoms | 3,551 | Processed atoms | - |
| **Hold2** | `knowledge_atoms/processed/hold2.duckdb` | hold2_data | 3,610 | HOLD₂ processed atoms | - |
| **Contacts HOLD1** | `contacts/intake/hold1.duckdb` | contacts | 0 | Contact intake | Contacts Service |
| **Contacts HOLD2** | `contacts/processed/hold2.duckdb` | contacts | 1,578 | Processed contacts | Contacts Service, Primitive App |
| **Documents HOLD1** | `documents/intake/hold1.duckdb` | documents | 6,859 | Document intake | Documents Service |
| **Documents HOLD2** | `documents/processed/hold2.duckdb` | documents | 0 | Processed documents | Documents Service |
| **Identity Registry** | `identity/processed/id_registry.duckdb` | id_registry | 1 | Entity ID registry (local) | Identity Service |
| **Frontmatter Tracking** | `frontmatter/processed/hold2.duckdb` | frontmatter_tracking | 25 | Document frontmatter tracking | Script Service |
| **Analysis Results** | `analysis/processed/hold2.duckdb` | analysis_results | 4 | Analysis service results | Analytics Service |
| **Trinity Matches** | `trinity_matching/processed/matches.duckdb` | trinity_matches | 10 | Trinity matching results | Trinity Matching Service |
| **Truth Atoms** | `truth_atoms/truth_atoms.duckdb` | knowledge_atoms | 90 | Truth service atoms | Truth Service |
| **Model Gateway Prompts** | `model_gateway/prompts/prompts.duckdb` | prompts | 40 | Prompt templates | Model Gateway Service |
| **Recommendations** | `recommendations/processed/hold2.duckdb` | recommendations | 0 | Recommendation results | Recommendation Service |
| **Organism State** | `framework/processed/organism_state.duckdb` | organism_state | 1 | Framework organism state | Framework Service |
| **Health Checks** | `scripts/processed/health_checks.duckdb` | health_checks | 9 | Health check history | Terminal App |
| **Pattern Analysis** | `data/local/pattern_analysis.duckdb` | pattern_definitions, pattern_occurrences, scripts | 251,383 occurrences | Code pattern analysis | Primitive App |
| **Server Atoms** | `.primitive_engine/atoms.duckdb` | atoms | 59 | Server-side atoms | Primitive App Server |
| **Governance** | `data/local/governance.duckdb` | - | - | Governance data | Governance Service |
| **Identity** | `data/local/identity.duckdb` | - | - | Identity data | Identity Service |
| **Knowledge Atoms** | `data/local/knowledge_atoms.duckdb` | - | - | Knowledge atoms | Knowledge Service |
| **Logs** | `data/local/logs.duckdb` | - | - | Log data | Logging Service |
| **Truth** | `data/local/truth.duckdb` | - | - | Truth data | Truth Service |
| **Documents Storage** | `systems/document_storage/documents.duckdb` | - | - | Document storage | Document Storage Service |

#### 1.2 JSONL Files (67+ files)

**Location Pattern**: `Primitive/system_elements/holds/{service}/{intake|processed}/{name}.jsonl`

| File | Location | Entries | Purpose | Accessed By |
|------|----------|---------|---------|-------------|
| **Knowledge Graph Statements** | `knowledge_graph/intake/statements.jsonl` | 10,475 | Raw statements for parsing | Knowledge Graph Service |
| **Knowledge Graph Nodes** | `knowledge_graph/processed/nodes.jsonl` | 1,532 | Processed nodes | Knowledge Graph Service |
| **Knowledge Graph Edges** | `knowledge_graph/processed/edges.jsonl` | 1,556 | Processed edges | Knowledge Graph Service |
| **Knowledge Atoms HOLD1** | `knowledge_atoms/intake/hold1.jsonl` | 15 | Intake atoms | Truth Service |
| **Knowledge Atoms Primitive** | `knowledge_atoms/intake/primitive.jsonl` | 15 | Primitive atoms | Truth Service |
| **Knowledge Atoms Manifest** | `knowledge_atoms/manifests/manifest.jsonl` | 14,852 | Atom manifest/index | Truth Service |
| **Documents HOLD1** | `documents/intake/hold1.jsonl` | 9,256 | Intake documents | Documents Service |
| **Documents HOLD2** | `documents/processed/hold2.jsonl` | 10 | Processed documents | Documents Service |
| **Identity Registry** | `identity/intake/id_registry.jsonl` | 1 | ID registry intake | Identity Service |
| **Trinity Entities** | `trinity_matching/intake/entities.jsonl` | 430 | Entities for matching | Trinity Matching Service |
| **Detected Moments** | `moments/detected_moments.jsonl` | 505 | Detected moments | Moments Service |
| **Model Gateway HOLD1** | `model_gateway/intake/hold1.jsonl` | 3 | Intake prompts | Model Gateway Service |
| **Model Gateway HOLD2** | `model_gateway/processed/hold2.jsonl` | 3 | Processed prompts | Model Gateway Service |
| **Scripts HOLD1** | `scripts/intake/hold1.jsonl` | - | Script intake | Script Service |
| **System Version Catalog** | `Primitive/migrations/SYSTEM_VERSION_CATALOG.jsonl` | 40 | Component registry | Builder Service |
| **Governance Backlog** | `governance/intake/backlog.jsonl` | - | Backlog items | Governance Service |
| **Governance Reduction** | `governance/reduction/inventory.jsonl` | - | Reduction inventory | Governance Service |
| **Governance Moments** | `governance/intake/moment.jsonl` | - | Moment data | Governance Service |
| **Governance Moments (plural)** | `governance/intake/moments.jsonl` | - | Multiple moments | Governance Service |
| **System Intake** | `systems/document_storage/intake.jsonl` | - | System intake | Document Storage Service |

**Additional JSONL Files**:
- Test data: `test_pattern/hold1.jsonl`, `test_pattern/hold2.jsonl`
- Archive data: Various archived JSONL files in `_archive` directories
- Pipeline data: Various pipeline-specific JSONL files

#### 1.3 JSON Registry Files

| File | Location | Purpose | Status |
|------|----------|---------|--------|
| **Schema Registry** | `Primitive/system_elements/schema_registry/*.json` | System schema definitions (11 files) | ✅ Active |
| **Service Registry (Deprecated)** | `src/services/central_services/registry.json` | Service registry | 🚨 Deprecated |
| **Service Registry (Deprecated)** | `Primitive/system_elements/service_registry/registry.json` | Service registry | 🚨 Deprecated |
| **System Version Catalog** | `Primitive/migrations/SYSTEM_VERSION_CATALOG.jsonl` | Single source of truth | ✅ Active |

**Schema Registry Files** (11 files):
- `analysis_results.json`
- `backlog.json`
- `contacts.json`
- `costs.json`
- `documents.json`
- `knowledge_atoms.json`
- `knowledge_graph.json`
- `model_requests.json`
- `model_responses.json`
- `recommendations.json`
- `scripts.json`

#### 1.4 CSV Files

| File | Location | Purpose | Accessed By |
|------|----------|---------|-------------|
| **Stage 1 Messages** | `data/raw/stage_1_local_messages.csv` | Text messages (stage 1) | Text Messages Pipeline |
| **Stage 2 Aligned** | `data/raw/stage_2_aligned_messages.csv` | Aligned messages | Text Messages Pipeline |
| **Stage 2 Unresolved** | `data/raw/stage_2_unresolved_handles.csv` | Unresolved handles | Text Messages Pipeline |
| **Business Contacts** | `data/business_contacts_review.csv` | Business contacts | Contacts Service |
| **Identity Contacts** | `data/identity/*.csv` | Identity contact data | Identity Service |
| **Exports** | `data/exports/*.csv` | Exported data | Various services |

#### 1.5 Log Files

| File | Location | Purpose | Accessed By |
|------|----------|---------|-------------|
| **Daemon Log** | `Primitive/logs/current/daemon.log` | Daemon operations | Terminal App, Primitive App |
| **Daemon Error Log** | `Primitive/logs/current/daemon_error.log` | Daemon errors | Terminal App, Primitive App |
| **Healthcheck Log** | `Primitive/logs/current/healthcheck.log` | Health check operations | Terminal App |
| **Healthcheck Error Log** | `Primitive/logs/current/healthcheck_error.log` | Health check errors | Terminal App |

#### 1.6 Markdown Files

| File | Location | Purpose | Accessed By |
|------|----------|---------|-------------|
| **Health Check Report** | `Primitive/reports/health_check_latest.md` | System health status | Terminal App |
| **Framework Docs** | `framework/**/*.md` | Framework documentation | Various |
| **Pipeline Docs** | `pipelines/**/*.md` | Pipeline documentation | Various |
| **Service Docs** | `Primitive/central_services/**/README.md` | Service documentation | Various |

---

### 2. Cloud Storage (BigQuery)

#### 2.1 BigQuery Projects and Datasets

| Project | Dataset | Purpose | Status | Accessed By |
|---------|---------|---------|--------|-------------|
| **flash-clover-464719-g1** | `identity` | Identity and contacts | ✅ Active | Identity Service, Contacts Service |
| **flash-clover-464719-g1** | `spine` | Text messages pipeline | ✅ Active | Text Messages Pipeline |
| **flash-clover-464719-g1** | `gemini_web` | Gemini Web pipeline | ✅ Active | Gemini Web Pipeline |
| **llama-pro-global** | `core_metabolism` | Unified deep storage | ✅ Active | Primitive App (Cloud Service) |
| **llama-pro-local** | `instance_hold` | Instance-specific data | ✅ Active | Primitive App (Cloud Service) |
| **llama-vault** | `s3-archive` | AWS cold storage archive | ⚠️ Idle | Primitive App (Cloud Service) |

#### 2.2 BigQuery Tables

**Identity Dataset** (`flash-clover-464719-g1.identity`):
- `id_registry` - Entity ID registry (65,350+ rows)
- `contacts_master` - Master contacts table

**Spine Dataset** (`flash-clover-464719-g1.spine`):
- `text_messages_stage_1` - Stage 1 text messages
- `text_messages_stage_3` - Stage 3 text messages (with entity IDs)
- `text_messages_stage_4` - Stage 4 LLM processed
- `text_messages_stage_5` - Stage 5 NLP processed
- `text_messages_stage_6` - Stage 6 tokenized
- `text_messages_stage_6_tokens` - Stage 6 tokens
- `entity_unified` - Unified entity data

**Gemini Web Dataset** (`flash-clover-464719-g1.gemini_web`):
- `gemini_web_stage_1` - Stage 1 activities
- `gemini_web_stage_2` - Stage 2 normalized
- `gemini_web_stage_3` - Stage 3 with IDs
- `gemini_web_stage_4` - Stage 4 LLM processed
- `gemini_web_stage_5` - Stage 5 NLP processed

**Core Metabolism Dataset** (`llama-pro-global.core_metabolism`):
- Unified deep storage tables
- Synced from local HOLDs

**Instance Hold Dataset** (`llama-pro-local.instance_hold`):
- Instance-specific data
- Synced from local HOLDs

---

### 3. External Data Exports

#### 3.1 Google Takeout Exports

| Source | Location | Format | Purpose | Pipeline |
|--------|----------|--------|---------|----------|
| **Gemini Web Activity** | `data/web_exports/gemini_web/MyActivity.json` | JSON (activity log) | Gemini Web interactions | Gemini Web Pipeline |
| **Google AI Studio** | `data/ai_conversations/google_ai_studio/` | Various formats | AI conversation exports | - |
| **Google Takeout Archive** | `data/_archive/google_ai_studio_raw_export/` | Various formats | Archived exports | - |

#### 3.2 Web Exports

| Source | Location | Format | Purpose | Pipeline |
|--------|----------|--------|---------|----------|
| **ChatGPT Web** | `data/web_exports/chatgpt/` | JSON (conversations) | ChatGPT conversations | - |
| **Claude Web** | `data/web_exports/claude/` | JSON (conversations) | Claude conversations | - |
| **Gemini Web** | `data/web_exports/gemini_web/` | JSON (activity log) | Gemini Web activity | Gemini Web Pipeline |

#### 3.3 Text Message Exports

| Source | Location | Format | Purpose | Pipeline |
|--------|----------|--------|---------|----------|
| **Local Messages** | `data/raw/stage_1_local_messages.csv` | CSV | Text messages (raw) | Text Messages Pipeline |
| **Aligned Messages** | `data/raw/stage_2_aligned_messages.csv` | CSV | Aligned messages | Text Messages Pipeline |
| **Unresolved Handles** | `data/raw/stage_2_unresolved_handles.csv` | CSV | Unresolved handles | Text Messages Pipeline |

#### 3.4 Social Media Exports

| Source | Location | Format | Purpose | Pipeline |
|--------|----------|--------|---------|----------|
| **Grindr Data Export** | `data/data_request-15582c8b-fa3f-4154-9b40-bb52aa69f2a9/` | HTML, JSON, Media | Grindr account data | - |

**Grindr Export Structure**:
- `account_report/` - Account information
- `ai_report/` - AI-related data
- `albums_report/` - Photo albums
- `chat_report/` - Chat messages (122 AAC files, 110 JPG files)
- `consent_report/` - Consent data
- `location_report/` - Location data
- `media_report/` - Media files
- `product_report/` - Product data
- `purchase_report/` - Purchase data
- `push_report/` - Push notification data
- `right_now_report/` - Right Now feature data
- `roam_report/` - Roam feature data
- `third_party_report/` - Third-party data
- `visiting_report/` - Visiting data

#### 3.5 Zoom Sessions

| Source | Location | Format | Purpose | Pipeline |
|--------|----------|--------|---------|----------|
| **Zoom Sessions** | `data/zoom_chats/` | Various | Zoom session data | Zoom Pipeline |

#### 3.6 Browser History

| Source | Location | Format | Purpose | Pipeline |
|--------|----------|--------|---------|----------|
| **Browser History** | `data/web_exports/browser_history/` | JSON/CSV | Browser history data | - |

---

### 4. API Data Sources

#### 4.1 LLM APIs

| API | Purpose | Access Method | Used By |
|-----|---------|---------------|---------|
| **Ollama API** | Local LLM inference | `http://localhost:11434/api/generate` | Model Gateway Service, Truth Service |
| **Gemini API** | Google Gemini LLM | Google Cloud API | Model Gateway Service, Gemini Web Pipeline |
| **Claude API** | Anthropic Claude LLM | Anthropic API | Model Gateway Service |

**Ollama Models**:
- `primitive:latest` - Primary model
- Various other models available via Ollama

**Model Gateway Service**:
- Centralized LLM access
- Supports Ollama, Gemini, Claude
- Cost tracking and rate limiting
- Prompt template management

#### 4.2 BigQuery API

| API | Purpose | Access Method | Used By |
|-----|---------|---------------|---------|
| **BigQuery API** | Cloud data storage/query | Google Cloud BigQuery Client | All services, pipelines |

**BigQuery Client Features**:
- Cost protection (session-wide limits)
- Query result caching
- Retry logic with circuit breaker
- Protected table enforcement
- Cost tracking

#### 4.3 Daemon API

| Endpoint | Purpose | Method | Used By |
|----------|---------|--------|---------|
| `GET /health` | Daemon health status | HTTP | Terminal App, Primitive App |
| `GET /dashboard` | Dashboard data | HTTP | Terminal App |
| `GET /atoms` | Knowledge atoms | HTTP | Terminal App, Primitive App |
| `GET /atoms/search` | Search atoms | HTTP | Terminal App, Primitive App |
| `GET /registry/primitives` | Primitive registry | HTTP | Terminal App, Primitive App |
| `GET /registry/services` | Service registry | HTTP | Terminal App, Primitive App |
| `GET /logs` | Log entries | HTTP | Terminal App, Primitive App |
| `POST /daemon/restart` | Restart daemon | HTTP | Terminal App |

**Base URL**: `http://localhost:8000`

#### 4.4 MCP Servers

| Server | Purpose | Access Method | Used By |
|--------|---------|---------------|---------|
| **Brave Search MCP** | Web search | MCP protocol | Various services |
| **Filesystem MCP** | File operations | MCP protocol | Various services |
| **GitHub MCP** | GitHub operations | MCP protocol | Various services |
| **Truth Engine MCP** | Truth Engine operations | MCP protocol | Various services |

---

### 5. HOLD Pattern Storage

All services follow the **HOLD₁ → AGENT → HOLD₂** pattern:

#### 5.1 Service HOLDs

| Service | HOLD₁ (Intake) | HOLD₂ (Processed) | Purpose |
|---------|----------------|-------------------|---------|
| **Cost Service** | `cost_service/intake/hold1.jsonl` | `cost_service/processed/hold2.duckdb` | Cost tracking |
| **Run Service** | `run_service/intake/hold1.jsonl` | `run_service/processed/hold2.duckdb` | Run tracking |
| **Relationship Service** | `relationship_service/intake/hold1.jsonl` | `relationship_service/processed/hold2.duckdb` | Relationship tracking |
| **Version Service** | `version_service/intake/hold1.jsonl` | `version_service/processed/hold2.duckdb` | Version tracking |
| **Workflow Service** | `workflow_service/intake/hold1.jsonl` | `workflow_service/processed/hold2.duckdb` | Workflow orchestration |
| **Search Service** | `search_service/intake/hold1.jsonl` | `search_service/processed/hold2.duckdb` | Search operations |
| **Analytics Service** | `analytics_service/intake/hold1.jsonl` | `analytics_service/processed/hold2.duckdb` | Analytics results |
| **Quality Service** | `quality_service/intake/hold1.jsonl` | `quality_service/processed/hold2.duckdb` | Quality assessments |
| **Builder Service** | `builder_service/intake/hold1.jsonl` | `builder_service/processed/hold2.duckdb` | Build operations |

**HOLD Pattern**:
- **HOLD₁**: Raw intake data (JSONL format)
- **AGENT**: Transformation logic (service-specific)
- **HOLD₂**: Processed data (DuckDB format)

---

### 6. Pipeline Data

#### 6.1 Text Messages Pipeline

| Stage | Input | Output | Purpose |
|-------|-------|--------|---------|
| **Stage 0** | Source assessment | Assessment docs | Source analysis |
| **Stage 1** | CSV files | `spine.text_messages_stage_1` | Source ingestion |
| **Stage 2** | Stage 1 | `spine.text_messages_stage_2` | Source normalization |
| **Stage 3** | Stage 2 | `spine.text_messages_stage_3` | System ID generation |
| **Stage 4** | Stage 3 | `spine.text_messages_stage_4` | LLM processing |
| **Stage 5** | Stage 4 | `spine.text_messages_stage_5` | NLP processing |
| **Stage 6** | Stage 5 | `spine.text_messages_stage_6` | Tokenization |
| **Stage 7-15** | Previous stages | Various tables | Additional processing |

**Data Flow**:
```
CSV Files → Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5 → Stage 6 → ...
```

#### 6.2 Gemini Web Pipeline

| Stage | Input | Output | Purpose |
|-------|-------|--------|---------|
| **Stage 0** | Source assessment | Assessment docs | Source analysis |
| **Stage 1** | `MyActivity.json` | `gemini_web_stage_1` | Source ingestion |
| **Stage 2** | Stage 1 | `gemini_web_stage_2` | Source normalization |
| **Stage 3** | Stage 2 | `gemini_web_stage_3` | System ID generation |
| **Stage 4** | Stage 3 | `gemini_web_stage_4` | LLM processing |
| **Stage 5** | Stage 4 | `gemini_web_stage_5` | NLP processing |

**Data Flow**:
```
Google Takeout JSON → Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5
```

---

### 7. System Registries

#### 7.1 System Version Catalog

| File | Location | Entries | Purpose | Status |
|------|----------|---------|---------|--------|
| **System Version Catalog** | `Primitive/migrations/SYSTEM_VERSION_CATALOG.jsonl` | 40 | Single source of truth for components | ✅ Active |

**Schema**:
- `component` - Component name
- `path` - File path
- `purpose` - Purpose description
- `status` - Status (ACTIVE, DEPRECATED, etc.)
- `retention` - Retention policy
- `category` - Category (Services, Pipelines, etc.)
- `registered_at` - Registration timestamp
- `version` - Version number
- `registry_name` - Registry name
- `phase` - Phase (0-5)
- `exhale` - Has exhale method
- `inhale` - Has inhale method
- `hold1` - HOLD₁ path
- `hold2` - HOLD₂ path
- `produces_atoms` - Produces knowledge atoms
- `produces_edges` - Produces graph edges
- And more...

#### 7.2 Schema Registry

| Location | Files | Purpose | Status |
|----------|-------|---------|--------|
| `Primitive/system_elements/schema_registry/` | 11 JSON files | System schema definitions | ✅ Active |

**Files**:
- `analysis_results.json`
- `backlog.json`
- `contacts.json`
- `costs.json`
- `documents.json`
- `knowledge_atoms.json`
- `knowledge_graph.json`
- `model_requests.json`
- `model_responses.json`
- `recommendations.json`
- `scripts.json`

---

### 8. Browser Storage (Primitive App)

#### 8.1 In-Memory DuckDB (WASM)

| Table | Schema | Purpose | Accessed By |
|-------|--------|---------|-------------|
| **Primitives** | id, name, category, last_active | Primitive entries | Primitive App UI |
| **Atoms** | id, type, content, source, timestamp, vector (1024-dim), hash | Knowledge atoms with vectors | Primitive App RAG |
| **External Knowledge** | id, source_url, source_title, title, summary, relevance_to_me, timestamp, hash | External knowledge items | Primitive App |
| **Lenses Perspectives** | id, category, lens, perspective, last_updated, hash | Lens perspectives | Primitive App |
| **Thresholds** | id, type, label, description, value, timestamp, message_id | Threshold crossings | Primitive App |

**Note**: Browser DuckDB is **ephemeral** (in-memory, lost on refresh)

---

## 🔄 Data Flow Patterns

### Pattern 1: HOLD₁ → AGENT → HOLD₂

```
External Source → HOLD₁ (JSONL) → AGENT (Service Logic) → HOLD₂ (DuckDB)
```

**Example**: Cost Service
- **HOLD₁**: `cost_service/intake/hold1.jsonl` (raw cost events)
- **AGENT**: Cost transformation logic
- **HOLD₂**: `cost_service/processed/hold2.duckdb` (processed costs)

### Pattern 2: Pipeline Stages

```
Source → Stage 1 → Stage 2 → Stage 3 → ... → Final Stage
```

**Example**: Text Messages Pipeline
- **Source**: CSV files
- **Stage 1**: Source ingestion → BigQuery
- **Stage 2**: Normalization → BigQuery
- **Stage 3**: ID generation → BigQuery
- **Stage 4**: LLM processing → BigQuery
- **Stage 5**: NLP processing → BigQuery
- **Stage 6**: Tokenization → BigQuery

### Pattern 3: Local → Cloud Sync

```
Local HOLD → Sync Service → BigQuery
```

**Example**: Identity Service
- **Local**: `identity/intake/id_registry.jsonl`
- **Sync**: `identity_service.sync_to_bigquery()`
- **Cloud**: `identity.id_registry` (BigQuery)

### Pattern 4: API → Service → HOLD

```
External API → Service → HOLD₁ → AGENT → HOLD₂
```

**Example**: Model Gateway Service
- **API**: Ollama/Gemini/Claude API
- **Service**: Model Gateway Service
- **HOLD₁**: `model_gateway/intake/hold1.jsonl`
- **AGENT**: Prompt processing
- **HOLD₂**: `model_gateway/processed/hold2.jsonl`

---

## 📋 Data Source Access Methods

### 1. Direct File Access

**Used By**: Terminal App, Local Services

**Pattern**:
```python
from pathlib import Path
data = Path("path/to/file.jsonl").read_text()
```

### 2. DuckDB Queries

**Used By**: All Services, Primitive App

**Pattern**:
```python
import duckdb
conn = duckdb.connect("path/to/file.duckdb")
result = conn.execute("SELECT * FROM table").fetchall()
```

### 3. BigQuery Queries

**Used By**: Pipelines, Services

**Pattern**:
```python
from src.services.central_services.core.bigquery_client import get_bigquery_client
bq_client = get_bigquery_client()
result = bq_client.query("SELECT * FROM table").result()
```

### 4. Service APIs

**Used By**: Apps, Other Services

**Pattern**:
```python
from Primitive.central_services.cost_service import CostService
service = CostService()
service.exhale(service="my_service", operation="op", cost_usd=0.01)
```

### 5. Daemon API

**Used By**: Terminal App, Primitive App

**Pattern**:
```python
import requests
response = requests.get("http://localhost:8000/atoms")
atoms = response.json()
```

---

## 🎯 Key Data Sources by Category

### Most Critical Data Sources

1. **System Version Catalog** (`SYSTEM_VERSION_CATALOG.jsonl`) - Single source of truth
2. **Knowledge Graph** (`knowledge_graph/graph.duckdb`) - 1,532 nodes, 1,556 edges
3. **Identity Registry** (BigQuery + local) - 65,350+ entity IDs
4. **Pattern Analysis** (`pattern_analysis.duckdb`) - 251,383 pattern occurrences
5. **Text Messages Pipeline** (BigQuery `spine` dataset) - Main pipeline data

### Most Frequently Accessed

1. **Knowledge Atoms** - Accessed by Truth Service, Search Service, Primitive App
2. **Contacts** - Accessed by Contacts Service, Primitive App
3. **Identity Registry** - Accessed by Identity Service, all pipelines
4. **System Version Catalog** - Accessed by Builder Service, all services
5. **Health Checks** - Accessed by Terminal App, Daemon

### Largest Data Sources

1. **Pattern Analysis** - 251,383 pattern occurrences
2. **Knowledge Graph Statements** - 10,475 entries
3. **Identity Registry** - 65,350+ rows (BigQuery)
4. **Knowledge Atoms Manifest** - 14,852 entries
5. **Documents HOLD1** - 9,256 entries

---

## 📝 Notes

### Data Source Characteristics

1. **HOLD Pattern**: All services follow HOLD₁ → AGENT → HOLD₂
2. **Dual Format**: Most HOLDs have both JSONL (intake) and DuckDB (processed)
3. **BigQuery Sync**: Critical data synced to BigQuery for cloud storage
4. **Local First**: Most data stored locally, synced to cloud
5. **Append-Only**: JSONL files are append-only audit trails
6. **Queryable**: DuckDB files are queryable via SQL

### Data Source Locations

- **HOLDs**: `Primitive/system_elements/holds/{service}/`
- **Pipelines**: `pipelines/{pipeline_name}/`
- **Data**: `data/{category}/`
- **Logs**: `Primitive/logs/current/`
- **Registries**: `Primitive/migrations/`, `Primitive/system_elements/schema_registry/`

### Data Source Status

- ✅ **Active**: Currently in use
- 🚨 **Deprecated**: Marked for removal, kept for backward compatibility
- ⚠️ **Idle**: Not actively used but maintained
- ❌ **Archived**: Moved to archive, not actively used

---

## 🔍 Finding Data Sources

### Search Patterns

```bash
# Find all DuckDB files
find . -name "*.duckdb" -type f

# Find all JSONL files
find . -name "*.jsonl" -type f

# Find all BigQuery references
grep -r "bigquery\|BigQuery" --include="*.py"

# Find all service HOLDs
find Primitive/system_elements/holds -type d

# Find all pipeline data
find pipelines -name "*.py" -o -name "*.sql"
```

### Service Discovery

```python
# Query System Version Catalog
import duckdb
import json

conn = duckdb.connect(":memory:")
conn.execute("""
    CREATE TABLE catalog AS
    SELECT * FROM read_json_objects('Primitive/migrations/SYSTEM_VERSION_CATALOG.jsonl')
""")

# Get all active services
services = conn.execute("""
    SELECT component, path, hold1, hold2
    FROM catalog
    WHERE status = 'ACTIVE' AND category = 'Services'
""").fetchall()
```

---

## 📚 Related Documentation

- **Complete Dataset Inventory**: `docs/COMPLETE_DATASET_INVENTORY.md`
- **BigQuery Sync Mechanism**: `docs/BIGQUERY_SYNC_MECHANISM.md`
- **BigQuery Sync Inventory**: `docs/BIGQUERY_SYNC_INVENTORY.md`
- **Apps Dataset Connections**: `docs/APPS_DATASET_CONNECTIONS.md`
- **System Version Catalog Schema**: `Primitive/migrations/CATALOG_METADATA_SCHEMA.md`
- **The Furnace and The Form**: `docs/THE_FURNACE_AND_THE_FORM.md` - Framework for Emergent Synthesis

---

**Last Updated**: 2026-01-06
**Maintained By**: Truth Engine Documentation System
