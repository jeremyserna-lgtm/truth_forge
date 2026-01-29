# entity_unified - Complete Specification

**Date**: 2026-01-27  
**Status**: PRODUCTION TABLE  
**Purpose**: SPINE unified production table with content-date partitioning

---

## TABLE ARCHITECTURE

### Physical Configuration

**Table ID**: `{PROJECT_ID}.{DATASET_ID}.entity_unified`

**Partitioning**:
- **Type**: DAY
- **Field**: `content_date`
- **Purpose**: Enables efficient date-range queries and partition pruning

**Clustering**:
- **Fields**: `['level', 'conversation_id', 'entity_id']`
- **Purpose**: Optimizes queries filtering by entity hierarchy and conversation context

**Description**: "SPINE unified production table with content-date partitioning"

---

## COMPLETE SCHEMA (34 Fields)

### Identity Fields

| Field Name | Type | Mode | Description |
|------------|------|------|-------------|
| `entity_id` | STRING | NULLABLE | Primary entity identifier (generated at Stage 3) |
| `level` | INTEGER | NULLABLE | Entity hierarchy level (L2=word, L3=span, L4=sentence, L5=message, L6=turn, L7=topic, L8=conversation) |
| `entity_type` | STRING | NULLABLE | Type classification (e.g., "message", "sentence", "word") |
| `entity_mode` | STRING | NULLABLE | Entity state (e.g., "active", "archived") |
| `parent_id` | STRING | NULLABLE | Parent entity in hierarchy |

### Hierarchical ID Fields

| Field Name | Type | Mode | Description |
|------------|------|------|-------------|
| `conversation_id` | STRING | NULLABLE | L8 conversation identifier |
| `topic_segment_id` | STRING | NULLABLE | L7 topic segment identifier |
| `turn_id` | STRING | NULLABLE | L6 turn identifier |
| `message_id` | STRING | NULLABLE | L5 message identifier (maps to entity_id when level=5) |
| `sentence_id` | STRING | NULLABLE | L4 sentence identifier (maps to entity_id when level=4) |
| `span_id` | STRING | NULLABLE | L3 span identifier (maps to entity_id when level=3) |
| `word_id` | STRING | NULLABLE | L2 word identifier (maps to entity_id when level=2) |

### Source Fields

| Field Name | Type | Mode | Description |
|------------|------|------|-------------|
| `source_pipeline` | STRING | NULLABLE | Pipeline name (e.g., "claude_code") |
| `source_file` | STRING | NULLABLE | Source file path |
| `source_file_path` | STRING | NULLABLE | Full source file path |
| `source_system` | STRING | NULLABLE | Source system identifier |
| `source_ids` | STRING | REPEATED | Array of source identifiers |

### Content Fields

| Field Name | Type | Mode | Description |
|------------|------|------|-------------|
| `text` | STRING | NULLABLE | Entity text content |
| `canonical_form` | STRING | NULLABLE | Normalized/canonical text form |
| `persona` | STRING | NULLABLE | Persona identifier |

### Metadata Field

| Field Name | Type | Mode | Description |
|------------|------|------|-------------|
| `metadata` | JSON | NULLABLE | **CRITICAL**: Stores all enrichment data (role, message_type, embeddings, emotions, keywords, intent, etc.) |

### Timestamp Fields

| Field Name | Type | Mode | Description |
|------------|------|------|-------------|
| `content_date` | DATE | NULLABLE | Content date (partitioning field) |
| `source_message_timestamp` | TIMESTAMP | NULLABLE | Original message timestamp |
| `created_at` | TIMESTAMP | NULLABLE | Entity creation timestamp |
| `updated_at` | TIMESTAMP | NULLABLE | Entity last update timestamp |
| `ingestion_timestamp` | TIMESTAMP | NULLABLE | Pipeline ingestion timestamp |
| `ingestion_job_id` | STRING | NULLABLE | Pipeline run_id |

### Validation Fields

| Field Name | Type | Mode | Description |
|------------|------|------|-------------|
| `validation_status` | STRING | NULLABLE | Validation status (PASSED, WARNING, FAILED) |

