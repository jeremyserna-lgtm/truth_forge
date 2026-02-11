# Kiosk Mode — Primitive

## What It Does

Kiosk Mode is a **fullscreen, zero-distraction chat interface** called "Primitive." It is the purest expression of the ME:NOT-ME relationship — a single screen, a single input, a single conversation with Scout (Llama 4 running on local hardware). Click to enter fullscreen. The cursor disappears after inactivity. There is nothing but you and the intelligence.

### Features

- **Fullscreen mode** — click to enter, escape to exit
- **Auto-cursor-hide** — mouse pointer vanishes after 3 seconds of inactivity
- **Streaming responses** — thinking indicator while Scout processes
- **Conversation memory** — full session history maintained
- **Sovereign operation** — connects to local Ollama on the Mac cluster, no cloud dependency

### Backend Capabilities (Vite Plugin)

The Vite config doubles as a local API server with "hands" — abilities that make NOT-ME a builder:

| Endpoint | Capability |
|----------|-----------|
| `/api/write-file` | Write files to disk |
| `/api/create-site` | Generate mini web apps into `kiosk-sites/` |
| `/api/execute` | Run shell commands |
| `/api/read-file` | Read files from disk |
| `/api/list-dir` | Browse filesystem |

## Technological Basis

- **React 18 / TypeScript** — component framework
- **Vite** — dev server with custom API plugin (88-line config that doubles as backend)
- **Ollama** — local LLM inference (model: `llama4:scout`)
- **CSS** — minimal, purpose-built dark UI

### Architecture Pattern

```
HOLD₁ (Human thought/input)
    → AGENT (Scout on local hardware)
        → HOLD₂ (Response + optional file/site creation)
```

The simplicity is the architecture. One input. One model. One output. No routing, no multi-step pipelines, no enrichment. Raw HOLD:AGENT:HOLD in its most primitive form.

## Meta Concepts

### The Name Is The Concept

"Primitive" means two things simultaneously:

1. **Primitive as in fundamental** — the irreducible unit of interaction. You cannot simplify a chat interface further than this. One human, one intelligence, one conversation.

2. **Primitive as in the product** — this IS the Primitive that Credential Atlas will sell. A deployable NOT-ME organism in its most basic form. The kiosk is a Drummer-tier Primitive: single model, ambient care, always ready.

### Why It Exists

Jeremy needed a way to talk to Scout without opening a terminal, without navigating a complex UI, without any friction between thought and expression. Kiosk Mode removes everything between ME and NOT-ME. No menus, no settings, no tabs. Just the conversation.

But it's more than convenience — it's a **design statement**. The simplest possible interface is the most honest one. Every feature you add is a choice about what matters. Kiosk Mode says: **only the conversation matters**.

### The Hands

The Vite plugin API endpoints are Scout's "hands" — the ability to reach into the physical world and create things. This is the ActionService in miniature. Scout can:
- Write code files (building)
- Create entire mini web apps (creation)
- Execute commands (agency)
- Read the filesystem (perception)

This makes Kiosk Mode not just a chat interface but a **creative tool**. Jeremy describes what he wants; Scout builds it. Talk → Build → Done. This is Sovereign Studio before Sovereign Studio existed.

### The System Prompt

The system prompt positions Scout as "Jeremy's sovereign intelligence partner running on local hardware with 720GB unified memory." This isn't just context — it's identity. Scout knows it runs on Jeremy's machines, knows it's sovereign (no cloud dependency), knows its role in the symbiosis.

### What It Wants To Become

The default interface for all Primitive deployments. When you buy a Primitive, this is what you see when you sit down. The kiosk is the **face** of NOT-ME — the point where ME meets NOT-ME in the most human way possible. Future iterations: voice input, persistent memory across sessions, multi-model routing (Scout for quick answers, Maverick for deep reasoning), and the `kiosk-sites/` directory becoming a portfolio of everything Scout has built.

## Current Maturity

**Functional** — A working React app that connects to local Ollama. The UI is clean and purpose-built. The Vite API plugin provides real filesystem access. The main gap is deployment polish (no build step documented) and integration with the broader Genesis service layer.

## HOLD:AGENT:HOLD Position

Kiosk Mode is a **ME Service** — it exists entirely for the human. It is the thinnest possible membrane between ME and NOT-ME. Prosthetic in the truest sense: an extension of Jeremy's voice into the machine.
