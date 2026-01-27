# Truth Engine: System Architecture

**Version**: 1.0
**Created**: 2025-12-24
**Parent**: [TRUTH_ENGINE_VISION.md](./TRUTH_ENGINE_VISION.md)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TRUTH ENGINE SYSTEM                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     INTERFACE LAYER (Care)                          │    │
│  │                                                                      │    │
│  │  ┌──────────────────┐      ┌──────────────────┐                     │    │
│  │  │   Desktop App    │      │    Web App       │                     │    │
│  │  │   (Tauri/Mac)    │      │   (Next.js)      │                     │    │
│  │  │                  │      │                  │                     │    │
│  │  │ • Relationships  │      │ • Interviews     │                     │    │
│  │  │ • Analysis       │      │ • Observer Portal│                     │    │
│  │  │ • Operations     │      │ • Shared Views   │                     │    │
│  │  │ • Local cache    │      │                  │                     │    │
│  │  └────────┬─────────┘      └────────┬─────────┘                     │    │
│  │           │                         │                                │    │
│  │           └────────────┬────────────┘                                │    │
│  │                        ▼                                             │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                    API Layer (Next.js)                        │   │    │
│  │  │  /api/relationships  /api/interview  /api/analysis  /api/...  │   │    │
│  │  └────────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     SERVICE LAYER (Meaning)                          │    │
│  │                                                                      │    │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │    │
│  │  │ Central Svcs   │  │ Python Bridge  │  │ LLM Services   │         │    │
│  │  │ (Python)       │  │ (FastAPI)      │  │ (Claude/Gemini)│         │    │
│  │  │                │  │                │  │                │         │    │
│  │  │ • Identity     │  │ • API server   │  │ • Analysis     │         │    │
│  │  │ • Logging      │  │ • BQ queries   │  │ • Generation   │         │    │
│  │  │ • Governance   │  │ • Enrichment   │  │ • Interviews   │         │    │
│  │  │ • Cost tracking│  │                │  │                │         │    │
│  │  └────────────────┘  └────────────────┘  └────────────────┘         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     DATA LAYER (Truth + Heat)                        │    │
│  │                                                                      │    │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │    │
│  │  │ BigQuery       │  │ GCS            │  │ Local SQLite   │         │    │
│  │  │                │  │                │  │ (Desktop only) │         │    │
│  │  │ • spine.*      │  │ • Raw exports  │  │                │         │    │
│  │  │ • identity.*   │  │ • Backups      │  │ • Offline cache│         │    │
│  │  │ • governance.* │  │ • Large files  │  │ • Quick access │         │    │
│  │  │ • ai_coord.*   │  │                │  │                │         │    │
│  │  └────────────────┘  └────────────────┘  └────────────────┘         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     INGESTION LAYER (Truth)                          │    │
│  │                                                                      │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │    │
│  │  │ ChatGPT  │ │ Claude   │ │  Texts   │ │  Zoom    │ │ Contacts │  │    │
│  │  │ Pipeline │ │ Pipeline │ │ Pipeline │ │ Pipeline │ │ Pipeline │  │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Interface Layer

#### Desktop App (Tauri)

**Technology**: Tauri 2.0 + Rust backend + Next.js webview

**Purpose**: Native Mac application for daily operations

**Capabilities**:
- Menu bar presence (always accessible)
- System notifications
- Local file system access
- Background sync with BigQuery
- Offline mode with SQLite cache
- Keyboard shortcuts
- Native window management

**File structure**:
```
desktop/
├── src-tauri/
│   ├── src/
│   │   ├── main.rs              # Entry point
│   │   ├── commands/
│   │   │   ├── mod.rs
│   │   │   ├── relationships.rs # Profile operations
│   │   │   ├── sync.rs          # Background sync
│   │   │   ├── cache.rs         # SQLite operations
│   │   │   └── notifications.rs
│   │   ├── db/
│   │   │   └── schema.rs        # SQLite schema
│   │   └── menu.rs              # Native menu
│   ├── tauri.conf.json
│   └── Cargo.toml
└── README.md
```

**Key commands** (Rust → JavaScript):
```rust
#[tauri::command]
async fn get_relationships(category: Option<String>) -> Result<Vec<Profile>, Error>

#[tauri::command]
async fn sync_with_bigquery() -> Result<SyncResult, Error>

#[tauri::command]
async fn generate_profile(contact_id: String) -> Result<Profile, Error>

#[tauri::command]
async fn update_category(profile_id: String, category: String) -> Result<(), Error>
```

#### Web App (Next.js)