### Count Rollup Fields

| Field Name | Type | Mode | Description |
|------------|------|------|-------------|
| `l7_count` | INTEGER | NULLABLE | Count of L7 children |
| `l6_count` | INTEGER | NULLABLE | Count of L6 children |
| `l5_count` | INTEGER | NULLABLE | Count of L5 children |
| `l4_count` | INTEGER | NULLABLE | Count of L4 children |
| `l3_count` | INTEGER | NULLABLE | Count of L3 children |
| `l2_count` | INTEGER | NULLABLE | Count of L2 children |

---

## PROTECTIONS AND CONSTRAINTS

### 1. **Partitioning Protection**
- **Mechanism**: Time-based partitioning on `content_date`
- **Benefit**: Automatic partition pruning for date-range queries
- **Protection**: Prevents full table scans on date-filtered queries
- **Maintenance**: BigQuery automatically manages partition lifecycle

### 2. **Clustering Protection**
- **Mechanism**: Clustering on `['level', 'conversation_id', 'entity_id']`
- **Benefit**: Optimizes queries filtering by hierarchy level and conversation
- **Protection**: Reduces query cost and latency for hierarchical queries
- **Maintenance**: Clustering maintained automatically by BigQuery

### 3. **Schema Enforcement**
- **Mechanism**: BigQuery enforces schema at insert time
- **Protection**: Prevents insertion of invalid data types or missing required fields
- **Error**: Insert fails if schema mismatch detected

### 4. **NULLABLE Mode**
- **Mechanism**: All fields are NULLABLE (no REQUIRED fields)
- **Benefit**: Allows incremental data loading
- **Protection**: Prevents insertion failures due to missing optional fields
- **Trade-off**: Requires application-level validation for required business logic

### 5. **REPEATED Field Protection**
- **Mechanism**: `source_ids` is REPEATED (array)
- **Protection**: BigQuery validates array structure
- **Error**: Insert fails if non-array value provided for REPEATED field

### 6. **JSON Field Validation**
- **Mechanism**: `metadata` field is JSON type
- **Protection**: BigQuery validates JSON structure
- **Error**: Insert fails if invalid JSON provided
- **Note**: JSON content structure not validated (application-level concern)

---

## DATA FLOW ARCHITECTURE

### Input Sources
1. **Stage 16**: Final promotion stage (claude_code pipeline)
2. **Stage 14**: Structural entity promotion (other pipelines)
3. **Direct inserts**: Manual/API inserts (if any)

### Data Transformation Requirements

**From Stage 15 → entity_unified**:

1. **Direct Mappings**:
   - `entity_id` → `entity_id`
   - `parent_id` → `parent_id`
   - `level` → `level`
   - `source_pipeline` → `source_pipeline`
   - `text` → `text`
   - `content_date` → `content_date`
   - `validation_status` → `validation_status`

2. **Derived Fields**:
   - `entity_type` → Derive from `level` (e.g., "message" for level=5)
   - `entity_mode` → Set to "active" or derive from `validation_status`
   - `conversation_id` → Map from `session_id` when level=8, or derive from parent hierarchy
   - `message_id` → Map from `entity_id` when level=5
   - `sentence_id` → Map from `entity_id` when level=4
   - `span_id` → Map from `entity_id` when level=3
   - `word_id` → Map from `entity_id` when level=2
   - `turn_id` → Derive from parent hierarchy when level=6
   - `source_file` → Map from `source_file` field
   - `source_file_path` → Map from `source_file` field
   - `source_system` → Set to `SOURCE_NAME`
   - `source_ids` → Create array from source identifiers
   - `created_at` → Set to current timestamp
   - `updated_at` → Set to current timestamp
   - `ingestion_job_id` → Map from `run_id`
   - `ingestion_timestamp` → Set to current timestamp
   - `source_message_timestamp` → Map from `timestamp_utc`

3. **Metadata Storage**:
   - All enrichment fields (role, message_type, embeddings, emotions, keywords, intent, etc.) → Store in `metadata` JSON field

