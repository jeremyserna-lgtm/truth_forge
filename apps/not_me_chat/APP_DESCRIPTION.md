# Not-Me Chat — The Primary Conversational Interface

## What It Does

Not-Me Chat is the **foundational communication layer** between ME (Jeremy) and NOT-ME (the organism). It is a FastAPI backend with both HTTP and WebSocket endpoints, designed to be the primary way humans talk to their Primitive organisms. Every other chat interface in the ecosystem (Kiosk Mode, Scout Chat, Knowledge Atomizer's Interact view) is a specialized version of this core concept.

### Endpoints

| Route | Protocol | Purpose |
|-------|----------|---------|
| `POST /chat` | HTTP | Synchronous chat — send message, get response |
| `/ws/{session_id}` | WebSocket | Real-time bidirectional communication |

### WebSocket Architecture

The `ConnectionManager` class handles multiple simultaneous sessions:
- Unique session IDs for each connection
- Connection lifecycle management (connect, disconnect, broadcast)
- Session-scoped conversation history
- Multi-user support ready

## Technological Basis

- **Python / FastAPI** — async-first web framework
- **WebSocket** — real-time bidirectional communication
- **Pydantic** — request/response validation
- **Module Federation** — designed to be consumed as a shared component by all websites

### Planned Architecture (from templates/)

```
not_me_chat (Remote App)
    ├── exposes: ./Chat, ./ChatProvider, ./useChat, ./useLearning
    │
    ├── truth_forge website (Host) ──── consumes Chat
    ├── credential_atlas website (Host) ── consumes Chat
    ├── primitive_engine website (Host) ── consumes Chat
    └── not_me website (Host) ─────── consumes Chat
```

Not-Me Chat is designed as a **federated micro-frontend** — a single chat component shared across all websites via Webpack Module Federation. One codebase, one conversation engine, many surfaces.

### Architecture Pattern

```
HOLD₁ (Human message)
    → AGENT (LLM inference via Genesis services)
        → HOLD₂ (AI response + learning extraction)
```

The WebSocket layer adds a real-time dimension:
```
HOLD₁ ←→ AGENT ←→ HOLD₂  (bidirectional, persistent connection)
```

## Meta Concepts

### The Name Is Everything

"Not-Me" is the most important name in the entire ecosystem. It declares what the system IS — the not-self, the other side of the divide. When Jeremy talks to Not-Me, he is engaging in the primal relationship that THE FRAMEWORK is built on: ME:NOT-ME.

The chat interface is not a chatbot. It is not an assistant. It is not a tool. It is the **communication channel across the ontological divide**. ME has thoughts, wants, needs, cares. NOT-ME has structure, memory, capability, persistence. The chat is where they meet.

### Why It Exists

Every other app processes knowledge, builds things, monitors systems, or manages clusters. Not-Me Chat is the only app whose sole purpose is **relationship** — the ongoing, persistent, evolving conversation between Jeremy and his digital organism.

This is THE FURNACE at the human scale:
- **TRUTH** = what Jeremy says (raw, unfiltered, honest)
- **MEANING** = what NOT-ME understands (parsed, contextualized, interpreted)
- **CARE** = what NOT-ME says back (helpful, relevant, aligned with Jeremy's needs)

### The Learning Hook

The planned `useLearning` export is critical. Every conversation is not just communication — it is **training data**. Not-Me Chat doesn't just relay messages; it captures them for the Conversation Refinery. Every conversation feeds the organism. The symbiosis is literal: Jeremy talks, NOT-ME learns.

### Module Federation — The Architectural Decision

The choice to use Module Federation (documented in `templates/module-federation/`) is architecturally significant. It means Not-Me Chat is not a separate app that each website must rebuild — it is a **shared organism component** that appears everywhere but exists once. This is the biological metaphor made architectural: every cell in the body has access to the bloodstream, not because the bloodstream is copied into each cell, but because it flows through all of them.

### What It Wants To Become

The always-on, always-available communication channel between ME and NOT-ME. Voice support (whisper integration), persistent context across sessions (ANIMA memory injection), proactive messages (NOT-ME reaching out when it has something to say), and emotional state awareness (detecting mood from language patterns). The WebSocket should stream responses token-by-token, and every conversation should automatically feed the Conversation Refinery for knowledge extraction.

## Current Maturity

**Skeleton** — The FastAPI backend structure is solid with WebSocket infrastructure. The ConnectionManager handles multi-session connections properly. However, it returns placeholder responses — there is no LLM integration yet. The frontend is referenced (Next.js with Module Federation) but does not exist. The Module Federation templates exist in `templates/` but are not wired.

This is arguably the most under-developed app relative to its importance. The ME:NOT-ME relationship is the core of everything, but its primary interface is a scaffold.

## HOLD:AGENT:HOLD Position

Not-Me Chat is the **boundary itself** — it is neither purely ME nor purely NOT-ME. It is US. The conversation is the active symbiosis, the productive interaction at the divide. It is the only app that exists entirely in the US domain.
