# Embeddings & Vector Search System

**Status**: Production Architecture  
**Date**: 2026-01-27  
**Category**: AI Systems & Architecture

---

## Executive Summary

The Embeddings System generates 6-task-specific embeddings using `gemini-embedding-001` (3072 dimensions) for semantic search, clustering, similarity matching, classification, Q&A, and fact-checking across the spine hierarchy.

**Architecture Decision**: Post-enrichment generation with task-specific embeddings stored in `spine.entity_embeddings`.

---

## Core Concepts

### Canonical Model

**ONLY USE**:
- **Model**: `gemini-embedding-001`
- **Dimensions**: 3072
- **Task Types**: Six distinct task types stored in separate columns
- **Storage**: `spine.entity_embeddings` with six embedding columns

**Forbidden Models**:
- ❌ `text-embedding-004` (deprecated, wrong dimensions)
- ❌ `text-embedding-005` (lower quality, wrong dimensions)
- ❌ Any other embedding model

**Reason**: Maintaining a single canonical embedding space ensures vector comparability, no fragmentation, consistent retrieval semantics, and a single distance metric/index.

---

## Mathematical Architecture

### 6-Task Embedding Architecture

All eligible entities get six embeddings stored in separate columns:

| Task Type | Column Name | Purpose |
|-----------|-------------|---------|
| **RETRIEVAL_DOCUMENT** | `embedding_retrieval` | Semantic search, RAG, document retrieval |
| **CLUSTERING** | `embedding_clustering` | Hierarchical spine construction (L4→L5→L6→L7→L8) |
| **SEMANTIC_SIMILARITY** | `embedding_similarity` | Cross-source moment detection (same concept across sources) |
| **CLASSIFICATION** | `embedding_classification` | Categorization, intent classification, labeling |
| **QUESTION_ANSWERING** | `embedding_qa` | Q&A matching, FAQ retrieval, answer extraction |
| **FACT_VERIFICATION** | `embedding_fact_check` | Fact-checking, claim verification, validation |

### Coverage Targets

**Entities That Get Embeddings**:
- **L8**: Conversations (all conversation types)
- **L5**: Messages (user, model_response, model_thinking, tool_result)
- **L4**: Sentences (all sentence types)

**Entities Excluded**:
- L1 (Tokens) - Too granular
- L2 (Words) - Too granular
- L3 (Spans) - Redundant with L4
- L6 (Turns) - Aggregated from L5
- L7 (Topic Segments) - Created later from clustering

---

## System Architecture

### Embedding Generation Flow

```
Enrichment Complete (Runs 0-14)
    ↓
Extract Eligible Entities (L8, L5, L4)
    ↓
Generate 6 Task-Specific Embeddings per Entity
    ↓
Store in spine.entity_embeddings
    ↓
Available for Vector Search, Clustering, Similarity
```

### Vector Search Architecture

**Storage**: `spine.entity_embeddings` table with:
- `entity_id` (links to `spine.entity_production`)
- `embedding_retrieval` (3072-dim vector)
- `embedding_clustering` (3072-dim vector)
- `embedding_similarity` (3072-dim vector)
- `embedding_classification` (3072-dim vector)
- `embedding_qa` (3072-dim vector)
- `embedding_fact_check` (3072-dim vector)

**Search Methods**:
- Cosine similarity for semantic search
- HDBSCAN for clustering
- KNN for similarity matching
- Classification models for categorization

---

## Meta Concepts

### Task-Specific Embeddings

Each task type optimizes for different operations:
- **Retrieval**: Optimized for document search and RAG
- **Clustering**: Optimized for hierarchical construction
- **Similarity**: Optimized for cross-source pattern matching
- **Classification**: Optimized for categorization
- **Q&A**: Optimized for question-answer matching
- **Fact Check**: Optimized for verification

### Post-Enrichment Generation

Embeddings are generated **after** enrichment runs complete:
- Enrichments provide context for better embeddings
- LLM enrichments inform semantic understanding
- Full context available for embedding generation

### Semantic Neighborhoods

Embeddings enable discovery of semantic neighborhoods:
- Similar concepts cluster together
- Cross-source patterns emerge
- Thematic relationships become visible

---

## Source References

**Primary Sources**:
- `data/services/knowledge/hold1/corpus/markdown/from_gcs/EMBEDDING_STRATEGY_CANONICAL_SPECIFICATION.md`
- `data/services/knowledge/hold1/corpus/markdown/from_gcs/EMBEDDINGS_VECTOR_SEARCH.md`
- `data/services/knowledge/hold1/corpus/markdown/from_gcs/EMBEDDING_BASED_CATEGORY_DISCOVERY.md`

**Related Concepts**:
- [Spine Structure](SPINE_STRUCTURE.md) - Embeddings generated at L4, L5, L8
- [Enrichments System](ENRICHMENTS_SYSTEM.md) - Embeddings generated after enrichment
- [AI Identity & Emergence](AI_IDENTITY_EMERGENCE.md) - L9 uses embeddings for domain discovery

---

## Key Takeaways

1. **6-Task Architecture**: Each entity gets 6 task-specific embeddings
2. **Canonical Model**: Only `gemini-embedding-001` (3072-dim)
3. **Post-Enrichment**: Generated after enrichment runs complete
4. **Level-Appropriate**: L4, L5, L8 get embeddings
5. **Vector Search**: Enables semantic search, clustering, similarity matching

---

*The Embeddings System provides semantic understanding and enables vector-based operations across the spine hierarchy.*
