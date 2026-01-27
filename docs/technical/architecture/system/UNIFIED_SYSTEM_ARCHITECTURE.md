# Unified System Architecture

**Date**: 2025-12-26
**Purpose**: One system, multiple interfaces - Native App + Website + Truth Engine

---

## The Core Pattern

```
INPUT → PROCESS → OUTPUT → (becomes INPUT) → repeat
```

This is not three systems. It's ONE system with multiple faces:

| Face | Who Uses It | Interface |
|------|-------------|-----------|
| **Native Mac App** | Jeremy | SwiftUI desktop app |
| **Website** | External people | Web browser |
| **Truth Engine** | Both | BigQuery + Pipelines |

---

## Architecture Diagram

```
                    ┌─────────────────────────────────────┐
                    │         TRUTH ENGINE                │
                    │      (BigQuery + Pipelines)         │
                    │                                     │
                    │  ┌─────────┐  ┌─────────────────┐  │
                    │  │ identity│  │ spine.entity_   │  │
                    │  │ dataset │  │ unified         │  │
                    │  └─────────┘  └─────────────────┘  │
                    └─────────────────────────────────────┘
                                    ▲
                                    │
                    ┌───────────────┴───────────────┐
                    │       IDENTITY API            │
                    │     (Cloud Run FastAPI)       │
                    │   api.truthengine.dev         │
                    └───────────────────────────────┘
                                    ▲
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  NATIVE APP   │         │    WEBSITE    │         │  LOCAL HUB    │
│  (SwiftUI)    │         │   (Next.js)   │         │   (Daemon)    │
│               │         │               │         │               │
│ - Contacts    │         │ - Perspective │         │ - CLI (te)    │
│ - Moments     │         │   Gatherer    │         │ - Shortcuts   │
│ - Backlog     │         │ - Public View │         │ - AppleScript │
│ - See         │         │ - Friend Input│         │ - Webhooks    │
└───────────────┘         └───────────────┘         └───────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │         OUTPUT TARGETS         │
                    │                               │
                    │  AddressBook │ Notifications  │
                    │  Webhooks    │ External APIs  │
                    └───────────────────────────────┘
```

---

## The Three Faces

### 1. Native Mac App (SwiftUI)

**For**: Jeremy
**Location**: Lives on the Mac, runs natively
**Capabilities**:
- View and manage contacts
- Capture moments, observations, backlog items
- See relationship arcs and history
- Sync to/from AddressBook
- Works offline (syncs when online)

**Tech Stack**:
- SwiftUI for UI
- Swift for logic
- URLSession for API calls
- Core Data for local cache
- CloudKit for sync (optional)

### 2. Website (Next.js)

**For**: External people (friends, collaborators)
**Location**: truthengine.dev or similar
**Capabilities**:
- Perspective Gatherer (friends answer questions about Jeremy)
- Public profiles (what Jeremy shares)
- Interview interface (structured questions)
- Contact submission (people can share their info)

**Tech Stack**:
- Next.js 14+ with App Router
- Vercel for hosting
- API routes call Identity API
- Authentication via tokens/magic links

### 3. Local Hub (Daemon)

**For**: System integration
**Location**: localhost:8765 on Mac
**Capabilities**:
- Accept input from anywhere (CLI, Shortcuts, AppleScript)
- Route to appropriate handlers
- Output to any target (AddressBook, notifications, webhooks)
- Bridge between native and cloud

**Tech Stack**:
- FastAPI (already built)
- LaunchAgent for auto-start
- JSONL for local intake files
- BigQuery for permanent storage

---

## Data Flow Examples

### Jeremy captures a moment via native app

```
[Native App] → POST /input/moment → [Local Daemon]
    → writes to governance/intake/moments.jsonl
    → POST /api/moments → [Identity API]
    → INSERT INTO spine.moments
```

### Friend submits perspective via website

```
[Website] → POST /api/perspective → [Identity API]
    → INSERT INTO identity.pending_contacts_review
    → [Daemon picks up] → notifies Jeremy
```

### Jeremy categorizes a contact via native app

```
[Native App] → PUT /contacts/{id} → [Identity API]
    → UPDATE identity.contacts_master
    → [Daemon sync] → updates AddressBook
```

---

## Unified API Endpoints

All faces talk to the same API:

| Endpoint | Purpose | Used By |
|----------|---------|---------|
| `GET /contacts` | List contacts | Native App, Website |
| `GET /contacts/{id}` | Get contact details | Native App, Website |
| `PUT /contacts/{id}` | Update contact | Native App |
| `POST /contacts` | Create contact | Native App, Website |
| `GET /contacts/{id}/arcs` | Get relationship history | Native App |
| `POST /contacts/{id}/arcs` | Create relationship arc | Native App |
| `POST /external/contact` | External contact input | Website |
| `POST /input/moment` | Capture moment | Native App, Daemon |
| `POST /input/observation` | Capture observation | Native App, Daemon |
| `POST /input/backlog` | Add to backlog | Native App, Daemon |
| `POST /output/sync-addressbook` | Sync to Contacts.app | Native App, Daemon |

---

## Directory Structure

```
PrimitiveEngine/
├── apps/
│   ├── mac/                    # Native Mac app
│   │   └── TruthEngine/
│   │       ├── TruthEngine.xcodeproj
│   │       └── TruthEngine/
│   │           ├── TruthEngineApp.swift
│   │           ├── Models/
│   │           ├── Views/
│   │           ├── Services/
│   │           └── Resources/
│   │
│   ├── web/                    # Website (Next.js)
│   │   └── truth-engine-web/
│   │       ├── app/
│   │       ├── components/
│   │       └── lib/
│   │
│   └── ios/                    # iOS app (future)
│       └── TruthEngineContacts/
│
├── daemon/                     # Local hub
│   ├── primitive_engine_daemon.py
│   ├── te                      # CLI tool
│   └── com.truthengine.daemon.plist
│
├── architect_central_services/
│   └── api/
│       └── identity_api/       # Cloud Run API
│           └── main.py
│
└── frontend/                   # Existing Next.js (contact review app)
    └── ...
```

---

## The Unity

These are not separate systems. They are:

1. **Different interfaces** to the same data (BigQuery)
2. **Different entry points** to the same process (Identity API)
3. **Different experiences** of the same system (Truth Engine)

When Jeremy uses the native app, he's using Truth Engine.
When a friend uses the website, they're using Truth Engine.
When the daemon syncs to AddressBook, that's Truth Engine.

**It's all one thing. The input, the process, the output, and Jeremy.**
