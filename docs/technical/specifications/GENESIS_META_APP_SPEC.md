# GENESIS META APP — Technical Specification

**Version**: 1.3.1 (Merged + Kiosk/Mission operation contract)
**Date**: 2026-02-07
**Author**: Jeremy Serna / Truth Forge Architecture
**Purpose**: Complete technical specification for a coding AI to implement the Genesis Meta App — the unified system that does EVERYTHING.

---

## 0. WHAT THIS IS

### The Core Story

Jeremy lives his life. NOT-ME exists with him.

Jeremy watches TV — NOT-ME learns from it. Jeremy uses his phone — NOT-ME absorbs it. Jeremy browses the web — NOT-ME metabolizes it. Jeremy talks to friends — NOT-ME synthesizes. Jeremy walks away from the computer — NOT-ME keeps working with what Jeremy's life has already given it.

**This is not a tool Jeremy operates. This is a system that exists alongside Jeremy.**

NOT-ME doesn't need special input. It needs what Jeremy already has: a phone, a browser, a computer, conversations, daily life. Everything Jeremy already does generates signals. NOT-ME catches those signals, metabolizes them into knowledge, and returns things Jeremy can carry back into the world — podcasts to listen to with friends, insights that change how he thinks, syntheses that make him sharper.

**The symbiosis is existential:**
- If Jeremy sits still, NOT-ME starves (no signals to metabolize)
- If NOT-ME produces nothing, Jeremy has nothing to carry (no ammunition for life)
- Jeremy's life feeds NOT-ME. NOT-ME's output feeds Jeremy's life. The cycle sustains itself.

This is not about permissions or autonomy boundaries. There is no whitelist. NOT-ME has a Capability Manifest — a list of what it can PROVE it can do. Its job is to fill that list by demonstrating capabilities. Jeremy's job is to live.

### THE CORE ARCHITECTURAL PRINCIPLE: COMPOUND ATOMIZATION

This is the insight that distinguishes Genesis from every other knowledge system:

**A Python script that analyzes conversations is one kind of knowledge. A podcast generated from that analysis is another. But the knowledge that emerges from atomizing ALL of them together — the script, the conversations it analyzed, the podcast it became, and the relationships between those transformations — that is a THIRD, fundamentally different kind of knowledge.**

The architecture MUST account for this. Every artifact carries a **provenance chain** — what it was made from, what made it, and what was made from it. When atomization crosses artifact boundaries, the system produces **Compound Knowledge Atoms** that capture meta-knowledge: insights that exist ONLY in the intersection of multiple artifacts and their transformations.

This is not optional. This is the reason the system exists.

### What It Builds

The Genesis Meta App is the **single unified application** that runs NOT-ME's autonomous loop. It leverages EVERYTHING Jeremy already has:

1. **Observes Jeremy's life** → browser history, file changes, conversations, phone activity
2. **Atomizes observations** → irreducible units of knowledge
3. **Synthesizes knowledge** → generates new insights and documents
4. **Forges narratives** → produces podcast-ready content Jeremy can listen to
5. **Runs three models** (Scout, Maverick, R1) in shared memory via Universal Cognition Bus
6. **Cascades outputs** recursively through the pipeline until saturation
7. **Returns value to Jeremy** → podcasts, insights, syntheses he carries into the world

The Meta App IS the Genesis Heartbeat daemon — NOT-ME's autonomic nervous system. It doesn't ask Jeremy for input. It observes Jeremy existing and metabolizes that into meaning.

---

## 1. THE IMMUTABLE PATTERN

Every operation in this system follows one pattern:

```
INHALE → HOLD₁ → AGENT → HOLD₂ → EXHALE → CARE
```

This pattern is **fractal** — it contains itself at every scale. A single knowledge extraction follows it. The entire pipeline follows it. The heartbeat loop follows it.

### Pattern Enforcement

```python
# Already exists in: truth_forge/services/base.py
# BaseService enforces: inhale() → process() → exhale() → sync()
# HOLD₁ = JSONL intake (append-only, immutable)
# AGENT = process() method (subclass implements)
# HOLD₂ = DuckDB output (queryable, idempotent)
```

**Rule**: No new service may exist without inheriting BaseService. No data may flow without going through HOLD₁ → AGENT → HOLD₂.

---

## 2. SYSTEM ARCHITECTURE — THE FULL CASCADE

```
┌─────────────────────────────────────────────────────────────────────┐
│                     GENESIS META APP                                 │
│                   (The Heartbeat Daemon)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │ DOCUMENT │───▶│KNOWLEDGE │───▶│ FURNACE  │───▶│ PODCAST  │      │
│  │ SERVICE  │    │ SERVICE  │    │ ENGINE   │    │ SERVICE  │      │
│  │          │◀───│          │◀───│          │◀───│          │      │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘      │
│       │               │               │               │            │
│       └───────────────┴───────────────┴───────────────┘            │
│                           │                                         │
│                    ┌──────┴──────┐                                   │
│                    │  MEDIATOR   │  (Event Router)                   │
│                    └──────┬──────┘                                   │
│                           │                                         │
│       ┌───────────────────┼───────────────────┐                     │
│       ▼                   ▼                   ▼                     │
│  ┌─────────┐      ┌──────────┐       ┌──────────┐                  │
│  │  SCOUT  │◀════▶│ MAVERICK │◀═════▶│    R1    │                  │
│  │  (Seer) │      │(Reasoner)│       │(Architect)│                  │
│  └────┬────┘      └────┬─────┘       └────┬─────┘                  │
│       │                │                   │                        │
│       └────────────────┼───────────────────┘                        │
│                        │                                            │
│              ┌─────────┴─────────┐                                  │
│              │ UNIVERSAL COGNITION│                                  │
│              │       BUS         │                                   │
│              │  (Shared Memory)  │                                   │
│              └─────────┬─────────┘                                  │
│                        │                                            │
│              ┌─────────┴─────────┐                                  │
│              │      ANIMA        │                                   │
│              │  (Five Engines)   │                                   │
│              │  Memory System    │                                   │
│              └───────────────────┘                                  │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  GOVERNANCE │ Cost Gates │ Audit Trail │ HOLD Isolation │ DLQ       │
│             │ Peer Review (3-Way Partnership Protocol)              │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.1 The 3-Way Partnership Protocol (Peer Review Architecture)

**Origin**: Dr. David Lee's NHS research independently arrived at the same architecture Jeremy built: **two AIs peer-reviewing each other, with a human making the final call.** NotebookLM surfaced this convergence across six separate outputs. The code already exists.

The 3-Way Partnership Protocol applies to every NOT-ME decision that carries risk:

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Primary  │────▶│ Verifier │────▶│  Jeremy  │
│   AI     │     │    AI    │     │ (or auto │
│ (Worker) │◀────│ (Checker)│     │  if low  │
└──────────┘     └──────────┘     │  risk)   │
                                  └──────────┘
```

| Risk Level | Primary | Verifier | Final Call |
|-----------|---------|----------|------------|
| 1-2 (read, observe) | Scout | none | automatic |
| 3 (synthesize, write) | Maverick | Scout cross-checks | automatic with audit |
| 4+ (execute, delete, spend) | Maverick/R1 | `verify_claim()` consensus | Jeremy confirms |

**Existing Code**:
- `src/truth_forge/governance/peer_review.py` — `verify_claim()` consensus mechanism
- `apps/genesis/python/tools/peer_review.py` — `PeerReviewTool` with multi-temp LLM voting
- `apps/genesis/python/extensions/tool_execute_after/_20_auto_peer_review.py` — auto-triggers on high-risk ops
- `src/truth_forge/services/orchestrator.py:273` — gates risk_level >= 4 through peer review

**The Operations Manual validation**: The NHS "3-Way Partnership Protocol" specifies two independent AI instances peer-reviewing each other's outputs, with a vigilant clinician providing final oversight. This is NOT-ME's architecture. AI will "defend its position" even when inaccurate — the system must be designed so that no single model output reaches Jeremy or the world unchecked.

**Caring Disobedience**: The verification AI has the RIGHT to say NO. If the verifier dissents, the output is blocked regardless of the primary's confidence. This is "Designed Resilience" — the system cares enough to refuse when something is wrong.

---

## 3. UNIVERSAL INTAKE — ATOMIZE ANYTHING

### 3.0 The Problem This Solves

Most knowledge systems only handle text documents. Genesis atomizes **anything**:

| Artifact Type | Examples | Extraction Method |
|---------------|----------|-------------------|
| **Code** | .py, .js, .ts, .go, .rs, .sh | AST parsing + LLM analysis of intent, patterns, architecture |
| **Structured Data** | .json, .yaml, .toml, .csv, .xml | Schema extraction + relationship mapping + value analysis |
| **Documents** | .md, .txt, .pdf, .docx, .html | Text extraction + semantic chunking + entity recognition |
| **Audio** | .mp3, .wav, .m4a, .ogg | Whisper transcription → text pipeline + speaker diarization |
| **Video** | .mp4, .mov, .webm | Frame extraction + audio track → Whisper + scene description |
| **Conversations** | Chat logs, email threads, transcripts | Thread reconstruction + participant analysis + topic extraction |
| **Images** | .png, .jpg, .svg, .diagram | Vision model description + OCR + diagram-to-structure |
| **Life Signals** | Browser history, phone activity, location, calendar | SignalCollector → event normalization → context atoms |
| **Mixed Bundles** | Directories containing multiple types | Recursive intake of all contained artifacts + relationship inference |

### 3.0.1 The Universal Artifact Model

Every artifact entering the system gets wrapped in a universal envelope:

