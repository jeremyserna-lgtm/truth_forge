-- Stage 4 Table: claude_code_stage_4
-- Purpose: Store all text corrections from LLM processing
-- Pattern: Universal Pipeline Pattern - Stage 4 (LLM Text Correction)

CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.spine.claude_code_stage_4` (
  -- Entity Identifiers
  entity_id STRING NOT NULL,         -- Entity ID from Stage 3
  source_name STRING,                -- Source identifier (claude_code, codex, github)

  -- Text Correction
  original_text STRING,              -- Original text from Stage 3
  corrected_text STRING,             -- LLM-corrected text
  correction_applied BOOLEAN,        -- Whether correction was applied
  is_ready BOOLEAN,                  -- Whether text is ready for NLP processing

  -- Audit Fields
  run_id STRING NOT NULL,           -- Run ID for traceability
  created_at TIMESTAMP NOT NULL,    -- Creation timestamp
)
PARTITION BY DATE(created_at)
CLUSTER BY source_name, entity_id
OPTIONS(
  description="Stage 4: All text corrections from LLM processing. Every message gets a Stage 4 record with original_text, corrected_text, and correction status. Used for tracking corrections and quality assessment."
);

-- Labels for cost tracking and governance
ALTER TABLE `flash-clover-464719-g1.spine.claude_code_stage_4`
SET OPTIONS (
  labels=[
    ("pipeline", "claude_code"),
    ("stage", "4"),
    ("purpose", "llm_text_correction"),
    ("table_type", "run_table"),
    ("data_quality", "corrected"),
    ("workstream", "w1_truth_service"),
    ("backup_enabled", "true")
  ]
);
