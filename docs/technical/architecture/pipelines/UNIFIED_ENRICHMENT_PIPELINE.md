# Unified Enrichment Pipeline Architecture

## Overview

This document describes the **three-layer enrichment architecture** for processing entities from `entity_unified` through staging to production enrichments.

**Enrichment Stack:**
- **Group A (CPU-only):** TextBlob (sentiment), textstat (readability)
- **Group B (Classification):** GoEmotions (27 emotions), RoBERTa Hate (toxicity)
- **Group C (Embedding-based):** KeyBERT (keywords), BERTopic (topics) - share sentence-transformers embedding

**Key Principle:** Each enrichment can run **alone** or in **groups**. Scripts are idempotent and fill gaps via `WHERE column IS NULL`.

---

## Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SOURCE PIPELINES (ChatGPT, Browser, Email, etc.)                           │
│  Each ends at its own Stage N → promotes to entity_unified                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ENTITY_UNIFIED (Production Spine)                                          │
│  - All sources converge here (L1-L8 structure stable)                       │
│  - Deduplication enforced                                                   │
│  - READ-ONLY for enrichments                                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ enrichment scripts read
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGING_ENTITY_ENRICHMENTS                                                 │
│  - Each script writes to ITS columns only                                   │
│  - Safe to overwrite (staging)                                              │
│  - Schema grows as enrichments grow                                         │
│  - WHERE column IS NULL → fill gaps                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ promotion decision
┌─────────────────────────────────────────────────────────────────────────────┐
│  ENTITY_ENRICHMENTS (Production)                                            │
│  - Validated, complete enrichments                                          │
│  - Query surface for downstream                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Enrichment Groups

| Group | Scripts | Shared Resource | Run Alone? | Run Together? |
|-------|---------|-----------------|------------|---------------|
| **A** | TextBlob, textstat | None (CPU-only) | ✅ | ✅ |
| **B** | GoEmotions, RoBERTa | None (own forward pass) | ✅ | ✅ |
| **C** | KeyBERT, BERTopic | sentence-transformer embedding | ✅ | ✅ |

**Group C Note:** If BERTopic ran first, `sentence_embedding` column is populated → KeyBERT can use it without recomputing.

---

## CLI Architecture

All enrichment scripts follow a **unified CLI pattern** for maximum flexibility.

### Universal CLI Options

```bash
python enrichment_script.py [OPTIONS]

# What to enrich
--enrichment {textblob,textstat,goemotions,roberta,keybert,bertopic,embedding}
--group {a,b,c,all}              # Run entire group

# Write mode
--mode {null-only,overwrite,append}
    null-only (default): Only WHERE column IS NULL
    overwrite: Overwrite ALL matching entities
    append: Insert new, skip existing

# Entity filtering
--level 5,8                       # Which levels (default: 5,8)
--source chatgpt_web              # Filter by source
--entity-ids file.txt             # Specific entity IDs from file

# Batch control
--limit 10000                     # Process N entities (0 = all)
--offset 0                        # Start from offset
--batch-size 1000                 # Batch size for processing
--write-batch-size 500            # Batch size for writes

# Output control
--dry-run                         # Show what would be processed
--verbose                         # Detailed logging
--progress                        # Show progress bar

# Table control
--staging                         # Write to staging (default)
--production                      # Write directly to production (dangerous)
--table-suffix _dev               # Use dev tables

# Reuse existing data
--use-existing-embedding          # Use sentence_embedding if present (for Group C)
--skip-if-any-enriched           # Skip entity if ANY enrichment exists
```

### Example Commands

```bash
# Fill in missing TextBlob enrichments for L5/L8
python enrichment_textblob.py --mode null-only --level 5,8

# Overwrite ALL textstat scores (recalculate everything)
python enrichment_textstat.py --mode overwrite

# Run TextBlob + textstat together on null columns
python enrichment_group_a.py --mode null-only

# Run GoEmotions on first 1000 entities (testing)
python enrichment_goemotions.py --limit 1000 --dry-run

# Run KeyBERT using existing embeddings from BERTopic run
python enrichment_keybert.py --use-existing-embedding

# Run only on ChatGPT data
python enrichment_roberta.py --source chatgpt_web

# Force overwrite specific entities
python enrichment_textblob.py --entity-ids bad_entities.txt --mode overwrite
```