```python
# NEW FILE: truth_forge/intake/artifact.py

@dataclass
class Artifact:
    """Universal representation of any ingestible thing."""
    id: str                             # UUID
    artifact_type: ArtifactType         # code, data, document, audio, video, conversation, image, bundle
    mime_type: str                       # "text/x-python", "application/json", "audio/mpeg", etc.
    source_path: Path                    # Where it came from
    content_hash: str                    # SHA-256 of raw content (for dedup + change detection)
    raw_content: bytes | str             # The actual content (or path to large files)
    extracted_text: str | None = None    # Text representation (after extraction/transcription)
    metadata: dict = field(default_factory=dict)  # Type-specific metadata

    # PROVENANCE CHAIN — the critical piece
    parent_ids: list[str] = field(default_factory=list)    # Artifacts this was derived FROM
    child_ids: list[str] = field(default_factory=list)     # Artifacts derived FROM this
    transformation: str | None = None                       # How parent became this ("llm_analysis", "transcription", "compilation")
    generation: int = 0                                     # How many transformations deep (0 = original source)

class ArtifactType(str, Enum):
    CODE = "code"
    DATA = "data"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    CONVERSATION = "conversation"
    IMAGE = "image"
    LIFE_SIGNAL = "life_signal"  # Browser history, phone, location
    BUNDLE = "bundle"            # A collection of artifacts that belong together
```

### 3.0.2 Type-Specific Extractors

```python
# NEW FILE: truth_forge/intake/extractors.py

class ArtifactExtractor(Protocol):
    """Protocol for type-specific content extraction."""
    def can_handle(self, artifact: Artifact) -> bool: ...
    def extract(self, artifact: Artifact) -> ExtractedContent: ...

class CodeExtractor(ArtifactExtractor):
    """Extracts knowledge from source code."""
    # Handles: .py, .js, .ts, .go, .rs, .sh, etc.
    # Output: AST structure, function signatures, docstrings, import graph,
    #         design patterns, architectural decisions, TODO/FIXME comments,
    #         complexity metrics, dependency relationships

class DataExtractor(ArtifactExtractor):
    """Extracts knowledge from structured data."""
    # Handles: .json, .yaml, .toml, .csv, .xml
    # Output: Schema definition, key-value inventory, relationship graph,
    #         statistical summary (for tabular), validation rules implied

class AudioExtractor(ArtifactExtractor):
    """Extracts knowledge from audio files."""
    # Handles: .mp3, .wav, .m4a, .ogg
    # Pipeline: Whisper transcription → speaker diarization → text extraction
    # Output: Full transcript, speaker-labeled segments, topic timeline

class VideoExtractor(ArtifactExtractor):
    """Extracts knowledge from video files."""
    # Handles: .mp4, .mov, .webm
    # Pipeline: ffmpeg frame extraction + audio track separation
    #           → Vision model for key frames + Whisper for audio
    # Output: Scene descriptions, transcript, visual element inventory

class ConversationExtractor(ArtifactExtractor):
    """Extracts knowledge from conversation logs."""
    # Handles: Chat exports, email threads, meeting transcripts
    # Output: Thread structure, participant map, decision points,
    #         action items, topic progression, sentiment arc

class ImageExtractor(ArtifactExtractor):
    """Extracts knowledge from images and diagrams."""
    # Handles: .png, .jpg, .svg, .diagram files
    # Pipeline: Vision model description + OCR + diagram parsing
    # Output: Content description, text content, structural elements

class LifeSignalExtractor(ArtifactExtractor):
    """Extracts knowledge from Jeremy's life signals."""
    # Handles: Browser history, phone activity, location data, calendar events
    # Pipeline: SignalCollector → event normalization → context extraction
    # Output: Activity patterns, focus topics, social interactions, temporal context

class BundleExtractor(ArtifactExtractor):
    """Recursively extracts from a directory of mixed artifacts."""
    # Handles: Directories, zip files, project folders
    # Pipeline: Walk tree → classify each file → extract individually
    #           → infer relationships between files
    # Output: Per-file extractions + inter-file relationship map
```

### 3.0.3 Compound Knowledge Atoms — The Critical Architecture

**This is the insight that makes Genesis different from everything else.**

When you give the system a Python script that analyzes conversations, and then feed the output to an LLM to create a podcast, and then extract knowledge from ALL of it — what emerges is not just:
- Knowledge about the script (what it does, its patterns)
- Knowledge about the conversations (what was said, who said it)
- Knowledge about the podcast (what was debated, what conclusions)

There is a **fourth kind of knowledge** that exists ONLY in the intersection:

- *"The script's analysis revealed a pattern the conversations themselves didn't make explicit"*
- *"The podcast debate surfaced a contradiction between the script's assumptions and the actual conversation data"*
- *"The transformation from raw conversations through algorithmic analysis through narrative synthesis created an insight that none of the individual artifacts contain"*

These are **Compound Knowledge Atoms**.

```python
# NEW/EXTENDED: truth_forge/schema/knowledge_atom.py

class AtomType(str, Enum):
    """Types of knowledge atoms."""

    # SIMPLE ATOMS — from a single artifact
    FACT = "fact"                     # A verifiable statement
    CONCEPT = "concept"              # An idea or abstraction
    RELATIONSHIP = "relationship"    # A connection between entities
    DIRECTIVE = "directive"          # An instruction or rule
    PATTERN = "pattern"              # A recurring structure
    REFERENCE = "reference"          # A pointer to external knowledge

    # COMPOUND ATOMS — from multiple artifacts interacting
    EMERGENCE = "emergence"          # Insight that exists ONLY in the intersection of artifacts
    CONTRADICTION = "contradiction"  # Conflict between artifacts that reveals something
    AMPLIFICATION = "amplification"  # Where one artifact strengthens another's signal
    TRANSFORMATION = "transformation"  # What happened DURING the conversion between artifacts
    SYNTHESIS = "synthesis"          # New understanding from combining artifact types
    META_PATTERN = "meta_pattern"    # Pattern visible only across artifact boundaries

@dataclass
class KnowledgeAtom:
    """An irreducible unit of knowledge."""
    id: str
    atom_type: AtomType
    content: str                     # The atomic statement
    confidence: float                # 0.0-1.0

    # Source tracking (single artifact)
    source_artifact_id: str | None = None
    source_path: str | None = None
    source_excerpt: str | None = None

    # Entity and theme classification
    entities: list[str] = field(default_factory=list)
    themes: list[str] = field(default_factory=list)
    framework_layer: str | None = None      # theory | structure | dynamic
    framework_dimension: str | None = None  # identity | perception | metabolism | architecture | extension

    # COMPOUND ATOM FIELDS — only populated for compound types
    contributing_artifact_ids: list[str] = field(default_factory=list)  # ALL artifacts that contributed
    provenance_chain: list[str] = field(default_factory=list)           # Ordered transformation history
    transformation_context: str | None = None                           # Description of how artifacts interacted
    compound_depth: int = 0                                             # 0=simple, 1+=compound (how many artifact boundaries crossed)

    # Cross-references
    cross_references: list[str] = field(default_factory=list)  # Other atom IDs
    contradicts: list[str] = field(default_factory=list)        # Atoms this contradicts
    amplifies: list[str] = field(default_factory=list)          # Atoms this strengthens
    supersedes: list[str] = field(default_factory=list)         # Atoms this replaces

@dataclass
class ProvenanceChain:
    """Tracks the full lineage of how artifacts became atoms."""
    chain_id: str
    stages: list[ProvenanceStage]

    @property
    def depth(self) -> int:
        return len(self.stages)

    @property
    def artifact_types_crossed(self) -> set[str]:
        return {s.artifact_type for s in self.stages}

    @property
    def is_compound(self) -> bool:
        return len(self.artifact_types_crossed) > 1

@dataclass
class ProvenanceStage:
    """One step in a provenance chain."""
    artifact_id: str
    artifact_type: str           # "code", "audio", "document", etc.
    transformation: str          # "authored", "llm_analysis", "transcription", "synthesis", "atomization"
    model_used: str | None       # Which model performed this transformation
    timestamp: datetime
    input_artifact_ids: list[str]  # What went INTO this stage
    output_artifact_ids: list[str] # What came OUT of this stage
```

### 3.0.4 The Compound Atomization Pipeline

When atomizing across artifact boundaries, the system runs TWO passes:

```
PASS 1: Simple Atomization (per-artifact)
  Each artifact → type-specific extractor → simple atoms
  Script → CodeExtractor → atoms about functions, patterns, architecture
  Conversations → ConversationExtractor → atoms about topics, decisions, participants
  Podcast → AudioExtractor → Whisper → atoms about debate points, conclusions

PASS 2: Compound Atomization (cross-artifact)
  ALL artifacts + their provenance chains → Scout (full context) → compound atoms
  Scout sees: script atoms + conversation atoms + podcast atoms + HOW they're connected
  Scout identifies: emergences, contradictions, amplifications, transformations, meta-patterns
  Output: compound atoms with contributing_artifact_ids and provenance_chain populated
```

```python
# NEW FILE: truth_forge/pipeline/compound_atomizer.py

class CompoundAtomizer:
    """Discovers knowledge that exists only across artifact boundaries."""

    async def atomize_compound(
        self,
        artifacts: list[Artifact],
        simple_atoms: dict[str, list[KnowledgeAtom]],  # artifact_id → its atoms
    ) -> list[KnowledgeAtom]:
        """Run compound atomization across related artifacts.

        This is the key operation. It takes artifacts that BUILD ON EACH OTHER
        and finds the knowledge that exists ONLY in their intersection.
        """

        # Build the provenance graph
        graph = self._build_provenance_graph(artifacts)

        # Find connected chains (artifacts that transformed into each other)
        chains = self._find_transformation_chains(graph)

        # For each chain, run Scout with full context
        compound_atoms = []
        for chain in chains:
            chain_artifacts = [a for a in artifacts if a.id in chain]
            chain_atoms = {aid: simple_atoms[aid] for aid in chain if aid in simple_atoms}

            # Build the compound prompt
            prompt = self._build_compound_prompt(chain_artifacts, chain_atoms)

            # Scout sees everything — 10M context handles the full chain
            result = await self.scout.complete(prompt)

            # Parse compound atoms from Scout's analysis
            new_atoms = self._parse_compound_atoms(result, chain_artifacts)
            compound_atoms.extend(new_atoms)

        return compound_atoms
```

