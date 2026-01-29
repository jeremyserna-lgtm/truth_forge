# Stages 1, 2, 3 Specification - Claude Code Pipeline

**Date**: 2026-01-27  
**Status**: ✅ Production Ready  
**Critical**: These stages are foundational - pipeline cannot proceed without them

---

## Executive Summary

Stages 1, 2, and 3 form the **foundational data pipeline** for Claude Code data processing:

- **Stage 1**: Extracts raw messages from JSONL files
- **Stage 2**: Cleans and normalizes extracted data
- **Stage 3**: **THE GATE** - Generates unique entity IDs (only user, assistant, thinking blocks pass through)

**⚠️ CRITICAL**: Stage 3 acts as THE GATE - only messages with `role IN ('user', 'assistant')` OR `message_type = 'thinking'` receive entity IDs. All other messages are filtered out.

---

## Stage 1: Data Extraction

### Purpose
Extract raw message data from Claude Code JSONL session files and load into BigQuery.

### Input
- **Source**: JSONL files in source directory
- **Format**: Claude Code session files (one message per line)
- **Message Types**: `user`, `assistant`, `tool_use`, `tool_result`, `summary`

### Processing
1. **File Discovery**: Recursively finds all `.jsonl` files in source directory
2. **Message Parsing**: 
   - Parses each JSON line
   - Extracts message metadata (role, type, content, timestamp)
   - Handles `summary` messages for session metadata
3. **Fingerprint Generation**: Creates deterministic hash for deduplication
   - Formula: `SHA256(session_id:message_index:content[:100])[:32]`
4. **Data Loading**: Uses `merge_rows_to_table()` for idempotent inserts
   - Match key: `fingerprint`
   - Preserves all runs (can step back)

### Output Schema
```python
{
    "extraction_id": "ext:{session_id}:{message_index}:{fingerprint[:8]}",
    "session_id": str,              # Session identifier
    "message_index": int,            # Message position in session
    "message_type": str,             # "user", "assistant", "tool_use", etc.
    "role": str,                     # "user", "assistant", "tool", or None
    "content": str,                  # Message content (JSON string if complex)
    "timestamp": datetime,            # Message timestamp
    "model": str,                     # Model used (if available)
    "cost_usd": float,               # Cost in USD (if available)
    "tool_name": str,                # Tool name (if tool_use)
    "tool_input": str,               # Tool input JSON (if tool_use)
    "tool_output": str,              # Tool output (if tool_result)
    "source_file": str,              # Path to source JSONL file
    "content_date": date,            # Date extracted from timestamp
    "fingerprint": str,              # 32-char hash for deduplication
    "extracted_at": datetime,        # When this record was extracted
    "run_id": str                    # Pipeline run identifier
}
```

### Key Features
- ✅ **Idempotent**: Re-running doesn't create duplicates (uses fingerprint)
- ✅ **Data Preservation**: All runs preserved (can step back)
- ✅ **Error Handling**: Graceful handling of malformed JSON, missing fields
- ✅ **Deduplication**: Fingerprint-based duplicate detection

### Role Assignment Logic
```python
if message_type == "user":
    role = "user"
elif message_type == "assistant":
    role = "assistant"
elif message_type == "tool_result":
    role = "tool"
else:
    role = None  # tool_use, summary, etc.
```

### Table Configuration
- **Table**: `claude_code.stage_1`
- **Partitioning**: By `content_date` (daily)
- **Clustering**: `session_id`, `message_type`
- **Match Key**: `fingerprint` (for merge operations)

---

## Stage 2: Data Cleaning

### Purpose
Clean and normalize extracted data: timestamp normalization, content cleaning, deduplication, and data quality validation.

### Input
- **Source**: `claude_code.stage_1` table
- **Filter**: All messages from Stage 1 (no filtering yet)

