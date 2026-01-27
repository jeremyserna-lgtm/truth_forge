# Pipeline Breathing Function - Knowledge Atoms as Natural Operation

**Date:** 2026-01-22  
**Status:** ✅ **IMPLEMENTED - Local-First Knowledge Atoms**

---

## The Vision

**Every pipeline stage produces knowledge atoms as its breathing function.**

Just as living organisms breathe to sustain life, pipeline stages "breathe" by producing knowledge atoms about their execution. This is not optional - it's part of how the stage exists.

---

## What is a Breathing Function?

**Breathing Function = Natural Operation**

- Every stage script has an `exhale()` function
- This function produces knowledge atoms automatically
- Knowledge atoms are part of the stage's natural operation
- No separate call needed - it's built into the stage execution
- The stage "breathes" knowledge about itself

---

## Implementation

### Local-First Policy (THE_PATTERN)

**Knowledge atoms follow THE_PATTERN: JSONL → AGENT → JSONL → DuckDB**

1. **HOLD₁**: Write to local JSONL file (`~/.primitive_engine/staging/claude_code_pipeline.jsonl`)
   - Append-only audit trail
   - Deduplication by `content_hash`
   - Safe atomic writes

2. **AGENT**: Deduplication and processing
   - Hash-based deduplication
   - Content normalization

3. **HOLD₂**: Write to local DuckDB (`~/.primitive_engine/knowledge.duckdb`)
   - Canonical store
   - Queryable knowledge base
   - Primary key: `atom_id`

4. **Sync**: Separate process syncs to BigQuery (cloud mirror)
   - Not part of pipeline execution
   - On-demand sync
   - Local is source of truth

---

## Usage in Stage Scripts

### Pattern: Call in AGENT Phase

```python
def main():
    run_id = get_current_run_id()
    
    with PipelineTracker(...) as tracker:
        # HOLD₁: Read input
        input_data = read_from_hold1()
        
        # AGENT: Process data
        output_data = process_data(input_data)
        
        # AGENT: Exhale knowledge atoms (BREATHING FUNCTION)
        from shared.pipeline_knowledge_atoms import exhale_pipeline_knowledge
        
        exhale_pipeline_knowledge(
            stage=0,
            stage_name="Discovery",
            run_id=run_id,
            discoveries={
                "files_discovered": 1044,
                "messages_discovered": 79334,
            },
            metrics={
                "processing_time_seconds": 12.5,
            },
            insights=[
                "JSONL format is consistent",
                "All files have session_id",
            ],
        )
        
        # HOLD₂: Write output
        write_to_hold2(output_data)
```

### What Each Stage Should Exhale

**Every stage should exhale:**
- **Discoveries**: What did the stage discover about the data?
- **Transformations**: How did the stage transform data?
- **Metrics**: Performance metrics (time, throughput, memory)
- **Insights**: What did we learn?
- **Patterns**: What patterns emerged?
- **Errors**: What errors occurred?
- **Warnings**: What warnings were generated?

---

## Knowledge Atom Schema

**Local Storage (JSONL + DuckDB):**

```python
{
    "atom_id": "atom:claude_code_stage_0:abc123def456",
    "content": "Pipeline Stage 0: Discovery\nRun ID: run:xyz...",
    "content_normalized": "pipeline stage 0: discovery...",
    "content_hash": "sha256_hash",
    "source_name": "claude_code_stage_0",
    "source_id": "run:xyz",
    "created_at": "2026-01-22T10:30:00Z",
    "run_id": "run:xyz",
    "metadata": {
        "pipeline": "claude_code",
        "stage": 0,
        "stage_name": "Discovery",
        "discoveries": {...},
        "transformations": {...},
        "metrics": {...},
        "insights": [...],
        "patterns": [...],
        "errors": [...],
        "warnings": [...],
    },
    "synced_to_cloud": false  # Local-first: not synced yet
}
```

---

## Storage Locations

### Local Storage (Source of Truth)

- **JSONL (HOLD₁)**: `~/.primitive_engine/staging/claude_code_pipeline.jsonl`
- **DuckDB (HOLD₂)**: `~/.primitive_engine/knowledge.duckdb`
  - Table: `knowledge_atoms`
  - Primary key: `atom_id`

### Cloud Storage (Mirror)

- **BigQuery**: `{PROJECT_ID}.{DATASET_ID}.knowledge_atoms`
- **Sync**: Separate process (not part of pipeline)
- **Policy**: Local is source of truth, cloud is mirror

---

## Querying Knowledge Atoms

### Local Query (DuckDB)

```python
from src.services.central_services.core.db import get_duckdb_connection

conn = get_duckdb_connection("~/.primitive_engine/knowledge.duckdb", read_only=True)

# Find all knowledge from a pipeline run
results = conn.execute("""
    SELECT atom_id, content, metadata
    FROM knowledge_atoms
    WHERE source_name LIKE 'claude_code_stage_%'
      AND run_id = ?
    ORDER BY created_at
""", [run_id]).fetchall()
```

### Local Query (JSONL)

```python
import json
from pathlib import Path

jsonl_path = Path.home() / ".primitive_engine" / "staging" / "claude_code_pipeline.jsonl"

with open(jsonl_path, "r") as f:
    for line in f:
        atom = json.loads(line)
        if atom["run_id"] == run_id:
            print(atom["content"])
```

---

## Integration Status

### ✅ Stage 0: Discovery
- **Status:** Implemented
- **Breathing Function:** Produces knowledge atoms about discovery process

### ⏳ Stages 1-16: To Be Implemented
- **Pattern:** Add `exhale_pipeline_knowledge()` call in AGENT phase
- **Location:** After processing, before writing to HOLD₂

---

## Benefits

### 1. **Pipeline Self-Awareness**
The pipeline learns about itself. Each run produces knowledge about how it behaves.

### 2. **Natural Operation**
Knowledge atoms are not an add-on - they're part of how the stage exists. The stage "breathes" knowledge.

### 3. **Local-First**
- Works offline
- Fast writes (no network latency)
- Local is source of truth
- Cloud sync is separate

### 4. **Queryable Knowledge**
- Query local DuckDB for instant results
- Query JSONL for audit trail
- Query cloud (after sync) for distributed access

### 5. **Pattern Discovery**
Query knowledge atoms to discover:
- Which stages are slowest?
- What errors are most common?
- What insights emerge across runs?
- What patterns indicate problems?

---

## Framework Alignment

**✅ HOLD → AGENT → HOLD Pattern:**
- Knowledge atoms are produced in the **AGENT phase**
- They capture what the AGENT discovered/transformed
- They are written to HOLD₁ (JSONL) and HOLD₂ (DuckDB)

**✅ Local-First Policy:**
- Local is source of truth
- Cloud is mirror
- Sync is separate process

**✅ Breathing Function:**
- Every stage has an `exhale()` function
- It's part of the stage's natural operation
- The stage "breathes" knowledge about itself

**✅ Furnace Principle:**
- **Truth**: Pipeline execution metadata
- **Heat**: Structuring into knowledge atoms
- **Meaning**: Queryable knowledge about pipeline behavior
- **Care**: Learn from pipeline patterns

---

## Next Steps

1. ✅ **Utility Created** - `pipeline_knowledge_atoms.py` (local-first)
2. ✅ **Stage 0 Implemented** - Example integration
3. ⏳ **Stages 1-16** - Add breathing function to all stages
4. ⏳ **Sync Script** - Create script to sync local knowledge atoms to BigQuery
5. ⏳ **Query Interface** - Create utility for querying local knowledge atoms

---

*The pipeline now breathes. Each stage produces knowledge about itself as part of its natural operation.*