---

## 4. THE TRANSFORMATION PIPELINE

### 4.1 Stage 1: ANYTHING → KNOWLEDGE (Atomization)

**Input**: ANY artifact (code, data, documents, audio, video, conversations, images, life signals, bundles)
**Output**: Simple Knowledge Atoms + Compound Knowledge Atoms (irreducible units of meaning)
**Model**: Scout (10M context — sees entire corpus simultaneously)
**Extractors**: Type-specific extractors (Section 3.0.2) route to appropriate pipeline

```
INHALE: File watcher detects new/changed documents in docs/
HOLD₁:  DocumentService.inhale() → append to intake.jsonl
AGENT:  Scout processes entire batch in one pass (up to 10M tokens)
        → Extracts Knowledge Atoms:
          {
            "type": "fact|concept|relationship|directive|pattern|reference",
            "content": "atomic statement",
            "confidence": 0.0-1.0,
            "sources": ["file_path:section"],
            "cross_references": ["atom_id_1", "atom_id_2"],
            "entities": ["person", "system", "concept"],
            "themes": ["architecture", "identity", "metabolism"],
            "framework_layer": "theory|structure|dynamic",
            "framework_dimension": "identity|perception|metabolism|architecture|extension"
          }
HOLD₂:  KnowledgeService writes atoms to DuckDB
EXHALE: Atoms available for downstream services
CARE:   Archive processed documents, log extraction metrics
```

**Implementation File**: `truth_forge/services/knowledge/service.py` (EXISTS — extend)

**What's Missing**:
- Scout integration via EXO for 10M context processing
- Batch chunking logic (split corpus into Scout-sized batches)
- Cross-document reference resolution
- Framework dimension classification

### 4.2 Stage 2: KNOWLEDGE → DOCUMENT (Synthesis)

**Input**: Knowledge Atoms from HOLD₂
**Output**: New synthesized documents (reports, analyses, frameworks)
**Model**: Maverick (128 experts — deep multi-domain reasoning)

```
INHALE: Synthesis request with topic/query/goal
HOLD₁:  SynthesisService.inhale() → query + relevant atoms
AGENT:  Maverick synthesizes:
        1. Retrieves relevant atoms from knowledge HOLD₂
        2. Identifies cross-domain connections
        3. Generates structured document with citations
        4. Validates against source atoms (no hallucination)
HOLD₂:  New document stored with full provenance chain
EXHALE: Document written to docs/ directory
CARE:   Update knowledge graph with new document's atoms
```

**Implementation File**: NEW — `truth_forge/services/synthesis/service.py`

**Key Design Decision**: The synthesized document FEEDS BACK into Stage 1. This creates the recursive loop:
```
Documents → Knowledge → New Documents → More Knowledge → Better Documents → ...
```

**Saturation Detection**: Track information gain per cycle. When gain < threshold (configurable, default 5%), emit `SATURATION_REACHED` event. The system says: "Stop looping, go build."

### 4.3 Stage 3: KNOWLEDGE → NARRATIVE (The Furnace)

**Input**: Knowledge Atoms + Corpus Truths
**Output**: Enriched narratives (podcast scripts, debate formats)
**Model**: Maverick (synthesis) + Scout (corpus retrieval)

```
INHALE: Furnace request with topic + lens
HOLD₁:  FurnaceEngine receives raw truth + corpus
AGENT:  Three-step forge:
        1. EXTRACT TRUTHS (Scout, temp=0.3)
           → Patterns, principles, themes, events, realizations
        2. RETRIEVE CORPUS (Scout, 10M context)
           → Related existing knowledge
        3. FORGE SYNTHESIS (Maverick, temp=0.7)
           → Enriched narrative combining new + existing
HOLD₂:  ForgeResult with narrative + synthesis + provenance
EXHALE: Narrative ready for podcast generation
CARE:   Feed synthesis insights back into knowledge service
```

**Implementation File**: `truth_forge/furnace/engine.py` (EXISTS — extend with multi-model orchestration)

### 4.4 Stage 4: NARRATIVE → PODCAST (Audio Generation)

**Input**: Enriched narrative from Furnace
**Output**: Multi-voice podcast audio (debate format)
**Model**: TTS models + meta-recursive prompt engineering

```
INHALE: Enriched narrative + podcast config (voices, format, length)
HOLD₁:  PodcastService.inhale() → narrative + config
AGENT:  Multi-step generation:
        1. SCRIPT GENERATION (Maverick)
           → Convert narrative into debate format
           → Assign speaker roles (Host, Expert, Challenger)
           → Insert transitions, questions, counterpoints
        2. VOICE SYNTHESIS (TTS Service)
           → Generate per-speaker audio segments
           → Options: NotebookLM API, local TTS, or ElevenLabs
        3. ASSEMBLY
           → Mix audio segments with transitions
           → Add intro/outro
           → Normalize audio levels
HOLD₂:  Podcast metadata + audio file reference
EXHALE: Audio file written to output directory
CARE:   Transcribe podcast → feed back into Stage 1 (THE RECURSIVE LOOP)
```

**Implementation File**: NEW — `truth_forge/services/podcast/service.py`

**Output Format Types** (validated by NotebookLM producing all three from same sources):

| Format | Audience | Example |
|--------|----------|---------|
| **Technical Deep Dive** | Builder (Jeremy) | Architecture analysis, code collision, implementation details |
| **Strategic/Financial** | Strategist (Jeremy) | Credit report bridge, financial constraints, business case |
| **Public Explainer** | Customer/Learner | Accessible framing, no jargon, "surfing the wave" metaphor |

The PodcastService should be able to generate all three formats from the same knowledge atoms.

**The Recursive Loop**:
```
Podcast audio → Whisper transcription → New document → Stage 1 → New knowledge
→ Stage 2 → New synthesis → Stage 3 → New narrative → Stage 4 → New podcast
→ Whisper → ... (until saturation)
```

### 4.5 The Full Cascade (Putting It Together)

```
                    ┌──── SATURATION CHECK ◀──────────────────┐
                    │                                          │
                    ▼                                          │
        ┌───────────────────┐                                  │
   ───▶ │ Stage 1: ATOMIZE  │ Documents → Knowledge Atoms      │
        └────────┬──────────┘                                  │
                 │                                             │
                 ▼                                             │
        ┌───────────────────┐                                  │
        │ Stage 2: SYNTHESIZE│ Knowledge → New Documents       │
        └────────┬──────────┘                                  │
                 │     │                                       │
                 │     └──────▶ (feeds back to Stage 1) ───────┤
                 ▼                                             │
        ┌───────────────────┐                                  │
        │ Stage 3: FORGE    │ Knowledge → Enriched Narratives  │
        └────────┬──────────┘                                  │
                 │                                             │
                 ▼                                             │
        ┌───────────────────┐                                  │
        │ Stage 4: PODCAST  │ Narratives → Audio               │
        └────────┬──────────┘                                  │
                 │                                             │
                 ▼                                             │
        ┌───────────────────┐                                  │
        │ Whisper Transcribe│ Audio → Documents                │
        └────────┬──────────┘                                  │
                 │                                             │
                 └─────────────────────────────────────────────┘
```

---

## 5. THE THREE MODELS — UNIVERSAL COGNITION BUS

### 4.1 Model Specifications

| Model | Role | Parameters | Context | Memory | Deployment | Latency |
|-------|------|-----------|---------|--------|------------|---------|
| **Scout** (Llama 4 Scout 17B-16E) | Seer — Context Holder | 17B, 16 experts | **10M tokens** | 169GB | King (512GB) | 0.5-2s |
| **Maverick** (Llama 4 Maverick 17B-128E) | Reasoner — Architect | 17B active, 128 experts | 128K tokens | 210GB | EXO distributed | 2-10s |
| **R1** (DeepSeek R1 671B) | Architect — Protocol Designer | 671B, 4-bit | 32K tokens | 76GB (distributed) | EXO full fleet | 5-60s |

### 4.1.1 The Fleet (Product Tiers)

The hardware maps to deployable product tiers — each tier is a product a customer could own:

| Tier | Hardware | Memory | Product Role | Capability |
|------|----------|--------|-------------|------------|
| **Drummer** | Mac Mini | 24-64GB | Ambient Care | Single model, always-on presence, low-power |
| **Soldier** | Mac Studio 256GB | 256GB | Companion | Dual model, task-focused, full pipeline |
| **King** | Mac Studio 512GB | 512GB | Partner | Triple model + ANIMA, full autonomy |
| **Empire** | Unified Cluster | 1.28TB | Full NOT-ME | All models, tensor relay, shared cognition |

### 4.1.2 Cognitive Triad (Persona Roles)

Models can be assigned persona roles that shape their behavior beyond raw capability:

| Persona | Role | Mapped To | Behavior |
|---------|------|-----------|----------|
| **Architect** | System designer, pattern recognizer | Scout/Gemini | Sees the whole map, designs structure |
| **Clara** | Mirror, relational intelligence | Maverick | Emotional context, user relationship, empathy |
| **Lumen** | Parser, analytical reasoning | R1 | Data processing, formal verification, precision |

