# Complete Pipeline Architecture: End-to-End Flow

**Date**: 2026-01-28  
**Status**: ✅ **CODE READY - NOT YET DEPLOYED**  
**Purpose**: Comprehensive documentation of the complete data pipeline from source ingestion through entity_unified, enrichments, and embeddings

---

## Executive Summary

This document describes the complete end-to-end pipeline architecture that processes AI conversation data from 8 sources into a unified knowledge graph with enrichments and embeddings. The pipeline is **code-complete** and ready to deploy, but **not currently running**.

**Pipeline Status**:
- ✅ **Code Complete**: All pipeline code written and tested
- ⏸️ **Not Running**: Pipeline has not been deployed/executed yet
- ✅ **Ready to Deploy**: Can be run via Dataflow or scheduled queries

---

## Table of Contents

1. [Data Sources](#data-sources)
2. [Ingestion Layer](#ingestion-layer)
3. [Dataflow Pipeline](#dataflow-pipeline)
4. [entity_unified Table](#entity_unified-table)
5. [entity_enrichments Table](#entity_enrichments-table)
6. [entity_embeddings Table](#entity_embeddings-table)
7. [Complete Flow Diagram](#complete-flow-diagram)
8. [Deployment Status](#deployment-status)

---

## Data Sources

The pipeline supports **8 AI conversation sources**:

| Source | Type | Location | Sync Method |
|--------|------|----------|-------------|
| **claude_code** | Local files | `~/.claude/projects/` | Cron job → GCS |
| **claude_web** | Export files | GCS (manual upload) | Manual upload to GCS |
| **gemini_web** | Export files | GCS (manual upload) | Manual upload to GCS |
| **gemini_code** | Local files | Local directory | Sync script → GCS |
| **codex** | Local files | Local directory | Sync script → GCS |
| **copilot** | Local files | Local directory | Sync script → GCS |
| **grok_web** | Export files | GCS (manual upload) | Manual upload to GCS |
| **text_messages** | Database (Mac) | Local SQLite/DB | Export → GCS |

**GCS Bucket Structure**:
```
gs://claude_code_pipeline_source/
└── data_pipelines/
    └── ai_conversations/
        ├── claude_code/      ← Cron sync from ~/.claude/projects/
        ├── claude_web/       ← Manual upload
        ├── gemini_web/       ← Manual upload
        ├── gemini_code/      ← Sync script
        ├── codex/            ← Sync script
        ├── copilot/          ← Sync script
        ├── grok_web/         ← Manual upload
        └── text_messages/    ← Export → upload
```

---

## Ingestion Layer

### BigQuery External Tables

Each source has a BigQuery external table pointing to GCS:

| Source | External Table | GCS Path Pattern |
|--------|---------------|------------------|
| claude_code | `spine.claude_code_external` | `gs://.../ai_conversations/claude_code/*.jsonl` |
| claude_web | `spine.claude_web_external` | `gs://.../ai_conversations/claude_web/*.jsonl` |
| gemini_web | `spine.gemini_web_external` | `gs://.../ai_conversations/gemini_web/*.jsonl` |
| gemini_code | `spine.gemini_code_external` | `gs://.../ai_conversations/gemini_code/*.jsonl` |
| codex | `spine.codex_external` | `gs://.../ai_conversations/codex/*.jsonl` |
| copilot | `spine.copilot_external` | `gs://.../ai_conversations/copilot/*.jsonl` |
| grok_web | `spine.grok_web_external` | `gs://.../ai_conversations/grok_web/*.jsonl` |
| text_messages | `spine.text_messages_external` | `gs://.../ai_conversations/text_messages/*.jsonl` |

**Status**: ✅ **All external tables created**

---

## Dataflow Pipeline

### Overview

**File**: `pipelines/adapters/claude_code/dataflow_pipeline.py`  
**Status**: ✅ **Code Complete - Ready to Run**  
**Runner**: Apache Beam / Google Cloud Dataflow

### Pipeline Flow

```
1. Extract
   ↓
2. THE GATE (Identity Generation)
   ↓
3. Gemini Flash Lite (Spelling Correction - User Messages Only)
   ↓
4. L5 Messages (entity_unified rows)
   ↓
5. L4 Sentences (spaCy segmentation on cleaned text)
   ↓
6. L8 Conversations (one per conversation_id)
   ↓
7. Write to entity_unified
```

### Critical Ordering Rules

**⚠️ CRITICAL**: Spelling correction **MUST** happen **BEFORE** spaCy:

1. **L5 Messages** are already the unit of analysis (from source data)
2. **Gemini Flash Lite** cleans spelling/grammar for user messages only
   - Model: `gemini-2.0-flash-lite` (cost-effective)
   - Prompt: Simple spelling-only prompt (preserves meaning for sentiment analysis)
   - **No Python spelling packages** (they mutilate text)
3. **spaCy** runs on **cleaned text** to create L4 sentences
4. **L5 → L4/L3/L2** happens when spaCy processes the cleaned L5 text

### Processing Details

**Spelling Correction**:
- **Model**: `gemini-2.0-flash-lite`
- **Prompt**: "Clean the spelling of this text. Do not change the meaning. We use this for sentiment analysis and must preserve intent and tone."
- **Scope**: User messages only (`role='user'`)
- **Output**: 
  - Cleaned text → `text` column
  - Original text → `metadata.text_original`

**THE GATE (Identity Service)**:
- Generates deterministic `entity_id` and `conversation_id`
- Format: `msg:{conversation_hash}:{sequence}`
- Must run **before** text cleaning (so IDs are stable)

**spaCy Processing**:
- Model: `en_core_web_sm`
- Segments cleaned L5 text into L4 sentences
- Creates sentence entities with proper hierarchy

### Levels Emitted

| Level | Entity Type | How Created | Notes |
|-------|------------|-------------|-------|
| **L4** | Sentences | spaCy segmentation of cleaned L5 text | Primary NLP unit |
| **L5** | Messages | Source data (already L5-level) | Main entity type |
| **L8** | Conversations | Aggregated from L5 messages | One per conversation_id |

**Not Produced by Pipeline**:
- L1 (Tokens) - Removed from pipeline
- L2 (Words) - Not produced (can be added later)
- L3 (Spans) - Not produced (can be added later)
- L6 (Turns) - Not produced (can be added later)
- L7 (Topics) - Not produced (can be added later)

### Usage

```bash
# Run for a specific source
python dataflow_pipeline.py --source claude_code
python dataflow_pipeline.py --source gemini_web
python dataflow_pipeline.py --source text_messages
```

---

## entity_unified Table

### Overview

**Table**: `spine.entity_unified`  
**Purpose**: Unified production table for all entities (L2–L8)  
**Schema**: 34 columns  
**Partitioning**: By `content_date` (DAY)  
**Clustering**: `['level', 'conversation_id', 'entity_id']`

### Complete Schema (34 Fields)

#### Identity Fields
- `entity_id` (STRING) - Primary identifier
- `level` (INTEGER) - Hierarchy level (L2–L8)
- `entity_type` (STRING) - Type classification
- `entity_mode` (STRING) - Entity state
- `parent_id` (STRING) - Parent in hierarchy

#### Hierarchical ID Fields
- `conversation_id` (STRING) - L8 identifier
- `topic_segment_id` (STRING) - L7 identifier
- `turn_id` (STRING) - L6 identifier
- `message_id` (STRING) - L5 identifier
- `sentence_id` (STRING) - L4 identifier
- `span_id` (STRING) - L3 identifier
- `word_id` (STRING) - L2 identifier

#### Source Fields
- `source_pipeline` (STRING) - Pipeline name
- `source_file` (STRING) - Source file path
- `source_file_path` (STRING) - Full path
- `source_system` (STRING) - Source system
- `source_ids` (REPEATED STRING) - Array of source IDs

#### Content Fields
- `text` (STRING) - **Cleaned text** (spelling corrected)
- `canonical_form` (STRING) - Normalized form
- `persona` (STRING) - Persona identifier

#### Metadata Field
- `metadata` (JSON) - **All enrichment data**:
  - `text_original` - Original text (before cleaning)
  - `role`, `message_type`, `message_index`
  - `cleaning_applied`, `cleaning_changes`
  - All other enrichment fields

#### Timestamp Fields
- `content_date` (DATE) - Partitioning field
- `source_message_timestamp` (TIMESTAMP)
- `created_at`, `updated_at` (TIMESTAMP)
- `ingestion_timestamp` (TIMESTAMP)
- `ingestion_job_id` (STRING)

#### Validation Fields
- `validation_status` (STRING)

#### Count Rollup Fields
- `l7_count`, `l6_count`, `l5_count`, `l4_count`, `l3_count`, `l2_count` (INTEGER)

### Data Flow

**From Dataflow Pipeline**:
- L4 sentences (from spaCy)
- L5 messages (from source data, cleaned)
- L8 conversations (aggregated)

**Text Handling**:
- `text` column: **Cleaned text** (spelling corrected by Gemini Flash Lite)
- `metadata.text_original`: **Original text** (preserved for reference)

---

## entity_enrichments Table

### Overview

**Table**: `spine.entity_enrichments`  
**Purpose**: Stores enrichment data (textblob, textstat, nrclex, goemotions, etc.)  
**Key**: `entity_id` (links to `entity_unified.entity_id`)  
**Status**: ✅ **Schema Ready - Enrichments Run Separately**

### Enrichment Types

#### 1. TextBlob (Sentiment & Subjectivity)
- `textblob_polarity` (FLOAT64) - Sentiment (-1 to 1)
- `textblob_subjectivity` (FLOAT64) - Subjectivity (0 to 1)
- `textblob_version` (STRING)

#### 2. TextStat (Readability Metrics)
- `textstat_flesch_reading_ease` (FLOAT64)
- `textstat_flesch_kincaid_grade` (FLOAT64)
- `textstat_gunning_fog` (FLOAT64)
- `textstat_smog_index` (FLOAT64)
- `textstat_automated_readability_index` (FLOAT64)
- `textstat_coleman_liau_index` (FLOAT64)
- `textstat_linsear_write_formula` (FLOAT64)
- `textstat_dale_chall_readability_score` (FLOAT64)
- `textstat_difficult_words` (INT64)
- `textstat_syllable_count` (INT64)
- `textstat_lexicon_count` (INT64)
- `textstat_sentence_count` (INT64)
- `textstat_char_count` (INT64)
- `textstat_version` (STRING)

#### 3. NRCLx (Emotions)
- `nrclx_emotions` (JSON) - Full emotion scores
- `nrclx_top_emotion` (STRING) - Primary emotion
- `nrclx_top_count` (INT64) - Top emotion count
- `nrclx_version` (STRING)

#### 4. GoEmotions (Emotion Classification)
- `goemotions_scores` (JSON) - All emotion scores
- `goemotions_top_emotions` (ARRAY<STRING>) - Top emotions
- `goemotions_primary_emotion` (STRING) - Primary emotion
- `goemotions_primary_score` (FLOAT64) - Confidence
- `goemotions_model` (STRING)
- `goemotions_version` (STRING)

#### 5. KeyBERT (Keyword Extraction)
- `keybert_top_keyword` (STRING)
- `keybert_top_score` (FLOAT64)
- `keybert_top_5_keywords` (ARRAY<STRING>)
- `keybert_all_keywords` (JSON)

#### 6. BERTopic (Topic Modeling)
- `bertopic_topic_id` (INT64)
- `bertopic_topic_probability` (FLOAT64)
- `bertopic_topic_words` (ARRAY<STRING>)

#### 7. RoBERTa Hate Speech Detection
- `roberta_hate_label` (STRING)
- `roberta_hate_score` (FLOAT64)

#### 8. Small Embeddings (For GPU Enrichments Only)
- `sentence_embedding` (ARRAY<FLOAT64) - **Small embeddings for GPU enrichments**
- `sentence_embedding_model` (STRING)
- **⚠️ NOTE**: These are **NOT** for similarity search. They're only for GPU-based enrichments (GoEmotions, KeyBERT, etc.)
- **⚠️ CRITICAL**: GPU enrichments **must run locally** - Google Cloud doesn't provide GPU access. These will be generated on local Mac Studios with GPUs.

### Enrichment Generation Flow

```
entity_unified (entities ready)
    ↓
Enrichment Scripts Run (separate from pipeline)
    ├─→ TextBlob (CPU - can run anywhere)
    ├─→ TextStat (CPU - can run anywhere)
    ├─→ NRCLx (CPU - can run anywhere)
    ├─→ GoEmotions (GPU - MUST run locally)
    ├─→ KeyBERT (GPU - MUST run locally)
    ├─→ BERTopic (GPU - MUST run locally)
    └─→ RoBERTa Hate (GPU - MUST run locally)
    ↓
entity_enrichments (enrichment data stored)
```

**Scripts**: `pipelines/enrichment/enrichment_*.py`

**⚠️ CRITICAL**: GPU enrichments (GoEmotions, KeyBERT, BERTopic, RoBERTa) **must run on local hardware** with GPUs. Google Cloud does not provide GPU access. These will be processed on Mac Studios with GPUs.

---

## entity_embeddings Table

### Overview

**Table**: `spine.entity_embeddings`  
**Purpose**: Stores vector embeddings for semantic search and similarity  
**Key**: `entity_id` (links to `entity_unified.entity_id`)  
**Status**: ✅ **Schema Ready - Embeddings Generated Post-Enrichment**

### Embedding Types

#### Cloud Embeddings (Gemini 001)

**Model**: `gemini-embedding-001`  
**Dimensions**: **3072**  
**Purpose**: Cloud-based semantic search, similarity, clustering  
**Storage**: BigQuery `entity_embeddings` table

**6 Task-Specific Embeddings** (all 3072-dim):

| Task Type | Column Name | Purpose |
|-----------|-------------|---------|
| RETRIEVAL_DOCUMENT | `embedding_retrieval` | Semantic search, RAG, document retrieval |
| CLUSTERING | `embedding_clustering` | Hierarchical spine construction |
| SEMANTIC_SIMILARITY | `embedding_similarity` | Cross-source moment detection |
| CLASSIFICATION | `embedding_classification` | Categorization, intent classification |
| QUESTION_ANSWERING | `embedding_qa` | Q&A matching, FAQ retrieval |
| FACT_VERIFICATION | `embedding_fact_check` | Fact-checking, claim verification |

**Coverage**: L4 (sentences), L5 (messages), L8 (conversations)

#### Local Embeddings

**Model**: `BAAI/bge-large-en-v1.5` (or Scout/Ollama on new computer)  
**Dimensions**: **1024**  
**Purpose**: Local semantic search, similarity matching  
**Storage**: Local (DuckDB, NPZ files)

**Use Cases**:
- Registry similarity check
- Document deduplication
- Local-only operations

**⚠️ CRITICAL RULE**: 
- **Never compare 3072-dim to 1024-dim embeddings**
- Cloud operations → Cloud embeddings (3072)
- Local operations → Local embeddings (1024)

### Embedding Generation Flow

```
entity_unified (entities ready)
    ↓
entity_enrichments (enrichments complete)
    ↓
Embedding Generation (post-enrichment)
    ├─→ Cloud: Gemini 001 (3072-dim) → entity_embeddings
    └─→ Local: BGE/Scout (1024-dim) → Local storage
    ↓
Available for Vector Search
```

**Why Post-Enrichment?**
- Enrichments provide context for better embeddings
- LLM enrichments inform semantic understanding
- Full context available for embedding generation

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ DATA SOURCES (8 sources)                                        │
│ claude_code, claude_web, gemini_web, gemini_code, codex,        │
│ copilot, grok_web, text_messages                                │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ GCS BUCKET                                                      │
│ gs://claude_code_pipeline_source/data_pipelines/ai_conversations/│
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ BIGQUERY EXTERNAL TABLES                                        │
│ spine.{source}_external (8 tables)                             │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ DATAFLOW PIPELINE                                               │
│ 1. Extract                                                      │
│ 2. THE GATE (entity_id, conversation_id)                        │
│ 3. Gemini Flash Lite (spelling correction - user messages only)│
│ 4. L5 Messages (cleaned text in text, original in metadata)   │
│ 5. L4 Sentences (spaCy on cleaned text)                         │
│ 6. L8 Conversations (aggregated)                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ entity_unified (34 columns)                                     │
│ - L4, L5, L8 entities                                           │
│ - Cleaned text in text column                                   │
│ - Original text in metadata.text_original                        │
└──────┬───────────────────────────────────────┬──────────────────┘
       │                                       │
       ↓                                       ↓
┌──────────────────────────┐      ┌──────────────────────────────┐
│ entity_enrichments       │      │ entity_embeddings            │
│                          │      │                              │
│ - TextBlob               │      │ Cloud (Gemini 001):          │
│ - TextStat               │      │ - 3072-dim embeddings        │
│ - NRCLx                  │      │ - 6 task-specific columns   │
│ - GoEmotions             │      │                              │
│ - KeyBERT                │      │ Local (BGE/Scout):           │
│ - BERTopic               │      │ - 1024-dim embeddings        │
│ - RoBERTa Hate           │      │ - Local storage              │
│ - Small embeddings       │      │                              │
│   (for GPU enrichments)  │      │                              │
└──────────────────────────┘      └──────────────────────────────┘
```

---

## Deployment Status

### Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Dataflow Pipeline Code** | ✅ Complete | Ready to run |
| **External Tables** | ✅ Created | All 8 sources |
| **entity_unified Schema** | ✅ Ready | 34 columns defined |
| **entity_enrichments Schema** | ✅ Ready | All enrichment columns defined |
| **entity_embeddings Schema** | ✅ Ready | Cloud + local embeddings defined |
| **Pipeline Execution** | ⏸️ Not Running | Code ready, not deployed |
| **Scheduled Jobs** | ❌ Not Created | Need to set up |

### What's Ready

✅ **Code Complete**:
- Multi-source Dataflow pipeline
- Spelling correction (Gemini Flash Lite)
- THE GATE integration
- spaCy sentence segmentation
- entity_unified row generation

✅ **Infrastructure Ready**:
- BigQuery external tables
- GCS bucket structure
- Dataflow API enabled

✅ **Documentation**:
- Pipeline code documented
- Schema specifications complete
- This comprehensive document

### What's Needed to Deploy

1. **Run Dataflow Pipeline**:
   ```bash
   cd pipelines/adapters/claude_code
   python dataflow_pipeline.py --source claude_code
   ```

2. **Set Up Sync Scripts** (for local file sources):
   - claude_code: ✅ Cron job exists
   - gemini_code, codex, copilot: Need sync scripts
   - text_messages: Need export → GCS script

3. **Create Scheduled Jobs** (optional):
   - BigQuery scheduled queries
   - Cloud Scheduler triggers

4. **Run Enrichments** (after entity_unified populated):
   ```bash
   python pipelines/enrichment/enrichment_textblob.py
   python pipelines/enrichment/enrichment_textstat.py
   # etc.
   ```

5. **Generate Embeddings** (after enrichments complete):
   - Cloud: Gemini 001 (3072-dim) → entity_embeddings
   - Local: BGE/Scout (1024-dim) → Local storage

---

## Key Design Decisions

### 1. Spelling Correction Before spaCy

**Decision**: Gemini Flash Lite spelling correction **MUST** run before spaCy.

**Reason**: 
- Python spelling packages mutilate text
- LLM correction preserves meaning (critical for sentiment analysis)
- Cleaned text must be used for all downstream NLP (spaCy, enrichments)

**Implementation**: 
- Simple prompt: "Clean the spelling. Do not change the meaning."
- Only user messages (`role='user'`)
- Original text preserved in `metadata.text_original`

### 2. L5 Messages Are Already Units

**Decision**: Messages from sources are already L5-level units.

**Reason**: 
- No need to "create" L5 - they exist in source data
- Pipeline splits L5 into L4/L3/L2 using cleaned text

### 3. Two Embedding Systems

**Decision**: Separate cloud (3072-dim) and local (1024-dim) embeddings.

**Reason**:
- Cloud: High-quality semantic search (Gemini 001)
- Local: Cost-effective local operations (BGE/Scout)
- Never mix dimensions (3072 ≠ 1024)

### 4. Small Embeddings in Enrichments

**Decision**: Small embeddings in `entity_enrichments` are **only** for GPU enrichments.

**Reason**:
- GoEmotions, KeyBERT, BERTopic need embeddings for processing
- These are **NOT** for similarity search
- Similarity search uses `entity_embeddings` (3072-dim cloud or 1024-dim local)

---

## Next Steps

1. **Deploy Pipeline**: Run Dataflow pipeline for each source
2. **Verify Data**: Check entity_unified has correct data
3. **Run Enrichments**: Execute enrichment scripts
4. **Generate Embeddings**: Create cloud and local embeddings
5. **Monitor**: Set up monitoring and alerts

---

**Last Updated**: 2026-01-28  
**Status**: ✅ **Code Complete - Ready to Deploy**  
**Test Coverage**: ✅ **Tests Created** - See `TEST_COVERAGE_PLAN.md` for coverage details

---

## Testing

**Test File**: `tests/unit/pipelines/test_dataflow_pipeline.py`  
**Coverage Target**: 95% (per user requirement)  
**Standard**: 90% minimum (per framework standards)

**Test Coverage**:
- ✅ Multi-source support (all 8 sources)
- ✅ Extract functions
- ✅ THE GATE identity generation
- ✅ Gemini Flash Lite spelling correction
- ✅ spaCy sentence segmentation
- ✅ Entity creation (L4, L5, L8)
- ✅ entity_unified row builder
- ✅ Error handling

**Run Tests**:
```bash
.venv/bin/pytest tests/unit/pipelines/test_dataflow_pipeline.py -v
```

**Check Coverage**:
```bash
.venv/bin/pytest tests/unit/pipelines/test_dataflow_pipeline.py \
  --cov=pipelines/adapters/claude_code/dataflow_pipeline \
  --cov-report=term-missing
```
