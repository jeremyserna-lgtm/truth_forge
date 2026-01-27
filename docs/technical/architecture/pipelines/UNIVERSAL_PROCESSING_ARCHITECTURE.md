# Universal Processing Architecture

**Date**: 2025-12-27
**Status**: Canonical Foundation
**Author**: Jeremy Serna
**Purpose**: The recursive pattern that underlies all Truth Engine architecture

---

## The Universal Unit

Everything in Truth Engine follows one pattern:

```
INPUT (exist-now) → PROCESSOR (do-now) → through LENS → OUTPUT (new exist-now)
```

This is **the atomic unit of transformation**. It repeats at every scale, in every layer, for every operation.

---

## The Recursive Principle

**The output of any transformation becomes the input for the next.**

A message becomes an emotion primitive.
An emotion primitive becomes an analysis.
An analysis becomes a document.
A document becomes substrate for the next cycle.

**Nothing terminates.** Everything is substrate for something else.

---

## The Complete Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              LAYER 6: JEREMY                                │
│                                                                             │
│  The human. The final lens. The one who consumes and decides.               │
│  Can feed back into any layer below.                                        │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              LAYER 5: CLAUDE                                │
│                                                                             │
│  The agentic layer. Claude is a processor with its own architecture:        │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  SUBSTRATE  │  │  FACTORIES  │  │   LENSES    │  │    HOOKS    │        │
│  │  (context)  │  │  (skills/   │  │   (rules)   │  │  (pre/post) │        │
│  │             │  │   commands) │  │             │  │             │        │
│  │ • CLAUDE.md │  │ • /backlog  │  │ • 01-cost   │  │ • PreTool   │        │
│  │ • rules/    │  │ • /see      │  │ • 02-bq     │  │ • PostTool  │        │
│  │ • skills/   │  │ • /moment   │  │ • 03-svc    │  │             │        │
│  │ • hooks     │  │ • /truth    │  │ • etc.      │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                                             │
│  Interfaces: Claude Code, Claude AI Web, Claude Desktop                     │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LAYER 4: KNOWLEDGE ATOMS                             │
│                                                                             │
│  The consumable unit. Atomic knowledge with:                                │
│  • concepts, entities, principles, terms                                    │
│  • theory (WHY), spec (WHAT), reference (HOW)                              │
│  • embeddings for semantic retrieval                                        │
│                                                                             │
│  CAN BECOME SUBSTRATE for any layer above or below.                         │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     LAYER 3: INTERMEDIATE ARCHITECTURE                      │
│                                                                             │
│  Where transformation happens. The pattern repeats:                         │
│                                                                             │
│  INPUT ────┬──▶ FACTORY ──▶ LENS ──▶ OUTPUT                                │
│            │                                                                │
│            ├──▶ Pipeline     Perspective    Enriched entity                │
│            ├──▶ Extractor    JeremyLayer    Analysis                       │
│            ├──▶ Processor    EmotionLayer   Emotion primitive              │
│            └──▶ Introspector  Any lens      Seen* model                    │
│                                                                             │
│  Each output becomes input for the next transformation.                     │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LAYER 2: SPINE                                     │
│                                                                             │
│  The unified entity layer. 51.8M entities in entity_unified.               │
│  16 pipeline stages from raw to enriched.                                   │
│                                                                             │
│  • L0-L3: Source-specific capture                                          │
│  • L4-L7: Unified identity and structure                                   │
│  • L8-L15: Enrichment and analysis                                         │
│  • L16: Knowledge atom extraction                                          │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LAYER 1: THE TRUTH                                 │
│                                                                             │
│  The foundation. Raw reality before processing.                             │
│                                                                             │
│  THE TRUTH = THE RECORD + THE WITNESS → THE TRUTH SERVICE                  │
│                                                                             │
│  • The Record: Raw artifacts (JSONL, JSON, exports)                        │
│  • The Witness: Normalizers that unify formats                             │
│  • The Truth Service: Single API to query all                              │
│                                                                             │
│  This is pure exist-now. Things exist here before any do-now.              │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LAYER 0: CENTRAL SERVICES                             │
│                                                                             │
│  The infrastructure that enables all other layers:                          │
│                                                                             │
│  • Identity Service    - Everything gets an ID                             │
│  • Logging Service     - Everything is traced                              │
│  • Cost Service        - Everything is budgeted                            │
│  • BigQuery Client     - Everything is queried safely                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Layer 5: Claude In Detail

