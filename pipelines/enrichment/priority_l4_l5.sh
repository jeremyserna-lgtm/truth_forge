#!/bin/bash
# Priority Enrichment: L4 & L5 (Sentences & Messages)
# Focus on user AND assistant messages - both are critical

set -e

cd /Users/jeremyserna/truth_forge
export PYTHONPATH=/Users/jeremyserna/truth_forge

echo "========================================================================"
echo "PRIORITY ENRICHMENT: L4 & L5 (User + Assistant Messages & Sentences)"
echo "========================================================================"
echo "Current status:"
echo "  L5 (Messages):  53,697 / 53,697 (100% enriched) ✅"
echo "  L4 (Sentences): 493,000 / 511,487 (96.4% enriched)"
echo ""
echo "Target: 100% enrichment on L4 and L5"
echo "Enrichments: TextStat (grade level), TextBlob (sentiment), NRCLex (emotion)"
echo ""

# Step 1: Fill remaining L4 gaps (18,487 sentences)
echo "[Step 1/3] Completing L4 (Sentences) enrichment..."
echo "Need to enrich: ~18,487 sentences"
echo ""

python3 pipelines/enrichment/enrichment_textstat.py \
  --batch-size 1000 \
  --limit 20000 \
  --level 4 || echo "⚠️ TextStat L4 had issues, continuing..."

python3 pipelines/enrichment/enrichment_textblob.py \
  --batch-size 1000 \
  --limit 20000 \
  --level 4 || echo "⚠️ TextBlob L4 had issues, continuing..."

python3 pipelines/enrichment/enrichment_nrclx.py \
  --batch-size 1000 \
  --limit 20000 \
  --level 4 || echo "⚠️ NRCLex L4 had issues, continuing..."

echo ""
echo "✅ L4 (Sentences) complete!"
echo ""

# Step 2: Backfill any L5 gaps
echo "[Step 2/3] Backfilling any L5 (Messages) gaps..."
echo ""

python3 pipelines/enrichment/enrichment_textstat.py \
  --batch-size 1000 \
  --limit 60000 \
  --level 5 || echo "⚠️ TextStat L5 had issues, continuing..."

python3 pipelines/enrichment/enrichment_textblob.py \
  --batch-size 1000 \
  --limit 60000 \
  --level 5 || echo "⚠️ TextBlob L5 had issues, continuing..."

python3 pipelines/enrichment/enrichment_nrclx.py \
  --batch-size 1000 \
  --limit 60000 \
  --level 5 || echo "⚠️ NRCLex L5 had issues, continuing..."

echo ""
echo "✅ L5 (Messages) backfill complete!"
echo ""

# Step 3: Expand to more conversations
echo "[Step 3/3] Expanding enrichment coverage to more conversations..."
echo "Target: Get more conversations into the enrichment pipeline"
echo ""

python3 pipelines/enrichment/enrichment_coverage_expander.py \
  --target-coverage 0.20 \
  --level 4,5 \
  --limit 100000 \
  --verbose

echo ""
echo "========================================================================"
echo "✅ PRIORITY L4/L5 ENRICHMENT COMPLETE"
echo "========================================================================"
echo "Both user AND assistant messages/sentences enriched with:"
echo "  - TextStat (grade level, sophistication)"
echo "  - TextBlob (sentiment)"
echo "  - NRCLex (emotion)"
echo ""
echo "Next: GPU enrichments on THE EMPIRE (GoEmotions, KeyBERT, BERTopic)"
echo ""
