-- BigQuery Scheduled Query: Claude Code to entity_unified
-- Transforms staging data from claude_code_stage_4 into production entity_unified format
-- Schedule: Daily at 2:00 AM UTC
-- Mode: Append (adds new records)

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
  CAST(NULL AS STRING) as topic_segment_id,
  CAST(NULL AS STRING) as turn_id,
  CAST(NULL AS STRING) as sentence_id,
  CAST(NULL AS STRING) as span_id,
  CAST(NULL AS STRING) as word_id,
  
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
