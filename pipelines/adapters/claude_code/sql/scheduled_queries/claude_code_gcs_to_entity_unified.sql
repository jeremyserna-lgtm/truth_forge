-- BigQuery Scheduled Query: GCS External Table to entity_unified
-- Transforms data from claude_code_external (GCS JSONL files) into entity_unified format
-- Schedule: Daily at 2:00 AM UTC (after cron sync runs at 1:00 AM)
-- Mode: Append (adds new records)

INSERT INTO `flash-clover-464719-g1.spine.entity_unified` (
  entity_id,
  level,
  entity_type,
  entity_mode,
  parent_id,
  source_ids,
  conversation_id,
  topic_segment_id,
  turn_id,
  message_id,
  sentence_id,
  span_id,
  word_id,
  text,
  source_pipeline,
  source_file,
  source_file_path,
  source_system,
  metadata,
  created_at,
  updated_at,
  ingestion_job_id,
  ingestion_timestamp,
  validation_status,
  source_message_timestamp,
  persona,
  content_date,
  canonical_form,
  l7_count,
  l6_count,
  l5_count,
  l4_count,
  l3_count,
  l2_count
)
SELECT
  -- Identity Fields
  COALESCE(s.entity_id, GENERATE_UUID()) as entity_id,
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
  ARRAY[CAST(COALESCE(s.entity_id, GENERATE_UUID()) AS STRING)] as source_ids,  -- Convert to REPEATED
  
  -- Hierarchical IDs
  s.session_id as conversation_id,  -- session_id becomes conversation_id
  CAST(NULL AS STRING) as topic_segment_id,
  CAST(NULL AS STRING) as turn_id,
  COALESCE(s.entity_id, GENERATE_UUID()) as message_id,  -- For level 5, message_id = entity_id
  CAST(NULL AS STRING) as sentence_id,
  CAST(NULL AS STRING) as span_id,
  CAST(NULL AS STRING) as word_id,
  
  -- Content
  s.text,
  
  -- Source Fields
  COALESCE(s.source_pipeline, 'claude_code') as source_pipeline,
  s.source_file,
  s.source_file as source_file_path,  -- Use source_file as path
  COALESCE(s.source_name, 'claude_code') as source_system,
  
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
  ) as metadata,
  
  -- Timestamps
  COALESCE(s.created_at, CURRENT_TIMESTAMP()) as created_at,
  CURRENT_TIMESTAMP() as updated_at,
  COALESCE(s.run_id, CAST(CURRENT_TIMESTAMP() AS STRING)) as ingestion_job_id,
  COALESCE(s.created_at, CURRENT_TIMESTAMP()) as ingestion_timestamp,
  
  -- Validation
  'PASSED' as validation_status,
  s.timestamp_utc as source_message_timestamp,
  
  -- Content Fields
  s.persona,
  COALESCE(s.content_date, CURRENT_DATE()) as content_date,
  
  -- Count fields (set to NULL for now, can be calculated later)
  CAST(NULL AS STRING) as canonical_form,
  CAST(NULL AS INT64) as l7_count,
  CAST(NULL AS INT64) as l6_count,
  CAST(NULL AS INT64) as l5_count,
  CAST(NULL AS INT64) as l4_count,
  CAST(NULL AS INT64) as l3_count,
  CAST(NULL AS INT64) as l2_count

FROM `flash-clover-464719-g1.spine.claude_code_external` s
WHERE 
  -- Only process records not already in entity_unified
  COALESCE(s.entity_id, GENERATE_UUID()) NOT IN (
    SELECT entity_id 
    FROM `flash-clover-464719-g1.spine.entity_unified`
    WHERE source_pipeline = 'claude_code'
  )
  -- Only process records from last 7 days (adjust as needed)
  AND COALESCE(s.content_date, CURRENT_DATE()) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
