# BigQuery Partitioning and Clustering Audit

**Created:** 2025-12-20
**Remediation Completed:** 2025-12-21
**Purpose:** Audit all BigQuery tables for effective partitioning and clustering
**Status:** COMPLETED - All P1 tables remediated

---

## Definition of Done

This workstream is complete when:

- [x] All P1 (CRITICAL) tables have been migrated to `content_date` partitioning
- [x] Row counts validated before and after migration (exact match required)
- [x] Partition distribution verified (data spread across multiple partitions)
- [x] L1 tokens isolated to separate cost-protected tables where applicable
- [x] Timestamp propagation implemented for all derived entity levels
- [x] Backup tables created for rollback capability
- [x] Universal Pipeline Pattern updated with learnings (partitioning, timestamp propagation, token isolation)
- [x] Audit document updated with remediation results
- [ ] Backup tables deleted after 7 days of stable operation (2025-12-28)

---

## Executive Summary

**Original Finding (2025-12-20):** Many tables were partitioned by `ingestion_date` or `extracted_at`, which is ineffective for batch-loaded historical data. When historical data spanning months or years is loaded in a single batch, all rows receive the same partition date, defeating partition pruning.

**Remediation Completed (2025-12-21):** All P1 tables have been migrated to `content_date` partitioning with timestamp propagation. L1 tokens isolated to separate cost-protected tables.

**Results:**
| Table | Before | After |
|-------|--------|-------|
| `entity_unified` | 1 partition, 11.8M rows | 130 partitions |
| `entity_tokens` | 1 partition, 39.8M rows | 128 partitions |
| `chatgpt_web_ingestion_final` | 0 partitions, 51.7M rows, 30GB | Split: 11.9M (L2-L8) + 39.8M (L1), both partitioned |

**Cost Impact:**
- Before: Every query scanned entire tables
- After: Queries with date filters scan only relevant partitions (80-95% cost reduction expected)

**Original Impact:**
- Full table scans required for most queries
- Increased costs (scan all data instead of relevant partitions)
- Slower query performance
- Some tables require partition filters but have unusable partitions

---

## Part 1: Partitioning and Clustering Principles

### 1.1 What Partitioning Does

Partitioning divides a table into segments based on a column value. When you query with a filter on the partition column, BigQuery only scans the relevant partitions (partition pruning).

**Cost Impact:** You pay for bytes scanned. Effective partitioning reduces bytes scanned.

### 1.2 The Ingestion Date Anti-Pattern

**The Problem:**
```
Historical data (spanning July 2024 - December 2025)
     ↓
Batch loaded on 2025-12-03
     ↓
All rows get ingestion_date = 2025-12-03
     ↓
One massive partition, no pruning possible
```

**Real Example from This Project:**
- `entity_unified`: 11.8M rows in ONE partition (2025-12-03)
- `entity_tokens`: 39.8M rows in ONE partition (2025-12-03)

**Typical Query Pattern:**
```sql
-- User wants data from October 2025
SELECT * FROM entity_unified
WHERE created_at BETWEEN '2025-10-01' AND '2025-10-31'
-- Result: Scans ALL 11.8M rows because partition is ingestion_date, not created_at
```

### 1.3 Effective Partitioning Strategies

| Scenario | Partition Column | Rationale |
|----------|-----------------|-----------|
| Historical data (conversations, messages) | `created_date` (the date the content was created) | Queries typically filter by when content was created |
| Event logs, audit trails | `event_date` or `timestamp` | Queries filter by when events occurred |
| Enrichment results | `source_created_date` (date of source entity) | Join with source entities by their creation date |
| Continuous ingestion | `ingestion_date` works | Each day's data is naturally in its own partition |

### 1.4 When Ingestion Date Works

Ingestion date partitioning IS appropriate when:
1. **Streaming/continuous ingestion**: Data arrives daily, queries want "last 7 days"
2. **Data freshness queries**: "What was ingested today?"
3. **Processing state tracking**: "What hasn't been processed yet?"

### 1.5 Clustering Best Practices

Clustering orders data within partitions by specified columns (up to 4).

