# Dataflow Pipeline Setup Steps

**Created**: 2026-01-28  
**Status**: Ready to Deploy

---

## 🚀 Quick Setup (5 Steps)

### Step 1: Install Dependencies

```bash
# Install Apache Beam
pip install apache-beam[gcp]

# Install spaCy
pip install spacy

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Step 2: Enable Dataflow API

```bash
gcloud services enable dataflow.googleapis.com --project=flash-clover-464719-g1
```

**Or in Console**: https://console.cloud.google.com/apis/library/dataflow.googleapis.com?project=flash-clover-464719-g1

### Step 3: Test Pipeline Locally (Optional)

```bash
cd pipelines/adapters/claude_code

# Test with DirectRunner (runs locally)
python dataflow_pipeline.py \
  --runner DirectRunner \
  --project flash-clover-464719-g1
```

### Step 4: Run on Dataflow

```bash
# Run on Dataflow (managed execution)
python dataflow_pipeline.py \
  --runner DataflowRunner \
  --project flash-clover-464719-g1 \
  --region us-central1 \
  --temp_location gs://claude_code_pipeline_source/temp \
  --staging_location gs://claude_code_pipeline_source/staging \
  --job_name claude-code-pipeline-$(date +%Y%m%d-%H%M%S)
```

### Step 5: Schedule with Cloud Scheduler

**In Google Console**:

1. Go to **Cloud Scheduler**: https://console.cloud.google.com/cloudscheduler?project=flash-clover-464719-g1
2. Click **"Create Job"**
3. **Name**: `claude-code-dataflow-daily`
4. **Schedule**: `0 2 * * *` (Daily at 2:00 AM UTC)
5. **Target**: HTTP
6. **URL**: `https://dataflow.googleapis.com/v1b3/projects/flash-clover-464719-g1/locations/us-central1/jobs:run`
7. **Method**: POST
8. **Auth**: OAuth token
9. **Body**: Job configuration JSON

---

## 📋 Prerequisites Checklist

- [ ] Dataflow API enabled
- [ ] BigQuery API enabled
- [ ] GCS bucket exists: `claude_code_pipeline_source`
- [ ] External table exists: `spine.claude_code_external`
- [ ] Python dependencies installed
- [ ] spaCy model downloaded

---

## 🔍 Monitor Pipeline

### Dataflow Console

1. Go to **Dataflow Console**: https://console.cloud.google.com/dataflow?project=flash-clover-464719-g1
2. See all running jobs
3. Click on job → See execution graph
4. Check logs and metrics

### BigQuery Console

```sql
-- Check if data is being written
SELECT COUNT(*) 
FROM `flash-clover-464719-g1.spine.entity_unified`
WHERE source_pipeline = 'claude_code'
  AND ingestion_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
```

---

## ✅ Success Criteria

- [ ] Pipeline job appears in Dataflow Console
- [ ] Job runs successfully (no errors)
- [ ] Data appears in entity_unified
- [ ] Scheduled job runs automatically

---

*Follow these steps to set up your Dataflow pipeline!*