---

## Script Implementation Pattern

### Base Enrichment Class

```python
#!/usr/bin/env python3
"""
Base class for all enrichment scripts.
Provides unified CLI, BigQuery integration, and write patterns.
"""

import argparse
from abc import ABC, abstractmethod
from google.cloud import bigquery
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseEnrichment(ABC):
    """Base class for all enrichment scripts."""

    # Override in subclass
    ENRICHMENT_NAME = "base"
    COLUMNS_OWNED = []  # Columns this enrichment writes to
    REQUIRES_EMBEDDING = False

    def __init__(self):
        self.client = bigquery.Client()
        self.args = self.parse_args()

    def parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description=f"Enrichment: {self.ENRICHMENT_NAME}"
        )

        # Write mode
        parser.add_argument(
            "--mode",
            choices=["null-only", "overwrite", "append"],
            default="null-only",
            help="Write mode: null-only (default), overwrite, append"
        )

        # Entity filtering
        parser.add_argument(
            "--level",
            type=str,
            default="5,8",
            help="Entity levels to process (comma-separated)"
        )
        parser.add_argument(
            "--source",
            type=str,
            help="Filter by source (e.g., chatgpt_web)"
        )
        parser.add_argument(
            "--entity-ids",
            type=str,
            help="File containing specific entity IDs to process"
        )

        # Batch control
        parser.add_argument("--limit", type=int, default=0)
        parser.add_argument("--offset", type=int, default=0)
        parser.add_argument("--batch-size", type=int, default=1000)
        parser.add_argument("--write-batch-size", type=int, default=500)

        # Output control
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--verbose", action="store_true")
        parser.add_argument("--progress", action="store_true")

        # Table control
        parser.add_argument("--staging", action="store_true", default=True)
        parser.add_argument("--production", action="store_true")
        parser.add_argument("--table-suffix", type=str, default="")

        # Embedding reuse
        parser.add_argument("--use-existing-embedding", action="store_true")

        return parser.parse_args()

    def build_query(self) -> str:
        """Build query to find entities needing enrichment."""
        levels = [int(l) for l in self.args.level.split(",")]

        # Base query
        query = f"""
        SELECT e.entity_id, e.text, e.level, e.source
        """

        # Add existing embedding if needed and requested
        if self.REQUIRES_EMBEDDING and self.args.use_existing_embedding:
            query += ", s.sentence_embedding"

        query += f"""
        FROM `project.spine.entity_unified` e
        LEFT JOIN `project.spine.staging_entity_enrichments` s
            ON e.entity_id = s.entity_id
        WHERE e.level IN ({','.join(str(l) for l in levels)})
          AND e.text IS NOT NULL
          AND LENGTH(e.text) > 10
        """

        # Mode-specific WHERE clause
        if self.args.mode == "null-only":
            # Only entities missing THIS enrichment
            null_checks = " OR ".join(
                f"s.{col} IS NULL" for col in self.COLUMNS_OWNED
            )
            query += f" AND (s.entity_id IS NULL OR {null_checks})"
        # overwrite mode: no additional filter (process all)

        # Source filter
        if self.args.source:
            query += f" AND e.source = '{self.args.source}'"

        # Limit/offset
        if self.args.limit > 0:
            query += f" LIMIT {self.args.limit}"
        if self.args.offset > 0:
            query += f" OFFSET {self.args.offset}"

        return query

    @abstractmethod
    def compute_enrichment(self, text: str, existing_embedding: Optional[List[float]] = None) -> Dict[str, Any]:
        """Compute enrichment for a single text. Override in subclass."""
        pass

    def run(self):
        """Main execution flow."""
        # Build query
        query = self.build_query()

        if self.args.dry_run:
            print(f"DRY RUN - Would execute:\n{query}")
            # Count matching entities
            count_query = query.replace("SELECT e.entity_id, e.text", "SELECT COUNT(*)")
            result = list(self.client.query(count_query).result())[0][0]
            print(f"Would process {result:,} entities")
            return

        # Execute query
        print(f"Querying entities for {self.ENRICHMENT_NAME}...")
        results = list(self.client.query(query).result())
        print(f"Found {len(results):,} entities to enrich")

        if not results:
            print("Nothing to process.")
            return

        # Process in batches
        enriched = []
        for i, row in enumerate(results):
            existing_emb = getattr(row, 'sentence_embedding', None) if self.args.use_existing_embedding else None
            result = self.compute_enrichment(row.text, existing_emb)
            result['entity_id'] = row.entity_id
            enriched.append(result)

            # Write batch
            if len(enriched) >= self.args.write_batch_size:
                self.write_batch(enriched)
                enriched = []

            if self.args.progress and i % 100 == 0:
                print(f"Progress: {i+1}/{len(results)}")

        # Write remaining
        if enriched:
            self.write_batch(enriched)

        print(f"Enrichment complete: {len(results):,} entities processed")

    def write_batch(self, enriched: List[Dict[str, Any]]):
        """Write enriched batch to staging table."""
        table_id = "project.spine.staging_entity_enrichments"
        if self.args.table_suffix:
            table_id += self.args.table_suffix

        # MERGE to update existing or insert new
        # Build SET clause for only our columns
        set_clause = ", ".join(f"{col} = source.{col}" for col in self.COLUMNS_OWNED)
        set_clause += f", {self.ENRICHMENT_NAME}_enriched_at = CURRENT_TIMESTAMP()"

        # Build INSERT columns
        insert_cols = ["entity_id"] + self.COLUMNS_OWNED + [f"{self.ENRICHMENT_NAME}_enriched_at"]

        # Execute MERGE
        # (Implementation details omitted for brevity)
        pass
```

