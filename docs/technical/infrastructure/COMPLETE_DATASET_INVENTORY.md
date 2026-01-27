# Complete Dataset Inventory

**Last Updated**: 2025-01-XX

This document provides a comprehensive inventory of **every dataset, HOLD, log, registry, and data element** that the Primitive App and Terminal App connect to.

## 🎯 Executive Summary

- **Total Datasets**: 78
  - DuckDB Databases: 20
  - JSONL Files: 32
  - JSON Registry Files: 11
  - Log Files: 4
  - BigQuery Datasets: 5
  - Browser Tables: 5
  - Markdown Reports: 1

- **🎯 PRIMITIVE REGISTRY LOCATION**: `Primitive/system_elements/schema_registry/*.json` (11 files)
  - Accessed via Daemon endpoint: `/registry/primitives`
  - Contains system schema definitions for all primitives

- **Most Critical Datasets**:
  1. **Schema Registry** - Primitive registry (11 JSON files)
  2. **SYSTEM_VERSION_CATALOG** - Component registry (40+ entries)
  3. **Knowledge Graph** - 1,532 nodes, 1,556 edges
  4. **Pattern Analysis** - 251,383 pattern occurrences
  5. **Identity Registry** - 65,350+ entity IDs (BigQuery + local)

---

## 📊 Quick Reference Table

