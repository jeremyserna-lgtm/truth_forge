-- Text Quality Assessment Query
-- Run this to determine if Stage 2 (Normalization) is needed
--
-- Usage: Run in BigQuery console or via bq command
-- bq query --use_legacy_sql=false < assess_text_quality.sql

SELECT
  source_name,
  COUNT(*) as total_messages,

  -- Whitespace issues
  COUNT(CASE WHEN text LIKE '%  %' THEN 1 END) as double_space_count,
  ROUND(COUNT(CASE WHEN text LIKE '%  %' THEN 1 END) * 100.0 / COUNT(*), 2) as double_space_pct,

  COUNT(CASE WHEN text LIKE '%\n\n\n%' THEN 1 END) as triple_newline_count,
  COUNT(CASE WHEN text LIKE '%\t%' THEN 1 END) as tab_count,

  -- Leading/trailing whitespace
  COUNT(CASE WHEN LENGTH(text) != LENGTH(TRIM(text)) THEN 1 END) as whitespace_trim_count,
  ROUND(COUNT(CASE WHEN LENGTH(text) != LENGTH(TRIM(text)) THEN 1 END) * 100.0 / COUNT(*), 2) as whitespace_trim_pct,

  -- Text length stats
  AVG(LENGTH(text)) as avg_length,
  MIN(LENGTH(text)) as min_length,
  MAX(LENGTH(text)) as max_length,

  -- Empty/null text
  COUNT(CASE WHEN text IS NULL OR LENGTH(TRIM(text)) = 0 THEN 1 END) as empty_text_count,

  -- Sample problematic texts (for inspection)
  ARRAY_AGG(
    CASE
      WHEN text LIKE '%  %' OR LENGTH(text) != LENGTH(TRIM(text))
      THEN text
    END
    LIMIT 5
  ) as sample_problematic_texts

FROM `flash-clover-464719-g1.spine.claude_code_stage_0`
GROUP BY source_name
ORDER BY source_name;
