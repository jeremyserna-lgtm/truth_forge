# Entity Enrichments Coverage & Gaps Report

**Date**: 2026-01-27  
**Source**: `spine.entity_enrichments`  
**Purpose**: Identify coverage gaps and actions needed to unlock analysis opportunities.

---

## Executive Summary

| Metric | Value |
|--------|--------|
| **Total entities** (`entity_unified`) | 11,875,341 |
| **Enriched entities** | 548,892 |
| **Entity-level coverage** | **4.62%** |
| **Table size** | ~1.8 GB |
| **Schema fields** | 91 |

**Key finding**: Only ~4.6% of entities have enrichments. Most analysis opportunities are constrained by low entity coverage and by many enrichment columns having zero or partial population.

---

## 1. Column Coverage Summary

### 1.1 Excellent (≥ 80%)

| Column | Coverage | Notes |
|--------|----------|--------|
| `source_ids` | 100% | Always populated |
| `sentence_embedding` | 100% | Embeddings present for all enriched rows |
| `keybert_top_5_keywords` | 100% | Keyword list populated |
| `bertopic_topic_words` | 100% | Topic words populated |
| `goemotions_top_emotions` | 100% | Top emotions populated |
| `enrichment_text` | 99.6% | Text used for enrichment |
| `source_platform` | 99.6% | Source attribution |
| `entity_type` | 98.0% | Entity type |
| `conversation_id` | 98.0% | Conversation linkage |
| `message_id` | 98.0% | Message linkage |
| `source_message_timestamp` | 98.0% | Timestamp |
| `metadata` | 98.0% | Metadata JSON |
| `entity_mode` | 88.2% | Structural / conceptual / translated |
| `parent_id` | 88.2% | Hierarchy |
| `turn_id` | 88.2% | Turn linkage |
| `sentence_id` | 88.2% | Sentence linkage |
| `source_file_path` | 88.2% | File path |
| `source_system` | 88.2% | System source |
| `topic_segment_id` | 86.9% | Topic segment |

**Analysis opportunities today**: Source/platform analysis, embedding-based similarity, keyword/topic exploration, conversation/turn structure, hierarchy.

---

### 1.2 Partial (20–50%)

| Column / family | Coverage | Notes |
|-----------------|----------|--------|
| **TextBlob** | ~36.9% | `textblob_polarity`, `textblob_subjectivity` |
| **TextStat** | ~36.9% | `textstat_flesch_reading_ease`, `textstat_flesch_kincaid_grade`, `textstat_gunning_fog`, `textstat_smog_index`, `textstat_automated_readability_index`, `textstat_coleman_liau_index`, `textstat_linsear_write_formula`, `textstat_dale_chall_readability_score`, `textstat_difficult_words`, `textstat_syllable_count`, `textstat_lexicon_count`, `textstat_sentence_count`, `textstat_char_count` |
| **NRCLx emotions** | ~36.5–36.7% | `nrclx_emotions`, `nrclx_top_emotion` (24.3%), `nrclx_top_count` |
| **Sentence embeddings** | ~35.9% | `sentence_embedding_model`, `sentence_embedding_computed_at` |
| **GoEmotions** | ~36.1–36.4% | `goemotions_scores`, `goemotions_primary_emotion`, `goemotions_primary_score`, `goemotions_enriched_at`, `goemotions_model` |
| **RoBERTa hate** | ~36.4% | `roberta_hate_label`, `roberta_hate_score`, `roberta_hate_enriched_at`, `roberta_hate_model` |
| `enrichment_batch_id` | 20.0% | Batch attribution |

**Gap**: Sentiment, readability, emotion, and hate-speech analyses are only possible over ~37% of enriched entities. Trends and comparisons will be biased toward that subset.

---

### 1.3 Low or Zero (< 20%)

| Column | Coverage | Notes |
|--------|----------|--------|
| `span_id` | 0% | No span-level linkage |
| `word_id` | 0% | No word-level linkage |
| `source_file` | 0% | Not populated (use `source_file_path`) |
| `cluster_id` | 0% | Clustering not in use |
| `cluster_label` | 0% | |
| `cluster_confidence` | 0% | |
| `primary_category` | 0% | No category taxonomy |
| `category_path` | 0% | |
| `content_type` | 0% | |
| `domain` | 0% | No domain tagging in enrichments |
| `resonance_group_id` | 0% | Resonance logic not populated |
| `resonance_score` | 0% | |
| `qa_role` | 0% | Q&A role not set |
| `is_claim` | 0% | Claim detection not used |
| `claim_type` | 0% | |
| `keybert_top_keyword` | 0% | Single top keyword not populated |
| `keybert_top_score` | 0% | |
| `keybert_all_keywords` | 0% | Full keyword set not stored |
| `keybert_enriched_at` | 0% | |
| `keybert_version` | 0% | |
| `bertopic_topic_id` | 0% | Topic IDs not stored |
| `bertopic_topic_probability` | 0% | Topic probabilities not stored |
| `bertopic_enriched_at` | 0% | |
| `bertopic_model_id` | 0% | |
| `enrichment_metadata` | 0% | Not used |
| `role` | 10.1% | User/assistant role sparse |
| `enrichment_quality_flags` | 5.7% | Quality flags rarely set |

**Gap**: No cluster/category/domain/claim/resonance-based analysis. Keyword and topic models exist in partial form (e.g. `keybert_top_5_keywords`, `bertopic_topic_words`) but richer KeyBERT/BERTopic outputs are missing.

---

