# LLM Refinery Pipeline

## Overview

This pipeline replaces rigid Python/spaCy stages with LLM-based processing for the L2-L8 hierarchical data structure. Instead of error-prone regex and NLP rules, we use local LLMs (via Ollama) to intelligently extract and structure conversation data.

## The L2-L8 Hierarchical Structure

```
L8 ─ Conversation (root)
 └─ L7 ─ Topic Segment (semantic groupings)
     └─ L6 ─ Turn (speaker change boundary)
         └─ L5 ─ Message (single utterance)
             └─ L4 ─ Sentence (grammatical unit)
                 └─ L3 ─ Span (phrase/clause)
                     └─ L2 ─ Word (token with attributes)
```

## Why LLM Processing?

| Old Approach (spaCy) | New Approach (LLM) |
|----------------------|-------------------|
| Rigid sentence boundary rules | Contextual understanding |
| POS tagging errors on informal text | Semantic understanding |
| No topic segmentation | Intelligent topic detection |
| No turn detection | Speaker intent recognition |
| Fixed NER categories | Dynamic entity extraction |
| No sentiment context | Full emotional understanding |

## Available Models (Ollama)

- `llama4:scout` (67GB) - Full 10M context, best quality
- `qwen2.5-coder:32b` (19GB) - Code-aware, good for technical
- `llama3.2:latest` (2GB) - Fast processing, lower quality

## Usage

```bash
# Process conversations with default settings
python -m pipelines.llm_refinery.process --input data/web_exports/claude_web/conversations.json

# Use specific model
python -m pipelines.llm_refinery.process --input data.json --model qwen2.5-coder:32b

# Process subset
python -m pipelines.llm_refinery.process --input data.json --limit 10
```

## Output Schema

Each layer produces entities matching the `entity_unified` BigQuery schema with:
- `entity_id`: Deterministic ID based on content hash
- `level`: Integer 2-8
- `parent_id`: Link to parent entity
- `text`: Extracted content
- `metadata`: Rich LLM-extracted attributes

## Pipeline Stages

1. **L8 Extraction** - Parse conversation boundaries
2. **L7 Extraction** - Detect topic segments via LLM
3. **L6 Extraction** - Identify speaker turns
4. **L5 Extraction** - Extract individual messages
5. **L4 Extraction** - LLM-based sentence segmentation
6. **L3 Extraction** - Semantic span/phrase extraction
7. **L2 Extraction** - Word-level with semantic attributes