| # | Dataset | Location | Type | Rows/Entries | Key Contents | Accessed By |
|---|---------|----------|------|--------------|--------------|-------------|
| **HEALTH CHECKS** |
| Health Check Report | `Primitive/reports/health_check_latest.md` | Markdown | 1 file | System health, HOLD status, Ollama status | Terminal App (LocalDataReader) |
| Health Check JSONL | `Primitive/staging/health_checks.jsonl` | JSONL | 9 entries | report_id, timestamp, checks, summary | Daemon |
| Health Check DuckDB | `Primitive/system_elements/holds/scripts/processed/health_checks.duckdb` | DuckDB | 9 rows | health_checks table | Terminal App (path defined) |
| **KNOWLEDGE ATOMS** |
| Atoms DuckDB (Server) | `.primitive_engine/atoms.duckdb` | DuckDB | 59 rows | atoms table | Primitive App (server) |
| Atoms DuckDB (HOLD) | `Primitive/system_elements/holds/knowledge_atoms/processed/atoms.duckdb` | DuckDB | 59 rows | atoms table | - |
| Atoms Embedded | `Primitive/system_elements/holds/knowledge_atoms/processed/atoms_embedded.duckdb` | DuckDB | 3,736 rows | embedded_atoms (with embeddings) | - |
| Atoms Cloud | `Primitive/system_elements/holds/knowledge_atoms/processed/atoms_cloud.duckdb` | DuckDB | 59 rows | atoms table | - |
| Atom2 DuckDB | `Primitive/system_elements/holds/knowledge_atoms/processed/atom2.duckdb` | DuckDB | 3,551 rows | atoms, knowledge_atoms tables | - |
| Hold2 DuckDB | `Primitive/system_elements/holds/knowledge_atoms/processed/hold2.duckdb` | DuckDB | 3,610 rows | hold2_data table | - |
| Hold1 JSONL | `Primitive/system_elements/holds/knowledge_atoms/intake/hold1.jsonl` | JSONL | 15 entries | Intake atoms | - |
| Primitive JSONL | `Primitive/system_elements/holds/knowledge_atoms/intake/primitive.jsonl` | JSONL | 15 entries | Primitive atoms | - |
| Manifest JSONL | `Primitive/system_elements/holds/knowledge_atoms/manifests/manifest.jsonl` | JSONL | 14,852 entries | Atom manifests | - |
| **KNOWLEDGE GRAPH** |
| Graph DuckDB | `Primitive/system_elements/holds/knowledge_graph/graph.duckdb` | DuckDB | 1,532 nodes, 1,556 edges | nodes, edges, statements tables | - |
| Statements JSONL | `Primitive/system_elements/holds/knowledge_graph/intake/statements.jsonl` | JSONL | 10,475 entries | Raw statements for parsing | - |
| Nodes JSONL | `Primitive/system_elements/holds/knowledge_graph/processed/nodes.jsonl` | JSONL | 1,532 entries | Processed nodes | - |
| Edges JSONL | `Primitive/system_elements/holds/knowledge_graph/processed/edges.jsonl` | JSONL | 1,556 entries | Processed edges | - |
| **CONTACTS** |
| Contacts HOLD1 | `Primitive/system_elements/holds/contacts/intake/hold1.duckdb` | DuckDB | 0 rows | contacts table (intake) | - |
| Contacts HOLD2 | `Primitive/system_elements/holds/contacts/processed/hold2.duckdb` | DuckDB | 1,578 rows | contacts table (processed) | Primitive App (contactService) |
| Contacts JSONL | `Primitive/system_elements/holds/contacts/intake/hold1.jsonl` | JSONL | 0 entries | Intake contacts | - |
| **DOCUMENTS** |
| Documents HOLD1 | `Primitive/system_elements/holds/documents/intake/hold1.duckdb` | DuckDB | 6,859 rows | documents table | - |
| Documents HOLD2 | `Primitive/system_elements/holds/documents/processed/hold2.duckdb` | DuckDB | 0 rows | documents, hold2_data tables | - |
| Documents HOLD1 JSONL | `Primitive/system_elements/holds/documents/intake/hold1.jsonl` | JSONL | 9,256 entries | Intake documents | - |
| Documents HOLD2 JSONL | `Primitive/system_elements/holds/documents/processed/hold2.jsonl` | JSONL | 10 entries | Processed documents | - |
| **IDENTITY** |
| ID Registry DuckDB | `Primitive/system_elements/holds/identity/processed/id_registry.duckdb` | DuckDB | 1 row | id_registry table | - |
| ID Registry JSONL | `Primitive/system_elements/holds/identity/intake/id_registry.jsonl` | JSONL | 1 entry | entity_id, entity_type, generation_method, context_data | Identity Service |
| **FRAMEWORK** |
| Organism State | `Primitive/system_elements/holds/framework/processed/organism_state.duckdb` | DuckDB | 1 row | organism_state table | - |
| **FRONTMATTER** |
| Frontmatter Tracking | `Primitive/system_elements/holds/frontmatter/processed/hold2.duckdb` | DuckDB | 25 rows | frontmatter_tracking table | - |
| **ANALYSIS** |
| Analysis Results | `Primitive/system_elements/holds/analysis/processed/hold2.duckdb` | DuckDB | 4 rows | analysis_results table | - |
| **MOMENTS** |
| Detected Moments | `Primitive/system_elements/holds/moments/detected_moments.jsonl` | JSONL | 505 entries | moment_id, message_id, moment_type, confidence | - |
| **TRINITY MATCHING** |
| Trinity Matches | `Primitive/system_elements/holds/trinity_matching/processed/matches.duckdb` | DuckDB | 10 rows | trinity_matches table | - |
| Trinity Entities | `Primitive/system_elements/holds/trinity_matching/intake/entities.jsonl` | JSONL | 430 entries | entity_id, text, emotions, topics | - |
| **TRUTH ATOMS** |
| Truth Atoms | `Primitive/system_elements/holds/truth_atoms/truth_atoms.duckdb` | DuckDB | 90 rows | knowledge_atoms table | - |
| **MODEL GATEWAY** |
| Prompts | `Primitive/system_elements/holds/model_gateway/prompts/prompts.duckdb` | DuckDB | 40 rows | prompts table | - |
| Model Gateway HOLD1 | `Primitive/system_elements/holds/model_gateway/intake/hold1.jsonl` | JSONL | 3 entries | Intake prompts | - |
| Model Gateway HOLD2 | `Primitive/system_elements/holds/model_gateway/processed/hold2.jsonl` | JSONL | 3 entries | Processed prompts | - |
| **RECOMMENDATIONS** |
| Recommendations | `Primitive/system_elements/holds/recommendations/processed/hold2.duckdb` | DuckDB | 0 rows | recommendations table | - |
| **PATTERN ANALYSIS** |
| Pattern Analysis | `data/local/pattern_analysis.duckdb` | DuckDB | 251,383 occurrences | pattern_definitions, pattern_occurrences, scripts | Primitive App (server) |
| **REGISTRIES** |
| Schema Registry | `Primitive/system_elements/schema_registry/*.json` | JSON | 11 files | System schemas (knowledge_atoms, contacts, etc.) | Daemon (/registry/primitives) |
| Service Registry | `Primitive/system_elements/service_registry/registry.json` | JSON | 4 services | Service definitions | - |
| Central Services Registry | `src/services/central_services/registry.json` | JSON | 13+ services | Service status, HOLD paths | - |
| SYSTEM_VERSION_CATALOG | `Primitive/migrations/SYSTEM_VERSION_CATALOG.jsonl` | JSONL | Multiple entries | Component registry, migration status | - |
| **GOVERNANCE** |
| Backlog | `architect_central_services/.../governance/intake/backlog.jsonl` | JSONL | Varies | Backlog items | Primitive App (server) |
| Perspectives | `architect_central_services/.../governance/intake/perspectives.jsonl` | JSONL | Varies | Perspective data | Primitive App (server) |
| **LOGS** |
| Daemon Log | `Primitive/logs/current/daemon.log` | Text | 0 lines | Daemon operations | Terminal App, Primitive App |
| Daemon Error Log | `Primitive/logs/current/daemon_error.log` | Text | 66 lines | Daemon errors | Terminal App, Primitive App |
| Healthcheck Log | `Primitive/logs/current/healthcheck.log` | Text | 0 lines | Health check operations | Terminal App |
| Healthcheck Error Log | `Primitive/logs/current/healthcheck_error.log` | Text | 235 lines | Health check errors | Terminal App |
| **BIGQUERY** |
| UNIFIED_DEEP_HOLD | `llama-pro-global.core_metabolism` | BigQuery | - | Unified data storage | Primitive App (cloudService) |
| LOCAL_INSTANCE_MIRROR | `llama-pro-local.instance_hold` | BigQuery | - | Instance-specific data | Primitive App (cloudService) |
| AWS_COLD_STORAGE | `llama-vault.s3-archive` | BigQuery/S3 | - | Archive storage | Primitive App (cloudService) |
| Identity Registry | `flash-clover-464719-g1.identity.id_registry` | BigQuery | 65,350+ rows | Entity ID registry | Identity Service |
| Contacts Master | `flash-clover-464719-g1.identity.contacts_master` | BigQuery | - | Master contacts table | Contacts Service |
| **BROWSER STORAGE (Primitive App)** |
| Primitives Table | Browser DuckDB WASM | DuckDB | In-memory | Primitive entries | Primitive App (dbService) |
| Atoms Table | Browser DuckDB WASM | DuckDB | In-memory | Knowledge atoms with vectors | Primitive App (dbService) |
| External Knowledge | Browser DuckDB WASM | DuckDB | In-memory | External knowledge items | Primitive App (dbService) |
| Lenses Perspectives | Browser DuckDB WASM | DuckDB | In-memory | Lens perspectives | Primitive App (dbService) |
| Thresholds | Browser DuckDB WASM | DuckDB | In-memory | Threshold crossings | Primitive App (dbService) |

