# Websites — The Public Faces

## What It Does

The Websites directory contains **five web properties** for the truth_forge ecosystem's public-facing presence, plus a shared component library specification. These are the surfaces that customers, partners, and the world see.

### The Five Sites

| Website | Package Name | Role | Subtitle |
|---------|-------------|------|----------|
| **truth_forge** | `@truth-forge/website-truth-forge` | THE GENESIS | The holding company site — framework docs, organism status, governance |
| **credential_atlas** | `@truth-forge/website-credential-atlas` | THE SEER | Credential verification platform — proving credentials are real |
| **not_me** | `@truth-forge/website-not-me` | THE CONVERSATION | Conversational AI interface — public-facing Not-Me chat |
| **primitive_engine** | `@truth-forge/website-primitive-engine` | THE BUILDER | Primitive creation and configuration — buy/configure your organism |
| **shared** | (specification only) | THE COMMONS | Shared components: Header, Footer, ThePattern, CostBadge |

### truth_forge Website (Most Developed)

The main site includes:
- **Vercel serverless API functions** — backend logic at the edge
- **Supabase integration** — authentication, database, real-time
- **Anthropic SDK** — Claude integration for site features
- **Google Cloud** — BigQuery, Cloud Storage, GenAI
- **Upstash Redis** — caching and rate limiting
- **Document service connectivity** — direct integration with the document-service app

### Planned Pages Across Sites

| truth_forge | credential_atlas | not_me | primitive_engine |
|-------------|-----------------|--------|-----------------|
| Landing | Landing | Landing | Landing |
| Framework docs | Verify credentials | Chat interface | Build a Primitive |
| Organism status | Issue credentials | Conversation history | Configure hardware |
| Governance | Credential types | Learning insights | Pricing tiers |
| Developer API | Organization portal | About | Deploy |

### Shared Components (Specification)

| Component | Purpose |
|-----------|---------|
| **Header** | Consistent navigation across all sites |
| **Footer** | Legal, links, brand consistency |
| **ThePattern** | Visual representation of HOLD:AGENT:HOLD |
| **CostBadge** | Real-time cost tracking display |

## Technological Basis

- **React 18 / TypeScript** — core framework for all sites
- **Vite** — development and build tooling
- **React Router** — client-side navigation
- **Vercel** — deployment platform (truth_forge site)
- **Supabase** — auth, database, real-time subscriptions
- **Tailwind CSS** — styling (some sites)

### Site-Specific Tech

| Site | Additional Dependencies |
|------|----------------------|
| truth_forge | Anthropic, BigQuery, GCS, GenAI, Supabase, Upstash Redis |
| credential_atlas | React Router |
| not_me | React Router |
| primitive_engine | Anthropic, React Router |
| shared | None (specification only) |

### Architecture Pattern

```
shared/ (Headers, Footers, ThePattern, CostBadge)
    │
    ├── truth_forge website ──── Vercel + Supabase + Claude + GCP
    ├── credential_atlas website ── React SPA
    ├── not_me website ──────── React SPA + Module Federation Chat
    └── primitive_engine website ── React SPA + Anthropic
```

All sites consume shared components (planned) and are designed to integrate the federated Not-Me Chat widget (from `templates/module-federation/`).

## Meta Concepts

### The Ecosystem's Skin

If Genesis is the organism's brain and the services are its organs, the websites are its **skin** — the boundary where the organism meets the world. The skin has two functions:
1. **Protection** — presenting the organism's capabilities in a controlled, curated way
2. **Sensation** — receiving input from the world (customer sign-ups, credential verifications, chat conversations)

Each website serves a different patch of skin:
- **truth_forge** = the face — identity, recognition, first impression
- **credential_atlas** = the hands — doing work, proving things, making contact
- **not_me** = the mouth — speaking, listening, conversing
- **primitive_engine** = the store — commerce, exchange, value transfer
- **shared** = the common cells — the DNA that makes all skin the same organism

### The Grammar in Practice

The websites demonstrate THE FRAMEWORK's grammar rules:
- Package names use hyphens: `@truth-forge/website-truth-forge` — these are products (US domain)
- Folder names use underscores: `truth_forge/`, `credential_atlas/` — these are infrastructure (NOT-ME domain)
- The user-facing names use capitals: Truth Forge, Credential Atlas — these are ME's concepts

### Why They Exist

The organism needs to interface with the world. Jeremy's vision is not just personal — it's commercial. These websites are the storefronts:
- **truth_forge** establishes credibility and explains the framework
- **credential_atlas** demonstrates the first product (credential verification)
- **not_me** gives the world access to the conversational AI
- **primitive_engine** sells the Primitive product (deployable organisms)

Each website is an act of **CARE-EXTERNAL** — the organism offering its capabilities to THE OTHER.

### The Document Service Bridge

The `truth_forge` website has direct integration with the `document-service` app, documented in `DOCUMENT_SERVICE.md` and `ENV_SETUP_DOCUMENT_SERVICE.md`. This means the main website can:
- Upload documents for processing
- Trigger knowledge atomization
- Access processed knowledge atoms
- Display atom metadata

This is significant: the public website is not just a marketing page — it's a **functional surface** of the organism. Visitors can interact with real capabilities.

### What They Want To Become

Production commercial websites deployed on Vercel with:
- Supabase authentication across all sites (federated login)
- Module Federation for shared chat (Not-Me on every page)
- Real-time organism status (from THE SEER)
- Stripe integration for Primitive purchases
- Customer onboarding that provisions new Primitive organisms
- API documentation for developer integration

### What Credential Atlas Specifically Represents

Credential Atlas is the **first commercial application** of the truth_forge framework. It uses the same knowledge atomization and verification patterns on a specific domain: credentials (degrees, certifications, work experience). The credential is the knowledge atom; verification is the fidelity check. The framework's patterns prove their value by solving a real commercial problem.

## Current Maturity

**Mixed** — The `truth_forge` website is the most developed with real Vercel deployment configuration, Supabase integration, serverless API functions, and document service connectivity. The `credential_atlas`, `not_me`, and `primitive_engine` sites are scaffolded with React Router and component structures but no backend integration. The `shared` directory contains only a README specification.

## HOLD:AGENT:HOLD Position

The websites are **ME Services for THE OTHER** — they exist for external humans (not Jeremy) to interact with the organism's capabilities. They are the commercial boundary where the organism's CARE-EXTERNAL becomes accessible to the world.
