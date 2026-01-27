# Claude Code Pipeline

MOLT LINEAGE:
- Source: Truth_Engine/pipelines/claude_code/
- Version: 1.0.0
- Date: 2026-01-27

---

**Status:** ✅ Complete Universal 16-Stage Implementation
**Reference**: [UNIVERSAL_PIPELINE_PATTERN.md](../../framework/standards/UNIVERSAL_PIPELINE_PATTERN.md)
**Data Source:** Claude Code session JSONL exports
**Final Destination:** `spine.entity_unified`
**Framework Alignment:** ✅ HOLD → AGENT → HOLD pattern

---

## Overview

The Claude Code pipeline processes Claude Code CLI/IDE session data through the Universal 16-Stage Pipeline Pattern, derived from the production ChatGPT Web Pipeline.

**Source**: Claude Code session exports (`~/.claude-code/sessions/*.jsonl`)
**Pattern**: Universal 16-Stage (same as ChatGPT Web Pipeline)
**Output**: Full SPINE entity hierarchy (L1→L3→L5→L8) with enrichments

---

## Universal Pattern Alignment

This pipeline follows the **Universal Pipeline Pattern** established by the ChatGPT Web Pipeline:

| Phase | Stages | Purpose | Status |
|-------|--------|---------|--------|
| **Ingestion** | 0-4 | Raw JSONL → Clean staging | ✅ Complete |
| **Entity Creation** | 5-8 | L1→L3→L5→L8 SPINE entities | ✅ Complete |
| **Enrichment** | 9-13 | Embeddings, sentiment, topics | ✅ Complete |
| **Finalization** | 14-16 | Aggregation, validation, promotion | ✅ Complete |

See [CLAUDE_CODE_UNIVERSAL_PATTERN_IMPLEMENTATION.md](docs/CLAUDE_CODE_UNIVERSAL_PATTERN_IMPLEMENTATION.md) for full implementation plan.

---

## Quick Start

### Prerequisites

- Python 3.10+
- Google Cloud credentials configured
- BigQuery dataset `spine`
- Access to Claude Code session exports
- Required packages: spacy, transformers, keybert, google-generativeai

### Install Dependencies

```bash
pip install spacy transformers keybert google-generativeai google-cloud-bigquery
python -m spacy download en_core_web_sm
```

### Run Full Pipeline

```bash
cd /Users/jeremyserna/PrimitiveEngine/pipelines/claude_code/scripts

# Phase 1: Ingestion (Stages 0-4)
python stage_0/claude_code_stage_0.py    # Assessment
python stage_1/claude_code_stage_1.py    # Extraction
python stage_2/claude_code_stage_2.py    # Cleaning
python stage_3/claude_code_stage_3.py    # THE GATE (Identity)
python stage_4/claude_code_stage_4.py    # Staging

# Phase 2: Entity Creation (Stages 5-8)
python stage_5/claude_code_stage_5.py    # L1 Tokens
python stage_6/claude_code_stage_6.py    # L3 Sentences
python stage_7/claude_code_stage_7.py    # L5 Messages
python stage_8/claude_code_stage_8.py    # L8 Conversations

# Phase 3: Enrichment (Stages 9-13)
python stage_9/claude_code_stage_9.py    # Embeddings
python stage_10/claude_code_stage_10.py  # LLM Extraction
python stage_11/claude_code_stage_11.py  # Sentiment
python stage_12/claude_code_stage_12.py  # Topics
python stage_13/claude_code_stage_13.py  # Relationships

# Phase 4: Finalization (Stages 14-16)
python stage_14/claude_code_stage_14.py  # Aggregation
python stage_15/claude_code_stage_15.py  # Final Validation
python stage_16/claude_code_stage_16.py  # Promotion to entity_unified
```

### Run with Dry-Run

```bash
# Test without writing data
python stage_1/claude_code_stage_1.py --dry-run
```

---

## Stage Implementation