**Order clusters by:**
1. **Most frequently filtered column first** (highest cardinality that appears in WHERE)
2. **Join keys second** (entity_id, conversation_id)
3. **Secondary filters third** (level, status, type)

**Example:**
```sql
CLUSTER BY level, conversation_id, entity_id
```
- `level` first: Common filter (L4, L5, L6, L7, L8)
- `conversation_id`: Common join key
- `entity_id`: Point lookups

---

## Part 2: Audit Methodology

### 2.1 Classification Criteria

| Classification | Description | Action Required |
|---------------|-------------|-----------------|
| 🔴 **CRITICAL** | Partition column defeats pruning (ingestion_date for batch data) | Recreate table with correct partition |
| 🟡 **SUBOPTIMAL** | Partition works but clustering could be improved | Update clustering |
| 🟢 **EFFECTIVE** | Partition and clustering align with query patterns | None |
| ⚪ **NO PARTITION** | Table should have partitioning but doesn't | Add partitioning |

### 2.2 Evaluation Questions

For each table, ask:
1. What column do users ACTUALLY filter on in queries?
2. Does the partition column match that filter column?
3. For historical data: Is partition by content creation date or ingestion date?
4. Are clustering columns ordered by filter frequency?

---

## Part 3: Audit Results by Dataset

### 3.1 Dataset: `spine` (Core Entity Data)

#### 🔴 CRITICAL ISSUES

| Table | Current Partition | Problem | Recommended Partition |
|-------|-------------------|---------|----------------------|
| `entity_unified` | `ingestion_date` | 11.8M rows in 1 partition; queries filter by created_at | `created_date` (extract from created_at) |
| `entity_tokens` | `ingestion_date` | 39.8M rows in 1 partition | `created_date` (from parent entity) |
| `chatgpt_relationships` | `ingestion_date` | Batch loaded, queries by relationship dates | `created_date` |

**entity_unified Details:**
- Current: All data in partition `2025-12-03`
- Actual data spans: Multiple months of conversations
- Query pattern: `WHERE created_at BETWEEN...` or `WHERE DATE(created_at) = ...`
- **Cost impact**: Every query scans 11.8M rows regardless of date filter

#### 🟡 SUBOPTIMAL

| Table | Current Partition | Issue | Recommendation |
|-------|-------------------|-------|----------------|
| `entity_embeddings` | `enrichment_date` | Queries often join to entities by entity creation date | Consider `source_created_date` or add clustering by `entity_id` first |
| `entity_enrichments` | `created_at` | OK for enrichment queries, but joins to entities scan all | Add clustering optimization |

#### 🟢 EFFECTIVE (Well-Designed)

| Table | Partition | Clustering | Notes |
|-------|-----------|------------|-------|
| `chatgpt_web_ingestion_stage_2` | `created_date` | `level, source_conversation_id` | Correct: partitions by content creation |
| `chatgpt_web_ingestion_stage_3` | `created_date` | `source_conversation_id, level` | Correct |
| `chatgpt_web_ingestion_stage_8` | `created_date` | `source_conversation_id, level` | Correct |
| `text_messages_stage_1` | `created_date` | `level, source_conversation_id` | Correct |
| `text_messages_stage_3` | `created_date` | `level, source_conversation_id, entity_id` | Correct |

#### ⚪ NO PARTITION (Should Have)

| Table | Clustering Only | Recommendation |
|-------|-----------------|----------------|
| `chatgpt_web_ingestion_final` | `level, topic_segment_id, conversation_id, entity_id` | Add partition by `created_date` |
| `chatgpt_web_ingestion_stage_1` | `level, source_conversation_id` | Add partition by `created_date` |
| `chatgpt_web_ingestion_stage_6` | `level, entity_id` | Add partition by `created_date` |
| `chatgpt_web_ingestion_stage_7` | `level, entity_id` | Add partition by `created_date` |
| `chatgpt_web_ingestion_stage_11_l7_boundaries` | `conversation_id, segment_sequence` | Add partition by `created_date` |
| `chatgpt_web_ingestion_stage_12` | `level, topic_segment_id` | Add partition by `created_date` |
| `chatgpt_web_ingestion_stage_13` | `level, topic_segment_id` | Add partition by `created_date` |
| `chatgpt_web_ingestion_stage_14` | `level, topic_segment_id, conversation_id, entity_id` | Add partition by `created_date` |
| `text_messages_stage_7` | `level, parent_id, sequence` | Add partition by `created_date` |
| `system_limits` | `limit_type, component, status` | Add partition by `created_date` |

