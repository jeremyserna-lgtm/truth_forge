# Enrichments System

**Status**: Production Implementation  
**Date**: 2026-01-27  
**Category**: AI Systems & Architecture

---

## Executive Summary

The Enrichments System applies 25+ enrichment packages to conversation data across the spine hierarchy, providing multi-scale emotional, tonal, and semantic analysis. The system operates in three tiers (FAST, STANDARD, FULL) with spine-level aware routing.

**Current Status**: FAST tier operational (~30 msg/sec), STANDARD and FULL tiers defined for future implementation.

---

## Core Concepts

### Three-Tier Architecture

| Tier | Speed | Cost | Use Case |
|------|-------|------|----------|
| **FAST** | 30-40 msg/sec | $0.07 on AWS | Quick first-pass analysis |
| **STANDARD** | 5-10 msg/sec | $0.20 on AWS | Comprehensive psychological analysis |
| **FULL** | 1-2 msg/sec | $0.50+ on AWS | Research-grade analysis, full dataset insights |

### Spine-Level Enrichment Mapping

Enrichments are applied at specific spine levels:

| Level | Spine Layer | Sentiment | Embedding | Identity |
|-------|-------------|-----------|-----------|----------|
| L8 | Conversation | Yes (Aggregated) | Yes (Vertex AI) | Required |
| L7 | Topic Segment | Yes (Aggregated) | No | Required |
| L6 | Turn | Yes (Aggregated) | No | Required |
| L5 | Message | Yes | Yes (Vertex AI) | Required |
| L4 | Sentence | Yes | No | Required |
| L3 | Span | Yes | No | Required |
| L2 | Word | Yes | No | Required (Inherited) |
| L1 | Token | Yes | No | Required (Inherited) |

---

## Mathematical Architecture

### FAST Tier (Currently Implemented)

1. **vader** - Sentiment (compound, pos, neg, neu)
2. **textblob** - Polarity & subjectivity
3. **nrclex** - 10 emotion dimensions
4. **spacy_light** - Entities, POS tags (truncated to 1000 chars)
5. **basic_stats** - Char/word count, punctuation, etc.

**Speed**: ~30 msg/sec | **Time**: ~30 min for 50k messages

### STANDARD Tier (Defined)

All FAST features, plus:

6. **spacy_full** - Full NLP (no truncation, dependency parsing)
7. **detoxify** - Toxicity detection (6 metrics)
8. **keybert** - Keyword extraction
9. **goemotions** - 27 fine-grained emotions
10. **vad** - Valence, Arousal, Dominance
11. **politeness** - Politeness strategies
12. **certainty** - Certainty/hedging detection
13. **temporal_focus** - Past/present/future orientation
14. **coping** - Coping mechanisms
15. **stress_signals** - Stress/anxiety indicators
16. **sarcasm** - Sarcasm detection

**Speed**: 5-10 msg/sec | **Cost**: $0.20 on AWS

### FULL Tier (Defined)

All STANDARD features, plus:

17. **dialogue_acts** - Speech acts classification
18. **moral_foundations** - Moral reasoning (6 foundations)
19. **hate_speech** - Hate speech detection
20. **identity_refs** - Identity mentions (race, gender, etc.)
21. **pii_flags** - PII detection (names, emails, phone numbers)
22. **bertopic** - Dynamic topic modeling

**Speed**: 1-2 msg/sec | **Cost**: $0.50+ on AWS

---

## Enrichment Packages

### Core NLP (Linguistic Structure)

**spaCy (en_core_web_sm)**:
- **Variables**: 24 variables (token, word, phrase, document levels)
- **Operates On**: word, sentence, message levels
- **Features**: POS tagging, dependency parsing, NER, noun chunks

**TextBlob**:
- **Purpose**: Sentiment polarity and subjectivity
- **Operates On**: sentence, message, conversation levels
- **Features**: Polarity (-1 to +1), Subjectivity (0 to 1)

