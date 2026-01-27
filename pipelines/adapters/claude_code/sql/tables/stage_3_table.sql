-- Stage 3 Table: claude_code_stage_3
-- Purpose: Store entities with registered entity_ids from identity_service
-- Pattern: Universal Pipeline Pattern - Stage 3 (System ID Registration - THE GATE)

CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.spine.claude_code_stage_3` (
  -- Message Identifiers
  message_id STRING NOT NULL,        -- Message ID from Stage 1
  entity_id STRING NOT NULL,         -- Entity ID (registered in identity_service)

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
  extracted_at TIMESTAMP,              -- Extraction timestamp from Stage 0
  enriched_at TIMESTAMP,              -- Enrichment timestamp from Stage 1
  registered_at TIMESTAMP NOT NULL,   -- Registration timestamp (Stage 3)

  -- Metadata
  metadata JSON,                      -- Additional metadata from TruthService

  -- Stage 1 Enrichment Fields
  sentiment_score FLOAT,              -- Sentiment polarity score
  sentiment_label STRING,             -- Sentiment label
  entities JSON,                      -- Extracted entities
  topics JSON,                        -- Topic classifications
  quality_score FLOAT,               -- Message quality score
  text_length INTEGER,                -- Text length in characters
  word_count INTEGER,                 -- Word count

  -- Audit Fields
  enrichment_run_id STRING,          -- Enrichment run identifier (Stage 1)
  registration_run_id STRING NOT NULL, -- Registration run identifier (Stage 3)
  stage_1_run_id STRING,             -- Stage 1 run identifier
)
PARTITION BY content_date
CLUSTER BY source_name, entity_id, level
OPTIONS(
  description="Stage 3: Entities with registered entity_ids from identity_service (THE GATE). Registers existing entity_ids from TruthService in central identity registry. All entity_ids are registered and tracked for deduplication, identity resolution, and entity matching."
);

-- Labels for cost tracking and governance
ALTER TABLE `flash-clover-464719-g1.spine.claude_code_stage_3`
SET OPTIONS (
  labels=[
    ("pipeline", "claude_code"),
    ("stage", "3"),
    ("purpose", "id_registration"),
    ("table_type", "run_table"),
    ("data_quality", "registered"),
    ("workstream", "w1_truth_service"),
    ("backup_enabled", "true")
  ]
);
