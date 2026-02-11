# LLM Refinery Pipeline - Process Documentation

## Overview

The LLM Refinery pipeline transforms raw conversation data into a hierarchical entity structure (L2-L8) using local Large Language Models via Ollama. This replaces rigid spaCy/NLP rules with intelligent, context-aware extraction.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LLM REFINERY PIPELINE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  INPUT                    PROCESSING                    OUTPUT              │
│  conversations.json  ──►  Ollama LLM  ──►  entity_unified (34 fields)      │
│  (Claude web export)      (local)          entity_enrichments (45 fields)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Input Stage

### Source Data
- **File**: `data/web_exports/claude_web/conversations.json`
- **Format**: JSON array of conversation objects
- **Size**: ~88MB (119 conversations in production)

### Conversation Structure
```json
{
  "uuid": "abc123-...",
  "name": "Conversation Title",
  "created_at": "2026-01-15T10:30:00Z",
  "chat_messages": [
    {
      "uuid": "msg-uuid-1",
      "sender": "human",
      "text": "How do I configure logging?",
      "created_at": "2026-01-15T10:30:05Z"
    },
    {
      "uuid": "msg-uuid-2", 
      "sender": "assistant",
      "text": "You can configure logging by...",
      "created_at": "2026-01-15T10:30:15Z"
    }
  ]
}
```

---

## 2. Entity Hierarchy (L8 → L2)

The pipeline extracts a 7-layer hierarchy from each conversation:

```
L8 CONVERSATION
│   └── Entire conversation context
│
├── L7 TOPIC SEGMENT
│   │   └── Semantic groupings within conversation
│   │
│   ├── L6 TURN
│   │   │   └── Speaker change boundaries
│   │   │
│   │   └── L5 MESSAGE
│   │       │   └── Individual utterances
│   │       │
│   │       └── L4 SENTENCE
│   │           │   └── Grammatical sentence units
│   │           │
│   │           └── L3 SPAN
│   │               │   └── Phrases/clauses with meaning
│   │               │
│   │               └── L2 WORD
│   │                   └── Tokens with semantic attributes
```

### Layer Details

| Level | Entity Type | Description | Key Attributes |
|-------|-------------|-------------|----------------|
| L8 | Conversation | Root container | title, summary, participants |
| L7 | Topic Segment | Thematic sections | topic_label, is_digression |
| L6 | Turn | Speaker groupings | speaker, turn_type |
| L5 | Message | Single utterance | role, message_type, has_code |
| L4 | Sentence | Grammar unit | sentence_type, complexity, mood |
| L3 | Span | Phrase/clause | span_type, entities, dependencies |
| L2 | Word | Token | word_type, is_key_term, semantic_role |

---

## 3. Processing Flow

### Step 1: Service Initialization

```
┌──────────────────────────────────────────────────────────────┐
│  SERVICE STARTUP                                             │
├──────────────────────────────────────────────────────────────┤
│  1. ServiceFactory creates LLMRefineryService                │
│  2. IdentityService provides run_id for batch                │
│  3. BaseService creates HOLD directories                     │
│  4. Verify Ollama connection at http://localhost:11434       │
└──────────────────────────────────────────────────────────────┘
```

### Step 2: L8 Conversation Processing

```python
# Creates root entity from conversation metadata
L8Conversation(
    uuid=conv["uuid"],
    title=conv.get("name", "Untitled"),
    participants=["human", "assistant"],
    created_at=conv["created_at"],
    summary=None  # Will be enriched later
)
```

### Step 3: L5 Message Extraction (Minimal)

For each message in `chat_messages`:
```python
L5Message(
    uuid=msg["uuid"],
    role=msg["sender"],
    text=msg["text"],
    message_type="question" | "answer" | "statement",
    created_at=msg["created_at"]
)
```

### Step 4: Deep Processing (L7→L2 via LLM)

When `min_level < 5`, the LLM analyzes messages for deeper structure:

```
┌─────────────────────────────────────────────────────────────────┐
│  LLM EXTRACTION CHAIN                                           │
├─────────────────────────────────────────────────────────────────┤
│  L7 TOPICS    ◄── "Identify topic segments in this message..."  │
│  L6 TURNS     ◄── "Detect speaker turn patterns..."             │
│  L4 SENTENCES ◄── "Extract grammatical sentences..."            │
│  L3 SPANS     ◄── "Identify meaningful phrases..."              │
│  L2 WORDS     ◄── "Analyze tokens and their roles..."           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. LLM Prompts

### Topic Segmentation (L7)
```
Analyze this conversation and identify distinct topic segments.
For each segment, provide:
- start_index: message index where topic begins
- end_index: message index where topic ends  
- topic_label: short descriptive label
- is_digression: whether this is an off-topic tangent

