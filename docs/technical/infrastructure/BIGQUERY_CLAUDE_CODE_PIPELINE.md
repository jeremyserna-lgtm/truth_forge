# BigQuery Native Pipeline: Claude Code → entity_unified

**Created**: 2026-01-28  
**Status**: Ready to Deploy  
**Project**: `flash-clover-464719-g1`  
**Dataset**: `spine`

---

## 🎯 Overview

This pipeline automatically loads data from `claude_code_stage_4` (staging table) into `entity_unified` (production table) using **BigQuery Scheduled Queries**. No Python scripts required.

---

## 📊 Current State

✅ **Source Table**: `spine.claude_code_stage_4` (8 rows, ready to process)  
✅ **Destination Table**: `spine.entity_unified` (11.8M rows, 34 fields)  
✅ **Schema**: Both tables exist and are properly configured

---

## 🔄 Pipeline Architecture

```
claude_code_stage_4 (Staging)
    ↓
BigQuery Scheduled Query (Transformation)
    ↓
entity_unified (Production)
```

**Schedule**: Daily at 2:00 AM UTC  
**Mode**: Append (adds new records, doesn't overwrite)

---

## 📝 Transformation Query

This SQL query transforms data from `claude_code_stage_4` to `entity_unified` format:

```sql
-- BigQuery Scheduled Query: Claude Code to entity_unified
-- Transforms staging data into production entity_unified format

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
  s.entity_id,
  COALESCE(s.level, 5) as level,  -- Default to level 5 (message)
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
  s.session_id as conversation_id,  -- session_id becomes conversation_id
  s.entity_id as message_id,  -- For level 5, message_id = entity_id
  NULL as topic_segment_id,
  NULL as turn_id,
  NULL as sentence_id,
  NULL as span_id,
  NULL as word_id,
  
  -- Content
  s.text,
  
  -- Source Fields
  s.source_pipeline,
  s.source_file,
  s.source_file as source_file_path,  -- Use source_file as path
  s.source_name as source_system,
  ARRAY[CAST(s.entity_id AS STRING)] as source_ids,  -- Convert to REPEATED
  
  -- Content Fields
  s.persona,
  
  -- Timestamps
  s.content_date,
  s.timestamp_utc as source_message_timestamp,
  s.created_at,
  CURRENT_TIMESTAMP() as updated_at,
  s.created_at as ingestion_timestamp,
  s.run_id as ingestion_job_id,
  
  -- Validation
  'PASSED' as validation_status,
  
  -- Metadata (JSON) - Store all enrichment fields here
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

FROM `flash-clover-464719-g1.spine.claude_code_stage_4` s
WHERE 
  -- Only process records not already in entity_unified
  s.entity_id NOT IN (
    SELECT entity_id 
    FROM `flash-clover-464719-g1.spine.entity_unified`
    WHERE source_pipeline = 'claude_code'
  )
  -- Only process records from last 7 days (adjust as needed)
  AND s.content_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
```

---

## 🚀 Setup Instructions

### Step 1: Create the Scheduled Query

1. **Open BigQuery Console**: https://console.cloud.google.com/bigquery?project=flash-clover-464719-g1

2. **Click "Compose New Query"**

3. **Paste the SQL query above**

4. **Click "Schedule"** (button in top right)

5. **Configure Schedule**:
   - **Name**: `claude_code_to_entity_unified_daily`
   - **Schedule frequency**: 
     - **Repeats**: Daily
     - **Time**: 02:00 UTC
     - **Start date**: Today
   - **Destination**:
     - **Write preference**: Append to table
     - **Table name**: `entity_unified`
     - **Dataset**: `spine`

6. **Click "Save"**

✅ **Done! The query will run automatically every day at 2 AM UTC.**

---

### Step 2: Test the Query (Optional)

Before scheduling, test the query:

1. **Run the query manually** in BigQuery Console
2. **Check results**: Verify data looks correct
3. **Check row count**: Should match expected records
4. **If successful**: Proceed to schedule it

---

### Step 3: Monitor the Pipeline

#### Check Query History

1. Go to **BigQuery Console** → **Scheduled Queries**
2. Find: `claude_code_to_entity_unified_daily`
3. Click → **History** tab
4. See all runs, success/failure, execution time

#### Check Data in entity_unified

```sql
-- Count records by source_pipeline
SELECT 
  source_pipeline,
  COUNT(*) as record_count,
  MIN(content_date) as earliest_date,
  MAX(content_date) as latest_date
FROM `flash-clover-464719-g1.spine.entity_unified`
WHERE source_pipeline = 'claude_code'
GROUP BY source_pipeline
ORDER BY source_pipeline
```

---

## 🔧 Advanced: Incremental Processing

The query above includes a `NOT IN` clause to prevent duplicates. For better performance with large datasets, consider:

### Option 1: Use MERGE Statement (Recommended for Updates)

```sql
MERGE `flash-clover-464719-g1.spine.entity_unified` AS target
USING (
  -- Same SELECT as above, but as subquery
  SELECT ... FROM `flash-clover-464719-g1.spine.claude_code_stage_4` s
  WHERE s.content_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
) AS source
ON target.entity_id = source.entity_id
WHEN NOT MATCHED THEN
  INSERT (entity_id, level, entity_type, ...)
  VALUES (source.entity_id, source.level, source.entity_type, ...)
```

### Option 2: Track Last Processed Timestamp

Create a metadata table to track last processed timestamp:

```sql
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.spine.pipeline_metadata` (
  pipeline_name STRING,
  last_processed_timestamp TIMESTAMP,
  last_processed_date DATE
);
```

Then modify the query to use this:

```sql
WHERE s.created_at > (
  SELECT COALESCE(MAX(last_processed_timestamp), TIMESTAMP('2020-01-01'))
  FROM `flash-clover-464719-g1.spine.pipeline_metadata`
  WHERE pipeline_name = 'claude_code'
)
```

---

## 📊 Pipeline Monitoring

### Create Monitoring Query

Create a scheduled query to monitor pipeline health:

```sql
-- Monitor: Claude Code Pipeline Health
SELECT
  CURRENT_TIMESTAMP() as check_time,
  'claude_code' as pipeline_name,
  (SELECT COUNT(*) FROM `flash-clover-464719-g1.spine.claude_code_stage_4`) as stage4_count,
  (SELECT COUNT(*) FROM `flash-clover-464719-g1.spine.entity_unified` WHERE source_pipeline = 'claude_code') as entity_unified_count,
  (SELECT MAX(content_date) FROM `flash-clover-464719-g1.spine.entity_unified` WHERE source_pipeline = 'claude_code') as latest_date,
  (SELECT COUNT(*) FROM `flash-clover-464719-g1.spine.claude_code_stage_4` WHERE content_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)) as recent_stage4_count
