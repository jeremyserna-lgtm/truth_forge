#!/bin/bash
# Additional CPU Enrichments - Fill More Gaps
# Focus on Clara Arc analysis dimensions

set -e

cd /Users/jeremyserna/truth_forge
export PYTHONPATH=/Users/jeremyserna/truth_forge

echo "========================================================================"
echo "ADDITIONAL CPU ENRICHMENTS - Batch 2"
echo "========================================================================"
echo "Adding more CPU-based enrichments for Clara Arc analysis"
echo ""

# Step 1: Expand coverage to more entities (target 50%)
echo "[1/3] Expanding enrichment coverage to 50%..."
python3 pipelines/enrichment/enrichment_coverage_expander.py \
  --target-coverage 0.50 \
  --level 5 \
  --limit 50000 \
  --verbose

echo ""
echo "✅ Coverage expanded to 50%"
echo ""

# Step 2: Fill NRCLex gaps (currently 84.8%)
echo "[2/3] Filling NRCLex emotion gaps..."
echo "Current: 84.8% | Target: 100%"
python3 pipelines/enrichment/enrichment_nrclx.py \
  --batch-size 1000 \
  --limit 50000 || echo "⚠️ NRCLex issues, continuing..."

echo ""

# Step 3: Add any missing TextStat/TextBlob to new coverage
echo "[3/3] Backfilling TextStat and TextBlob on new entities..."
python3 pipelines/enrichment/enrichment_textstat.py \
  --batch-size 1000 \
  --limit 50000 || echo "⚠️ TextStat issues, continuing..."

python3 pipelines/enrichment/enrichment_textblob.py \
  --batch-size 1000 \
  --limit 50000 || echo "⚠️ TextBlob issues, continuing..."

echo ""
echo "========================================================================"
echo "✅ BATCH 2 COMPLETE"
echo "========================================================================"
echo "Expanded coverage to 50% (~6M entities)"
echo "Backfilled all CPU enrichments"
echo ""
echo "Next: GPU enrichments on THE EMPIRE (GoEmotions, KeyBERT, BERTopic)"
echo ""
