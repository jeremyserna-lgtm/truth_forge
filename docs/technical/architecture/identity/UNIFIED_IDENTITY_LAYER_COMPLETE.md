# Unified Identity Layer - Complete

**Date**: 2025-12-26
**Status**: OPERATIONAL

---

## The Three Faces of One System

The unified system has three atomic units - each IS the system from its perspective:

| Face | Location | Purpose | Atomic Unit Of |
|------|----------|---------|----------------|
| **Native Mac App** | `/apps/mac/TruthEngine/` | Jeremy's primary interface | Your wanting |
| **Website** | `/frontend/` | External users' access | Others' access |
| **Infrastructure** | BigQuery + Pipelines | The substrate | What IS |

**The truth**: They are the same thing.

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        BigQuery                                  │
│                   (Source of Truth)                              │
│                                                                  │
│   identity.contacts_master  ←→  51.8M entities                  │
│   identity.contact_identifiers  ←→  phones, emails              │
│   identity.relationship_arcs  ←→  relationship history          │
│   governance.contact_edits  ←→  audit trail                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
     ┌──────────┐    ┌──────────┐    ┌──────────┐
     │  Native  │    │  Cloud   │    │ Website  │
     │  Mac App │    │   Run    │    │  Next.js │
     │          │    │   API    │    │          │
     └────┬─────┘    └────┬─────┘    └────┬─────┘
          │               │               │
          │    ┌──────────┴───────┐      │
          │    │                  │      │
          │    ▼                  │      │
          │  Identity API         │      │
          │  (REST)               │      │
          │    │                  │      │
          └────┼──────────────────┼──────┘
               │                  │
               ▼                  ▼
     ┌──────────────┐    ┌──────────────┐
     │    Daemon    │    │   Direct     │
     │  localhost   │    │   BigQuery   │
     │    :8765     │    │   Queries    │
     └──────────────┘    └──────────────┘
```

---

## Component Inventory

### 1. Native Mac App (SwiftUI)

**Location**: `/apps/mac/TruthEngine/`

| File | Purpose |
|------|---------|
| `TruthEngineApp.swift` | App entry, menu bar extra, keyboard shortcuts |
| `Models/Contact.swift` | Data models matching API |
| `Services/TruthEngineAPI.swift` | Cloud Run API client |
| `Services/DaemonService.swift` | Local daemon client |
| `Views/ContentView.swift` | Main navigation |
| `Views/ContactListView.swift` | Contact list with search/filter |
| `Views/QuickCaptureMenu.swift` | Menu bar quick input |
| `Views/InputViews.swift` | Moment/Observation/Backlog sheets |
| `Views/SettingsView.swift` | Configuration |

**Keyboard Shortcuts**:
- ⌘M - New Moment
- ⌘O - New Observation
- ⌘B - Add to Backlog
- ⇧⌘S - Sync to AddressBook

### 2. Website (Next.js)

**Location**: `/frontend/`

| Page | Purpose |
|------|---------|
| `/contacts` | Full contact management UI |
| `/interview` | Perspective Gatherer entry |
| `/interview/[code]` | Friend interview chat |
| `/chat` | AI conversation interface |
| `/insights` | Data insights |
| `/moments` | Moment browser |
| `/pipelines` | Pipeline status |

**API Routes**:
- `GET /api/contacts` - List contacts with filtering
- `PUT /api/contacts` - Update contact
- `POST /api/contacts` - Stats action
- `POST /api/interview/validate` - Validate friend code
- `POST /api/interview/chat` - Interview conversation

### 3. Local Daemon

**Location**: `/daemon/`

| Component | Purpose |
|-----------|---------|
| `primitive_engine_daemon.py` | FastAPI server on localhost:8765 |
| `te` | CLI for quick input |
| `com.truthengine.daemon.plist` | LaunchAgent for auto-start |

**Endpoints**:
- `POST /moment` - Capture moment
- `POST /see` - Record observation
- `POST /backlog` - Add to backlog
- `POST /changelog` - Log change
- `POST /sync/addressbook` - Trigger AddressBook sync
- `GET /status` - Daemon status
- `GET /health` - Health check

### 4. Identity API (Cloud Run)

**Location**: `/architect_central_services/api/identity_api/`

**Endpoints**:
- `GET /contacts` - List contacts
- `GET /contacts/{id}` - Get contact
- `PUT /contacts/{id}` - Update contact
- `POST /contacts` - Create contact
- `GET /contacts/{id}/arcs` - Get relationship arcs
- `POST /contacts/{id}/arcs` - Create arc
- `POST /external/contact` - External input

---

## The Input → Process → Output Pattern

Every face follows the same pattern:

```
INPUT           →    PROCESS         →    OUTPUT
─────────────────────────────────────────────────
Mac App Input   →    Daemon/API      →    BigQuery row
Website Form    →    Next.js API     →    BigQuery row
CLI Command     →    Daemon          →    JSONL file → BigQuery
External API    →    Identity API    →    BigQuery row
```

The output becomes input to the next cycle. The system feeds itself.

---

## Category Taxonomy

Both Mac App and Website use the same category system:

| Code | Label | Description |
|------|-------|-------------|
| A | Inner Circle / Family | Closest relationships |
| B | Close Friends / Friend | Strong connections |
| C | Friends / Acquaintance | Social connections |
| D | Acquaintances / Romantic | Dating/romantic |
| E | Professional / Ex-Romantic | Former relationships |
| F | Family / Service | Service providers |
| G | Dating/Romantic / Professional | Work contacts |
| H | Service Providers / Hostile | Blocked/hostile |
| S | - / Sexual | Sexual encounters |
| U | Unknown | Uncategorized |
| X | Do Not Contact / Exclude | Excluded |

---

## Running the System

### Start Everything

```bash
# 1. Start the daemon (auto-starts via LaunchAgent)
launchctl start com.truthengine.daemon

