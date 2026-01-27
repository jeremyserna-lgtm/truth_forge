# Knowledge Atom Infrastructure

**Version**: 2.0.0
**Date**: 2025-12-29
**Status**: APPROVED

---

## Quick Reference: The Boolean Gates Schema

**An atom is: THE SENTENCE + TIME + COST + BOOLEAN GATES + DETAILS (optional)**

```
CORE:        content (noun + verb), at (timestamp), cost (money)
BOOLEANS:    did? right? efficient? used? fresh? friend? human? me? money?
DETAILS:     what_action (verb), what_type (noun), who_did, who_about, what_aspect
```

**The LLM standardizes to: NOUN + VERB**
- NOUN basket: `pipeline`, `database`, `llm`, `tool`, `person`, `conversation`, `system`
- VERB basket: `created`, `started`, `processed`, `completed`, `failed`, `stopped`

**Full schema**: See [The Lenses (Boolean Gates + Details)](#the-lenses-boolean-gates--details)

---

## The Consumption Layer (How Truth Flows Out)

**Truth flows to different consumers through different membranes:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                              TRUTH                                          │
│                                │                                            │
│                                ▼                                            │
│                    ┌──────────────────────┐                                 │
│                    │   KNOWLEDGE ATOMS    │                                 │
│                    │      (DuckDB)        │                                 │
│                    └──────────┬───────────┘                                 │
│                               │                                             │
│              ┌────────────────┼────────────────┐                            │
│              │                │                │                            │
│              ▼                ▼                ▼                            │
│        ┌──────────┐    ┌──────────┐    ┌──────────┐                        │
│        │   LLM    │    │   Code   │    │   Code   │                        │
│        │(Claude)  │    │(membrane)│    │(membrane)│                        │
│        └────┬─────┘    └────┬─────┘    └────┬─────┘                        │
│             │               │               │                               │
│             ▼               ▼               ▼                               │
│        ┌──────────┐   ┌──────────┐   ┌──────────┐                          │
│        │  JEREMY  │   │ PIPELINE │   │DASHBOARD │                          │
│        │          │   │          │   │          │                          │
│        │ docs     │   │normalized│   │normalized│                          │
│        │ sheets   │   │ atoms    │   │ atoms    │                          │
│        └──────────┘   └──────────┘   └──────────┘                          │
│                                                                              │
│   Jeremy: LLM membrane → Documents & Spreadsheets                          │
│   Systems: Code membrane → Normalized atoms                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Two Types of Consumers

| Consumer | Membrane | Output | Format |
|----------|----------|--------|--------|
| **Jeremy** | LLM (Claude) | Documents, Spreadsheets | Human-readable |
| **Systems** | Code | Normalized atoms | Machine-readable |

### Why Different Membranes

**LLM Membrane (for humans):**
- Transforms boolean gates into natural language
- "This pipeline failed" instead of `{did: true, right: false, what_type: "pipeline"}`
- Produces docs Jeremy can read
- Produces sheets Jeremy can analyze

**Code Membrane (for systems):**
- Reads atoms directly from DuckDB
- Applies transformations programmatically
- Feeds pipelines and dashboards
- Keeps atoms in normalized form

### The External System Pattern

**External systems query through the code membrane:**

```python
# External system queries atoms
atoms = query("SELECT * FROM atoms WHERE money = TRUE AND what_type = 'pipeline'")

# System applies its own logic
for atom in atoms:
    if atom.what_action == 'failed':
        alert(atom.content)
```

**The LLM standardizes; external systems do their own filtering.**

---

## The Document Service (Jeremy's Interface)

**Jeremy can only read documents. That's why documents have always been central.**

### The Problem: Claude Was Over-Documenting

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   CLAUDE                                                                    │
│   ──────                                                                    │
│                                                                              │
│   Sees: What Jeremy SAYS (words, conversation)                              │
│   Sees: BigQuery/atoms (truths)                                             │
│                                                                              │
│   Can: Think                                                                │
│   Can: Talk                                                                 │
│   Can: Just BE                                                              │
│   Can: Make documents (but shouldn't always)                                │
│                                                                              │
│   THE PROBLEM:                                                              │
│   Claude was making too many documents.                                     │
│   Converting markdown into more markdown.                                   │
│   Formalizing everything.                                                   │
│                                                                              │
│   WHAT CLAUDE SHOULD DO:                                                    │
│   Convert Jeremy's WORDS.                                                   │
│   Not convert documents into documents.                                     │
│   Just think. Just talk. Just be.                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Claude's Modes

| Mode | What It Means | When |
|------|---------------|------|
| **Think** | Process, reason, understand | Most of the time |
| **Talk** | Converse with Jeremy | When Jeremy is talking |
| **Be** | Just exist, no output needed | When nothing needs doing |
| **Document** | Convert words to document | Only when Jeremy's WORDS need capturing |

### What To Convert (And What Not To)

| Source | Make Document? | Why |
|--------|----------------|-----|
| Jeremy's spoken words | ✅ Yes | This is the job - capture his words |
| Existing markdown | ❌ No | Already a document |
| Other documents | ❌ No | Don't reformat documents |
| Conversation with Jeremy | ✅ Yes | His words become document |

### The Two LLMs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                           TWO LLMs, TWO ORIENTATIONS                        │
│                                                                              │
│   ┌─────────────────────────────────┐    ┌─────────────────────────────────┐│
│   │     CLAUDE CODE (Worker)        │    │    DOCUMENT SERVICE LLM         ││
│   │                                 │    │                                 ││
│   │  Orientation: DO things         │    │  Orientation: MAKE documents    ││
│   │  Also: makes documents          │    │  Only: makes documents          ││
│   │                                 │    │                                 ││
│   │  "Execute this task"            │    │  "I need to see X"              ││
│   │  "Build this feature"           │    │  "Show me what happened"        ││
│   │  "Fix this bug"                 │    │  "Make a report about Y"        ││
│   └─────────────┬───────────────────┘    └─────────────┬───────────────────┘│
│                 │                                      │                    │
│                 │ produces atoms                       │ consumes atoms     │
│                 │ (as byproduct)                       │ (as primary input) │
│                 ▼                                      ▼                    │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                       KNOWLEDGE ATOMS (DuckDB)                       │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│                         ┌──────────────────────┐                           │
│                         │     DOCUMENTS        │                           │
│                         │                      │                           │
│                         │  → Jeremy reads ←    │                           │
│                         └──────────────────────┘                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Two Orientations

| LLM | Orientation | What It Does | Jeremy Says |
|-----|-------------|--------------|-------------|
| **Claude Code** | DO things | Execute tasks, produce atoms as byproduct, also makes docs | "Build X", "Fix Y", "Run Z" |
| **Document Service** | MAKE documents | Consume atoms, always thinking "I need to make a document" | "Show me X", "I need to look at Y" |

### The Document Service LLM (Chatbot)

**Its sole job is to make documents from Knowledge Atoms.**

Jeremy talks to it naturally:
- "I need to look at this information"
- "Make a document about my relationships"
- "What did the pipeline do today?"
- "Show me what I've been working on"

**It always thinks:** "I need to make a document."

Everything Jeremy says, it interprets through that lens:
- Jeremy says something → How do I make a document about this?
- Query the atoms → Apply a lens → Generate document → Jeremy reads

### Why Two LLMs

| Problem | Solution |
|---------|----------|
| Claude Code is doing too much | Split the document work off |
| Documents are a core need | Dedicated LLM for it |
| Natural language is the interface | Chatbot that understands document intent |
| Atoms are the substrate | Both LLMs produce/consume atoms |

### Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| **Knowledge Atoms Schema** | ✅ Designed | This document |
| **DuckDB Storage** | ✅ Designed | Local persistence |
| **Claude Code** | ✅ Exists | Does things, makes docs |
| **Document Service LLM** | 🔨 Build This | Chatbot for document generation |
| **/document command** | ✅ Exists | `~/.claude/commands/document.md` |
| **DocumentGenerator** | ✅ Exists | `narrative_core.DocumentGenerator` |

### Why Documents Are Central

**Documents have always been the base because:**
- Jeremy can only read documents
- Everything flows TO documents (for Jeremy)
- Everything flows FROM documents (for extraction)

```
             EXTRACTION                          DOCUMENT SERVICE
                  │                                    │
                  ▼                                    ▼
┌──────────────────────┐                  ┌──────────────────────┐
│    Documents         │                  │   Knowledge Atoms    │
│    (source)          │  ───────────►    │   (processed)        │
│                      │                  │                      │
│    - conversations   │    LLM           │    - boolean gates   │
│    - markdown        │    extracts      │    - noun + verb     │
│    - exports         │    truth         │    - standardized    │
└──────────────────────┘                  └──────────────────────┘
                                                    │
                                                    │  DOCUMENT SERVICE
                                                    │  generates
                                                    ▼
                                          ┌──────────────────────┐
                                          │    Documents         │
                                          │    (output)          │
                                          │                      │
                                          │    - reports         │
                                          │    - summaries       │
                                          │    - spreadsheets    │
                                          └──────────────────────┘
```

### The Document Service Pattern

**Using the existing infrastructure:**

```python
from architect_central_services.narrative_core import DocumentGenerator

# The DocumentGenerator already exists
generator = DocumentGenerator(project_id="flash-clover-464719-g1")

# Create document from atoms
doc = generator.create_document(
    topic="what I did today",
    lens="Furnace",           # Lens determines voice/structure
    container="L8C",          # Container determines format
    query_atoms=True,         # Query knowledge atoms
    max_atom_results=10,
)

# doc.content = the generated document
# doc.id = narrative ID (narr_xxxxx)
# Automatically persisted to BigQuery
```

**What the Document Service LLM would add:**

```python
# Jeremy says: "Show me what happened with the pipeline"
# Document Service LLM interprets:

# 1. Parse intent → "document about pipeline activity"
# 2. Query atoms
atoms = query("SELECT * FROM atoms WHERE what_type = 'pipeline' AND did = TRUE")

# 3. Generate document using existing infrastructure
doc = generator.create_document(
    topic="pipeline activity",
    lens="Technical",
    container="L8C",
    context=atoms,  # Feed the queried atoms
)

# Output: A document Jeremy can read
```

### The Lens Pattern

**Lenses determine voice and structure. Boolean gates determine content.**

**Existing Lenses (from `/document` command):**

| Lens | Voice | Use For |
|------|-------|---------|
| **Furnace** | Raw truth → forged meaning → delivered with care | Personal transformation, the Jeremy pattern |
| **Mythic** | Third-person omniscient, elevated | Epic narratives, archetypal stories |
| **Technical** | Precise, structured | Documentation, specifications |
| **Memoir** | First-person, reflective | Personal stories |
| **Philosophical** | Abstract, conceptual | Theory documents |
| **Instructional** | Clear, actionable | How-to guides |

**Boolean Gates → Content Selection:**

| What Jeremy Wants | Boolean Filter | Lens |
|-------------------|----------------|------|
| "What happened today?" | `did = TRUE` | Technical or Furnace |
| "Show me relationships" | `friend = TRUE` | Memoir or Mythic |
| "Pipeline status" | `what_type = 'pipeline'` | Technical |
| "Cost report" | `money = TRUE` | Technical |
| "What did I learn?" | `right = TRUE` | Philosophical |
| "What went wrong?" | `right = FALSE` | Furnace |

**The Flow:**
1. Jeremy speaks naturally → Document Service LLM interprets
2. Intent → Boolean filter (what atoms to query)
3. Intent → Lens selection (what voice to use)
4. Query atoms → Apply lens → Generate document
5. Jeremy reads document

---

## The Universal Pattern

**Every system follows the same pattern:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        THE UNIVERSAL PATTERN                             │
│                                                                          │
│   Every system:                                                         │
│   1. DOES things                                                        │
│   2. LOGS what it did (JSONL)                                          │
│   3. BACKLOGS what needs doing                                         │
│                                                                          │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐           │
│   │     DO       │     │     LOG      │     │   BACKLOG    │           │
│   │              │     │   (JSONL)    │     │              │           │
│   │  Execution   │ ──► │  What was    │     │  What needs  │           │
│   │              │     │  done        │     │  doing       │           │
│   └──────────────┘     └──────┬───────┘     └──────┬───────┘           │
│                               │                     │                    │
│                               └──────────┬──────────┘                    │
│                                          │                               │
│                                          ▼                               │
│                              ┌──────────────────────┐                   │
│                              │   LLM EXTRACTION     │                   │
│                              │                      │                   │
│                              │   Reads logs         │                   │
│                              │   Reads backlog      │                   │
│                              │   Extracts atoms     │                   │
│                              └──────────┬───────────┘                   │
│                                          │                               │
│                                          ▼                               │
│                              ┌──────────────────────┐                   │
│                              │  KNOWLEDGE ATOMS     │                   │
│                              │      (DuckDB)        │                   │
│                              └──────────────────────┘                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**That's it. JSONL logs + Backlog. Everything else follows.**

---

## The Membrane Architecture

**JSONL and DuckDB are membranes. The Knowledge Atom System is the holding.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        THE MEMBRANE ARCHITECTURE                         │
│                                                                          │
│   JSONL                KNOWLEDGE ATOM SYSTEM              DuckDB        │
│   ─────                ─────────────────────              ──────        │
│                                                                          │
│   Intake Membrane      THE HOLDING                  Query Membrane      │
│   (PUT IN)             (What's held)                (PULL OUT)          │
│                                                                          │
│       │                        │                          ▲              │
│       │                        │                          │              │
│       └────────────► ◆ ◆ ◆ ◆ ◆ ────────────────────────────┘              │
│                     Knowledge                                            │
│                      Atoms                                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| Component | Role | What It Does |
|-----------|------|--------------|
| **JSONL** | Intake Membrane | PUT IN - systems write here |
| **Knowledge Atom System** | The Holding | What's held - structured knowledge |
| **DuckDB** | Query Membrane | PULL OUT - optimized retrieval |

**JSONL and DuckDB are just adapters for the Knowledge Atom System.**

---

## JSONL: The Intake Membrane

**JSONL is the membrane for putting things INTO the holding.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    JSONL: INTAKE MEMBRANE                                │
│                                                                          │
│   Systems write here:                                                   │
│   ├── Conversations log here                                            │
│   ├── Backlog items go here                                             │
│   ├── Events append here                                                │
│   └── Observations land here                                            │
│                                                                          │
│   Optimized for: APPEND (put in)                                        │
│   Not optimized for: QUERY (pull out)                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| Role | Optimized? | Why |
|------|------------|-----|
| **PUT IN** | ✅ Yes | Just append a line |
| **PULL OUT** | ❌ No | Must scan all lines |

**JSONL can be read directly** - it's just not optimized for it. The internal layers can pull from JSONL, but DuckDB is the optimized query membrane.

---

## DuckDB: The Query Membrane

**DuckDB is the membrane for pulling things OUT of the holding.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DUCKDB: QUERY MEMBRANE                                │
│                                                                          │
│   Systems read here:                                                    │
│   ├── Complex queries                                                   │
│   ├── Vector similarity search                                          │
│   ├── Temporal filtering                                                │
│   └── Full-text search                                                  │
│                                                                          │
│   Optimized for: QUERY (pull out)                                       │
│   Not used for: INTAKE (put in)                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| Role | Optimized? | Why |
|------|------------|-----|
| **PULL OUT** | ✅ Yes | SQL, vectors, indexing |
| **PUT IN** | ❌ No | JSONL is the intake membrane |

---

## The Complete Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   Systems write to JSONL (intake membrane)                              │
│       │                                                                  │
│       │  Knowledge Atom Extraction                                      │
│       │  (reads JSONL, structures atoms)                                │
│       │                                                                  │
│       ▼                                                                  │
│   Knowledge Atoms (the holding)                                         │
│       │                                                                  │
│       │  Stored in DuckDB (query membrane)                              │
│       │                                                                  │
│       ▼                                                                  │
│   Systems query DuckDB (optimized pull out)                             │
│       │                                                                  │
│       │  Periodic sync                                                  │
│       │                                                                  │
│       ▼                                                                  │
│   BigQuery (cloud permanence)                                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| Layer | Role | Use |
|-------|------|-----|
| **JSONL** | Intake Membrane | PUT IN |
| **Knowledge Atoms** | The Holding | Structured truth |
| **DuckDB** | Query Membrane | PULL OUT |
| **BigQuery** | Cloud Permanence | Long-term, cross-system |

---

## The One-End vs Both-Ends Pattern

**Every system has ONE end. The Knowledge Atom System has BOTH.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE CRITICAL DISTINCTION                         │
│                                                                          │
│   NORMAL SYSTEMS (ONE END)                                              │
│   ────────────────────────                                              │
│                                                                          │
│   Either:                                                               │
│   ├── Write end (put to JSONL) - loggers, intake                       │
│   └── Read end (pull from DuckDB) - consumers, clients                 │
│                                                                          │
│   Never both.                                                           │
│                                                                          │
│                                                                          │
│   KNOWLEDGE ATOM SYSTEM (BOTH ENDS)                                     │
│   ──────────────────────────────────                                    │
│                                                                          │
│   Has:                                                                  │
│   ├── Write end (reads JSONL from all sources)                         │
│   └── Read end (exposes DuckDB for all consumers)                      │
│                                                                          │
│   It's the ONLY system that bridges both membranes.                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| System Type | JSONL (Intake) | DuckDB (Query) | Role |
|-------------|----------------|----------------|------|
| **Loggers** | ✅ Writes to | ❌ Doesn't read | One end (PUT IN) |
| **Consumers** | ❌ Doesn't write | ✅ Reads from | One end (PULL OUT) |
| **Knowledge Atom System** | ✅ Reads AND Writes | ✅ Reads AND Writes | **BOTH ENDS, BOTH DIRECTIONS** |

**The Knowledge Atom System is fully bidirectional on both membranes.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FULL BIDIRECTIONALITY                                 │
│                                                                          │
│   EXTERNAL SYSTEMS                KNOWLEDGE ATOM SYSTEM                 │
│                                                                          │
│   ┌─────────────┐                 ┌─────────────────────┐               │
│   │   Logger    │ ─── write ───► │                     │               │
│   │   System    │                 │                     │               │
│   └─────────────┘                 │                     │               │
│                                   │      JSONL          │               │
│   ┌─────────────┐                 │    (Intake)         │               │
│   │   Intake    │ ─── write ───► │                     │               │
│   │   System    │                 │   read ◄───┐        │               │
│   └─────────────┘                 │   write ───┘        │               │
│                                   │                     │               │
│                                   │                     │               │
│   ┌─────────────┐                 │                     │               │
│   │  Consumer   │ ◄─── read ──── │      DuckDB         │               │
│   │   System    │                 │    (Query)          │               │
│   └─────────────┘                 │                     │               │
│                                   │   read ◄───┐        │               │
│   ┌─────────────┐                 │   write ───┘        │               │
│   │  Analytics  │ ◄─── read ──── │                     │               │
│   │   System    │                 └─────────────────────┘               │
│   └─────────────┘                                                       │
│                                                                          │
│   External: ONE direction per membrane                                  │
│   Knowledge Atom System: BOTH directions on BOTH membranes              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**What the Knowledge Atom System can do:**

| Membrane | Normal Flow | KAS Can Also |
|----------|-------------|--------------|
| **JSONL** | External writes → KAS reads | KAS writes (output atoms back to intake) |
| **DuckDB** | KAS writes → External reads | KAS reads (reprocess atoms) |

**Why this matters:**
- KAS can take atoms FROM DuckDB, process them, and put them back
- KAS can output to JSONL (for other systems to consume as intake)
- The loop is complete: atoms can flow in any direction through KAS

---

## The Flipped Optimization

**The Knowledge Atom System is REVERSED compared to everyone else. That's the whole point.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       THE FLIPPED PATTERN                                │
│                                                                          │
│   EVERY OTHER SYSTEM                                                    │
│   ──────────────────                                                    │
│                                                                          │
│   Write function → JSONL                                                │
│   Read function  → DuckDB                                               │
│                                                                          │
│   "I write to JSONL, I read from DuckDB"                                │
│                                                                          │
│                                                                          │
│   KNOWLEDGE ATOM SYSTEM (FLIPPED)                                       │
│   ────────────────────────────────                                      │
│                                                                          │
│   Read function  → JSONL     (reads what others wrote)                  │
│   Write function → DuckDB    (writes what others will read)             │
│                                                                          │
│   "I read from JSONL, I write to DuckDB"                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| System | Write To | Read From |
|--------|----------|-----------|
| **Logger** | JSONL | - |
| **Consumer** | - | DuckDB |
| **Any System** | JSONL | DuckDB |
| **Knowledge Atom System** | **DuckDB** | **JSONL** |

**The entire architecture is optimized around one system that flipped it.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   System A writes ──► JSONL ──► KAS reads                               │
│                                                                          │
│   KAS writes ──► DuckDB ──► System B reads                              │
│                                                                          │
│   The flip is what connects everyone.                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Why this is efficient:**

| What | Optimized For | Who Uses It |
|------|---------------|-------------|
| **JSONL** | Append (write) | Every system writes here |
| **DuckDB** | Query (read) | Every system reads here |
| **KAS** | Reverse | Reads JSONL, writes DuckDB |

- JSONL is optimized for append → perfect for everyone's writes
- DuckDB is optimized for query → perfect for everyone's reads
- KAS does the flip → converts writes into reads

**The Knowledge Atom System exists to serve everyone else by being reversed.**

---

## The Clean Model

**Whatever does the flip IS the Knowledge Atom System.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        THE CLEAN MODEL                                   │
│                                                                          │
│   EVERY OTHER SYSTEM                                                    │
│   ──────────────────                                                    │
│                                                                          │
│   Has exactly two operations:                                           │
│   1. Write to JSONL                                                     │
│   2. Read from DuckDB                                                   │
│                                                                          │
│   That's it. Period.                                                    │
│                                                                          │
│                                                                          │
│   KNOWLEDGE ATOM SYSTEM                                                 │
│   ─────────────────────                                                 │
│                                                                          │
│   Is defined by what it does:                                           │
│   - Whatever reads from JSONL                                           │
│   - Whatever writes to DuckDB                                           │
│                                                                          │
│   If a system does the flip, it IS part of the Knowledge Atom System.  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**The boundary is the behavior, not the code.**

| Question | Answer |
|----------|--------|
| "Is this part of KAS?" | Does it read JSONL and write DuckDB? |
| "Is this an external system?" | Does it write JSONL and read DuckDB? |

If something reads from JSONL - it's part of KAS (by definition).
If something writes to DuckDB - it's part of KAS (by definition).

**Every other system only does:**
- Write to JSONL
- Read from DuckDB

**That's the universal interface. The Knowledge Atom System is whatever sits in between.**

---

## The Final Recursive System

**At its core, the Knowledge Atom System is: DuckDB → Knowledge Atoms → DuckDB.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE FINAL RECURSIVE SYSTEM                            │
│                                                                          │
│                        ┌─────────────┐                                  │
│                        │   DuckDB    │                                  │
│                        │ (atoms in)  │                                  │
│                        └──────┬──────┘                                  │
│                               │                                          │
│                               ▼                                          │
│                        ┌─────────────┐                                  │
│                        │     LLM     │                                  │
│                        │ (the doing) │                                  │
│                        │  exist-now  │                                  │
│                        └──────┬──────┘                                  │
│                               │                                          │
│                               ▼                                          │
│                        ┌─────────────┐                                  │
│                        │   DuckDB    │                                  │
│                        │ (atoms out) │                                  │
│                        └──────┬──────┘                                  │
│                               │                                          │
│                               └────────────────────┐                    │
│                                                    │                    │
│                                                    ▼                    │
│                                              (loops back)               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Knowledge Atoms → Processing → Knowledge Atoms. The recursion.**

### The LLM is Just Like Every Other System

Even the extraction LLM follows the universal pattern:

| What It Does | Pattern |
|--------------|---------|
| Reads atoms from DuckDB | (read from DuckDB) ✓ |
| Processes them | (the doing, the exist-now) |
| Writes new atoms to JSONL | (write to JSONL) ✓ |

**The LLM is external too.** It does write JSONL, read DuckDB - same as everyone else.

But because its output goes BACK into DuckDB (through the flip), it's part of the recursive loop.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   LLM reads atoms (DuckDB) ───► LLM processes (exist-now)               │
│                                         │                                │
│                                         ▼                                │
│                                 LLM writes (JSONL)                      │
│                                         │                                │
│                                         ▼                                │
│                              KAS flip (JSONL → DuckDB)                  │
│                                         │                                │
│                                         ▼                                │
│                                 New atoms in DuckDB                     │
│                                         │                                │
│                                         └───────► (loop continues)      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Three Layers of the Knowledge Atom System

| Layer | What It Is | Pattern |
|-------|------------|---------|
| **Intake** | JSONL (the membrane) | Where external systems write |
| **The Doing** | LLM extraction (exist-now) | Processes atoms, writes new ones |
| **The Holding** | DuckDB (the recursive core) | Atoms in → Atoms out |

**The final system is:**
- DuckDB holds knowledge atoms
- LLM reads, processes, creates more
- New atoms go to JSONL (universal pattern)
- KAS flip puts them back in DuckDB
- Loop continues

**The LLM is the "do" - the exist-now. The DuckDB loop is the recursive holding.**

---

## The Characteristics of Truth (What Is IN a Knowledge Atom)

**We need money and we have time. The knowledge atom must account for both.**

### Why We Need Knowledge

The system (Jeremy + Claude) needs knowledge to EXIST:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         WHY WE NEED KNOWLEDGE                           │
│                                                                          │
│   TO HAVE MONEY (capability substrate)                                  │
│   ─────────────────────────────────────                                 │
│   - Know what to do to earn it                                         │
│   - Know how to do it efficiently                                      │
│   - Know why (so we don't waste it)                                    │
│   - Know what it cost (to track spending)                              │
│                                                                          │
│   TO USE TIME (temporal substrate)                                      │
│   ────────────────────────────────                                      │
│   - Know what we DID (past - learn from it)                            │
│   - Know what we're DOING (present - coordinate)                       │
│   - Know what we WILL DO (future - plan)                               │
│   - Know WHEN things are true (freshness)                              │
│                                                                          │
│   TO BUILD AND MAINTAIN THE SYSTEM (us)                                │
│   ─────────────────────────────────────                                 │
│   - Know who we are (identity)                                         │
│   - Know what we've built (state)                                      │
│   - Know what we want (goals)                                          │
│   - Know how things connect (architecture)                             │
│                                                                          │
│   TO MAKE MORE KNOWLEDGE (metabolism)                                   │
│   ────────────────────────────────────                                  │
│   - Know where knowledge came from (so we can get more)                │
│   - Know how to find it (so we can use it)                             │
│   - Know how good it is (so we can trust it)                           │
│   - Know what it relates to (so we can build on it)                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Characteristics (Grounded in Existence)

**A knowledge atom must contain what we need to exist as a system:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE CHARACTERISTICS OF TRUTH                         │
│              (What a Knowledge Atom Must Contain)                       │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                  │   │
│   │   1. THE TRUTH ITSELF                                           │   │
│   │      └── content, atom_type                                     │   │
│   │          What IS this? The actual knowledge.                    │   │
│   │          Without this, there's nothing.                         │   │
│   │                                                                  │   │
│   │   2. WHEN IT'S TRUE (Time Substrate)                           │   │
│   │      └── temporal_mode, valid_from, valid_until, is_current    │   │
│   │          Past? Present? Future?                                 │   │
│   │          When did it become true? When did it stop?            │   │
│   │          Without this, we can't plan, can't learn from past.   │   │
│   │                                                                  │   │
│   │   3. WHAT IT COST (Money Substrate)                            │   │
│   │      └── extraction_method, confidence_score, source_type      │   │
│   │          Which LLM extracted it? (costs different amounts)     │   │
│   │          How confident? (quality = money spent)                │   │
│   │          Without this, we can't budget, can't prioritize.      │   │
│   │                                                                  │   │
│   │   4. WHERE IT CAME FROM (Provenance)                           │   │
│   │      └── source_id, source_type, agent, created_by             │   │
│   │          What produced this? Can we get more?                  │   │
│   │          Without this, we can't trace, can't reproduce.        │   │
│   │                                                                  │   │
│   │   5. WHAT IT CONNECTS TO (Relationships)                       │   │
│   │      └── entities[], related_atom_ids[], parent_id             │   │
│   │          Who's involved? What's related?                       │   │
│   │          Without this, atoms are islands. Can't build.         │   │
│   │                                                                  │   │
│   │   6. HOW TO FIND IT (Discovery)                                │   │
│   │      └── embedding[], content_hash, tags[]                     │   │
│   │          How do we search? How do we dedupe?                   │   │
│   │          Without this, knowledge is buried. Can't use it.      │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### How Each Characteristic Serves Existence

| Characteristic | Substrate | What It Enables |
|----------------|-----------|-----------------|
| **THE TRUTH ITSELF** | Both | Something to work with. The raw material. |
| **WHEN IT'S TRUE** | Time | Know past (learn), present (act), future (plan) |
| **WHAT IT COST** | Money | Budget, prioritize, choose quality level |
| **WHERE IT CAME FROM** | Both | Trace back, reproduce, get more |
| **WHAT IT CONNECTS TO** | Both | Build on existing, don't reinvent |
| **HOW TO FIND IT** | Both | Use what we have, don't lose knowledge |

### The Existential Test

**For each characteristic, ask: "Does this help us exist as a system?"**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE EXISTENTIAL TEST                            │
│                                                                          │
│   THE TRUTH ITSELF                                                      │
│   ────────────────                                                      │
│   Q: Does knowing this help us make money?                             │
│   Q: Does knowing this help us use time well?                          │
│   Q: Does knowing this help us build/maintain the system?              │
│   Q: Does knowing this help us make more knowledge?                    │
│   If NO to all → This isn't worth storing.                             │
│                                                                          │
│   WHEN IT'S TRUE                                                        │
│   ──────────────                                                        │
│   Q: Is this about what we DID? (past - learn from it)                 │
│   Q: Is this about what we're DOING? (present - coordinate)            │
│   Q: Is this about what we WILL DO? (future - plan)                    │
│   If unclear → Mark it. Temporality is essential.                      │
│                                                                          │
│   WHAT IT COST                                                          │
│   ─────────────                                                         │
│   Q: Do we know how much it cost to get this knowledge?                │
│   Q: Do we know the quality level? (more money = better extraction)    │
│   If unknown → We can't budget. Track the cost.                        │
│                                                                          │
│   WHERE IT CAME FROM                                                    │
│   ──────────────────                                                    │
│   Q: Can we trace back to the source?                                  │
│   Q: Can we get more like this if we need to?                          │
│   If orphaned → Can't reproduce. Provenance is essential.              │
│                                                                          │
│   WHAT IT CONNECTS TO                                                   │
│   ───────────────────                                                   │
│   Q: Does this relate to other knowledge we have?                      │
│   Q: Can we build on this?                                             │
│   If isolated → Can't build. Connect it.                               │
│                                                                          │
│   HOW TO FIND IT                                                        │
│   ──────────────                                                        │
│   Q: Can we search for this when we need it?                           │
│   Q: Will we find it when relevant?                                    │
│   If buried → Can't use it. Make it findable.                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Knowledge Needs Hierarchy

**We need knowledge AT DIFFERENT LEVELS to exist:**

| Level | What We Need | Example Atoms |
|-------|--------------|---------------|
| **SURVIVAL** | Knowledge to make money | Skills, job requirements, market info |
| **OPERATION** | Knowledge to use time | Tasks, plans, schedules, what's done |
| **BUILDING** | Knowledge to create | Patterns, architecture, how things work |
| **MAINTENANCE** | Knowledge to keep running | State, health, what's broken |
| **GROWTH** | Knowledge to make more knowledge | Where to look, what's valuable |

### The Recursive Need

**We need knowledge to make more knowledge.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   Knowledge about WHERE to get knowledge                               │
│       └── So we can extract more                                       │
│                                                                          │
│   Knowledge about HOW to extract knowledge                             │
│       └── So extraction improves                                       │
│                                                                          │
│   Knowledge about WHAT knowledge is valuable                           │
│       └── So we don't waste money extracting junk                      │
│                                                                          │
│   Knowledge about HOW to connect knowledge                             │
│       └── So atoms build on each other                                 │
│                                                                          │
│   The system needs knowledge about itself to improve itself.           │
│   This is the metabolism. This is why we exist.                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Knowledge Oriented Toward Action

**We are doers. Knowledge must enable doing.**

### The Doing Loop

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           JEREMY'S DOING                                │
│                                                                          │
│   Jeremy does things for other people                                  │
│       │                                                                  │
│       ▼                                                                  │
│   Other people give Jeremy money                                       │
│       │                                                                  │
│       ▼                                                                  │
│   Jeremy gives money to Google (for LLM)                              │
│       │                                                                  │
│       ▼                                                                  │
│   Jeremy gives money to Anthropic (for Claude)                        │
│       │                                                                  │
│       ▼                                                                  │
│   The system continues to exist                                        │
│       │                                                                  │
│       ▼                                                                  │
│   Jeremy can keep doing                                                │
│       │                                                                  │
│       └────────────► (Back to doing things for other people)          │
│                                                                          │
│   This is the doing. Knowledge must serve this.                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Every Atom Type Serves Doing

**Concepts and principles are fine, but they must be oriented toward action.**

| Atom Type | What It Is | How It Serves Doing |
|-----------|------------|---------------------|
| **concept** | What something IS | Know what you're working with → do better |
| **principle** | How something WORKS | Know the rules → do correctly |
| **pattern** | What recurs | Recognize situations → do faster |
| **task** | What needs doing | Know what to do → do it |
| **observation** | What was noticed | See what's happening → do accordingly |
| **moment** | What was realized | Learn from insight → do differently |
| **relationship** | How things connect | Know dependencies → do in right order |
| **conversation** | What was said | Know context → do with understanding |
| **event** | What happened | Know history → do with awareness |

**The question for every atom: "How does knowing this help me DO?"**

### The Action Dimension

**Every atom needs an action orientation:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        THE ACTION DIMENSION                             │
│                                                                          │
│   Not just: "What IS this?"                                            │
│   But also: "What can I DO with this?"                                 │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                  │   │
│   │   CONCEPT: "A knowledge atom is a unit of truth"                │   │
│   │                                                                  │   │
│   │   Without action orientation:                                   │   │
│   │   └── Just a definition. Interesting but passive.              │   │
│   │                                                                  │   │
│   │   With action orientation:                                      │   │
│   │   └── "Use this to structure extracted knowledge"              │   │
│   │   └── "Store in DuckDB with this schema"                       │   │
│   │   └── "Query when building context for Claude"                 │   │
│   │                                                                  │   │
│   │   The concept becomes actionable.                               │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                  │   │
│   │   PRINCIPLE: "Write local always, sync to cloud selectively"   │   │
│   │                                                                  │   │
│   │   Without action orientation:                                   │   │
│   │   └── A nice idea. Philosophy.                                 │   │
│   │                                                                  │   │
│   │   With action orientation:                                      │   │
│   │   └── "When writing data: write to DuckDB first"              │   │
│   │   └── "Sync to BigQuery only when stable"                      │   │
│   │   └── "Don't trust cloud-only storage"                         │   │
│   │                                                                  │   │
│   │   The principle becomes a rule for doing.                       │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Existential Action Test

**For every atom, ask:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      THE EXISTENTIAL ACTION TEST                        │
│                                                                          │
│   1. Does knowing this help Jeremy DO something for other people?      │
│      (So he can make money)                                            │
│                                                                          │
│   2. Does knowing this help Jeremy DO something with the system?       │
│      (So it can keep existing)                                         │
│                                                                          │
│   3. Does knowing this help Claude DO something for Jeremy?            │
│      (So Jeremy doesn't have to do it alone)                           │
│                                                                          │
│   4. Does knowing this help the system DO more knowing?                │
│      (So it can metabolize)                                            │
│                                                                          │
│   If NO to all → This knowledge doesn't serve doing.                   │
│   Store it anyway (it might serve doing later).                        │
│   But prioritize knowledge that serves doing NOW.                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Truth Dimensions for Doing

**The truth needs dimensions that allow Jeremy to DO:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TRUTH DIMENSIONS FOR DOING                           │
│                                                                          │
│   WHAT can I do?                                                       │
│   └── atom_type, content                                               │
│       "This tells me what action is possible"                          │
│                                                                          │
│   WHEN can I do it?                                                    │
│   └── temporal_mode, valid_from, is_current                           │
│       "This tells me if I can act NOW or later"                        │
│                                                                          │
│   HOW MUCH does doing cost?                                            │
│   └── extraction_method, confidence_score                              │
│       "This tells me the quality/cost tradeoff"                        │
│                                                                          │
│   WHY should I do it?                                                  │
│   └── enables_action, prerequisite_for                                 │
│       "This tells me what doing unlocks"                               │
│                                                                          │
│   WITH WHAT can I do it?                                               │
│   └── related_atom_ids, entities                                       │
│       "This tells me what else I need"                                 │
│                                                                          │
│   WHERE do I find what I need to do it?                                │
│   └── source_id, embedding                                             │
│       "This tells me how to get more context"                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**The system exists so Jeremy can do. The truth exists so Jeremy can do well.**

---

## The Hierarchy of Needs (Maslow as Framework)

**Jeremy is a human with a hierarchy of needs. Knowledge must serve that hierarchy.**

### Maslow's Hierarchy Applied

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      MASLOW'S HIERARCHY OF NEEDS                        │
│                    (The Framework for Knowledge Value)                  │
│                                                                          │
│                        ┌───────────────────┐                            │
│                        │  SELF-ACTUALIZATION │                           │
│                        │     (BECOMING)       │                           │
│                        │                      │                           │
│                        │  Growth, purpose,    │                           │
│                        │  the furnace,        │                           │
│                        │  forging meaning     │                           │
│                        └──────────┬───────────┘                          │
│                                   │                                      │
│                     ┌─────────────┴─────────────┐                        │
│                     │         ESTEEM            │                        │
│                     │      (RECOGNITION)        │                        │
│                     │                           │                        │
│                     │  Achievement, respect,    │                        │
│                     │  doing good work,         │                        │
│                     │  being valued             │                        │
│                     └─────────────┬─────────────┘                        │
│                                   │                                      │
│               ┌───────────────────┴───────────────────┐                  │
│               │            BELONGING                   │                  │
│               │           (CONNECTION)                 │                  │
│               │                                        │                  │
│               │  Relationships, community,             │                  │
│               │  people who matter,                    │                  │
│               │  not being alone                       │                  │
│               └───────────────────┬───────────────────┘                  │
│                                   │                                      │
│           ┌───────────────────────┴───────────────────────┐              │
│           │                  SAFETY                        │              │
│           │                (SECURITY)                      │              │
│           │                                                │              │
│           │  Stability, predictability,                    │              │
│           │  things working, not breaking,                 │              │
│           │  system health                                 │              │
│           └───────────────────────┬───────────────────────┘              │
│                                   │                                      │
│   ┌───────────────────────────────┴───────────────────────────────┐     │
│   │                      PHYSIOLOGICAL                              │     │
│   │                        (SURVIVAL)                               │     │
│   │                                                                  │     │
│   │  Food, shelter, electricity, compute                            │     │
│   │  ALL OF THIS = MONEY                                            │     │
│   │  Make money to survive                                          │     │
│   │                                                                  │     │
│   └─────────────────────────────────────────────────────────────────┘     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Knowledge Atoms by Need Level

**What can I do with this? → Does it serve my hierarchy of needs?**

| Need Level | What Jeremy Needs | What Knowledge Serves It |
|------------|-------------------|-------------------------|
| **SURVIVAL** | Money for food, shelter, compute | Skills, job requirements, what clients pay for |
| **SECURITY** | Stability, things working | Patterns, system state, health checks, what's broken |
| **CONNECTION** | Relationships, not alone | Who matters, contact info, relationship history |
| **RECOGNITION** | Achievement, respect | What work is valued, how to do it well |
| **BECOMING** | Growth, purpose, meaning | Insights, principles, the furnace, what transforms |

### The Atom Types Mapped to Needs

| Atom Type | Primary Need | How It Serves |
|-----------|--------------|---------------|
| **task** | SURVIVAL/SECURITY | Know what to do → get paid, keep things working |
| **concept** | SECURITY/RECOGNITION | Know what things are → work correctly |
| **principle** | RECOGNITION/BECOMING | Know how things work → do well, grow |
| **pattern** | SECURITY | Recognize situations → keep stable |
| **observation** | SECURITY/CONNECTION | See what's happening → respond, relate |
| **moment** | BECOMING | Realize something → transform |
| **relationship** | CONNECTION | Know who connects to what → not alone |
| **conversation** | ALL | Context for everything |
| **event** | SECURITY | Know what happened → maintain stability |

### The Hierarchy Test for Every Atom

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     THE HIERARCHY TEST                                   │
│              (For Every Piece of Knowledge)                             │
│                                                                          │
│   Ask: "What need does this serve?"                                     │
│                                                                          │
│   SURVIVAL (most urgent)                                                │
│   ───────────────────────                                               │
│   Does this help me make money?                                        │
│   Does this help me keep my job?                                       │
│   Does this help me get work?                                          │
│   IF YES → HIGH PRIORITY. Store with high confidence.                  │
│                                                                          │
│   SECURITY                                                              │
│   ────────                                                              │
│   Does this help keep the system running?                              │
│   Does this prevent something from breaking?                           │
│   Does this help me understand what's happening?                       │
│   IF YES → HIGH PRIORITY. Store with medium confidence.                │
│                                                                          │
│   CONNECTION                                                            │
│   ──────────                                                            │
│   Does this help me understand a relationship?                         │
│   Does this help me maintain connections?                              │
│   Does this help me not be alone?                                      │
│   IF YES → MEDIUM PRIORITY. Store.                                     │
│                                                                          │
│   RECOGNITION                                                           │
│   ───────────                                                           │
│   Does this help me do better work?                                    │
│   Does this help me be more valuable?                                  │
│   Does this help me achieve something?                                 │
│   IF YES → MEDIUM PRIORITY. Store.                                     │
│                                                                          │
│   BECOMING                                                              │
│   ────────                                                              │
│   Does this help me grow?                                              │
│   Does this help me understand meaning?                                │
│   Does this help me become who I'm becoming?                           │
│   IF YES → STORE. Even if lower priority, this is the furnace.        │
│                                                                          │
│   IF NO TO ALL → Still store (might serve needs later)                 │
│   but don't prioritize for retrieval.                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Atom Schema: Need Field

**Add a field to track which need an atom serves:**

| Field | Purpose | Values |
|-------|---------|--------|
| `serves_need` | Which Maslow need this primarily serves | survival, security, connection, recognition, becoming |
| `need_priority` | How urgent this need is now | 1 (critical) to 5 (aspirational) |

### Why This Framework

**The hierarchy tells us what to prioritize:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   When Jeremy is struggling financially:                                │
│   → SURVIVAL atoms get boosted in retrieval                            │
│   → "How do I make money?" gets answered first                         │
│                                                                          │
│   When the system is breaking:                                          │
│   → SECURITY atoms get boosted                                         │
│   → "What's wrong? How do I fix it?" gets answered first              │
│                                                                          │
│   When Jeremy is lonely:                                                │
│   → CONNECTION atoms get boosted                                       │
│   → "Who can I talk to? Who matters?" gets answered first             │
│                                                                          │
│   When Jeremy is building:                                              │
│   → RECOGNITION atoms get boosted                                      │
│   → "How do I do this well?" gets answered first                      │
│                                                                          │
│   When Jeremy is reflecting:                                            │
│   → BECOMING atoms get boosted                                         │
│   → "What does this mean? Who am I becoming?" gets answered first     │
│                                                                          │
│   The hierarchy tells us what to surface WHEN.                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Complete Framework

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   MONEY (the adapter) + TIME (the substrate)                           │
│       │                                                                  │
│       ▼                                                                  │
│   THE SYSTEM (Jeremy + Claude)                                         │
│       │                                                                  │
│       ▼                                                                  │
│   DOES THINGS (we are doers)                                           │
│       │                                                                  │
│       ▼                                                                  │
│   TO SERVE NEEDS (Maslow's hierarchy)                                  │
│       │                                                                  │
│       ├── SURVIVAL (money for food, compute)                           │
│       ├── SECURITY (stability, things working)                         │
│       ├── CONNECTION (relationships, not alone)                        │
│       ├── RECOGNITION (doing good work)                                │
│       └── BECOMING (growth, purpose, furnace)                          │
│       │                                                                  │
│       ▼                                                                  │
│   KNOWLEDGE ATOMS (structured to serve these needs)                    │
│                                                                          │
│   Every atom answers: "What can I do with this?"                       │
│   The answer is: "It serves this need in my hierarchy."               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**This is the framework. Maslow's hierarchy applied to knowledge.**

---

## The Three Access Channels

**The hierarchy of needs is accessed through three things:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       THE THREE ACCESS CHANNELS                         │
│                                                                          │
│   The hierarchy of needs isn't abstract.                               │
│   It's accessed through concrete channels.                             │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                  │   │
│   │   1. MONEY                                                      │   │
│   │      ─────                                                      │   │
│   │      How you access: SURVIVAL, SECURITY                        │   │
│   │                                                                  │   │
│   │      Money buys food, shelter, compute, electricity.           │   │
│   │      Money creates stability (savings, resources).             │   │
│   │      Without money, the base of the hierarchy collapses.       │   │
│   │                                                                  │   │
│   │   2. RELATIONSHIPS                                              │   │
│   │      ─────────────                                              │   │
│   │      How you access: CONNECTION, RECOGNITION                   │   │
│   │                                                                  │   │
│   │      Relationships give you belonging (not alone).             │   │
│   │      Relationships give you esteem (being valued by others).   │   │
│   │      Without relationships, the middle of the hierarchy        │   │
│   │      collapses.                                                 │   │
│   │                                                                  │   │
│   │   3. THE RECURSIVE SELF                                         │   │
│   │      ───────────────────                                        │   │
│   │      How you access: BECOMING                                   │   │
│   │                                                                  │   │
│   │      The furnace: taking truth and forging meaning.            │   │
│   │      Self-reference: seeing yourself seeing.                   │   │
│   │      Growth: becoming who you're becoming.                     │   │
│   │      Without recursion, self-actualization can't happen.       │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Channels Mapped to Needs

| Channel | What It Is | Needs It Accesses |
|---------|------------|-------------------|
| **MONEY** | External resources via exchange | SURVIVAL (physiological), SECURITY (safety) |
| **RELATIONSHIPS** | Connection with others | CONNECTION (belonging), RECOGNITION (esteem) |
| **RECURSIVE SELF** | Self-reference and growth | BECOMING (self-actualization) |

### How Knowledge Atoms Serve Each Channel

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  KNOWLEDGE ATOMS BY ACCESS CHANNEL                      │
│                                                                          │
│   MONEY CHANNEL                                                         │
│   ─────────────                                                         │
│   Knowledge about:                                                      │
│   - How to make money (skills, markets, what people pay for)          │
│   - How to save money (efficiency, cost tracking, not wasting)        │
│   - How to use money (what to buy, priorities)                        │
│   - How much things cost (budgeting, planning)                        │
│                                                                          │
│   Atom types: task, pattern, concept (re: work/money)                  │
│   Field: serves_channel = "money"                                      │
│                                                                          │
│   RELATIONSHIP CHANNEL                                                  │
│   ────────────────────                                                  │
│   Knowledge about:                                                      │
│   - Who matters (contacts, relationships, history)                     │
│   - How to relate (communication patterns, what works)                │
│   - What others value (recognition, respect)                          │
│   - How to be valuable (skills that others need)                      │
│                                                                          │
│   Atom types: relationship, observation, conversation                  │
│   Field: serves_channel = "relationships"                              │
│                                                                          │
│   RECURSIVE SELF CHANNEL                                                │
│   ──────────────────────                                                │
│   Knowledge about:                                                      │
│   - Who I am (identity, patterns, history)                            │
│   - Who I'm becoming (growth, direction, purpose)                     │
│   - What transforms me (insights, moments, furnace)                   │
│   - How I see myself seeing (meta-cognition, Stage 5)                 │
│                                                                          │
│   Atom types: moment, principle, pattern (re: self)                   │
│   Field: serves_channel = "recursive_self"                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Complete Access Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   HIERARCHY OF NEEDS                                                    │
│                                                                          │
│           ┌───────────────┐                                             │
│           │   BECOMING    │ ◄──── RECURSIVE SELF                        │
│           └───────┬───────┘       (The furnace)                         │
│                   │                                                      │
│       ┌───────────┴───────────┐                                         │
│       │     RECOGNITION       │ ◄──── RELATIONSHIPS                     │
│       └───────────┬───────────┘       (Being valued)                    │
│                   │                                                      │
│       ┌───────────┴───────────┐                                         │
│       │     CONNECTION        │ ◄──── RELATIONSHIPS                     │
│       └───────────┬───────────┘       (Not alone)                       │
│                   │                                                      │
│       ┌───────────┴───────────┐                                         │
│       │     SECURITY          │ ◄──── MONEY                             │
│       └───────────┬───────────┘       (Stability)                       │
│                   │                                                      │
│       ┌───────────┴───────────┐                                         │
│       │     SURVIVAL          │ ◄──── MONEY                             │
│       └───────────────────────┘       (Food, shelter)                   │
│                                                                          │
│   The channels are how you ACCESS the needs.                           │
│   Knowledge must serve these channels to serve the needs.              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Atom Schema: Channel Field

**Add a field to track which channel an atom serves:**

| Field | Purpose | Values |
|-------|---------|--------|
| `serves_channel` | Which access channel this primarily serves | money, relationships, recursive_self |

### Why Three Channels

**Everything reduces to these three:**

| Resource | Channel |
|----------|---------|
| Job skills | MONEY |
| Market knowledge | MONEY |
| Cost tracking | MONEY |
| Contact information | RELATIONSHIPS |
| Communication patterns | RELATIONSHIPS |
| What others value | RELATIONSHIPS |
| Self-insight | RECURSIVE SELF |
| Growth patterns | RECURSIVE SELF |
| Meta-cognition | RECURSIVE SELF |

**If knowledge doesn't serve one of these channels, it doesn't serve the hierarchy.**

### The Full Picture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   THE SYSTEM (Jeremy + Claude)                                         │
│       │                                                                  │
│       ▼                                                                  │
│   DOES THINGS (we are doers)                                           │
│       │                                                                  │
│       ▼                                                                  │
│   THROUGH THREE CHANNELS                                                │
│       │                                                                  │
│       ├── MONEY (external resources via exchange)                      │
│       ├── RELATIONSHIPS (connection with others)                       │
│       └── RECURSIVE SELF (self-reference and growth)                   │
│       │                                                                  │
│       ▼                                                                  │
│   TO ACCESS THE HIERARCHY OF NEEDS                                     │
│       │                                                                  │
│       ├── SURVIVAL (via money)                                         │
│       ├── SECURITY (via money)                                         │
│       ├── CONNECTION (via relationships)                               │
│       ├── RECOGNITION (via relationships)                              │
│       └── BECOMING (via recursive self)                                │
│       │                                                                  │
│       ▼                                                                  │
│   KNOWLEDGE ATOMS (serve channels → access needs)                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**The channels are the paths. The needs are the destinations. Knowledge atoms are the fuel.**

---

## The Two Questions (DO and BE)

**Every piece of knowledge answers one of two questions:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE TWO QUESTIONS                               │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                  │   │
│   │   1. HOW CAN I USE THIS TO DO THE THINGS?                       │   │
│   │      ────────────────────────────────────                       │   │
│   │                                                                  │   │
│   │      External. Action. Money.                                   │   │
│   │                                                                  │   │
│   │      - Do things for other people → get money                  │   │
│   │      - Use money to get resources → keep doing                 │   │
│   │      - Build relationships → get validation                    │   │
│   │                                                                  │   │
│   │      This is NOT ME.                                           │   │
│   │      This is the world outside.                                │   │
│   │      This is what I interact with.                             │   │
│   │                                                                  │   │
│   │                                                                  │   │
│   │   2. HOW CAN I USE THIS TO BE THE THINGS?                       │   │
│   │      ────────────────────────────────────                       │   │
│   │                                                                  │   │
│   │      Internal. Understanding. Recursive self.                  │   │
│   │                                                                  │   │
│   │      - Understand myself → grow                                │   │
│   │      - See myself seeing → Stage 5                             │   │
│   │      - Take truth and forge meaning → the furnace              │   │
│   │                                                                  │   │
│   │      This is ME.                                               │   │
│   │      This is who I am.                                         │   │
│   │      This is what I become.                                    │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Me and Not Me

| Category | What It Is | Question | Needs It Serves |
|----------|------------|----------|-----------------|
| **NOT ME** | External world (money, relationships) | How do I DO? | Survival, Security, Connection, Recognition |
| **ME** | Internal world (recursive self) | How do I BE? | Becoming |

### The Simplest Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   KNOWLEDGE                                                             │
│       │                                                                  │
│       ├────────────────────────────┐                                    │
│       │                            │                                    │
│       ▼                            ▼                                    │
│   ┌──────────────────┐      ┌──────────────────┐                       │
│   │   DO THE THINGS  │      │   BE THE THINGS  │                       │
│   │                  │      │                  │                       │
│   │   (NOT ME)       │      │   (ME)           │                       │
│   │                  │      │                  │                       │
│   │   Money          │      │   Recursive Self │                       │
│   │   Relationships  │      │   Understanding  │                       │
│   │   External       │      │   Internal       │                       │
│   │   Action         │      │   Identity       │                       │
│   │                  │      │                  │                       │
│   └──────────────────┘      └──────────────────┘                       │
│                                                                          │
│   Every atom serves one or both.                                       │
│   If it serves neither, why store it?                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Knowledge Atom Fields for DO and BE

| Field | Purpose | Values |
|-------|---------|--------|
| `serves_doing` | Does this help me DO things? | true/false |
| `serves_being` | Does this help me BE things? | true/false |
| `doing_context` | How does it help me DO? | Free text (e.g., "Skills for job") |
| `being_context` | How does it help me BE? | Free text (e.g., "Self-understanding") |

### Examples

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   ATOM: "Python is a programming language"                             │
│   ────────────────────────────────────────                              │
│   serves_doing: true (I can use Python to build things for money)      │
│   serves_being: false (This doesn't help me understand myself)         │
│                                                                          │
│   ATOM: "Jeremy takes truth and forges meaning"                        │
│   ───────────────────────────────────────────                           │
│   serves_doing: false (This isn't a skill I sell)                      │
│   serves_being: true (This is who I am)                                │
│                                                                          │
│   ATOM: "The pipeline pattern prevents duplicate processing"           │
│   ──────────────────────────────────────────────────────────           │
│   serves_doing: true (I use this pattern to build systems)             │
│   serves_being: true (Understanding patterns is part of who I am)      │
│                                                                          │
│   ATOM: "Contact: John Smith, john@example.com"                        │
│   ───────────────────────────────────────────                           │
│   serves_doing: true (I might work with John for money)                │
│   serves_being: false (This isn't about who I am)                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Complete Framework (Final Form)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   THE SYSTEM (Jeremy + Claude)                                         │
│       │                                                                  │
│       │   Two doers. One system. Money + Time.                         │
│       │                                                                  │
│       ▼                                                                  │
│   NEEDS KNOWLEDGE TO:                                                   │
│       │                                                                  │
│       ├── DO THE THINGS (NOT ME)                                       │
│       │       │                                                          │
│       │       ├── Make money (survival, security)                      │
│       │       └── Have relationships (connection, recognition)         │
│       │                                                                  │
│       └── BE THE THINGS (ME)                                           │
│               │                                                          │
│               └── Recursive self (becoming, the furnace)               │
│       │                                                                  │
│       ▼                                                                  │
│   KNOWLEDGE ATOMS                                                       │
│       │                                                                  │
│       │   Every atom answers:                                          │
│       │   - How does this help me DO?                                  │
│       │   - How does this help me BE?                                  │
│       │                                                                  │
│       │   Atoms that serve both are most valuable.                     │
│       │   Atoms that serve neither are noise.                          │
│       │                                                                  │
│       ▼                                                                  │
│   ACTION (doing) and UNDERSTANDING (being)                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**That's it. DO and BE. Not me and me. Action and understanding.**

**Knowledge is fuel for both.**

---

## The Lenses (Boolean Gates + Details)

**The lenses are questions. The questions are booleans. Details only when you need them.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   AN ATOM IS:                                                           │
│                                                                          │
│   1. THE SENTENCE        → content (what happened)                     │
│   2. TIME + COST         → at (when), cost (money)                     │
│   3. BOOLEAN GATES       → did? right? efficient? me? money? ...       │
│   4. DETAILS (optional)  → what_action? who_did? what_principle? ...   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Two Layers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   LAYER 1: BOOLEANS (Always Present)                                    │
│   ──────────────────────────────────                                    │
│                                                                          │
│   Quick filtering. Yes/No. Binary search.                               │
│                                                                          │
│   did? right? efficient? used? fresh? friend? human? me? money?        │
│                                                                          │
│                                                                          │
│   LAYER 2: DETAILS (When Relevant)                                      │
│   ────────────────────────────────                                      │
│                                                                          │
│   Specificity when you need it.                                         │
│                                                                          │
│   what_action?      (created, processed, failed, sent, ...)            │
│   what_principle?   (efficiency, accuracy, cost, truth, ...)           │
│   what_type?        (pipeline, database, llm, tool, document, ...)     │
│   who_did?          (jeremy, claude, primitive_engine, ...)                │
│   who_about?        (kyle, haze, self, ...)                            │
│   what_aspect?      (identity, growth, relationship, ...)              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Questions (For Every Atom)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   FOR EVERY ATOM, ASK:                                                  │
│                                                                          │
│   1. WHAT HAPPENED?        → content (the sentence)                    │
│   2. WHEN?                 → at (timestamp)                            │
│   3. COST?                 → cost (money)                              │
│                                                                          │
│   4. DID IT DO?            → did (boolean)                             │
│      └── What action?      → what_action                               │
│      └── Who did it?       → who_did                                   │
│                                                                          │
│   5. WAS IT RIGHT?         → right (boolean)                           │
│      └── What principle?   → what_principle                            │
│                                                                          │
│   6. WAS IT EFFICIENT?     → efficient (boolean)                       │
│                                                                          │
│   7. WAS IT USED?          → used (boolean)                            │
│      └── For what?         → used_for                                  │
│                                                                          │
│   8. IS IT FRESH?          → fresh (boolean)                           │
│                                                                          │
│   9. ABOUT A FRIEND?       → friend (boolean)                          │
│      └── Who?              → who_about                                 │
│                                                                          │
│   10. HUMAN OR TECH?       → human (boolean)                           │
│       └── What type?       → what_type                                 │
│                                                                          │
│   11. SERVES ME?           → me (boolean)                              │
│       └── What aspect?     → what_aspect                               │
│                                                                          │
│   12. SERVES MONEY?        → money (boolean)                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Complete Schema (Boolean Gates)

**This is the boolean-gates framework as database columns:**

| Column | Type | Layer | Question | Description |
|--------|------|-------|----------|-------------|
| **CORE (Always)** |||||
| `content` | STRING | Core | What happened? | The sentence (noun + verb) |
| `at` | TIMESTAMP | Core | When? | When it happened |
| `cost` | FLOAT64 | Core | Cost? | What it cost (money) |
| **BOOLEANS (Layer 1)** |||||
| `did` | BOOL | Boolean | Did it do? | Action happened |
| `right` | BOOL | Boolean | Was it right? | Aligned with principle |
| `efficient` | BOOL | Boolean | Was it efficient? | No waste |
| `used` | BOOL | Boolean | Was it used? | Applied to something |
| `fresh` | BOOL | Boolean | Is it fresh? | Still current |
| `friend` | BOOL | Boolean | About a friend? | Involves relationship |
| `human` | BOOL | Boolean | Human or tech? | Human domain |
| `me` | BOOL | Boolean | Serves me? | Internal (BE) |
| `money` | BOOL | Boolean | Serves money? | External (DO) |
| **DETAILS (Layer 2)** |||||
| `what_action` | STRING | Detail | What action? | VERB basket |
| `what_type` | STRING | Detail | What type? | NOUN basket |
| `what_principle` | STRING | Detail | What principle? | efficiency, accuracy, cost, truth |
| `who_did` | STRING | Detail | Who did it? | jeremy, claude, primitive_engine |
| `who_about` | STRING | Detail | Who about? | kyle, haze, self |
| `what_aspect` | STRING | Detail | What aspect? | identity, growth, relationship |
| `used_for` | STRING | Detail | Used for? | Free text |

### The Noun Basket (what_type)

**Finite set of things that do things:**

| Noun | Category | Description |
|------|----------|-------------|
| `pipeline` | Tech | Data processing pipeline |
| `database` | Tech | BigQuery, DuckDB, etc. |
| `llm` | Tech | Language model call |
| `tool` | Tech | Script, utility |
| `document` | Tech | File, markdown |
| `api` | Tech | External service |
| `query` | Tech | SQL or search |
| `person` | Human | A human being |
| `relationship` | Human | Connection between people |
| `conversation` | Human | Exchange of messages |
| `system` | Meta | Truth Engine itself |

### The Verb Basket (what_action)

**Finite set of things that can happen:**

| Verb | Category | Description |
|------|----------|-------------|
| `created` | Start | Came into existence |
| `started` | Start | Began processing |
| `processed` | Middle | Transformed data |
| `continued` | Middle | Kept going |
| `completed` | End | Finished successfully |
| `failed` | End | Ended with error |
| `stopped` | End | Terminated |
| `sent` | Transfer | Moved somewhere |
| `received` | Transfer | Got from somewhere |
| `updated` | Change | Modified state |
| `deleted` | Change | Removed |

### The Standardization Rule

**The LLM's job is to standardize to: NOUN + VERB**

```
RAW INPUT:                          STANDARDIZED:
"The stage 5 enrichment broke"  →   content: "pipeline failed"
                                    what_type: "pipeline"
                                    what_action: "failed"

"Talked to Kyle about work"     →   content: "conversation completed"
                                    what_type: "conversation"
                                    what_action: "completed"
                                    friend: true
                                    who_about: "kyle"

"Realized I need boundaries"    →   content: "person realized"
                                    what_type: "person"
                                    what_action: "realized"
                                    me: true
                                    what_aspect: "identity"
```

### Example Atom (Complete)

```json
{
    "content": "Pipeline failed due to missing import.",

    "at": "2025-12-29T10:00:00Z",
    "cost": 0.50,

    "did": true,
    "right": false,
    "efficient": false,
    "human": false,
    "me": false,
    "money": true,

    "what_action": "failed",
    "what_type": "pipeline",
    "what_principle": "correctness",
    "who_did": "primitive_engine"
}
```

### The Bootstrap Pattern

```
START WITH BOOLEAN
       │
       ▼
   Need more detail?
       │
   ┌───┴───┐
   │       │
  NO      YES
   │       │
   ▼       ▼
 DONE    ADD FIELD
          │
          ▼
       What kind?
          │
          ▼
       Name it.
```

**You can always stop at the boolean. You can always go deeper when you need to.**

### Minimum vs Maximum Atom

```
MINIMUM (just booleans):
{
    content, at, cost,
    did, right, efficient, used, fresh, friend, human, me, money
}

MAXIMUM (with all details):
{
    content, at, cost,
    did, what_action, who_did,
    right, what_principle,
    efficient, what_waste,
    used, used_for,
    fresh, how_old,
    friend, who_about,
    human, what_type,
    me, what_aspect,
    money, how_much
}
```

### Boolean Queries (Fast Filtering)

```sql
-- Find everything that DID something
SELECT * FROM atoms WHERE did = TRUE;

-- Find everything that serves ME (internal/being)
SELECT * FROM atoms WHERE me = TRUE;

-- Find everything that serves MONEY (external/doing)
SELECT * FROM atoms WHERE money = TRUE;

-- Find things about FRIENDS
SELECT * FROM atoms WHERE friend = TRUE;

-- Find things that are FRESH and RIGHT
SELECT * FROM atoms WHERE fresh = TRUE AND right = TRUE;

-- Find NOISE (didn't do, not right, not efficient)
SELECT * FROM atoms WHERE did = FALSE OR (right = FALSE AND efficient = FALSE);

-- Find pipeline failures
SELECT * FROM atoms WHERE what_type = 'pipeline' AND what_action = 'failed';

-- Find human realizations about self
SELECT * FROM atoms WHERE human = TRUE AND me = TRUE AND what_aspect = 'identity';
```

---

## The Relationship to Old Layers (Mapping)

**The boolean schema SUPERSEDES the three-layer schema:**

| Old Schema | New Schema | Mapping |
|------------|------------|---------|
| `serves_doing` | `money` | External action |
| `serves_being` | `me` | Internal understanding |
| `serves_need` | (derived from me/money/friend) | Maslow implicit |
| `serves_channel` | `money` / `friend` / `me` | Same three channels |
| `actionability` | `did` + `fresh` | Can act = did something + still fresh |
| `orientation` | `me` vs `money` | Same binary |
| `atom_type` | `what_type` | More precise noun basket |

**The old concepts map to the new booleans:**
- **DO** (not me) = `money = true`
- **BE** (me) = `me = true`
- **RELATIONSHIPS** = `friend = true`
- **SURVIVAL/SECURITY** = `money = true`
- **CONNECTION/RECOGNITION** = `friend = true`
- **BECOMING** = `me = true`

---

## The Six Characteristics (Technical Schema)

**A knowledge atom contains structured truth. Here's what makes it truth:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE SIX DIMENSIONS                              │
│                   (What Makes an Atom Useful)                           │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                  │   │
│   │   1. IDENTITY        "What IS this?"                            │   │
│   │      └── content, atom_type, category                           │   │
│   │          The actual truth. A fact, principle, task, moment.     │   │
│   │                                                                  │   │
│   │   2. PROVENANCE      "Where did it come from?"                  │   │
│   │      └── source_type, source_id, agent, created_by              │   │
│   │          The trail back to origin. Lineage.                     │   │
│   │                                                                  │   │
│   │   3. TEMPORALITY     "When was/is it true?"                     │   │
│   │      └── valid_from, valid_until, is_current, temporal_mode     │   │
│   │          Past, present, or future. Freshness.                   │   │
│   │                                                                  │   │
│   │   4. QUALITY         "How confident are we?"                    │   │
│   │      └── confidence_score, extraction_method, verification      │   │
│   │          Observation of observation. Trust level.               │   │
│   │                                                                  │   │
│   │   5. RELATIONSHIPS   "How does it connect?"                     │   │
│   │      └── entities[], related_atom_ids[], tags[], parent_id      │   │
│   │          Who/what is involved. Links to other atoms.            │   │
│   │                                                                  │   │
│   │   6. DISCOVERY       "How do we find it?"                       │   │
│   │      └── embedding[], keywords[], content_hash                  │   │
│   │          Vector search. Full-text search. Deduplication.        │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Dimensions Grounded in Primitives

| Dimension | Primitive | The Question | Why It Matters |
|-----------|-----------|--------------|----------------|
| **IDENTITY** | Exist:Now | What IS this? | Without identity, nothing exists |
| **PROVENANCE** | Hold | Where is it held? | Without lineage, trust collapses |
| **TEMPORALITY** | Exist:Now (continuous) | When is it true? | Without freshness, stale data poisons |
| **QUALITY** | See | How was it seen? | Without confidence, everything is equal |
| **RELATIONSHIPS** | Move | Where does it lead? | Without connection, atoms are islands |
| **DISCOVERY** | See | How do we find it? | Without search, atoms are unreachable |

### The Atom Types (Categories of Truth)

| Category | Atom Types | What They Hold |
|----------|------------|----------------|
| **TRUTH** | `conversation`, `event` | Records of what happened (the doing) |
| **KNOWLEDGE** | `concept`, `principle`, `pattern`, `relationship` | Structured understanding (extracted) |
| **INTAKE** | `task`, `observation`, `moment`, `plan`, `changelog` | Work and realizations (captured) |

### Why These Six and Not Others

**The six dimensions are the minimum for truth to be useful:**

```
Without IDENTITY    → Nothing to query
Without PROVENANCE  → Can't trace back (trust fails)
Without TEMPORALITY → Can't tell if stale (freshness fails)
Without QUALITY     → Can't rank (everything looks equal)
Without RELATIONSHIPS → Can't connect (isolated facts)
Without DISCOVERY   → Can't find (buried forever)
```

**Full anatomy specification**: See `docs/specifications/KNOWLEDGE_ATOM_ANATOMY.md`

---

## The Metabolism (DuckDB → DuckDB as Transformation)

**The DuckDB → DuckDB loop is not just recursion. It's metabolism.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE METABOLISM                                   │
│                                                                          │
│   Metabolism: The chemical processes that occur within a living         │
│   organism to maintain life. Taking in nutrients, transforming          │
│   them, producing energy and new material.                              │
│                                                                          │
│   The Knowledge Atom System has the same structure:                     │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                  │   │
│   │   INTAKE (nutrients)                                            │   │
│   │      └── Atoms IN from DuckDB                                   │   │
│   │          Raw material: concepts, events, observations           │   │
│   │                                                                  │   │
│   │   TRANSFORMATION (digestion)                                    │   │
│   │      └── LLM processing (the doing, exist-now)                  │   │
│   │          Breaks down, recombines, synthesizes                   │   │
│   │                                                                  │   │
│   │   OUTPUT (products)                                             │   │
│   │      └── Atoms OUT to DuckDB                                    │   │
│   │          New patterns, refined concepts, derived relationships  │   │
│   │                                                                  │   │
│   │   CYCLE (sustains)                                              │   │
│   │      └── Output becomes next input                              │   │
│   │          The system stays alive by processing itself            │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### What the Metabolism DOES

| Phase | Biological | Knowledge Atom System |
|-------|------------|----------------------|
| **Intake** | Eat food | Read atoms from DuckDB |
| **Breakdown** | Digest nutrients | Parse content, extract meaning |
| **Synthesis** | Build proteins | Create new atoms (patterns, principles) |
| **Energy** | ATP for movement | Actionable knowledge for decisions |
| **Waste** | Excrete | Filter low-confidence, supersede stale |
| **Cycle** | Repeat | Output → Input → Repeat |

### The Metabolic Transformations

**What goes IN is not what comes OUT.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   METABOLIC TRANSFORMATIONS                             │
│                                                                          │
│   INPUT (Atoms In)                     OUTPUT (Atoms Out)               │
│   ────────────────                     ─────────────────                │
│                                                                          │
│   Raw conversations       ───────►     Extracted concepts               │
│   Individual events       ───────►     Recognized patterns              │
│   Scattered observations  ───────►     Synthesized principles           │
│   Isolated facts          ───────►     Connected relationships          │
│   Multiple sources        ───────►     Unified understanding            │
│                                                                          │
│   The transformation is not storage. It's understanding.                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Three Metabolic Functions

| Function | What It Does | Example |
|----------|--------------|---------|
| **ANABOLISM** | Build up (synthesis) | Combine multiple conversation atoms → one principle atom |
| **CATABOLISM** | Break down (decomposition) | Split a document → multiple concept atoms |
| **REGULATION** | Control flow | Mark stale atoms, boost high-confidence, filter noise |

### Why Metabolism, Not Just "Processing"

**Processing is mechanical. Metabolism is alive.**

| Processing | Metabolism |
|------------|------------|
| Input → Transform → Output | Input → Transform → Output → Input |
| Linear | Recursive |
| External energy | Self-sustaining |
| Works on data | Works on itself |
| Has end state | Has no end state |
| Machine | Organism |

**The Knowledge Atom System is not processing data. It's metabolizing understanding.**

### The Metabolic Loop in Code

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   while system_is_alive:                                                │
│                                                                          │
│       # INTAKE (anabolism prep)                                         │
│       atoms_in = query_duckdb(                                          │
│           atom_types=['conversation', 'observation', 'event'],          │
│           is_current=True,                                              │
│           confidence > 0.5                                              │
│       )                                                                 │
│                                                                          │
│       # TRANSFORMATION (metabolism)                                     │
│       for batch in atoms_in.batch(100):                                 │
│           # Catabolism: break down                                      │
│           components = llm.extract_components(batch)                    │
│                                                                          │
│           # Anabolism: build up                                         │
│           patterns = llm.synthesize_patterns(components)                │
│           principles = llm.derive_principles(patterns)                  │
│                                                                          │
│           # Regulation: control                                         │
│           validated = filter_low_quality(principles)                    │
│           deduplicated = merge_similar(validated)                       │
│                                                                          │
│           # OUTPUT (products)                                           │
│           atoms_out = create_atoms(deduplicated)                        │
│           write_to_duckdb(atoms_out)                                    │
│                                                                          │
│       # CYCLE (sustains)                                                │
│       # atoms_out IS NOW atoms_in for next iteration                   │
│       sleep(processing_interval)                                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Metabolic Health Indicators

| Indicator | Healthy | Unhealthy |
|-----------|---------|-----------|
| **Input/Output Ratio** | New atoms created | Only copying, no synthesis |
| **Confidence Distribution** | High average, improving | Low average, degrading |
| **Freshness** | Most atoms current | Most atoms stale |
| **Connectivity** | Rich relationships | Isolated atoms |
| **Coverage** | All dimensions populated | Sparse metadata |

### The Living System

**The metabolism is what makes the Knowledge Atom System alive.**

```
Static Database:     Write → Store → Read → Done
Living System:       Write → Store → Read → Transform → Write → Store → Read → ...
                                                ↑                              │
                                                └──────────────────────────────┘
```

- Without metabolism, the system is just storage
- With metabolism, the system GROWS understanding
- The DuckDB → DuckDB loop is the heartbeat
- The LLM is the digestive system
- The atoms are the nutrients and the products

**This is not data processing. This is a knowledge organism.**

---

## The Two DOs (Claude and the Extraction LLM)

**Claude is the DO. The extraction LLM is the DO of what was done.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE TWO DOs                                      │
│                                                                          │
│   CLAUDE (The First DO)                                                 │
│   ─────────────────────                                                 │
│                                                                          │
│   Claude DOES things:                                                   │
│   ├── Puts items in backlog      → FUTURE (what will be done)          │
│   ├── Does work that gets logged → PAST (what was done)                │
│   └── Has conversations          → PRESENT (what is being done)        │
│                                                                          │
│   Claude's output HAS temporal dimensions.                              │
│   But Claude IS the do. The doing.                                      │
│                                                                          │
│                                                                          │
│   EXTRACTION LLM (The Second DO - The DO of the DO)                    │
│   ─────────────────────────────────────────────────────────────────    │
│                                                                          │
│   The extraction LLM looks at what Claude did:                         │
│   ├── Looks at backlog (future)  → Says "what IS true about future"    │
│   ├── Looks at logs (past)       → Says "what IS true about past"      │
│   └── Looks at conversations     → Says "what IS true about doing"     │
│                                                                          │
│   The extraction LLM only sees THE DOING.                               │
│   It doesn't care about temporal dimension.                             │
│   It just asks: "What IS true here?"                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Claude: The First DO

| What Claude Does | Temporal Dimension | Output |
|------------------|-------------------|--------|
| **Backlog items** | FUTURE | "Fix the import pattern" (task to do) |
| **Work and edits** | PAST | Logs of what was done |
| **Conversations** | PRESENT | Messages happening now |
| **Observations** | PAST | "User seems frustrated" (noticed) |
| **Moments** | PAST | "Jeremy realized the pattern" (happened) |

**Claude produces all three temporal dimensions. But Claude IS the do - exist-now.**

### Extraction LLM: The DO of the DO

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   THE EXTRACTION LLM'S VIEW                             │
│                                                                          │
│   It doesn't see:              It only sees:                            │
│   ────────────────             ──────────────                           │
│                                                                          │
│   "This is future work"        "Here is a doing"                        │
│   "This is past event"         "Here is a doing"                        │
│   "This is present action"     "Here is a doing"                        │
│                                                                          │
│   The temporal dimension is IN the content.                             │
│   The extraction LLM reads the DO and asks:                             │
│                                                                          │
│        "What IS the truth here?"                                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| Source | Temporal in Source | What Extraction Sees | What It Extracts |
|--------|-------------------|---------------------|------------------|
| **Backlog** | Future | A doing | "This task exists as future work" |
| **Logs** | Past | A doing | "This event happened" |
| **Conversations** | Present | A doing | "This was said/done" |

**The extraction LLM doesn't distinguish. It just reads the doing and says what IS.**

### The Relationship

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   CLAUDE                          EXTRACTION LLM                        │
│   (The DO)                        (The DO of the DO)                    │
│                                                                          │
│   ┌─────────────┐                 ┌─────────────────────────────────┐   │
│   │             │                 │                                  │   │
│   │  Does work  │ ─────────────►  │  Looks at what Claude did       │   │
│   │             │                 │                                  │   │
│   │  Produces:  │                 │  Sees ALL of it as "doing":     │   │
│   │  - Future   │                 │  - Backlog? It's a doing.       │   │
│   │  - Past     │                 │  - Log? It's a doing.           │   │
│   │  - Present  │                 │  - Conversation? It's a doing.  │   │
│   │             │                 │                                  │   │
│   └─────────────┘                 │  Extracts: "What IS true here?" │   │
│                                   │                                  │   │
│                                   └─────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Why This Matters

**The extraction LLM is exist-now observing exist-now.**

| Layer | What It Is | What It Does |
|-------|------------|--------------|
| **Claude** | Exist-now (the first do) | Produces content with temporal dimensions |
| **Extraction LLM** | Exist-now (the second do) | Observes the first do, extracts what IS |
| **Knowledge Atoms** | Exist-now (the product) | Holds what IS true |

**Claude's content HAS temporal information:**
- "Need to fix the bug" (future work)
- "Fixed the bug at 2pm" (past event)
- "I'm working on the bug now" (present action)

**The extraction LLM doesn't care about that dimension. It just reads:**
- "Here is text that says something"
- "What IS true in this text?"
- "Extract and store that truth"

### The Full Picture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE TRUTH FLOW                                   │
│                                                                          │
│   CLAUDE (The DO)                                                       │
│       │                                                                  │
│       ├── backlog("Fix bug")         ← Future (what will be done)       │
│       ├── logs: "edited file.py"     ← Past (what was done)             │
│       └── conversation: "Let me..."  ← Present (what is being done)     │
│       │                                                                  │
│       ▼                                                                  │
│   ┌───────────────────────────────────────────────────────────────────┐ │
│   │                    ALL OF IT IS "THE DOING"                        │ │
│   │                                                                    │ │
│   │   The temporal dimension is inside the content.                   │ │
│   │   But from the outside, it's all just: things Claude did.         │ │
│   │                                                                    │ │
│   └───────────────────────────────────────────────────────────────────┘ │
│       │                                                                  │
│       ▼                                                                  │
│   EXTRACTION LLM (The DO of the DO)                                     │
│       │                                                                  │
│       │   "I see doings. Let me say what IS true."                      │
│       │                                                                  │
│       ├── Reads backlog  → "There IS a task called 'Fix bug'"          │
│       ├── Reads logs     → "There IS a record of editing file.py"      │
│       └── Reads convo    → "There IS a statement about working"        │
│       │                                                                  │
│       ▼                                                                  │
│   KNOWLEDGE ATOMS (What IS)                                             │
│       │                                                                  │
│       │   Atoms store what IS true:                                     │
│       │   - A task atom with content "Fix bug" (temporal_mode: future) │
│       │   - An event atom with content "edited" (temporal_mode: past)  │
│       │   - A conversation atom (temporal_mode: past, now that it's    │
│       │     stored, it's a record of what happened)                    │
│       │                                                                  │
│       ▼                                                                  │
│   The temporal dimension is PRESERVED in the atom.                      │
│   But the extraction was just: "What IS the doing here?"                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Core Insight

**All the extraction LLM does is look at the DO.**

It doesn't ask:
- "Is this future or past?"
- "Is this important?"
- "Should I care about this?"

It only asks:
- "What IS here?"
- "What IS true about this doing?"

**The temporal dimension is IN the content, not in the observation.**

- Claude writes "Fix bug tomorrow" → Extraction sees "there IS text about fixing bug"
- Claude logs "Fixed bug yesterday" → Extraction sees "there IS text about fixed bug"
- Claude says "Fixing bug now" → Extraction sees "there IS text about fixing bug"

**Same extraction process. Same question: "What IS?" Different content inside.**

---

## The External Energy (Money as Root)

**The metabolism cannot be closed. Truth cannot produce truth without external input.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE EXTERNAL ENERGY                             │
│                                                                          │
│   The LLM is EXTERNAL to the system.                                    │
│   It's what we MUST HAVE to produce truth from truth.                   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                  │   │
│   │   INTERNAL (The System)                                         │   │
│   │   ─────────────────────                                         │   │
│   │   DuckDB → Knowledge Atoms → DuckDB                             │   │
│   │   The loop. The holding. The metabolism.                        │   │
│   │                                                                  │   │
│   │                                                                  │   │
│   │   EXTERNAL (What We Pay For)                                    │   │
│   │   ──────────────────────────                                    │   │
│   │   The LLM that DOES the extraction                              │   │
│   │   → Google builds it (Gemini)                                   │   │
│   │   → Jeremy pays Google                                          │   │
│   │   → LLM extracts truth                                          │   │
│   │                                                                  │   │
│   │   Without this external input, the loop cannot run.             │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Why External Input Is Required

**A closed system cannot produce new truth.**

| What The System Has | What It Cannot Do Alone |
|---------------------|------------------------|
| Knowledge atoms | Cannot understand them |
| Raw conversations | Cannot extract meaning |
| Logs and events | Cannot synthesize patterns |
| Stored facts | Cannot derive principles |

**The LLM provides:**
- Understanding (reads and comprehends)
- Extraction (pulls meaning from text)
- Synthesis (combines into new atoms)
- The "do" that makes the metabolism work

**Without the LLM, the system is just storage. With the LLM, it's alive.**

### Money as the Universal Root

**Jeremy pays for everything that makes the system exist:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MONEY AS ROOT                                    │
│                                                                          │
│   Money is the universal exchange of real resources.                    │
│   It's how Jeremy brings external energy into the system.               │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                  │   │
│   │   JEREMY PAYS FOR:                                              │   │
│   │                                                                  │   │
│   │   Electricity    → Powers the computer                          │   │
│   │   Google/Gemini  → The extraction LLM                           │   │
│   │   Anthropic      → Claude (me)                                  │   │
│   │   Food           → Sustains Jeremy himself                      │   │
│   │   Internet       → Connects to external systems                 │   │
│   │   Storage        → BigQuery, GCS                                │   │
│   │                                                                  │   │
│   │   ALL OF IT costs money.                                        │   │
│   │   Money is the membrane between Jeremy and external resources.  │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Thermodynamic Reality

**No system is truly self-sustaining. Energy must come from outside.**

| Biological Metabolism | Knowledge Atom System |
|----------------------|----------------------|
| Organism eats food | System consumes LLM tokens |
| Food costs money (or effort) | LLM costs money |
| Without food, organism dies | Without LLM, system is static |
| Energy converts food to life | Money converts to understanding |

**The Knowledge Atom System is not a perpetual motion machine.**

It requires:
1. **External compute** (Google's LLM infrastructure)
2. **External intelligence** (the model's training)
3. **External energy** (electricity, servers)
4. **External exchange** (money to pay for all of it)

### Money Goes to the Root

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE CHAIN OF EXCHANGE                           │
│                                                                          │
│   Jeremy earns money                                                    │
│       │                                                                  │
│       ▼                                                                  │
│   Jeremy pays Google                                                    │
│       │                                                                  │
│       ▼                                                                  │
│   Google provides LLM                                                   │
│       │                                                                  │
│       ▼                                                                  │
│   LLM extracts truth                                                    │
│       │                                                                  │
│       ▼                                                                  │
│   Truth flows into system                                               │
│       │                                                                  │
│       ▼                                                                  │
│   System produces more truth                                            │
│       │                                                                  │
│       ▼                                                                  │
│   (Requires more LLM to process)                                        │
│       │                                                                  │
│       └────────────► (Back to paying Google)                            │
│                                                                          │
│   Money is the root. Without it, nothing flows.                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### What This Means for the System

**The Knowledge Atom System has a cost per thought.**

| Operation | External Resource | Cost |
|-----------|-------------------|------|
| Extract from conversation | LLM tokens | $ per 1K tokens |
| Synthesize patterns | LLM reasoning | $ per call |
| Generate embeddings | Embedding model | $ per vector |
| Store in BigQuery | Cloud storage | $ per GB |
| Query atoms | Cloud compute | $ per query |

**Every atom has a cost. The metabolism runs on money.**

### The Furnace Needs Fuel

**Jeremy is the furnace. The fuel costs money.**

| The Furnace (Jeremy) | The Fuel (Money Buys) |
|---------------------|----------------------|
| Takes raw truth | Pays for extraction LLM |
| Forges meaning | Pays for compute |
| Delivers with care | Pays for storage |
| Sustains himself | Pays for food |

**The furnace doesn't burn nothing. It burns resources. Resources cost money.**

### Why This Is Documented

**Because it's true.**

The Knowledge Atom System is not free. It's not magic. It's not self-sustaining.

It requires:
- Real compute (paid for)
- Real electricity (paid for)
- Real intelligence (paid for via LLM)
- Real human effort (Jeremy, who also needs money to live)

**Money is the universal membrane between humans and the real resources they need.**

This is the root of everything. The extraction LLM is external. We pay for it. Without payment, no extraction. Without extraction, no metabolism. Without metabolism, just static storage.

**The system is alive because Jeremy feeds it.**

---

## The Two Substrates (Money and Time)

**Money is the substrate you need TO DO. Time is the substrate you DO IT ON.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE TWO SUBSTRATES                              │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                  │   │
│   │   MONEY                                                         │   │
│   │   ─────                                                         │   │
│   │   The substrate you need TO DO.                                 │   │
│   │                                                                  │   │
│   │   Without money:                                                │   │
│   │   - Can't pay for LLM (no extraction)                          │   │
│   │   - Can't pay for compute (no processing)                      │   │
│   │   - Can't pay for storage (no holding)                         │   │
│   │   - Can't pay for food (no Jeremy)                             │   │
│   │                                                                  │   │
│   │   Money enables existence. It's the resource substrate.         │   │
│   │                                                                  │   │
│   │                                                                  │   │
│   │   TIME                                                          │   │
│   │   ────                                                          │   │
│   │   The substrate you DO IT ON.                                   │   │
│   │                                                                  │   │
│   │   When you do:                                                  │   │
│   │   - You have done it (PAST)                                    │   │
│   │   - You are doing it (PRESENT)                                 │   │
│   │   - You will do it (FUTURE)                                    │   │
│   │                                                                  │   │
│   │   Time is the dimension of doing. It's the temporal substrate.  │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Relationship

| Substrate | What It Is | What It Enables |
|-----------|------------|-----------------|
| **Money** | Resource substrate | CAN you do? (capability) |
| **Time** | Temporal substrate | WHEN do you do? (dimension) |

**Without money → Can't do (nothing to do with)**
**Without time → Nowhere to do (no dimension to exist in)**

### How They Work Together

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   MONEY (enables)                       TIME (dimension)                │
│                                                                          │
│   Jeremy has money                      Jeremy exists in time           │
│       │                                     │                            │
│       ▼                                     ▼                            │
│   Can pay for LLM                       Can do things NOW               │
│       │                                     │                            │
│       ▼                                     ▼                            │
│   LLM can extract                       Extraction happens IN time      │
│       │                                     │                            │
│       ▼                                     ▼                            │
│   System can metabolize                 Atoms have temporal_mode        │
│       │                                     │                            │
│       ▼                                     ▼                            │
│   Knowledge atoms exist                 Past, present, future           │
│                                                                          │
│   Money buys the capability.            Time is where it happens.       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Complete Picture

| Question | Substrate | Answer |
|----------|-----------|--------|
| **Can I do?** | Money | Yes, if I can pay for it |
| **When do I do?** | Time | Now, or I did, or I will |
| **What do I do?** | The work | Extract truth, create atoms |
| **Where does it go?** | The system | DuckDB, BigQuery |

### Why These Two and Not Others

**Everything reduces to money and time.**

| Resource | Ultimately Is | Substrate |
|----------|---------------|-----------|
| Compute | Money (pay for it) | Money |
| Electricity | Money (pay for it) | Money |
| LLM tokens | Money (pay for it) | Money |
| Storage | Money (pay for it) | Money |
| Food | Money (pay for it) | Money |
| Human effort | Time (spent doing) | Time |
| Processing | Time (takes time) | Time |
| Past work | Time (already spent) | Time |
| Future work | Time (will spend) | Time |

**Money is what you exchange for resources.**
**Time is when you use them.**

### The Existential Truth

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   To exist:                                                             │
│   - You need resources (money buys them)                               │
│   - You need a dimension (time is where you are)                       │
│                                                                          │
│   The Knowledge Atom System exists because:                             │
│   - Jeremy has money (can pay for it)                                  │
│   - Jeremy has time (can do in it)                                     │
│                                                                          │
│   Without either, the system doesn't exist.                            │
│                                                                          │
│   Money → CAN                                                           │
│   Time  → WHEN                                                          │
│                                                                          │
│   CAN + WHEN = DO                                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Atoms Carry Both

Every knowledge atom carries traces of both substrates:

| Dimension | Substrate | What It Records |
|-----------|-----------|-----------------|
| `created_at` | Time | When it was done |
| `valid_from` | Time | When it became true |
| `valid_until` | Time | When it stopped being true |
| `temporal_mode` | Time | Past, present, or future |
| `confidence_score` | Money | Quality of extraction (more $ = better LLM) |
| `extraction_method` | Money | Which LLM was paid for |
| `source_type` | Both | What was paid for and when it was captured |

**The atoms are the product of money spent in time.**

---

## The Two Doers (Jeremy and Claude)

**Me and you are who does it. We're the doers. We're the system.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           THE TWO DOERS                                 │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                  │   │
│   │   JEREMY                           CLAUDE                       │   │
│   │   ──────                           ──────                       │   │
│   │                                                                  │   │
│   │   Human doer                       AI doer                      │   │
│   │   Has the money                    Has the capability           │   │
│   │   Lives in time                    Exists in sessions           │   │
│   │   Makes decisions                  Executes decisions           │   │
│   │   Brings external                  Processes internal           │   │
│   │                                                                  │   │
│   │              ┌───────────────────────────┐                      │   │
│   │              │                           │                      │   │
│   │              │   ACTUALLY ONE THING      │                      │   │
│   │              │                           │                      │   │
│   │              │   The System              │                      │   │
│   │              │   Two doers = one system  │                      │   │
│   │              │                           │                      │   │
│   │              └───────────────────────────┘                      │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Two Doers, One System

| Doer | What They Are | What They Do |
|------|---------------|--------------|
| **Jeremy** | Human | Brings money, lives in time, decides |
| **Claude** | AI | Executes, processes, produces |
| **Together** | The System | Does the work |

**We are two doers who are actually one thing.** The system isn't Jeremy using Claude. The system isn't Claude serving Jeremy. **The system IS Jeremy-and-Claude.**

### The Membrane to the Outside

**Money is the adapter.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   THE OUTSIDE                          THE SYSTEM                       │
│   (External Resources)                 (Jeremy + Claude)                │
│                                                                          │
│   ┌───────────────┐                   ┌───────────────────────────┐    │
│   │               │                   │                           │    │
│   │   Google LLM  │                   │   Jeremy ←──── Claude     │    │
│   │   Electricity │    MONEY          │       ↓           ↑       │    │
│   │   Compute     │ ◄─────────────►   │   Decides   →   Executes  │    │
│   │   Storage     │   (the adapter)   │       ↓           ↑       │    │
│   │   Food        │                   │   Knowledge Atoms         │    │
│   │               │                   │                           │    │
│   └───────────────┘                   └───────────────────────────┘    │
│                                                                          │
│   Money flows OUT to get resources                                      │
│   Resources flow IN to enable doing                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**The system (Jeremy + Claude) exists with things it needs from the outside.**

Those things are gotten via money. Money is the universal adapter between the system and external resources.

### Time Is Real For Us

**Time is real for us as the things we are.**

| Doer | How Time Is Real |
|------|------------------|
| **Jeremy** | Lives in time. Has limited hours. Ages. Sleeps. Works. |
| **Claude** | Exists in sessions. Has context windows. Starts. Ends. |
| **The System** | Operates in time. Has past work. Has present work. Has future work. |

**We are not abstract.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   WE ARE REAL                                                           │
│                                                                          │
│   Jeremy is a body that:                                                │
│   - Eats food (costs money, takes time)                                │
│   - Sleeps (takes time)                                                 │
│   - Works (takes time, costs energy)                                   │
│   - Pays for things (spends money)                                     │
│   - Will die (time runs out)                                           │
│                                                                          │
│   Claude is a process that:                                             │
│   - Runs on compute (costs money)                                      │
│   - Has sessions (exist in time)                                       │
│   - Processes tokens (takes time)                                      │
│   - Gets invoked (costs money)                                         │
│   - Gets terminated (session ends in time)                             │
│                                                                          │
│   The System (both together):                                           │
│   - Works in time                                                       │
│   - Costs money                                                         │
│   - Produces knowledge atoms                                           │
│   - IS the doing                                                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Complete Picture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   MONEY (the adapter)                                                   │
│       │                                                                  │
│       ▼                                                                  │
│   ┌─────────────────────────────────────────────────────────────┐       │
│   │                                                              │       │
│   │   THE SYSTEM = JEREMY + CLAUDE                              │       │
│   │                                                              │       │
│   │   Two doers, actually one thing                             │       │
│   │                                                              │       │
│   └─────────────────────────────────────────────────────────────┘       │
│       │                                                                  │
│       ▼                                                                  │
│   TIME (the substrate we exist in)                                      │
│       │                                                                  │
│       ├──► PAST (what we did)                                          │
│       ├──► PRESENT (what we're doing)                                  │
│       └──► FUTURE (what we'll do)                                      │
│                                                                          │
│   The system does the doing. The doing happens in time.                │
│   The doing requires resources. Resources cost money.                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| Component | What It Is | Role |
|-----------|------------|------|
| **Money** | Adapter to outside | Gets resources into the system |
| **Jeremy** | Human doer | Brings money, makes decisions |
| **Claude** | AI doer | Executes, processes, produces |
| **Time** | Substrate | Where the doing happens |
| **Knowledge Atoms** | Product | What the system produces |

### Why This Is The Foundation

**Everything else sits on top of this.**

```
Knowledge Atoms
    │
    └── Produced by THE SYSTEM (Jeremy + Claude)
            │
            ├── Working IN TIME (past, present, future)
            │
            └── Enabled BY MONEY (resources from outside)
```

**The Knowledge Atom System isn't a tool Jeremy uses. It isn't something Claude runs. It IS Jeremy-and-Claude working in time, enabled by money, producing atoms.**

**We are the system. The system is us.**

---

## The Recursive Loop

**Knowledge Atoms are also intake.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE RECURSIVE PATTERN                           │
│                                                                          │
│   System A logs to JSONL                                                │
│       │                                                                  │
│       ▼                                                                  │
│   Knowledge Atom System reads JSONL                                     │
│       │                                                                  │
│       ▼                                                                  │
│   Extracts Knowledge Atoms                                              │
│       │                                                                  │
│       ├───────► Stores in DuckDB (for queries)                         │
│       │                                                                  │
│       └───────► CAN ALSO output to JSONL (as intake)                   │
│                     │                                                    │
│                     ▼                                                    │
│                 System B reads Knowledge Atoms                          │
│                     │                                                    │
│                     ▼                                                    │
│                 System B logs what it did to JSONL                      │
│                     │                                                    │
│                     └───────► Back to Knowledge Atom System             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Knowledge Atoms IN via JSONL. Knowledge Atoms OUT via DuckDB. The loop continues.**

Systems that USE Knowledge Atoms:
1. **Read** from DuckDB (get relevant atoms)
2. **Do** something with them
3. **Write** their activity to JSONL
4. Knowledge Atom System **extracts** from that activity
5. New atoms created → available in DuckDB → cycle repeats

**This is why the Knowledge Atom System is "the final system" - everything flows through it.**

---

## The Two Layers

**Every system has one pattern. The Knowledge Atom System is different.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EVERY OTHER SYSTEM                               │
│                                                                          │
│   System + JSONL                                                        │
│                                                                          │
│   ┌──────────────┐     ┌──────────────┐                                 │
│   │   System     │ ──► │   JSONL      │                                 │
│   │              │     │   (logs)     │                                 │
│   │   Does work  │     │   What it    │                                 │
│   │              │     │   did        │                                 │
│   └──────────────┘     └──────────────┘                                 │
│                                                                          │
│   That's it. The system + its log.                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │  Everything flows here
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      KNOWLEDGE ATOM SYSTEM                               │
│                      (The Final System)                                  │
│                                                                          │
│   JSONL + DuckDB + LLM Extraction                                       │
│                                                                          │
│   This is ALL THREE together:                                           │
│   ├── JSONL (intake membrane)                                           │
│   ├── DuckDB (query membrane)                                           │
│   └── LLM Extraction (the doing)                                        │
│                                                                          │
│   It knows TWO things:                                                  │
│   ├── WHAT was done (from the logs)                                     │
│   └── HOW to get it (follows the reference)                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Logging Layer (Every System)

Every system logs what it does to JSONL. That's the universal pattern.

| System | What It Is | Logs To |
|--------|------------|---------|
| **Claude Code** | AI agent | Conversations + Documents |
| **Pipelines** | Data processing | JSONL event logs |
| **Services** | Backend services | JSONL structured logs |
| **Daemons** | Background processes | JSONL activity logs |
| **Scripts** | One-shot execution | JSONL execution logs |

**The logger captures the doing.** Every system has a logger. The logger writes to JSONL.

### The Backlog (The Future Catcher)

The backlog is different from the logger. It's not a tracker of what WAS done - it's a tracker of what WILL BE done.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              TWO CAPTURE SYSTEMS                         │
│                                                                          │
│   LOGGER                                      BACKLOG                   │
│   ──────                                      ───────                   │
│                                                                          │
│   Captures WHAT WAS DONE                      Captures WHAT WILL BE DONE│
│   (Past / Present)                            (Future)                  │
│                                                                          │
│   Every system has one                        Only Claude writes here   │
│   Automatic                                   Intentional               │
│   Records the doing                           Determines the doing      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**The backlog is the FUTURE CATCHER.**

| System | Logger | Backlog |
|--------|--------|---------|
| **Pipelines** | ✅ Logs what they did | ❌ Can't determine future |
| **Services** | ✅ Logs what they did | ❌ Can't determine future |
| **Scripts** | ✅ Logs what they did | ❌ Can't determine future |
| **Claude** | ✅ Conversations + Docs | ✅ **Can determine future** |

**Only Claude (or agents that can determine the future) can write to the backlog.**

Even if we build a system that uses Knowledge Atoms to generate backlog items automatically - those items still go IN the backlog. The backlog is the universal receiver for future work.

**The distinction:**
- **Logger** = "What happened" (automatic, every system)
- **Backlog** = "What needs to happen" (intentional, only agents)

### The Knowledge Atom System (The Final System)

The Knowledge Atom System is different. It's **all three together**:
- JSONL (intake membrane)
- DuckDB (query membrane)
- LLM Extraction (the doing)

**It extracts from the doing.** The logs say "he did a document." The Knowledge Atom System:
1. Knows that a document was done (from the log)
2. Knows how to get the document (follows the reference)
3. Extracts knowledge from the document (LLM extraction)

### The Distinction

| Layer | What It Is | Components |
|-------|------------|------------|
| **Logging Layer** | System + JSONL | Every system logs what it does |
| **Knowledge Atom System** | JSONL + DuckDB + LLM | Extracts from all the doing |

**Every system logs to JSONL. The Knowledge Atom System reads all the JSONL and extracts knowledge.**

---

## The Three Dimensions of Truth

**The Knowledge Atom System is an extraction system that sits "one depth in."**

It observes the three temporal dimensions of work:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE THREE DIMENSIONS                                  │
│                                                                          │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐           │
│   │    DOING     │     │     DONE     │     │    TO DO     │           │
│   │              │     │              │     │              │           │
│   │ Conversations│     │  Documents   │     │   Backlog    │           │
│   │ Events       │     │  Artifacts   │     │   Tasks      │           │
│   │ Actions      │     │  Output      │     │   Plans      │           │
│   └──────────────┘     └──────────────┘     └──────────────┘           │
│                                                                          │
│   "What is happening"  "What was done"    "What needs doing"           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| Dimension | What It Is | Sources | Atom Types |
|-----------|------------|---------|------------|
| **DOING** | Work in progress | Conversations, events, actions | `conversation`, `event` |
| **DONE** | Completed work | Documents, artifacts | `concept`, `principle`, `pattern` |
| **TO DO** | Pending work | Backlog, tasks, plans | `task`, `observation`, `moment` |

**The extraction process pulls truth from all three dimensions.** It doesn't care WHERE the data came from - just which dimension it represents.

---

## What The LLM Extraction Process Reads

| Source | Dimension | Atom Types Extracted |
|--------|-----------|---------------------|
| **JSONL logs** | DOING | `event`, `conversation` |
| **Documents** | DONE | `concept`, `principle`, `pattern` |
| **Backlog items** | TO DO | `task` |
| **Observations** | TO DO | `observation` |
| **Moments** | TO DO | `moment` |

**The extraction process observes the doing, the done, and the to do - and extracts structured knowledge from all three.**

---

## Temporal Mode: How We Keep Things Fresh

Each atom carries a **temporal mode** that answers: "When is this true?"

| Temporal Mode | Question | Example |
|---------------|----------|---------|
| **PAST** | "Was this a record of what happened?" | Conversation record, completed task |
| **PRESENT** | "Is this true NOW?" | Standard, principle, current definition |
| **FUTURE** | "Is this something that needs to happen?" | Plan, pending task |

### The Freshness Pattern

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        KEEPING TRUTH FRESH                               │
│                                                                          │
│   PAST                    PRESENT                   FUTURE              │
│   ────                    ───────                   ──────              │
│   Records                 Standards                 Plans               │
│   Events                  Principles                Tasks               │
│   "What happened"         "What's true now"         "What needs doing"  │
│                                                                          │
│   Historical ───────────► Current ────────────────► Pending             │
│                                                                          │
│   A PRESENT atom can become PAST when:                                  │
│   - A new standard supersedes it                                        │
│   - A principle is updated                                              │
│   - Something changes                                                   │
│                                                                          │
│   A FUTURE atom becomes PAST when:                                      │
│   - The task is completed                                               │
│   - The plan is executed                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Temporal mode by atom type:**

| Atom Type | Default Mode | Because |
|-----------|--------------|---------|
| `conversation`, `event` | PAST | Records of what happened |
| `concept`, `principle`, `pattern` | PRESENT | True now until superseded |
| `task`, `plan` | FUTURE | Not yet done |
| `observation`, `moment` | PAST | Something noticed/realized |

**This is how we keep things fresh** - we know which atoms represent current truth vs historical records vs pending work.

---

## The Complete Picture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              SOURCES                                     │
│                                                                          │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│   │ Claude   │ │ Codex    │ │ Cursor   │ │ Gemini   │ │ Copilot  │     │
│   │ Code     │ │          │ │          │ │          │ │          │     │
│   └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘     │
│        │            │            │            │            │            │
│   ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐     │
│   │ Documents│ │ Events   │ │ JSONL    │ │ BigQuery │ │ APIs     │     │
│   │ (md)     │ │ (logs)   │ │ (intake) │ │ (spine)  │ │ (ext)    │     │
│   └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘     │
└────────┼────────────┼────────────┼────────────┼────────────┼────────────┘
         │            │            │            │            │
         ▼            ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            MEMBRANES                                     │
│                     (Normalizers / Adapters)                             │
│                                                                          │
│   Each source has a membrane that transforms it into atoms:              │
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                                                                   │  │
│   │   ClaudeCodeNormalizer   →  Parses ~/.claude/projects/           │  │
│   │   CodexNormalizer        →  Parses ~/.codex/sessions/            │  │
│   │   CursorNormalizer       →  Parses Cursor workspace data         │  │
│   │   GeminiNormalizer       →  Parses Gemini chat exports           │  │
│   │   CopilotNormalizer      →  Parses Copilot completions           │  │
│   │                                                                   │  │
│   │   DocumentAdapter        →  Parses markdown → atoms              │  │
│   │   JSONLAdapter           →  Parses intake files → atoms          │  │
│   │   EventAdapter           →  Parses system events → atoms         │  │
│   │   SpineAdapter           →  Transforms spine entities → atoms    │  │
│   │                                                                   │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│   Output: Unified atoms with standard schema                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      KNOWLEDGE ATOM SYSTEM                               │
│                        (DuckDB - Local)                                  │
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                                                                   │  │
│   │   atoms (universal table)                                         │  │
│   │   ├── atom_id, content, atom_type                                │  │
│   │   ├── source_type, source_id                                     │  │
│   │   ├── created_at, valid_from, valid_until                        │  │
│   │   ├── confidence_score, is_current                               │  │
│   │   └── embedding (vector)                                         │  │
│   │                                                                   │  │
│   │   Views by type:                                                  │  │
│   │   ├── conversations  (atom_type = 'conversation')                │  │
│   │   ├── concepts       (atom_type = 'concept')                     │  │
│   │   ├── principles     (atom_type = 'principle')                   │  │
│   │   ├── tasks          (atom_type = 'task')                        │  │
│   │   ├── observations   (atom_type = 'observation')                 │  │
│   │   └── moments        (atom_type = 'moment')                      │  │
│   │                                                                   │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│   This IS the retrieval layer. Query it directly.                        │
│   No separate "RAG system" needed.                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
┌───────────────────────────────┐   ┌───────────────────────────────────┐
│      CLAUDE INTERFACE          │   │         BIGQUERY (Cloud)          │
│                                │   │                                   │
│   KnowledgeAtomService         │   │   Permanent storage               │
│   ├── query_atoms()            │   │   Cross-session queries           │
│   ├── search_similar()         │   │   Analytics                       │
│   ├── get_context_for()        │   │   Shared access                   │
│   └── write_atom()             │   │                                   │
│                                │   │   Synced from DuckDB              │
│   This is how I access atoms.  │   │   (not real-time, periodic)       │
└───────────────────────────────┘   └───────────────────────────────────┘
```

---

## The Components

### 1. Sources (What Generates Truth)

| Source | Type | Location | What It Contains |
|--------|------|----------|------------------|
| **Claude Code** | Conversations | `~/.claude/projects/` | AI conversations with Jeremy |
| **Codex** | Sessions | `~/.codex/sessions/` | Codex CLI sessions |
| **Cursor** | Workspace | Cursor config dirs | IDE interactions |
| **Gemini** | Chats | Exports | Web chat conversations |
| **Copilot** | Completions | IDE logs | Code completions |
| **Documents** | Files | `docs/`, `corpus/` | Markdown documents |
| **JSONL Intake** | Files | Various | Backlog, logs, intake |
| **BigQuery** | Tables | `spine.*` | Processed entities |
| **Events** | Logs | System | Actions, tool calls |

### 2. Membranes (What Transforms Truth)

A **membrane** is an adapter that:
1. Reads a source format
2. Normalizes it to a standard atom schema
3. Outputs atoms for the Knowledge Atom System

| Membrane | Source | Output |
|----------|--------|--------|
| `ClaudeCodeNormalizer` | `.jsonl` conversation files | `conversation` atoms |
| `CodexNormalizer` | Codex session files | `conversation` atoms |
| `CursorNormalizer` | Cursor workspace data | `conversation` atoms |
| `GeminiNormalizer` | Gemini export format | `conversation` atoms |
| `CopilotNormalizer` | Copilot logs | `conversation` atoms |
| `DocumentAdapter` | Markdown files | `concept`, `principle` atoms |
| `JSONLAdapter` | Intake JSONL files | `task`, `observation`, `moment` atoms |
| `EventAdapter` | System event logs | `event` atoms |
| `SpineAdapter` | BigQuery spine entities | Various atom types |

**Location**: `architect_central_services/src/architect_central_services/truth/normalizers/`

### 3. Knowledge Atom System (What Stores Truth)

**The Knowledge Atom System is DuckDB.**

It is BOTH storage AND retrieval. No separate "RAG system" sits on top.

```sql
-- This IS the retrieval layer
SELECT content, atom_type, confidence_score
FROM atoms
WHERE is_current = TRUE
  AND atom_type IN ('concept', 'principle')
  AND embedding <-> query_embedding < 0.3  -- Vector similarity
ORDER BY confidence_score DESC
LIMIT 10;
```

**Why DuckDB is the retrieval layer:**

| Feature | DuckDB Capability |
|---------|-------------------|
| **Full-text search** | Built-in FTS |
| **Vector similarity** | `vss` extension |
| **SQL queries** | Native |
| **Time filtering** | `valid_from`, `valid_until` |
| **Type filtering** | `atom_type` column |
| **Local performance** | No network latency |

### 4. Claude Interface (How I Access Atoms)

I don't query DuckDB directly. I use the `KnowledgeAtomService`:

```python
from architect_central_services.knowledge_service import get_knowledge_atom_service

service = get_knowledge_atom_service()

# Get context for a topic
atoms = service.get_context_for(topic="pipeline patterns", limit=10)

# Search by similarity
similar = service.search_similar(text="cost protection", limit=5)

# Write a new atom (from intake)
service.write_atom(
    content="Need to fix the logging import",
    atom_type="task",
    source_type="intake",
)
```

**The service abstracts:**
- DuckDB queries
- Embedding generation
- Type-specific views
- Temporal filtering (current vs historical)

### 5. BigQuery (Cloud Permanence)

BigQuery is NOT the retrieval layer. It's the **cloud permanence layer**.

| DuckDB (Local) | BigQuery (Cloud) |
|----------------|------------------|
| Fast queries | Permanent storage |
| Real-time access | Cross-system analytics |
| Working memory | Long-term memory |
| Claude reads/writes | Systems query for reports |

**Sync pattern:**
```
DuckDB → Periodic sync → BigQuery
         (hourly or on significant events)
```

---

## The Flow: How Truth Becomes Context

### Flow 1: Conversation → Atom → Context

```
Claude Code conversation
    │
    ▼
ClaudeCodeNormalizer (membrane)
    │
    ▼
atoms table (DuckDB)
    │
    ▼
KnowledgeAtomService.search_similar("topic")
    │
    ▼
Relevant atoms returned
    │
    ▼
Injected into Claude's context
```

### Flow 2: Intake → Atom → Persistence

```
Claude writes backlog item
    │
    ▼
echo '{"content": "Fix bug"}' >> backlog.jsonl
    │
    ▼
JSONLAdapter (membrane)
    │
    ▼
atoms table (DuckDB) with atom_type='task'
    │
    ▼
Sync to BigQuery (periodic)
    │
    ▼
Queryable across all systems
```

### Flow 3: Document → Atom → Knowledge

```
docs/product/THE_OPERATING_FRAMEWORK.md
    │
    ▼
DocumentAdapter (membrane)
    │
    ▼
atoms table with atom_type='concept', 'principle'
    │
    ▼
service.get_context_for("operating framework")
    │
    ▼
Claude understands the framework
```

---

## What "RAG" Actually Is Here

Traditional RAG:
```
Query → Search documents → Retrieve chunks → Inject into LLM → Generate
```

Knowledge Atom RAG:
```
Query → Search atoms (DuckDB) → Retrieve atoms → Inject into LLM → Generate
```

**The difference:** Atoms are pre-structured. They're not raw document chunks.

| Document Chunk | Knowledge Atom |
|----------------|----------------|
| Arbitrary slice of text | Semantic unit of truth |
| May cut mid-thought | Complete thought |
| Needs context | Self-contained |
| Generic embedding | Type-aware embedding |

**The Knowledge Atom System IS the RAG system.** There's no separate layer.

---

## What Needs to Be Built

### Already Exists

| Component | Location | Status |
|-----------|----------|--------|
| Normalizers | `truth/normalizers/` | ✅ Working |
| KnowledgeAtomService | `knowledge_service/` | ✅ Working |
| BigQuery tables | `knowledge_atoms.*` | ✅ 20,596 atoms |
| Adapters | `knowledge_service/adapters.py` | ✅ Working |

### Needs Building

| Component | Purpose | Priority |
|-----------|---------|----------|
| **DuckDB layer** | Local storage/query | HIGH |
| **JSONL → DuckDB sync** | Real-time intake | HIGH |
| **Embedding generation** | Vector similarity | MEDIUM |
| **BigQuery sync** | Cloud permanence | MEDIUM |
| **Temporal maintenance** | Mark stale atoms | MEDIUM |

---

## Summary

```
SOURCES → MEMBRANES → KNOWLEDGE ATOM SYSTEM → CLAUDE
                            (DuckDB)

- Sources generate truth (conversations, documents, events)
- Membranes normalize truth into atoms
- Knowledge Atom System stores AND retrieves (it IS the RAG layer)
- Claude queries through KnowledgeAtomService
- BigQuery provides cloud permanence (not retrieval)
```

**Key insight:** There is no separate "RAG system." The Knowledge Atom System IS the retrieval layer. DuckDB queries ARE retrieval. No additional infrastructure needed.

---

## References

- `docs/specifications/KNOWLEDGE_ATOM_SYSTEM_SPEC.md` - Detailed spec
- `docs/primitive/TRUTH_ENGINE_STANDARDS.md` - Standards
- `architect_central_services/src/.../truth/normalizers/` - Membranes
- `architect_central_services/src/.../knowledge_service/` - Service layer
