# Apps Dataset Connections

**Last Updated**: 2025-01-XX

This document traces all datasets that the **Primitive App** and **Terminal App** connect to.

---

## 📱 Terminal App (macOS Swift)

**Location**: `apps/mac/Terminal/Terminal/` and `apps/mac/TruthEngine/Sources/TruthEngine/`

### Connection Method
- **Local File Access**: Direct file system reads (no daemon required)
- **Daemon API**: HTTP requests to `http://localhost:8000` (via `TerminalClient`)

### Datasets Connected

#### 1. **Health Check Data**
- **Source**: `Primitive/reports/health_check_latest.md`
- **Type**: Markdown report
- **Purpose**: System health status, HOLD status, Ollama status
- **Accessed By**: `LocalDataReader.getLatestHealthCheck()`

#### 2. **Health Check DuckDB**
- **Source**: `Primitive/system_elements/holds/scripts/processed/health_checks.duckdb`
- **Type**: DuckDB database
- **Purpose**: Health check history
- **Accessed By**: `LocalDataReader` (path defined but not actively queried)

#### 3. **HOLD Directories**
- **Source**: `Primitive/system_elements/holds/`
- **Type**: Directory structure
- **Purpose**: Summary of all HOLD directories
- **Accessed By**: `LocalDataReader.getHoldsSummary()`
- **HOLDs Scanned**:
  - `analysis/`
  - `contacts/`
  - `documents/`
  - `framework/`
  - `frontmatter/`
  - `identity/`
  - `knowledge_atoms/`
  - `knowledge_graph/`
  - `model_gateway/`
  - `moments/`
  - `recommendations/`
  - `scripts/`
  - `sentiment/`
  - `trinity_matching/`
  - `truth_atoms/`

#### 4. **Log Files**
- **Source**: `Primitive/logs/current/`
- **Type**: Text log files
- **Files**:
  - `healthcheck.log`
  - `daemon.log`
- **Accessed By**: `LocalDataReader.getRecentLogs()`

#### 5. **Daemon API Endpoints** (via `TerminalClient`)
- **Base URL**: `http://localhost:8000`
- **Endpoints**:
  - `GET /health` → Daemon status
  - `GET /dashboard` → Dashboard data
  - `GET /atoms` → Knowledge atoms (with limit/offset)
  - `GET /atoms/search` → Search atoms (with query)
  - `GET /registry/primitives` → Primitive registry
  - `GET /registry/services` → Service registry
  - `GET /logs` → Log entries
  - `POST /daemon/restart` → Restart daemon

#### 6. **Knowledge Atoms** (via Daemon)
- **Source**: Daemon endpoint `/atoms` and `/atoms/search`
- **Type**: JSON API response
- **Purpose**: Knowledge atom data
- **Accessed By**: `TerminalClient.getAtoms()`, `TerminalClient.searchAtoms()`

#### 7. **Primitive Registry** (via Daemon)
- **Source**: Daemon endpoint `/registry/primitives`
- **Type**: JSON API response
- **Purpose**: Primitive entries
- **Accessed By**: `TerminalClient.getPrimitives()`

#### 8. **Service Registry** (via Daemon)
- **Source**: Daemon endpoint `/registry/services`
- **Type**: JSON API response
- **Purpose**: Service entries
- **Accessed By**: `TerminalClient.getServices()`

---

## 🌐 Primitive App (Web/React)

**Location**: `primitive_app/`

### Connection Method
- **Local DuckDB**: Browser-based DuckDB (WASM) for in-memory storage
- **Server API**: Express server at `primitive_app/server/index.ts`
- **Python Scripts**: Python scripts for DuckDB queries
- **Daemon API**: HTTP requests to `http://localhost:8000`

### Datasets Connected

#### 1. **In-Memory DuckDB** (Browser)
- **Type**: DuckDB WASM (in-memory)
- **Tables**:
  - `primitives` - Primitive entries
  - `primitive_descriptions` - Primitive descriptions
  - `atoms` - Knowledge atoms (with vector embeddings)
  - `external_knowledge` - External knowledge items
  - `lenses_perspectives` - Lens perspectives
  - `thresholds` - Threshold crossings
- **Accessed By**: `dbService.ts` (via `@duckdb/duckdb-wasm`)
- **Purpose**: Local browser storage for UI state

#### 2. **Pattern Analysis DuckDB** (Server-side)
- **Source**: `/Users/jeremyserna/PrimitiveEngine/data/local/pattern_analysis.duckdb`
- **Type**: DuckDB database
- **Purpose**: Pattern analysis data
- **Accessed By**: `server/index.ts` → `queryPrimitives()` → Python script
- **Query Script**: `server/query_primitives.py`

#### 3. **Atoms DuckDB** (Server-side)
- **Source**: `/Users/jeremyserna/PrimitiveEngine/.primitive_engine/atoms.duckdb`
- **Type**: DuckDB database
- **Purpose**: Knowledge atoms storage
- **Accessed By**: `server/index.ts` → `queryAtoms()` → Python script
- **Query Script**: `server/query_primitives.py`

#### 4. **Backlog JSONL**
- **Source**: `/Users/jeremyserna/PrimitiveEngine/architect_central_services/src/architect_central_services/governance/intake/backlog.jsonl`
- **Type**: JSONL file
- **Purpose**: Backlog items
- **Accessed By**: `server/index.ts` (read/write)