### Emotion Analysis

**NRCLex**:
- **Purpose**: 10 emotion dimensions
- **Operates On**: message, conversation levels
- **Emotions**: anger, fear, anticipation, trust, surprise, sadness, joy, disgust, sadness, positive, negative

**GoEmotions (RoBERTa)**:
- **Purpose**: 27 fine-grained emotions
- **Operates On**: sentence level
- **Model**: RoBERTa-based emotion classifier
- **Emotions**: admiration, amusement, anger, annoyance, approval, caring, confusion, curiosity, desire, disappointment, disapproval, disgust, embarrassment, excitement, fear, gratitude, grief, joy, love, nervousness, optimism, pride, realization, relief, remorse, sadness, surprise

### Sentiment Analysis

**VADER**:
- **Purpose**: Sentiment analysis optimized for social media
- **Features**: compound, pos, neg, neu scores
- **Range**: -1.0 to +1.0

### Keyword & Topic Extraction

**KeyBERT**:
- **Purpose**: Keyword extraction using BERT embeddings
- **Model**: all-MiniLM-L6-v2
- **Output**: Top keywords with relevance scores

**BERTopic**:
- **Purpose**: Dynamic topic modeling
- **Output**: Topic assignments with confidence

---

## Meta Concepts

### LLM-First Enrichment Strategy

**Principle**: Use LLMs (Gemini Flash/Pro) for enrichment before traditional NLP when:
- Context matters more than speed
- Semantic understanding required
- Multi-turn analysis needed

**Tier Structure**:
- **Tier 1**: Fast local NLP (spaCy, TextBlob, NRCLex)
- **Tier 2**: Flash (Gemini Flash 8B/1.5) — summarization, topic extraction
- **Tier 3**: Pro (Gemini Pro 1.5/2.0) — deep analysis, reasoning traces

### Spine-Level Awareness

Enrichments are routed by spine level:
- **L1-L3**: Word/span level — linguistic features
- **L4**: Sentence level — sentiment, emotions
- **L5**: Message level — comprehensive analysis
- **L6-L8**: Aggregated analysis

### Enrichment-to-Schema Mapping

Each enrichment package maps to specific schema fields:
- **Sentiment** → `enrichment.sentiment_*` fields
- **Emotions** → `enrichment.goemotions_*` or `enrichment.nrclex_*` fields
- **Keywords** → `enrichment.keybert_*` fields
- **Topics** → `enrichment.bertopic_*` fields

---

## Source References

**Primary Sources**:
- `data/services/knowledge/hold1/corpus/markdown/from_gcs/ENRICHMENT_PACKAGE_ANALYSIS.md`
- `data/services/knowledge/hold1/corpus/markdown/from_gcs/ENRICHMENT_TIERS.md`
- `data/services/knowledge/hold1/corpus/markdown/from_gcs/ENRICHMENT_TO_SCHEMA_MAPPING.md`
- `data/services/knowledge/hold1/corpus/markdown/from_gcs/CONVERSATION_ENRICHMENT_STRATEGY.md`

**Related Concepts**:
- [Spine Structure](SPINE_STRUCTURE.md) - Enrichment applied at spine levels
- [Embeddings System](EMBEDDINGS_SYSTEM.md) - Embeddings generated after enrichment
- [Conversation Processing](CONVERSATION_PROCESSING.md) - NLP pipeline integration

---

## Key Takeaways

1. **Three-Tier System**: FAST (operational), STANDARD (defined), FULL (defined)
2. **25+ Packages**: Comprehensive analysis capabilities
3. **Spine-Level Routing**: Enrichments applied at appropriate levels
4. **LLM-First Strategy**: Semantic understanding prioritized
5. **Cost-Speed Tradeoff**: Tiers balance speed vs. depth

---

*The Enrichments System provides multi-scale analysis across the spine hierarchy, enabling comprehensive understanding of conversation data.*
