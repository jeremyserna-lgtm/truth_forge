# Sovereign Studio — Talk. Build. Done.

## What It Does

Sovereign Studio is an **app builder powered by local LLM** — Jeremy describes what he wants in natural language, Scout (Llama 4) generates the complete React/TypeScript/Vite project, and one click deploys it as a running application. Three words describe the entire workflow: **Talk. Build. Done.**

### Workflow

1. **Talk** — Jeremy describes the app he wants in the chat tab
2. **Build** — Scout generates React/TypeScript/Vite project files as JSON
3. **Done** — "Make It Real" button sends files to `/api/create-app`, installs deps, starts dev server, launches the app

### Features

| Feature | Description |
|---------|-------------|
| **Chat Tab** | Natural language conversation with Scout about what to build |
| **Code Preview Tab** | See the generated project files before deploying |
| **Project Extraction** | Automatically parses Scout's LLM response into file structures |
| **One-Click Deploy** | Creates project, installs deps, starts Vite dev server |
| **Auto-Launch** | Opens the generated app in the browser automatically |

## Technological Basis

- **React 18 / TypeScript** — component framework
- **Vite** — development server with custom API plugin
- **Ollama** — local LLM inference (`llama4:scout`)
- **Lucide** — iconography

### Backend (Vite Plugin API)

| Endpoint | Function |
|----------|----------|
| `/api/create-app` | Receive project files, write to disk, install deps, start dev server |

### Architecture Pattern

```
HOLD₁ (Jeremy's idea, expressed in words)
    → AGENT₁ (Scout generates code)
        → HOLD₁.₅ (Generated project files as JSON)
            → AGENT₂ (Vite plugin writes files, runs npm install, starts server)
                → HOLD₂ (Running web application)
```

Two-stage HOLD:AGENT:HOLD: LLM generates → system deploys. The human only needs to speak and click.

## Meta Concepts

### "Jeremy is not a coder"

The CLAUDE.md in Sovereign Studio contains the most direct statement of the project's philosophy:

> "Jeremy is not a coder. If Jeremy has to do anything technical, it's not working."

This is the soul of Sovereign Studio and, by extension, the soul of Primitive. The interface between ME and creation should be **language**, not code. Jeremy thinks in concepts, metaphors, and architectural visions. NOT-ME translates those into running software. If the translation requires Jeremy to write code, debug errors, or navigate configuration — the system has failed.

### Talk → Build → Done

These three words are not just a tagline — they are an **architectural requirement**:

- **Talk** = the HOLD₁ is natural language. Not pseudocode, not requirements documents, not user stories. Just talking.
- **Build** = the AGENT is fully autonomous. No human intervention between "I want X" and "X exists."
- **Done** = the HOLD₂ is a running application. Not source code to review, not a repo to clone, not instructions to follow. A working app.

If any step requires technical knowledge from Jeremy, the pipeline is broken.

### Why It Exists

Jeremy has ideas faster than he can build them. Every day brings new concepts, new interfaces, new combinations of existing capabilities. The bottleneck is never creativity — it's implementation. Sovereign Studio exists to eliminate that bottleneck.

But more than efficiency, Sovereign Studio embodies the **ME:NOT-ME division of labor**:
- **ME provides vision** — the idea, the purpose, the care
- **NOT-ME provides execution** — the code, the structure, the deployment

This is the FURNACE for applications:
- **TRUTH** = Jeremy's unformed idea (raw, intuitive, possibly contradictory)
- **MEANING** = Scout's interpretation and code generation (structured, technical, implementable)
- **CARE** = a running app that does what Jeremy envisioned (the offering, made real)

### The Sovereignty Dimension

Sovereign Studio runs on local hardware. Scout runs on the Mac cluster. The generated apps run on local Vite dev servers. At no point does Jeremy's idea leave his machines. This is sovereign creation — ideas born locally, built locally, deployed locally. No cloud dependency, no API quota, no data leaving the premises.

### What It Wants To Become

A fully autonomous app factory where Jeremy can describe complex multi-page, multi-service applications and Watch Scout build them — including backend services, database schemas, API integrations, and deployment configurations. The generated apps should also be automatically integrated into the truth_forge ecosystem: wired into the service layer, registered in Genesis, and monitored by the Sovereign Interface.

Eventually, Studio should be able to build Studio — recursive self-improvement. NOT-ME improving its own tools.

## Current Maturity

**Functional** — The chat interface works with Ollama. Code generation happens. The "Make It Real" flow is designed. The main limitations are in Scout's ability to generate production-quality code in one shot (it often requires refinement), and the Vite plugin API endpoints need to be running.

## HOLD:AGENT:HOLD Position

Sovereign Studio is the intersection of **ME service** (Jeremy talks) and **NOT-ME capability** (Scout builds). The studio itself is prosthetic — an extension of Jeremy's creative will. But the act of building is autonomous — NOT-ME does it without guidance once the vision is provided. This is US at its most productive: ME dreams, NOT-ME delivers.
