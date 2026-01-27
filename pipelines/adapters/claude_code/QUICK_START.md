# Quick Start: Running the Claude Code Pipeline

**Date:** 2026-01-22  
**Status:** ✅ Ready to Run

---

## Prerequisites

1. **Python 3.10+** installed
2. **Google Cloud credentials** configured
3. **BigQuery dataset** `spine` exists
4. **Required packages** installed:
   ```bash
   pip install spacy google-cloud-bigquery google-cloud-secret-manager
   python -m spacy download en_core_web_sm
   ```

---

## Quick Run

### Option 1: Run Full Pipeline (Recommended)

```bash
cd /Users/jeremyserna/Truth_Engine/pipelines/claude_code/scripts

# Run all stages (0-16)
python run_pipeline.py
```

### Option 2: Run with Custom Source Directory

```bash
# Point to your Claude Code session files
python run_pipeline.py --source-dir ~/my-claude-sessions
```

### Option 3: Run Specific Stages

```bash
# Run stages 0-4 only (ingestion phase)
python run_pipeline.py --end-stage 4

# Run stages 5-10 (entity creation)
python run_pipeline.py --start-stage 5 --end-stage 10

# Run specific stages
python run_pipeline.py --stages 0,1,2,3,4
```

### Option 4: Dry-Run (Test Without Writing)

```bash
# Test the pipeline without writing to BigQuery
python run_pipeline.py --dry-run
```

---

## What Happens

### Stage 0: Assessment (Discovery)
- Discovers all JSONL files in source directory
- Analyzes data structure
- Generates discovery manifest
- **Output:** Assessment report + discovery manifest

### Stage 1: Extraction
- Extracts messages from JSONL files
- Parses conversation structure
- **Output:** `claude_code_stage_1` table

### Stage 2: Cleaning
- Normalizes data
- Deduplicates messages
- **Output:** `claude_code_stage_2` table

### Stage 3: THE GATE (Identity)
- Generates entity IDs using Primitive.identity
- **Output:** `claude_code_stage_3` table

### Stage 4: Staging + LLM Text Correction
- Corrects spelling for spaCy processing
- Uses Gemini CLI/API Flash-Lite
- **Output:** `claude_code_stage_4` table

### Stage 5: L8 Conversations
- Creates conversation entities
- Calculates word/lemma counts
- **Output:** `claude_code_stage_5` table

### Stage 6: L6 Turns
- Creates turn entities
- Groups messages into turns
- **Output:** `claude_code_stage_6` table

### Stage 7: L5 Messages
- Creates message entities
- Includes thinking blocks
- **Output:** `claude_code_stage_7` table

### Stage 8: L4 Sentences
- Creates sentence entities using spaCy
- Calculates word/lemma counts
- **Output:** `claude_code_stage_8` table

### Stage 9: L3 Spans (NER)
- Extracts named entities using spaCy
- **Output:** `claude_code_stage_9` table

### Stage 10: L2 Words
- Creates word entities using spaCy
- Includes all spaCy token features
- **Output:** `claude_code_stage_10` table

### Stage 11: Parent-Child Validation
- Validates parent-child links
- **Output:** Validation report

### Stage 12: Count Denormalization
- Rolls up counts from child to parent levels
- **Output:** Updated tables with counts

### Stage 13: Pre-Promotion Validation
- Validates data before promotion
- **Output:** Validation report

### Stage 14: Promotion to entity_unified
- Promotes entities to `entity_unified` table
- **Output:** `spine.entity_unified` table

### Stage 15: Final Validation
- Quality gate validation
- **Output:** Validation report

### Stage 16: Final Promotion
- Final promotion to `entity_unified`
- **Output:** `spine.entity_unified` table (final)

---

## Revolutionary Features Active

When you run the pipeline, these revolutionary features are automatically enabled:

1. **Bitemporal Time-Travel** - Every entity has system_time and valid_time
2. **Event Sourcing** - Every change recorded in event store
3. **Cryptographic Provenance** - Complete data lineage tracked
4. **Knowledge Graphs** - Relationships automatically discovered
5. **Causal Chains** - Causal relationships tracked
6. **Multi-Dimensional Indexing** - Spatial, temporal, semantic indexing
7. **Correction Workflows** - Fix errors while preserving history
8. **State Reconstruction** - Rebuild any entity at any point

---

## Troubleshooting

### "Source directory does not exist"
- Check that `~/.claude/projects` exists
- Or specify `--source-dir` with your path

### "BigQuery table not found"
- Ensure BigQuery dataset `spine` exists
- Check Google Cloud credentials

### "spaCy model not found"
- Run: `python -m spacy download en_core_web_sm`

### "Module not found"
- Ensure you're in the project root
- Check Python path includes Truth_Engine

---

## Next Steps After Running

Once the pipeline completes:

1. **Query the data:**
   ```sql
   SELECT * FROM `spine.entity_unified` 
   WHERE source_name = 'claude_code' 
   LIMIT 10
   ```

2. **Use time-travel queries:**
   ```python
   from pipelines.claude_code.services.revolutionary_services.time_travel_api import TimeTravelAPI
   
   api = TimeTravelAPI()
   conversation = api.query_conversation_at_time(
       conversation_id="conv_123",
       valid_time=datetime(2026, 1, 15),
   )
   ```

3. **Explore knowledge graphs:**
   ```python
   from pipelines.claude_code.services.revolutionary_services.knowledge_graph_service import KnowledgeGraphService
   
   kg = KnowledgeGraphService()
   relationships = kg.discover_reply_relationships("conv_123")
   ```

---

## Ready to Show People

The pipeline is ready to run. When you execute it:

- ✅ All stages will run sequentially
- ✅ Revolutionary features will be active
- ✅ Data will flow through the complete pipeline
- ✅ Results will be in `spine.entity_unified`

**This is real. This works. This is ready to show.**