### TextBlob Enrichment Example

```python
#!/usr/bin/env python3
"""TextBlob sentiment enrichment script."""

from textblob import TextBlob
from base_enrichment import BaseEnrichment

class TextBlobEnrichment(BaseEnrichment):
    ENRICHMENT_NAME = "textblob"
    COLUMNS_OWNED = ["textblob_polarity", "textblob_subjectivity"]
    REQUIRES_EMBEDDING = False

    def compute_enrichment(self, text: str, existing_embedding=None) -> dict:
        blob = TextBlob(text)
        return {
            "textblob_polarity": blob.sentiment.polarity,
            "textblob_subjectivity": blob.sentiment.subjectivity,
            "textblob_version": "0.17.1"
        }

if __name__ == "__main__":
    TextBlobEnrichment().run()
```

### KeyBERT Enrichment Example (Uses Embedding)

```python
#!/usr/bin/env python3
"""KeyBERT keyword extraction enrichment script."""

import json
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from base_enrichment import BaseEnrichment

class KeyBERTEnrichment(BaseEnrichment):
    ENRICHMENT_NAME = "keybert"
    COLUMNS_OWNED = ["keybert_keywords", "keybert_top_keyword", "sentence_embedding"]
    REQUIRES_EMBEDDING = True

    def __init__(self):
        super().__init__()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.keybert = KeyBERT(model=self.embedding_model)

    def compute_enrichment(self, text: str, existing_embedding=None) -> dict:
        # Use existing embedding or compute new
        if existing_embedding is not None:
            embedding = existing_embedding
        else:
            embedding = self.embedding_model.encode(text).tolist()

        # Extract keywords using embedding
        keywords = self.keybert.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            top_n=5,
            doc_embeddings=[embedding]
        )

        return {
            "keybert_keywords": json.dumps(keywords),
            "keybert_top_keyword": keywords[0][0] if keywords else None,
            "sentence_embedding": embedding,
            "sentence_embedding_model": "all-MiniLM-L6-v2",
            "keybert_version": "0.8.3"
        }

if __name__ == "__main__":
    KeyBERTEnrichment().run()
```

---

## Model Taxonomy

### Group A: CPU-Only (No ML)

| Model | Purpose | Output | Dependencies |
|-------|---------|--------|--------------|
| **TextBlob** | Sentiment | polarity (-1→+1), subjectivity (0→1) | `textblob` |
| **textstat** | Readability | Flesch, grade level, fog, etc. | `textstat` |

### Group B: Classification Models (Own Forward Pass)