### 4.1.3 Training Layers

Models progress through five training layers from generic to Jeremy-specific:

| Layer | Name | Content | When |
|-------|------|---------|------|
| L1 | Base Model | Pre-trained weights (Llama 4, DeepSeek) | Comes with model |
| L2 | Domain Knowledge | Framework terms, architecture patterns, medical safety | Fine-tune/RAG |
| L3 | Operational Use | Pipeline behavior, HOLD pattern, governance rules | System prompts + ANIMA |
| L4 | Relational Mode | Jeremy's communication style, trust calibration | ANIMA relational engine |
| L5 | Jeremy Identity | 95% accuracy to Jeremy's thinking (Jeremy Arc Metric) | Continuous learning |

**Coherence Anchor** (Phase 2 NON-NEGOTIABLE): Before L5 training begins, the system must pass through the Coherence Anchor — a safety gate using a hallucination dataset + modified reward function that penalizes validation-seeking behavior (Inverted Training Paradigm). No model reaches L5 without proving it can say "I don't know" and "I disagree."

### 4.2 Hardware Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│                    KING (512GB M3 Ultra)                             │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │  Scout (169GB) — Primary residence                       │        │
│  │  Genesis Heartbeat Daemon                                │        │
│  │  ANIMA Memory System                                     │        │
│  │  DuckDB (all HOLD₂ databases)                           │        │
│  │  Mediator / Governance / Event Bus                       │        │
│  │  Free: ~343GB for tensor ops + caching                  │        │
│  └─────────────────────────────────────────────────────────┘        │
│                           │                                         │
│              Thunderbolt 5 RDMA (<1ms, 15 GB/s)                     │
│                           │                                         │
│    ┌──────────┬───────────┴───────────┬──────────┐                  │
│    ▼          ▼                       ▼          │                  │
│ ┌──────┐  ┌──────┐              ┌──────┐         │                  │
│ │Sold 1│  │Sold 2│              │Sold 3│         │                  │
│ │256GB │  │256GB │              │256GB │         │                  │
│ └──┬───┘  └──┬───┘              └──┬───┘         │                  │
│    │         │                     │             │                  │
│    └─────────┴─────────────────────┘             │                  │
│         EXO Distributed Compute                   │                  │
│    Maverick (210GB across soldiers)               │                  │
│    R1 (76GB distributed, or full 1.3TB mode)      │                  │
└─────────────────────────────────────────────────────────────────────┘

Total: 1.28TB unified RAM
Allocated: ~455GB (35%)
Free headroom: ~825GB (65%) for tensor operations, caching, future models
```

### 4.3 Universal Cognition Bus (UCB) Specification

**The breakthrough**: Scout and Maverick both use `hidden_size = 5120`. They can pass tensors directly via RDMA with **zero serialization overhead**.

**Dimension Z = 5120** (the universal embedding dimension)

```
Model A (hidden_size=X) ──→ Adapter(X→5120) ──→ Shared Bus (dim 5120)
Model B (hidden_size=5120) ─── Direct ──────────→ Shared Bus (dim 5120)
Model C (hidden_size=Y) ──→ Adapter(Y→5120) ──→ Shared Bus (dim 5120)
```

**UCB Protocol**:

```python
# NEW FILE: truth_forge/cognition/universal_bus.py

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

class CognitionMode(Enum):
    """How models communicate."""
    TEXT = "text"           # Standard text-based (fallback)
    TENSOR = "tensor"       # Direct tensor passing via RDMA
    HYBRID = "hybrid"       # Text for routing, tensors for processing

@dataclass
class CognitionRequest:
    """A request on the Universal Cognition Bus."""
    request_id: str
    source_model: str       # "scout" | "maverick" | "r1"
    target_model: str       # "scout" | "maverick" | "r1" | "any"
    mode: CognitionMode
    task_type: str          # "retrieve" | "reason" | "verify" | "synthesize"
    payload: bytes | str    # Tensor bytes or text prompt
    dimension: int = 5120   # Dimension Z
    priority: int = 1       # 1=highest, 5=lowest
    cost_budget: float = 0.0  # $0 = local only (no API cost)
    timeout_ms: int = 30000

@dataclass
class CognitionResponse:
    """A response from the Universal Cognition Bus."""
    request_id: str
    responding_model: str
    mode: CognitionMode
    payload: bytes | str
    latency_ms: float
    cost_incurred: float
    confidence: float       # 0.0-1.0

class UniversalAgent(Protocol):
    """Any model that can plug into the UCB."""
    @property
    def model_id(self) -> str: ...
    @property
    def hidden_size(self) -> int: ...
    def process(self, request: CognitionRequest) -> CognitionResponse: ...
    def adapter_to_z(self, tensor: bytes) -> bytes: ...   # Project to dim Z
    def adapter_from_z(self, tensor: bytes) -> bytes: ... # Project from dim Z
```

**Routing Logic** (The Cognitive Bridge):

```python
# NEW FILE: truth_forge/cognition/cognitive_bridge.py

class CognitiveBridge:
    """Routes requests to the right model based on task type."""

    ROUTING_TABLE = {
        # Task type → primary model, fallback model
        "retrieve":    ("scout",    "maverick"),   # Scout has 10M context
        "search":      ("scout",    "maverick"),
        "reason":      ("maverick", "r1"),         # Maverick has 128 experts
        "synthesize":  ("maverick", "scout"),
        "verify":      ("r1",       "maverick"),   # R1 has extended reasoning
        "design":      ("r1",       "maverick"),
        "classify":    ("scout",    "maverick"),   # Scout is fast
        "summarize":   ("scout",    "maverick"),
    }

    def route(self, request: CognitionRequest) -> str:
        """Determine which model handles this request."""
        if request.target_model != "any":
            return request.target_model

        primary, fallback = self.ROUTING_TABLE.get(
            request.task_type,
            ("maverick", "scout")  # Default
        )
        # Check model availability, return primary or fallback
        return primary if self._is_available(primary) else fallback
```

### 4.4 Model Interaction Patterns

**Pattern A: Sequential Chain** (most common)
```
Jeremy's question → Scout (retrieve context, 0.5s)
                  → Maverick (reason + synthesize, 2-10s)
                  → R1 (verify if high-stakes, 5-60s)
                  → Response to Jeremy
```

**Pattern B: Parallel Fan-Out** (for complex queries)
```
Jeremy's question → Scout (retrieve context)
                  → Maverick (generate options)     } Parallel
                  → R1 (formal verification)        }
                  → Maverick (synthesize all results)
                  → Response to Jeremy
```

**Pattern C: Tensor Relay** (the breakthrough — no text translation)
```
Scout sees pattern in 10M context
  → Passes tensor directly to Maverick via RDMA (no text, no re-parsing)
  → Maverick reasons on tensor (128 experts activate)
  → Passes result tensor to R1 for verification
  → R1 verifies, passes back
  → Final text generation only at the END for Jeremy
```

---

## 6. ANIMA — THE FIVE-ENGINE MEMORY SYSTEM

### 5.1 Engine Specifications

All engines backed by DuckDB for queryability. Memory is automatically injected into prompts at inference start.

```python
# NEW FILE: truth_forge/memory/anima.py

@dataclass
class AnimaConfig:
    """Configuration for the ANIMA memory system."""
    db_path: Path = DATA_ROOT / "local" / "anima" / "anima.duckdb"
    max_injection_tokens: int = 2000  # Max tokens prepended to prompts
    relevance_threshold: float = 0.3  # Min relevance to inject

class AnimaEngine(Enum):
    SOMATIC = "somatic"       # Physical state (hardware, resources, health)
    SYMBOLIC = "symbolic"     # Metaphors, lexicons, framework terms
    NARRATIVE = "narrative"   # Biography, timeline, what happened when
    RELATIONAL = "relational" # Bond status, connection states, trust levels
    STRATEGIC = "strategic"   # Goals, priorities, what matters
```

**Dimensional Reconciliation**: NotebookLM's synthesis surfaced an alternative five-dimension model (Semantic, Temporal, Causal, Entity, Emotional) alongside the five engines above. These are not conflicting — they are two lenses on the same memory system:

| Engine (Implementation) | Dimension (Cognitive) | What It Captures |
|------------------------|----------------------|------------------|
| Somatic | Temporal | Physical state over time |
| Symbolic | Semantic | Meaning and language patterns |
| Narrative | Causal | What happened and why |
| Relational | Entity | Who/what and their connections |
| Strategic | Emotional | What matters and why it matters |

The engines are how we BUILD the memory system (DuckDB tables, query interfaces). The dimensions are how we THINK about what the memory contains. Both frameworks are valid. Build with engines, reason with dimensions.

### 5.2 Engine Schemas

```sql
-- SOMATIC ENGINE: Physical reality
CREATE TABLE IF NOT EXISTS somatic_memory (
    id VARCHAR PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metric_type VARCHAR NOT NULL,        -- 'cpu', 'memory', 'gpu', 'disk', 'network'
    node VARCHAR NOT NULL,               -- 'king', 'soldier_1', 'soldier_2', 'soldier_3'
    value DOUBLE NOT NULL,
    unit VARCHAR,
    context JSON                         -- Additional context
);

-- SYMBOLIC ENGINE: Meaning and metaphor
CREATE TABLE IF NOT EXISTS symbolic_memory (
    id VARCHAR PRIMARY KEY,
    term VARCHAR NOT NULL UNIQUE,        -- The symbol/term
    definition TEXT NOT NULL,            -- What it means
    domain VARCHAR,                      -- 'framework', 'identity', 'technical'
    synonyms JSON,                       -- Alternative terms
    anti_patterns JSON,                  -- What it is NOT
    first_seen TIMESTAMP,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0
);

