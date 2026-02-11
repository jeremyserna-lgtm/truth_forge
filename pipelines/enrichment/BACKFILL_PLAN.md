# Entity Enrichments Backfill Plan

**Date**: 2026-02-01  
**Status**: Planning  
**Target**: Close all enrichment coverage gaps systematically

---

## Current State Summary

| Metric | Current | Target |
|--------|---------|--------|
| **Entity Coverage** | 4.62% (548K / 11.9M) | 50% → 100% |
| **Sentiment (TextBlob)** | 37% of enriched | 100% |
| **Emotions (NRCLx/GoEmotions)** | 36-37% of enriched | 100% |
| **Readability (TextStat)** | 37% of enriched | 100% |
| **Keywords (KeyBERT)** | Partial (top_5 only) | Complete |
| **Topics (BERTopic)** | Partial (words only) | Complete |
| **Clustering** | 0% | 100% |
| **Taxonomy/Domain** | 0% | 100% |
| **Claims/QA Role** | 0% | 100% |
| **Resonance** | 0% | 100% |
| **Span/Word Linkage** | 0% | L2/L3 entities |

---

## Gap Categories

### Category A: Coverage Expansion (P0)
**Problem**: Only 4.62% of entities have enrichment rows  
**Scripts**: `enrichment_triage.py`, `enrichment_coverage_expander.py`

| Task | Entities | Priority |
|------|----------|----------|
| Create enrichment rows for L5 messages | ~2M | P0 |
| Create enrichment rows for L4 sentences | ~5M | P0 |
| Create enrichment rows for L8 conversations | ~50K | P0 |
| Create enrichment rows for L6 turns | ~500K | P1 |
| Create enrichment rows for L7 topic segments | ~200K | P1 |

### Category B: Backfill Existing Nulls (P1)
**Problem**: ~63% of enriched entities have null sentiment/emotion/readability  
**Scripts**: `enrichment_textblob.py`, `enrichment_textstat.py`, `enrichment_nrclx.py`, `enrichment_goemotions.py`, `enrichment_roberta_hate.py`

| Column Family | Current Coverage | Gap Count | Script |
|---------------|-----------------|-----------|--------|
| `textblob_*` | 37% | ~346K | `enrichment_textblob.py` |
| `textstat_*` | 37% | ~346K | `enrichment_textstat.py` |
| `nrclx_*` | 36.5% | ~348K | `enrichment_nrclx.py` |
| `goemotions_*` | 36% | ~351K | `enrichment_goemotions.py` |
| `roberta_hate_*` | 36% | ~351K | `enrichment_roberta_hate.py` |

### Category C: Field Completion (P2)
**Problem**: Some enrichment families have partial data (list exists, scalar missing)  
**Scripts**: `enrichment_keybert.py`, `enrichment_bertopic.py`

| Field | Has | Missing | Action |
|-------|-----|---------|--------|
| `keybert_top_5_keywords` | ✅ 100% | - | - |
| `keybert_top_keyword` | ❌ 0% | 548K | Extract from top_5 |
| `keybert_top_score` | ❌ 0% | 548K | Compute from keywords |
| `keybert_all_keywords` | ❌ 0% | 548K | Optional expansion |
| `bertopic_topic_words` | ✅ 100% | - | - |
| `bertopic_topic_id` | ❌ 0% | 548K | Assign from model |
| `bertopic_topic_probability` | ❌ 0% | 548K | Compute from model |

### Category D: New Enrichments (P2/P3)
**Problem**: Entire enrichment families at 0%  
**Scripts**: `enrichment_clustering.py`, `enrichment_taxonomy.py`, `enrichment_claims.py`, `enrichment_resonance.py`

| Family | Coverage | Unlocks |
|--------|----------|---------|
| **Clustering** (`cluster_*`) | 0% | Cluster-based analysis, cohort discovery |
| **Taxonomy** (`domain`, `content_type`, `primary_category`) | 0% | Domain filtering, category analytics |
| **Claims** (`is_claim`, `claim_type`, `qa_role`) | 0% | Fact-checking, Q&A structure |
| **Resonance** (`resonance_*`) | 0% | Pattern/theme tracking, Total Resonance |

### Category E: Fine-Grained Linkage (P3)
**Problem**: L2/L3 entities have no enrichment linkage  
**Script**: `enrichment_fine_grained.py`

