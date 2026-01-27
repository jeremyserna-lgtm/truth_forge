# Enrichment Pipeline - Systematic Gap Closure

**Purpose**: Systematically close gaps in `spine.entity_enrichments` to increase analysis opportunities.

**Current State**: 4.62% entity coverage (548,892 of 11.9M entities), with many enrichment columns partially populated (~37%) or empty (0%).

**Strategy**: Idempotent enrichment scripts following BaseEnrichment pattern, organized by priority (P0→P1→P2→P3), with null-only mode to fill gaps incrementally.

---

## Architecture

### BaseEnrichment Pattern

All enrichment scripts extend `BaseEnrichment` which provides:
- Unified CLI (--mode, --level, --source, --limit, etc.)
- Idempotent gap-filling via `WHERE column IS NULL`
- Staging table writes (default) with promotion to production
- Batch processing with configurable batch sizes
- Progress tracking and dry-run support

### Three-Layer Architecture

```
entity_unified (read-only)
    ↓
staging_entity_enrichments (writes)
    ↓
entity_enrichments (production)
```

---

## Enrichment Scripts

### Phase 0: Foundation

- **`enrichment_triage.py`** - Flash-Lite triage for entity prioritization
- **`enrichment_coverage_expander.py`** - Create minimal enrichment rows to expand coverage

### Phase 1: P1 Backfills (Group A & B)

- **`enrichment_textblob.py`** - TextBlob sentiment (CPU-only)
- **`enrichment_textstat.py`** - TextStat readability (CPU-only)
- **`enrichment_nrclx.py`** - NRCLx emotions (CPU-only)
- **`enrichment_goemotions.py`** - GoEmotions classification (GPU recommended)
- **`enrichment_roberta_hate.py`** - RoBERTa hate speech detection (GPU recommended)

### Phase 2: P2 Completion (Group C & New)

- **`enrichment_keybert.py`** - KeyBERT keyword completion (embedding-based)
- **`enrichment_bertopic.py`** - BERTopic topic completion (embedding-based)
- **`enrichment_clustering.py`** - HDBSCAN clustering (embedding-based)
- **`enrichment_taxonomy.py`** - Taxonomy/domain/category population

### Phase 3: P3 Advanced Features

- **`enrichment_claims.py`** - Claims detection and Q&A role
- **`enrichment_resonance.py`** - Resonance pattern detection
- **`enrichment_fine_grained.py`** - Fine-grained identity linkage (span_id, word_id)
- **`enrichment_quality.py`** - Quality flags and metadata

### Phase 4: Orchestration

- **`orchestrator.py`** - Coordinate running multiple scripts
- **`monitor_coverage.py`** - Track coverage over time and generate reports

---

## Usage

### Individual Script

```bash
# Backfill TextBlob for L5/L8 entities
python pipelines/enrichment/enrichment_textblob.py --level 5,8 --mode null-only

# Overwrite all TextStat scores
python pipelines/enrichment/enrichment_textstat.py --mode overwrite

# Run with dry-run first
python pipelines/enrichment/enrichment_goemotions.py --dry-run --limit 100
```

### Using Orchestrator

```bash
# Run Phase 1 (P1 backfills)
python pipelines/enrichment/orchestrator.py --phase p1

# Run Group A (TextBlob + TextStat)
python pipelines/enrichment/orchestrator.py --group a

# Run all phases
python pipelines/enrichment/orchestrator.py --all

# Run with common arguments
python pipelines/enrichment/orchestrator.py --phase p1 --common-args "--limit 10000 --progress"
```

### Coverage Monitoring

```bash
# Generate markdown report
python pipelines/enrichment/monitor_coverage.py --output coverage_report.md

# Generate CSV report
python pipelines/enrichment/monitor_coverage.py --format csv --output coverage_report.csv

# Print to stdout
python pipelines/enrichment/monitor_coverage.py
```

### Coverage Expansion

```bash
# Expand to 50% coverage
python pipelines/enrichment/enrichment_coverage_expander.py --target-coverage 0.50

# Expand specific levels
python pipelines/enrichment/enrichment_coverage_expander.py --level 8,5 --limit 10000
```

---

## Common Arguments

All enrichment scripts support:

- `--mode {null-only,overwrite,append}` - Write mode (default: null-only)
- `--level 5,8` - Spine levels to process
- `--source claude_code` - Filter by source platform
- `--limit 1000` - Maximum entities to process
- `--offset 0` - Start from offset
- `--batch-size 1000` - Processing batch size
- `--write-batch-size 500` - Write batch size
- `--dry-run` - Show what would be processed
- `--verbose` - Enable verbose logging
- `--progress` - Show progress updates
- `--staging` - Write to staging (default)
- `--production` - Write directly to production
- `--use-existing-embedding` - Reuse existing embeddings (Group C)

---

## Dependencies

**Python packages**:
```bash
pip install textblob textstat nrclex transformers torch sentence-transformers keybert bertopic hdbscan google-cloud-bigquery
```

**Optional**:
- `google-generativeai` - For triage and claims detection
- `sklearn` - For resonance clustering (fallback)

---

## File Structure

```
pipelines/enrichment/
├── __init__.py
├── config.py                   # BigQuery config
├── utils.py                    # Shared utilities
├── base_enrichment.py          # BaseEnrichment class
├── orchestrator.py             # Coordination script
├── monitor_coverage.py         # Coverage tracking
├── enrichment_triage.py         # P0: Triage
├── enrichment_coverage_expander.py  # P0: Coverage expansion
├── enrichment_textblob.py      # P1: TextBlob
├── enrichment_textstat.py      # P1: TextStat
├── enrichment_nrclx.py         # P1: NRCLx
├── enrichment_goemotions.py    # P1: GoEmotions
├── enrichment_roberta_hate.py  # P1: RoBERTa
├── enrichment_keybert.py       # P2: KeyBERT
├── enrichment_bertopic.py      # P2: BERTopic
├── enrichment_clustering.py    # P2: Clustering
├── enrichment_taxonomy.py      # P2: Taxonomy
├── enrichment_claims.py        # P3: Claims
├── enrichment_resonance.py     # P3: Resonance
├── enrichment_fine_grained.py   # P3: Fine-grained
└── enrichment_quality.py      # P3: Quality
```

---

## Success Metrics

**Entity Coverage**:
- Target: Increase from 4.62% to 50%+ within 3 months
- Track by level, source, date

**Column Coverage**:
- P1 enrichments: 80%+ coverage (from ~37%)
- P2 enrichments: 50%+ coverage (from 0%)
- P3 enrichments: 30%+ coverage (from 0%)

---

## References

- **Gaps Report**: `docs/technical/enrichment/ENRICHMENT_COVERAGE_GAPS_REPORT.md`
- **Pipeline Architecture**: `docs/technical/architecture/pipelines/UNIFIED_ENRICHMENT_PIPELINE.md`
- **Plan**: `.cursor/plans/enrichment_gap_closure_plan_e48c2848.plan.md`
