# Truth Engine: Implementation Roadmap

**Version**: 1.0
**Created**: 2025-12-24
**Parent**: [TRUTH_ENGINE_VISION.md](./TRUTH_ENGINE_VISION.md)

---

## Overview

This roadmap defines the phased implementation of the Truth Engine interface layer. The approach prioritizes working features over comprehensive design, with each phase delivering usable functionality.

---

## Backlog Reference

**This roadmap is tracked in the backlog**: See `architect_central_services/docs/BACKLOG.md` item #24 for detailed implementation notes.

The backlog and this roadmap are synchronized. Updates should be reflected in both.

---

## Current State

### Already Built

| Component | Location | Status |
|-----------|----------|--------|
| Entity substrate | `spine.entity_unified` | Production (51.8M entities) |
| Central services | `architect_central_services/` | Production |
| Web frontend | `frontend/` | Production on Vercel |
| Chat interface | `/chat` | Production |
| Insights view | `/insights` | Production |
| Developer insights | `/developer-insights` | Production |
| Perspective gatherer | `tools/perspective_gatherer/` | Working, needs migration |
| Contact review | `tools/contact_review/` | Working Streamlit app |
| Friend profiles | `tools/perspective_gatherer/friends/` | 5 YAML profiles exist |
| Identity layer design | `docs/architecture/IDENTITY_LAYER_ARCHITECTURE.md` | Documented |

### Gaps to Fill

| Gap | Priority | Phase |
|-----|----------|-------|
| Relationship management UI | High | 1 |
| Profile generation | High | 1 |
| Interview migration to frontend | High | 1 |
| Python Bridge (FastAPI) | High | 1 |
| Pattern analysis UI | Medium | 2 |
| Desktop app (Tauri) | Medium | 4 |
| "How is Jeremy" dashboard | Medium | 3 |
| Observer portal | Low | 5 |

---

## Build Order

The dependency chain determines the build order:

```
BigQuery Tables → Python Bridge → Web Routes → Components → Desktop App
       ↓              ↓                ↓
  identity.*    services/api/     frontend/app/
```

Each layer depends on the previous. Don't skip ahead.

---

## Phase 1: Relationship Foundation

**Goal**: Working relationship management in the web app.

**Timeframe**: Foundation priority

### Deliverables

#### 1.1 BigQuery Tables

Create the core tables for relationship data:

```sql
-- Run these in sequence
-- 1. identity.relationship_profiles
-- 2. identity.interview_sessions
-- 3. identity.relationship_categorizations
```

See [DATA_MODELS.md](./DATA_MODELS.md) for complete schemas.

**Verification**:
- [ ] Tables created in BigQuery
- [ ] Clustered by appropriate columns
- [ ] Labels applied

#### 1.2 API Routes

Add to existing `frontend/app/api/`:

```
frontend/app/api/
├── relationships/
│   ├── route.ts              # GET list, POST create
│   ├── [id]/
│   │   └── route.ts          # GET one, PATCH update
│   ├── categorize/
│   │   └── route.ts          # POST categorize
│   └── generate/
│       └── route.ts          # POST generate profile
└── interview/
    ├── route.ts              # GET by code
    ├── [code]/
    │   └── route.ts          # GET session, POST message
    └── complete/
        └── route.ts          # POST complete interview
```

**Verification**:
- [ ] All routes return correct data shapes
- [ ] Error handling works
- [ ] BigQuery queries use `get_bigquery_client()`

#### 1.3 Relationship List Page

New route: `/relationships`

**Features**:
- List all relationship profiles
- Filter by category
- Sort by last contact, name, category
- Quick actions: view, categorize, generate profile

**Components**:
```
frontend/app/relationships/
├── page.tsx                  # Main list view
└── components/
    ├── RelationshipCard.tsx  # Individual card
    ├── CategoryFilter.tsx    # Filter by category
    └── SortSelector.tsx      # Sort options
```

**Verification**:
- [ ] Lists profiles from BigQuery
- [ ] Filters work correctly
- [ ] Cards link to detail pages

#### 1.4 Profile View/Edit Page

New route: `/relationships/[id]`

**Features**:
- View full profile
- Edit any field
- View/add notes
- Manage action items
- Trigger interview
- View interview results

**Components**:
```
frontend/app/relationships/[id]/
├── page.tsx                  # Profile view
└── components/
    ├── ProfileHeader.tsx     # Name, category, contact
    ├── BiographySection.tsx  # Bio details
    ├── AnalysisSection.tsx   # AI analysis
    ├── CommunicationSection.tsx
    ├── InterviewSection.tsx  # Interview status/results
    ├── NotesSection.tsx
    └── ActionItems.tsx
```

