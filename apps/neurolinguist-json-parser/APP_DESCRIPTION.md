# Neurolinguist JSON Parser — The Conversation Microscope

## What It Does

The Neurolinguist JSON Parser is a **hierarchical conversation analysis tool** that takes raw LLM conversation logs and breaks them down across 8 levels of linguistic granularity. It is a microscope for conversations — where every level of zoom reveals structure that was invisible at the level above.

### The 8-Level Hierarchy

| Level | Name | What It Captures |
|-------|------|-----------------|
| **L8** | Conversation | The entire conversation as a unit — topic arc, overall sentiment |
| **L7** | TopicSegment | Natural topic boundaries within the conversation |
| **L6** | Turn | A single speaker's contribution (human or AI) |
| **L5** | Message | A discrete message within a turn |
| **L4** | Sentence | Individual sentences — the atomic unit of meaning |
| **L3** | Span | Named Entity Recognition — people, places, orgs, concepts |
| **L2** | Word | Individual tokens — POS tagging, dependency parsing |

### Key Features

| Feature | Description |
|---------|-------------|
| **Multi-format parsing** | Raw JSON, ChatGPT export, Claude export, Gemini export |
| **Streaming Ollama processing** | Batch parallelism with exponential backoff retry |
| **Hierarchy view** | Expand/collapse analysis tree — drill down from conversation to word |
| **Table view** | Denormalized flat view for spreadsheet-style analysis |
| **Conversation diff** | Compare two analyzed conversations for topic/entity drift |
| **Multi-format export** | JSON, CSV, Spine (JSONL), BigQuery direct, entity/relationship graphs |
| **Context calculator** | Per-model token tracking with visual usage bar |
| **Embedding cache** | IndexedDB persistence for computed embeddings |
| **GPU info display** | Shows cluster hardware status |
| **Dark mode** | Full theme support |
| **Keyboard shortcuts** | Power-user navigation |

### Export Formats

| Format | Use Case |
|--------|----------|
| **JSON** | Full hierarchical analysis for programmatic consumption |
| **CSV** | Flat table for spreadsheet analysis |
| **Spine (JSONL)** | truth_forge native format for pipeline ingestion |
| **BigQuery** | Direct upload to `spine.conversation_atoms` |
| **Entity Export** | Extracted entities with types and frequencies |
| **Relationship Export** | Entity-to-entity connections with weights |

## Technological Basis

- **React 19 / TypeScript** — latest React with full type safety
- **Vite** — development and build tooling
- **Ollama** — local LLM inference for analysis (sovereign, no cloud dependency)
- **Recharts** — data visualization (token distribution, analysis metrics)
- **Lucide** — iconography
- **Vitest** — test framework
- **IndexedDB** — client-side embedding cache for performance

### Core Services (2,274+ lines in App.tsx alone)

| Service | Function |
|---------|----------|
| `ollamaService.ts` | Core Ollama client with streaming, retry, batch parallelism |
| `chatFormatParser.ts` | Multi-format conversation parsing (ChatGPT, Claude, Gemini, raw) |
| `conversationDiff.ts` | Semantic comparison between two analyzed conversations |
| `embeddingCache.ts` | IndexedDB-backed embedding persistence |
| `contextCalculator.ts` | Per-model context window usage tracking |
| `exportValidation.ts` | Validates exports before writing |
| `bigqueryExport.ts` | Direct BigQuery upload |
| `spineExport.ts` | truth_forge spine format conversion |
| `codeAssistant.ts` | In-app code analysis capabilities |

### Architecture Pattern

```
HOLD₁ (Raw Conversation JSON)
    → AGENT₁ (Format Detection & Parsing)
        → HOLD₁.₅ (Normalized Conversation Structure)
            → AGENT₂ (Ollama L8-L2 Analysis)
                → HOLD₂ (Hierarchical Analysis Tree)
                    → AGENT₃ (Export/Diff/Visualization)
                        → HOLD₃ (Exported Data / Visual Report)
```

