> **DEPRECATED**: This document has been superseded.
> - **Superseded By**: [CANONICAL_KNOWLEDGE_ATOMS_COMPLETE.md](CANONICAL_KNOWLEDGE_ATOMS_COMPLETE.md) or [ID_SYSTEM_IMPLEMENTATION_COMPLETE.md](ID_SYSTEM_IMPLEMENTATION_COMPLETE.md) or [ID_SYSTEM_FEDERATION_UPGRADE_COMPLETE.md](ID_SYSTEM_FEDERATION_UPGRADE_COMPLETE.md)
> - **Deprecated On**: 2026-01-27
> - **Archived On**: 2026-01-27
> - **Reason**: Consolidated into complete implementation documents.
>
> This document has been moved to archive. See archive location below.

---

# Pipeline Knowledge Atoms Implementation

**Date:** 2026-01-22  
**Status:** ✅ **IMPLEMENTED - All stages can now produce knowledge atoms**

---

## The Vision

**Every pipeline stage produces knowledge atoms about its execution.**

This creates meta-knowledge - knowledge about the pipeline process itself, not just the data being processed. This enables:

- **Learning from pipeline behavior**: What patterns emerge? What works well?
- **Understanding transformations**: How does data flow through stages?
- **Performance insights**: What are the bottlenecks? What's efficient?
- **Quality tracking**: What errors occur? What warnings are common?
- **Discovery patterns**: What does each stage discover about the data?

---

## Implementation

### Shared Utility Created

**File:** `pipelines/claude_code/scripts/shared/pipeline_knowledge_atoms.py`

**Functions:**
- `exhale_pipeline_knowledge()` - Full knowledge atom creation
- `exhale_stage_summary()` - Quick summary atom creation

### Knowledge Atom Schema

Knowledge atoms are written to: `{PROJECT_ID}.{DATASET_ID}.knowledge_atoms`

**Schema:**
- `atom_id`: Unique identifier (format: `atom:{source_name}:{hash12}`)
- `content`: Human-readable knowledge content
- `content_normalized`: Lowercased version for search
- `content_hash`: SHA256 hash for deduplication
- `source_name`: `{pipeline_name}_stage_{N}`
- `source_id`: Run ID
- `created_at`: Timestamp
- `run_id`: Pipeline run ID
- `metadata`: JSON with structured data (discoveries, transformations, metrics, insights, patterns, errors, warnings)
- `synced_to_cloud`: Always `true` (writing directly to BigQuery)

---

## Usage Pattern

### In Each Pipeline Stage

Add knowledge atom generation in the **AGENT phase** (after processing, before writing to HOLD₂):

```python
from shared.pipeline_knowledge_atoms import exhale_pipeline_knowledge

# ... stage processing ...

# AGENT: Exhale knowledge atoms about pipeline execution
exhale_pipeline_knowledge(
    stage=0,  # Stage number
    stage_name="Discovery",  # Human-readable name
    run_id=run_id,
    discoveries={
        "files_discovered": 1044,
        "messages_discovered": 79334,
        "thinking_blocks": 1234,
    },
    transformations={
        "input_files": 1044,
        "output_manifest": 1,
        "compression_ratio": 1044.0,
    },
    metrics={
        "processing_time_seconds": 12.5,
        "files_per_second": 83.5,
        "memory_peak_mb": 512,
    },
    insights=[
        "JSONL format is consistent across all files",
        "All files have session_id field",
        "Average 76 messages per file",
    ],
    patterns=[
        "File size follows power law distribution",
        "Most sessions are single-day interactions",
    ],
    errors=[],
    warnings=[
        "3 files had malformed JSON lines (skipped)",
    ],
)
```

### Quick Summary Pattern

For simple cases:

```python
from shared.pipeline_knowledge_atoms import exhale_stage_summary

exhale_stage_summary(
    stage=5,
    stage_name="L8 Conversation Creation",
    run_id=run_id,
    summary="Created 351 conversation entities from 31,021 messages",
    stats={
        "conversations_created": 351,
        "avg_messages_per_conversation": 88.3,
    },
)
```

---

## What Knowledge Atoms Capture

### 1. Discoveries
**What did the stage discover about the data?**
- File counts, message counts, entity counts
- Data structure patterns
- Field availability
- Data quality indicators

### 2. Transformations
**How did the stage transform data?**
- Input → Output ratios
- Aggregation ratios
- Filtering statistics
- Data reduction/expansion

### 3. Metrics
**Performance and resource usage:**
- Processing time
- Throughput (rows/second, files/second)
- Memory usage
- Cost (if applicable)

### 4. Insights
**What did we learn?**
- Data quality observations
- Format consistency
- Pattern observations
- Anomalies discovered

### 5. Patterns
**What patterns emerged?**
- Distribution patterns
- Relationship patterns
- Temporal patterns
- Structural patterns

