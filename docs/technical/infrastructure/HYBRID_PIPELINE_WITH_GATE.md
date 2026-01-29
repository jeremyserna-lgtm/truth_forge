# Hybrid Pipeline: BigQuery + Python Stages (Including THE GATE)

**Created**: 2026-01-28  
**Purpose**: Complete pipeline that includes THE GATE, text cleaning, and spaCy NLP processing

---

## 🎯 The Problem

**BigQuery limitations:**
- ❌ No spaCy (NLP library)
- ❌ No identity_service (THE GATE)
- ❌ Limited text processing capabilities
- ❌ Can't run Python code directly

**Your requirements:**
- ✅ THE GATE (Stage 3) - identity service
- ✅ Text cleaning (Stage 2)
- ✅ spaCy NLP processing (Stages 5-6)
- ✅ Multiple processing stages (0-16)

---

## ✅ Solution: Hybrid Pipeline

**Use BigQuery for data loading, Python for processing:**

```
GCS Files
    ↓
BigQuery Data Transfer Service (Loads to staging)
    ↓
Python Pipeline Stages (THE GATE, cleaning, spaCy, etc.)
    ↓
BigQuery Staging Tables (per stage)
    ↓
Final: entity_unified
```

---

## 🏗️ Architecture

### Phase 1: Data Loading (BigQuery Native)

```
GCS (data_pipelines/ai_conversations/{source}/*.jsonl)
    ↓
BigQuery Data Transfer Service
    ↓
Staging Table: {source}_raw
```

### Phase 2: Python Pipeline (Cloud Run / Cloud Functions)

```
{source}_raw (BigQuery)
    ↓
Stage 1: Extraction (Python)
    ↓
Stage 2: Cleaning (Python)
    ↓
Stage 3: THE GATE (Python + identity_service) ← REQUIRED
    ↓
Stage 4: Staging (Python)
    ↓
Stage 5: L1 Tokens (Python + spaCy)
    ↓
Stage 6: L3 Sentences (Python + spaCy)
    ↓
... (more stages)
    ↓
Stage 16: Promotion (Python)
    ↓
entity_unified (BigQuery)
```

---

## 🚀 Implementation Options

### Option 1: Cloud Run Jobs (Recommended)

**Run Python pipeline stages as Cloud Run jobs:**

1. **Containerize your pipeline scripts**
2. **Create Cloud Run job** that runs all stages
3. **Trigger from BigQuery** (via Cloud Scheduler or Pub/Sub)

**Benefits**:
- ✅ Full Python environment (spaCy, identity_service)
- ✅ Scalable (auto-scales)
- ✅ Managed by Google
- ✅ Can run on schedule

### Option 2: Cloud Functions

**Run each stage as a Cloud Function:**

1. **Create Cloud Function** for each stage
2. **Chain functions** (Function 1 → Function 2 → etc.)
3. **Trigger from BigQuery** or schedule

**Benefits**:
- ✅ Serverless (pay per execution)
- ✅ Easy to deploy
- ✅ Automatic scaling

### Option 3: Keep Local + Cloud Scheduler

**Run Python pipeline locally, triggered by Cloud Scheduler:**

1. **Keep existing Python scripts**
2. **Create Cloud Scheduler job** that calls your local machine
3. **Or use Cloud Run** to run the scripts

---

## 📋 Complete Pipeline Flow

### Step 1: Load Data (BigQuery Data Transfer Service)

```
GCS Files → BigQuery Data Transfer Service → {source}_raw
```

**Setup**: Create Data Transfer Service for each source
- `claude_code_raw`
- `chatgpt_web_raw`
- `claude_web_raw`
- `gemini_web_raw`
- `grok_web_raw`

### Step 2: Run Python Pipeline (Cloud Run Job)

**Pipeline stages** (your existing scripts):
- Stage 1: Extraction
- Stage 2: Cleaning
- Stage 3: **THE GATE** (identity_service)
- Stage 4: Staging
- Stage 5: L1 Tokens (spaCy)
- Stage 6: L3 Sentences (spaCy)
- ... (all stages)
- Stage 16: Promotion to entity_unified

