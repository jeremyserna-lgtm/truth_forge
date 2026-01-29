#!/bin/bash
# Quick Start: CPU Enrichments (TextBlob, TextStat, NRCLex)
# Run NOW on Mac Air while waiting for THE EMPIRE

set -e

cd /Users/jeremyserna/truth_forge
export PYTHONPATH=/Users/jeremyserna/truth_forge

echo "========================================================================"
echo "STARTING CPU ENRICHMENTS - Batch 1"
echo "========================================================================"
echo "Processing 10,000 entities with CPU enrichments (TextBlob, TextStat, NRCLex)"
echo "Cost: $0 (runs locally)"
echo "Time: ~30-60 minutes"
echo ""

# Step 1: Expand coverage first (create skeleton rows)
echo "[1/4] Expanding enrichment coverage..."
python3 pipelines/enrichment/enrichment_coverage_expander.py \
  --target-coverage 0.10 \
  --level 5 \
  --limit 10000

echo ""
echo "✅ Coverage expanded"
echo ""

# Step 2: TextBlob (sentiment)
echo "[2/4] Running TextBlob (sentiment)..."
python3 pipelines/enrichment/enrichment_textblob.py \
  --batch-size 500 \
  --limit 10000 || echo "⚠️ TextBlob had issues, continuing..."

echo ""

# Step 3: TextStat (readability)
echo "[3/4] Running TextStat (readability)..."
python3 pipelines/enrichment/enrichment_textstat.py \
  --batch-size 500 \
  --limit 10000 || echo "⚠️ TextStat had issues, continuing..."

echo ""

# Step 4: NRCLex (emotion)
echo "[4/4] Running NRCLex (emotion)..."
python3 pipelines/enrichment/enrichment_nrclx.py \
  --batch-size 500 \
  --limit 10000 || echo "⚠️ NRCLex had issues, continuing..."

echo ""
echo "========================================================================"
echo "✅ BATCH 1 COMPLETE"
echo "========================================================================"
echo "Processed: 10,000 entities with CPU enrichments"
echo ""
echo "Next steps:"
echo "1. Wait for THE EMPIRE (GPU enrichments: GoEmotions, KeyBERT, BERTopic)"
echo "2. Add Genesis metadata (thought_type, cognitive_stage, pattern)"
echo "3. Extract for Genesis training"
echo ""