---

## 📋 Detailed Dataset Descriptions

### Health Check Data

#### 1. Health Check Report (Markdown)
- **Path**: `Primitive/reports/health_check_latest.md`
- **Type**: Markdown report
- **Contents**:
  - Overall system status (OK/WARN/FAIL)
  - Counts: ok, warn, fail
  - Date/timestamp
  - HOLDs table with status for each HOLD
  - Ollama status and available models
- **Accessed By**: Terminal App (`LocalDataReader.getLatestHealthCheck()`)
- **Purpose**: System health overview

#### 2. Health Check JSONL
- **Path**: `Primitive/staging/health_checks.jsonl`
- **Type**: JSONL file
- **Entries**: 9
- **Schema**:
  - `report_id`: Unique report identifier
  - `timestamp`: ISO timestamp
  - `primitive_root`: Path to Primitive directory
  - `checks`: Health check details
  - `summary`: Summary statistics
  - `content_hash`: Content hash for deduplication
- **Accessed By**: Daemon endpoint `/health`

#### 3. Health Check DuckDB
- **Path**: `Primitive/system_elements/holds/scripts/processed/health_checks.duckdb`
- **Type**: DuckDB database
- **Table**: `health_checks`
- **Rows**: 9
- **Schema**: report_id, timestamp, overall_status, ok_count, warn_count, fail_count, holds, ollama_status, ollama_models
- **Accessed By**: Terminal App (path defined but not actively queried)

