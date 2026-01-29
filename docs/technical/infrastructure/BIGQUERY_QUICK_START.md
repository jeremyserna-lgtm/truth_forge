# BigQuery Pipeline Quick Start Checklist

**Last Updated**: 2026-01-28  
**Purpose**: 30-minute setup to get your first automated pipeline running

---

## ⚡ 30-Minute Setup

### Step 1: Enable APIs (2 minutes)

```bash
# Enable BigQuery Data Transfer Service
gcloud services enable bigquerydatatransfer.googleapis.com

# Enable BigQuery API (if not already enabled)
gcloud services enable bigquery.googleapis.com
```

**Or in Console**: https://console.cloud.google.com/apis/library

---

### Step 2: Create Your First Scheduled Query (5 minutes)

1. **Open BigQuery Console**: https://console.cloud.google.com/bigquery

2. **Write a test query**:
```sql
-- Replace with your actual table
SELECT 
  CURRENT_TIMESTAMP() as run_time,
  COUNT(*) as total_records
FROM `identity.contacts_master`
```

3. **Click "Schedule"** (top right)

4. **Configure**:
   - **Name**: `test_daily_summary`
   - **Schedule**: Daily at 2:00 AM
   - **Destination**: Create new table `identity.test_summary`
   - **Write preference**: Overwrite

5. **Click "Save"**

✅ **Done. Check back tomorrow at 2 AM to see if it ran.**

---

### Step 3: Set Up Cloud Storage Transfer (10 minutes)

#### 3a. Create GCS Bucket

```bash
# Create bucket
gsutil mb -p YOUR_PROJECT_ID gs://your-data-pipeline/

# Or in Console: https://console.cloud.google.com/storage
```

#### 3b. Upload Test File

```bash
# Create a test JSONL file
echo '{"id": 1, "name": "Test"}' > test.jsonl

# Upload to GCS
gsutil cp test.jsonl gs://your-data-pipeline/test/
```

#### 3c. Create BigQuery Transfer

1. **Go to**: BigQuery Console → **Data Transfers**
2. **Click**: "Create Transfer"
3. **Source**: Cloud Storage
4. **Configure**:
   - **Source URI**: `gs://your-data-pipeline/test/*.jsonl`
   - **Destination dataset**: `identity` (or create new)
   - **Table name**: `test_transfer`
   - **Schedule**: Daily at 3:00 AM
   - **File format**: JSON (Newline delimited)
5. **Click "Save"**

✅ **Done. Transfer will run automatically.**

---

### Step 4: Verify It Works (5 minutes)

#### Check Scheduled Query

1. Go to **BigQuery Console** → **Scheduled Queries**
2. Find your query: `test_daily_summary`
3. Click on it → **History** tab
4. Should show "Scheduled" status

#### Check Data Transfer

1. Go to **BigQuery Console** → **Data Transfers**
2. Find your transfer
3. Click → **Transfer History**
4. Should show transfer runs

#### Run Test Manually

1. **Scheduled Query**: Click "Run Now" to test immediately
2. **Data Transfer**: Click "Run Now" to test immediately

✅ **If both work, you're set up!**

---

## 🎯 Next Steps (This Week)

### Day 1: Replace One Script

Pick ONE of your current sync scripts and replace it:

**Option A: Contacts Sync**
- Set up Cloud Storage bucket for contacts
- Create Data Transfer from GCS → BigQuery
- Schedule daily

**Option B: Pipeline Stage**
- Upload JSONL files to GCS (automated)
- Create Data Transfer from GCS → BigQuery
- Schedule daily

### Day 2-3: Add Transformations

Create Scheduled Queries for:
- Data cleaning
- Aggregations
- Joins between tables

### Day 4-5: Migrate More Sources

- Add more Data Transfers
- Set up more Scheduled Queries
- Test everything

---

## 📊 Your Current Tables (Reference)

Based on your codebase, you're using:

- `identity.contacts_master` - Main contacts table
- `identity.id_registry` - ID registry
- `spine.text_messages_stage_*` - Pipeline stages
- Various pipeline tables

**Start with one table. Get it working. Then expand.**

---

## 🔍 Monitoring

### Check Query History

```sql
-- See all scheduled query runs
SELECT 
  creation_time,
  job_id,
  total_bytes_processed,
  state
FROM `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE job_type = 'QUERY'
  AND creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY creation_time DESC
LIMIT 100
```

### Check Transfer History

1. BigQuery Console → Data Transfers
2. Click on transfer → Transfer History
3. See all runs, success/failure, error messages

---

## ⚠️ Common Issues

### "Permission Denied"

**Fix**: Grant BigQuery Data Transfer Service account access:
```bash
# Grant service account access to GCS bucket
gsutil iam ch serviceAccount:PROJECT_NUMBER@gcp-sa-bigquerydatatransfer.iam.gserviceaccount.com:objectViewer gs://your-bucket
```

### "Table Not Found"

**Fix**: Create destination table first, or use "Create table if not exists" option

### "Invalid Schema"

**Fix**: 
1. Let BigQuery auto-detect schema first
2. Then manually adjust if needed
3. Or upload schema file

---

## ✅ Success Checklist

After 30 minutes, you should have:

- [ ] BigQuery Data Transfer Service enabled
- [ ] One scheduled query created and saved
- [ ] One data transfer created and saved
- [ ] Tested both manually (Run Now)
- [ ] Verified they appear in history

**If all checked, you're ready to migrate your real pipelines!**

---

## 🚀 Ready to Go?

1. **Start with Step 1** (enable APIs)
2. **Do Step 2** (scheduled query) - takes 5 minutes
3. **Do Step 3** (data transfer) - takes 10 minutes
4. **Verify in Step 4** - takes 5 minutes

**Total time: 30 minutes to get your first automated pipeline running.**

---

*Once this works, you'll know BigQuery-native pipelines work. Then migrate your real data sources.*
