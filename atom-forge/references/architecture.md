# Atom-Forge Architecture

## THE INSIGHT

The spine was the engineering scaffolding — decomposing conversations into L2-L8 hierarchies to enable mechanical processing. Knowledge atoms are the intelligence — extracted meaning with 12-dimensional metadata that captures everything the spine provides and more.

The realization: if the Knowledge Atom system is strong enough, it can look at conversation data and directly produce the atoms that tell you everything — facts, emotions, decisions, patterns, relationships — without the intermediate spine decomposition.

```
BEFORE (Pipeline Architecture):
  Raw Data → Python NLP → Spine (L2-L8) → Enrichment → Knowledge Atoms → BigQuery
  [6 stages, multiple tools, fragile, expensive]

AFTER (Atom-Forge Architecture):
  Raw Data → LLM (Claude) → Knowledge Atoms → BigQuery
  [1 stage, one intelligence, robust, direct]
```

## THE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                       ATOM-FORGE                             │
│              Universal Knowledge Atom Gateway                │
│                                                              │
│  ┌─────────┐    ┌──────────────┐    ┌───────────────────┐   │
│  │ Sources  │───→│  LLM Core    │───→│  3-Gate Dedup     │   │
│  │         │    │  (Claude)    │    │                   │   │
│  │ • JSONL  │    │              │    │  Gate 1: SHA-256  │   │
│  │ • Text   │    │ • Comprehend │    │  Gate 2: Cosine   │   │
│  │ • JSON   │    │ • Extract    │    │  Gate 3: Graph    │   │
│  │ • CSV    │    │ • Dimension  │    │                   │   │
│  │ • Any    │    │ • 12-dim     │    │                   │   │
│  └─────────┘    └──────────────┘    └────────┬──────────┘   │
│                                               │              │
│                                    ┌──────────▼──────────┐   │
│                                    │   truth-forge MCP    │   │
│                                    │                      │   │
│                                    │  • Write atoms       │   │
│                                    │  • Generate embed    │   │
│                                    │  • SafeBQ Writer     │   │
│                                    │  • DLQ on failure    │   │
│                                    └──────────┬──────────┘   │
│                                               │              │
│                                    ┌──────────▼──────────┐   │
│                                    │     BigQuery         │   │
│                                    │  knowledge_atoms     │   │
│                                    └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## THE LLM IS THE TRANSFORMER

In traditional pipelines, you write code for each transformation step:
- spaCy for sentence segmentation
- Gemini Flash Lite for text cleaning
- Regex for entity extraction
- Custom code for topic detection
- Statistical models for sentiment analysis

In Atom-Forge, the LLM does ALL of this in one pass:
- It reads the raw data
- It understands the context, the participants, the emotional undertones
- It extracts facts, decisions, patterns, emotions — all at once
- It fills 12 metadata dimensions with nuanced understanding
- It produces clean, deduplicated, richly annotated knowledge atoms

This is not a simplification — it's an evolution. The LLM brings understanding that no mechanical pipeline can match.

## SOURCE ADAPTERS

Atom-Forge processes any input, but different sources benefit from specialized reading patterns:

### Claude Code Sessions (.claude/projects/*.jsonl)
- Record types: user, assistant, queue-operation
- Rich content: thinking blocks, tool use, code
- Subagent conversations in subdirectories
- Source metadata: session_id, model, version, cwd, git_branch

### Gemini Conversations
- Export format: JSON with structured messages
- Roles: user, model
- May include function calls and results

### Generic LLM Conversations
- Any JSON/JSONL with role + content structure
- Detect format, map to standard conversation model

### Documents and Transcripts
- Text files, markdown, HTML
- Extract knowledge directly from prose

### Structured Data
- CSV/JSON with domain-specific fields
- LLM interprets column meanings, extracts knowledge

## FOUR PILLARS COMPLIANCE

### Fail-Safe
- If atomization fails for a record, log to DLQ, continue
- If BigQuery write fails, retry with exponential backoff (1s, 2s, 4s)
- If entire session fails, log error, move to next session
- Never lose data — failed records are preserved for retry

### No Magic
- Every atom traces to exact source (file + record UUID + timestamp)
- 12-dimensional metadata is explicitly populated (no hidden inference)
- Enrichment coverage shows exactly what percentage of dimensions are filled
- Atomization report documents every extraction decision

### Observability
- Per-session atomization reports
- Batch processing progress logs
- Deduplication statistics (which gate caught what)
- Cost tracking (tokens used, estimated spend)
- Processing checkpoints for resume

### Idempotency
- SHA-256 content hash = same input → same atom ID
- Reprocessing a session produces identical atoms
- 3-gate deduplication prevents duplicate writes
- Checkpoint-based resume doesn't reprocess completed sessions

## DATA ENFORCEMENT

- NEVER use streaming inserts (batch only via SafeBigQueryWriter)
- NEVER skip validation
- NEVER hardcode source_pipeline values
- ALWAYS include source tracking (source_file, source_file_path, source_system)
- ALWAYS validate before write
- ALWAYS log to DLQ on failure
- ALWAYS use WRITE_APPEND disposition

## COST MODEL

Processing 1,039 sessions (2.4 GB):
- Reading: ~2.4M tokens input per session average → varies widely
- Extraction: Claude processes text, produces atoms
- Per-session cost cap: $0.50
- Total pipeline cap: $80.00
- Expected yield: 50,000–200,000 knowledge atoms
- Cost per atom: ~$0.0004–$0.0016

## THE RELATIONSHIP TO SPINE

The spine infrastructure (entity_unified) still exists and serves its purpose for structural queries — "show me the third message in conversation X" requires hierarchical decomposition. Atom-Forge doesn't replace the spine; it provides an alternative path for KNOWLEDGE extraction that goes directly to atoms.

The two systems are complementary:
- **Spine**: Structural decomposition (WHAT was said, in WHAT order, by WHOM)
- **Atoms**: Knowledge extraction (what was KNOWN, DECIDED, FELT, LEARNED)

Some data may flow through both. Some data only needs atoms. The universal gateway means you choose the right path for the right purpose.

## FUTURE: ANY SYSTEM, ALWAYS

The vision: every system Jeremy uses produces knowledge atoms automatically.
- Claude Code conversations → atoms (via ingest-sessions)
- Gemini conversations → atoms (via generic adapter)
- Browser history → atoms (via truth-browser-logger + atomizer)
- Text messages → atoms (via text message adapter)
- Documents → atoms (via document atomizer)
- Meetings → atoms (via transcript atomizer)

One gateway. Many sources. All knowledge atoms. All in BigQuery. All searchable, deduplicated, connected.