Return as JSON array.
```

### Sentence Extraction (L4)
```
Extract all sentences from this message text.
For each sentence provide:
- text: the exact sentence text
- sentence_type: declarative|interrogative|imperative|exclamatory
- complexity: simple|compound|complex
- mood: indicative|subjunctive|conditional|imperative

Return as JSON array.
```

### Word Analysis (L2)
```
Analyze each word token in this span.
For each word provide:
- text: the word
- word_type: noun|verb|adjective|adverb|preposition|conjunction|pronoun|article|interjection
- is_key_term: true if semantically significant
- canonical_form: lemma/root form
- semantic_role: agent|patient|theme|location|instrument|none

Return as JSON array.
```

---

## 5. Central Services Integration

### IdentityService

Provides deterministic, content-based IDs:

```python
from src.truth_forge.services import IdentityService

id_service = IdentityService()

# Generate entity ID from content
entity_id = id_service.generate_id(
    prefix="msg",
    content=message_text,
    parent_id=conversation_id
)
# Result: "msg:a1b2c3d4e5f67890:0000"
```

### BaseService

Provides HOLD pattern directories:

```
data/services/llm_refinery/
├── hold1/      # Raw LLM responses (before validation)
├── hold2/      # Validated entities (before commit)
└── staging/    # Ready for output
```

### LoggingService

Structured logging via structlog:

```python
self.log.info("conversation_processed", 
    uuid=conv_id,
    entity_count=17,
    enrichment_count=2
)
```

---

## 6. Output Schema (entity_unified)

All entities output to a 34-column BigQuery-compatible schema:

| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | STRING | Unique identifier |
| `level` | INT64 | Hierarchy level (2-8) |
| `entity_type` | STRING | conversation/topic/turn/message/sentence/span/word |
| `entity_mode` | STRING | active/archived/deleted |
| `parent_id` | STRING | Parent entity reference |
| `conversation_id` | STRING | Root conversation ID |
| `turn_id` | STRING | Turn reference (nullable) |
| `span_id` | STRING | Span reference (nullable) |
| `text` | STRING | Entity text content |
| `summary` | STRING | AI-generated summary (nullable) |
| `source_pipeline` | STRING | "llm_refinery" |
| `source_system` | STRING | "claude_web" |
| `ingestion_job_id` | STRING | Run ID from IdentityService |
| `metadata` | JSON | Level-specific attributes |
| `relationships` | JSON | Links to other entities |
| `lineage` | JSON | Processing provenance |
| `tags` | ARRAY | Classification tags |
| `quality_score` | FLOAT64 | Extraction confidence |
| `priority` | INT64 | Processing priority |
| `content_date` | DATE | Partition key |
| `created_at` | TIMESTAMP | Original creation time |
| `modified_at` | TIMESTAMP | Last modification |
| `expires_at` | TIMESTAMP | TTL (nullable) |
| `version` | INT64 | Entity version |
| `ingestion_timestamp` | TIMESTAMP | Processing time |
| + 9 more computed fields |

---

## 7. Entity Enrichments (entity_enrichments)

In addition to the core entity_unified output, the pipeline produces **enrichments** that provide deep semantic analysis for selected entity levels.

### Enrichment Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      ENRICHMENT EXTRACTION                              │
├─────────────────────────────────────────────────────────────────────────┤
│  ENTITY              LLM ANALYSIS              ENRICHMENT OUTPUT        │
│  L5 Message  ──►  Sentiment/Emotion  ──►  entity_enrichments (45 cols) │
│  (or L4 Sentence)  Keywords/Topics           for BigQuery              │
│                    Content Classification                               │
└─────────────────────────────────────────────────────────────────────────┘
```

### Configuration

```python
from pipelines.llm_refinery import LLMRefineryService, RefineryConfig

config = RefineryConfig(
    enable_enrichments=True,     # Enable enrichment extraction
    enrichment_levels=[5, 4],    # Which levels get enrichments
    min_level=4                  # Process down to L4
)
```

### Enrichment Components

| Component | Fields | Library Compatibility |
|-----------|--------|----------------------|
| **Sentiment** | `textblob_polarity`, `textblob_subjectivity` | TextBlob |
| **Emotion (NRCLex)** | `nrclx_emotions`, `nrclx_top_emotion`, `nrclx_top_count` | NRCLex |
| **Emotion (GoEmotions)** | `goemotions_primary_emotion`, `goemotions_primary_score`, `goemotions_top_emotions` | GoEmotions/HF |
| **Readability** | `textstat_flesch_reading_ease`, `textstat_flesch_kincaid_grade`, `textstat_gunning_fog`, + 9 more | TextStat |
| **Keywords** | `keybert_top_keyword`, `keybert_top_score`, `keybert_top_5_keywords`, `keybert_all_keywords` | KeyBERT |
| **Topics** | `bertopic_topic_id`, `bertopic_topic_probability`, `bertopic_topic_words`, `bertopic_topic_label` | BERTopic |
| **Content** | `content_type`, `domain`, `primary_category`, `category_path`, `qa_role`, `is_claim`, `claim_type` | Custom |
| **Hate Speech** | `roberta_hate_label`, `roberta_hate_score` | RoBERTa |