---

### Knowledge Atoms

#### 1. Atoms DuckDB (Server)
- **Path**: `.primitive_engine/atoms.duckdb`
- **Type**: DuckDB database
- **Table**: `atoms`
- **Rows**: 59
- **Accessed By**: Primitive App server (`queryAtoms()`)
- **Purpose**: Server-side atoms storage

#### 2. Atoms Embedded DuckDB
- **Path**: `Primitive/system_elements/holds/knowledge_atoms/processed/atoms_embedded.duckdb`
- **Type**: DuckDB database
- **Table**: `embedded_atoms`
- **Rows**: 3,736
- **Schema**: atom_id, content, content_hash, source_name, source_file, embedding (vector)
- **Purpose**: Atoms with vector embeddings for similarity search

#### 3. Atom2 DuckDB
- **Path**: `Primitive/system_elements/holds/knowledge_atoms/processed/atom2.duckdb`
- **Type**: DuckDB database
- **Tables**: `atoms` (3,551 rows), `knowledge_atoms` (7 rows)
- **Purpose**: Processed atoms storage

#### 4. Hold2 DuckDB
- **Path**: `Primitive/system_elements/holds/knowledge_atoms/processed/hold2.duckdb`
- **Type**: DuckDB database
- **Table**: `hold2_data`
- **Rows**: 3,610
- **Schema**: atom_id, content, content_hash, source_name, created_at, etc.
- **Purpose**: HOLD₂ processed atoms

#### 5. Manifest JSONL
- **Path**: `Primitive/system_elements/holds/knowledge_atoms/manifests/manifest.jsonl`
- **Type**: JSONL file
- **Entries**: 14,852
- **Purpose**: Atom manifest/index

---

### Knowledge Graph

#### 1. Graph DuckDB
- **Path**: `Primitive/system_elements/holds/knowledge_graph/graph.duckdb`
- **Type**: DuckDB database
- **Tables**:
  - `nodes`: 1,532 rows
    - Columns: node_id, label, label_normalized, entity_type, aliases, etc.
  - `edges`: 1,556 rows
    - Columns: edge_id, subject_id, subject_label, predicate, predicate_normalized, object_id, object_label, etc.
  - `statements`: 0 rows (raw statements before parsing)
- **Purpose**: Graph-based knowledge storage with node/edge deduplication

#### 2. Statements JSONL
- **Path**: `Primitive/system_elements/holds/knowledge_graph/intake/statements.jsonl`
- **Type**: JSONL file
- **Entries**: 10,475
- **Schema**: statement_id, raw_text, subject, subject_type, predicate, predicate_lemma, object, object_type, source_atom_id, parsed_at
- **Purpose**: Raw statements for parsing into nodes/edges

#### 3. Nodes JSONL
- **Path**: `Primitive/system_elements/holds/knowledge_graph/processed/nodes.jsonl`
- **Type**: JSONL file
- **Entries**: 1,532
- **Purpose**: Processed nodes export

#### 4. Edges JSONL
- **Path**: `Primitive/system_elements/holds/knowledge_graph/processed/edges.jsonl`
- **Type**: JSONL file
- **Entries**: 1,556
- **Purpose**: Processed edges export

---

### Contacts

#### 1. Contacts HOLD2 DuckDB
- **Path**: `Primitive/system_elements/holds/contacts/processed/hold2.duckdb`
- **Type**: DuckDB database
- **Table**: `contacts`
- **Rows**: 1,578
- **Schema**: contact_id, display_name, first_name, last_name, organization, primitive, nickname, category_code, relationship_category, notes, is_business, created_at, updated_at, synced_from_bq_at, synced_to_bq_at, _dirty
- **Accessed By**: Primitive App (`contactService.ts`)
- **BigQuery Sync**: `identity.contacts_master`
- **Purpose**: Local contact storage with bidirectional BigQuery sync