---

### 3.2 Dataset: `governance` (Audit & Compliance)

#### 🟢 MOSTLY EFFECTIVE

Most governance tables partition by event timestamps, which is correct for audit/compliance queries.

| Table | Partition | Status |
|-------|-----------|--------|
| `audit_log` | `start_time` | ✅ Correct |
| `cost_tracking` | `timestamp` | ✅ Correct |
| `enforcement_log` | `timestamp` | ✅ Correct |
| `model_usage_requests` | `timestamp` | ✅ Correct |
| `model_usage_responses` | `timestamp` | ✅ Correct |
| `budget_tracking` | `timestamp` | ✅ Correct |
| `policies` | `created_at` | ✅ Correct |

#### ⚪ NO PARTITION

| Table | Recommendation |
|-------|----------------|
| `access_control` | Add partition by `created_at` if table grows |
| `correction_rules` | Add partition by `created_at` if table grows |
| `analysis_cache` | Add partition by `cached_at` or TTL-based |

---

### 3.3 Dataset: `identity` (People & Resolution)

#### 🟢 EFFECTIVE

| Table | Partition | Status |
|-------|-----------|--------|
| `contacts_master` | `extraction_timestamp` | ✅ Correct for extraction-based queries |
| `identity_resolutions` | `resolved_at` | ✅ Correct |
| `manual_resolutions` | `created_at` | ✅ Correct |
| `agent_sessions` | `created_at` | ✅ Correct |

#### 🟡 SUBOPTIMAL

| Table | Current Partition | Issue |
|-------|-------------------|-------|
| `raw_apple_contacts_*` | `extraction_timestamp` | OK but queries might filter by contact dates |

---

### 3.4 Dataset: `enrichment`

#### 🟢 EFFECTIVE

| Table | Partition | Status |
|-------|-----------|--------|
| `enrichment_run` | `started_at` | ✅ Correct |
| `tier1` | `enriched_at` | ✅ Correct |
| `flash_triage` | `enriched_at` | ✅ Correct |
| `pro_analysis` | `enriched_at` | ✅ Correct |

#### 🟡 COULD IMPROVE

| Table | Current Partition | Suggestion |
|-------|-------------------|------------|
| `claude_embeddings` | `session_date` | Consider adding `entity_created_date` for cross-date joins |

---

### 3.5 Dataset: `ai_coordination`

#### 🟢 ALL EFFECTIVE

All tables partition by `created_at` or relevant event timestamps.

---

### 3.6 Dataset: `knowledge`

#### 🟢 MOSTLY EFFECTIVE

| Table | Partition | Status |
|-------|-----------|--------|
| `narratives` | `generated_at` | ✅ Correct |
| `architecture_decisions` | `timestamp` | ✅ Correct |
| `validation_log` | `timestamp` | ✅ Correct |

---

## Part 4: Remediation Plan (COMPLETED 2025-12-21)

### 4.1 Priority 1: Fix Critical Tables ✅ DONE

**Migration Script:** [`architect_central_services/sql/migrations/partition_fix_entity_unified_tokens.sql`](../../architect_central_services/sql/migrations/partition_fix_entity_unified_tokens.sql)

**Status:** All P1 tables have been remediated. See Part 7 for details.

These tables had the most data and worst partitioning:

#### Table: `spine.entity_unified` (11.8M rows)

**Current State:**
- Partition: `ingestion_date` (all data in 2025-12-03)
- Clustering: `conversation_id, entity_type, level`

**Target State:**
- Partition: `content_date` (derived from `source_message_timestamp`, falls back to `created_at`)
- Clustering: `level, conversation_id, entity_id`

**Key Insight:** The `source_message_timestamp` field contains the actual date when content was created on the source platform (ChatGPT). This spans 126 distinct dates from Aug 2024 - Nov 2025. Using this for partitioning enables effective partition pruning when querying by content creation date.