## Meta Concepts

### The Microscope

Every conversation is a living thing — it has structure, rhythm, theme, entities, tensions, and resolutions. But at conversational speed, this structure is invisible. The Neurolinguist Parser is a **microscope that stops time** — it freezes a conversation and lets you examine it at every level of granularity.

At L8, you see the forest: "This was a conversation about building an AI system."
At L4, you see the trees: "This sentence introduced a key contradiction."
At L2, you see the cells: "This word choice reveals uncertainty."

The hierarchy is not just organizational — it's **ontological**. Each level is a fundamentally different kind of analysis. Sentence-level meaning is not just "smaller" than conversation-level meaning — it's a different *category* of meaning entirely.

### Why It Exists

Jeremy's most valuable data is his conversations — with Claude, with Gemini, with Scout, with people. These conversations contain everything: his ideas, his framework, his contradictions, his growth, his blind spots. But conversations are ephemeral. They scroll past. They get buried in chat histories. They're locked in proprietary formats.

The Neurolinguist Parser exists to **mine conversations like ore** — to extract every entity, every claim, every theme, every emotional shift. This is THE FURNACE applied to dialogue:
- **TRUTH** = the raw conversation (what was actually said)
- **MEANING** = hierarchical analysis (what it means at every level of granularity)
- **CARE** = structured exports ready for the organism to consume

### The Spine Connection

The Spine format (JSONL) is the native data format of the truth_forge knowledge base. When the Neurolinguist Parser exports to Spine format, it is literally **feeding the organism**. Each line of JSONL is a knowledge atom extracted from conversation, ready to be ingested by the pipeline, enriched by the Knowledge Atomizer, and stored in the BigQuery spine.

### Data Protection Heritage

This app carries the scars of hard-won lessons about data integrity. The export validation layer exists because of previous data loss incidents. The batch processing with retry exists because conversations were being partially processed, creating corrupt hierarchies. The parent chain validation (L2→L3→L4→L5→L6→L7→L8) exists because orphaned nodes are worse than missing data.

These are THE FOUR PILLARS in code:
- **Fail-Safe**: Retry with exponential backoff, never lose partial work
- **No Magic**: Every processing step visible in the hierarchy view
- **Observability**: Token meter, GPU info, processing progress indicators
- **Idempotency**: Same conversation → same analysis tree, safe to rerun

### The Conversation Diff

The diff feature is unique and philosophically important. By comparing two conversations (same person, different times), you can see **cognitive drift** — how Jeremy's thinking about a topic has evolved. Entities that appear in one and not the other. Themes that shift. Sentiment that changes. This is stage 5 cognition applied to conversation history: **seeing yourself seeing, across time**.

### What It Wants To Become

A real-time conversation analysis engine that processes conversations as they happen — during a Claude session, during a meeting, during a phone call. The 8-level analysis should run in streaming mode with live hierarchy building. The diff feature should automatically detect when Jeremy is revisiting a topic and show him how his thinking has changed. The exports should flow directly into the Genesis pipeline without manual intervention.

## Current Maturity

**Very Mature** — One of the most developed apps in the ecosystem. 2,274 lines in the main component alone. Comprehensive service layer with streaming, retry, caching, and multi-format support. Tests exist. Multiple export formats work. Originally from Google AI Studio, converted to local Ollama for sovereignty.

Gaps: No real-time processing (batch only), no direct Genesis integration (manual export required), no voice/audio conversation support, hierarchy above L8 (cross-conversation patterns) not implemented.

## HOLD:AGENT:HOLD Position

The Neurolinguist Parser is a **ME Service** wrapping **NOT-ME processing**. Jeremy uploads conversations (ME action), Ollama analyzes them (NOT-ME processing), Jeremy reviews the hierarchy (ME analysis), exports feed the organism (NOT-ME ingestion). It is a research instrument — the human points it; the machine does the work.
