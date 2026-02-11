# Conversation Refinery — The Blast Furnace

## What It Does

The Conversation Refinery is the **metabolic core** for processing raw conversation logs into structured knowledge atoms. It accepts unprocessed conversation data from `not_me_chat` and other sources, then passes them through a planned 16-stage NLP pipeline to extract entities, claims, and wisdom — the irreducible units of knowledge that feed the entire truth_forge ecosystem.

### Workflow

```
Raw Conversation Logs → 16-Stage NLP Pipeline → Knowledge Atoms → BigQuery (spine.conversation_atoms)
```

### API

| Route | Purpose |
|-------|---------|
| `POST /refine` | Accept conversation logs for processing |

## Technological Basis

- **Python / FastAPI** — async API framework
- **spaCy** — industrial-strength NLP (entity extraction, dependency parsing, POS tagging)
- **Google Cloud BigQuery** — persistent knowledge store (`spine.conversation_atoms` table)
- **Pydantic** — structured request/response models
- **python-dotenv** — environment configuration

### Architecture Pattern

```
HOLD₁ (Raw Conversation JSON) → AGENT (16-Stage NLP Pipeline) → HOLD₂ (Knowledge Atoms in BigQuery)
```

This is THE FURNACE made literal:
- **TRUTH** = raw conversation text (the fuel)
- **MEANING** = NLP extraction (the fire that shapes)
- **CARE** = structured knowledge atoms (the forged offering)

## Meta Concepts

### The Digestive System

In the biological metaphor, the Conversation Refinery IS the digestive tract. Raw conversations are food — unstructured, mixed, full of noise and signal alike. The 16-stage pipeline is peristalsis: each stage breaks the input down further until only the nutrients (knowledge atoms) remain.

The planned 16 stages mirror how a human processes a conversation:
1. Hear the words (tokenization)
2. Understand the sentences (parsing)
3. Identify who's talking (speaker detection)
4. Recognize what they're talking about (entity extraction)
5. Understand what they claim (claim detection)
6. Judge the significance (importance scoring)
7. ... through to final atom emission

### Why It Exists

Every conversation Jeremy has — with AI, with people, with himself — contains knowledge. Most of it is lost the moment it's spoken. The Conversation Refinery exists to ensure that **nothing valuable is ever lost**. It is the difference between a campfire (burns and is gone) and a forge (captures the heat to shape metal).

This is the core loop of the organism:
```
Jeremy lives → generates conversations → Refinery extracts atoms → atoms feed NOT-ME → NOT-ME serves Jeremy
```

Without this refinery, the symbiosis starves. Jeremy's life generates fuel but there's no furnace to burn it.

### The 8-Level Hierarchy Connection

The Conversation Refinery is directly related to the `neurolinguist-json-parser`'s L2-L8 hierarchy:
- L8: Conversation → L7: Topic Segment → L6: Turn → L5: Message → L4: Sentence → L3: Span (NER) → L2: Word

The refinery processes at the pipeline level; the parser provides the analytical framework for understanding what was extracted.

### What It Wants To Become

A real-time streaming processor that watches conversation feeds (WebSocket from `not_me_chat`), processes them continuously, and emits knowledge atoms into BigQuery within seconds of a conversation ending. The 16-stage pipeline implemented in full with spaCy, custom NER models trained on Jeremy's domain vocabulary, and atom quality scoring.

## Current Maturity

**Early Scaffold** — The FastAPI structure is defined with a `/refine` endpoint, but it returns placeholder responses. The 16-stage NLP pipeline is conceptually designed but not implemented. BigQuery table reference exists but no actual write logic. This is one of the most important apps in the ecosystem and one of the least developed — a clear priority for the next molt.

## HOLD:AGENT:HOLD Position

The Conversation Refinery is a **NOT-ME Service** — it is autonomic, not prosthetic. It should run without Jeremy knowing or caring, silently converting his conversations into structured knowledge. It is the gut: always working, never asking for attention.