## 2. Gaps by Analysis Opportunity

### 2.1 Entity-level coverage (4.62%)

**Gap**: Enrichments exist for only 548,892 of 11,875,341 entities.

**To complete**:
- Expand enrichment pipeline to more entities (prioritize by level, source, date).
- Define and implement triage (e.g. Flash-Lite) so high-value entities are enriched first.
- Track coverage over time (e.g. by `source_platform`, `entity_type`, `level`).

**Unlocks**: Representative sentiment, emotion, readability, and keyword analyses across the full spine.

---

### 2.2 Sentiment & emotion

**Gap**: TextBlob sentiment ~37%. NRCLx and GoEmotions emotions ~36–37%. Many entities have no sentiment/emotion.

**To complete**:
- Run TextBlob (and optionally other sentiment) on all enriched entities.
- Backfill NRCLx / GoEmotions where missing.
- Ensure `nrclx_top_emotion` is set whenever `nrclx_emotions` exists.

**Unlocks**: Sentiment and emotion trends, polarity shifts, emotion distribution by source/platform/conversation.

---

### 2.3 Readability & text complexity

**Gap**: All TextStat metrics ~37%.

**To complete**:
- Run TextStat (or equivalent) on all enriched entities.
- Persist full set of readability columns.

**Unlocks**: Readability trends, complexity by source/level, content-quality metrics.

---

### 2.4 Keywords & topics

**Gap**: `keybert_top_5_keywords` and `bertopic_topic_words` are full; `keybert_top_keyword`, `keybert_top_score`, `keybert_all_keywords`, `bertopic_topic_id`, `bertopic_topic_probability` are empty.

**To complete**:
- Populate `keybert_top_keyword`, `keybert_top_score`, and optionally `keybert_all_keywords` from KeyBERT runs.
- Populate `bertopic_topic_id`, `bertopic_topic_probability`, and model/version metadata from BERTopic.

**Unlocks**: Single-keyword filters, topic-based cohort analysis, topic trends over time.

---

### 2.5 Clustering & taxonomy

**Gap**: `cluster_id`, `cluster_label`, `cluster_confidence`, `primary_category`, `category_path`, `content_type`, `domain` are empty.

**To complete**:
- Run clustering (e.g. HDBSCAN on embeddings) and write `cluster_*`.
- Define taxonomy and map entities to `primary_category` / `category_path`.
- Populate `content_type` and `domain` from metadata or upstream pipeline.

**Unlocks**: Cluster-level analysis, category and domain breakdowns, cross-domain comparisons.

---

### 2.6 Claims & Q&A structure

**Gap**: `is_claim`, `claim_type`, `qa_role` are empty.

**To complete**:
- Add claim-detection step (e.g. LLM or classifier) and write `is_claim`, `claim_type`.
- Set `qa_role` from conversation structure (user/assistant/system).

**Unlocks**: Claim-centric analysis, Q&A role–based filtering, fact-checking workflows.

---

### 2.7 Fine-grained identity & resonance

**Gap**: `span_id`, `word_id` unused; `resonance_group_id`, `resonance_score` empty.

**To complete**:
- Add span/word-level enrichment where needed (e.g. for L2/L3).
- Implement resonance logic and persist `resonance_group_id`, `resonance_score`.

**Unlocks**: Span/word-level analytics, resonance and repetition analysis.

---

### 2.8 Quality & traceability

**Gap**: `enrichment_quality_flags` 5.7%; `enrichment_metadata` empty; no `enrichment_type` column.

**To complete**:
- Define quality flags and set them in the enrichment pipeline.
- Use `enrichment_metadata` for run-specific or model-specific info.
- Consider adding `enrichment_type` (or similar) for enrichment source/run type.

**Unlocks**: Quality filtering, debugging, and enrichment lineage.

---

## 3. Prioritized Completion Checklist

| Priority | Area | Actions |
|----------|------|--------|
| **P0** | Entity coverage | Increase % of entities enriched; add triage; monitor coverage by source/level. |
| **P1** | Sentiment / emotion | Backfill TextBlob, NRCLx, GoEmotions to all enriched entities; fix `nrclx_top_emotion`. |
| **P1** | Readability | Backfill TextStat to all enriched entities. |
| **P2** | Keywords / topics | Populate KeyBERT and BERTopic ID/score/probability columns. |
| **P2** | Clustering & taxonomy | Add clustering; define categories; populate `domain` / `content_type`. |
| **P3** | Claims & Q&A | Add claim detection; set `qa_role`. |
| **P3** | Resonance & fine-grained | Implement resonance; add span/word linkage where needed. |
| **P3** | Quality & metadata | Use `enrichment_quality_flags` and `enrichment_metadata`; add `enrichment_type` if desired. |

---

## 4. How to Re-run Coverage Analysis

```bash
cd /Users/jeremyserna/truth_forge
source .venv/bin/activate
cd mcp-servers/spine-analysis-mcp
python scripts/analyze_enrichment_coverage.py
```

Optionally, use the MCP tool `get_enrichment_coverage` (when configured) for on-demand coverage snapshots.

---

## 5. References

- **Enrichment schema** (conceptual): `SCHEMA_ENRICHMENT_RUNS_UNIFIED.md`, `TRUTH_ENGINE_COMPLETE_SPECIFICATION.md`
- **Spine tables**: `entity_unified`, `entity_enrichments`, `entity_embeddings`
- **Coverage script**: `mcp-servers/spine-analysis-mcp/scripts/analyze_enrichment_coverage.py`
