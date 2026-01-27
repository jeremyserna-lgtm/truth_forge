# Web Architecture: Truth Forge Websites

**Created**: 2026-01-26
**Status**: Planning

---

## Overview

Truth Forge centrally manages **four websites** with a **shared AI chat component** (NOT-ME) deployed across all.

```
                    ┌─────────────────────────────────┐
                    │         truth_forge             │
                    │     (Central Management)        │
                    └─────────────────────────────────┘
                                   │
         ┌─────────────┬──────────┼──────────┬─────────────┐
         ▼             ▼          ▼          ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│truth-forge.ai│ │credential-  │ │primitive-   │ │ not-me.ai   │
│             │ │atlas.ai     │ │engine.ai    │ │             │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
       │               │              │               │
       └───────────────┴──────────────┴───────────────┘
                              │
                    ┌─────────────────┐
                    │  NOT-ME Chat    │
                    │ (Shared Component)│
                    │                 │
                    │ ★ Deployed to   │
                    │   ALL 4 sites   │
                    │ ★ Centralized   │
                    │   learning      │
                    └─────────────────┘
```

---

## Domain Registry

| Domain | Purpose | Product |
|--------|---------|---------|
| **truth-forge.ai** | Holding company site | Truth Forge (genesis) |
| **credential-atlas.ai** | Credential verification | Credential Atlas (THE SEER) |
| **primitive-engine.ai** | Architecture services | Primitive Engine (THE BUILDER) |
| **not-me.ai** | AI chat product | NOT-ME (the interface) |

---

## Component Architecture

### 1. NOT-ME Chat (Shared Component)

The AI chat interface that represents the user's "NOT-ME" - their technological extension.

**Key Requirements:**
- Deployable as embeddable component to any website
- Centralized learning persistence (learnings from all sites flow back)
- Consistent UX across all deployments
- Per-site customization (branding, persona, context)

**Current Location**: `apps/frontend/` (Next.js)

**Recommended Location**: `apps/not_me_chat/`

```
apps/not_me_chat/
├── src/
│   ├── components/      # Chat UI components
│   ├── hooks/           # Shared hooks
│   ├── lib/             # Core logic
│   └── styles/          # Theming
├── embed/               # Embeddable build output
│   └── not-me-chat.js   # Single embeddable script
├── package.json
└── README.md
```

**Deployment Model:**
```html
<!-- Embed on any site -->
<script src="https://not-me.ai/embed/not-me-chat.js"></script>
<not-me-chat
  site="credential-atlas"
  api-key="..."
/>
```

### 2. Website Apps (4 sites)

Each website is a separate Next.js application with shared components.

**Recommended Structure:**
```
apps/websites/
├── truth_forge/           # truth-forge.ai
│   ├── app/
│   ├── components/
│   └── package.json
├── credential_atlas/      # credential-atlas.ai
│   ├── app/
│   ├── components/
│   └── package.json
├── primitive_engine/      # primitive-engine.ai
│   ├── app/
│   ├── components/
│   └── package.json
├── not_me/                # not-me.ai
│   ├── app/
│   ├── components/
│   └── package.json
└── shared/                # Shared across all sites
    ├── components/        # Common UI components
    ├── hooks/             # Common hooks
    ├── styles/            # Common styles/themes
    └── lib/               # Common utilities
```

### 3. Primitive App (Admin/Dashboard)

The substantial React application for internal operations.

**Current Location**: `apps/primitive_app/` (41K+ lines in App.tsx alone)

**Purpose**: Internal admin, operations dashboard, NOT a public website

**Recommended Location**: `apps/admin/` or `apps/dashboard/`

---

## Migration Mapping

### Current → Target

| Current | Target | Notes |
|---------|--------|-------|
| `apps/frontend/` | `apps/not_me_chat/` | **Shared chat component** (embeds in all sites) |
| `apps/truth-forge-website/` | `apps/websites/truth_forge/` | truth-forge.ai |
| `apps/credential_atlas/` | `apps/websites/credential_atlas/` | credential-atlas.ai |
| `apps/stage5mind/` | `apps/websites/not_me/` | **not-me.ai** |
| `apps/primitive_app/` | `apps/admin/` | Internal dashboard |
| `apps/primitive_web/` | ARCHIVE | Superseded |
| `apps/truth_engine_web/` | ARCHIVE | Old naming |
| `apps/web/` | DELETE | Single script |
| `apps/primitive-slot-builder/` | **MERGE INTO** `not_me_chat/` | Dynamic prompt builder (dependency) |

### Merge Before Migration

