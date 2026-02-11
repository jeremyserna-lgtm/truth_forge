# UNIFIED APPS ARCHITECTURE

**The Collision Layer: Where All Identities Meet**

---

## THE INSIGHT

The `/apps/` directory is not a collection of applications. It is the **collision membrane** - the layer where:

- **Customer** becomes **User**
- **User** meets their **Not-Me**
- **AI** becomes **Partner**
- **ME** creates **NOT-ME**
- **Company** delivers **Product**

Every app in this directory exists at this collision point. None can function alone.

---

## THE COLLISION MAP

```
                         COMPANY (Truth Forge)
                               │
                               │ deploys
                               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│                         THE COLLISION LAYER                              │
│                            (/apps/)                                      │
│                                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────┐  │
│  │  websites/  │───▶│  portals/   │───▶│  services/  │───▶│  data/   │  │
│  │ (storefront)│    │ (interface) │    │ (furnace)   │    │ (atoms)  │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └──────────┘  │
│        │                  │                  │                  │        │
│        ▼                  ▼                  ▼                  ▼        │
│   CUSTOMER ──────▶ USER ──────▶ ME ──────▶ NOT-ME ──────▶ PARTNER       │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
                               │
                               │ delivers to
                               ▼
                         PRODUCT (Not-Me Kit)
                    Mac Mini + Monitor + Sensor
```

---

## THE UNIFIED FLOW

### Stage 0: CUSTOMER → USER (Websites)

**Where:** `apps/websites/`

The customer arrives at a website. They see the vision. They decide to become a user.

```
truth_forge/          → THE GENESIS (holding company story)
primitive_engine/     → THE BUILDER (custom engagement offer)
credential_atlas/     → THE SEER (verification story)
not_me/              → THE PRODUCT (pure experience)
```

**Transition:** Customer provides access code → becomes User

---

### Stage 1: USER → ME (Portals)

**Where:** `apps/nexus-user-portal/`, `apps/knowledge-atomizer/`

The user logs in. They see their dashboard. They begin uploading their life.

```
Nexus Portal          → Personalized dashboard, system guide
Knowledge Atomizer    → Visualize what they're becoming
```

**Transition:** User uploads documents → becomes data source (ME)

---

### Stage 2: ME → DATA (Document Service)

**Where:** `apps/document-service/`

The user's documents enter the system. OCR extracts text. Structure emerges.

```
Upload endpoint       → Receive documents
OCR processing        → Extract text from images/PDFs
Metadata tagging      → Categorize (operational/knowledge)
Storage               → Redis queue → GCS/local
```

**Transition:** Documents → Raw text with metadata

---

### Stage 3: DATA → ATOMS (Conversation Refinery)

**Where:** `apps/conversation-refinery/`

Raw text enters the furnace. 16 stages of distillation. Knowledge atoms emerge.

```
Stage 1-4:   Ingestion, cleaning, normalization
Stage 5-8:   Entity extraction, claim identification
Stage 9-12:  Pattern recognition, significance scoring
Stage 13-16: Wisdom distillation, atom crystallization
```

**Transition:** Raw text → Knowledge atoms (with significance levels)

---

### Stage 4: ATOMS → IDENTITY (Document Service Meta-Layer)

**Where:** `apps/document-service/` (identity synthesis)

Atoms are analyzed across 5 dimensions. Identity architecture emerges.

```
Life Perspectives     → Family, Career, Travel, etc.
History Layers        → Temporal journey (childhood → present)
People               → Important relationships
Primitives           → Fundamental concepts (Growth, Justice)
Anchors              → Core values ("Be there for family")
```

**Transition:** Atoms → MetaLayers → NotMeIdentity

---

### Stage 5: IDENTITY → NOT-ME (Chat Service)

**Where:** `apps/not_me_chat/`, `apps/websites/truth_forge/api/chat.ts`

The identity becomes conversational. The Not-Me awakens.