```

Schedule this to run **after** the main pipeline (e.g., 2:30 AM) to verify success.

---

## 🎯 Next Steps

1. ✅ **Create the scheduled query** (Step 1 above)
2. ✅ **Test it manually** first
3. ✅ **Monitor first few runs** to ensure it works
4. ✅ **Set up monitoring query** (optional but recommended)
5. ✅ **Adjust schedule** if needed (frequency, time)

---

## 🆘 Troubleshooting

### Query Fails with "Table not found"

**Fix**: Verify table names are correct:
- Source: `flash-clover-464719-g1.spine.claude_code_stage_4`
- Destination: `flash-clover-464719-g1.spine.entity_unified`

### Query Fails with "Schema mismatch"

**Fix**: Check that field types match. The query above handles type conversions, but verify:
- `level` is INTEGER
- `content_date` is DATE
- `metadata` is JSON

### No Data Appearing

**Check**:
1. Does `claude_code_stage_4` have new data?
2. Is the `NOT IN` clause excluding all records? (Remove it temporarily to test)
3. Is the date filter too restrictive?

### Duplicate Records

**Fix**: The `NOT IN` clause should prevent duplicates. If you see duplicates:
1. Check if `entity_id` is unique in `claude_code_stage_4`
2. Consider using MERGE instead of INSERT

---

## ✅ Success Criteria

You'll know it's working when:

- [ ] Scheduled query appears in "Scheduled Queries" list
- [ ] Query runs successfully (check History tab)
- [ ] New records appear in `entity_unified` with `source_pipeline = 'claude_code'`
- [ ] No duplicate records
- [ ] Data looks correct (spot check a few records)

---

## 📚 Related Documentation

- **BigQuery Scheduled Queries**: https://cloud.google.com/bigquery/docs/scheduling-queries
- **BigQuery MERGE**: https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax#merge_statement
- **entity_unified Schema**: `pipelines/adapters/claude_code/reports/ENTITY_UNIFIED_COMPLETE_SPECIFICATION.md`

---

*This pipeline replaces custom Python scripts with native BigQuery features. It runs automatically, handles errors, and requires zero maintenance.*
