#!/bin/bash
# L4/L5 Priority Enrichment Backfill
# Robust version with checkpoints, memory management, and graceful shutdown
#
# Usage: ./l4_l5_backfill.sh [--dry-run] [--limit N] [--resume] [--staging]
#
# Features:
# - Streaming pagination (won't crash your machine)
# - Checkpoints (resume from where you left off)
# - Graceful shutdown (Ctrl+C saves progress)
# - Memory monitoring (warns if approaching limit)
#
# Examples:
#   ./l4_l5_backfill.sh                    # Run all enrichments to production
#   ./l4_l5_backfill.sh --limit 10000      # Process 10K entities per enrichment
#   ./l4_l5_backfill.sh --resume           # Resume from last checkpoint
#   ./l4_l5_backfill.sh --dry-run          # Show what would be processed

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../.."

# Parse arguments
DRY_RUN=""
LIMIT=""
RESUME=""
TARGET="--production"  # Default to production table
PAGE_SIZE="--page-size 5000"
COMMON_ARGS="--level 4,5 --mode null-only --progress"

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --limit)
            LIMIT="--limit $2"
            shift 2
            ;;
        --resume)
            RESUME="--resume"
            shift
            ;;
        --staging)
            TARGET=""  # Empty means staging (default in script)
            shift
            ;;
        --page-size)
            PAGE_SIZE="--page-size $2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dry-run] [--limit N] [--resume] [--staging] [--page-size N]"
            exit 1
            ;;
    esac
done

ARGS="$COMMON_ARGS $TARGET $DRY_RUN $LIMIT $RESUME $PAGE_SIZE"

echo "=============================================="
echo "L4/L5 PRIORITY ENRICHMENT BACKFILL"
echo "=============================================="
echo "Arguments: $ARGS"
echo "Checkpoints: ./checkpoints/"
echo "DLQ: ./dlq/"
echo ""
echo "Press Ctrl+C to gracefully stop (progress saved)"
echo "Use --resume to continue from checkpoint"
echo "=============================================="

# Activate virtual environment
source .venv/bin/activate
export PYTHONPATH="$PWD:$PYTHONPATH"

# Create checkpoint and dlq directories
mkdir -p checkpoints dlq

# Track overall progress
TOTAL_WRITTEN=0
TOTAL_FAILED=0

run_enrichment() {
    local name=$1
    local script=$2
    local extra_args=${3:-""}

    echo ""
    echo ">>> $name"
    echo "---"

    if python "$script" $ARGS $extra_args; then
        echo "<<< $name completed"
    else
        echo "<<< $name failed (check logs)"
    fi
}

# Phase 1: Foundation (CPU-only, fast)
echo ""
echo "=== PHASE 1: FOUNDATION ENRICHMENTS (CPU-only) ==="

run_enrichment "[1/7] TextBlob Sentiment" \
    "pipelines/enrichment/enrichment_textblob.py"

run_enrichment "[2/7] TextStat Readability" \
    "pipelines/enrichment/enrichment_textstat.py"

run_enrichment "[3/7] NRCLex Emotions" \
    "pipelines/enrichment/enrichment_nrclx.py"

# Phase 2: Sovereign (CPU-only, critical for training)
echo ""
echo "=== PHASE 2: SOVEREIGN ENRICHMENTS (CPU-only) ==="

# Check if sovereign enrichment scripts exist
if [[ -f "pipelines/enrichment/enrichment_cognitive_stage.py" ]]; then
    run_enrichment "[4/7] Cognitive Stage (Kegan 1-5)" \
        "pipelines/enrichment/enrichment_cognitive_stage.py"
else
    echo "[4/7] Cognitive Stage - SKIPPED (script not found)"
fi

if [[ -f "pipelines/enrichment/enrichment_struggle_filter.py" ]]; then
    run_enrichment "[5/7] Struggle Filter (Swimming/Drowning)" \
        "pipelines/enrichment/enrichment_struggle_filter.py"
else
    echo "[5/7] Struggle Filter - SKIPPED (script not found)"
fi

if [[ -f "pipelines/enrichment/enrichment_confidence.py" ]]; then
    run_enrichment "[6/7] Confidence Calibration" \
        "pipelines/enrichment/enrichment_confidence.py"
else
    echo "[6/7] Confidence Calibration - SKIPPED (script not found)"
fi

if [[ -f "pipelines/enrichment/enrichment_source_attribution.py" ]]; then
    run_enrichment "[7/7] Source Attribution (ME/NOT-ME)" \
        "pipelines/enrichment/enrichment_source_attribution.py"
else
    echo "[7/7] Source Attribution - SKIPPED (script not found)"
fi

echo ""
echo "=============================================="
echo "L4/L5 BACKFILL COMPLETE"
echo "=============================================="
echo ""
echo "Checkpoints saved to: ./checkpoints/"
echo "Failed records in: ./dlq/"
echo ""
echo "Next steps:"
echo "1. Check coverage: python pipelines/enrichment/monitor_coverage.py"
echo "2. For GPU enrichments (GoEmotions, RoBERTa), run separately:"
echo "   python pipelines/enrichment/enrichment_goemotions.py $ARGS --batch-size 32"
echo "   python pipelines/enrichment/enrichment_roberta_hate.py $ARGS --batch-size 32"
echo ""