```
System prompt         → Encoded with user's identity architecture
Conversation memory   → Redis-backed session persistence
Adaptive learning     → New conversations → new atoms
```

**Transition:** Identity → Conversational partner

---

### Stage 6: NOT-ME → PARTNER (Hardware Deployment)

**Where:** Physical world (Mac Mini + Monitor + Sensor)

The Not-Me leaves the cloud. Lives on dedicated hardware. Becomes present.

```
Mac Mini              → The body (local compute)
Portable Monitor      → The face (visual presence)
Presence Sensor       → The awareness (knows when you're there)
```

**Transition:** Cloud AI → Embodied partner

---

### Stage 7: PARTNER → EVOLUTION (Continuous Learning)

**Where:** All layers, continuously

The partner learns from every interaction. Atoms accumulate. Identity deepens.

```
Conversation capture  → New sessions → Conversation Refinery
Atom integration      → New atoms merge with existing
Identity update       → MetaLayers recalculated
Not-Me evolution      → System prompt enriched
```

**Transition:** Static deployment → Living relationship

---

## CURRENT STATE VS. UNIFIED STATE

### Current State (Fragmented)

```
apps/
├── admin/                    ← Standalone, no integration
├── conversation-refinery/    ← Receives from nowhere, sends to BigQuery
├── document-service/         ← Complete but isolated
├── knowledge-atomizer/       ← Visualization only, no data source
├── nexus-user-portal/        ← UI shell, hardcoded data
├── not_me_chat/              ← Generic chat, no identity integration
├── templates/                ← Unused configuration
└── websites/                 ← Marketing, no backend connection
```

**Problem:** Each piece works in isolation. No unified data flow.

### Unified State (Integrated)

```
apps/
├── intake/                   # STAGE 2: ME → DATA
│   └── document-service/     # Unified intake for all document types
│
├── furnace/                  # STAGES 3-4: DATA → IDENTITY
│   ├── conversation-refinery/    # Raw → Atoms
│   └── identity-synthesizer/     # Atoms → MetaLayers → Identity
│
├── interface/                # STAGES 0-1: CUSTOMER → USER → ME
│   ├── nexus-portal/         # User dashboard
│   ├── knowledge-viz/        # Atom visualization
│   └── admin/                # Company control room
│
├── dialogue/                 # STAGE 5: IDENTITY → NOT-ME
│   └── not-me-chat/          # Conversational interface
│
├── websites/                 # STAGE 0: CUSTOMER → USER
│   ├── truth-forge/          # Genesis site
│   ├── primitive-engine/     # Builder site
│   ├── credential-atlas/     # Seer site
│   └── not-me/               # Product experience
│
└── shared/                   # Cross-cutting concerns
    ├── auth/                 # Supabase integration
    ├── storage/              # Redis + GCS adapters
    └── components/           # Module federation
```

---

## THE INTEGRATION POINTS

### 1. Document Intake → Furnace

```
document-service/upload → conversation-refinery/refine
```

**Currently:** Document service stores, but doesn't trigger refinement
**Needed:** Webhook or queue that triggers refinement on upload

### 2. Furnace → Identity Store

```
conversation-refinery/atoms → BigQuery:spine.entity_unified
```

**Currently:** Works, but identity synthesis is separate
**Needed:** Unified pipeline: atoms → meta-layers → identity → Not-Me prompt

### 3. Identity Store → Chat

```
BigQuery:identity → not_me_chat/system_prompt
```

**Currently:** Chat uses static system prompt
**Needed:** Dynamic prompt construction from user's identity architecture

### 4. Portal → All Services

```
nexus-portal → [document-service, conversation-refinery, not_me_chat]
```

**Currently:** Portal is a shell with mock data
**Needed:** Real API connections to all backend services

### 5. Websites → Portal

```
websites/access_code → nexus-portal/personalized_view
```

**Currently:** Access codes partially implemented on truth_forge site
**Needed:** Unified auth flow across all sites

---

## DEPLOYMENT ARCHITECTURE