### Processing
1. **SQL-Based Cleaning**:
   - Content normalization: `TRIM(REGEXP_REPLACE(content, r'\s+', ' '))`
   - Timestamp normalization: UTC conversion
   - Word count calculation
   - Content length calculation
2. **Deduplication**:
   - Uses `ROW_NUMBER() OVER (PARTITION BY fingerprint ORDER BY extracted_at)`
   - Marks duplicates: `is_duplicate = TRUE` for non-first occurrences
3. **Data Loading**: Uses `merge_rows_to_table()` for idempotent inserts
   - Match key: `fingerprint`
   - Preserves all runs (can step back)

### Output Schema
Adds cleaning metadata to Stage 1 schema:
```python
{
    # All Stage 1 fields, plus:
    "content_cleaned": str,          # Normalized content (whitespace cleaned)
    "content_length": int,           # Character count
    "word_count": int,               # Word count
    "timestamp_utc": datetime,       # UTC-normalized timestamp
    "is_duplicate": bool,            # TRUE if duplicate (by fingerprint)
    "cleaned_at": datetime           # When this record was cleaned
}
```

### Key Features
- ✅ **Idempotent**: Re-running doesn't create duplicates
- ✅ **Data Preservation**: All runs preserved (can step back)
- ✅ **Datetime Serialization**: Properly handles BigQuery datetime objects
- ✅ **None Value Handling**: Gracefully handles missing/null values
- ✅ **Error Handling**: Individual row errors caught and logged

### Deduplication Logic
```sql
ROW_NUMBER() OVER (
    PARTITION BY fingerprint 
    ORDER BY extracted_at
) > 1 AS is_duplicate
```
- First occurrence of each fingerprint: `is_duplicate = FALSE`
- Subsequent occurrences: `is_duplicate = TRUE`

### Table Configuration
- **Table**: `claude_code.stage_2`
- **Partitioning**: By `content_date` (daily)
- **Clustering**: `session_id`, `message_type`, `is_duplicate`
- **Match Key**: `fingerprint` (for merge operations)

---

## Stage 3: THE GATE - Identity Generation

### Purpose
**THE GATE** - Generate unique entity IDs for messages. This is where system identities are born. No entity can exist without passing through THE GATE.

### ⚠️ CRITICAL FILTERING POLICY

**Stage 3 only allows the following message types to pass through:**

1. **User Messages**: `role = 'user'`
2. **Assistant Messages**: `role = 'assistant'`
3. **Thinking Blocks**: `message_type = 'thinking'` OR `message_type LIKE '%thinking%'`

**All other messages are filtered out:**
- `tool_use` messages → **FILTERED OUT**
- `tool_result` messages → **FILTERED OUT**
- `summary` messages → **FILTERED OUT**
- Any other message types → **FILTERED OUT**

### Input
- **Source**: `claude_code.stage_2` table
- **Filter**: 
  ```sql
  WHERE NOT is_duplicate
    AND (
      role IN ('user', 'assistant')
      OR message_type = 'thinking'
      OR message_type LIKE '%thinking%'
    )
  ```

### Processing
1. **Filter Non-Duplicates**: Only process `is_duplicate = FALSE` records
2. **Apply Role Filter**: Only user, assistant, and thinking blocks
3. **Generate Entity IDs**:
   - Uses `generate_entity_id(session_id, message_index, fingerprint)`
   - Creates deterministic GUID: `{SOURCE_NAME}:{session_id}:{message_index}:{fingerprint[:12]}`
   - Generates ID: `msg:{16-char hash}`
   - Registers with identity_service
4. **Data Loading**: Uses `merge_rows_to_table()` for idempotent inserts
   - Match key: `entity_id`
   - Preserves all runs (can step back)

### Output Schema
Adds identity metadata to Stage 2 schema:
```python
{
    # All Stage 2 fields, plus:
    "entity_id": str,                 # REQUIRED - Unique entity identifier (THE GATE output)
    "identity_created_at": datetime   # When entity_id was generated
}
```