**Verification**:
- [ ] All profile fields display
- [ ] Edits save to BigQuery
- [ ] Interview section shows correct state

#### 1.5 Categorization Workflow

New route: `/relationships/categorize`

**Features**:
- Queue of uncategorized contacts
- AI suggests category with reasoning
- User confirms or overrides
- Batch processing option

**Workflow**:
1. Load uncategorized profiles
2. For each: show AI suggestion
3. User confirms/overrides
4. Save categorization
5. Move to next

**Verification**:
- [ ] Queue loads correctly
- [ ] AI suggestions appear
- [ ] Categorizations save with audit trail

#### 1.6 Interview Migration

Migrate `tools/perspective_gatherer/` to main frontend:

**New routes**:
- `/interview` - Code entry page
- `/interview/[code]` - Interview session

**Migration steps**:
1. Copy interview logic to frontend
2. Migrate friend YAML profiles to BigQuery
3. Update Claude prompts for web context
4. Test with existing friend profiles

**Verification**:
- [ ] Code entry works
- [ ] Interview runs in browser
- [ ] Results save to BigQuery

#### 1.7 Python Bridge (FastAPI)

**Location**: `services/api/` (new)

**Purpose**: HTTP API for frontend to call Python services (BigQuery, LLM, central services)

**Endpoints**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/relationships` | GET | List profiles |
| `/api/relationships/{id}` | GET | Get single profile |
| `/api/relationships` | POST | Create profile |
| `/api/relationships/{id}` | PATCH | Update profile |
| `/api/relationships/{id}/categorize` | POST | Update category |
| `/api/profiles/generate` | POST | Generate profile from data |
| `/api/interview/{code}` | GET | Get interview session |
| `/api/interview/{code}/message` | POST | Send interview message |

**Structure**:
```
services/api/
├── main.py                   # FastAPI app
├── routers/
│   ├── relationships.py      # Relationship endpoints
│   ├── profiles.py           # Profile generation
│   └── interview.py          # Interview endpoints
├── models/
│   └── schemas.py            # Pydantic models
└── requirements.txt
```

**Integration with central services**:
```python
from architect_central_services import get_bigquery_client, get_logger
from architect_central_services.core.shared import SessionCostLimiter
```

**Verification**:
- [ ] All endpoints return correct data shapes
- [ ] Uses central services (not direct clients)
- [ ] Cost tracking on LLM operations
- [ ] CORS configured for frontend

---

## Phase 2: Analysis & Profiles

**Goal**: Profile generation and pattern analysis (web only).

**Timeframe**: After Phase 1 stable

### Deliverables

#### 2.1 Profile Generation

New route: `/relationships/generate`

**Features**:
- Aggregate data from multiple sources
- Generate biographical narrative
- Create relationship arc
- Identify blind spots
- Suggest action items

**Data sources to aggregate**:
- Apple Contacts (if linked)
- Text message patterns (if available)
- AI conversation mentions
- Interview results
- Manual notes

**Verification**:
- [ ] Aggregation pulls from all sources
- [ ] Generated profiles are coherent
- [ ] Claude API cost tracked

#### 2.2 Timeline View

New route: `/analysis/timeline`

**Features**:
- Visual timeline of events
- Zoom levels (day, week, month)
- Event markers with details
- Filter by type, theme
- Connect to entities

**Verification**:
- [ ] Timeline renders correctly
- [ ] Events link to entities
- [ ] Zoom/filter works

#### 2.3 Pattern Detection

New route: `/analysis/patterns`

**Features**:
- List detected patterns
- Pattern details with evidence
- Related patterns
- Toggle anonymized view

**Verification**:
- [ ] Patterns display correctly
- [ ] Evidence links work
- [ ] Anonymization works

---

## Phase 3: Intimates Experience

**Goal**: Features for friends/family.

**Timeframe**: After Phase 2 stable

### Deliverables

#### 3.1 "How is Jeremy" Dashboard

New route: `/how-is-jeremy/[access_token]`

**Features**:
- Translated emotional state
- Current focus indicator
- "Good time to reach out?" signal
- What he might need
- What to avoid

**Data pipeline**:
1. Analyze recent messages (24-48h)
2. Detect emotional trajectory
3. Translate to accessible language
4. Generate actionable guidance

**Verification**:
- [ ] State updates regularly
- [ ] Translations are meaningful
- [ ] Access tokens work

#### 3.2 Care Instructions

Add to profile or standalone page.

**Features**:
- What helps when...
- Signs he needs support
- Communication preferences
- Do's and don'ts

**Verification**:
- [ ] Instructions are accurate
- [ ] Editable by Jeremy
- [ ] Accessible to permitted friends

#### 3.3 Reciprocal Input

New route: `/observe/[access_token]`

**Features**:
- Friends can submit observations
- "I noticed..." form
- Pattern submissions
- Optional anonymity

**Verification**:
- [ ] Submissions save correctly
- [ ] Jeremy notified
- [ ] Privacy preserved

---

## Phase 4: Desktop App (Tauri)

**Goal**: Native Mac application for daily operations.

**Timeframe**: After Phase 3 stable

### Deliverables

#### 4.1 Tauri Project Setup

New directory: `desktop/`

**Setup**:
```bash
# Initialize Tauri project
npm create tauri-app@latest desktop
cd desktop
npm install