**Trigger**: Cloud Scheduler (daily after Data Transfer runs)

### Step 3: Monitor

- BigQuery Console → See staging tables
- Cloud Run → See job executions
- Logs → See pipeline progress

---

## 🔧 Setting Up Cloud Run Job

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install spaCy model
RUN python -m spacy download en_core_web_sm

# Copy pipeline scripts
COPY pipelines/ ./pipelines/
COPY src/ ./src/

# Run pipeline
CMD ["python", "pipelines/adapters/claude_code/scripts/run_pipeline.py"]
```

### 2. Deploy to Cloud Run

```bash
# Build and deploy
gcloud run jobs create claude-code-pipeline \
  --source . \
  --region us-central1 \
  --set-env-vars="BIGQUERY_PROJECT_ID=flash-clover-464719-g1" \
  --max-retries=3
```

### 3. Schedule with Cloud Scheduler

```bash
# Create scheduler job
gcloud scheduler jobs create http claude-code-pipeline-daily \
  --schedule="0 2 * * *" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/flash-clover-464719-g1/jobs/claude-code-pipeline:run" \
  --http-method=POST \
  --oauth-service-account-email=your-service-account@project.iam.gserviceaccount.com
```

---

## 🎯 Recommended Setup

### For Each Source

1. **BigQuery Data Transfer Service**:
   - Loads GCS → `{source}_raw` table
   - Runs daily at 1:00 AM UTC
   - Handles file deduplication automatically

2. **Cloud Run Job**:
   - Runs Python pipeline (all stages including THE GATE)
   - Reads from `{source}_raw`
   - Writes to staging tables and `entity_unified`
   - Runs daily at 2:00 AM UTC (after Data Transfer)

3. **Cloud Scheduler**:
   - Triggers Cloud Run job
   - Handles retries
   - Sends notifications

---

## 📊 Complete Timeline

```
1:00 AM UTC: BigQuery Data Transfer Service loads GCS → {source}_raw
    ↓
2:00 AM UTC: Cloud Run job runs Python pipeline
    ├─ Stage 1: Extraction
    ├─ Stage 2: Cleaning
    ├─ Stage 3: THE GATE (identity_service) ← REQUIRED
    ├─ Stage 4: Staging
    ├─ Stage 5: L1 Tokens (spaCy)
    ├─ Stage 6: L3 Sentences (spaCy)
    ├─ ... (all stages)
    └─ Stage 16: Promotion → entity_unified
    ↓
Result: Complete pipeline with THE GATE and spaCy processing
```

---

## ✅ What This Gives You

- ✅ **THE GATE**: Identity service integration
- ✅ **Text Cleaning**: Stage 2 processing
- ✅ **spaCy NLP**: Stages 5-6 with full NLP
- ✅ **All Stages**: Complete 16-stage pipeline
- ✅ **Managed**: Cloud Run handles execution
- ✅ **Scheduled**: Automatic daily runs
- ✅ **Scalable**: Auto-scales with load

---

## 🆚 Comparison

| Feature | Pure BigQuery | Hybrid (BigQuery + Python) |
|---------|---------------|----------------------------|
| **THE GATE** | ❌ No | ✅ Yes |
| **spaCy** | ❌ No | ✅ Yes |
| **Text Cleaning** | ⚠️ Limited | ✅ Full |
| **All Stages** | ❌ No | ✅ Yes |
| **Managed** | ✅ Yes | ✅ Yes |
| **Complexity** | Low | Medium |

---

## 📚 Next Steps

1. **Set up BigQuery Data Transfer Service** (for loading)
2. **Containerize Python pipeline** (Dockerfile)
3. **Deploy to Cloud Run** (as job)
4. **Schedule with Cloud Scheduler** (daily trigger)
5. **Monitor** (BigQuery + Cloud Run logs)

---

*This hybrid approach gives you THE GATE, spaCy, and all pipeline stages while still using BigQuery for data loading.*