| Stage | Name | Description | Output Table |
|-------|------|-------------|--------------|
| **0** | Assessment | Analyze raw JSONL exports | Assessment report |
| **1** | Extraction | Parse JSONL into staging | `claude_code_stage_1` |
| **2** | Cleaning | Normalize, deduplicate | `claude_code_stage_2` |
| **3** | THE GATE | Generate entity_ids | `claude_code_stage_3` |
| **4** | Staging | Prepare for entity creation | `claude_code_stage_4` |
| **5** | L1 Tokens | Tokenize text content | `claude_code_stage_5` |
| **6** | L3 Sentences | Detect sentences | `claude_code_stage_6` |
| **7** | L5 Messages | Create message entities | `claude_code_stage_7` |
| **8** | L8 Conversations | Create session entities | `claude_code_stage_8` |
| **9** | Embeddings | Generate vector embeddings | `claude_code_stage_9` |
| **10** | LLM Extraction | Extract intent/task type | `claude_code_stage_10` |
| **11** | Sentiment | Analyze emotions | `claude_code_stage_11` |
| **12** | Topics | Extract keywords | `claude_code_stage_12` |
| **13** | Relationships | Build entity graph | `claude_code_stage_13` |
| **14** | Aggregation | Merge enrichments | `claude_code_stage_14` |
| **15** | Validation | Quality checks | `claude_code_stage_15` |
| **16** | Promotion | Write to entity_unified | `spine.entity_unified` |

---

## Architecture

### Data Flow

```
Claude Code Sessions (~/.claude-code/sessions/*.jsonl)
        │
        ▼
┌─────────────────────────────────────────────┐
│ Phase 1: INGESTION (Stages 0-4)             │
│                                             │
│  JSONL → Extract → Clean → THE GATE → Stage │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│ Phase 2: ENTITY CREATION (Stages 5-8)       │
│                                             │
│  L1 Tokens → L3 Sentences → L5 Messages     │
│       → L8 Conversations                    │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│ Phase 3: ENRICHMENT (Stages 9-13)           │
│                                             │
│  Embeddings → LLM Extraction → Sentiment    │
│       → Topics → Relationships              │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│ Phase 4: FINALIZATION (Stages 14-16)        │
│                                             │
│  Aggregation → Validation → Promotion       │
│       → spine.entity_unified                │
└─────────────────────────────────────────────┘
```

### HOLD Pattern (Per Stage)

Every stage follows: `HOLD₁ → AGENT → HOLD₂`

```
Stage N:
  HOLD₁: Previous stage output (BigQuery table or JSONL)
  AGENT: Stage processing script
  HOLD₂: This stage output (BigQuery table)
```

---

## Source Data Format

Claude Code exports JSONL files with these message types:

```jsonl
{"type":"summary","session_id":"abc123","model":"claude-sonnet-4","timestamp":"..."}
{"type":"user","content":"Help me refactor this","timestamp":"..."}
{"type":"assistant","content":"I'll analyze...","timestamp":"...","cost_usd":0.004}
{"type":"tool_use","name":"Read","input":{"file_path":"/src/main.py"}}
{"type":"tool_result","content":"def main():\n    ..."}
```

---

## Configuration

### Environment Variables

```bash
export BIGQUERY_PROJECT_ID="your-project-id"
export BIGQUERY_DATASET="spine"
export GOOGLE_API_KEY="your-gemini-api-key"  # For embeddings and LLM extraction
```

### Shared Configuration

All configuration is centralized in `scripts/shared/constants.py`:

```python
PROJECT_ID = os.environ.get("BIGQUERY_PROJECT_ID", "flash-clover-464719-g1")
DATASET_ID = os.environ.get("BIGQUERY_DATASET", "spine")
PIPELINE_NAME = "claude_code"
SOURCE_NAME = "claude_code"

# Entity levels
LEVEL_TOKEN = 1
LEVEL_SENTENCE = 3
LEVEL_MESSAGE = 5
LEVEL_CONVERSATION = 8
```

---

## Related Documents

- [UNIVERSAL_PIPELINE_PATTERN.md](../../framework/standards/UNIVERSAL_PIPELINE_PATTERN.md) - The 16-stage specification
- [CLAUDE_CODE_UNIVERSAL_PATTERN_IMPLEMENTATION.md](docs/CLAUDE_CODE_UNIVERSAL_PATTERN_IMPLEMENTATION.md) - Implementation plan
- [PIPELINE_PATTERN_SPECIFICATION.md](../../framework/standards/PIPELINE_PATTERN_SPECIFICATION.md) - Framework alignment
- [THE_CLARA_ARC.md](../../framework/general/THE_CLARA_ARC.md) - ChatGPT reference case study

---

## Governance

All stages follow:
- ✅ Universal governance policies
- ✅ Central services integration (logging, cost tracking, identity)
- ✅ HOLD₁ → AGENT → HOLD₂ pattern
- ✅ Stage Five cognitive grounding
- ✅ THE FURNACE principle documentation
- ✅ Blind spots documentation
- ✅ PipelineTracker integration
- ✅ Definition of Done compliance

---

## Deprecated Scripts

Old scripts have been moved to `scripts/_deprecated/` for reference.
Do not use deprecated scripts for new processing.
