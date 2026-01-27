# Spine Structure: L1-L12 Hierarchical Architecture

**Status**: Production Architecture  
**Date**: 2026-01-27  
**Category**: AI Systems & Architecture

---

## Executive Summary

The Spine Structure is a 12-level hierarchical decomposition system that processes conversation data from atomic tokens (L1) to emergent identity (L12). It provides multi-resolution analysis, enabling both structural understanding (L1-L8) and emergent discovery (L9-L12).

**SPINE = Structured Psychological Intelligence Navigation Engine**

---

## Core Concepts

### The Two-Tier Architecture

**L1-L8: Structural Hierarchy (What Was Said)**
- Hierarchical decomposition of conversations
- Parent/child relationships
- Denormalization chain

**L9-L12: Emergent Discovery (What It Means)**
- ML-enhanced discovery
- Pattern recognition across conversations
- Identity synthesis

---

## Mathematical Architecture

### L1-L8: Structural Levels

| Level | Entity Type | Parent | What It Contains |
|-------|-------------|--------|------------------|
| **L8** | Conversation | NULL | Entire conversation |
| **L7** | Topic Segment | conversation_id | Thematic segments (created later) |
| **L6** | Turn | conversation_id | User/assistant exchange pair |
| **L5** | Message | turn_id | Single message from user or assistant |
| **L4** | Sentence | message_id | spaCy sentence boundary |
| **L3** | Span | sentence_id | Noun chunks, named entities |
| **L2** | Word | sentence_id | Content words, non-punctuation tokens |
| **L1** | Token | word_id OR sentence_id | All spaCy tokens including punctuation |

### L9-L12: Emergent Intelligence

| Level | Discovery Method | What It Discovers |
|-------|------------------|-------------------|
| **L9** | HDBSCAN clustering on L8 embeddings | Domain (thematic clusters) |
| **L10** | GMM with timestamps/metadata + Speech Acts | Context (communicative context) |
| **L11** | PELT changepoint detection + Phase Transitions | Phase (temporal transitions) |
| **L12** | Weighted rollup + Identity Signals | Identity (unified synthesis) |

---

## Parent/Child Relationships

**Key Principles**:
1. Every entity has exactly ONE direct parent (except L8 which has NULL)
2. L7 is NEVER used as a parent_id (no entity has parent_id = topic_segment_id)
3. Words (L2) belong to sentences (L4), not spans (L3)
4. Tokens (L1) belong to words (L2) if they're word tokens, otherwise to sentences (L4) for punctuation

### Denormalization Chain

Each level inherits metadata from parent levels, creating a denormalization chain that enables efficient querying at any resolution.

---

## Enrichment Strategy

### Spine-Level Enrichment Mapping

| Level | Spine Layer | Sentiment Analysis | Embedding Generation | Identity Attribution |
|-------|-------------|-------------------|---------------------|---------------------|
| L8 | Document/Conversation | Yes (Aggregated) | **Yes (Vertex AI)** | **Required** |
| L7 | Topic-Segment | Yes (Aggregated) | No | **Required** |
| L6 | Section/Turn | Yes (Aggregated) | No | **Required** |
| L5 | Paragraph/Message | Yes | **Yes (Vertex AI)** | **Required** |
| L4 | Sentence | Yes | No | **Required** |
| L3 | Span | Yes | No | **Required** |
| L2 | Word | Yes | No | **Required** (Inherited) |
| L1 | Token | Yes | No | **Required** (Inherited) |

**Enrichment Details**:
- **Sentiment Analysis**: Applied at every level from token up to conversation
- **Embedding Generation**: Performed using **Google Vertex AI** at L8 and L5
- **Identity Attribution**: Required at all levels, inherited at lower levels

---

## Meta Concepts

### The Tri-Modal Architecture

The spine operates across three modes:
1. **Structural**: L1-L8 decomposition (what was said)
2. **Conceptual**: Clustered representations (what it means)
3. **Translated**: LLM-enhanced understanding (how to express it)

### Multi-Resolution Analysis

The spine enables analysis at multiple resolutions:
- **Fine-grained**: Word-level sentiment, token-level POS tags
- **Medium-grained**: Message-level topics, turn-level dynamics
- **Coarse-grained**: Conversation-level themes, domain-level patterns

### Emergent Discovery

L9-L12 layers discover patterns that emerge across multiple conversations:
- **L9 Domains**: Thematic clusters across conversations
- **L10 Contexts**: Communicative contexts enhanced with speech acts
- **L11 Phases**: Temporal transitions detected via changepoint analysis
- **L12 Identity**: Unified synthesis of all levels into identity representation

---

## Source References

**Primary Sources**:
- `data/services/knowledge/hold1/corpus/markdown/from_gcs/SPINE_METADATA_STRUCTURE.md`
- `data/services/knowledge/hold1/corpus/markdown/from_gcs/UNIVERSAL_SPINE_ARCHITECTURE.md`
- `data/services/knowledge/hold1/corpus/markdown/from_gcs/TRIMODAL_SPINE_ARCHITECTURE_CANONICAL_SPECIFICATION.md`
- `data/services/knowledge/hold1/corpus/markdown/from_gcs/SPINE_LEVELS_REFERENCE.md`

**Related Concepts**:
- [Enrichments System](ENRICHMENTS_SYSTEM.md) - Enrichment applied at spine levels
- [Embeddings System](EMBEDDINGS_SYSTEM.md) - Embeddings generated at L5 and L8
- [AI Identity & Emergence](AI_IDENTITY_EMERGENCE.md) - L9-L12 emergent intelligence

---

## Key Takeaways

1. **12-Level Hierarchy**: From tokens (L1) to identity (L12)
2. **Two-Tier Architecture**: Structural (L1-L8) and Emergent (L9-L12)
3. **Parent/Child Relationships**: Strict hierarchy with denormalization
4. **Multi-Resolution Analysis**: Query at any level of granularity
5. **ML-Enhanced Discovery**: L9-L12 use ML models for pattern discovery

---

*The Spine Structure is the foundational architecture for processing and understanding conversation data at multiple resolutions.*