### Key Features
- ✅ **THE GATE**: Validates no null entity_ids (enforced by schema and validation)
- ✅ **Idempotent**: Re-running doesn't create duplicates (uses entity_id)
- ✅ **Data Preservation**: All runs preserved (can step back)
- ✅ **Role Filtering**: Only user, assistant, thinking blocks pass through
- ✅ **Identity Registration**: All IDs registered with identity_service

### Entity ID Generation
```python
def generate_entity_id(session_id: str, message_index: int, fingerprint: str) -> str:
    # Create GUID from stable components
    guid = f"{SOURCE_NAME}:{session_id}:{message_index}:{fingerprint[:12]}"
    
    # Generate via identity_service
    entity_id = generate_message_id_from_guid(guid, message_index)
    # Returns: "msg:{16-char hash}"
    
    # Register with central registry
    register_id(entity_id, metadata={...})
    
    return entity_id
```

### THE GATE Validation
After processing, Stage 3 validates:
```python
validate_gate_no_null_identity(bq_client, TABLE_STAGE_3, "entity_id")
```
- **Enforcement**: Raises `ValueError` if any null entity_ids found
- **Schema**: `entity_id` is `mode="REQUIRED"` in BigQuery schema
- **Purpose**: Ensures no entity can exist without a valid ID

### Table Configuration
- **Table**: `claude_code.stage_3`
- **Partitioning**: By `content_date` (daily)
- **Clustering**: `entity_id`, `session_id`
- **Match Key**: `entity_id` (for merge operations)

---

## Data Flow Summary

```
JSONL Files
    ↓
[Stage 1: Extraction]
    - Parse JSONL files
    - Extract messages
    - Generate fingerprints
    - Load to stage_1 table
    ↓
[Stage 2: Cleaning]
    - Read from stage_1
    - Clean content
    - Normalize timestamps
    - Mark duplicates
    - Load to stage_2 table
    ↓
[Stage 3: THE GATE]
    - Read from stage_2
    - FILTER: user, assistant, thinking only
    - Generate entity_ids
    - Register with identity_service
    - Validate no null IDs
    - Load to stage_3 table
    ↓
[Downstream Stages]
    - All entities have valid entity_ids
    - Ready for SPINE creation
```

---

## Data Persistence Pattern

All three stages use the **same idempotent persistence pattern**:

### Pattern: `merge_rows_to_table()`

```python
merge_rows_to_table(
    client=client,
    table_id=validated_table,
    rows=records,
    match_key="fingerprint"  # or "entity_id" for Stage 3
)
```

### Benefits
- ✅ **Idempotent**: Re-running doesn't create duplicates
- ✅ **Data Preservation**: All runs preserved (can step back)
- ✅ **SQL Injection Prevention**: All table IDs validated
- ✅ **Error Handling**: Graceful fallback to direct insert if merge fails

### Match Keys
- **Stage 1**: `fingerprint` (32-char hash)
- **Stage 2**: `fingerprint` (32-char hash)
- **Stage 3**: `entity_id` (msg:{16-char hash})

---

## Filtering Logic Details

### Stage 3 Filtering Query

```sql
SELECT *
FROM `claude_code.stage_2`
WHERE NOT is_duplicate
  AND (
    role IN ('user', 'assistant')
    OR message_type = 'thinking'
    OR message_type LIKE '%thinking%'
  )
ORDER BY session_id, message_index
```

### What Passes Through
| role | message_type | Passes? | Reason |
|------|--------------|---------|--------|
| `user` | `user` | ✅ YES | role = 'user' |
| `assistant` | `assistant` | ✅ YES | role = 'assistant' |
| `None` | `thinking` | ✅ YES | message_type = 'thinking' |
| `None` | `thinking_block` | ✅ YES | message_type LIKE '%thinking%' |
| `tool` | `tool_use` | ❌ NO | Not user/assistant, not thinking |
| `tool` | `tool_result` | ❌ NO | Not user/assistant, not thinking |
| `None` | `summary` | ❌ NO | Not user/assistant, not thinking |