**Technology**: Next.js 14 + React 18 + TypeScript

**Purpose**: Web-accessible features for all audiences

**Deployment**: Vercel (existing: `prj_G7XHKyayhkqIEK9bCE4xV5PE0V8R`)

**Current routes**:
```
/ .................... Landing page
/chat ................ Conversational interface
/insights ............ Pattern visualization
/moments ............. Key moments
/developer-insights .. Development journey
/login ............... Authentication
/signup .............. Registration
```

**New routes to add**:
```
/relationships ............. Relationship list & categorization
/relationships/[id] ........ Individual profile view
/relationships/categorize .. Batch categorization workflow
/relationships/generate .... Profile generation

/interview ................. Enter interview code
/interview/[code] .......... Interview session

/analysis .................. Analysis dashboard
/analysis/timeline ......... Temporal view
/analysis/graph ............ Network view
/analysis/patterns ......... Pattern detection

/ingestion ................. Pipeline status
/ingestion/sources ......... Data source management

/portal .................... Observer portal (future)
```

**File structure additions**:
```
frontend/
├── app/
│   ├── relationships/
│   │   ├── page.tsx
│   │   ├── [id]/
│   │   │   └── page.tsx
│   │   ├── categorize/
│   │   │   └── page.tsx
│   │   └── generate/
│   │       └── page.tsx
│   │
│   ├── interview/
│   │   ├── page.tsx
│   │   └── [code]/
│   │       └── page.tsx
│   │
│   ├── analysis/
│   │   ├── page.tsx
│   │   ├── timeline/
│   │   ├── graph/
│   │   └── patterns/
│   │
│   ├── ingestion/
│   │   ├── page.tsx
│   │   └── sources/
│   │
│   └── api/
│       ├── relationships/
│       │   ├── route.ts
│       │   ├── [id]/route.ts
│       │   ├── categorize/route.ts
│       │   └── generate/route.ts
│       ├── interview/
│       │   ├── route.ts
│       │   └── [code]/route.ts
│       └── analysis/
│           └── route.ts
│
├── components/
│   ├── relationships/
│   │   ├── RelationshipCard.tsx
│   │   ├── ProfileView.tsx
│   │   ├── ProfileEditor.tsx
│   │   ├── CategorySelector.tsx
│   │   └── CategorizationQueue.tsx
│   ├── interview/
│   │   ├── InterviewChat.tsx
│   │   └── InterviewSummary.tsx
│   └── analysis/
│       ├── TimelineView.tsx
│       ├── GraphView.tsx
│       └── PatternCard.tsx
│
└── lib/
    ├── relationships.ts
    ├── profiles.ts
    ├── interview.ts
    └── analysis.ts
```

---

### 2. Service Layer

#### Central Services (Python)

**Location**: `architect_central_services/`

**Already built**:
- Identity service (70+ ID generation functions)
- Logging service (structured logging)
- Governance (policy enforcement, hooks)
- Cost tracking (SessionCostLimiter)
- Configuration (TOML-based)
- BigQuery client (with cost protection)

**Key imports**:
```python
from architect_central_services import (
    get_logger,
    get_current_run_id,
    get_correlation_ids,
    log_event,
    track_cost,
    generate_profile_id,
)
from architect_central_services.core.shared import (
    get_bigquery_client,
    SessionCostLimiter,
)
```

#### Python Bridge (FastAPI)

**Purpose**: HTTP API for frontend to call Python services

**Location**: `services/api/` (new)

**Endpoints**:
```python
# services/api/main.py

from fastapi import FastAPI
from architect_central_services import get_bigquery_client

app = FastAPI(title="Truth Engine API")

@app.get("/api/relationships")
async def list_relationships(category: str = None):
    """List relationship profiles."""
    client = get_bigquery_client()
    # Query identity.relationship_profiles
    ...

@app.post("/api/relationships/{id}/categorize")
async def categorize_relationship(id: str, category: str):
    """Update relationship category."""
    ...

@app.post("/api/profiles/generate")
async def generate_profile(contact_id: str):
    """Generate profile from aggregated data."""
    ...

@app.get("/api/interview/{code}")
async def get_interview_session(code: str):
    """Get interview session by code."""
    ...
```

#### LLM Services

**Claude API** (via Anthropic SDK):
- Profile generation (relationship arc, blind spots)
- Interview facilitation
- Pattern analysis
- Natural language queries

**Gemini** (via Vertex AI):
- Embeddings for semantic search
- Large-scale analysis
- Cost-effective operations

