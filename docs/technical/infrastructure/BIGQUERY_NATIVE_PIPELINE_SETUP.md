# BigQuery Native Pipeline Setup Guide

**Last Updated**: 2026-01-28  
**Purpose**: Step-by-step guide to replace custom scripts with BigQuery-native solutions

---

## 🎯 Overview

This guide shows you how to replace all your custom Python sync scripts with **BigQuery-native features** that work out of the box:

1. **BigQuery Data Transfer Service** - For scheduled data loads
2. **BigQuery Scheduled Queries** - For transformations
3. **Cloud Storage + Load Jobs** - For file-based sources
4. **BigQuery Pipelines** - For complex multi-step workflows

**No custom Python scripts required. Everything runs in BigQuery.**

---

## 📊 Your Current Data Sources (From Your Codebase)

Based on your code, you're syncing:

1. **Supabase** → BigQuery (`identity.contacts_master`)
2. **Local DuckDB files** → BigQuery (various tables)
3. **JSONL files** → BigQuery (pipeline stages)
4. **CRM Twenty** ↔ BigQuery (bidirectional sync)
5. **External APIs** → BigQuery (various sources)

---

## ✅ Solution 1: BigQuery Data Transfer Service

### For: External Sources (S3, Cloud Storage, APIs)

**What it does**: Automatically loads data from external sources into BigQuery on a schedule.

### Step-by-Step Setup

#### Step 1: Enable BigQuery Data Transfer Service

```bash
# In Google Cloud Console
# Or via gcloud CLI:
gcloud services enable bigquerydatatransfer.googleapis.com
```

#### Step 2: Create a Transfer (Google Cloud Console)

1. Go to **BigQuery Console** → **Data Transfers**
2. Click **"Create Transfer"**
3. Select your source type:
   - **Amazon S3** (if you have S3 buckets)
   - **Google Cloud Storage** (recommended - move files here first)
   - **Google Analytics 4** (if applicable)
   - **Google Ads** (if applicable)
   - **Facebook Ads** (if applicable)

#### Step 3: Configure Transfer

**Example: Cloud Storage → BigQuery**

1. **Source**: Select your GCS bucket
2. **Destination**: Select BigQuery dataset (e.g., `identity`)
3. **Table name**: Enter table name (e.g., `contacts_master`)
4. **Schedule**: 
   - **Daily** at 2:00 AM
   - **Hourly** every hour
   - **Custom** cron expression
5. **File format**: JSON, CSV, Parquet, etc.
6. **Schema**: Auto-detect or upload schema file

#### Step 4: Save and Run

Click **"Save"**. BigQuery will:
- ✅ Run on schedule automatically
- ✅ Handle errors and retries
- ✅ Send notifications on failure
- ✅ Track transfer history

**That's it. No code required.**

---

## ✅ Solution 2: BigQuery Scheduled Queries

### For: Transformations, Data Cleaning, Aggregations

**What it does**: Runs SQL queries automatically on a schedule.

### Step-by-Step Setup

#### Step 1: Write Your SQL Query

In BigQuery Console, write your transformation query:

```sql
-- Example: Transform raw contacts into cleaned contacts
CREATE OR REPLACE TABLE `identity.contacts_cleaned` AS
SELECT
  contact_id,
  COALESCE(first_name, '') || ' ' || COALESCE(last_name, '') AS full_name,
  LOWER(TRIM(email)) AS email_normalized,
  organization,
  job_title,
  CASE 
    WHEN is_business = TRUE THEN 'Business'
    ELSE 'Personal'
  END AS contact_type,
  created_at,
  updated_at
FROM `identity.contacts_master`
WHERE updated_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
```

#### Step 2: Schedule the Query

1. Click **"Schedule"** button (top right in query editor)
2. **Schedule name**: `daily_contacts_cleanup`
3. **Schedule frequency**: 
   - **Daily** at 2:00 AM
   - **Hourly** every hour
   - **Custom** cron: `0 2 * * *` (daily at 2 AM)
4. **Destination table**: 
   - **Write if empty** (first run)
   - **Append** (add new rows)
   - **Overwrite** (replace table)
5. **Query parameters**: Set any parameters (e.g., date ranges)

#### Step 3: Save

Click **"Save"**. BigQuery will:
- ✅ Run query on schedule
- ✅ Write results to destination table
- ✅ Handle errors automatically
- ✅ Send email notifications on failure

**No Python scripts. Just SQL.**

---

## ✅ Solution 3: Cloud Storage + BigQuery Load Jobs

### For: Local Files (DuckDB, JSONL, CSV) → BigQuery

**What it does**: Upload files to Cloud Storage, then load into BigQuery automatically.

### Step-by-Step Setup

#### Step 1: Upload Files to Cloud Storage