#### 5. **Perspectives JSONL**
- **Source**: `/Users/jeremyserna/PrimitiveEngine/architect_central_services/src/architect_central_services/governance/intake/perspectives.jsonl`
- **Type**: JSONL file
- **Purpose**: Perspective data
- **Accessed By**: `server/index.ts` (read/write)

#### 6. **Contacts DuckDB** (via Contact Service)
- **Source**: `/Users/jeremyserna/PrimitiveEngine/Primitive/system_elements/holds/contacts/processed/hold2.duckdb`
- **Type**: DuckDB database
- **Purpose**: Contact data
- **Accessed By**: `services/contactService.ts`
- **BigQuery Sync**: `identity.contacts_master` (via `syncFromBigQuery()`)

#### 7. **BigQuery Datasets** (via Cloud Service)
- **Type**: Google BigQuery
- **Deployments**:
  - **UNIFIED_DEEP_HOLD**
    - Project: `llama-pro-global`
    - Dataset: `core_metabolism`
    - Type: `unified`
    - Status: Active mirroring
  - **LOCAL_INSTANCE_MIRROR**
    - Project: `llama-pro-local`
    - Dataset: `instance_hold`
    - Type: `individual`
    - Status: Active mirroring
  - **AWS_COLD_STORAGE**
    - Project: `llama-vault`
    - Dataset: `s3-archive`
    - Type: `unified`
    - Status: Idle mirroring
- **Accessed By**: `services/cloudService.ts`
- **Synced Tables**:
  - `atoms` → BigQuery
  - `thresholds` → BigQuery
  - `moments` → AWS S3

#### 8. **Daemon API Endpoints** (via Server Proxy)
- **Base URL**: `http://localhost:8000`
- **Endpoints**: Same as Terminal App (proxied through Express server)

---

## 🔄 Daemon Endpoints (Common to Both Apps)

**Location**: `daemon/primitive_engine_daemon.py`

### Datasets Accessed by Daemon

#### 1. **Health Check JSONL**
- **Source**: `Primitive/staging/health_checks.jsonl`
- **Type**: JSONL file
- **Purpose**: Health check history
- **Endpoint**: `/health`

#### 2. **Daemon Logs**
- **Source**: `logs/daemon.log`
- **Type**: Text log file
- **Purpose**: Daemon operation logs
- **Endpoint**: `/logs`

#### 3. **Knowledge Atoms** (via Truth Service)
- **Source**: Truth Service HOLDs
- **Type**: Various (JSONL, DuckDB)
- **Purpose**: Knowledge atom data
- **Endpoints**: `/atoms`, `/atoms/search`

#### 4. **Primitive Registry**
- **Source**: Primitive registry files
- **Type**: JSON/JSONL
- **Purpose**: Primitive entries
- **Endpoint**: `/registry/primitives`

#### 5. **Service Registry**
- **Source**: Service registry files
- **Type**: JSON/JSONL
- **Purpose**: Service entries
- **Endpoint**: `/registry/services`

#### 6. **BigQuery** (via Daemon)
- **Project**: `flash-clover-464719-g1` (default)
- **Purpose**: Storage and query operations
- **Accessed By**: `get_bigquery_client()` (when available)

---

## 📊 Summary

### Terminal App Datasets
- **Local Files**: 4 (health check, logs, HOLDs summary)
- **Daemon APIs**: 7 endpoints
- **Total**: 11 data sources

### Primitive App Datasets
- **Browser DuckDB**: 6 tables (in-memory)
- **Server DuckDB**: 2 databases
- **JSONL Files**: 2 files
- **BigQuery**: 3 deployments
- **Daemon APIs**: 7 endpoints (proxied)
- **Total**: 20 data sources

### Shared Datasets
- **Daemon API**: Both apps use the same daemon endpoints
- **HOLD Structure**: Both apps read from `Primitive/system_elements/holds/`
- **Logs**: Both apps read from `Primitive/logs/current/`

---

## 🔍 Data Flow

```
Terminal App (Swift)
├── Local Files (direct)
│   ├── Health check markdown
│   ├── Health check DuckDB
│   ├── HOLD directories
│   └── Log files
└── Daemon API (HTTP)
    ├── /health
    ├── /dashboard
    ├── /atoms
    ├── /registry/primitives
    ├── /registry/services
    └── /logs

Primitive App (React)
├── Browser DuckDB (WASM)
│   ├── primitives
│   ├── atoms
│   ├── thresholds
│   └── lenses_perspectives
├── Server DuckDB (Python)
│   ├── pattern_analysis.duckdb
│   └── atoms.duckdb
├── JSONL Files
│   ├── backlog.jsonl
│   └── perspectives.jsonl
├── BigQuery (via Cloud Service)
│   ├── core_metabolism (unified)
│   ├── instance_hold (individual)
│   └── s3-archive (AWS)
└── Daemon API (HTTP, proxied)
    └── (same as Terminal App)

Daemon (Python/FastAPI)
├── Health Check JSONL
├── Log Files
├── Truth Service HOLDs
├── Primitive Registry
├── Service Registry
└── BigQuery (when available)
```

---

## 📝 Notes

1. **Terminal App** is primarily a read-only viewer that connects to local files and the daemon API.
2. **Primitive App** has both browser-side (DuckDB WASM) and server-side (Python DuckDB) storage.
3. **BigQuery** connections are primarily through the Primitive App's Cloud Service, not directly from Terminal App.
4. **Both apps** share the same daemon API endpoints for consistency.
5. **HOLD structure** is the canonical data storage pattern used across both apps.