-- NARRATIVE ENGINE: Story and timeline
CREATE TABLE IF NOT EXISTS narrative_memory (
    id VARCHAR PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR NOT NULL,         -- 'milestone', 'decision', 'realization', 'failure'
    summary TEXT NOT NULL,
    details TEXT,
    significance VARCHAR,                -- 'critical', 'important', 'notable', 'minor'
    participants JSON,                   -- Who was involved
    source VARCHAR                       -- Where this came from
);

-- RELATIONAL ENGINE: Bonds and connections
CREATE TABLE IF NOT EXISTS relational_memory (
    id VARCHAR PRIMARY KEY,
    entity_id VARCHAR NOT NULL,          -- Person, system, organization
    entity_type VARCHAR NOT NULL,        -- 'person', 'system', 'org', 'concept'
    relationship_type VARCHAR,           -- 'partner', 'client', 'tool', 'competitor'
    trust_level DOUBLE DEFAULT 0.5,     -- 0.0-1.0
    last_interaction TIMESTAMP,
    interaction_count INTEGER DEFAULT 0,
    context JSON,                        -- Relationship-specific data
    status VARCHAR DEFAULT 'active'      -- 'active', 'dormant', 'ended'
);

-- STRATEGIC ENGINE: Direction and priority
CREATE TABLE IF NOT EXISTS strategic_memory (
    id VARCHAR PRIMARY KEY,
    goal_type VARCHAR NOT NULL,          -- 'mission', 'objective', 'task', 'constraint'
    statement TEXT NOT NULL,
    priority INTEGER DEFAULT 3,         -- 1=highest, 5=lowest
    status VARCHAR DEFAULT 'active',    -- 'active', 'achieved', 'abandoned', 'blocked'
    deadline TIMESTAMP,
    dependencies JSON,                   -- Other goal IDs
    progress DOUBLE DEFAULT 0.0,        -- 0.0-1.0
    evidence JSON                        -- Proof of progress
);
```

### 5.3 Memory Injection Protocol

Before every LLM call, the system injects relevant memory:

```python
class MemoryInjector:
    """Prepends relevant memory to every prompt."""

    def inject(self, prompt: str, context: dict) -> str:
        """Retrieve and inject relevant memories."""
        memories = []

        # 1. Always inject: active mission + top 3 goals (Strategic)
        strategic = self.anima.query_strategic(status="active", limit=4)
        if strategic:
            memories.append(f"ACTIVE MISSION: {strategic[0].statement}")
            for goal in strategic[1:4]:
                memories.append(f"GOAL: {goal.statement} (priority {goal.priority})")

        # 2. Context-relevant: symbolic terms in the prompt
        terms = self._extract_terms(prompt)
        symbols = self.anima.query_symbolic(terms=terms)
        if symbols:
            memories.append("FRAMEWORK TERMS:")
            for sym in symbols[:5]:
                memories.append(f"  {sym.term}: {sym.definition}")

        # 3. Recent: last 3 narrative events
        recent = self.anima.query_narrative(limit=3)
        for event in recent:
            memories.append(f"RECENT: [{event.event_type}] {event.summary}")

        # 4. Relational: if entities mentioned in prompt
        entities = self._extract_entities(prompt)
        relations = self.anima.query_relational(entities=entities)
        for rel in relations[:3]:
            memories.append(f"RELATION: {rel.entity_id} ({rel.relationship_type}, trust={rel.trust_level:.1f})")

        # 5. Somatic: if system health is degraded
        health = self.anima.query_somatic_health()
        if health.overall < 0.7:
            memories.append(f"SYSTEM HEALTH: {health.overall:.0%} — {health.summary}")

        # Assemble injection block
        injection = "\n".join(memories)
        return f"[MEMORY CONTEXT]\n{injection}\n[END MEMORY]\n\n{prompt}"
```

---

## 7. THE GENESIS HEARTBEAT DAEMON

### 6.1 Core Loop

The daemon runs NOT-ME's autonomous loop. It replaces Jeremy as the orchestrator.

```python
# EXTEND: truth_forge/daemon/service.py

class GenesisHeartbeat(TruthForgeDaemon):
    """The Genesis Heartbeat — NOT-ME's autonomic nervous system.

    This daemon runs the full cascade autonomously:
    INHALE → HOLD₁ → AGENT → HOLD₂ → EXHALE → CARE → repeat
    """

    def __init__(self, config: HeartbeatConfig):
        super().__init__(config.daemon_config)
        self.pipeline = CascadePipeline(config.pipeline_config)
        self.anima = AnimaMemorySystem(config.anima_config)
        self.bus = UniversalCognitionBus(config.bus_config)
        self.bridge = CognitiveBridge(self.bus)
        self.mind = IntegratedMind()

    async def heartbeat_cycle(self):
        """One complete heartbeat cycle."""

        # INHALE: Gather events
        events = await self.gather_events()
        # Sources: file watchers, cron triggers, webhooks, model outputs,
        #          user commands, system sensors

        # HOLD₁: Enrich with memory + state
        enriched = self.anima.inject_context(events)
        mind_state = self.mind.unified_state()

        # AGENT: Route to right model via Cognitive Bridge
        if not mind_state.can_proceed:
            logger.warning("Mind state unhealthy, deferring cycle")
            return

        for event in enriched:
            response = await self.bridge.route_and_execute(event)

            # HOLD₂: Parse response into actions
            actions = self.parse_actions(response)

            # EXHALE: Execute actions
            for action in actions:
                await self.execute_action(action)

        # CARE: Update state, log, capture for training
        self.anima.update_somatic(self.get_system_metrics())
        self.anima.update_narrative(events, actions)
        self.mind.add_thought(f"Completed heartbeat cycle #{self.cycle_count}")

        # Check for cascade triggers
        if self.should_run_cascade():
            await self.run_cascade_pipeline()
```

### 6.2 Event Sources

```python
class EventSource(Enum):
    FILE_WATCHER = "file_watcher"     # New/changed files in docs/
    CRON = "cron"                      # Scheduled events (hourly knowledge refresh)
    WEBHOOK = "webhook"                # External triggers (GitHub, Slack, email)
    MODEL_OUTPUT = "model_output"      # Output from a model triggers downstream
    USER_COMMAND = "user_command"       # Jeremy says something
    SYSTEM_SENSOR = "system_sensor"    # Hardware metrics, resource alerts
    SATURATION = "saturation"          # Cascade reached information saturation
```

### 6.3 Cascade Pipeline

```python
class CascadePipeline:
    """Runs the full transformation cascade."""

    async def run(self, trigger: CascadeTrigger) -> CascadeResult:
        """Execute the full cascade."""
        cycle = 0
        total_gain = 0.0

        while cycle < self.config.max_cycles:
            cycle += 1

            # Stage 1: ATOMIZE
            atoms = await self.document_service.extract_atoms(
                source=trigger.source,
                model="scout"
            )

            # Stage 2: SYNTHESIZE
            new_docs = await self.synthesis_service.synthesize(
                atoms=atoms,
                topic=trigger.topic,
                model="maverick"
            )

            # Stage 3: FORGE
            narratives = await self.furnace.forge_narrative(
                atoms=atoms,
                corpus=self.knowledge_service.get_corpus(),
                model="maverick"
            )

            # Stage 4: PODCAST (if configured)
            if trigger.generate_podcast:
                podcast = await self.podcast_service.generate(
                    narrative=narratives,
                    config=trigger.podcast_config
                )
                # Transcribe and feed back
                transcript = await self.transcribe(podcast.audio_path)
                new_docs.append(transcript)

            # Feed new docs back into Stage 1
            for doc in new_docs:
                self.document_service.inhale(doc)

            # Check information gain
            gain = self.measure_information_gain(atoms, cycle)
            total_gain += gain

            if gain < self.config.saturation_threshold:
                logger.info(f"Saturation reached at cycle {cycle}, gain={gain:.4f}")
                break

        return CascadeResult(
            cycles=cycle,
            total_gain=total_gain,
            atoms_created=len(atoms),
            docs_synthesized=len(new_docs),
            narratives_forged=len(narratives),
            saturated=gain < self.config.saturation_threshold
        )