| Field | Purpose | Action |
|-------|---------|--------|
| `span_id` | Link to L3 spans | Populate from hierarchy |
| `word_id` | Link to L2 words | Populate from hierarchy |

---

## Execution Plan

### Phase 0: Coverage Expansion (Week 1)
**Goal**: Get from 4.62% to 25% entity coverage

```bash
# Step 0.1: Triage high-value entities
python pipelines/enrichment/enrichment_triage.py --level 5,8 --limit 500000

# Step 0.2: Expand coverage to L5 messages
python pipelines/enrichment/enrichment_coverage_expander.py --level 5 --limit 1000000

# Step 0.3: Expand coverage to L4 sentences
python pipelines/enrichment/enrichment_coverage_expander.py --level 4 --limit 2000000

# Step 0.4: Expand coverage to L8 conversations
python pipelines/enrichment/enrichment_coverage_expander.py --level 8 --limit 50000
```

### Phase 1: P1 Backfills (Week 2)
**Goal**: Fill all null sentiment/emotion/readability in existing enriched entities

```bash
# Group A: CPU-only (can run anywhere)
python pipelines/enrichment/enrichment_textblob.py --mode null-only --progress
python pipelines/enrichment/enrichment_textstat.py --mode null-only --progress
python pipelines/enrichment/enrichment_nrclx.py --mode null-only --progress

# Group B: GPU-recommended (local Mac Studio)
python pipelines/enrichment/enrichment_goemotions.py --mode null-only --batch-size 64 --progress
python pipelines/enrichment/enrichment_roberta_hate.py --mode null-only --batch-size 64 --progress
```

### Phase 2: P2 Completion (Week 3)
**Goal**: Complete KeyBERT/BERTopic fields, add clustering/taxonomy

```bash
# KeyBERT field completion
python pipelines/enrichment/enrichment_keybert.py --mode complete-fields --progress

# BERTopic field completion
python pipelines/enrichment/enrichment_bertopic.py --mode complete-fields --progress

# Clustering (requires embeddings)
python pipelines/enrichment/enrichment_clustering.py --mode null-only --progress

# Taxonomy population
python pipelines/enrichment/enrichment_taxonomy.py --mode null-only --progress
```

### Phase 3: P3 Advanced (Week 4)
**Goal**: Claims, resonance, fine-grained, quality

```bash
# Claims detection and Q&A role
python pipelines/enrichment/enrichment_claims.py --mode null-only --progress

# Resonance pattern detection
python pipelines/enrichment/enrichment_resonance.py --mode null-only --progress

# Fine-grained linkage (span_id, word_id)
python pipelines/enrichment/enrichment_fine_grained.py --mode null-only --progress

# Quality flags
python pipelines/enrichment/enrichment_quality.py --mode null-only --progress
```

### Phase 4: Sovereign Architecture (Week 5)
**Goal**: Add Sovereign-specific enrichments from LLM Refinery

These are NEW enrichment types defined in `pipelines/llm_refinery/enrichments.py`:

| Enrichment Class | Fields | Script Needed |
|------------------|--------|---------------|
| `CognitiveStageEnrichment` | `cognitive_stage`, `stage_polarity`, banned/manifestation vocab | **NEW** |
| `StruggleFilterEnrichment` | `struggle_pattern_type`, `swimming_score`, `drowning_score`, `training_weight`, `arc_position`, `resistance_value` | **EXISTS** (v2.0 Experiential Integration) |
| `MetabolicStageEnrichment` | `metabolic_stage`, insight_level, care_type | **NEW** |
| `ConfidenceCalibrationEnrichment` | `confidence_level`, hedging, uncertainty | **NEW** |
| `SourceAttributionEnrichment` | ME/NOT-ME detection, voice classification | **NEW** |
| `TemporalLensEnrichment` | past/present/future orientation | **NEW** |
| `OperationalCycleEnrichment` | SEE:SEE:DO:DONE phase tracking | **NEW** |
| `JeremyArcEnrichment` | thought_type, mode, behavioral_pattern | **NEW** |
| `TotalResonanceEnrichment` | Full resonance tracking (23 fields) | **NEW** |

**Action**: Create new enrichment scripts for Sovereign Architecture fields.

---

## Resource Requirements

