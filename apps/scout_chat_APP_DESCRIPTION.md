# Scout Chat — The Direct Line

## What It Does

Scout Chat is a **single HTML file** — 336 lines of pure HTML, CSS, and JavaScript — that connects directly to Scout (Llama 4 17B-16E) running on the King node of the Mac Studio cluster. No frameworks, no build steps, no dependencies. Open the file, start talking.

### Features

- Purple gradient UI with rounded message bubbles
- Loading dots animation while Scout thinks
- Full conversation history within the session
- Auto-focus input, Enter to send
- Connects to EXO cluster at `192.168.68.121:8765`
- Model: `mlx-community/Llama-4-Scout-17B-16E-Instruct-8bit`

## Technological Basis

- **Vanilla HTML/CSS/JavaScript** — zero dependencies
- **Fetch API** — HTTP POST to OpenAI-compatible `/v1/chat/completions` endpoint
- **EXO** — distributed inference framework on the Mac Studio cluster
- **MLX** — Apple's machine learning framework (model runs via mlx_lm)

### Architecture Pattern

```
HOLD₁ (Human message in browser)
    → AGENT (Scout on King node via EXO)
        → HOLD₂ (Response rendered in browser)
```

The simplest possible HOLD:AGENT:HOLD. No middleware, no backend, no routing. Browser → EXO → Browser.

## Meta Concepts

### The Prototype of Everything

Scout Chat was the first working proof that the local inference vision is real. Before Genesis, before the Knowledge Atomizer, before Sovereign Studio — there was this: a single HTML file talking to a local model. It proved three things:

1. **Local inference works** — Llama 4 runs on Jeremy's hardware, no cloud needed
2. **The EXO cluster works** — distributed inference across Mac Studios is viable
3. **The interface can be trivial** — you don't need React, you don't need a framework, you just need a text box and a model

### Why It Exists

Scout Chat exists because Jeremy needed to talk to Scout **right now**, without setting up a development environment, without installing dependencies, without waiting for a build. It is the **emergency phone** — always works, always available, no complexity to break.

It also serves as the **reference implementation** for all other chat interfaces. Every chat app in the ecosystem (Kiosk Mode, Not-Me Chat, Knowledge Atomizer's Interact view) is a more sophisticated version of what this file does in 336 lines.

### Sovereignty in Action

This file embodies the sovereignty vision more than any other app. It has:
- No cloud dependency (local model)
- No framework dependency (vanilla JS)
- No build dependency (raw HTML)
- No package dependency (zero npm packages)

If the internet goes down, if npm is unavailable, if every framework breaks — this file still works. That's sovereignty.

### What It Wants To Become

It's already what it wants to be — a direct line to Scout. If anything, it should stay exactly this simple. Complexity belongs in other apps. Scout Chat is the reference point for "this is all you really need."

## Current Maturity

**Complete** — It does exactly what it was built to do. No features missing, no bugs to fix, no dependencies to update. The only thing that changes is the model ID and the cluster IP when hardware moves.

## HOLD:AGENT:HOLD Position

Scout Chat is a **ME Service** in its purest form — a direct wire from Jeremy's fingers to Scout's inference engine. No mediation, no enrichment, no processing. Just communication.