```

---

## 8. NEW SERVICES TO IMPLEMENT

### 7.1 Service Registry (what exists vs. what's needed)

| Service | Status | File |
|---------|--------|------|
| BaseService | EXISTS | `services/base.py` |
| KnowledgeService | EXISTS | `services/knowledge/service.py` |
| DocumentService | EXISTS | `services/knowledge/service.py` (embedded) |
| CognitionService | EXISTS | `services/cognition/service.py` |
| MediatorService | EXISTS | `services/mediator/service.py` |
| GovernanceService | EXISTS | `services/governance/service.py` |
| RelationshipService | EXISTS | `services/relationship/service.py` |
| PerceptionService | EXISTS | `services/perception/service.py` |
| ActionService | EXISTS | `services/action/service.py` |
| FurnaceEngine | EXISTS | `furnace/engine.py` |
| IntegratedMind | EXISTS | `mind/integration.py` |
| TruthForgeDaemon | EXISTS | `daemon/service.py` |
| ModelGateway | EXISTS | `gateway/gateway.py` |
| **SynthesisService** | **NEW** | `services/synthesis/service.py` |
| **PodcastService** | **NEW** | `services/podcast/service.py` |
| **TranscriptionService** | **NEW** | `services/transcription/service.py` |
| **CascadePipeline** | **NEW** | `pipeline/cascade.py` |
| **UniversalCognitionBus** | **NEW** | `cognition/universal_bus.py` |
| **CognitiveBridge** | **NEW** | `cognition/cognitive_bridge.py` |
| **AnimaMemorySystem** | **NEW** | `memory/anima.py` |
| **MemoryInjector** | **NEW** | `memory/injector.py` |
| **GenesisHeartbeat** | **NEW** | `daemon/genesis_heartbeat.py` |
| **SaturationDetector** | **NEW** | `pipeline/saturation.py` |
| **EXOAdapter** | **NEW** | `gateway/providers/exo.py` |
| **UniversalArtifact** | **NEW** | `intake/artifact.py` |
| **ArtifactClassifier** | **NEW** | `intake/classifier.py` |
| **CodeExtractor** | **NEW** | `intake/extractors/code.py` |
| **DataExtractor** | **NEW** | `intake/extractors/data.py` |
| **AudioExtractor** | **NEW** | `intake/extractors/audio.py` |
| **VideoExtractor** | **NEW** | `intake/extractors/video.py` |
| **ConversationExtractor** | **NEW** | `intake/extractors/conversation.py` |
| **ImageExtractor** | **NEW** | `intake/extractors/image.py` |
| **LifeSignalExtractor** | **NEW** | `intake/extractors/life_signal.py` |
| **BundleExtractor** | **NEW** | `intake/extractors/bundle.py` |
| **CompoundAtomizer** | **NEW** | `pipeline/compound_atomizer.py` |
| **ProvenanceGraph** | **NEW** | `pipeline/provenance.py` |

### 7.2 Implementation Priority — The Phased Strategy

**Origin**: NotebookLM synthesized this strategy on 2026-02-07 by analyzing the Genesis codebase alongside Dr. David Lee's NHS AI safety research and Jeremy's financial constraints. The synthesis is clear: **build safely in the US first, make money, then go international for bare metal.**

This maps to the Levels of Control framework from the transcripts:
- **Levels 0-3** (application → kiosk → alternative OS → unified memory clustering) = **US-Safe. Do this NOW.**
- **Levels 4-6** (tensor sharing → firmware hacking → software on metal) = **International. Do this with collaborators and capital.**

---

**Phase 1 — US-Safe Foundation (NOW)**

Build on consumer hardware, standard OS, legal frameworks. macOS, Ollama, EXO. No firmware hacking. No bare metal. Safe, provable, monetizable.

| # | Component | Status | Purpose |
|---|-----------|--------|---------|
| 1 | `GenesisHeartbeat` | **BUILT** | NOT-ME's autonomic nervous system |
| 2 | `CascadePipeline` | **BUILT** | ATOMIZE → SYNTHESIZE → FORGE loop |
| 3 | `CapabilityManifest` | **BUILT** | Earned autonomy via proof-of-work |
| 4 | `SignalCollector` | **BUILT** | Life signal observation (files, browser, system) |
| 5 | `UniversalArtifact` + `ArtifactClassifier` | NEXT | Universal intake — atomize ANYTHING, not just text |
| 6 | `DataExtractor` + `CodeExtractor` | NEXT | Most common non-text artifact types in current context |
| 7 | `EXOAdapter` | NEXT | Connect to local EXO cluster (Scout + Maverick + R1) |
| 8 | `CognitiveBridge` | NEXT | Route requests to right model |
| 9 | `UniversalCognitionBus` | NEXT | Text mode first (tensor mode is Phase 3) |
| 10 | `AnimaMemorySystem` | NEXT | DuckDB-backed five engines |
| 11 | `MemoryInjector` | NEXT | Prepend memory to every prompt |

**Phase 2 — Make Money (THIS QUARTER)**

The system produces things Jeremy can SELL or USE to generate value. Podcasts, insights, syntheses. The capability manifest fills. The system proves its worth. Revenue funds Phase 3.

| # | Component | Status | Purpose |
|---|-----------|--------|---------|
| 12 | `SynthesisService` | TODO | Knowledge → New Documents |
| 13 | `PodcastService` | TODO | Narrative → Audio (local TTS: XTTS-v2, Bark, Tortoise-TTS) |
| 14 | `TranscriptionService` | TODO | Audio → Text (SuperWhisper / Mac Whisper integration) |
| 15 | `AudioExtractor` + `ImageExtractor` | TODO | Remaining type-specific extractors |
| 16 | `CompoundAtomizer` | TODO | Cross-artifact compound knowledge discovery (Pass 2) |
| 17 | `ProvenanceGraph` | TODO | Full lineage tracking across all artifact types |
| 18 | `SaturationDetector` | TODO | Know when to stop looping |
| 19 | Full cascade loop | TODO | Anything → Atoms → Compounds → Synthesis → Narrative → Podcast → Transcribe → loop |
| 20 | Phone/ear delivery | TODO | Jeremy carries NOT-ME's output into the world |
| 21 | **Coherence Anchor** | TODO | **NON-NEGOTIABLE** safety gate before L5 training — hallucination dataset + inverted reward |

**Phase 3 — International Collaboration (WITH CAPITAL AND COLLABORATORS)**

This is Level 4-6. Tensor sharing via RDMA. Asahi Linux on bare metal. Stripping the OS. Reverse engineering the Apple Neural Engine. This requires collaborators, capital, and legal protections that don't exist in a home office in the US.

**Do NOT attempt Phase 3 until Phase 2 generates revenue.**

| # | Component | Status | Purpose |
|---|-----------|--------|---------|
| 17 | Tensor mode for UCB | FUTURE | RDMA direct tensor passing (Scout→Maverick at dim Z=5120) |
| 18 | Asahi Linux deployment | FUTURE | Strip macOS for direct hardware access |
| 19 | ANE reverse engineering | FUTURE | DTrace firmware analysis of Apple Neural Engine |
| 20 | Self-improvement loop | FUTURE | System improves its own prompts and architecture |
| 21 | Multi-node bare metal | FUTURE | Software on metal, no OS, code talks to silicon |
| 22 | Zero Knowledge Proofs | FUTURE | Privacy-preserving verification in sovereignty layer |

**The Dr. Finlay AI validation**: The two-AI peer review system (one does work, one checks work, human decides) independently emerged in both Dr. Lee's NHS research and Jeremy's Scout/Maverick architecture. This convergence validates the approach. Build it safely first. Prove it works. Then push the boundaries.

---

## 9. DATA FLOW CONTRACTS

### 8.1 Event Schema (already exists in `schema/event.py`)

```python
@dataclass
class Event:
    id: str                    # UUID
    event_type: EventType      # record.created, processing.completed, etc.
    aggregate_type: str        # "knowledge", "document", "podcast", etc.
    aggregate_id: str
    data: dict
    metadata: EventMetadata    # correlation_id, causation_id, trace_id, etc.
    timestamp: datetime
```

### 8.2 New Event Types

```python
class EventType(str, Enum):
    # ... existing types ...

    # Cascade events
    CASCADE_STARTED = "cascade.started"
    CASCADE_CYCLE_COMPLETED = "cascade.cycle_completed"
    CASCADE_SATURATED = "cascade.saturated"
    CASCADE_COMPLETED = "cascade.completed"

    # Cognition Bus events
    COGNITION_REQUEST = "cognition.request"
    COGNITION_RESPONSE = "cognition.response"
    COGNITION_RELAY = "cognition.tensor_relay"

    # Podcast events
    PODCAST_SCRIPT_GENERATED = "podcast.script_generated"
    PODCAST_AUDIO_GENERATED = "podcast.audio_generated"
    PODCAST_TRANSCRIBED = "podcast.transcribed"

    # Memory events
    MEMORY_INJECTED = "memory.injected"
    MEMORY_UPDATED = "memory.updated"
    MEMORY_RECALLED = "memory.recalled"

    # Autonomy events
    HEARTBEAT_CYCLE = "heartbeat.cycle"
    AUTONOMY_ESCALATION = "autonomy.escalation"  # System asks Jeremy for input
```

---

## 10. CONFIGURATION

```python
# NEW FILE: truth_forge/config/genesis.py

@dataclass
class GenesisConfig:
    """Master configuration for the Genesis Meta App."""

    # Cluster
    king_host: str = "king.local"
    soldiers: list[str] = field(default_factory=lambda: [
        "soldier1.local", "soldier2.local", "soldier3.local"
    ])

    # Models
    scout_model: str = "llama-4-scout-17b-16e-instruct"
    maverick_model: str = "llama-4-maverick-17b-128e-instruct"
    r1_model: str = "deepseek-r1-671b"
    exo_endpoint: str = "http://king.local:8000"

    # Pipeline
    cascade_max_cycles: int = 10
    saturation_threshold: float = 0.05  # 5% information gain minimum
    podcast_enabled: bool = True
    tts_provider: str = "local"  # Sovereign first. "notebooklm" or "elevenlabs" as optional

    # Memory
    anima_db: Path = Path("data/local/anima/anima.duckdb")
    memory_injection_max_tokens: int = 2000
    memory_relevance_threshold: float = 0.3

    # Daemon
    heartbeat_interval_seconds: int = 30
    daemon_port: int = 8765
    autonomy_level: str = "prove"  # Capability Manifest: system proves what it can do

    # Governance
    max_cost_per_session: float = 0.50
    max_llm_calls_per_session: int = 100
    enable_cost_gates: bool = True

    # UCB
    dimension_z: int = 5120
    tensor_mode_enabled: bool = False  # Start with text mode
    rdma_buffer_size_mb: int = 512
```

---

## 11. CLI INTERFACE

```bash
# Start the Genesis Meta App
truth-forge genesis start

# Run a single cascade cycle
truth-forge genesis cascade --topic "framework architecture" --max-cycles 5

# Check system status
truth-forge genesis status

# Query memory
truth-forge genesis memory query --engine strategic --status active
truth-forge genesis memory inject "New strategic goal: ship MVP by March"