**See full migration script:** `architect_central_services/sql/migrations/partition_fix_entity_unified_tokens.sql`

#### Table: `spine.entity_tokens` (39.8M rows)

**Current State:**
- Partition: `ingestion_date` (all data in 2025-12-03)
- Clustering: `conversation_id, word_id`

**Target State:**
- Partition: `content_date` (derived from `source_message_timestamp`)
- Clustering: `conversation_id, word_id`

### 4.2 Priority 2: Add Partitions to Unpartitioned Tables

For each unpartitioned table in the `chatgpt_web_ingestion_stage_*` series:
1. Determine if table is staging (temporary) or long-term
2. For long-term tables, add `created_date` partition
3. Keep clustering as-is (already well-designed)

### 4.3 Priority 3: Clustering Optimization

Review clustering column order based on actual query patterns:
1. Analyze query logs for most common WHERE clauses
2. Reorder clustering columns to match filter frequency
3. Consider adding `entity_id` to more tables for point lookups

---

## Part 5: Ongoing Audit Checklist

Use this checklist for every new table:

### Before Creating Table

- [ ] What column will queries most commonly filter on?
- [ ] Is this batch-loaded historical data or streaming?
- [ ] If historical: partition by content creation date, NOT ingestion date
- [ ] Clustering columns ordered by: filter frequency → join keys → secondary filters

### After Creating Table

- [ ] Verify partition column appears in typical WHERE clauses
- [ ] Monitor query costs to validate partition pruning is working
- [ ] Check `INFORMATION_SCHEMA.PARTITIONS` for balanced partition sizes

### Query for Partition Effectiveness

```sql
-- Check if partitions are balanced or if one partition has all data
SELECT
  partition_id,
  total_rows,
  total_logical_bytes / 1024 / 1024 AS mb
FROM `project.dataset.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'your_table'
ORDER BY partition_id;
```

---

## Part 6: Summary Tables

### Tables Requiring Immediate Action (Status Updated 2025-12-21)

| Priority | Table | Rows | Issue | Status |
|----------|-------|------|-------|--------|
| P1 | `spine.entity_unified` | 11.8M | Single partition | ✅ Fixed - 130 partitions |
| P1 | `spine.entity_tokens` | 39.8M | Single partition | ✅ Fixed - 128 partitions |
| P1 | `spine.chatgpt_web_ingestion_final` | 51.7M | No partition, L1 mixed | ✅ Fixed - Split + partitioned |
| P2 | `spine.chatgpt_web_ingestion_stage_1` | 62K | No partition | Lower priority - has clustering |
| P2 | `spine.chatgpt_web_ingestion_stage_6` | - | No partition | Lower priority - has clustering |
| P2 | `spine.chatgpt_web_ingestion_stage_7` | - | No partition | Lower priority - has clustering |

### Tables with Effective Partitioning

| Dataset | Count | Notes |
|---------|-------|-------|
| `spine` (stage tables with created_date) | 5 | ✅ Well designed |
| `governance` | ~20 | ✅ Timestamp-based, appropriate |
| `identity` | ~15 | ✅ Mostly effective |
| `enrichment` | ~10 | ✅ Enrichment-date based |
| `ai_coordination` | ~8 | ✅ All effective |
| `knowledge` | ~10 | ✅ All effective |

---

## Appendix A: Raw Partition Data

### Spine Dataset - All Partitioned Tables

| Table | Partition Column | Clustering |
|-------|------------------|------------|
| chatgpt_relationships | ingestion_date 🔴 | source_entity_id, target_entity_id, relationship_type, status |
| chatgpt_web_ingestion_stage_2 | created_date ✅ | level, source_conversation_id |
| chatgpt_web_ingestion_stage_3 | created_date ✅ | source_conversation_id, level |
| chatgpt_web_ingestion_stage_8 | created_date ✅ | source_conversation_id, level |
| entity_embeddings | enrichment_date | entity_id |
| entity_enrichments | created_at | entity_id, level, source_platform |
| entity_perspectives | created_date ✅ | entity_id, perspective_type, source |
| entity_tokens | ingestion_date 🔴 | conversation_id, word_id |
| entity_unified | ingestion_date 🔴 | conversation_id, entity_type, level |
| gemini_validation_runs | run_date | entity_id, iteration_number, run_type |
| monitored_things_stage1 | extracted_at | (none) |
| rag_documents | ingested_at | source_directory |
| system_existence | exists_at | monitor_type, entity_type |
| system_observations | created_date ✅ | observation_type, observed_component, severity |
| text_messages_stage_1 | created_date ✅ | level, source_conversation_id |
| text_messages_stage_3 | created_date ✅ | level, source_conversation_id, entity_id |
| text_messages_stage_5 | created_at | level, parent_id |
| text_messages_stage_6 | created_at | level, parent_id |
| text_messages_stage_7_tokens | partition_key | parent_id, sequence |
| zoom_chat_messages | extracted_at | sender, recipient_type |
| zoom_existence_extraction | extracted_at | extraction_type |
| zoom_meaningful_events | event_at ✅ | event_type, subject_type |
| zoom_my_state | started_at ✅ | state_type |
| zoom_participants | last_seen_at | participant_name |

---

## Appendix B: Migration Scripts Template

### Generic Table Migration

```sql
-- Template for migrating from ingestion_date to created_date partition