4. **Count Fields**:
   - `l7_count`, `l6_count`, `l5_count`, `l4_count`, `l3_count`, `l2_count` → Populate from count rollups in Stage 12

---

## ERROR CONDITIONS

### 1. Schema Mismatch Errors

**Error**: `Schema field mismatch: Field 'field_name' not found in schema`  
**Cause**: Stage 16 tries to insert field that doesn't exist in entity_unified  
**Protection**: BigQuery schema validation  
**Resolution**: Update Stage 16 to match actual schema

**Error**: `Invalid value for field 'source_ids': Expected REPEATED, got STRING`  
**Cause**: Non-array value provided for REPEATED field  
**Protection**: BigQuery type validation  
**Resolution**: Convert to array format

**Error**: `Invalid JSON in field 'metadata'`  
**Cause**: Invalid JSON string provided  
**Protection**: BigQuery JSON validation  
**Resolution**: Ensure valid JSON serialization

### 2. Type Mismatch Errors

**Error**: `Cannot insert STRING into INTEGER field 'level'`  
**Cause**: Wrong data type provided  
**Protection**: BigQuery type coercion rules  
**Resolution**: Ensure correct type conversion

**Error**: `Cannot insert DATE into TIMESTAMP field 'created_at'`  
**Cause**: Type mismatch  
**Protection**: BigQuery type validation  
**Resolution**: Convert DATE to TIMESTAMP

### 3. Partitioning Errors

**Error**: `Partitioning field 'content_date' is NULL`  
**Cause**: NULL value for partitioning field  
**Protection**: BigQuery partitioning constraint  
**Resolution**: Ensure content_date is always set

**Error**: `Invalid date value for partitioning field`  
**Cause**: Invalid date format  
**Protection**: BigQuery date validation  
**Resolution**: Ensure valid DATE format

### 4. Clustering Errors

**Error**: `Clustering field 'level' is NULL`  
**Cause**: NULL value for clustering field  
**Protection**: None (clustering fields can be NULL)  
**Impact**: Reduced query performance  
**Resolution**: Set level value

### 5. Data Quality Errors

**Error**: `Duplicate entity_id detected`  
**Cause**: Same entity_id inserted multiple times  
**Protection**: Application-level (merge_rows_to_table)  
**Resolution**: Use MERGE statement or check before insert

---

## QUERY PATTERNS

### Common Queries

1. **Get all messages in a conversation**:
   ```sql
   SELECT * FROM `entity_unified`
   WHERE conversation_id = 'conv_123'
     AND level = 5
   ORDER BY source_message_timestamp
   ```

2. **Get entity hierarchy**:
   ```sql
   SELECT * FROM `entity_unified`
   WHERE conversation_id = 'conv_123'
   ORDER BY level, parent_id
   ```

3. **Get entities by date range**:
   ```sql
   SELECT * FROM `entity_unified`
   WHERE content_date BETWEEN '2026-01-01' AND '2026-01-31'
   ```

4. **Get enrichment data from metadata**:
   ```sql
   SELECT 
     entity_id,
     JSON_EXTRACT_SCALAR(metadata, '$.role') as role,
     JSON_EXTRACT_SCALAR(metadata, '$.message_type') as message_type
   FROM `entity_unified`
   WHERE level = 5
   ```

---

## MAINTENANCE

### Table Maintenance

- **Partitioning**: Automatic (BigQuery managed)
- **Clustering**: Automatic (BigQuery managed)
- **Schema Updates**: Require ALTER TABLE statements
- **Data Retention**: Managed via partition expiration (if configured)

### Monitoring

- **Query Performance**: Monitor via BigQuery query logs
- **Partition Usage**: Monitor partition sizes and query patterns
- **Schema Drift**: Monitor via schema comparison scripts

---

## CERTIFICATION

**I certify that this document accurately describes the entity_unified table schema, architecture, protections, and data flow requirements as of 2026-01-27.**

**This specification is the source of truth for all pipeline stages that write to entity_unified.**

---

**Next**: See stage-by-stage certification documents for proof that each stage correctly maps to this schema.