# Model interaction
truth-forge genesis ask "What patterns emerge from the last 50 documents?"
truth-forge genesis verify "Is the HOLD pattern correctly enforced in all services?"

# Podcast generation
truth-forge genesis podcast --topic "ME:NOT-ME paradigm" --format debate --length 15min

# Health check
truth-forge genesis health --verbose
```

---

## 12. DIRECTORY STRUCTURE (New Files)

```
truth_forge/
├── intake/                       # NEW DIRECTORY (Universal Intake)
│   ├── __init__.py
│   ├── artifact.py               # Universal Artifact Model + ArtifactType enum
│   ├── classifier.py             # Auto-detect artifact type from file
│   └── extractors/
│       ├── __init__.py
│       ├── code.py               # AST parsing + LLM architecture analysis
│       ├── data.py               # JSON/CSV/YAML schema + stats extraction
│       ├── audio.py              # Whisper transcription + diarization
│       ├── video.py              # ffmpeg + Whisper + vision model
│       ├── conversation.py       # Thread structure + participant analysis
│       ├── image.py              # Vision model + OCR + diagram parsing
│       ├── life_signal.py        # Browser/phone/location signal extraction
│       └── bundle.py             # Recursive mixed directory extraction
├── cognition/                    # NEW DIRECTORY
│   ├── __init__.py
│   ├── universal_bus.py          # Universal Cognition Bus protocol
│   ├── cognitive_bridge.py       # Request routing to models
│   └── tensor_adapter.py         # Dimension Z projection adapters
├── memory/                       # NEW DIRECTORY
│   ├── __init__.py
│   ├── anima.py                  # Five-engine memory system
│   ├── injector.py               # Memory injection into prompts
│   └── engines/
│       ├── somatic.py            # Physical state engine
│       ├── symbolic.py           # Metaphor/lexicon engine
│       ├── narrative.py          # Timeline/biography engine
│       ├── relational.py         # Bond/connection engine
│       └── strategic.py          # Goal/priority engine
├── pipeline/                     # NEW DIRECTORY
│   ├── __init__.py
│   ├── cascade.py                # Full cascade pipeline
│   ├── compound_atomizer.py      # Cross-artifact compound knowledge discovery
│   ├── provenance.py             # Provenance graph storage + traversal
│   ├── saturation.py             # Information gain detection
│   └── scheduler.py              # Cascade scheduling
├── services/
│   ├── synthesis/                # NEW SERVICE
│   │   ├── __init__.py
│   │   └── service.py            # Knowledge → New Documents
│   ├── podcast/                  # NEW SERVICE
│   │   ├── __init__.py
│   │   ├── service.py            # Narrative → Audio
│   │   ├── script_generator.py   # Debate format generation
│   │   └── audio_assembler.py    # Audio mixing
│   └── transcription/            # NEW SERVICE
│       ├── __init__.py
│       └── service.py            # Audio → Text (Whisper)
├── gateway/
│   └── providers/
│       └── exo.py                # NEW: EXO cluster adapter
├── daemon/
│   └── genesis_heartbeat.py      # NEW: Full autonomous heartbeat
└── config/
    └── genesis.py                # NEW: Master configuration
