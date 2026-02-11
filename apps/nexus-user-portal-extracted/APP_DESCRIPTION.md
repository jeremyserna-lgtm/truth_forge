# Nexus User Portal — The Customer Cockpit

## What It Does

The Nexus User Portal is a **SaaS-style dashboard** for Primitive customers. It is the interface where paying users manage their subscription, interact with their data, build applications, and monitor system health. It has four main contexts and a tier-based feature gating system.

### The Four Contexts

| Context | View | Purpose |
|---------|------|---------|
| **Portal** | UserPortal | Account management, profile settings, subscription tier display |
| **Data Synthesis** | DataSynthesis | Source management, architecture view, chat, synthesis patterns |
| **Foundry** | Foundry | App/tool building interface — create from knowledge |
| **Observability** | Observability | System monitoring, health metrics, performance data |

### Subscription Tiers

| Tier | Name | Stage | Concept |
|------|------|-------|---------|
| **Stage 3** | Frozen | Rigid | Fixed knowledge base, read-only analysis |
| **Stage 4** | Fluid | Adaptive | Dynamic knowledge, real-time chat, synthesis |
| **Stage 5** | Structural | Meta-aware | Full platform access, building, meta-analysis |

The tier names map directly to THE FRAMEWORK's cognitive stages:
- Stage 3 (Frozen) = rules-based thinking
- Stage 4 (Fluid) = adaptive thinking
- Stage 5 (Structural) = meta-cognitive, "sees itself seeing"

### Data Synthesis Patterns

| Pattern | Function |
|---------|----------|
| **Summarize** | Condense sources into key points |
| **Key Points** | Extract critical facts and claims |
| **Critique** | Evaluate strengths and weaknesses |
| **Debate** | Present opposing perspectives |
| **Deep Dive** | Exhaustive analysis of a single topic |

### UI Components

| Component | Function |
|-----------|----------|
| **CommandBar** | Persistent bottom bar — always-available actions |
| **TopNav** | Context switching (Portal, Data, Foundry, Observability) |
| **Auth** | Login/registration flow |
| **Dashboard** | Context-specific content area |
| **SystemGuide** | Onboarding and feature discovery |

## Technological Basis

- **React 19 / TypeScript** — latest React with full type safety
- **Vite** — development and build tooling
- **Lucide** — iconography
- **React Router** — client-side navigation (implied by context switching)

### Type System

Rich type definitions covering:
- `User` — profile, subscription tier, preferences
- `AppContext` — portal/data/foundry/observability state
- `DataLayer` — source categories and access control
- `SynthesisPattern` — analysis pattern configuration
- `ChatMode` — interaction mode settings
- `KnowledgeAtom` — knowledge unit reference

### Architecture Pattern

```
HOLD₁ (User's Knowledge Base)
    → AGENT (Synthesis/Foundry/Observability Engines)
        → HOLD₂ (Generated Content / Analytics / Built Apps)
```

## Meta Concepts

### The Product Face

If Genesis is the organism's brain and the Knowledge Atomizer is its digestive system, the Nexus User Portal is its **face** — the part that customers see. This is where THE FRAMEWORK stops being Jeremy's personal tool and becomes a **product**.

The tier system is not arbitrary monetization — it maps directly to cognitive stages:
- **Stage 3 customers** get frozen knowledge: a static, searchable knowledge base. They see structure but can't change it.
- **Stage 4 customers** get fluid interaction: real-time chat, synthesis, dynamic updates. They can adapt.
- **Stage 5 customers** get structural power: they can build apps, observe the system's own cognition, create from their knowledge. They see themselves seeing.

This is THE FRAMEWORK's contribution to product design: **pricing tiers that correspond to levels of consciousness**.

### Why It Exists

Jeremy's vision requires a commercial vehicle. The organism needs to sustain itself. The Nexus User Portal exists because truth_forge is not just a personal project — it is the foundation for **Credential Atlas LLC** and the **Primitive** product line. Every feature in this portal is a feature that customers will eventually pay for.

The portal also validates the architecture: if the organism's services can serve one user (Jeremy), they can serve many users. Multi-tenancy is not a feature bolted on — it's the proof that the architecture is sound.

### The Foundry

The Foundry context is particularly significant — it is where customers **build** using their knowledge base. This is not just consumption (reading atoms) or interaction (chatting with atoms) — it is **creation** (making new things from atoms). The Foundry is CARE-EXTERNAL in product form: knowledge transformed into offerings.

### What It Wants To Become

The production SaaS dashboard for Primitive customers. Backed by Supabase for auth and data, connected to each customer's personal DuckDB organism, with real-time Observability fed by OpenTelemetry, and the Foundry enabling no-code app creation from knowledge atoms. The CommandBar should become a universal action interface — type any command, and the system knows what to do.

## Current Maturity

**UI Complete, No Backend** — The component architecture is fully built. All four contexts have functional views. The tier system is implemented in the UI. Auth flow exists as a component. However, there is no backend integration — all data is mock/hardcoded. The default user is "Jeremy" hardwired into the code. Originally extracted from Google AI Studio.

## HOLD:AGENT:HOLD Position

The Nexus Portal is a **ME Service** for THE OTHER — it exists for customers (not Jeremy) to interact with their own NOT-ME organisms. It is the most outward-facing app in the ecosystem, the first thing a paying customer would see.