### 6. Errors
**What went wrong?**
- Error types
- Error frequencies
- Error contexts

### 7. Warnings
**What should we be aware of?**
- Data quality warnings
- Performance warnings
- Configuration warnings

---

## Integration Status

### ✅ Stage 0: Discovery
- **Status:** Implemented
- **Knowledge Atoms:** Discoveries, insights, patterns about source data

### ⏳ Stages 1-16: To Be Implemented
- **Pattern:** Add `exhale_pipeline_knowledge()` call after processing, before writing to HOLD₂
- **Location:** In the AGENT phase of each stage

---

## Example: Stage 0 Knowledge Atom

**Content:**
```
Pipeline Stage 0: Discovery
Run ID: run:abc123

DISCOVERIES:
  - files_discovered: 1044
  - files_analyzed: 1044
  - messages_discovered: 79334
  - thinking_blocks: 1234
  - tool_calls: 5678
  - models_used: claude-sonnet-4-20250514, claude-opus-4-20250514

INSIGHTS:
  - Source data format: jsonl
  - Assessment result: GO

PATTERNS:
  - Average messages per file: 76.0
```

**Metadata (JSON):**
```json
{
  "pipeline": "claude_code",
  "stage": 0,
  "stage_name": "Discovery",
  "run_id": "run:abc123",
  "discoveries": {
    "files_discovered": 1044,
    "messages_discovered": 79334
  },
  "insights": [
    "Source data format: jsonl",
    "Assessment result: GO"
  ],
  "patterns": [
    "Average messages per file: 76.0"
  ]
}
```

---

## Querying Knowledge Atoms

### Find All Knowledge from a Pipeline Run

```sql
SELECT 
  atom_id,
  content,
  metadata
FROM `flash-clover-464719-g1.spine.knowledge_atoms`
WHERE source_name LIKE 'claude_code_stage_%'
  AND run_id = 'run:abc123'
ORDER BY created_at
```

### Find Insights from All Stages

```sql
SELECT 
  JSON_EXTRACT_SCALAR(metadata, '$.stage') as stage,
  JSON_EXTRACT_SCALAR(metadata, '$.stage_name') as stage_name,
  JSON_EXTRACT_ARRAY(metadata, '$.insights') as insights
FROM `flash-clover-464719-g1.spine.knowledge_atoms`
WHERE source_name LIKE 'claude_code_stage_%'
  AND JSON_EXTRACT_ARRAY(metadata, '$.insights') IS NOT NULL
```

### Find Performance Patterns

```sql
SELECT 
  JSON_EXTRACT_SCALAR(metadata, '$.stage') as stage,
  JSON_EXTRACT_SCALAR(metadata, '$.metrics.processing_time_seconds') as duration
FROM `flash-clover-464719-g1.spine.knowledge_atoms`
WHERE source_name LIKE 'claude_code_stage_%'
  AND JSON_EXTRACT(metadata, '$.metrics') IS NOT NULL
ORDER BY CAST(duration AS FLOAT64) DESC
```

---

## Benefits

### 1. **Pipeline Self-Awareness**
The pipeline learns about itself. Each run produces knowledge about how it behaves.

### 2. **Pattern Discovery**
Query knowledge atoms to discover patterns:
- Which stages are slowest?
- What errors are most common?
- What insights emerge across runs?

### 3. **Quality Tracking**
Track data quality over time:
- How does data quality change?
- What warnings are persistent?
- What patterns indicate problems?

### 4. **Performance Optimization**
Identify bottlenecks:
- Which stages take longest?
- What's the throughput per stage?
- Where can we optimize?

### 5. **Documentation**
Knowledge atoms serve as living documentation:
- What does each stage discover?
- How does data transform?
- What patterns emerge?

---

## Next Steps

1. ✅ **Utility Created** - `pipeline_knowledge_atoms.py`
2. ✅ **Stage 0 Implemented** - Example integration
3. ⏳ **Stages 1-16** - Add knowledge atom generation to all stages
4. ⏳ **Query Interface** - Create MCP server or utility for querying knowledge atoms
5. ⏳ **Visualization** - Dashboard showing pipeline knowledge over time

---

## Framework Alignment

**✅ HOLD → AGENT → HOLD Pattern:**
- Knowledge atoms are produced in the **AGENT phase**
- They capture what the AGENT discovered/transformed
- They are written to HOLD₂ (knowledge_atoms table)

**✅ Furnace Principle:**
- **Truth**: Pipeline execution metadata
- **Heat**: Structuring into knowledge atoms
- **Meaning**: Queryable knowledge about pipeline behavior
- **Care**: Learn from pipeline patterns

**✅ Stage Five Grounding:**
- Knowledge atoms document what each stage **cannot see** (blind spots)
- They capture the **boundaries** of each stage
- They record the **purpose** and **structure** of each stage

---

*The pipeline now produces knowledge about itself. Each run teaches us something new.*
