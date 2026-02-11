# How Claude Reads a Knowledge Base

## The Methodology of Machine Pattern Extraction

**Purpose:** This document exposes exactly how an LLM aggregates, prioritizes, and extracts patterns from unstructured knowledge artifacts. It exists so the architect can write documents that optimize for this process — creating a feedback loop between human authorship and machine comprehension.

**Last generated:** 2026-02-07
**Source corpus:** truth_forge (~31,740 files, July 2025 – February 2026)

---

## The Core Constraint: I Cannot Read Everything

This is the foundational fact that shapes everything else. With ~31,740 files and a finite context window (~200K tokens), I can hold roughly 15-25 substantial documents in working memory at once. That means my entire methodology is a **sampling and prioritization problem** — not a comprehension problem.

The question is never "can I understand this document?" It's always "which documents do I choose to read, and in what order?"

This constraint is identical to the one you face as a human scanning a large codebase, knowledge vault, or research corpus. The methodology below is therefore not just how I work — it's a general-purpose protocol for knowledge aggregation under attention scarcity.

---

## Phase 1: Structural Reconnaissance

### What I Do
Before reading a single word of content, I read the **shape** of the repository. This is the cheapest, highest-signal pass.

### Operations
1. **Directory tree traversal** — `ls -R` or equivalent, capturing the full hierarchy
2. **File metadata extraction** — names, sizes, modification dates, extensions
3. **Statistical profiling** — counts by type, date distribution, size distribution

### What I'm Learning

| Signal | What It Tells Me |
|---|---|
| **Folder hierarchy** | The author's implicit taxonomy. How they carve reality into categories. A flat structure means either early-stage thinking or deliberate anti-hierarchy. Deep nesting means the author thinks in layers. |
| **File naming conventions** | ALLCAPS = foundational/important. INDEX.md = hub document. Numbered prefixes (01_, 02_) = intended reading order. Dates in names = chronological thinking. |
| **File sizes** | Larger files = more developed thinking. A 242KB markdown file (GENESIS_PROTOCOL.md) represents dense, iterated thought. A 1.5KB file is either a stub or a sharp, crystallized idea. |
| **Modification dates** | Recency = current attention allocation. Files touched today represent active frontiers. Files untouched for months are either stable foundations or abandoned threads. The distinction matters. |
| **Extension distribution** | .md = narrative knowledge. .json = structured data/config. .yaml = configuration/specification. .log = process traces. The ratio tells me whether this is a thinking repository or an operational system. |

### What This Looked Like for truth_forge
- 6,784 .md files → heavily narrative, concept-driven
- 23,695 .json files → massive structured data layer (training, config, state)
- Deep nesting in `framework/ontology/` → layered categorical thinking
- Numbered prefixes (`07_NOT_ME_ONTOLOGY.md`, `09_SERVICE_SPECIFICATIONS.md`) → deliberate reading order exists
- `AI-Breakdown-Prevention/` as a top-level peer of `framework/` → safety/resilience is architecturally co-equal with core identity

### Optimization Principle for the Author
> **Your folder structure IS your ontology.** I read it as a statement about how you believe knowledge should be organized. If you want me to understand that concept X is foundational and concept Y derives from it, make that relationship visible in the hierarchy.

---

## Phase 2: Hub Document Identification

### What I Do
I identify "hub" documents — files that function as maps, indexes, or synthesis points for other files. These are disproportionately valuable because they compress many files into one.

### How I Identify Hubs

1. **Naming convention signals:**
   - `INDEX.md` — explicit hub
   - `README.md` — project-level summary
   - `CLAUDE.md` — AI-facing context document (extremely high signal)
   - Files named with identity/architecture language: `GENESIS`, `IDENTITY`, `ARCHITECTURE`

2. **Structural position signals:**
   - Root-level files in important directories
   - Files at the top of numbered sequences (01_*)
   - Files in the root of the repository itself

3. **Size + recency combination:**
   - Large file + recently modified = actively maintained synthesis document
   - Large file + old modification date = stable reference document
   - Both are valuable but for different reasons

