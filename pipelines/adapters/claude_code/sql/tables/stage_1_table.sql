-- Stage 1 Table: claude_code_stage_1
-- Purpose: Store enriched messages with sentiment, entities, topics, and quality scores
-- Pattern: Universal Pipeline Pattern - Stage 1 (Message Enrichment)

CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.spine.claude_code_stage_1` (
  -- Message Identifiers (from Stage 0)
  message_id STRING NOT NULL,        -- Entity ID from TruthService
  entity_id STRING NOT NULL,         -- Entity ID from TruthService

  -- Source Information (from Stage 0)
  source_name STRING NOT NULL,       -- Source identifier (claude_code, codex, github)
  source_pipeline STRING,             -- Pipeline identifier
  source_file STRING,                -- Source file path

  -- Message Content (from Stage 0)
  text STRING NOT NULL,               -- Message text content
  level INTEGER NOT NULL,             -- Entity level (5 for messages)

  -- Timestamps (from Stage 0)
  content_date DATE,                  -- Content date (partitioned)
  created_at TIMESTAMP,               -- Original creation timestamp
  extracted_at TIMESTAMP,             -- Extraction timestamp from Stage 0

  -- Metadata (from Stage 0)
  metadata JSON,                      -- Additional metadata from TruthService

  -- Audit Fields (from Stage 0)
  run_id STRING,                      -- Run identifier from Stage 0

  -- Stage 1 Enrichment Fields
  sentiment_score FLOAT,              -- Sentiment polarity score (-1.0 to 1.0)
  sentiment_label STRING,             -- Sentiment label (positive, negative, neutral)
  entities JSON,                      -- Extracted entities (JSON array)
  topics JSON,                        -- Topic classifications (JSON array)
  quality_score FLOAT,               -- Message quality score (0.0 to 1.0)
  text_length INTEGER,                -- Text length in characters
  word_count INTEGER,                 -- Word count

  -- Stage 1 Audit Fields
  enriched_at TIMESTAMP NOT NULL,     -- Enrichment timestamp
  enrichment_run_id STRING,          -- Enrichment run identifier
)
PARTITION BY content_date
CLUSTER BY source_name, sentiment_label
OPTIONS(
  description="Stage 1: Enriched messages with sentiment analysis, entity extraction, topic classification, and quality scoring. Adds enrichment data to Stage 0 messages for downstream analysis."
);

-- Labels for cost tracking and governance
ALTER TABLE `flash-clover-464719-g1.spine.claude_code_stage_1`
SET OPTIONS (
  labels=[
    ("pipeline", "claude_code"),
    ("stage", "1"),
    ("purpose", "message_enrichment"),
    ("table_type", "run_table"),
    ("data_quality", "enriched"),
    ("workstream", "w1_truth_service"),
    ("backup_enabled", "true")
  ]
);
