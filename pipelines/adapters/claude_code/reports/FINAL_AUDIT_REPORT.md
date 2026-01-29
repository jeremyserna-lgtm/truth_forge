================================================================================
COMPREHENSIVE PIPELINE AUDIT REPORT
================================================================================

Total Issues Found: 23


================================================================================
ERROR_HANDLING (1 issues)
================================================================================

MEDIUM Severity (1 issues):
--------------------------------------------------------------------------------
  Stage 16: Error messages may be too technical for non-coders


================================================================================
IMPORT_ERROR (2 issues)
================================================================================

HIGH Severity (2 issues):
--------------------------------------------------------------------------------
  Stage 0: Missing central_services module
    File: claude_code_stage_0.py:72
    Code: from src.services.central_services.core import (  # noqa: E402

  Stage 0: Missing central_services module
    File: claude_code_stage_0.py:76
    Code: from src.services.central_services.core.pipeline_tracker import (  # noqa: E402


================================================================================
PARSE_ERROR (7 issues)
================================================================================

CRITICAL Severity (7 issues):
--------------------------------------------------------------------------------
  Stage 8: Failed to parse file: invalid syntax (claude_code_stage_8.py, line 93)

  Stage 9: Failed to parse file: invalid syntax (claude_code_stage_9.py, line 92)

  Stage 10: Failed to parse file: invalid syntax (claude_code_stage_10.py, line 100)

  Stage 11: Failed to parse file: invalid syntax (claude_code_stage_11.py, line 93)

  Stage 12: Failed to parse file: invalid syntax (claude_code_stage_12.py, line 92)

  Stage 13: Failed to parse file: invalid syntax (claude_code_stage_13.py, line 100)

  Stage 15: Failed to parse file: invalid syntax (claude_code_stage_15.py, line 99)


================================================================================
SQL_INJECTION (13 issues)
================================================================================

CRITICAL Severity (13 issues):
--------------------------------------------------------------------------------
  Stage 2: Unvalidated timestamp interpolation
    File: claude_code_stage_2.py:312
    Code: TIMESTAMP('{cleaned_at}') AS cleaned_at,

  Stage 2: Unvalidated table ID in SELECT
    File: claude_code_stage_2.py:321
    Code: count_query = f"SELECT COUNT(*) as cnt FROM `{validated_stage_1_table}`"

  Stage 3: Unvalidated table ID in SELECT
    File: claude_code_stage_3.py:279
    Code: count_query = f"SELECT COUNT(*) as cnt FROM `{validated_stage_2_table}` WHERE NO

  Stage 4: Unvalidated timestamp interpolation
    File: claude_code_stage_4.py:271
    Code: TIMESTAMP('{created_at}') AS created_at,

  Stage 4: Unvalidated table ID in SELECT
    File: claude_code_stage_4.py:289
    Code: count_query = f"SELECT COUNT(*) as cnt FROM `{validated_stage_3_table}` WHERE ru

  Stage 4: Unvalidated table ID in SELECT
    File: claude_code_stage_4.py:309
    Code: count_query = f"SELECT COUNT(*) as cnt FROM `{validated_stage_4_table}` WHERE ru

  Stage 5: Unvalidated table ID in SELECT
    File: claude_code_stage_5.py:300
    Code: count_query = f"SELECT COUNT(*) as cnt FROM `{validated_stage_4_table}` WHERE te

  Stage 6: Unvalidated table ID in SELECT
    File: claude_code_stage_6.py:213
    Code: query = f"SELECT entity_id, text, session_id, content_date FROM `{validated_stag

  Stage 14: Unvalidated timestamp interpolation
    File: claude_code_stage_14.py:246
    Code: TIMESTAMP('{aggregated_at}') as aggregated_at,

  Stage 14: Unvalidated table ID in SELECT
    File: claude_code_stage_14.py:265
    Code: count_query = f"SELECT COUNT(*) as cnt FROM `{validated_stage_7_table}`"

  Stage 14: Unvalidated timestamp interpolation
    File: claude_code_stage_14.py:295
    Code: TIMESTAMP('{aggregated_at}') as aggregated_at,

  Stage 14: Unvalidated table ID in SELECT
    File: claude_code_stage_14.py:307
    Code: count_query = f"SELECT COUNT(*) as cnt FROM `{validated_stage_14_table}` WHERE r

  Stage 16: Unvalidated value in WHERE clause
    File: claude_code_stage_16.py:214
    Code: WHERE {status_filter}
