# BigQuery Pipeline: GCS → entity_unified

**Created**: 2026-01-28  
**Status**: Ready to Deploy  
**Project**: `flash-clover-464719-g1`  
**Dataset**: `spine`  
**Source Bucket**: `claude_code_pipeline_source`

---

## 🎯 Overview

This pipeline automatically loads JSONL files from Cloud Storage bucket `claude_code_pipeline_source` and transforms them into `entity_unified`. 

**Two approaches provided:**
1. **BigQuery Data Transfer Service** (Recommended - fully managed)
2. **Scheduled Query with External Table** (Alternative - more control)

---

## 📊 Architecture

```
Cloud Storage (claude_code_pipeline_source/*.jsonl)
    ↓
BigQuery Data Transfer Service (Automatic Load)
    ↓
Staging Table (claude_code_stage_4_raw)
    ↓
BigQuery Scheduled Query (Transformation)
    ↓
entity_unified (Production)
```

---

## ✅ Option 1: BigQuery Data Transfer Service (Recommended)

### Step 1: Set Up Data Transfer Service

1. **Open BigQuery Console**: https://console.cloud.google.com/bigquery?project=flash-clover-464719-g1

2. **Go to Data Transfers**: Click "Data Transfers" in left sidebar

3. **Create Transfer**: Click "Create Transfer"

4. **Select Source**: Choose "Cloud Storage"

5. **Configure Transfer**:
   - **Display name**: `claude_code_gcs_to_staging`
   - **Source URI**: `gs://claude_code_pipeline_source/*.jsonl`
   - **Destination dataset**: `spine`
   - **Destination table**: `claude_code_stage_4_raw` (will be created)
   - **File format**: JSON (Newline delimited)
   - **Write preference**: Append
   - **Schema**: Auto-detect (or upload schema file)

6. **Schedule**:
   - **Schedule starts**: Today
   - **Repeats**: Daily
   - **Time**: 1:00 AM UTC (before transformation query)

7. **Click "Save"**

✅ **Data Transfer Service will automatically load files from GCS daily.**

---

### Step 2: Create Transformation Query

Create a scheduled query to transform from staging to entity_unified:

**SQL Query** (see file: `claude_code_gcs_to_entity_unified.sql`):

```sql
-- Transform from staging table to entity_unified
INSERT INTO `flash-clover-464719-g1.spine.entity_unified` (
  entity_id,
  level,
  entity_type,
  entity_mode,
  parent_id,
  conversation_id,
  message_id,
  text,
  source_pipeline,
  source_file,
  source_file_path,
  source_system,
  source_ids,
  persona,
  content_date,
  source_message_timestamp,
  created_at,
  updated_at,
  ingestion_timestamp,
  ingestion_job_id,
  validation_status,
  metadata
)
SELECT
  -- Identity Fields
  COALESCE(s.entity_id, GENERATE_UUID()) as entity_id,
  COALESCE(s.level, 5) as level,
  CASE 
    WHEN s.level = 1 THEN 'token'
    WHEN s.level = 3 THEN 'sentence'
    WHEN s.level = 4 THEN 'sentence'
    WHEN s.level = 5 THEN 'message'
    WHEN s.level = 8 THEN 'conversation'
    ELSE 'message'
  END as entity_type,
  'active' as entity_mode,
  s.parent_id,
  
  -- Hierarchical IDs
  s.session_id as conversation_id,
  s.entity_id as message_id,
  CAST(NULL AS STRING) as topic_segment_id,
  CAST(NULL AS STRING) as turn_id,
  CAST(NULL AS STRING) as sentence_id,
  CAST(NULL AS STRING) as span_id,
  CAST(NULL AS STRING) as word_id,
  
  -- Content
  s.text,
  
  -- Source Fields
  COALESCE(s.source_pipeline, 'claude_code') as source_pipeline,
  s.source_file,
  s.source_file as source_file_path,
  COALESCE(s.source_name, 'claude_code') as source_system,
  ARRAY[CAST(COALESCE(s.entity_id, GENERATE_UUID()) AS STRING)] as source_ids,
  
  -- Content Fields
  s.persona,
  
  -- Timestamps
  COALESCE(s.content_date, CURRENT_DATE()) as content_date,
  s.timestamp_utc as source_message_timestamp,
  COALESCE(s.created_at, CURRENT_TIMESTAMP()) as created_at,
  CURRENT_TIMESTAMP() as updated_at,
  COALESCE(s.created_at, CURRENT_TIMESTAMP()) as ingestion_timestamp,
  COALESCE(s.run_id, CAST(CURRENT_TIMESTAMP() AS STRING)) as ingestion_job_id,
  
  -- Validation
  'PASSED' as validation_status,
  
  -- Metadata (JSON)
  JSON_OBJECT(
    'role', s.role,
    'message_type', s.message_type,
    'message_index', s.message_index,
    'content_length', s.content_length,
    'word_count', s.word_count,
    'model', s.model,
    'cost_usd', s.cost_usd,
    'tool_name', s.tool_name,
    'tool_input', s.tool_input,
    'tool_output', s.tool_output,
    'fingerprint', s.fingerprint,
    'source_name', s.source_name
  ) as metadata

FROM `flash-clover-464719-g1.spine.claude_code_stage_4_raw` s
WHERE 
  -- Only process records not already in entity_unified
  s.entity_id NOT IN (
    SELECT entity_id 
    FROM `flash-clover-464719-g1.spine.entity_unified`
    WHERE source_pipeline = 'claude_code'
  )
  -- Only process records from last 7 days
  AND COALESCE(s.content_date, CURRENT_DATE()) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
```