---

### Documents

#### 1. Documents HOLD1 DuckDB
- **Path**: `Primitive/system_elements/holds/documents/intake/hold1.duckdb`
- **Type**: DuckDB database
- **Table**: `documents`
- **Rows**: 6,859
- **Schema**: document_id, source_path, source_type, content, content_hash, etc.
- **Purpose**: Intake document storage

#### 2. Documents HOLD1 JSONL
- **Path**: `Primitive/system_elements/holds/documents/intake/hold1.jsonl`
- **Type**: JSONL file
- **Entries**: 9,256
- **Purpose**: Intake documents (JSONL format)

---

### Identity

#### 1. ID Registry DuckDB
- **Path**: `Primitive/system_elements/holds/identity/processed/id_registry.duckdb`
- **Type**: DuckDB database
- **Table**: `id_registry`
- **Rows**: 1 (test entry)
- **Schema**: entity_id, entity_type, generation_method, context_data, stable, first_generated_at, first_requestor, generation_count, status, created_at, updated_at, source_system, parent_entity_id, persona_name
- **Purpose**: Local ID registry (HOLD₂)

#### 2. ID Registry JSONL
- **Path**: `Primitive/system_elements/holds/identity/intake/id_registry.jsonl`
- **Type**: JSONL file
- **Entries**: 1 (test entry)
- **Schema**: Same as DuckDB
- **Purpose**: ID registry intake (HOLD₁) - syncs to BigQuery `identity.id_registry`
- **Accessed By**: Identity Service (`register_id()`, `sync_to_bigquery()`)

---

### Framework

#### 1. Organism State DuckDB
- **Path**: `Primitive/system_elements/holds/framework/processed/organism_state.duckdb`
- **Type**: DuckDB database
- **Table**: `organism_state`
- **Rows**: 1
- **Schema**: state_id, timestamp, health_status, services_status, metrics, etc.
- **Purpose**: Framework service organism state storage

---

### Frontmatter

#### 1. Frontmatter Tracking DuckDB
- **Path**: `Primitive/system_elements/holds/frontmatter/processed/hold2.duckdb`
- **Type**: DuckDB database
- **Table**: `frontmatter_tracking`
- **Rows**: 25
- **Schema**: file_path, doc_title, doc_type, stamped_at, run_id
- **Purpose**: Track documents with frontmatter

---

### Analysis

#### 1. Analysis Results DuckDB
- **Path**: `Primitive/system_elements/holds/analysis/processed/hold2.duckdb`
- **Type**: DuckDB database
- **Table**: `analysis_results`
- **Rows**: 4
- **Schema**: analysis_id, timestamp, category, metrics, summary, etc.
- **Purpose**: Analysis service results

---

### Moments

#### 1. Detected Moments JSONL
- **Path**: `Primitive/system_elements/holds/moments/detected_moments.jsonl`
- **Type**: JSONL file
- **Entries**: 505
- **Schema**: moment_id, message_id, conversation_id, timestamp, moment_type, confidence, signatures_found, evidence, enrichment_data, detected_at
- **Purpose**: Detected moments from conversations

---

### Trinity Matching

#### 1. Trinity Matches DuckDB
- **Path**: `Primitive/system_elements/holds/trinity_matching/processed/matches.duckdb`
- **Type**: DuckDB database
- **Table**: `trinity_matches`
- **Rows**: 10
- **Schema**: match_id, entity_id, atom_id, score, match_type, etc.
- **Purpose**: Trinity matching results

#### 2. Trinity Entities JSONL
- **Path**: `Primitive/system_elements/holds/trinity_matching/intake/entities.jsonl`
- **Type**: JSONL file
- **Entries**: 430
- **Schema**: entity_id, text, content_date, keybert_top_keyword, goemotions_primary_emotion, bertopic_topic_id
- **Purpose**: Entities for trinity matching

---

### Truth Atoms

#### 1. Truth Atoms DuckDB
- **Path**: `Primitive/system_elements/holds/truth_atoms/truth_atoms.duckdb`
- **Type**: DuckDB database
- **Table**: `knowledge_atoms`
- **Rows**: 90
- **Schema**: atom_id, content, atom_type, confidence, source_agent, etc.
- **Purpose**: Truth service knowledge atoms

