# BigQuery Sync Inventory

**Last Updated**: 2025-01-XX

This document lists all scripts and services that actively sync data to BigQuery.

## 🎯 Active Sync Scripts

### 1. `scripts/register_stage_3_entity_ids.py`
- **Purpose**: Registers entity_ids from text messages Stage 3
- **Sync Method**: Calls `identity_service.sync_to_bigquery()`
- **Target Table**: `identity.id_registry`
- **Pattern**: HOLD₁ (local JSONL) → AGENT (sync) → HOLD₂ (BigQuery)
- **When**: Manual execution or scheduled
- **Status**: ✅ Active (newly implemented)

### 2. `scripts/zoom_capture_robust.py`
- **Purpose**: Syncs captured Zoom sessions to BigQuery
- **Sync Method**: Subprocess call to `architect_central_services/pipelines/zoom/scripts/stage_0/upload_raw_sessions.py`
- **Target Tables**: Zoom pipeline tables
- **When**: After each Zoom capture event
- **Status**: ✅ Active

## 🔧 Active Sync Services

### 1. `src/services/central_services/identity_service/service.py`
- **Function**: `sync_to_bigquery(dry_run=False, batch_size=1000)`
- **Purpose**: Syncs ID registry from local JSONL to BigQuery
- **Target Table**: `identity.id_registry`
- **Pattern**: HOLD₁ (JSONL) → AGENT (sync) → HOLD₂ (BigQuery)
- **Called By**: `scripts/register_stage_3_entity_ids.py`
- **Status**: ✅ Active (newly implemented)

### 2. `src/services/central_services/contacts/service.py`
- **Function**: `sync_to_bigquery(dry_run=False)`
- **Purpose**: Syncs dirty contacts from local DuckDB to BigQuery
- **Target Table**: `identity.contacts_master`
- **Pattern**: Local DuckDB → BigQuery (MERGE)
- **Called By**: Can be called directly or via service API
- **Status**: ✅ Active

### 3. `src/services/central_services/bigquery_archive_service/service.py`
- **Function**: `archive_file(file_info)`
- **Purpose**: Archives large processed files to BigQuery
- **Target Tables**: Various tables in `archive` dataset
- **Pattern**: Local JSONL/JSON → GCS → BigQuery
- **When**: Periodic archiving of processed files
- **Status**: ✅ Active

## 📊 Direct BigQuery Writers (Not Sync Pattern)

These scripts write directly to BigQuery but don't follow the sync pattern:

### Text Messages Pipeline
- **Stage 3**: `pipelines/text_messages/scripts/stage_3/text_messages_stage_3.py`
  - Writes to: `spine.text_messages_stage_3`
  - Method: Direct BigQuery load (MERGE)

- **Stage 14**: `pipelines/text_messages/scripts/stage_14/text_messages_stage_14.py`
  - Writes to: `spine.entity_unified`
  - Method: Direct BigQuery MERGE

### Zoom Pipeline
- **Stage 0**: `architect_central_services/pipelines/zoom/scripts/stage_0/upload_raw_sessions.py`
  - Writes to: Zoom pipeline tables
  - Method: Direct BigQuery load
  - Called by: `scripts/zoom_capture_robust.py`

## 📝 Related (Not Direct BigQuery Sync)

### `scripts/utilities/THE_CLOUD_SYNC.py`
- **Purpose**: Syncs knowledge atoms to GCS bucket
- **Target**: `gs://truth-engine-atoms/`
- **Note**: This is GCS sync, not BigQuery, but feeds into cloud storage
- **Status**: ✅ Active

## 📋 Summary

**Total Active Sync Scripts**: 2
1. `register_stage_3_entity_ids.py` - ID registry
2. `zoom_capture_robust.py` - Zoom sessions

**Total Active Sync Services**: 3
1. `identity_service.sync_to_bigquery()` - ID registry
2. `contacts_service.sync_to_bigquery()` - Contacts
3. `bigquery_archive_service.archive_file()` - File archiving

**Direct Writers (Not Sync)**: Multiple pipeline stages

## 🔍 How to Find More

To find scripts that call BigQuery:

```bash
# Find scripts with sync functions
grep -r "sync_to_bigquery\|sync_from_bigquery" scripts/

# Find scripts using BigQuery client
grep -r "bigquery\.Client\|get_bigquery_client" scripts/

# Find services with sync methods
grep -r "def.*sync.*bigquery" src/services/central_services/
```