**Option A: Manual Upload (One-time)**

```bash
# Upload JSONL file to GCS
gsutil cp local/path/to/file.jsonl gs://your-bucket/data/contacts/
```

**Option B: Automated Upload (Scheduled)**

Use **Cloud Scheduler** + **Cloud Functions** to upload files automatically:

1. **Cloud Scheduler** triggers daily
2. **Cloud Function** runs Python script to:
   - Read local files
   - Upload to GCS
   - Trigger BigQuery load

**Or use `gsutil rsync` in a cron job:**

```bash
# Add to crontab
0 1 * * * gsutil -m rsync -r /local/path/to/data/ gs://your-bucket/data/
```

#### Step 2: Create BigQuery Load Job (Scheduled)

**Option A: Use BigQuery Data Transfer Service**

1. Go to **BigQuery Console** → **Data Transfers**
2. Create transfer from **Cloud Storage**
3. Point to your GCS bucket path
4. Set schedule (daily, hourly, etc.)

**Option B: Use Cloud Scheduler + BigQuery API**

1. **Cloud Scheduler** triggers daily
2. Calls **Cloud Function** that:
   - Lists new files in GCS
   - Creates BigQuery load job via API
   - Loads files into BigQuery

**Option C: Event-Driven (Recommended)**

Use **Event-Driven Transfers** (BigQuery feature):

1. Enable **Pub/Sub notifications** on GCS bucket
2. Configure **Event-Driven Transfer** in BigQuery
3. When file is uploaded → BigQuery loads it automatically

**No manual scripts needed.**

---

## ✅ Solution 4: BigQuery Pipelines (Dataform)

### For: Complex Multi-Step Workflows

**What it does**: Run multiple SQL queries, notebooks, and data prep steps in sequence.

### Step-by-Step Setup

#### Step 1: Create Pipeline

1. Go to **BigQuery Console** → **Pipelines**
2. Click **"Create Pipeline"**
3. Name: `contacts_processing_pipeline`

#### Step 2: Add Steps

**Step 1: Load Raw Data**
```sql
-- Load from Cloud Storage
CREATE OR REPLACE TABLE `identity.contacts_raw` AS
SELECT * FROM EXTERNAL_QUERY(...)
```

**Step 2: Clean Data**
```sql
-- Clean and normalize
CREATE OR REPLACE TABLE `identity.contacts_cleaned` AS
SELECT ... FROM `identity.contacts_raw`
WHERE ...
```

**Step 3: Enrich Data**
```sql
-- Add enrichments
CREATE OR REPLACE TABLE `identity.contacts_enriched` AS
SELECT 
  c.*,
  e.enrichment_data
FROM `identity.contacts_cleaned` c
LEFT JOIN `identity.enrichments` e ON c.contact_id = e.contact_id
```

#### Step 3: Define Dependencies

- Step 2 depends on Step 1
- Step 3 depends on Step 2

#### Step 4: Schedule Pipeline

1. Click **"Schedule"**
2. Set frequency (daily, hourly, etc.)
3. **Save**

BigQuery runs all steps in order automatically.

---

## 🔄 Replacing Your Current Sync Scripts

### Current Script: `bigquery_sync.py`

**What it does**: Syncs contacts from BigQuery to Supabase, Local DB, CRM Twenty

**Replace with**:

1. **Keep BigQuery as source of truth** ✅
2. **Use Supabase → BigQuery Data Transfer** (if Supabase supports it)
3. **Or use Cloud Functions** triggered by BigQuery changes:

```python
# Cloud Function (triggered by BigQuery table changes)
def sync_to_supabase(event, context):
    """Triggered when BigQuery table changes."""
    # Get changed rows from BigQuery
    # Sync to Supabase
    # Sync to CRM Twenty
```

**Or use BigQuery → Supabase connector** (if available in Supabase)

---

### Current Script: Pipeline Stages (stage_3, stage_4, etc.)

**What they do**: Process JSONL files and load to BigQuery

**Replace with**:

1. **Upload JSONL to Cloud Storage** (automated via `gsutil rsync`)
2. **BigQuery Data Transfer Service** loads from GCS automatically
3. **BigQuery Scheduled Queries** transform data between stages

**No Python scripts needed.**

---

## 📋 Complete Migration Checklist

### Phase 1: Set Up Data Transfer Service (Week 1)

- [ ] Enable BigQuery Data Transfer Service API
- [ ] Create transfer for Cloud Storage → BigQuery
- [ ] Test transfer manually
- [ ] Set up schedule (daily at 2 AM)
- [ ] Verify data loads correctly

### Phase 2: Set Up Scheduled Queries (Week 1)

- [ ] Write transformation SQL queries
- [ ] Schedule daily cleanup query
- [ ] Schedule daily aggregation queries
- [ ] Test queries manually
- [ ] Verify scheduled runs work

