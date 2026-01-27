# Conversation Data Processing & NLP

**Status**: Production Pipeline  
**Date**: 2026-01-27  
**Category**: Processing & Analysis

---

## Executive Summary

The Conversation Processing system applies natural language processing (NLP) techniques to conversation data, enabling multi-scale analysis from word-level to conversation-level. The system processes AI conversations (ChatGPT, Claude, Gemini) and SMS messages through a unified analytical hierarchy.

**Core Pipeline**: GCS Source → Shredder → BigQuery Staging → Production → Embeddings → Topic Segmentation → Enrichment → Analysis

---

## Core Concepts

### Unified Analytical Hierarchy

The system creates a **unified analytical hierarchy** that works across all data types:

1. **Sentence Level**: Individual sentences within messages
   - Fine-grained linguistic analysis
   - NLP processing (spaCy, sentiment, emotions)

2. **Paragraph Level**: Logical groupings of sentences within messages
   - Thematic analysis within messages
   - Text segmentation and topic modeling

3. **Message Level**: Individual messages (SMS) or turns (AI conversations)
   - Message-level content and sentiment analysis
   - Current Truth Engine enrichment (25+ fields)

4. **Turn Level**: Speaker turns in conversations (back-and-forth exchanges)
   - Interaction dynamics and conversation flow
   - Group messages by speaker transitions

5. **Conversation Level**: Complete conversation units (AI sessions, SMS bursts)
   - High-level patterns, outcomes, relationship analysis
   - Conversation tagging schema

---

## Mathematical Architecture

### NLP Processing Pipeline

**Stage 1: Shredder (Tier 2)**
- spaCy + spaCy-TextBlob + textstat + pyspellchecker + Presidio
- Field normalization, POS, noun chunks, NER
- Baseline sentiment, readability, typo rate, PII signals

**Stage 2: Enrichment (Tier 1-3)**
- **Tier 1**: NRCLex, spaCy, Detoxify, KeyBERT (sentiment, NER, keywords)
- **Tier 2**: Flash (Gemini Flash 8B/1.5) — summarization, topic extraction
- **Tier 3**: Pro (Gemini Pro 1.5/2.0) — deep analysis, reasoning traces

**Stage 3: Embedding**
- Generate 3072-dim embeddings (gemini-embedding-001)
- Write to `enrichment.agent_embeddings`

### Message-Level Enrichment

**Baseline enrichment packages**:

| Package | Feature Key | Value Type | Description | Example Value |
|---------|-------------|------------|-------------|---------------|
| VADER | `sentiment.vader.compound` | float | Compound sentiment score | -0.65 to +0.95 |
| TextBlob | `sentiment.textblob.polarity` | float | Polarity (-1 to +1) | -0.5 to +0.8 |
| TextBlob | `sentiment.textblob.subjectivity` | float | Subjectivity (0 to 1) | 0.3 to 0.9 |
| NRCLex | `emotions.nrclex.*` | dict | 10 emotion dimensions | anger, fear, joy, etc. |
| spaCy | `nlp.spacy.entities` | list | Named entities | Person, Org, Location |
| spaCy | `nlp.spacy.noun_chunks` | list | Noun phrases | "the system", "user input" |

### Conversation-Level Enrichment

**Aggregated analysis**:
- Overall sentiment trends
- Topic classification
- Emotion distribution
- Keyword frequency
- Conversation outcomes

---

## Meta Concepts

### Data Type Adaptations

**AI Coding Conversations**:
- Structured conversation threads with clear turn boundaries
- Enrichment Focus: Technical collaboration, task success, code quality

**AI Chat Conversations**:
- Structured conversation threads with clear turn boundaries
- Enrichment Focus: Emotional processing, life planning, decision making

**SMS Messages**:
- Flat list of messages without conversation structure
- Turn Detection: Group by time gaps and participant changes
- Conversation Boundaries: Burst detection (messages within time window)
- Enrichment Focus: Relationship dynamics, communication patterns

### The Core Pipeline

```
GCS Source → Shredder (Tier 2) → BigQuery Staging → Production (Trinity)
→ Embeddings → L7 Topic Segmentation → Enrichment (Basic/Advanced)
→ Conceptual L5/L7 (embeddings clustering) → Translated L5/L7 (Gemini)
→ Analysis Service (on-demand)
```

---

## Source References

**Primary Sources**:
- `data/services/knowledge/hold1/corpus/markdown/from_gcs/conversation_pipeline_core.md`
- `data/services/knowledge/hold1/corpus/markdown/from_gcs/CONVERSATION_ENRICHMENT_STRATEGY.md`
- `data/services/knowledge/hold1/corpus/markdown/from_gcs/UNIFIED_ANALYTICAL_HIERARCHY.md`

**Related Concepts**:
- [Spine Structure](SPINE_STRUCTURE.md) - Processing follows spine hierarchy
- [Enrichments System](ENRICHMENTS_SYSTEM.md) - NLP enrichments applied
- [Embeddings System](EMBEDDINGS_SYSTEM.md) - Semantic embeddings generated

---

## Key Takeaways

1. **Unified Hierarchy**: Works across AI conversations and SMS
2. **Multi-Scale Analysis**: Sentence → Paragraph → Message → Turn → Conversation
3. **25+ Enrichment Fields**: Comprehensive NLP analysis
4. **Pipeline Architecture**: Structured processing from source to analysis
5. **Data Type Aware**: Adapts to different conversation structures

---

*The Conversation Processing system provides comprehensive NLP analysis across multiple scales and data types.*
