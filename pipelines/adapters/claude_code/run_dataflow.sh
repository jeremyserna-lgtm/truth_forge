#!/bin/bash
# Run Dataflow Pipeline

set -e

PROJECT_ID="flash-clover-464719-g1"
REGION="us-central1"
TEMP_LOCATION="gs://claude_code_pipeline_source/temp"
STAGING_LOCATION="gs://claude_code_pipeline_source/staging"
JOB_NAME="claude-code-pipeline-$(date +%Y%m%d-%H%M%S)"

echo "🚀 Running Dataflow Pipeline..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Job Name: $JOB_NAME"
echo ""

# Check if running locally or on Dataflow
if [ "$1" == "--local" ]; then
    echo "Running locally with DirectRunner..."
    python3 dataflow_pipeline.py \
        --runner DirectRunner \
        --project $PROJECT_ID
else
    echo "Running on Dataflow (managed)..."
    python3 dataflow_pipeline.py \
        --runner DataflowRunner \
        --project $PROJECT_ID \
        --region $REGION \
        --temp_location $TEMP_LOCATION \
        --staging_location $STAGING_LOCATION \
        --job_name $JOB_NAME \
        --autoscaling_algorithm THROUGHPUT_BASED \
        --max_num_workers 10
fi

echo ""
echo "✅ Pipeline submitted!"
echo "Monitor at: https://console.cloud.google.com/dataflow/jobs/$REGION/$JOB_NAME?project=$PROJECT_ID"
