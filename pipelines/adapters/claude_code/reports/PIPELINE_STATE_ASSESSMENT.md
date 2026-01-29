# Claude Code Pipeline State Assessment

**Generated**: 2026-01-27  
**Assessment Script**: `assess_pipeline_state.py`

## Executive Summary

The claude_code pipeline has been partially executed. Data exists in early stages (1-4) and in the final production table (entity_unified), but intermediate stages (5-15) have not been run.

## Current State

### Tables with Data

| Stage | Name | Status | Row Count | Table |
|-------|------|--------|-----------|-------|
| 1 | Extraction | ✅ HAS DATA | 286,706 | `claude_code_stage_1` |
| 2 | Cleaning | ✅ HAS DATA | 286,706 | `claude_code_stage_2` |
| 3 | Identity Generation | ✅ HAS DATA | 226,972 | `claude_code_stage_3` |
| 4 | Staging | ✅ HAS DATA | 8 | `claude_code_stage_4` |
| 16 | Promotion | ✅ HAS DATA | 11,875,341 | `entity_unified` |

### Missing Tables (Not Created)

- Stage 0: Discovery & Assessment
- Stage 5: Tokenization (L1)
- Stage 6: Sentence Detection (L3)
- Stage 7: Message Entities (L5)
- Stage 8: Conversation Entities (L8)
- Stage 9: Embeddings
- Stage 10: LLM Extractions
- Stage 11: Sentiment Analysis
- Stage 12: Topic Extraction
- Stage 13: Relationships
- Stage 14: Aggregation
- Stage 15: Validation

## Analysis

### Pipeline Progression

**Current Status**: ⚠️ **PARTIAL EXECUTION** - Critical data loss detected

- **Early Stages (1-4)**: ⚠️ Partial with data loss
  - Stage 1: 286,706 rows extracted ✅
  - Stage 2: 286,706 rows cleaned ✅
  - Stage 3: 226,972 rows with identities (59,734 rows filtered by THE GATE) ✅
  - Stage 4: **ONLY 8 ROWS** staged ❌ **99.996% DATA LOSS**

- **Entity Creation Stages (5-8)**: ❌ Not run
  - No SPINE entity hierarchy created
  - No tokens (L1), sentences (L3), messages (L5), or conversations (L8)
  - **Action Required**: Run stages 5-8 to create entity hierarchy

- **Enrichment Stages (9-13)**: ❌ Not run
  - No embeddings, extractions, sentiment, topics, or relationships
  - **Action Required**: Run stages 9-13 after entity creation

- **Finalization Stages (14-16)**: ⚠️ Incomplete
  - Stage 14-15: Not run
  - Stage 16: Has 11.8M rows but **intermediate stages missing**
  - **Likely Cause**: Data from different pipeline source, not claude_code

### Critical Data Fidelity Issues

1. **🔴 CRITICAL: Stage 4 Data Loss - ROOT CAUSE IDENTIFIED**
   - **Input**: 226,972 rows from Stage 3 (2 run_ids: run_60885139, run_e9b8a6d2)
   - **Output**: Only 8 rows in Stage 4 (1 run_id: run_9ee6effe)
   - **Loss**: 226,964 rows (99.996% data loss)
   - **Root Cause**: **CONFIRMED**
     - Stage 4 uses `CREATE OR REPLACE TABLE` which replaces the entire table
     - Stage 4 was run with a different run_id (`run_9ee6effe`) that only had 8 rows
     - This run replaced all previous data in the table
     - Stage 4 does NOT filter by run_id when reading from Stage 3 - it processes ALL data
     - But the table replacement mechanism means only the last run's data remains
   - **Risk**: **CRITICAL** - Design flaw allows data loss on re-runs
   - **Action Required**: **IMMEDIATE FIX**
     - **Option 1**: Add run_id filtering to Stage 4 query (recommended)
     - **Option 2**: Change from CREATE OR REPLACE to INSERT with run_id deduplication
     - **Option 3**: Re-run Stage 4 to process all current Stage 3 data (226,972 rows)

2. **Missing Entity Hierarchy**: Stages 5-8 not executed
   - **Impact**: No SPINE entities created (L1→L3→L5→L8)
   - **Blocking**: Cannot proceed with enrichment without entities
   - **Action Required**: Run stages 5-8 after fixing stage 4

3. **Entity Unified Data Source Mismatch**: 11.8M rows in entity_unified but no source stages
   - **Observation**: entity_unified has 11.8M rows but stages 5-15 are missing
   - **Possible Causes**:
     - Data from different pipeline (not claude_code)
     - Manual data insertion
     - Different source_pipeline value
     - Legacy data from previous pipeline version
   - **Action Required**: Verify data source
     - Query entity_unified for source_pipeline = 'claude_code'
     - Check if data matches current pipeline structure
     - Determine if cleanup/rollback needed

## Recommendations

### 🔴 IMMEDIATE PRIORITY ACTIONS

1. **URGENT: Fix Stage 4 Data Loss (Root Cause Identified)**
   - **Root Cause**: `CREATE OR REPLACE TABLE` replaced all data when run with different run_id
   - **Current State**: Stage 3 has 226,972 rows, Stage 4 has only 8 rows
   - **Fix Options**:
     - **Option A (Recommended)**: Modify Stage 4 to filter by run_id when reading from Stage 3
       - Add `WHERE run_id = @run_id` to the SELECT query
       - Use INSERT instead of CREATE OR REPLACE
       - Prevents data loss on re-runs
     - **Option B**: Re-run Stage 4 to process all current Stage 3 data
       - Will restore 226,972 rows to Stage 4
       - But doesn't fix the underlying design issue
   - **Action**: Choose fix option and implement immediately

2. **Verify Entity Unified Data Source**
   - **Query**: Check source_pipeline field in entity_unified
   ```sql
   SELECT source_pipeline, COUNT(*) as count
   FROM `flash-clover-464719-g1.spine.entity_unified`
   GROUP BY source_pipeline
   ```
   - **Action**: If not from claude_code, determine if cleanup needed

### Next Steps (After Stage 4 Fix)

3. **Run Missing Stages Sequentially**
   - **Stage 4**: Re-run after fixing data loss issue
   - **Stages 5-8**: Create SPINE entity hierarchy (L1→L3→L5→L8)
   - **Stages 9-13**: Run enrichment (embeddings, extractions, sentiment, topics, relationships)
   - **Stages 14-16**: Run finalization (aggregation, validation, promotion)

4. **Validate End-to-End Data Flow**
   - Verify row counts at each stage
   - Check for additional data loss
   - Ensure entity relationships are correct
   - Validate final promotion to entity_unified

### Next Steps

1. Run `assess_pipeline_state.py` to get current state
2. Investigate stage 4 data loss
3. Run stages 5-8 to create entity hierarchy
4. Run enrichment stages 9-13
5. Run finalization stages 14-16
6. Verify end-to-end data flow

## Usage

To re-run this assessment:

```bash
python pipelines/adapters/claude_code/scripts/assess_pipeline_state.py
```

For JSON output:

```bash
python pipelines/adapters/claude_code/scripts/assess_pipeline_state.py --json
```