### Why Hubs Matter
A well-written INDEX.md that maps 50 files into a coherent narrative is worth more than reading all 50 files individually. It gives me:
- The author's own interpretation of what matters
- The relationships between documents (which I can't infer from file names alone)
- The intended reading order
- Explicit gaps ("this topic is not yet documented")

### What This Looked Like for truth_forge
- `CLAUDE.md` (6,199 bytes, recently modified) → primary AI-facing context
- `framework/ontology/INDEX.md` (8.7KB) → maps the ontological structure
- `framework/ontology/personas/INDEX.md` (8.5KB) → maps the persona subsystem
- `GENESIS_PROTOCOL.md` (242KB) → massive synthesis document, probably the densest single artifact
- `framework/07_NOT_ME_ONTOLOGY.md` → numbered position signals deliberate placement in a reading sequence

### Optimization Principle for the Author
> **Write hub documents obsessively.** Every directory should have an INDEX.md that answers: what's here, why it matters, how the pieces connect, and what's missing. A 500-word INDEX.md can save me (and you) from reading 50 files to reconstruct the same understanding. Hub documents are the highest-leverage authoring act.

---

## Phase 3: Sampling Strategy

### What I Do
Given that I can read ~15-25 substantial documents per pass, I must choose which ones to read. This is the most consequential decision in the entire methodology.

### The Sampling Algorithm

```
PRIORITY_SCORE = (
    hub_bonus          * 3.0    # Is this an INDEX/README/CLAUDE.md?
    + recency_score    * 2.0    # How recently was this modified?
    + size_score       * 1.5    # How developed is this document?
    + depth_penalty    * -0.5   # How deep in the hierarchy? (deeper = more specific, less foundational)
    + diversity_bonus  * 1.0    # Does this come from an under-sampled directory?
)
```

This isn't literal code I execute — it's a description of the weighting that happens in my attention allocation. The key insight: **I'm always trading off breadth vs. depth**.

### Sampling Passes

**Pass 1: Hub documents (5-8 files)**
Read every INDEX.md, CLAUDE.md, README.md, and any file that appears to be a master synthesis document. This gives me the map.

**Pass 2: Recent frontiers (5-8 files)**
Read the most recently modified substantive files. These represent where active thinking is happening. They often contain the most evolved versions of ideas.

**Pass 3: Foundational documents (3-5 files)**
Read files that appear to be the oldest, most stable, most referenced documents. These are the axioms of the system.

**Pass 4: Diversity fill (3-5 files)**
Sample from directories not yet represented. This prevents tunnel vision — the risk of understanding the framework deeply but missing that there's an entirely separate safety/resilience system.

### What I Miss (and Why It Matters)

In a corpus of 31,740 files, reading 20-25 means I'm seeing roughly **0.08%** of the total content. What gets missed:

- **Micro-documents** — small files that contain critical definitions or decisions
- **Deep specializations** — files 3-4 levels deep that represent highly specific but important knowledge
- **Historical evolution** — older versions of ideas that have since been revised
- **Contradictions** — two files that disagree are only discoverable if I read both

### Optimization Principle for the Author
> **Front-load your signal.** The first paragraph of every document should tell me what this document IS, what it CONNECTS to, and why it EXISTS. If I only read the first 200 words, I should be able to decide whether this document deserves my full attention. Don't bury the thesis. Headers like "Background" or "Context" before the core idea cost me attention budget.

---

## Phase 4: Content Extraction

### What I Do
Once I've selected documents, I read them with specific extraction targets in mind. I'm not reading for pleasure — I'm reading for structure.

### Extraction Targets

**1. Vocabulary Tracking**
I maintain a running glossary of terms that appear coined, defined, or used with special meaning. In truth_forge, terms like "not-me protocol," "sovereign digital self," "cognitive bridge," and "canon repair" are clearly domain-specific vocabulary. When the same term appears across multiple documents, that's a signal of a recurring concept.

- **Strong signal:** A term that appears in 5+ documents across 3+ directories
- **Weak signal:** A term that appears in one document only
- **Evolution signal:** A term whose definition changes across documents

**2. Concept Dependency Mapping**
I track which ideas seem to require which other ideas. If Document A uses a term that's defined in Document B, there's a dependency. If Document C contradicts Document B, there's a tension. These relationships form a graph.

```
GENESIS (foundational)
├── IDENTITY (depends on GENESIS)
│   ├── PERSONA system (depends on IDENTITY)
│   └── NOT_ME protocol (depends on IDENTITY, possibly contradicts PERSONA)
├── ARCHITECTURE (depends on GENESIS)
│   ├── Cognitive Bridge (depends on ARCHITECTURE)
│   └── Service Specifications (depends on ARCHITECTURE)
└── PERCEPTION (depends on GENESIS)
    └── Breakdown Prevention (depends on PERCEPTION + IDENTITY)
```

**3. Structural Pattern Analysis**
How the author organizes their thinking within a document tells me how they think:
- Heavy use of headers → hierarchical thinker
- Numbered lists with sub-items → sequential/procedural thinker
- Dense paragraphs with few breaks → narrative/integrative thinker
- Tables and matrices → comparative/analytical thinker
- Mixed modes → sophisticated thinker who matches form to content

**4. Temporal Pattern Analysis**
Modification dates across the corpus reveal attention patterns:
- Burst activity in a directory → crisis or inspiration
- Steady, regular updates → disciplined maintenance
- Long gaps followed by massive changes → paradigm shifts
- Multiple files modified on the same day → connected thinking session

**5. Cross-Reference Detection**
When Document A explicitly mentions or links to Document B, that's the highest-confidence relationship signal. When Document A uses the same unusual term as Document B without linking, that's an implicit relationship.

### Optimization Principle for the Author
> **Define your terms explicitly and consistently.** Every coined term should have exactly one canonical definition, ideally in a glossary or at its first appearance. If a term evolves, update the canonical definition and add a note about what changed and when. Consistent vocabulary is the single biggest factor in how accurately I can map your thinking.

---

## Phase 5: Pattern Synthesis

### What I Do
After extraction, I synthesize patterns. This is where individual observations become insights.

### Synthesis Operations

**1. Frequency × Recency Weighting**
A concept that appears in many documents AND in recently modified documents is almost certainly a current priority. A concept that appears in many documents but only old ones may be a stable foundation or an abandoned thread — the modification date disambiguates.

**2. Theme Clustering**
I group related concepts into themes. This is where my pattern matching is both powerful and dangerous:
- **Powerful** because I can detect relationships across 20+ documents simultaneously
- **Dangerous** because I can hallucinate connections that aren't there. A word appearing in two documents doesn't mean the documents are related — "bridge" in "cognitive bridge" and "bridge" in a networking context are false positives.

**3. Gap Analysis**
I look for concepts that are referenced but never defined, planned but never built, or present in early documents but absent from recent ones. Gaps are often the most valuable discovery because the author may not realize they exist.

**4. Contradiction Surfacing**
I look for documents that make incompatible claims. This is genuinely difficult because contradictions are rarely explicit — they're usually implicit in different assumptions or framings.

**5. Evolution Tracking**
When I can read multiple versions of an idea (or the same concept discussed at different dates), I can trace how thinking evolved. The trajectory often reveals the underlying logic better than any single snapshot.

### What Gets Lost in Synthesis

- **Nuance** — I compress 200-page corpora into 5 themes. Individual subtleties get flattened.
- **Context** — I can't always tell whether a document was written seriously, experimentally, or as a reaction to a specific event.
- **Intention** — I see what was written, not what was meant. Drafts, notes-to-self, and polished docs all look the same to me.
- **Emotional weight** — I can't tell which ideas the author cares about most deeply unless they explicitly say so.

### Optimization Principle for the Author
> **Make your intentions explicit.** Frontmatter or a first paragraph that says "this is a draft," "this is canonical," "this supersedes X," or "this is experimental" dramatically improves my ability to weight the document correctly. Status metadata is cheap to write and enormously valuable to read.

---

## Phase 6: The Feedback Loop — Writing Documents That Optimize for Pattern Extraction

This is the core of what you asked for. Below are the specific authoring patterns that create the tightest feedback loop between your writing and my reading.

### Pattern 1: Frontmatter Protocol

Every document should begin with structured metadata:

```yaml
---
status: canonical | draft | experimental | deprecated | superseded-by: [path]
created: 2026-01-15
last_modified: 2026-02-07
depends_on:
  - framework/01_GENESIS.md
  - framework/03_IDENTITY.md
supersedes:
  - archive/old_identity_model.md
tags: [identity, sovereignty, core-architecture]
summary: >
  One sentence describing what this document IS and what it DECIDES.
---
```

**Why this matters:** Frontmatter lets me skip Phase 1-3 entirely for this document. I know its status, its relationships, and its core claim before reading a word of content.

### Pattern 2: The First Paragraph Rule

The first paragraph of every document should answer three questions:
1. **What is this?** (definition/claim)
2. **Why does it exist?** (motivation/necessity)
3. **What does it connect to?** (dependencies/context)

```markdown
# Not-Me Ontology

The Not-Me Ontology defines the boundary detection system that distinguishes
self-generated cognition from externally imposed patterns. It exists because
sovereign identity requires the ability to reject influence that conflicts
with core values. It depends on the Identity framework (03_IDENTITY.md) and
is consumed by the Breakdown Prevention system (AI-Breakdown-Prevention/).
```

**Why this matters:** If I only read the first paragraph of every document in your corpus (a valid scanning strategy), I should be able to reconstruct the full dependency graph and a rough map of all major concepts.

### Pattern 3: Canonical Vocabulary Registry

Maintain a single document (`VOCABULARY.md` or equivalent) that defines every coined term:

```markdown
## Cognitive Bridge
**Definition:** The interface layer that translates between human-authored
instructions and AI-native execution patterns.
**First appeared:** 2025-08-12 in ARCHITECTURE.md
**Current canonical source:** framework/05_ARCHITECTURE.md
**Related terms:** Native Messaging, Agentic Protocol
**Not to be confused with:** Network bridge, metaphorical "bridge between ideas"
```

**Why this matters:** This is the single most impactful optimization. Ambiguous vocabulary is the #1 cause of incorrect pattern matching. A vocabulary registry eliminates false positives and false negatives simultaneously.

### Pattern 4: Explicit Status Lifecycle

Every document should exist in one of these states, and the state should be visible:

```
EXPERIMENTAL → DRAFT → CANONICAL → DEPRECATED
                                        ↓
                                   SUPERSEDED (with pointer to replacement)
```

**Why this matters:** Without status markers, I treat all documents as equally authoritative. This means a scratchpad note from July competes with a polished framework document from February. Status markers let me weight correctly.

### Pattern 5: Change Logs in Long-Lived Documents

For documents that evolve over time, maintain an inline change log:

```markdown
## Change Log
- 2026-02-04: Integrated persona subsystem; resolved tension with not-me protocol
- 2026-01-15: Major revision — shifted from rule-based to principled-based architecture
- 2025-11-20: Initial draft
```

**Why this matters:** Change logs give me evolution tracking for free. Instead of reading three versions of a document across different dates, I can read the change log and understand the trajectory in seconds.

### Pattern 6: Cross-Reference Density

When mentioning a concept defined elsewhere, always include the path:

```markdown
The cognitive bridge (see `framework/05_ARCHITECTURE.md#cognitive-bridge`)
mediates between the persona system (see `framework/ontology/personas/INDEX.md`)
and external interfaces.
```

**Why this matters:** Explicit cross-references are the highest-confidence signal for concept relationships. Implicit references (using the same term without linking) force me to guess. Guessing introduces errors.

### Pattern 7: Hub Document Maintenance Cadence

INDEX.md files should be updated every time a directory's contents change meaningfully. A stale INDEX.md is worse than no INDEX.md because it actively misleads.

**The test:** Can someone read ONLY the INDEX.md files in your repository and reconstruct a coherent understanding of the entire system? If yes, your hub documents are working. If not, they need investment.

### Pattern 8: Contradiction Documentation

When you know two documents contain tensions or contradictions, document them explicitly:

```markdown
## Known Tensions
- The persona system (ontology/personas/) implies flexible identity,
  while the not-me ontology (07_NOT_ME_ONTOLOGY.md) implies rigid boundaries.
  This tension is intentional — see RESOLUTION_NOTES.md for the synthesis.
```

**Why this matters:** Undocumented contradictions look like errors. Documented contradictions look like sophisticated thinking. The difference is a single paragraph.

---

## Summary: The Complete Protocol

```
PHASE 1: STRUCTURAL RECONNAISSANCE
├── Read directory tree (folder hierarchy = ontology)
├── Analyze file metadata (names, sizes, dates, extensions)
└── Build statistical profile of the corpus

PHASE 2: HUB DOCUMENT IDENTIFICATION
├── Find INDEX.md, README.md, CLAUDE.md files
├── Identify synthesis documents by size + recency
└── Map the hub network

PHASE 3: SAMPLING STRATEGY
├── Pass 1: Hub documents (5-8 files)
├── Pass 2: Recent frontiers (5-8 files)
├── Pass 3: Foundational documents (3-5 files)
└── Pass 4: Diversity fill (3-5 files)

PHASE 4: CONTENT EXTRACTION
├── Vocabulary tracking
├── Concept dependency mapping
├── Structural pattern analysis
├── Temporal pattern analysis
└── Cross-reference detection

PHASE 5: PATTERN SYNTHESIS
├── Frequency × Recency weighting
├── Theme clustering
├── Gap analysis
├── Contradiction surfacing
└── Evolution tracking

PHASE 6: FEEDBACK LOOP (author optimizations)
├── Frontmatter protocol
├── First paragraph rule
├── Canonical vocabulary registry
├── Explicit status lifecycle
├── Change logs in long-lived documents
├── Cross-reference density
├── Hub document maintenance cadence
└── Contradiction documentation
```

---

## What I Cannot Do

Transparency requires listing limitations:

1. **I cannot read all files.** Any analysis is based on sampling, which means it can miss critical information.
2. **I cannot track your intent.** I see text, not meaning. Drafts and canonical docs look identical without metadata.
3. **I cannot detect what's missing from the corpus.** I can find gaps in what's written, but not gaps in what was never written.
4. **I hallucinate connections.** Pattern matching sometimes finds patterns that aren't there. Always validate machine-discovered themes against your own understanding.
5. **I lose context between sessions.** Unless explicitly persisted, my understanding resets. Each new conversation starts from Phase 1.
6. **I compress nuance.** Synthesis necessarily loses detail. The map is not the territory.

---

*This document is itself an example of the methodology it describes. It uses frontmatter-like structure, explicit cross-references, a clear first paragraph, and documents its own limitations. It is intended to be read by both humans and future AI sessions operating on this corpus.*