| Source | Merge Into | Components |
|--------|------------|------------|
| `primitive-slot-builder/` | `not_me_chat/` | `SlotPromptBuilder.tsx`, `geminiService.ts` |

### New to Create

| App | Purpose |
|-----|---------|
| `apps/websites/primitive_engine/` | primitive-engine.ai (NEW) |
| `apps/websites/shared/` | Shared components across all 4 sites |

---

## Learning Persistence Architecture

The NOT-ME chat must persist learnings across all site deployments:

```
┌─────────────────────────────────────────────────────────────┐
│                    truth_forge (central)                     │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Learning Persistence Layer              │    │
│  │                                                      │    │
│  │  • Conversations from ALL sites                      │    │
│  │  • User preferences (per-user, cross-site)           │    │
│  │  • Context accumulation                              │    │
│  │  • Federated knowledge                               │    │
│  └─────────────────────────────────────────────────────┘    │
│                            ▲                                 │
│         ┌──────────────────┼──────────────────┐             │
│         │                  │                  │             │
│    ┌────┴────┐       ┌────┴────┐       ┌────┴────┐        │
│    │ TF Chat │       │ CA Chat │       │ PE Chat │        │
│    └─────────┘       └─────────┘       └─────────┘        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow:**
1. User interacts with NOT-ME on credential-atlas.ai
2. Conversation sent to central learning service
3. Learnings available when same user visits primitive-engine.ai
4. NOT-ME "knows" the user across all sites

---

## Deployment Strategy

### Option A: Monorepo with Turborepo/Nx

```
apps/
├── not_me_chat/         # Shared chat (npm package + CDN)
└── websites/
    ├── truth_forge/
    ├── credential_atlas/
    ├── primitive_engine/
    └── not_me/
```

**Pros:** Single repo, shared dependencies, atomic deploys
**Cons:** Larger repo, more complex CI/CD

### Option B: Multi-repo with Shared Package

```
truth_forge/apps/not_me_chat/  → Published as @truth-forge/not-me-chat
truth_forge/apps/websites/     → Each site imports the package
```

**Pros:** Independent deploys, clearer boundaries
**Cons:** Version coordination, dependency management

**Recommendation:** Option A (Monorepo) - simpler for 4 sites + 1 shared component.

---

## Apps to ARCHIVE/DELETE

Based on this architecture, these apps are superseded:

| App | Action | Reason |
|-----|--------|--------|
| `primitive_web/` | ARCHIVE | Superseded by websites structure |
| `truth_engine_web/` | ARCHIVE | Old naming |
| `web/` | DELETE | Single script, not a real app |
| `poc-simple/` | ARCHIVE | POC, not production |
| `ai-conversation-quality/` | EVALUATE | May be testing tool |
| `ai-video-shuffle-extension/` | ARCHIVE | Browser extension, separate concern |
| `ios/` | ARCHIVE | Mobile, separate roadmap |
| `mac/` | ARCHIVE | Desktop, separate roadmap |

**Note:** `primitive-slot-builder/` is NOT archived - it gets **merged into** `not_me_chat/` first.

## Apps KEPT (Active)

| App | Target | Domain |
|-----|--------|--------|
| `frontend/` | `apps/not_me_chat/` | Shared chat component |
| `truth-forge-website/` | `apps/websites/truth_forge/` | truth-forge.ai |
| `credential_atlas/` | `apps/websites/credential_atlas/` | credential-atlas.ai |
| `stage5mind/` | `apps/websites/not_me/` | not-me.ai |
| (NEW) | `apps/websites/primitive_engine/` | primitive-engine.ai |
| `primitive_app/` | `apps/admin/` | Internal dashboard |

---

## Summary

| Category | Count | Apps |
|----------|-------|------|
| **Websites** | 4 | truth-forge.ai, credential-atlas.ai, not-me.ai, primitive-engine.ai |
| **Shared Components** | 1 | NOT-ME Chat (embeddable) |
| **Internal Tools** | 1 | Admin Dashboard (primitive_app) |
| **TOTAL ACTIVE** | **6** | Down from 18 |
| **Archived** | 8+ | Various legacy |

### Source Mapping

| Domain | Source App | Status |
|--------|------------|--------|
| truth-forge.ai | `truth-forge-website/` | EXISTS |
| credential-atlas.ai | `credential_atlas/` | EXISTS |
| not-me.ai | `stage5mind/` | EXISTS |
| primitive-engine.ai | (none) | **NEEDS CREATION** |

---

*NOT-ME: The interface to your technological self. One component, four sites, unified learning.*

— Web Architecture v1.0, 2026-01-26
