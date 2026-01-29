# Comprehensive Pipeline Fix Plan

**Date**: 2026-01-27  
**Total Issues Identified**: 139  
**Status**: In Progress

## Executive Summary

A comprehensive audit has identified **139 critical issues** across all 17 pipeline stages:

- **99 IMPORT_ERROR issues** - All stages have broken imports
- **12 SQL_INJECTION issues** - Unvalidated table IDs and timestamp interpolations
- **12 DUPLICATE_PREVENTION issues** - Stages don't prevent duplicates
- **16 ERROR_HANDLING issues** - Technical error messages

## Issue Categories

### 1. Import Errors (99 issues) - CRITICAL BLOCKER

**Problem**: All stages try to import from `src.services.central_services` which doesn't exist in the codebase.

**Root Cause**: The codebase structure changed but stage scripts weren't updated.

**Fix Strategy**:
- Replace all `from src.services.central_services.core import ...` with `from shared.logging_bridge import ...`
- Replace `from truth_forge.core import get_logger` with `from shared.logging_bridge import get_logger`
- Create fallback implementations for missing functions:
  - `get_bigquery_client()` → `bigquery.Client()`
  - `PipelineTracker` → Simple context manager
  - `require_diagnostic_on_error()` → No-op function

**Affected Stages**: All 17 stages

### 2. SQL Injection Vulnerabilities (12 issues) - CRITICAL SECURITY

**Problem**: Unvalidated table IDs and timestamp values in SQL queries.

**Examples**:
- `f"SELECT COUNT(*) FROM `{STAGE_1_TABLE}`"` - Table ID not validated
- `TIMESTAMP('{cleaned_at}')` - Timestamp not validated

**Fix Strategy**:
- Add `from shared_validation import validate_table_id` to all stages
- Validate all table IDs before use: `validated_table = validate_table_id(table_id)`
- Use parameterized queries or validate timestamp strings
- Ensure all f-string SQL uses validated values

**Affected Stages**: 2, 3, 4, 5, 6, 14, 16

### 3. Duplicate Prevention (12 issues) - CRITICAL DATA INTEGRITY

**Problem**: 
- Stage 4 uses `CREATE OR REPLACE TABLE` which causes data loss on re-runs
- Stages 5-16 use `insert_rows_json` without duplicate prevention

**Fix Strategy**:

**Stage 4**:
- Replace `CREATE OR REPLACE TABLE` with `DELETE ... WHERE run_id = ?` followed by `INSERT`
- Or use `MERGE` with run_id filtering

**Stages 5-16**:
- Replace `insert_rows_json` with `merge_rows_to_table` from `shared.utilities`
- Use appropriate `match_key` for each stage:
  - Stage 3: `entity_id`
  - Stage 5: `token_id`
  - Stage 6: `sentence_id`
  - Stage 7: `entity_id` (message)
  - Stage 8: `conversation_id`
  - Stage 9-16: `entity_id`

**Affected Stages**: 4 (CRITICAL), 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16

### 4. Error Handling (16 issues) - MEDIUM PRIORITY

**Problem**: Error messages are too technical for non-coders.

**Fix Strategy**:
- Wrap all exceptions in main() with user-friendly messages
- Add "What this means" and "What to do" explanations
- Remove technical stack traces from user-facing output

**Affected Stages**: All 17 stages

## Implementation Plan

### Phase 1: Foundation (COMPLETE)
- ✅ Created `merge_rows_to_table()` utility function
- ✅ Added to `shared/__init__.py` exports
- ✅ Created comprehensive audit tool
- ✅ Created fix automation script

### Phase 2: Import Fixes (IN PROGRESS)
- Fix all import statements across all stages
- Test that stages can be imported without errors
- Verify logging works correctly

### Phase 3: Security Fixes
- Add `validate_table_id()` to all SQL queries
- Fix timestamp interpolations
- Verify no SQL injection vulnerabilities remain

### Phase 4: Duplicate Prevention
- Fix Stage 4 (CREATE OR REPLACE → MERGE/DELETE+INSERT)
- Replace `insert_rows_json` with `merge_rows_to_table` in all stages
- Test idempotency (re-running stages doesn't create duplicates)

### Phase 5: Error Handling
- Add user-friendly error messages
- Test error scenarios
- Verify non-coder accessibility

### Phase 6: Verification
- Re-run comprehensive audit
- Verify all issues resolved
- Test end-to-end pipeline execution

## Detailed Fixes by Stage

### Stage 1: Extraction
**Issues**: 7 import errors, 1 duplicate prevention, 1 error handling

**Fixes**:
1. Replace imports with `shared.logging_bridge`
2. Add fingerprint-based duplicate checking before insert
3. Add user-friendly error messages

### Stage 2: Cleaning
**Issues**: 7 import errors, 2 SQL injection, 1 error handling

**Fixes**:
1. Replace imports with `shared.logging_bridge`
2. Validate `STAGE_1_TABLE` and `STAGE_2_TABLE` before use
3. Validate `cleaned_at` timestamp
4. Add user-friendly error messages

### Stage 3: Identity Generation
**Issues**: 8 import errors, 1 SQL injection, 1 duplicate prevention, 1 error handling

**Fixes**:
1. Replace imports with `shared.logging_bridge`
2. Validate `STAGE_2_TABLE` before use
3. Replace `insert_rows_json` with `merge_rows_to_table` (match_key: `entity_id`)
4. Add user-friendly error messages

### Stage 4: Staging
**Issues**: 7 import errors, 2 SQL injection, 1 CRITICAL duplicate prevention, 1 error handling

**Fixes**:
1. Replace imports with `shared.logging_bridge`
2. Validate `STAGE_3_TABLE` and `STAGE_4_TABLE` before use
3. **CRITICAL**: Replace `CREATE OR REPLACE TABLE` with:
   ```sql
   DELETE FROM `{STAGE_4_TABLE}` WHERE run_id = '{run_id}';
   INSERT INTO `{STAGE_4_TABLE}` SELECT ... FROM `{STAGE_3_TABLE}` WHERE run_id = '{run_id}';
   ```
4. Validate `created_at` timestamp
5. Add user-friendly error messages

### Stages 5-16: Entity Creation & Enrichment
**Issues**: Import errors, duplicate prevention, error handling

**Fixes**:
1. Replace imports with `shared.logging_bridge`
2. Replace `insert_rows_json` with `merge_rows_to_table` using appropriate match_key
3. Validate all table IDs before use
4. Add user-friendly error messages

## Testing Strategy

After each phase:
1. Run comprehensive audit to verify fixes
2. Test stage imports (should not fail)
3. Test duplicate prevention (re-run stage, verify no duplicates)
4. Test SQL injection prevention (try malicious table IDs, should fail validation)
5. Test error handling (trigger errors, verify user-friendly messages)

## Success Criteria

- ✅ All stages can be imported without errors
- ✅ All SQL queries use validated table IDs
- ✅ All stages prevent duplicates (idempotent)
- ✅ All error messages are user-friendly
- ✅ Comprehensive audit shows 0 critical issues
- ✅ End-to-end pipeline execution succeeds

## Next Steps

1. Execute Phase 2: Fix all import statements
2. Execute Phase 3: Fix SQL injection vulnerabilities
3. Execute Phase 4: Implement duplicate prevention
4. Execute Phase 5: Improve error handling
5. Execute Phase 6: Verify all fixes