---

### Model Gateway

#### 1. Prompts DuckDB
- **Path**: `Primitive/system_elements/holds/model_gateway/prompts/prompts.duckdb`
- **Type**: DuckDB database
- **Table**: `prompts`
- **Rows**: 40
- **Schema**: function_name, variant, template, prompt_type, description, etc.
- **Purpose**: Model gateway prompt templates

---

### Pattern Analysis

#### 1. Pattern Analysis DuckDB
- **Path**: `data/local/pattern_analysis.duckdb`
- **Type**: DuckDB database
- **Tables**:
  - `pattern_definitions`: 85 rows
  - `pattern_occurrences`: 251,383 rows
  - `pattern_stats`: 21,771 rows
  - `scan_runs`: 4 rows
  - `scripts`: 3,025 rows
  - `test_scripts`: 0 rows
- **Accessed By**: Primitive App server (`queryPrimitives()`)
- **Purpose**: Code pattern analysis and AST patterns

---

### Registries

#### 1. Schema Registry
- **Path**: `Primitive/system_elements/schema_registry/*.json`
- **Type**: JSON files (11 files)
- **Files**:
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
- **Accessed By**: Daemon endpoint `/registry/primitives`
- **Purpose**: System schema definitions (primitive registry)

#### 2. Service Registry
- **Path**: `Primitive/system_elements/service_registry/registry.json`
- **Type**: JSON file
- **Services**: 4 (model_gateway_service, recommendation_service, knowledge_graph_service, script_service)
- **Purpose**: Service definitions

#### 3. Central Services Registry
- **Path**: `src/services/central_services/registry.json`
- **Type**: JSON file
- **Status**: DEPRECATED (replaced by SYSTEM_VERSION_CATALOG.jsonl)
- **Services**: 13+ services with status, HOLD paths, migration status
- **Purpose**: Central services registry (legacy)

#### 4. SYSTEM_VERSION_CATALOG
- **Path**: `Primitive/migrations/SYSTEM_VERSION_CATALOG.jsonl`
- **Type**: JSONL file
- **Purpose**: Single source of truth for component registry and migration status
- **Schema**: component, path, purpose, status, retention, category, registered_at, version, registry_name, registry_status, phase, exhale, inhale, hold1, hold2, produces_atoms, produces_edges, registered, registry_version, last_updated

---

### Governance

#### 1. Backlog JSONL
- **Path**: `architect_central_services/src/architect_central_services/governance/intake/backlog.jsonl`
- **Type**: JSONL file
- **Accessed By**: Primitive App server
- **Purpose**: Backlog items for governance

#### 2. Perspectives JSONL
- **Path**: `architect_central_services/src/architect_central_services/governance/intake/perspectives.jsonl`
- **Type**: JSONL file
- **Accessed By**: Primitive App server
- **Purpose**: Perspective data for governance

---

### Logs

#### 1. Daemon Log
- **Path**: `Primitive/logs/current/daemon.log`
- **Type**: Text log
- **Lines**: 0
- **Accessed By**: Terminal App, Primitive App
- **Purpose**: Daemon operation logs

#### 2. Daemon Error Log
- **Path**: `Primitive/logs/current/daemon_error.log`
- **Type**: Text log
- **Lines**: 66
- **Size**: 5.9 KB
- **Accessed By**: Terminal App, Primitive App
- **Purpose**: Daemon error logs

#### 3. Healthcheck Log
- **Path**: `Primitive/logs/current/healthcheck.log`
- **Type**: Text log
- **Lines**: 0
- **Accessed By**: Terminal App
- **Purpose**: Health check operation logs

#### 4. Healthcheck Error Log
- **Path**: `Primitive/logs/current/healthcheck_error.log`
- **Type**: Text log
- **Lines**: 235
- **Size**: 23.1 KB
- **Accessed By**: Terminal App
- **Purpose**: Health check error logs

---

### BigQuery Datasets

#### 1. UNIFIED_DEEP_HOLD
- **Project**: `llama-pro-global`
- **Dataset**: `core_metabolism`
- **Type**: Unified
- **Status**: Active mirroring
- **Accessed By**: Primitive App (`cloudService.ts`)
- **Purpose**: Unified deep storage