**Schedule this query**:
1. Click "Schedule" in BigQuery Console
2. **Name**: `claude_code_gcs_to_entity_unified`
3. **Schedule**: Daily at 2:00 AM UTC (after Data Transfer runs)
4. **Destination**: Append to `spine.entity_unified`
5. **Save**

---

## ✅ Option 2: External Table + Scheduled Query (Alternative)

If you prefer more control, use an External Table:

### Step 1: Create External Table

```sql
-- Create external table pointing to GCS bucket
CREATE OR REPLACE EXTERNAL TABLE `flash-clover-464719-g1.spine.claude_code_external` (
  entity_id STRING,
  parent_id STRING,
  source_name STRING,
  source_pipeline STRING,
  level INTEGER,
  text STRING,
  session_id STRING,
  message_index INTEGER,
  message_type STRING,
  role STRING,
  persona STRING,
  content_length INTEGER,
  word_count INTEGER,
  model STRING,
  cost_usd FLOAT64,
  tool_name STRING,
  tool_input STRING,
  tool_output STRING,
  source_file STRING,
  content_date DATE,
  timestamp_utc TIMESTAMP,
  created_at TIMESTAMP,
  metadata STRING,
  fingerprint STRING,
  run_id STRING
)
OPTIONS (
  format = 'JSON',
  uris = ['gs://claude_code_pipeline_source/*.jsonl']
);
```

### Step 2: Create Scheduled Query to Load from External Table

```sql
-- Load from external table to staging, then to entity_unified
INSERT INTO `flash-clover-464719-g1.spine.entity_unified` (
  -- Same fields as Option 1
  ...
)
SELECT
  -- Same transformation as Option 1
  ...
FROM `flash-clover-464719-g1.spine.claude_code_external` s
WHERE 
  -- Same filters as Option 1
  ...
```

---

## 📤 Uploading Files to GCS

When you have JSONL files to process:

```bash
# Upload single file
gsutil cp local_file.jsonl gs://claude_code_pipeline_source/

# Upload all JSONL files from directory
gsutil -m cp /path/to/files/*.jsonl gs://claude_code_pipeline_source/

# Upload with folder structure
gsutil -m rsync -r /local/path/ gs://claude_code_pipeline_source/
```

**Note**: BigQuery Data Transfer Service will automatically detect new files and load them on schedule.

---

## 🔍 Monitoring

### Check Data Transfer Status

1. BigQuery Console → **Data Transfers**
2. Click on `claude_code_gcs_to_staging`
3. **Transfer History** tab
4. See all runs, success/failure, records loaded

### Check Staging Table

```sql
-- Check what's in staging
SELECT 
  COUNT(*) as total_records,
  COUNT(DISTINCT entity_id) as unique_entities,
  MIN(content_date) as earliest_date,
  MAX(content_date) as latest_date,
  COUNT(DISTINCT source_file) as unique_files
FROM `flash-clover-464719-g1.spine.claude_code_stage_4_raw`
```

### Check entity_unified

```sql
-- Check Claude Code records in entity_unified
SELECT 
  COUNT(*) as total_records,
  COUNT(DISTINCT entity_id) as unique_entities,
  MIN(content_date) as earliest_date,
  MAX(content_date) as latest_date
FROM `flash-clover-464719-g1.spine.entity_unified`
WHERE source_pipeline = 'claude_code'
```

---

## 🎯 Recommended Setup

**Use Option 1 (Data Transfer Service)** because:
- ✅ Fully managed by Google
- ✅ Automatic file detection
- ✅ Built-in error handling
- ✅ No code required
- ✅ Handles schema evolution

**Schedule**:
- **1:00 AM UTC**: Data Transfer Service loads from GCS
- **2:00 AM UTC**: Transformation query runs

---

## 🚀 Quick Start

1. **Upload a test file** to `gs://claude_code_pipeline_source/test.jsonl`
2. **Set up Data Transfer Service** (Option 1, Step 1)
3. **Test transfer manually**: Click "Run Now" on the transfer
4. **Verify staging table**: Check `claude_code_stage_4_raw` has data
5. **Set up transformation query** (Option 1, Step 2)
6. **Test transformation**: Run query manually
7. **Schedule both**: Set up automatic runs

---

## 📚 Related Files

- **Transformation SQL**: `pipelines/adapters/claude_code/sql/scheduled_queries/claude_code_gcs_to_entity_unified.sql`
- **Setup Guide**: `docs/technical/infrastructure/BIGQUERY_CLAUDE_CODE_PIPELINE.md`
- **Quick Start**: `docs/technical/infrastructure/BIGQUERY_PIPELINE_READY.md`

---

*This pipeline automatically processes files from Cloud Storage and loads them into entity_unified. No Python scripts required.*