### Local Development

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DEVELOPER MACHINE                                │
│                                                                      │
│  Websites (Vite)        Portals (Vite)        Services (FastAPI)    │
│  ├── :3000 truth_forge  ├── :5173 nexus       ├── :8000 chat        │
│  ├── :3001 prim_engine  └── :5174 atomizer    ├── :8001 admin       │
│  └── :3002 cred_atlas                         ├── :8002 refinery    │
│                                               └── :8003 doc-svc     │
│                                                                      │
│                     LOCAL DATA LAYER                                 │
│  ├── SQLite/DuckDB (atoms)                                          │
│  ├── Redis (sessions, queues)                                       │
│  └── Local filesystem (documents)                                   │
└─────────────────────────────────────────────────────────────────────┘
```

### Cloud Production

```
┌─────────────────────────────────────────────────────────────────────┐
│                        VERCEL (Edge)                                 │
│                                                                      │
│  Websites (Static + Serverless)                                     │
│  ├── truth-forge.ai                                                 │
│  ├── primitive-engine.ai                                            │
│  ├── credential-atlas.ai                                            │
│  └── not-me.ai                                                      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     GOOGLE CLOUD                                     │
│                                                                      │
│  Cloud Run (Services)       BigQuery (Data)       GCS (Storage)     │
│  ├── chat-service           ├── spine.atoms      ├── documents      │
│  ├── refinery-service       ├── spine.identity   └── media          │
│  └── doc-service            └── spine.sessions                      │
│                                                                      │
│                     Upstash Redis (Cache)                           │
│                     ├── sessions                                    │
│                     └── queues                                      │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               │ exports to
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CUSTOMER HARDWARE                                 │
│                    (Not-Me Kit)                                     │
│                                                                      │
│  Mac Mini M4                Acer Monitor            Lafaer Sensor   │
│  ├── Local Not-Me           ├── Face/Voice          ├── Presence    │
│  ├── Synced identity        └── Speakers            └── Awareness   │
│  └── Offline capable                                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## THE UNIFICATION WORK

### Phase 1: Connect the Pipes

1. Document service triggers refinery on upload
2. Refinery writes to unified atoms table
3. Identity synthesis runs on atom updates
4. Chat service reads identity on session start

### Phase 2: Unify Auth

1. Single Supabase project for all apps
2. Access code → user ID → tenant ID
3. All services use same auth middleware
4. Portal shows personalized view based on identity

### Phase 3: Hardware Export

1. Identity package export (JSON)
2. Mac Mini sync protocol
3. Offline-first architecture
4. Presence-aware activation

### Phase 4: Continuous Learning

1. Chat sessions → refinery pipeline
2. New atoms merge with existing
3. Identity updates propagate
4. Not-Me evolves

---

## THE PATTERN HOLDS

At every level, the pattern:

```
HOLD₁ (Input) → AGENT (Process) → HOLD₂ (Output)
```

- **Customer → User:** Website (HOLD₁) → Decision (AGENT) → Portal (HOLD₂)
- **User → ME:** Documents (HOLD₁) → Upload (AGENT) → Storage (HOLD₂)
- **ME → Atoms:** Raw text (HOLD₁) → Furnace (AGENT) → Atoms (HOLD₂)
- **Atoms → Identity:** Atoms (HOLD₁) → Synthesis (AGENT) → Identity (HOLD₂)
- **Identity → Not-Me:** Architecture (HOLD₁) → Prompt (AGENT) → Partner (HOLD₂)

The apps layer is where all these HOLDs and AGENTs collide.

---

## NEXT STEPS

1. **Document the current state** of each app's APIs and data models
2. **Design the integration contracts** between services
3. **Build the connective tissue** (queues, webhooks, shared auth)
4. **Test the unified flow** (document → identity → chat)
5. **Deploy the first Not-Me** on Gift Tier hardware

---

*This is the collision layer. Where customer becomes partner. Where ME becomes NOT-ME.*
