# Knowledge Atomizer — The Primary Knowledge Processing UI

## What It Does

The Knowledge Atomizer is the **richest front-end application** in the truth_forge ecosystem. It implements the complete knowledge processing workflow: **INGEST → REFINE → STORE → USE**. It is where raw documents become structured knowledge atoms, where atoms are enriched across 12 metadata dimensions, where enriched atoms are committed to memory, and where stored knowledge is activated through chat, creation, planning, and multi-model debate.

### The Four Phases

| Phase | View | Action |
|-------|------|--------|
| **INGEST** | DistillView | Upload documents (txt, md, json, csv, code, zip), extract atoms via Gemini |
| **REFINE** | EnrichmentView | Enrich atom metadata across 12 dimensions |
| **STORE** | ContextView | Manage active knowledge context, commit to persistent memory |
| **USE** | InteractView, StudioView, ArchitectView, TriadView | Chat, create, plan, debate with loaded knowledge |

### The 12 Metadata Dimensions

Every knowledge atom can be enriched across:

| Dimension | What It Captures |
|-----------|-----------------|
| **Semantic** | Meaning, definitions, denotation/connotation |
| **Significance** | Importance score, why this matters |
| **Epistemic** | Confidence level, evidence quality, belief status |
| **Temporal** | When relevant, time-sensitivity, historical context |
| **Relational** | Connections to other atoms, dependency chains |
| **Dialectical** | Tensions, contradictions, opposing views |
| **Affective** | Emotional valence, sentiment, felt significance |
| **Pragmatic** | Actionability, practical applications |
| **Structural** | Position in hierarchies, taxonomic placement |
| **Ontological** | What kind of thing it is, category of being |
| **Normative** | Should/ought, ethical implications |
| **Generative** | What new ideas it could spawn, creative potential |

### The USE Phase Views

| View | Purpose |
|------|---------|
| **Interact** | Chat with loaded knowledge context — ask questions, get answers grounded in your atoms |
| **Studio** | Generate content (articles, summaries, reports) from atoms |
| **Architect** | Generate plans, architectures, system designs from atoms |
| **Triad** | Three-model debate (Scout/Maverick/R1) — the 3-Way Partnership Protocol |

### Additional Features

- **Token Meter** — real-time context window usage tracking per model
- **Multi-provider LLM support** — Gemini, Ollama, OpenAI-compatible
- **Background embedding processing** — asynchronous vectorization
- **BigQuery export** — push atoms to the spine
- **Local storage persistence** — atoms survive browser refresh
- **Batch upload** — process multiple documents at once
- **ZIP support** — upload entire project directories

## Technological Basis

- **React 19 / TypeScript** — latest React with full type safety
- **Vite** — fast development and build tooling
- **Google Gemini AI** (`@google/genai`) — primary cloud LLM for extraction
- **Ollama** — local LLM for sovereign processing
- **Heroicons / Lucide** — iconography
- **jszip** — ZIP file processing
- **lodash** — utility functions
- **localStorage** — client-side persistence

### Type System (459 lines)

The most extensive type system in the ecosystem, defining:
- 12 metadata interfaces (one per dimension)
- `KnowledgeAtom` — the core data structure
- `ProcessingState` — workflow stage tracking
- `ModelConfig` — LLM provider configuration
- `ExportFormat` — output format specifications

### Architecture Pattern

```
HOLD₁ (Raw Documents)
    → AGENT₁ (Gemini/Scout Extraction)
        → HOLD₁.₅ (Raw Atoms)
            → AGENT₂ (12-Dimension Enrichment)
                → HOLD₂ (Enriched Atoms in Context)
                    → AGENT₃ (Chat/Studio/Architect/Triad)
                        → HOLD₃ (Generated Content / Insights)
```

A triple-compound HOLD:AGENT:HOLD — each phase has its own transformation, each transformation has its own intermediate state.

## Meta Concepts

### THE FURNACE Made Visual

The Knowledge Atomizer is the visual representation of THE FURNACE. Every tab in the UI corresponds to a stage of the metabolic process:

- **INGEST = TRUTH** — raw documents enter, unprocessed, full of noise
- **REFINE = MEANING** — extraction and enrichment apply cognitive fire to raw truth
- **STORE = CARE-INTERNAL** — the organism absorbs what it has learned
- **USE = CARE-EXTERNAL** — knowledge becomes offering through chat, content, plans

You can literally watch THE FURNACE operate by clicking through the tabs. Truth goes in the left side. Care comes out the right side.

### Compound Atomization

The Knowledge Atomizer embodies the core architectural innovation: **compound knowledge atoms**. When you upload multiple documents and process them together, the system doesn't just extract atoms from each document independently — it finds the **intersections**: emergences (insights that only exist across documents), contradictions (where documents disagree), amplifications (where documents reinforce each other), and transformations (where one document's atom becomes something new in the context of another).

This is knowledge that doesn't exist in any single document. It exists only in the *space between* documents. The Knowledge Atomizer is the tool that makes that space visible.

### The Triad — 3-Way Partnership Protocol

The Triad View implements Dr. David Lee's "Designed Resilience" research: two AIs peer-reviewing each other, with Jeremy making the final call. Scout provides initial analysis, Maverick challenges it, R1 synthesizes. Each has the RIGHT to disagree — "Caring Disobedience." This is not consensus-seeking; it's truth-seeking through structured conflict.

### Why It Exists

Jeremy needed a way to **see** the knowledge processing happen — to watch documents become atoms, to inspect enrichment dimensions, to verify that the extraction captured what mattered. The Knowledge Atomizer is the X-ray machine for the organism's digestive system. Without it, knowledge processing is invisible. With it, Jeremy can see every atom, every dimension, every connection.

### What It Wants To Become

The primary interface for all knowledge work in the Primitive product. Every Primitive customer should have their own Knowledge Atomizer instance, processing their documents, enriching their atoms, building their personal knowledge base. The 12-dimension enrichment should become automatic (LLM-scored), bulk processing should be the default, and the BigQuery export should be replaced by direct DuckDB persistence within the organism.

## Current Maturity

**Highly Developed** — This is one of the most feature-complete apps in the ecosystem. The full INGEST → REFINE → STORE → USE workflow is implemented. Multi-provider LLM support works. The type system is comprehensive. The UI is functional and navigable. Originally from Google AI Studio, now standalone.

Gaps: No direct integration with Genesis services (operates independently), no persistent backend (localStorage only), no multi-user support, no automated enrichment (manual per-dimension).

## HOLD:AGENT:HOLD Position

The Knowledge Atomizer spans both domains — it is a **ME Service** (Jeremy uses it to see and control knowledge processing) that wraps **NOT-ME Services** (the LLM extraction and enrichment are autonomous). It is the prosthetic hand operating the furnace controls.
