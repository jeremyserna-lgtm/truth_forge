# Sovereign Genesis — The Unified Platform

## What It Does

Sovereign Genesis is the **unification app** — it combines three separate applications (Knowledge Atomizer, Sovereign Interface, and Sovereign Studio) into a single platform with sidebar navigation. Instead of switching between three browser tabs and three development servers, Jeremy gets one app with three views.

### The Three Views

| View | Source App | Purpose |
|------|-----------|---------|
| **Knowledge Atomizer** | `knowledge-atomizer/` | Ingest → Refine → Store → Use workflow |
| **Sovereign Interface** | `sovereign-interface/` | System cognition dashboard (THE SEER, NOT-ME Terminal) |
| **Sovereign Studio** | `sovereign-studio/` | Talk → Build → Done (app generation) |

### UI Features

- Collapsible sidebar navigation
- Dark/light theme toggle
- Animated gradient status indicator
- Clean, focused workspace per view

## Technological Basis

- **React 19 / TypeScript** — latest React
- **Vite** — development and build
- **Tailwind CSS** — utility-first styling with dark mode
- **Lucide** — iconography
- **Recharts** — data visualization (from Sovereign Interface)
- **react-simple-code-editor** — code editing (from Sovereign Studio)
- **Gemini AI / Ollama** — multi-provider LLM integration

### Shared Service Layer

| Service | Function |
|---------|----------|
| `geminiService.ts` | Google Gemini API integration |
| `ollamaService.ts` | Local Ollama inference |
| `llmService.ts` | Multi-provider LLM routing |
| `localLLMService.ts` | Local-first LLM with fallback |
| `scoutService.ts` | Scout-specific inference |
| `storageService.ts` | Local storage persistence |
| `clusterService.ts` | Cluster management integration |
| `importService.ts` | Document import utilities |

### Architecture Pattern

```
                    ┌─ Atomizer View ──── INGEST → REFINE → STORE → USE
                    │
Sidebar Navigation ─┼─ Interface View ── THE SEER / NOT-ME Terminal / Bootstrap
                    │
                    └─ Studio View ───── Talk → Build → Done
```

All three views share the same service layer, meaning LLM calls, storage, and cluster management are consistent across contexts.

## Meta Concepts

### Convergence

Sovereign Genesis is the first attempt at the fundamental insight that drives this entire project: **all of these apps are one app**. The Knowledge Atomizer, the Sovereign Interface, and Sovereign Studio are not separate tools — they are three perspectives on the same organism. Atomization is how the organism ingests. Interface is how Jeremy observes the organism. Studio is how the organism builds.

By combining them, Sovereign Genesis acknowledges what was always true: the organism does not have separate apps for separate functions. It has one body with many organs, and the dashboard should reflect that unity.

### Why It Exists

Jeremy was running three dev servers, switching between three browser tabs, losing context every time he changed apps. Sovereign Genesis exists because **context switching is the enemy of flow**. One app, one window, one train of thought. The sidebar is all the navigation needed.

This is also a product preview — when a Primitive customer sits down at their machine, they should see ONE app, not twelve. Sovereign Genesis is the prototype for that unified experience.

### The Shared Service Layer

The most architecturally significant thing about Sovereign Genesis is not the combined UI — it's the **shared service layer**. All three views talk to the same LLM services, the same storage, the same cluster manager. This means:
- Knowledge atoms extracted in Atomizer are available in Studio
- Cluster status displayed in Interface affects model selection in Atomizer
- Content created in Studio can be fed back to Atomizer for extraction

The services become the organism's bloodstream — flowing through all organs simultaneously.

### What It Wants To Become

The Genesis Meta App — the single application described in `GENESIS_META_APP_SPEC.md`. Not just three views in a sidebar, but a fully unified organism interface where:
- Atomization runs continuously in the background
- Interface monitoring is always visible
- Studio creation uses the latest atoms automatically
- New views are added as organs are added to the organism
- The sidebar becomes a cortex map — showing which organs are active, which are processing, which need attention

## Current Maturity

**Well-Structured Shell** — The sidebar navigation, theme toggle, and view switching are functional. The service layer is defined. The three views have component structures. However, the views themselves are primarily shells referencing the parent apps' functionality — the deep feature set of the standalone Knowledge Atomizer (989-line App.tsx) is reduced to a simpler view here.

The gap between Sovereign Genesis and the standalone apps represents the work needed to truly unify: the standalone apps have features that haven't been ported, and the unified platform has architectural advantages (shared services) that the standalone apps lack.

## HOLD:AGENT:HOLD Position

Sovereign Genesis is a **ME Service** — the unified prosthetic cockpit. It combines three prosthetic instruments into one dashboard. The organism doesn't need it to function; Jeremy needs it to see, build, and control.