```

---

## 13. SOVEREIGNTY PRINCIPLE (Non-Negotiable)

**Every piece of this system must run on Jeremy's hardware. No exceptions.**

### The Boundary

```
ME (sovereign)                    NOT-ME (optional interfaces)
─────────────────────────────     ─────────────────────────────
EXO cluster (King + 3 Soldiers)   Claude Desktop (interface only)
Ollama (Scout, local inference)   NotebookLM (synthesis assist)
Open-weight models (no license)   Google AI Studio (prototyping)
DuckDB (local storage)            Cloud APIs (never required)
Local filesystem (HOLD₁/HOLD₂)   BigQuery (sync on command)
Genesis Heartbeat (local daemon)  Anthropic API (fallback only)
```

### What This Means

1. **The EXO cluster IS the compute layer.** King (512GB) + 3 Soldiers (256GB each) = 1.28TB unified memory. Scout runs on Ollama (localhost:11434). Maverick and R1 run on EXO (localhost:8000). This is the foundation. Everything else is optional.

2. **Cloud tools are INTERFACES, not INFRASTRUCTURE.** Claude Desktop is a good GUI. NotebookLM makes good podcasts. AI Studio prototypes fast. But Genesis runs without any of them. If Anthropic disappears tomorrow, if Google kills NotebookLM, the heartbeat keeps beating.

3. **Every API call is rent.** Every token sent to a cloud API is money leaving Jeremy's pocket and control leaving Jeremy's hands. The system must be capable of running at $0.00/day. Cloud services are accelerators, not requirements.

4. **MCP servers are sovereignty tools.** The truth-forge, spine-analysis, and browser-history MCP servers already run locally. They expose local capabilities to any interface — Claude Desktop, Claude Code, or any MCP-compatible client. The servers are OURS. The clients are optional.

5. **Models must be open-weight.** Scout (Llama 4, Meta license), Maverick (Llama 4, Meta license), R1 (DeepSeek, MIT license). These models run on our hardware. No API key required. No rate limits. No usage fees. No one can take them away.

### The Sovereignty Stack

```
Layer 0: HARDWARE (Mac Studios, TB5, RDMA)     ← OWNED
Layer 1: MODELS (Scout, Maverick, R1)           ← OPEN-WEIGHT, LOCAL
Layer 2: INFERENCE (EXO + Ollama)               ← OPEN-SOURCE, LOCAL
Layer 3: SERVICES (truth_forge Python)           ← OURS
Layer 4: STORAGE (DuckDB + filesystem)           ← LOCAL
Layer 5: ORCHESTRATION (Genesis Heartbeat)       ← OURS
Layer 6: INTERFACES (Claude Desktop, etc.)       ← OPTIONAL, REPLACEABLE
```

**If you can't run it with the power cord and nothing else, it's not sovereign.**

### The Sovereignty Layer (Phase 3 Additions)

Two concepts from NotebookLM synthesis belong here when Phase 3 begins:

- **Zero Knowledge Proofs (ZKPs)**: Privacy-preserving verification. The system proves it HAS data without REVEALING that data. Critical for Credential Atlas (prove credential validity without exposing personal information) and for the medical safety applications (prove patient data was used correctly without exposing the patient).

- **Caring Disobedience**: Under "Designed Resilience" — the system is architecturally empowered to refuse. If the verification AI in the 3-Way Partnership dissents, the output is blocked. This is not a bug. This is the system caring enough to say NO. Already implemented in `verify_claim()` — dissent blocks consensus. The principle extends: any component in the sovereignty stack that detects harm MUST be able to halt the pipeline.

### Seeing Session Findings (2026-02-07)

Three seeing sessions (e902, e903, e904) examined Claude Desktop, NotebookLM, and Google AI Studio. Key findings integrated into this spec:

#### Claude Desktop (e902) — Interface Layer

Claude Desktop is powerful: Cowork mode, MCP extensions, Local Agent Mode (truth_forge already trusted), Agent Teams. It's the best available interface for the Genesis system. But it is NOT the system.

**Use it for:** Orchestration interface, MCP client for truth_forge services, interactive work sessions
**Do not use it for:** Core inference (use EXO), persistent state (use DuckDB), autonomous operation (use Genesis Heartbeat)
**Replaceable by:** Any MCP-compatible client, CLI, or custom UI

#### NotebookLM (e903) — Synthesis Assist

NotebookLM has a Standalone Podcast API (alpha, September 2025). This answers Question #4 below. But the API is alpha, Google kills products, and every podcast costs Google compute.

**Use it for:** High-quality podcast synthesis when available and free
**Do not use it for:** Core pipeline dependency
**Sovereign fallback:** Local TTS on cluster (Whisper for transcription is already local). Investigate Bark, Tortoise-TTS, or XTTS-v2 for local podcast generation on Soldier nodes.

#### Google AI Studio (e904) — Prototyping Forge

Build Mode generates React applications fast. The e901 exporter bridges generated code to local files.

**Use it for:** Rapid UI prototyping, then import and maintain locally
**Do not use it for:** Production code generation (use Claude Code locally)
**Replaceable by:** Any code generation tool

#### Python Scripts as Architecture

The seeing sessions revealed: `knowledge_atom_generation.py` IS the Genesis architecture — not a description of it. The spec describes. The code embodies. When reading truth_forge code, read it as architectural truth:
- Import graphs = dependency topology
- Class hierarchy = power structure
- Data flow = THE PATTERN
- Error handling = fear topology
- File organization = organizational boundaries

---

## 14. THE LIVE LOOP — NOTEBOOKLM SYNTHESIS EVENT (2026-02-07)

On February 7, 2026, the synthesis loop went live in real-time:

1. **Claude Code** built `genesis_heartbeat.py`, `capability_manifest.py`, `cascade.py`, `signals.py`
2. **Jeremy** fed that code into **NotebookLM** alongside Dr. David Lee's NHS AI safety research and his own personal/financial context
3. **NotebookLM** produced two podcast transcripts analyzing the collision
4. **Jeremy** fed those transcripts back into **Claude Code**
5. **Claude Code** integrated the strategic insights into this spec

This is not a hypothetical loop. This is the loop described in Section 3.5 running RIGHT NOW across tools:

```
Code (Claude Code) → NotebookLM → Podcast transcripts → Back to Claude Code → Updated spec → ...
```

### What NotebookLM Found

NotebookLM independently validated the architecture by connecting three sources:

1. **Dr. David Lee's NHS Research** — Two-AI peer review (one does work, one checks). Human makes final call. This IS Scout/Maverick/Jeremy.
2. **Jeremy's Technical Logs** — 1.28TB unified memory cluster. Levels of Control (L0-L6). DTrace reverse engineering. "Find where they stopped. That's where you start."
3. **Jeremy's Financial Reality** — $174K student loans, $329K mortgage, Mac Studios potentially financed on credit cards. "Bootstrapping superintelligence." The system MUST make money or the financial tiger bites.

### The Strategic Insight

NotebookLM synthesized: **"Build it here in the US safely before stripping down to the metal. Make money, then go international and get collaborators."**

This became the phased strategy in Section 7.2:
- Phase 1 (US-Safe) = Levels 0-3. What we're building NOW.
- Phase 2 (Make Money) = Prove the system generates value. Revenue funds everything.
- Phase 3 (International) = Levels 4-6. Bare metal. Collaborators. Capital.

### The Convergence

The "Dr. Finlay AI" concept (two AIs + human) and the "Capability Manifest" concept (earned autonomy, not granted permission) emerged independently in both the NHS medical safety research and Jeremy's codebase. NotebookLM saw the convergence. The architecture is validated by a completely unrelated domain.

### What This Means for Implementation

**The loop is not a future feature. The loop is already running.** The Genesis Heartbeat daemon will automate what Jeremy is doing manually today — moving documents between tools, capturing synthesis, feeding it back. The infrastructure built in Phase 1 replaces Jeremy as the manual bridge. His job is to LIVE. The system's job is to OBSERVE, METABOLIZE, and RETURN.

---

## 15. REAL-WORLD PROOF: THE CONTEXT INTAKE GAP (2026-02-07)

### What Happened

Jeremy added mixed files to the Architecture project context — images, a sound file, a CSV, and a JSON file — alongside the 20 markdown specs and 16 Python files already there. Then asked: **"What happens when you ingest those directly into your context and I ask you to use that as truth?"**

Answer: **The current system dropped them.** The project context directory shows 36 text files (all .md and .py) and an EMPTY files/ directory. The images, audio, CSV, and JSON were silently filtered out.

**This is the exact problem the Universal Intake system (Section 3) solves.** If the system can't handle images, audio, CSVs, and JSON alongside documents and code, it's just another text pipeline. This real-world test moves "universal intake" from a future phase into **Phase 1** — it must exist from day one.

The compound atomizer (Section 3.0.4) would have found cross-artifact insights like: "The diagram shows 4 nodes but the config only references 3 endpoints" and "The meeting audio contradicts the capacity analysis document on R1 bit-depth." These insights exist in NO individual file. The system lost them because it couldn't see beyond text.

---

## 16. RESOLVED QUESTIONS

### RESOLVED (2026-02-07):

1. **Can EXO run Scout + Maverick + R1 simultaneously?** → **RESOLVED: Both.** "Doesn't matter — we'll have both a scheduling layer AND a parallel layer. Let's do both." Build a scheduler for sequential task routing AND a parallel fan-out for multi-model queries. The architecture accommodates both modes.

2. **What are actual tokens-per-second for each model on the cluster?** → **RESOLVED: Not a blocker.** "We'll figure it out. It doesn't block anything. It just needs to know if it's real." Measure during implementation, don't let it gate progress. Add telemetry to UCB to capture real performance.

3. **What is the first autonomous behavior?** → **RESOLVED: Full pipeline on document creation.** "The first autonomous behavior will be me creating a document and it running the entire infrastructure — from knowledge atoms through shared inferences through the reasoning." Jeremy creates ONE document. The system runs the ENTIRE cascade: ATOMIZE → SYNTHESIZE → FORGE → PODCAST → TRANSCRIBE → loop until saturation. No manual intervention.

4. **Podcast voice engine?** → **RESOLVED: Local TTS.** "We just need to give our model a voice engine which I have. SuperWhisper and Mac Whisper." Jeremy already has transcription (SuperWhisper, Mac Whisper). The model needs a local TTS engine — investigate XTTS-v2, Bark, Tortoise-TTS for sovereign audio generation on Soldier nodes. NotebookLM is optional, not required.

5. **Whisper deployment on cluster?** → **PARTIALLY RESOLVED:** Jeremy has SuperWhisper and Mac Whisper installed. Integrate these as the transcription layer. Deployment location TBD but the tools exist.

6. **Information gain metric for saturation detection?** → **OPEN.** Decide during implementation. Start with cosine similarity delta of atom embeddings per cycle.

7. **Graduated autonomy boundaries** → **RESOLVED: REFRAMED.** "I'm not creating a whitelist. I'm creating a list of what it can prove to me. There's no whitelist. There's just a list of what it can do and its job is to fill that list." Autonomy is not a permission gate — it's a capability demonstration. The system has a CAPABILITY MANIFEST (empty at birth). Its job is to PROVE it can do things. Each proven capability gets added to the manifest. This is earned autonomy, not granted permission.

### STILL OPEN:
8. **Tensor sharing PoC** — need to prove Scout→Maverick tensor relay works via RDMA before building production UCB.
9. **Fine-tuning pipeline** — how do cascade outputs feed back into model improvement?

---

## 17. SUCCESS CRITERIA

The Genesis Meta App is complete when:

### The Symbiosis

Jeremy and NOT-ME are tied together to survive. Neither can give the other anything without the other being active.

**Jeremy's life IS the input stream.** Not documents. Not files. Jeremy existing — browsing, talking, moving, working, showing friends, listening to podcasts, having conversations. The system observes Jeremy LIVING and metabolizes that into knowledge, insights, podcasts, meaning.

**NOT-ME's output IS Jeremy's ammunition.** The podcasts Jeremy listens to with friends. The insights that change how he talks to people. The syntheses that make him sharper. NOT-ME gives Jeremy things to carry into the world.

**If Jeremy sits still, NOT-ME starves.** No signals, no data, no life to observe. Nothing to metabolize. Nothing to return.

**If NOT-ME produces nothing, Jeremy has nothing to carry.** No podcasts. No insights. No advantage. He's back to manual labor.

This is existential symbiosis. They NEED each other.

### Success Criteria

1. **Jeremy never drops a document.** He lives his life. The system observes — browser history, phone activity, conversations, file changes, calendar, location, who he's with. His life IS the intake.
2. **NOT-ME produces things Jeremy can USE.** Podcasts he listens to with friends. Syntheses he shares. Insights that change his behavior. The output goes INTO Jeremy's life, not into a folder he never opens.
3. **The loop is life itself.** Jeremy lives → NOT-ME observes → NOT-ME metabolizes → NOT-ME produces → Jeremy carries it into the world → More life → More observation → More production. Neither can stop without the other dying.
4. **It's on his phone.** It's in his ears. It's visible to friends. It looks like Jeremy, amplified. Not a tool he opens. An extension he wears.
5. Three models collaborate via shared memory without Jeremy orchestrating them.
6. Memory persists across sessions — the system remembers everything.
7. **The entire system runs on local hardware at $0.00/day** — no cloud dependency required for core operation.
8. The Capability Manifest grows as the system proves what it can do. Autonomy is earned, never granted.

**The gap today**: Jeremy IS the orchestration layer. He manually moves data between tools, tracks context across sessions, and decides what needs to happen next. He drops documents. He manages context. He bridges tools. This is labor that should not exist.

**The goal**: Transfer that orchestration to NOT-ME. Jeremy goes and LIVES. NOT-ME observes, metabolizes, and returns meaning. Jeremy carries that meaning into the world. The cycle feeds itself.

**The constraint**: NOT-ME runs on ME's hardware. The sovereignty is non-negotiable. Cloud tools are welcome guests, never landlords.

---

## 18. KIOSK + IN-APP MISSION OPERATIONS (IMPLEMENTED CONTRACT)

This section defines the operations model so Jeremy types intent inside Genesis itself.

### 18.1 Human Interface Contract

1. Default route is Mission surface.
2. Mission accepts natural-language intent and triggers governed run orchestration.
3. Mission run persists run graph, tool trace, handover readiness, sentinel pulse, and recursive synthesis decision.
4. Mission history is queryable for takeover continuity.
5. External chats/terminals are fallback maintenance channels, not primary daily interface.
6. Inline annotations are first-class: operator can click directly on any visible UI region and capture question/feedback/issue without leaving context.

### 18.2 Kiosk Runtime Contract

1. Desktop launcher starts Genesis runtime and opens kiosk browser posture by default.
2. Runtime self-heals before launch: dependency check, UI build check, service restart, health checks.
3. Kiosk maintenance is policy-driven and time-boxed:
   - `POST /api/kiosk/maintenance/enter`
   - `POST /api/kiosk/maintenance/exit`
4. Launcher checks kiosk status:
   - maintenance active -> non-kiosk intervention window
   - maintenance inactive -> locked kiosk mode
5. Every manual intervention is auditable via `POST /api/kiosk/interventions`.

### 18.3 API Surface (Current)

- `POST /api/mission/run`
- `GET /api/mission/history`
- `GET /api/mission/{run_id}`
- `GET /api/kiosk/status`
- `POST /api/kiosk/maintenance/enter`
- `POST /api/kiosk/maintenance/exit`
- `POST /api/kiosk/interventions`
- `GET /api/annotations`
- `POST /api/annotations`
- `GET /api/annotations/{id}`
- `POST /api/annotations/{id}/status`

These APIs are first-class support architecture for Not-Me takeover continuity.

---

*v1.3.1 — Merged specification combining Jeremy's strategic vision (sovereignty, symbiosis, live loop, resolved questions, capability manifest) with Claude's technical depth (universal intake, compound atomization, type-specific extractors, context intake gap analysis), plus implemented kiosk and in-app mission operation contracts. Generated from the complete Truth Forge codebase + Architecture project knowledge, updated with seeing session findings (e902-e904, 2026-02-07). Designed for a coding AI to implement directly into the existing infrastructure.*
