#!/bin/bash
# Start Enrichment Pipeline - Run CPU enrichments NOW
# Cost: ~$5-40 total, very affordable for 3 businesses

set -e

echo "========================================================================"
echo "STARTING ENRICHMENT PIPELINE"
echo "========================================================================"
echo "Timestamp: $(date)"
echo ""

cd /Users/jeremyserna/truth_forge

# Step 1: Expand enrichment coverage to 50%
echo "Step 1: Expanding enrichment coverage to 50%..."
echo "Current: 4.62% (549K entities)"
echo "Target: 50%+ (~6M entities)"
echo ""

python3 pipelines/enrichment/enrichment_coverage_expander.py \
  --target-coverage 0.50 \
  --level 8,5,4 \
  --limit 100000 \
  --verbose

echo ""
echo "✅ Coverage expansion complete!"
echo ""

# Step 2: Run CPU enrichments (TextBlob - sentiment)
echo "Step 2: Running TextBlob (sentiment analysis)..."
echo "Cost: $0 (local CPU)"
echo ""

python3 pipelines/enrichment/enrichment_textblob.py \
  --batch-size 1000 \
  --limit 10000

echo ""
echo "✅ TextBlob complete!"
echo ""

# Step 3: Run TextStat (readability metrics)
echo "Step 3: Running TextStat (readability)..."
echo "Cost: $0 (local CPU)"
echo ""

python3 pipelines/enrichment/enrichment_textstat.py \
  --batch-size 1000 \
  --limit 10000

echo ""
echo "✅ TextStat complete!"
echo ""

# Step 4: Run NRCLex (emotion)
echo "Step 4: Running NRCLex (emotion)..."
echo "Cost: $0 (local CPU)"
echo ""

python3 pipelines/enrichment/enrichment_nrclx.py \
  --batch-size 1000 \
  --limit 10000

echo ""
echo "✅ NRCLex complete!"
echo ""

echo "========================================================================"
echo "ALL CPU ENRICHMENTS COMPLETE"
echo "========================================================================"
echo "Next: GPU enrichments on THE EMPIRE (GoEmotions, KeyBERT, BERTopic)"
echo "Next: Gemini enrichment for Genesis metadata (thought_type, cognitive_stage, pattern)"
echo ""