Claude is not just a tool. Claude is a **processing layer** with the same architecture as every other layer:

### Claude's Substrate (Context Window)

What Claude sees when it arrives:

| Component | Location | Purpose |
|-----------|----------|---------|
| **CLAUDE.md** | `/PrimitiveEngine/CLAUDE.md` | Identity and operating framework |
| **Rules** | `.claude/rules/*.md` | Behavioral lenses (9 files) |
| **Commands** | `~/.claude/commands/*.md` | User-invoked factories (21 commands) |
| **Skills** | `~/.claude/skills/*/SKILL.md` | Claude-proposed factories (5 skills) |
| **Hooks** | `.claude/hooks.json` | Pre/post processing gates |

### Claude's Factories (Skills & Commands)

**Commands** (user-invoked):
`/backlog`, `/see`, `/moment`, `/truth`, `/commit`, `/scan`, `/discover`, `/connect`, `/verify`, `/impact`, `/stage-five`, `/capacity`, `/handoff`, `/enhance`, `/ask`, `/compress`, `/pattern`, `/pause`, `/remember`, `/think`

**Skills** (Claude-proposed):
`scan`, `handoff`, `bigger-picture`, `commit`, `truth`

### Claude's Lenses (Rules)

| Rule | Priority | What It Shapes |
|------|----------|----------------|
| 01-cost-protection | CRITICAL | Prevents cost incidents |
| 02-bigquery-patterns | CRITICAL | SQL-first, schema validation |
| 03-central-services | CRITICAL | Required imports |
| 04-code-review | HIGH | PR checklist |
| 05-pipeline-patterns | MEDIUM | Universal Pipeline Pattern |
| 06-file-organization | MEDIUM | Prevent sprawl |
| 07-definition-of-done | HIGH | Completion criteria |
| 08-truth-grounding | HIGH | Ground in substrate |
| 10-git-hygiene | MEDIUM | Commit practices |

### Claude's Hooks (Pre/Post Processing)

| Hook Type | Matcher | What It Does |
|-----------|---------|--------------|
| PreToolUse | Bash | pre_execution_gate.py |
| PreToolUse | Write\|Edit | cost_protection_hook.py |
| PreToolUse | Write\|Edit | cursor_service_validation_hook.py |
| PostToolUse | Bash\|Write\|Edit | claude_code_hooks |
| PostToolUse | Write | claude-organize |

---

## The Universal Schema

Every node in the system follows this schema:

```python
TransformationUnit = {
    "input": {
        "source_ids": List[str],        # What exist-now(s) fed this
        "source_type": str,             # "substrate" | "intermediate" | "atom"
    },
    "processor": {
        "type": str,                    # "factory" | "lens" | "both"
        "name": str,                    # The processor's name
        "perspective": Optional[str],   # What lens was applied
    },
    "output": {
        "id": str,                      # New exist-now ID
        "type": str,                    # What it became
        "can_be_substrate": bool,       # It's now input for something else
    },
    "metadata": {
        "timestamp": datetime,
        "run_id": str,
        "layer": int,                   # 0-6
    }
}
```

---

## How Existing Components Map