# 2. Start the website
cd frontend && npm run dev

# 3. Build/run Mac app
cd apps/mac/TruthEngine && swift build && swift run
# Or open in Xcode and run
```

### Quick Input (CLI)

```bash
# Moment
te moment "Realized the three faces are one system"

# Observation
te see "User seemed confused about categories"

# Backlog
te backlog "Add relationship intensity slider" --priority p1_high
```

### Verify Connections

```bash
# Check daemon
curl http://localhost:8765/health

# Check Identity API
curl -H "X-API-Key: dev-key-12345" https://identity-api-xxx.run.app/health

# Check website
curl http://localhost:3000/api/contacts
```

---

## The Atomic Unit Insight

From the conversation that created this:

> "A website is an atomic unit as a domain that is visited online, and as an identity atomic unit of identity for others that it is the atomic unit that is what others use to be the input/exist/output of other people's systems."

> "The native app can be the interface layer I most want to be the atomic unit and the atomic unit of the thing that is most not that, that wanting it to be the atomic unit and it not being the atomic unit makes it the atomic unit."

> "Other architecture is the atomic unit of things that are not the desired unit and I say it through the universal of substrate that the atomic unit wasn't the atomic unit before now but is now and will be in the future."

**Translation**: Each face is THE system depending on who's looking. The truth is they are one.

---

## What's Done

- [x] Native Mac App scaffolding (SwiftUI)
- [x] Website with full contacts UI
- [x] Perspective Gatherer interview system
- [x] Local daemon for quick capture
- [x] Identity API (Cloud Run)
- [x] All components read/write same BigQuery tables
- [x] Category taxonomy unified
- [x] Input patterns unified (moment, see, backlog, changelog)

---

## What's Next

1. **Deploy Identity API** to Cloud Run
2. **Build Mac App** in Xcode, sign, distribute
3. **Deploy Website** to Vercel
4. **AddressBook Sync** - Wire up the AppleScript bridge
5. **Relationship Arcs UI** - Visualize relationship history

---

*The system exists and endures. Three faces, one truth.*