### Phase 3: Migrate File-Based Sources (Week 2)

- [ ] Set up GCS bucket for data files
- [ ] Configure `gsutil rsync` or Cloud Function to upload files
- [ ] Create BigQuery Data Transfer from GCS
- [ ] Test end-to-end flow
- [ ] Set up monitoring/alerts

### Phase 4: Replace Custom Scripts (Week 2-3)

- [ ] Identify all custom sync scripts
- [ ] Map each to BigQuery-native solution
- [ ] Set up replacements
- [ ] Test thoroughly
- [ ] Decommission old scripts

---

## 🎯 Recommended Architecture

```
┌─────────────────┐
│  Data Sources   │
│  (Supabase,     │
│   Files, APIs)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Cloud Storage  │  ← Upload files here (automated)
│  (GCS Bucket)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  BigQuery Data Transfer     │  ← Automatic loads
│  Service (Scheduled)        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────┐
│  BigQuery       │
│  (Raw Tables)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  BigQuery Scheduled Queries │  ← Transformations
│  (Daily/Hourly)             │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────┐
│  BigQuery       │
│  (Final Tables) │
└─────────────────┘
```

---

## 💰 Cost Estimate

**BigQuery Data Transfer Service**:
- **Free** for many sources (Google Analytics, Ads, etc.)
- **Storage costs**: Standard BigQuery storage ($0.02/GB/month)
- **Query costs**: Standard BigQuery query pricing ($5/TB scanned)

**BigQuery Scheduled Queries**:
- **Free** to schedule
- **Query costs**: Only pay for queries that run ($5/TB scanned)

**Cloud Storage**:
- **Storage**: $0.020/GB/month
- **Operations**: $0.05 per 10,000 operations

**Total**: ~$50-200/month for moderate data volumes (much cheaper than custom infrastructure)

---

## 🚀 Quick Start: Your First Pipeline (Today)

### Step 1: Test BigQuery Scheduled Query (5 minutes)

1. Open BigQuery Console
2. Write a simple query:
```sql
SELECT 
  COUNT(*) as total_contacts,
  COUNT(DISTINCT organization) as unique_orgs
FROM `identity.contacts_master`
WHERE updated_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
```

3. Click **"Schedule"**
4. Name: `daily_contacts_summary`
5. Schedule: Daily at 2:00 AM
6. Destination: Create new table `identity.daily_summary`
7. **Save**

**Done. It will run automatically tomorrow at 2 AM.**

### Step 2: Set Up Cloud Storage Transfer (10 minutes)

1. Create GCS bucket: `gs://your-project-data/`
2. Upload a test JSONL file
3. Go to BigQuery → Data Transfers
4. Create transfer from Cloud Storage
5. Point to your test file
6. Set destination table
7. **Save and run test**

**Done. It will load automatically.**

---

## 📚 Documentation Links

- **BigQuery Data Transfer Service**: https://cloud.google.com/bigquery/docs/dts-introduction
- **BigQuery Scheduled Queries**: https://cloud.google.com/bigquery/docs/scheduling-queries
- **BigQuery Pipelines**: https://cloud.google.com/bigquery/docs/pipelines-introduction
- **Event-Driven Transfers**: https://cloud.google.com/bigquery/docs/event-driven-transfer
- **Cloud Storage Setup**: https://cloud.google.com/storage/docs

---

## ✅ Success Criteria

You'll know it's working when:

- [ ] Data appears in BigQuery tables automatically
- [ ] Scheduled queries run on time (check query history)
- [ ] No Python scripts are running for data sync
- [ ] You get email notifications on failures (if configured)
- [ ] Data is fresh (updated within schedule window)

---

## 🆘 Troubleshooting

### Transfer Not Running

1. Check **Data Transfers** page → **Transfer History**
2. Look for error messages
3. Verify source credentials/permissions
4. Check schedule configuration

### Scheduled Query Failing

1. Check **Scheduled Queries** page → **History**
2. Click on failed query to see error
3. Test query manually first
4. Verify destination table permissions

### Files Not Loading

1. Verify files are in GCS bucket
2. Check file format matches configuration
3. Verify BigQuery has permissions to read GCS
4. Check transfer logs for errors

---

## 🎓 The Bottom Line

**You don't need custom Python scripts for data pipelines.**

BigQuery provides:
- ✅ **Data Transfer Service** - for loading data
- ✅ **Scheduled Queries** - for transformations  
- ✅ **Pipelines** - for complex workflows
- ✅ **Event-Driven Transfers** - for real-time loads

**All managed. All reliable. All in BigQuery.**

Stop writing scripts. Start configuring BigQuery.

---

*This guide replaces all custom sync scripts with BigQuery-native solutions.*