#### 2. LOCAL_INSTANCE_MIRROR
- **Project**: `llama-pro-local`
- **Dataset**: `instance_hold`
- **Type**: Individual
- **Status**: Active mirroring
- **Accessed By**: Primitive App (`cloudService.ts`)
- **Purpose**: Local instance mirror

#### 3. AWS_COLD_STORAGE
- **Project**: `llama-vault`
- **Dataset**: `s3-archive`
- **Type**: Unified
- **Status**: Idle mirroring
- **Accessed By**: Primitive App (`cloudService.ts`)
- **Purpose**: AWS cold storage archive

#### 4. Identity Registry
- **Project**: `flash-clover-464719-g1`
- **Dataset**: `identity`
- **Table**: `id_registry`
- **Rows**: 65,350+
- **Accessed By**: Identity Service
- **Purpose**: Entity ID registry (cloud storage)

#### 5. Contacts Master
- **Project**: `flash-clover-464719-g1`
- **Dataset**: `identity`
- **Table**: `contacts_master`
- **Accessed By**: Contacts Service
- **Purpose**: Master contacts table (cloud storage)

---

### Browser Storage (Primitive App)

#### 1. Primitives Table
- **Location**: Browser DuckDB WASM (in-memory)
- **Type**: DuckDB table
- **Schema**: id, name, category, last_active
- **Purpose**: Primitive entries for UI

#### 2. Atoms Table
- **Location**: Browser DuckDB WASM (in-memory)
- **Type**: DuckDB table
- **Schema**: id, type, content, source, timestamp, vector (1024-dim), hash
- **Purpose**: Knowledge atoms with vector embeddings for RAG

#### 3. External Knowledge Table
- **Location**: Browser DuckDB WASM (in-memory)
- **Type**: DuckDB table
- **Schema**: id, source_url, source_title, title, summary, relevance_to_me, timestamp, hash
- **Purpose**: External knowledge items

#### 4. Lenses Perspectives Table
- **Location**: Browser DuckDB WASM (in-memory)
- **Type**: DuckDB table
- **Schema**: id, category, lens, perspective, last_updated, hash
- **Purpose**: Lens perspectives

#### 5. Thresholds Table
- **Location**: Browser DuckDB WASM (in-memory)
- **Type**: DuckDB table
- **Schema**: id, type, label, description, value, timestamp, message_id
- **Purpose**: Threshold crossings

---

## 🎯 Key Findings

### Primitive Registry Location
**The primitive registry is in**: `Primitive/system_elements/schema_registry/*.json`

This is accessed by:
- Daemon endpoint: `/registry/primitives`
- Terminal App: Via `TerminalClient.getPrimitives()`
- Primitive App: Via daemon API (proxied)

### Total Dataset Count
- **DuckDB Databases**: 25+
- **JSONL Files**: 15+
- **JSON Registry Files**: 15+
- **Log Files**: 4
- **BigQuery Datasets**: 5
- **Browser Tables**: 5
- **Total**: 70+ data sources

### Most Important Datasets
1. **Schema Registry** (`Primitive/system_elements/schema_registry/`) - **THIS IS THE PRIMITIVE REGISTRY**
2. **SYSTEM_VERSION_CATALOG** (`Primitive/migrations/SYSTEM_VERSION_CATALOG.jsonl`) - Component registry
3. **Knowledge Graph** (`knowledge_graph/graph.duckdb`) - 1,532 nodes, 1,556 edges
4. **Pattern Analysis** (`data/local/pattern_analysis.duckdb`) - 251,383 pattern occurrences
5. **Identity Registry** (BigQuery + local) - Entity ID tracking

---

## 📝 Notes

- All HOLD directories follow the pattern: `Primitive/system_elements/holds/{service_name}/`
- HOLD₁ = intake (raw data)
- HOLD₂ = processed (transformed data)
- Most services have both DuckDB and JSONL versions
- BigQuery is used for cloud storage and system-wide tracking
- Browser DuckDB is ephemeral (in-memory, lost on refresh)
- Server DuckDB is persistent (file-based)