### Impact
- **Tool messages are filtered out**: Tool use and tool results do NOT receive entity_ids
- **Only conversation content proceeds**: User messages, assistant messages, and thinking blocks
- **Downstream stages**: Will only see messages that passed through THE GATE

---

## Error Handling

### Stage 1
- **Malformed JSON**: Logged as warning, skipped
- **Missing fields**: Handled gracefully (None values)
- **Merge failures**: Fallback to direct insert

### Stage 2
- **Query errors**: Raised as ValueError with details
- **Row conversion errors**: Individual rows caught, logged, skipped
- **Batch errors**: Tracked and reported
- **Empty batches**: Returns early with zero counts

### Stage 3
- **Query errors**: Raised as ValueError with details
- **ID generation errors**: Should not occur (deterministic)
- **THE GATE validation**: Raises ValueError if null entity_ids found
- **Merge failures**: Fallback to direct insert

---

## Quality Assurance

### Comprehensive Audit
- ✅ **0 Issues Found**: All stages pass comprehensive audit
- ✅ **Type Safety**: Proper datetime serialization
- ✅ **None Handling**: Graceful handling of null values
- ✅ **Error Recovery**: Comprehensive error handling throughout

### Validation Points
1. **Stage 1**: Input table exists and has data
2. **Stage 2**: Input table exists and has data
3. **Stage 3**: 
   - Input table exists and has data
   - **THE GATE**: No null entity_ids (enforced)

---

## Usage Examples

### Run Stage 1
```bash
python3 pipelines/adapters/claude_code/scripts/stage_1/claude_code_stage_1.py
```

### Run Stage 2
```bash
python3 pipelines/adapters/claude_code/scripts/stage_2/claude_code_stage_2.py
```

### Run Stage 3 (THE GATE)
```bash
python3 pipelines/adapters/claude_code/scripts/stage_3/claude_code_stage_3.py
```

### Dry Run (Check Counts)
```bash
python3 pipelines/adapters/claude_code/scripts/stage_3/claude_code_stage_3.py --dry-run
```

---

## Critical Notes

### ⚠️ Stage 3 Filtering is MANDATORY

**The pipeline cannot proceed correctly without Stage 3 filtering.**

- **Tool messages must be filtered out**: They don't represent conversation content
- **Only user/assistant/thinking should have entity_ids**: This is the foundation for downstream processing
- **THE GATE validation ensures data quality**: No entity can exist without a valid ID

### 🔒 Data Persistence is Critical

- **All stages preserve data**: Can step back to previous runs
- **Idempotent operations**: Safe to re-run without duplicates
- **Match keys ensure uniqueness**: Fingerprint (Stages 1-2), entity_id (Stage 3)

### 📊 Monitoring

Check data in stages:
```bash
python3 pipelines/adapters/claude_code/scripts/check_stages_1_2_3_data.py
```

Verify Stage 3:
```bash
python3 pipelines/adapters/claude_code/scripts/stage_3/verify_stage_3.py
```

---

## Conclusion

Stages 1, 2, and 3 form the **foundational pipeline** that:

1. ✅ Extracts raw data from JSONL files
2. ✅ Cleans and normalizes the data
3. ✅ **THE GATE**: Generates unique entity IDs (only for user, assistant, thinking blocks)

**Without these stages working correctly, the pipeline cannot proceed.**

All stages are production-ready with:
- ✅ Professional code quality
- ✅ Comprehensive error handling
- ✅ Idempotent data persistence
- ✅ Proper filtering (Stage 3)

---

**Last Updated**: 2026-01-27  
**Status**: ✅ Production Ready  
**Next Steps**: Proceed to Stage 4 (SPINE creation)