# Configure for Mac
# Edit src-tauri/tauri.conf.json
```

#### 4.2 Core Features

**Features**:
- Menu bar presence (always accessible)
- Window management
- Load web app in webview
- Background sync with BigQuery
- Local SQLite cache for offline access

#### 4.3 Rust Commands

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

#### 4.4 SQLite Cache

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
  operation TEXT NOT NULL,
  table_name TEXT NOT NULL,
  record_id TEXT NOT NULL,
  data JSON,
  created_at INTEGER NOT NULL
);
```

**Verification**:
- [ ] App builds for Mac
- [ ] Web content loads
- [ ] Menu bar icon works
- [ ] Offline mode functions
- [ ] Sync works correctly

---

## Phase 5: Observer Portal

**Goal**: Public-facing documentation and patterns.

**Timeframe**: After core features stable

### Deliverables

#### 5.1 Observer Portal Landing

New route: `/portal`

**Features**:
- The Story (narrative entry)
- Architecture overview
- Pattern gallery link
- Builder resources link

#### 5.2 Pattern Gallery

New route: `/portal/patterns`

**Features**:
- Anonymized pattern cards
- Searchable/filterable
- Detail views
- Related patterns

#### 5.3 Architecture Documentation

New route: `/portal/architecture`

**Features**:
- System overview
- Data models
- Pipeline patterns
- Cost considerations

#### 5.4 Metrics Dashboard

New route: `/portal/metrics`

**Features**:
- Entity counts
- Pipeline status
- Timeline statistics
- System health

---

## Technical Approach

### Development Pattern

For each feature:

1. **Schema first**: Define BigQuery table (if needed)
2. **API second**: Build API route with tests
3. **UI third**: Build React components
4. **Integration**: Connect everything
5. **Verification**: Run through checklist

### Testing Strategy

```bash
# Unit tests
cd frontend && npm test

# API tests
cd frontend && npm run test:api

# E2E tests (future)
cd frontend && npm run test:e2e
```

### Deployment

**Web (continuous)**:
- Push to main → Vercel deploys automatically
- Preview deploys for PRs

**Desktop (releases)**:
- Tag version → GitHub Actions builds
- DMG uploaded to releases

---

## Definition of Done Per Phase

Each phase is complete when:

- [ ] All features implemented and working
- [ ] Data persists in BigQuery correctly
- [ ] API routes have error handling
- [ ] UI is usable (not necessarily polished)
- [ ] Documentation updated
- [ ] No cost protection violations
- [ ] Tested manually

---

## Dependencies

### Phase 1 Dependencies

| Dependency | Status | Needed For |
|------------|--------|------------|
| BigQuery tables | Not created | All data storage |
| Claude API key | Already have | Profile generation |
| Existing frontend | Production | Extending |

### Phase 2 Dependencies

| Dependency | Status | Needed For |
|------------|--------|------------|
| Tauri CLI | Not installed | Desktop app |
| Rust toolchain | May need | Tauri backend |
| Phase 1 complete | Pending | Building on foundation |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Scope creep | Strict phase boundaries, defer to next phase |
| Cost overruns | SessionCostLimiter on all LLM operations |
| Integration issues | Test early, fail fast |
| Desktop complexity | Start with webview, add native features incrementally |

---

## Success Metrics

| Phase | Success When |
|-------|--------------|
| 1 | Can categorize contacts and view profiles in web app |
| 2 | Can see timeline/patterns, desktop app runs |
| 3 | Friends can see "How is Jeremy" and do interviews |
| 4 | Observer portal is public and useful |

---

## Related Documents

- [TRUTH_ENGINE_VISION.md](./TRUTH_ENGINE_VISION.md) - Overall vision
- [DESIGN_PRINCIPLES.md](./DESIGN_PRINCIPLES.md) - Core design principles
- [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) - Technical architecture
- [DATA_MODELS.md](./DATA_MODELS.md) - Complete schemas
- [AUDIENCE_EXPERIENCES.md](./AUDIENCE_EXPERIENCES.md) - UX design
- [BACKLOG.md](../../architect_central_services/docs/BACKLOG.md#24-product-frontend-implementation) - Detailed implementation notes
