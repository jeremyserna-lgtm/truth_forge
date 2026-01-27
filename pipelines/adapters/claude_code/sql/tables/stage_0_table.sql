-- Stage 0 Table: claude_code_stage_0
-- Purpose: Store extracted messages from TruthService (entity_unified) for Claude Code, Codex, and Github sources
-- Pattern: Universal Pipeline Pattern - Stage 0 (Message Extraction)

CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.spine.claude_code_stage_0` (
  -- Message Identifiers
  message_id STRING NOT NULL,        -- Entity ID from TruthService (used as message_id)
  entity_id STRING NOT NULL,         -- Entity ID from TruthService

  -- Source Information
  source_name STRING NOT NULL,       -- Source identifier (claude_code, codex, github)
  source_pipeline STRING,             -- Pipeline identifier
  source_file STRING,                -- Source file path

  -- Message Content
  text STRING NOT NULL,               -- Message text content
  level INTEGER NOT NULL,             -- Entity level (5 for messages)

  -- Timestamps
  content_date DATE,                  -- Content date (partitioned)
  created_at TIMESTAMP,               -- Original creation timestamp
  extracted_at TIMESTAMP NOT NULL,   -- Extraction timestamp

  -- Metadata
  metadata JSON,                      -- Additional metadata from TruthService

  -- Audit Fields
  run_id STRING,                      -- Run identifier for traceability
)
PARTITION BY content_date
CLUSTER BY source_name, level
OPTIONS(
  description="Stage 0: Extracted messages from TruthService for Claude Code, Codex, and Github sources. Extracts level 5 entities (messages) from entity_unified table."
);

-- Labels for cost tracking and governance
ALTER TABLE `flash-clover-464719-g1.spine.claude_code_stage_0`
SET OPTIONS (
  labels=[
    ("pipeline", "claude_code"),
    ("stage", "0"),
    ("purpose", "message_extraction"),
    ("table_type", "run_table"),
    ("data_quality", "raw"),
    ("workstream", "w1_truth_service"),
    ("backup_enabled", "true")
  ]
);
