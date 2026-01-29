#!/bin/bash
# Setup script for Dataflow pipeline

set -e

echo "🚀 Setting up Dataflow Pipeline..."

# Check if we're in the right directory
if [ ! -f "dataflow_pipeline.py" ]; then
    echo "❌ Error: dataflow_pipeline.py not found. Run this from pipelines/adapters/claude_code/"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements_dataflow.txt

# Download spaCy model
echo "📥 Downloading spaCy model..."
python3 -m spacy download en_core_web_sm

# Enable Dataflow API
echo "🔧 Enabling Dataflow API..."
gcloud services enable dataflow.googleapis.com --project=flash-clover-464719-g1

# Check GCS bucket exists
echo "🔍 Checking GCS bucket..."
if ! gsutil ls gs://claude_code_pipeline_source/ &> /dev/null; then
    echo "⚠️  Warning: GCS bucket claude_code_pipeline_source may not exist"
    echo "   Create it with: gsutil mb -p flash-clover-464719-g1 gs://claude_code_pipeline_source"
fi

# Create temp and staging directories
echo "📁 Creating temp directories..."
gsutil mb -p flash-clover-464719-g1 gs://claude_code_pipeline_source/temp 2>/dev/null || true
gsutil mb -p flash-clover-464719-g1 gs://claude_code_pipeline_source/staging 2>/dev/null || true

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Test locally: python3 dataflow_pipeline.py --runner DirectRunner"
echo "2. Run on Dataflow: python3 dataflow_pipeline.py --runner DataflowRunner --project flash-clover-464719-g1 --region us-central1 --temp_location gs://claude_code_pipeline_source/temp"
