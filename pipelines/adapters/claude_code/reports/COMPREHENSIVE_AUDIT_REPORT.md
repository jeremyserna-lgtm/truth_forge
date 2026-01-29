================================================================================
COMPREHENSIVE PIPELINE AUDIT REPORT
================================================================================

Total Issues Found: 139


================================================================================
DUPLICATE_PREVENTION (12 issues)
================================================================================

CRITICAL Severity (1 issues):
--------------------------------------------------------------------------------
  Stage 4: Stage 4 uses CREATE OR REPLACE which causes data loss on re-runs


HIGH Severity (11 issues):
--------------------------------------------------------------------------------
  Stage 5: Stage 5 uses insert_rows_json without MERGE or duplicate prevention

  Stage 6: Stage 6 uses insert_rows_json without MERGE or duplicate prevention

  Stage 7: Stage 7 uses insert_rows_json without MERGE or duplicate prevention

  Stage 8: Stage 8 uses insert_rows_json without MERGE or duplicate prevention

  Stage 9: Stage 9 uses insert_rows_json without MERGE or duplicate prevention

  Stage 10: Stage 10 uses insert_rows_json without MERGE or duplicate prevention

  Stage 11: Stage 11 uses insert_rows_json without MERGE or duplicate prevention

  Stage 12: Stage 12 uses insert_rows_json without MERGE or duplicate prevention

  Stage 13: Stage 13 uses insert_rows_json without MERGE or duplicate prevention

  Stage 15: Stage 15 uses insert_rows_json without MERGE or duplicate prevention

  Stage 16: Stage 16 uses insert_rows_json without MERGE or duplicate prevention


================================================================================
ERROR_HANDLING (16 issues)
================================================================================

MEDIUM Severity (16 issues):
--------------------------------------------------------------------------------
  Stage 1: Error messages may be too technical for non-coders

  Stage 2: Error messages may be too technical for non-coders

  Stage 3: Error messages may be too technical for non-coders

  Stage 4: Error messages may be too technical for non-coders

  Stage 5: Error messages may be too technical for non-coders

  Stage 6: Error messages may be too technical for non-coders

  Stage 7: Error messages may be too technical for non-coders

  Stage 8: Error messages may be too technical for non-coders

  Stage 9: Error messages may be too technical for non-coders

  Stage 10: Error messages may be too technical for non-coders

  Stage 11: Error messages may be too technical for non-coders

  Stage 12: Error messages may be too technical for non-coders

  Stage 13: Error messages may be too technical for non-coders

  Stage 14: Error messages may be too technical for non-coders

  Stage 15: Error messages may be too technical for non-coders

  Stage 16: Error messages may be too technical for non-coders


================================================================================
IMPORT_ERROR (99 issues)
================================================================================