-- Step 1: Create new table
CREATE TABLE `project.dataset.table_v2`
PARTITION BY created_date
CLUSTER BY <clustering_columns>
OPTIONS(
  description = 'Migrated from table_v1 with correct partitioning',
  labels = [('migrated_from', 'table_v1'), ('migration_date', '2025-12-20')]
)
AS
SELECT
  * EXCEPT(ingestion_date),
  DATE(created_at) as created_date  -- Or appropriate date extraction
FROM `project.dataset.table_v1`;

-- Step 2: Validate
SELECT
  (SELECT COUNT(*) FROM `project.dataset.table_v1`) as old_count,
  (SELECT COUNT(*) FROM `project.dataset.table_v2`) as new_count;

-- Step 3: Check partition distribution
SELECT
  partition_id,
  total_rows
FROM `project.dataset.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'table_v2'
ORDER BY partition_id;

-- Step 4: Rename (when ready)
-- ALTER TABLE `project.dataset.table_v1` RENAME TO `table_v1_backup`;
-- ALTER TABLE `project.dataset.table_v2` RENAME TO `table_v1`;
```

---

---

## Part 7: Remediation Completed (2025-12-21)

### P1 Tables Fixed

| Table | Before | After | Status |
|-------|--------|-------|--------|
| `entity_unified` | 1 partition (ingestion_date) | 130 partitions (content_date) | ✅ Complete |
| `entity_tokens` | 1 partition (ingestion_date) | 128 partitions (content_date) | ✅ Complete |
| `chatgpt_relationships` | ingestion_date partition | Empty table, no action needed | ✅ N/A |
| `chatgpt_web_ingestion_final` | 0 partitions, 30GB with L1 | Split into 2 tables, partitioned | ✅ Complete |

### chatgpt_web_ingestion_final Split

| New Table | Levels | Rows | Partitions | Size |
|-----------|--------|------|------------|------|
| `chatgpt_web_ingestion_final` | L2-L8 | 11.87M | 128 | ~9.5 GB |
| `chatgpt_web_ingestion_final_tokens` | L1 | 39.87M | 126 | ~22 GB |

### Key Improvements

1. **Timestamp Propagation**: Source timestamps now propagated from L5 to all child levels
2. **content_date Partitioning**: All fixed tables use content creation date, not ingestion date
3. **L1 Token Isolation**: Tokens isolated to cost-protected separate table
4. **Universal Pipeline Pattern Updated**: Added sections on partitioning, timestamp propagation, and token isolation

### Backup Tables (Safe to Delete After 7 Days)

- `entity_unified_backup_20251221`
- `entity_tokens_backup_20251221`
- `chatgpt_web_ingestion_final_backup_20251221`

---

**Document Maintainer:** Claude Code
**Last Audit:** 2025-12-21
**Remediation Completed:** 2025-12-21
**Next Review:** After any table schema changes