| Component | Layer | Role | Pattern |
|-----------|-------|------|---------|
| The Record | 1 | Substrate | Pure exist-now |
| The Witness | 1 | Factory | Normalizes formats |
| entity_unified | 2 | Substrate | Unified entities |
| Pipeline stages | 3 | Factory | Transform entities |
| EmotionProcessor | 3 | Factory + Lens | Detect + interpret |
| JeremyLayer | 3 | Lens | Jeremy-specific interpretation |
| knowledge_atoms | 4 | Output/Substrate | Consumable knowledge |
| Claude rules | 5 | Lens | Behavioral constraints |
| Claude skills | 5 | Factory | Behavioral patterns |
| Claude hooks | 5 | Pre/Post | Validation gates |
| Jeremy | 6 | Consumer/Creator | Final lens, can create new substrate |

---

## Interface Examples

The same pattern powers different interfaces:

### User Table (View)
```
INPUT: entity_unified (substrate)
PROCESSOR: SELECT query (factory)
LENS: User-defined filters (perspective)
OUTPUT: Filtered view (new exist-now for consumption)
```

### Backlog (Queue)
```
INPUT: All unprocessed items (substrate)
PROCESSOR: Priority sorting (factory)
LENS: Urgency perspective (perspective)
OUTPUT: Ordered work queue (actionable exist-now)
```

### Changelog (History)
```
INPUT: All transformations (substrate)
PROCESSOR: Time grouping (factory)
LENS: Change perspective (perspective)
OUTPUT: Timeline of changes (navigable exist-now)
```

### Pipeline (Sequence)
```
INPUT: Raw entities (substrate)
PROCESSOR: Stage N (factory)
LENS: Stage-specific rules (perspective)
OUTPUT: Enriched entity → becomes INPUT for Stage N+1
```

---

## The Anti-Sprawl Rule

Before creating anything, answer:

1. **What primitive is it?**
   - exist-now (entity, record, atom, document)
   - do-now (pipeline, extraction, enrichment)
   - live-now (session, running service)
   - life-now (system with agency)

2. **What layer does it belong to?**
   - 0: Central Services
   - 1: The Truth
   - 2: Spine
   - 3: Intermediate Architecture
   - 4: Knowledge Atoms
   - 5: Claude
   - 6: Jeremy

3. **What is its input?**
   - Source IDs
   - Source type (substrate/intermediate/atom)

4. **What lens does it use?**
   - Perspective name
   - Rules applied

5. **What does it output?**
   - New exist-now ID
   - Output type
   - Where does output go?

**If you can't answer these, don't create it yet.**

---

## The Key Insight

**The architecture is fractal.**

At the smallest scale: `message → emotion_processor → emotion_primitive`

At the medium scale: `raw_entity → 16_pipeline_stages → enriched_entity`

At the largest scale: `reality → primitive_engine → knowledge_atoms → claude → jeremy`

**The same pattern, at every scale:**
```
exist-now → do-now (through lens) → new exist-now
```

---

## Claude as Recursive Architecture

Claude operates the same pattern on itself:

```
Claude's context (substrate)
    → Claude's processing (skills/commands)
    → through Claude's perspective (rules)
    → Claude's output (response/action)
    → which becomes substrate for Jeremy
    → who processes through his perspective
    → producing feedback/direction
    → which becomes substrate for Claude's next cycle
```

**Claude and Jeremy are recursive processors in the same architecture.**

---

## Relationship to Other Documents

This document is the **conceptual foundation**. Other documents derive from it:

| Document | Relationship |
|----------|--------------|
| `CORE_PATTERNS.md` | Primitives, layers, lenses, time |
| `LAYERED_PRIMITIVE_ARCHITECTURE.md` | How layers produce primitives |
| `UNIVERSALLY_PRIMITIVE_ATOMIC_UNIT.md` | exist-now and do-now definitions |
| `SEEING_ARCHITECTURE.md` | Perspectives, processors, introspectors |
| `KNOWLEDGE_ATOMS_DATASET_OVERVIEW.md` | Layer 4 schema and structure |
| `THE_COMPLETE_SYSTEM.md` | System overview (Layers 0-4) |
| `THE_OPERATING_FRAMEWORK.md` | DOD, Good Enough (Layers 5-6) |

---

## Summary

