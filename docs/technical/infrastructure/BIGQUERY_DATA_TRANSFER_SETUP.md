# BigQuery Data Transfer Service Setup (Recommended)

**Created**: 2026-01-28  
**Purpose**: Set up fully managed data transfers that handle duplicates automatically

---

## 🎯 Why BigQuery Data Transfer Service?

**Better than cron jobs because:**
- ✅ **Automatic duplicate detection** - Only loads new files
- ✅ **Fully managed** - Google handles everything
- ✅ **Automatic retries** - If a transfer fails, it retries
- ✅ **Monitoring dashboard** - See all transfers in one place
- ✅ **Email notifications** - Get alerts on failures
- ✅ **No local machine required** - Runs in the cloud

---

## 🚀 Setup Instructions

### Step 1: Upload Files to GCS (One Time or Manual)

```bash
# Claude Code (local files)
gsutil -m cp ~/.claude/projects/*.jsonl gs://claude_code_pipeline_source/data_pipelines/ai_conversations/claude_code/

# Other sources (when you receive them)
gsutil cp chatgpt_file.jsonl gs://claude_code_pipeline_source/data_pipelines/ai_conversations/chatgpt_web/
gsutil cp claude_web_file.jsonl gs://claude_code_pipeline_source/data_pipelines/ai_conversations/claude_web/
gsutil cp gemini_file.jsonl gs://claude_code_pipeline_source/data_pipelines/ai_conversations/gemini_web/
gsutil cp grok_file.jsonl gs://claude_code_pipeline_source/data_pipelines/ai_conversations/grok_web/
```

### Step 2: Create Data Transfer Service

For **each source**, create a transfer:

#### Claude Code Transfer

1. **Open BigQuery Console**: https://console.cloud.google.com/bigquery?project=flash-clover-464719-g1

2. **Go to Data Transfers**: Click "Data Transfers" in left sidebar

3. **Create Transfer**: Click "Create Transfer"

4. **Select Source**: Choose "Cloud Storage"

5. **Configure**:
   - **Display name**: `claude_code_gcs_transfer`
   - **Source URI**: `gs://claude_code_pipeline_source/data_pipelines/ai_conversations/claude_code/*.jsonl`
   - **Destination dataset**: `spine`
   - **Destination table**: `claude_code_staging` (will be created)
   - **File format**: JSON (Newline delimited)
   - **Write preference**: **Append** (adds new records)
   - **Schema**: Auto-detect

6. **Schedule**:
   - **Schedule starts**: Today
   - **Repeats**: Daily
   - **Time**: 1:00 AM UTC

7. **Click "Save"**

#### Repeat for Other Sources

Create transfers for:
- `chatgpt_web_gcs_transfer` → `gs://.../chatgpt_web/*.jsonl` → `chatgpt_web_staging`
- `claude_web_gcs_transfer` → `gs://.../claude_web/*.jsonl` → `claude_web_staging`
- `gemini_web_gcs_transfer` → `gs://.../gemini_web/*.jsonl` → `gemini_web_staging`
- `grok_web_gcs_transfer` → `gs://.../grok_web/*.jsonl` → `grok_web_staging`

---

## 🔄 How Deduplication Works

### Automatic File-Level Deduplication

BigQuery Data Transfer Service automatically:
- ✅ Tracks which files have been processed
- ✅ Only loads new files (by filename and metadata)
- ✅ Skips files that were already loaded

**Example**:
- Day 1: Loads `file1.jsonl`, `file2.jsonl`
- Day 2: Only loads `file3.jsonl` (skips file1, file2)
- Day 3: No new files → No transfer needed

### Record-Level Deduplication (In Query)

For the transformation query, add deduplication:

```sql
WHERE entity_id NOT IN (
  SELECT entity_id 
  FROM `flash-clover-464719-g1.spine.entity_unified`
  WHERE source_pipeline = 'claude_code'
)
```

This ensures even if a file is processed twice, records aren't duplicated.

---

## 📊 Complete Pipeline Flow

```
Local Files / Emailed Files
    ↓
Upload to GCS (manual or script)
    ↓
BigQuery Data Transfer Service (Automatic, handles duplicates)
    ↓
Staging Tables (claude_code_staging, chatgpt_web_staging, etc.)
    ↓
BigQuery Scheduled Query (Transformation + record deduplication)
    ↓
entity_unified (Production)
```

---

## 🔍 Monitoring

### Check Transfer Status

1. BigQuery Console → **Data Transfers**
2. See all transfers in one dashboard
3. Click on transfer → **Transfer History**
4. See:
   - Success/failure
   - Files processed
   - Records loaded
   - Error messages

### Check Staging Tables

```sql
-- See what was loaded
SELECT 
  COUNT(*) as total_records,
  COUNT(DISTINCT _FILE_NAME) as unique_files,
  MIN(_PARTITIONTIME) as earliest_load,
  MAX(_PARTITIONTIME) as latest_load
FROM `flash-clover-464719-g1.spine.claude_code_staging`
```

---

## ✅ Benefits Over Cron Job

| Feature | Cron Job | Data Transfer Service |
|---------|----------|----------------------|
| **Deduplication** | Manual (rsync) | ✅ Automatic |
| **Retry Logic** | ❌ No | ✅ Automatic |
| **Monitoring** | Log files | ✅ Dashboard |
| **Notifications** | ❌ No | ✅ Email alerts |
| **Requires Local Machine** | ✅ Yes | ❌ No |
| **Managed** | ❌ You manage | ✅ Google manages |

---

## 🎯 Recommendation

**Use BigQuery Data Transfer Service for all sources:**

1. **Claude Code**: Upload files once, Data Transfer Service handles rest
2. **Other sources**: Upload when received, Data Transfer Service processes automatically

**No cron jobs needed. Everything runs in the cloud.**

---

*Would you like me to help you set up the Data Transfer Service transfers?*