### Compute
| Phase | CPU Hours | GPU Hours | Notes |
|-------|-----------|-----------|-------|
| P0 Coverage | 10-20 | 0 | BigQuery reads + minimal writes |
| P1 Backfills | 20-40 | 10-20 | GoEmotions/RoBERTa need GPU |
| P2 Completion | 10-20 | 20-40 | Clustering/embedding ops |
| P3 Advanced | 10-20 | 10-20 | Some LLM calls |
| P4 Sovereign | 20-40 | 0-10 | LLM-based classification |

### Storage
- Current `entity_enrichments`: ~1.8 GB
- At 50% coverage: ~20 GB estimated
- At 100% coverage: ~40 GB estimated

### Cost Estimates
| Resource | Unit Cost | Estimated Units | Total |
|----------|-----------|-----------------|-------|
| BigQuery reads | $5/TB | ~5 TB | $25 |
| BigQuery writes | $0.05/GB | ~40 GB | $2 |
| Gemini embedding API | $0.00004/1K chars | ~100M chars | $4 |
| Local GPU time | $0 (owned) | ~100 hours | $0 |
| **Total** | | | **~$31** |

---

## Monitoring

### Daily Coverage Check

```bash
python pipelines/enrichment/monitor_coverage.py --output reports/coverage_$(date +%Y%m%d).json
```

### Key Metrics to Track

| Metric | Current | Week 1 Target | Week 4 Target |
|--------|---------|---------------|---------------|
| Entity coverage % | 4.62% | 25% | 75% |
| TextBlob coverage % | 37% | 80% | 100% |
| Clustering coverage % | 0% | 0% | 80% |
| Resonance coverage % | 0% | 0% | 50% |

---

## Dependencies

```
embeddings ─────────────────────────────────────┐
                                                │
entity_unified ──► coverage_expander ──► triage │
                         │                      │
                         ▼                      │
                 enrichment rows                │
                         │                      │
         ┌───────────────┼───────────────┐      │
         ▼               ▼               ▼      ▼
    textblob         textstat         nrclx  clustering
    goemotions       roberta_hate            bertopic
         │               │               │      │
         └───────────────┼───────────────┘      │
                         ▼                      │
                      claims                    │
                      taxonomy                  │
                      resonance ◄───────────────┘
                         │
                         ▼
                  fine_grained
                     quality
```

---

## Validation Checklist

After each phase:

- [ ] Run coverage monitor
- [ ] Check for null counts in target columns
- [ ] Verify staging → production promotion
- [ ] Spot-check sample entities
- [ ] Update this document with actual results

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits | Slow embedding generation | Batch requests, exponential backoff |
| GPU memory overflow | Crash on large batches | Reduce batch size, chunk processing |
| Data inconsistency | Broken joins | Validate entity_id linkage after writes |
| Cost overrun | Budget exceeded | Set hard limits, monitor daily |
| Schema drift | Breaking changes | Lock schema, version enrichment models |

---

## Scripts to Create

The following NEW enrichment scripts are needed for Sovereign Architecture:

```
pipelines/enrichment/
├── enrichment_cognitive_stage.py     # Kegan 1-5 classification
├── enrichment_struggle_filter.py     # ✅ COMPLETE (v2.0 Experiential Integration Protocol)
├── enrichment_metabolic.py           # TRUTH:MEANING:CARE tracking
├── enrichment_confidence.py          # Confidence calibration
├── enrichment_source_attribution.py  # ME/NOT-ME detection
├── enrichment_temporal.py            # Past/present/future lens
├── enrichment_operational_cycle.py   # SEE:SEE:DO:DONE tracking
├── enrichment_jeremy_arc.py          # Jeremy Arc test metrics
└── enrichment_total_resonance.py     # Full resonance tracking
```

---

## Next Steps

1. **Immediate**: Run Phase 0 coverage expansion
2. **This Week**: Complete Phase 1 backfills
3. **Next Week**: Phase 2 + begin Phase 3
4. **Month 1**: Complete Phase 4 (Sovereign enrichments)
5. **Ongoing**: Monitor coverage, iterate on gaps

---

## References

- [ENRICHMENT_COVERAGE_GAPS_REPORT.md](../../docs/technical/enrichment/ENRICHMENT_COVERAGE_GAPS_REPORT.md)
- [COMPLETE_PIPELINE_ARCHITECTURE.md](../../docs/technical/infrastructure/COMPLETE_PIPELINE_ARCHITECTURE.md)
- [LLM Refinery enrichments.py](../llm_refinery/enrichments.py)
- [BaseEnrichment pattern](./base_enrichment.py)