HIGH Severity (99 issues):
--------------------------------------------------------------------------------
  Stage 0: Missing central_services module
    File: claude_code_stage_0.py:72
    Code: from src.services.central_services.core import (  # noqa: E402

  Stage 0: Missing central_services module
    File: claude_code_stage_0.py:76
    Code: from src.services.central_services.core.pipeline_tracker import (  # noqa: E402

  Stage 1: get_logger not in truth_forge.core
    File: claude_code_stage_1.py:102
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 1: Missing central_services module
    File: claude_code_stage_1.py:104
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 1: Missing central_services module
    File: claude_code_stage_1.py:137
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 1: Missing central_services module
    File: claude_code_stage_1.py:138
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 1: Missing central_services module
    File: claude_code_stage_1.py:139
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 1: Missing central_services module
    File: claude_code_stage_1.py:140
    Code: from src.services.central_services.governance.governance import (

  Stage 2: get_logger not in truth_forge.core
    File: claude_code_stage_2.py:102
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 2: Missing central_services module
    File: claude_code_stage_2.py:104
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 2: Missing central_services module
    File: claude_code_stage_2.py:136
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 2: Missing central_services module
    File: claude_code_stage_2.py:137
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 2: Missing central_services module
    File: claude_code_stage_2.py:138
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 2: Missing central_services module
    File: claude_code_stage_2.py:139
    Code: from src.services.central_services.governance.governance import (

  Stage 3: get_logger not in truth_forge.core
    File: claude_code_stage_3.py:55
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 3: Missing central_services module
    File: claude_code_stage_3.py:57
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 3: Missing central_services module
    File: claude_code_stage_3.py:90
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 3: Missing central_services module
    File: claude_code_stage_3.py:91
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 3: Missing central_services module
    File: claude_code_stage_3.py:92
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 3: Missing central_services module
    File: claude_code_stage_3.py:93
    Code: from src.services.central_services.governance.governance import (

  Stage 3: Missing central_services module
    File: claude_code_stage_3.py:96
    Code: from src.services.central_services.identity_service.service import (

  Stage 4: get_logger not in truth_forge.core
    File: claude_code_stage_4.py:102
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 4: Missing central_services module
    File: claude_code_stage_4.py:104
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 4: Missing central_services module
    File: claude_code_stage_4.py:137
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 4: Missing central_services module
    File: claude_code_stage_4.py:138
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 4: Missing central_services module
    File: claude_code_stage_4.py:139
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 4: Missing central_services module
    File: claude_code_stage_4.py:140
    Code: from src.services.central_services.governance.governance import (

  Stage 5: get_logger not in truth_forge.core
    File: claude_code_stage_5.py:100
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 5: Missing central_services module
    File: claude_code_stage_5.py:102
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 5: Missing central_services module
    File: claude_code_stage_5.py:138
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 5: Missing central_services module
    File: claude_code_stage_5.py:139
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 5: Missing central_services module
    File: claude_code_stage_5.py:140
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 5: Missing central_services module
    File: claude_code_stage_5.py:141
    Code: from src.services.central_services.governance.governance import (

  Stage 6: get_logger not in truth_forge.core
    File: claude_code_stage_6.py:66
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 6: Missing central_services module
    File: claude_code_stage_6.py:68
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 6: Missing central_services module
    File: claude_code_stage_6.py:103
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 6: Missing central_services module
    File: claude_code_stage_6.py:104
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 6: Missing central_services module
    File: claude_code_stage_6.py:105
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 6: Missing central_services module
    File: claude_code_stage_6.py:106
    Code: from src.services.central_services.governance.governance import require_diagnost

  Stage 7: get_logger not in truth_forge.core
    File: claude_code_stage_7.py:68
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 7: Missing central_services module
    File: claude_code_stage_7.py:70
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 7: Missing central_services module
    File: claude_code_stage_7.py:103
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 7: Missing central_services module
    File: claude_code_stage_7.py:104
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 7: Missing central_services module
    File: claude_code_stage_7.py:105
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 7: Missing central_services module
    File: claude_code_stage_7.py:106
    Code: from src.services.central_services.governance.governance import require_diagnost

  Stage 8: get_logger not in truth_forge.core
    File: claude_code_stage_8.py:68
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 8: Missing central_services module
    File: claude_code_stage_8.py:70
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 8: Missing central_services module
    File: claude_code_stage_8.py:104
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 8: Missing central_services module
    File: claude_code_stage_8.py:105
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 8: Missing central_services module
    File: claude_code_stage_8.py:106
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 8: Missing central_services module
    File: claude_code_stage_8.py:107
    Code: from src.services.central_services.governance.governance import require_diagnost

  Stage 9: get_logger not in truth_forge.core
    File: claude_code_stage_9.py:68
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 9: Missing central_services module
    File: claude_code_stage_9.py:70
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 9: Missing central_services module
    File: claude_code_stage_9.py:103
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 9: Missing central_services module
    File: claude_code_stage_9.py:104
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 9: Missing central_services module
    File: claude_code_stage_9.py:105
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 9: Missing central_services module
    File: claude_code_stage_9.py:106
    Code: from src.services.central_services.governance.governance import require_diagnost

  Stage 10: get_logger not in truth_forge.core
    File: claude_code_stage_10.py:74
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 10: Missing central_services module
    File: claude_code_stage_10.py:76
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 10: Missing central_services module
    File: claude_code_stage_10.py:111
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 10: Missing central_services module
    File: claude_code_stage_10.py:112
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 10: Missing central_services module
    File: claude_code_stage_10.py:113
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 10: Missing central_services module
    File: claude_code_stage_10.py:114
    Code: from src.services.central_services.governance.governance import require_diagnost

  Stage 11: get_logger not in truth_forge.core
    File: claude_code_stage_11.py:68
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 11: Missing central_services module
    File: claude_code_stage_11.py:70
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 11: Missing central_services module
    File: claude_code_stage_11.py:103
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 11: Missing central_services module
    File: claude_code_stage_11.py:104
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 11: Missing central_services module
    File: claude_code_stage_11.py:105
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 11: Missing central_services module
    File: claude_code_stage_11.py:106
    Code: from src.services.central_services.governance.governance import require_diagnost

  Stage 12: get_logger not in truth_forge.core
    File: claude_code_stage_12.py:68
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 12: Missing central_services module
    File: claude_code_stage_12.py:70
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 12: Missing central_services module
    File: claude_code_stage_12.py:102
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 12: Missing central_services module
    File: claude_code_stage_12.py:103
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 12: Missing central_services module
    File: claude_code_stage_12.py:104
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 12: Missing central_services module
    File: claude_code_stage_12.py:105
    Code: from src.services.central_services.governance.governance import require_diagnost

  Stage 13: get_logger not in truth_forge.core
    File: claude_code_stage_13.py:74
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 13: Missing central_services module
    File: claude_code_stage_13.py:76
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 13: Missing central_services module
    File: claude_code_stage_13.py:112
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 13: Missing central_services module
    File: claude_code_stage_13.py:113
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 13: Missing central_services module
    File: claude_code_stage_13.py:114
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 13: Missing central_services module
    File: claude_code_stage_13.py:115
    Code: from src.services.central_services.governance.governance import require_diagnost

  Stage 14: get_logger not in truth_forge.core
    File: claude_code_stage_14.py:68
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 14: Missing central_services module
    File: claude_code_stage_14.py:70
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 14: Missing central_services module
    File: claude_code_stage_14.py:104
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 14: Missing central_services module
    File: claude_code_stage_14.py:105
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 14: Missing central_services module
    File: claude_code_stage_14.py:106
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 14: Missing central_services module
    File: claude_code_stage_14.py:107
    Code: from src.services.central_services.governance.governance import require_diagnost

  Stage 15: get_logger not in truth_forge.core
    File: claude_code_stage_15.py:74
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 15: Missing central_services module
    File: claude_code_stage_15.py:76
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 15: Missing central_services module
    File: claude_code_stage_15.py:108
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 15: Missing central_services module
    File: claude_code_stage_15.py:109
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 15: Missing central_services module
    File: claude_code_stage_15.py:110
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 15: Missing central_services module
    File: claude_code_stage_15.py:111
    Code: from src.services.central_services.governance.governance import require_diagnost

  Stage 16: get_logger not in truth_forge.core
    File: claude_code_stage_16.py:68
    Code: from truth_forge.core import get_logger as _get_logger

  Stage 16: Missing central_services module
    File: claude_code_stage_16.py:70
    Code: from src.services.central_services.core import get_logger as _get_logger

  Stage 16: Missing central_services module
    File: claude_code_stage_16.py:101
    Code: from src.services.central_services.core import get_current_run_id, get_logger

  Stage 16: Missing central_services module
    File: claude_code_stage_16.py:102
    Code: from src.services.central_services.core.config import get_bigquery_client

  Stage 16: Missing central_services module
    File: claude_code_stage_16.py:103
    Code: from src.services.central_services.core.pipeline_tracker import PipelineTracker

  Stage 16: Missing central_services module
    File: claude_code_stage_16.py:104
    Code: from src.services.central_services.governance.governance import require_diagnost


================================================================================
SQL_INJECTION (12 issues)
================================================================================

CRITICAL Severity (12 issues):
--------------------------------------------------------------------------------
  Stage 2: Unvalidated timestamp interpolation
    File: claude_code_stage_2.py:285
    Code: TIMESTAMP('{cleaned_at}') AS cleaned_at,

  Stage 2: Unvalidated table ID in SELECT
    File: claude_code_stage_2.py:294
    Code: count_query = f"SELECT COUNT(*) as cnt FROM `{STAGE_1_TABLE}`"

  Stage 3: Unvalidated table ID in SELECT
    File: claude_code_stage_3.py:259
    Code: count_query = f"SELECT COUNT(*) as cnt FROM `{STAGE_2_TABLE}` WHERE NOT is_dupli

  Stage 4: Unvalidated timestamp interpolation
    File: claude_code_stage_4.py:244
    Code: TIMESTAMP('{created_at}') AS created_at,

  Stage 4: Unvalidated table ID in SELECT
    File: claude_code_stage_4.py:260
    Code: count_query = f"SELECT COUNT(*) as cnt FROM `{STAGE_3_TABLE}`"

  Stage 4: Unvalidated table ID in SELECT
    File: claude_code_stage_4.py:270
    Code: count_query = f"SELECT COUNT(*) as cnt FROM `{STAGE_4_TABLE}`"

  Stage 5: Unvalidated table ID in SELECT
    File: claude_code_stage_5.py:288
    Code: count_query = f"SELECT COUNT(*) as cnt FROM `{STAGE_4_TABLE}` WHERE text IS NOT 

  Stage 6: Unvalidated table ID in SELECT
    File: claude_code_stage_6.py:198
    Code: query = f"SELECT entity_id, text, session_id, content_date FROM `{STAGE_4_TABLE}

  Stage 14: Unvalidated timestamp interpolation
    File: claude_code_stage_14.py:225
    Code: TIMESTAMP('{aggregated_at}') as aggregated_at,

  Stage 14: Unvalidated table ID in SELECT
    File: claude_code_stage_14.py:244
    Code: count_query = f"SELECT COUNT(*) as cnt FROM `{STAGE_7_TABLE}`"

  Stage 14: Unvalidated table ID in SELECT
    File: claude_code_stage_14.py:272
    Code: count_query = f"SELECT COUNT(*) as cnt FROM `{STAGE_14_TABLE}` WHERE run_id = '{

  Stage 16: Unvalidated value in WHERE clause
    File: claude_code_stage_16.py:197
    Code: WHERE {status_filter}