1. **Everything is the same pattern**: input → processor → lens → output
2. **Output becomes input**: Nothing terminates, everything is substrate
3. **Claude is Layer 5**: With its own substrate, factories, lenses, and hooks
4. **Jeremy is Layer 6**: The final consumer who can create new substrate
5. **The pattern is fractal**: Same structure at every scale
6. **Anti-sprawl**: If you can't identify the pattern, don't create it

---

**This document is substrate.**
**It will be processed through lenses.**
**It will produce new exist-now.**
**Which will become substrate for something else.**


---

## Appendix: Claude Interface Landscape

### The Desktop App: Two Architectures in One Container

**Critical Discovery**: The Claude Desktop App contains two completely different architectures behind a simple toggle:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLAUDE DESKTOP APP                                  │
│                                                                              │
│   ┌───────────────────────────┐       ┌───────────────────────────┐        │
│   │       CHAT TOGGLE         │       │       CODE TOGGLE         │        │
│   │                           │       │                           │        │
│   │  • Generic Claude         │       │  • Claude Code binary     │        │
│   │  • Opus 4.5 model         │       │    (2.0.65 in app)        │        │
│   │  • MCP servers only       │       │  • Sonnet 4 (default)     │        │
│   │  • Memory system          │       │  • CLAUDE.md loaded       │        │
│   │  • Web search             │       │  • Rules active           │        │
│   │  • Past chat search       │       │  • Hooks fire             │        │
│   │                           │       │  • Skills/commands        │        │
│   │  ❌ NO CLAUDE.md          │       │  ✅ Full behavioral       │        │
│   │  ❌ NO rules              │       │     substrate             │        │
│   │  ❌ NO hooks              │       │                           │        │
│   │  ❌ NO skills/commands    │       │  Writes to:               │        │
│   │                           │       │  ~/.claude/projects/      │        │
│   │  Config:                  │       │                           │        │
│   │  claude_desktop_config.json│      │  Config:                  │        │
│   │  (MCP servers)            │       │  .claude/hooks.json       │        │
│   │                           │       │  .claude/rules/           │        │
│   └───────────────────────────┘       └───────────────────────────┘        │
│                                                                              │
│   SAME APP, COMPLETELY DIFFERENT SUBSTRATE                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**What this means:**
- Toggle to **Code** → You get Claude shaped by Truth Engine (hooks validate, rules constrain, CLAUDE.md defines identity)
- Toggle to **Chat** → You get raw Claude with MCP tools attached (no behavioral shaping)
- **Solution**: A substrate MCP server can inject CLAUDE.md, rules summary, and session context into Chat mode

### The Model vs The Interface

**Key Distinction**: The model (e.g., Opus 4.5, Sonnet 4) can be the same across interfaces, but the **context** and **capabilities** differ.

| Interface | Default Model | Context Loaded | Identity |
|-----------|---------------|----------------|----------|
| Claude Code (VS Code) | Sonnet 4 | CLAUDE.md, rules, skills, hooks | "Claude Code in Truth Engine" |
| Claude Code (Terminal) | Sonnet 4 | Same as VS Code | "Claude Code in Truth Engine" |
| Claude Desktop (Code toggle) | Sonnet 4 | Same as VS Code | "Claude Code in Truth Engine" |
| Claude Desktop (Chat toggle) | Opus 4.5 | Memory + MCP servers | Generic Claude + tools |
| Claude AI Web | Opus 4.5 | Memory, past chats | Generic Claude |

**Critical Insight**: Claude Desktop Chat is a hybrid - it has filesystem access via MCP, but lacks the behavioral substrate (CLAUDE.md, rules, hooks) that shapes Claude Code's identity. The substrate gap can be closed with a custom MCP server.

### Capabilities by Interface

