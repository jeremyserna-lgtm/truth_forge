# Connectors

## Atom-Forge Ecosystem Connections

| Category | Tool | Status |
|----------|------|--------|
| Atom writer | truth-forge MCP — Knowledge Atoms (20K+ atoms in `knowledge_atoms` dataset) | Configured |
| Deduplication | truth-forge MCP — 3-gate system (hash, 0.95 cosine similarity, knowledge graph) | Configured |
| Embedding | Gemini embedding API — `text-embedding-004` (3072 dimensions) | Configured |
| Data warehouse | BigQuery `flash-clover-464719-g1.knowledge_atoms` | Configured |
| Session source | Local filesystem — `.claude/projects/` JSONL files | Configured |
| Spine reference | spine-analysis MCP — for knowledge graph gate (Gate 3) | Configured |

## Architecture

```
ANY DATA ──→ [LLM Atomizer] ──→ 3-Gate Dedup ──→ Knowledge Atoms ──→ BigQuery
              (Claude IS               │
               the engine)             ├─ Gate 1: SHA-256 hash (exact match)
                                       ├─ Gate 2: Cosine similarity ≥ 0.95
                                       └─ Gate 3: Knowledge graph resolution
```

## What Goes In

- Claude Code session JSONL files (conversations with tools, thinking, results)
- Gemini conversation exports
- Any LLM conversation data (Codex, Copilot, Grok)
- Text documents, transcripts, notes
- Any structured or unstructured data

## What Comes Out

Knowledge Atoms with 12-dimensional metadata:
1. Semantic (theme, domain, abstraction)
2. Significance (tier, novelty, actionability)
3. Epistemic (certainty, evidence, verifiability)
4. Temporal (scope, durability)
5. Relational (entities, concepts, dependencies, implications)
6. Dialectical (supports, contradicts, tensions, synthesis)
7. Affective (sentiment, intensity, stakes, urgency)
8. Pragmatic (actions, preconditions, consequences, audience)
9. Structural (type, complexity, completeness)
10. Ontological (entity type, categories, taxonomy, parts)
11. Normative (descriptive/prescriptive/evaluative, values, prescriptions)
12. Enrichment tracking (coverage %, last enriched timestamp)
