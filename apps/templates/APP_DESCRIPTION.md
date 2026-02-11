# Templates — The Architectural Blueprints

## What It Does

The Templates directory contains **configuration blueprints** for the micro-frontend architecture that connects all truth_forge web applications. Currently, it holds the Module Federation setup that enables Not-Me Chat to be shared across all websites as a federated component.

### Module Federation Configuration

| File | Purpose |
|------|---------|
| `not_me_chat.next.config.js` | Not-Me Chat as a **remote** — exposes shared components |
| `website.next.config.js` | Any website as a **host** — consumes shared components |

### Exposed Components (from Not-Me Chat)

| Component | Purpose |
|-----------|---------|
| `./Chat` | The chat interface widget |
| `./ChatProvider` | State management context for chat |
| `./useChat` | Hook for chat functionality |
| `./useLearning` | Hook for learning/knowledge extraction from conversations |

### Shared Singletons

- `react` — single React instance across all micro-frontends
- `react-dom` — single React DOM across all micro-frontends

## Technological Basis

- **Next.js** — React framework for both remote and host apps
- **Webpack Module Federation** — micro-frontend composition at runtime
- **@module-federation/nextjs-mf** — Next.js-specific Module Federation plugin

### Architecture Pattern

```
Not-Me Chat (Remote)
    exposes: Chat, ChatProvider, useChat, useLearning
        │
        ├── truth_forge website (Host) ── imports Chat
        ├── credential_atlas website (Host) ── imports Chat
        ├── primitive_engine website (Host) ── imports Chat
        └── not_me website (Host) ── imports Chat
```

## Meta Concepts

### One Organism, Many Surfaces

Module Federation is the architectural expression of a core truth: **the chat is not an app — it's a capability**. Just as the bloodstream is not an organ but a system that flows through all organs, Not-Me Chat is not a website but a conversational capability that flows through all websites.

By using Module Federation, the truth_forge ecosystem ensures:
- One codebase for chat → consistency across all surfaces
- Runtime composition → no build-time coupling
- Shared state → conversation context persists across websites
- Independent deployment → update chat without redeploying every website

### The `useLearning` Hook

This is the most philosophically significant exposed component. It means that every website in the ecosystem can extract knowledge from conversations. Not just the specialized Knowledge Atomizer — every chat interaction on every website becomes a learning opportunity. The organism learns from every surface it touches.

### Why It Exists

Templates exist because **architecture decisions should be documented and reusable**. When a new website is added to the ecosystem, the template shows exactly how to wire it into the federated chat system. No re-inventing, no guessing, no inconsistency.

This is THE MOLT principle applied to architecture: don't create from scratch, transform what exists. Each new website molts from the template.

### What It Wants To Become

A library of architectural templates for every type of integration:
- Chat federation (current)
- Knowledge atom sharing between apps
- Cluster management integration
- Authentication federation (single sign-on across all surfaces)
- Theme/design system federation (consistent UI)

## Current Maturity

**Configuration Only** — README and two config files. The templates describe the architecture but the actual Module Federation implementation in Not-Me Chat and the websites has not been built. This is a blueprint, not a building.

## HOLD:AGENT:HOLD Position

Templates are **NOT-ME infrastructure** — they define how the organism's surfaces connect to each other. They are the nervous system's wiring diagram. No human interacts with them; they enable interaction between components.