**Integration pattern**:
```python
# lib/llm.py

async def generate_relationship_arc(profile: dict) -> str:
    """Generate narrative relationship arc."""
    prompt = f"""
    Based on this relationship data, write a 2-3 paragraph narrative
    describing the relationship arc from beginning to present...

    {json.dumps(profile)}
    """
    response = await claude.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

---

### 3. Data Layer

#### BigQuery Datasets

| Dataset | Purpose | Key Tables |
|---------|---------|------------|
| `spine` | Entity hierarchy | entity_unified, entity_enrichments |
| `identity` | Identity management | id_registry, relationship_profiles, known_people |
| `governance` | Audit & compliance | process_costs, contact_classifications |
| `ai_coordination` | Agent messaging | agent_sessions, agent_messages |

#### New Tables (to create)

```sql
-- identity.relationship_profiles
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.identity.relationship_profiles` (
  profile_id STRING NOT NULL,
  name STRING NOT NULL,
  category STRING NOT NULL,

  phone STRING,
  email STRING,
  location STRING,

  known_since DATE,
  how_met STRING,
  relationship_type STRING,

  biography JSON,
  communication JSON,
  analysis JSON,
  interview JSON,
  action_items ARRAY<STRING>,

  source STRING NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY category, name
OPTIONS (
  description = "Relationship profiles for identity layer",
  labels = [("system", "primitive_engine"), ("layer", "identity")]
);

-- identity.interview_sessions
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.identity.interview_sessions` (
  session_id STRING NOT NULL,
  profile_id STRING NOT NULL,
  code STRING NOT NULL UNIQUE,
  status STRING NOT NULL,  -- pending, in_progress, completed

  friend_profile JSON,     -- Interview configuration
  messages JSON,           -- Conversation history
  analysis JSON,           -- Accumulated analysis
  summary STRING,          -- Final summary

  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY status, profile_id
OPTIONS (
  description = "Perspective gathering interview sessions"
);

-- identity.relationship_categorizations
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.identity.relationship_categorizations` (
  categorization_id STRING NOT NULL,
  profile_id STRING NOT NULL,

  previous_category STRING,
  new_category STRING NOT NULL,

  categorized_by STRING NOT NULL,  -- user, ai_suggested, batch
  ai_confidence FLOAT64,
  ai_reasoning STRING,

  categorized_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
  description = "Audit trail for relationship categorizations"
);
```

#### Local SQLite (Desktop Only)

**Purpose**: Offline cache for desktop app

**Schema**:
```sql
-- Cached relationship profiles
CREATE TABLE profiles (
  profile_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  data JSON NOT NULL,
  synced_at INTEGER NOT NULL,
  modified_locally INTEGER DEFAULT 0
);

-- Pending changes to sync
CREATE TABLE pending_sync (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  operation TEXT NOT NULL,  -- create, update, delete
  table_name TEXT NOT NULL,
  record_id TEXT NOT NULL,
  data JSON,
  created_at INTEGER NOT NULL
);

-- Sync metadata
CREATE TABLE sync_status (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
```

---

### 4. Ingestion Layer

**Existing pipelines**:
| Pipeline | Stages | Status |
|----------|--------|--------|
| ChatGPT Web | 0-16 | Complete |
| Text Messages | 0-12 | In progress |
| Zoom Avatars | 0-3 | Real-time daemon |
| Claude Code | 0 | Assessed |
| Cursor | 0 | Assessed |
| Contacts | Custom | Needs migration |

**Pipeline pattern** (Universal):
```
pipelines/{source}/
├── scripts/stage_{N}/
├── docs/
├── sql/tables/
├── config/
└── tests/
```

---

## Data Flow

### Relationship Categorization Flow

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ Apple Contacts │     │ Conversation   │     │ Text Message   │
│ (raw data)     │     │ Mentions       │     │ Patterns       │
└───────┬────────┘     └───────┬────────┘     └───────┬────────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Aggregation Layer   │
                    │  - Merge by phone    │
                    │  - Enrich with data  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  AI Categorization   │
                    │  - Suggest category  │
                    │  - Explain reasoning │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Human Confirmation  │
                    │  - Accept/Override   │
                    │  - Add notes         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Profile Generation  │
                    │  - Biography         │
                    │  - Relationship arc  │
                    │  - Action items      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  BigQuery Storage    │
                    │  relationship_profiles│
                    └──────────────────────┘
```

### Interview Flow

```
┌────────────────┐
│ Create Profile │
│ + Interview    │
└───────┬────────┘
        │
        ▼
┌────────────────┐     ┌────────────────┐
│ Generate Code  │────▶│ Share Link     │
│ (adam-2024)    │     │ with Friend    │
└────────────────┘     └───────┬────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Friend Opens Link   │
                    │  /interview/adam-2024│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Claude Interview    │
                    │  - Dynamic questions │
                    │  - Listen for signals│
                    │  - Accumulate insight│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Session Complete    │
                    │  - Generate summary  │
                    │  - Attach to profile │
                    │  - Notify Jeremy     │
                    └──────────────────────┘
```

---

## Security & Privacy

### Authentication

**Current**: Custom auth via `/api/auth/` routes

**Future consideration**: Add OAuth for shared access

### Privacy Layers

Access control by audience tier:

```typescript
type PrivacyLayer = 'core' | 'intimate' | 'friend' | 'family' | 'observer' | 'public';

interface AccessControl {
  profile_id: string;
  viewer_id: string;
  layer: PrivacyLayer;
  permissions: {
    view_contact: boolean;
    view_communication: boolean;
    view_analysis: boolean;
    view_interview: boolean;
    edit: boolean;
  };
}
```

### Data Protection

- All BigQuery tables use customer-managed encryption
- No PII in logs (use correlation IDs)
- Interview sessions encrypted at rest
- Friend profiles only accessible via unique codes

---

## Deployment

### Web App

**Platform**: Vercel
**URL**: (existing deployment)
**Config**: `frontend/vercel.json`

**Environment variables**:
```
GOOGLE_APPLICATION_CREDENTIALS_JSON=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
```

### Desktop App

**Build**: `tauri build`
**Distribution**: DMG for Mac
**Updates**: Tauri's built-in updater (future)

### Python Services

**Platform**: Cloud Run (if needed for API)
**Local**: Direct Python execution

---

## Substrate Fluidity: Schema Discovery

The interface layer implements **fluid discovery** - it adapts to what exists in the data layer rather than requiring pre-built UI for each table or view.

### Discovery Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SCHEMA DISCOVERY FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. DISCOVER                    2. ENRICH                   3. RENDER       │
│  ┌─────────────────────┐       ┌─────────────────────┐     ┌────────────┐  │
│  │ INFORMATION_SCHEMA  │       │ interface_registry  │     │ Generic    │  │
│  │                     │       │                     │     │ Components │  │
│  │ • Tables            │──────▶│ • Display names     │────▶│            │  │
│  │ • Views             │       │ • Render hints      │     │ <DataView> │  │
│  │ • Labels            │       │ • Relationships     │     │ <CardGrid> │  │
│  │ • Descriptions      │       │ • Access control    │     │ <Timeline> │  │
│  └─────────────────────┘       └─────────────────────┘     └────────────┘  │
│           │                             │                        │          │
│           │         ┌───────────────────┘                        │          │
│           │         │                                            │          │
│           ▼         ▼                                            ▼          │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         DYNAMIC INTERFACE                             │  │
│  │                                                                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │  │
│  │  │ Relationships│  │   Patterns   │  │  Entities    │  + any new    │  │
│  │  │    View      │  │    View      │  │    View      │    views...   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘               │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Discovery Service

**Location**: `services/api/discovery/` or `frontend/lib/discovery/`

```typescript
// lib/discovery/schema-discovery.ts

import { BigQuery } from '@google-cloud/bigquery';

interface DiscoveredView {
  dataset: string;
  name: string;
  type: 'TABLE' | 'VIEW';
  labels: Record<string, string>;
  description?: string;
  columns: ColumnInfo[];
  registryEntry?: InterfaceRegistryEntry;
}

async function discoverAvailableViews(): Promise<DiscoveredView[]> {
  const client = getBigQueryClient();

  // Step 1: Query INFORMATION_SCHEMA for all tables/views
  const [tables] = await client.query({
    query: `
      SELECT
        table_schema as dataset,
        table_name as name,
        table_type as type
      FROM \`flash-clover-464719-g1\`.INFORMATION_SCHEMA.TABLES
      WHERE table_schema IN ('spine', 'identity', 'governance', 'ai_coordination')
    `
  });

  // Step 2: Enrich with registry metadata
  const [registry] = await client.query({
    query: `SELECT * FROM identity.interface_registry`
  });

  // Step 3: Merge discovered with registry
  return tables.map(table => ({
    ...table,
    registryEntry: registry.find(r =>
      r.dataset === table.dataset && r.table_or_view === table.name
    )
  }));
}
```

### Generic Rendering Components

**Purpose**: Render any discovered view without view-specific code.

```typescript
// components/generic/DataView.tsx

interface DataViewProps {
  source: string;              // "identity.relationship_profiles"
  columns?: string[] | 'auto'; // Which columns to show
  renderType?: RenderType;     // Override auto-detection
  filters?: Record<string, any>;
}

function DataView({ source, columns = 'auto', renderType, filters }: DataViewProps) {
  // 1. Get registry entry for this source
  const { data: registry } = useRegistryEntry(source);

  // 2. Discover schema if not in registry
  const { data: schema } = useSchemaDiscovery(source);

  // 3. Determine columns to display
  const displayColumns = columns === 'auto'
    ? registry?.default_columns || schema?.columns.slice(0, 5)
    : columns;

  // 4. Determine render type
  const type = renderType
    || registry?.render_type
    || inferRenderType(schema);

  // 5. Fetch data
  const { data, isLoading } = useViewData(source, { columns: displayColumns, filters });

  // 6. Render with appropriate component
  switch (type) {
    case 'table':
      return <GenericTable data={data} columns={displayColumns} schema={schema} />;
    case 'cards':
      return <GenericCardGrid data={data} schema={schema} />;
    case 'timeline':
      return <GenericTimeline data={data} schema={schema} />;
    default:
      return <GenericTable data={data} columns={displayColumns} schema={schema} />;
  }
}
```

### Auto-Navigation

The navigation menu is also discovery-driven:

```typescript
// components/navigation/DynamicNav.tsx

function DynamicNav() {
  const { data: views } = useDiscoveredViews();
  const { data: registry } = useInterfaceRegistry();

  // Group views by dataset
  const grouped = groupBy(views, 'dataset');

  return (
    <nav>
      {Object.entries(grouped).map(([dataset, tables]) => (
        <NavSection key={dataset} title={formatDatasetName(dataset)}>
          {tables.map(table => {
            const entry = registry?.find(r => r.table_or_view === table.name);
            return (
              <NavItem
                key={table.name}
                href={`/data/${dataset}/${table.name}`}
                icon={entry?.icon || 'table'}
                label={entry?.display_name || formatTableName(table.name)}
              />
            );
          })}
        </NavSection>
      ))}
    </nav>
  );
}
```

### Adding a New View (No Code Required)

When a new BigQuery view is created:

1. **Automatic discovery**: Interface sees it immediately via INFORMATION_SCHEMA
2. **Optional enrichment**: Add to `interface_registry` for custom display
3. **Automatic navigation**: Appears in nav if registered
4. **Automatic rendering**: Uses generic components based on schema

```sql
-- Example: Create a new view
CREATE VIEW `flash-clover-464719-g1.identity.active_relationships` AS
SELECT * FROM identity.relationship_profiles
WHERE category != 'HISTORICAL';

-- Optionally register with metadata
INSERT INTO identity.interface_registry VALUES (
  'reg_active_rel',
  'identity', 'active_relationships',
  'Active Relationships',
  'Current non-historical relationships',
  'users', '#4CAF50',
  JSON '{"render_type": "cards", "default_columns": ["name", "category", "last_contact"]}',
  JSON '{"related_views": ["identity.relationship_profiles"]}',
  ['operator'],
  true, true,
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);
```

Result: The view appears in the interface, renders as cards, shows the specified columns.

### Seeing the Discovery (Meta-Transparency)

The interface can show its own discovery process:

```
System View: /system/discovery

Available Data Sources
├── Discovering...
│   ├── spine.entity_unified (51.8M rows)
│   ├── identity.relationship_profiles (127 rows)
│   ├── identity.interview_sessions (5 rows)
│   └── [12 more tables]
│
├── Registry Status
│   ├── 8 registered views
│   ├── 7 auto-discovered
│   └── 1 pending registration
│
└── [Register New View] [Refresh Discovery]
```

This implements the design principle: **the interface shows the system operating, including how it discovers what to show.**

---

## Performance Considerations

### BigQuery Optimization

- All tables partitioned by date
- Clustered by frequently-queried columns
- Use `LIMIT` for UI queries
- Cache results in SQLite for desktop

### Frontend Optimization

- Use React Query for data caching
- Pagination for large lists
- Progressive loading for analysis views
- Local SQLite for offline access

### LLM Cost Management

- Use Claude Haiku for simple categorization
- Use Claude Sonnet for profile generation
- Batch operations where possible
- Track costs via `SessionCostLimiter`

---

## Related Documents

- [TRUTH_ENGINE_VISION.md](./TRUTH_ENGINE_VISION.md) - Product vision
- [DATA_MODELS.md](./DATA_MODELS.md) - Complete data schemas
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) - Build phases