| Model | Purpose | Output | Dependencies |
|-------|---------|--------|--------------|
| **GoEmotions** | 27 emotions | Multi-label probabilities | `transformers`, BERT |
| **RoBERTa Hate** | Toxicity | hate/nothate + score | `transformers`, RoBERTa |

### Group C: Embedding-Based (Share Embeddings)

| Model | Purpose | Output | Dependencies |
|-------|---------|--------|--------------|
| **KeyBERT** | Keywords | Top-N keywords + scores | `keybert`, `sentence-transformers` |
| **BERTopic** | Topics | Topic ID + words | `bertopic`, `sentence-transformers` |

---

## Dependencies

```bash
# Group A (CPU-only)
pip install textblob textstat

# Group B (Classification)
pip install transformers torch

# Group C (Embedding-based)
pip install sentence-transformers keybert bertopic
pip install hdbscan umap-learn  # BERTopic dependencies
```

---

## Anti-Fragile Properties

| Property | Implementation |
|----------|----------------|
| **Run anything alone** | Each script is independent, owns its columns |
| **Run groups together** | Group scripts aggregate for efficiency |
| **Re-run fills gaps** | `--mode null-only` (default) |
| **Force overwrite** | `--mode overwrite` |
| **Staging protects production** | Default writes to staging |
| **Column ownership** | Each script touches only its columns |
| **Embedding reuse** | `--use-existing-embedding` for Group C |
| **Incremental** | `--limit`, `--offset` for partial runs |
| **Testable** | `--dry-run` shows what would happen |

---

## Execution Examples

### Initial Full Enrichment

```bash
# Run all Group A (fast, CPU)
python enrichment_textblob.py --mode null-only
python enrichment_textstat.py --mode null-only

# Run all Group B (needs GPU for speed)
python enrichment_goemotions.py --mode null-only
python enrichment_roberta.py --mode null-only

# Run Group C (compute embedding once, reuse)
python enrichment_bertopic.py --mode null-only  # Computes embeddings
python enrichment_keybert.py --mode null-only --use-existing-embedding
```

### Re-run Specific Enrichment

```bash
# Recalculate all textstat (new version)
python enrichment_textstat.py --mode overwrite

# Fill in missing GoEmotions for new data
python enrichment_goemotions.py --mode null-only --source browser_history
```

### Testing

```bash
# Dry run to see what would be processed
python enrichment_textblob.py --dry-run --verbose

# Process small sample
python enrichment_goemotions.py --limit 100 --verbose

# Process specific entities
echo "entity_123\nentity_456" > test_ids.txt
python enrichment_textblob.py --entity-ids test_ids.txt --mode overwrite
```

---

## Memory and Performance

| Enrichment | Memory | Time per 1K entities |
|------------|--------|---------------------|
| TextBlob | ~50MB | ~5 seconds |
| textstat | ~50MB | ~3 seconds |
| GoEmotions | ~2GB (CPU), ~500MB (GPU) | ~60s (CPU), ~5s (GPU) |
| RoBERTa Hate | ~2GB (CPU), ~500MB (GPU) | ~40s (CPU), ~3s (GPU) |
| KeyBERT | ~500MB | ~30 seconds |
| BERTopic | ~2GB | ~120 seconds (fit) |

**Recommendation:** Run Group A first (instant), then Group B (medium), then Group C (slower but reuses embeddings).

---

## Staging Table Schema

See: `architect_central_services/sql/spine/create_staging_entity_enrichments.sql`

Key columns per enrichment:
- `{enrichment}_*` columns for results
- `{enrichment}_enriched_at` timestamp
- `{enrichment}_version` for reproducibility

---

## Promotion to Production

```sql
-- Promote staging to production (after validation)
MERGE `spine.entity_enrichments` AS prod
USING `spine.staging_entity_enrichments` AS staging
ON prod.entity_id = staging.entity_id
WHEN MATCHED THEN UPDATE SET
  -- Copy all enrichment columns
  prod.textblob_polarity = staging.textblob_polarity,
  prod.textblob_subjectivity = staging.textblob_subjectivity,
  -- ... all other columns ...
  prod.updated_at = CURRENT_TIMESTAMP(),
  prod.promoted_from_staging_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT (...)
VALUES (...);
```