### Enrichment Output Example (45 fields)

```json
{
  "entity_id": "msg:0e421c8b59169718:0000",
  "enrichment_text": "How do I configure the logging service?",
  "enrichment_batch_id": "run:01KGDR2DXDBCE15GGA4FVHAQ5J",
  "enrichment_quality_flags": ["llm_extracted"],
  "enriched_at": "2026-02-01T23:19:58.703064+00:00",
  
  "textblob_polarity": -0.5,
  "textblob_subjectivity": 0.7,
  
  "nrclx_emotions": {"joy": 0.01, "sadness": 0.2, "anger": 0.6},
  "nrclx_top_emotion": "anger",
  "nrclx_top_count": 60,
  
  "goemotions_primary_emotion": "anger",
  "goemotions_primary_score": 0.6,
  "goemotions_top_emotions": ["anger", "annoyance", "frustration"],
  
  "textstat_flesch_kincaid_grade": 8.5,
  "textstat_difficult_words": 3,
  "textstat_lexicon_count": 24,
  
  "keybert_top_keyword": "logging",
  "keybert_top_score": 1.0,
  "keybert_top_5_keywords": ["logging", "service", "structured", "JSON", "output"],
  
  "bertopic_topic_label": "Logging Configuration",
  "bertopic_topic_words": ["logging", "configuration", "JSON"],
  
  "content_type": "question",
  "domain": "programming",
  "qa_role": "question",
  "is_claim": false
}
```

---

## 8. Usage Examples

### Basic Processing (L5 only)

```python
from pipelines.llm_refinery import LLMRefineryService, RefineryConfig
import json

# Load conversations
with open("data/web_exports/claude_web/conversations.json") as f:
    conversations = json.load(f)

# Create service
config = RefineryConfig(min_level=5)  # Only messages
service = LLMRefineryService(config)

# Process single conversation
entities, enrichments = service.process(conversations[0])
print(f"Extracted {len(entities)} entities, {len(enrichments)} enrichments")

service.shutdown()
```

### Deep Processing with Enrichments

```python
config = RefineryConfig(
    min_level=2,                 # Full depth to words
    enable_enrichments=True,
    enrichment_levels=[5, 4]     # Enrich messages and sentences
)
service = LLMRefineryService(config)

entities, enrichments = service.process(conversation)
# entities: L8 + L7 topics + L6 turns + L5 messages + L4 sentences + L3 spans + L2 words
# enrichments: sentiment/emotion/keywords for each L5 and L4 entity
```

### Batch Processing

```python
# Process multiple conversations with output files
service.process_batch(
    conversations[:10],
    output_file="output/entities.jsonl",
    enrichments_file="output/enrichments.jsonl"
)
```

---

## 9. CLI Usage

### Process Single Conversation

```bash
python -m pipelines.llm_refinery.cli process \
    data/web_exports/claude_web/conversations.json \
    --index 0 \
    --output output/single.jsonl \
    --min-level 4
```

### Batch Processing with Enrichments

```bash
python -m pipelines.llm_refinery.cli process-batch \
    data/web_exports/claude_web/conversations.json \
    output/entities.jsonl \
    --enrichments-file output/enrichments.jsonl \
    --enable-enrichments \
    --enrichment-levels 5,4 \
    --limit 10
```

---

## 10. Performance Metrics

### Typical Processing Times

| Depth | Entities/Conversation | Time/Conversation |
|-------|----------------------|-------------------|
| L5 only | ~15-30 | 2-5 seconds |
| L4 (sentences) | ~50-100 | 15-30 seconds |
| L2 (full depth) | ~200-500 | 45-90 seconds |

### Resource Usage
- **Memory**: ~2GB (model-dependent)
- **GPU**: Recommended for 32B+ models
- **Disk**: ~1KB per entity output

---

## 11. Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Timeout errors | Large messages | Increase `timeout` config |
| Empty extractions | JSON parse failure | Check LLM response format |
| Missing IDs | IdentityService down | Fallback enabled automatically |
| Slow processing | Small model | Use `qwen2.5-coder:32b` or larger |

### Debug Mode
```python
import logging
logging.getLogger("pipelines.llm_refinery").setLevel(logging.DEBUG)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-02-01 | Added entity_enrichments output (45 fields) |
| 1.0.0 | 2026-02-01 | Initial release with central services integration |