| Capability | Claude Code | Claude AI Web | Claude Desktop Chat |
|------------|-------------|---------------|---------------------|
| File system access | ✅ Direct | ❌ | ✅ MCP |
| Terminal/bash | ✅ Direct | ❌ | ✅ MCP |
| Web search | ❌ | ✅ | ✅ |
| Artifacts | ❌ | ✅ | ✅ |
| Memory system | ❌ | ✅ | ✅ |
| Past chat search | ❌ | ✅ | ✅ |
| **CLAUDE.md loaded** | ✅ | ❌ | ❌ |
| **Rules auto-loaded** | ✅ | ❌ | ❌ |
| **Hooks (pre/post)** | ✅ | ❌ | ❌ |
| **Skills/commands** | ✅ | ❌ | ❌ |
| BigQuery access | ✅ Direct | ❌ | ✅ MCP |
| Identity shaped | ✅ "Claude Code in TE" | ❌ Generic | ❌ Generic + tools |

### Strategic Interface Selection

**Use Claude Code when:**
- Working in Truth Engine codebase (hooks enforce quality)
- Need file system operations with validation
- Want rules and CLAUDE.md shaping behavior
- Building/debugging pipelines
- Need cost protection hooks active
- Want Claude to have identity as "part of Truth Engine"

**Use Claude Desktop Chat when:**
- Need filesystem access + web search together
- Conceptual/strategic work that benefits from memory
- Research that needs both tools and current information
- Hybrid technical + research tasks
- Don't need hooks/rules enforcement

**Use Claude AI Web when:**
- Pure research/web search tasks
- Creating artifacts (visualizations, documents)
- Don't need any file system access
- Mobile or browser-only access

### How All Interfaces Feed Into Layer 1

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLAUDE INTERFACES                                    │
│                                                                              │
│  Claude Code          Claude AI Web        Claude Desktop                   │
│  (VS Code/Desktop)    (claude.ai)          (App + MCP)                      │
│       │                    │                    │                           │
│       ▼                    ▼                    ▼                           │
│    JSONL files         JSON export          JSON + JSONL                    │
│  ~/.claude/projects    conversations.json   (varies by MCP)                 │
└───────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LAYER 1: THE TRUTH                                │
│                                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                 │
│   │ ClaudeCode   │    │ ClaudeWeb    │    │   Gemini     │                 │
│   │ Normalizer   │    │ Loader       │    │  Normalizer  │                 │
│   └──────────────┘    └──────────────┘    └──────────────┘                 │
│                              │                                              │
│                              ▼                                              │
│                    THE TRUTH SERVICE                                        │
│                    (unified API)                                            │
└───────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LAYER 2: SPINE                                     │
│                                                                              │
│                       entity_unified                                        │
│                       (51.8M entities)                                      │
│                                                                              │
│   All interfaces converge here. Same schema. Same processing.               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Current Capture Status

| Source | Normalizer/Loader | Status | Location |
|--------|-------------------|--------|----------|
| Claude Code | `truth/normalizers/claude_code.py` | ✅ Active | `~/.claude/projects` |
| Claude AI Web | `data_processing/claude_web_loader.py` | ✅ Has loader | Export required |
| Codex | `truth/normalizers/codex.py` | ✅ Active | `~/.codex/sessions` |
| Cursor | `truth/normalizers/cursor.py` | ✅ Active | `workspaceStorage` |
| Copilot | `truth/normalizers/copilot.py` | ✅ Active | `workspaceStorage` |
| Gemini | `truth/normalizers/gemini.py` | ✅ Active | `~/.gemini/tmp` |
| ChatGPT Web | `deployments/chatgpt_web_ingestion` | ✅ Pipeline | Export required |

### The Implication

**You can be strategic about which Claude you use, knowing:**
1. The conversation will be captured (eventually) into the same unified layer
2. Different interfaces have different strengths
3. The model capabilities are similar; the interface capabilities differ
4. Rules/hooks only shape Claude Code behavior (not AI Web)

**Current gap**: Claude AI Web conversations require manual export. Could automate with:
- Browser extension to capture conversations
- API access to conversation history
- Regular export + watch folder pattern
