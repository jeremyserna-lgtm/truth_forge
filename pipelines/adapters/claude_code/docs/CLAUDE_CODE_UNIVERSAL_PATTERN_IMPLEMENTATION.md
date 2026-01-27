# Claude Code Pipeline: Universal Pattern Implementation

**Doc ID**: doc:pipeline:claude_code:universal_implementation
**Version**: 1.0.0
**Created**: 2026-01-18
**Status**: Implementation Plan
**Reference**: [UNIVERSAL_PIPELINE_PATTERN.md](../../../framework/standards/UNIVERSAL_PIPELINE_PATTERN.md)

---

## Executive Summary

This document defines how the Claude Code pipeline implements the Universal 16-Stage Pipeline Pattern, derived from the production ChatGPT Web Pipeline.

### Current State vs. Target State

| Aspect | Current State | Target State |
|--------|---------------|--------------|
| **Pipeline Type** | Reprocessing (from entity_unified) | Full ingestion (from raw JSONL) |
| **Stages Implemented** | 0, 1, 3, 4, 5, 6 (custom) | 0-16 (universal pattern) |
| **Entity Levels** | L5 only (messages) | L1, L3, L5, L8 (full SPINE) |
| **Enrichments** | LLM correction | Embeddings, sentiment, topics, relationships |
| **Output** | Back to entity_unified | Full enriched entity set |

---

## 1. Pipeline Identity

| Property | Value |
|----------|-------|
| **Pipeline Name** | `claude_code` |
| **Source System** | Claude Code CLI / IDE sessions |
| **Source Format** | JSONL session exports |
| **Final Destination** | `spine.entity_unified` |
| **Entity Count Target** | TBD (based on session volume) |

---

## 2. Source Data: Claude Code JSONL Format

### Export Location
```
~/.claude-code/sessions/*.jsonl
```

### Message Types

```jsonl
{"type":"summary","session_id":"abc123","cwd":"/project","model":"claude-sonnet-4","timestamp":"2026-01-18T10:30:00Z"}
{"type":"user","content":"Refactor this function","timestamp":"2026-01-18T10:30:01Z"}
{"type":"assistant","content":"I'll analyze the code...","timestamp":"2026-01-18T10:30:05Z","cost_usd":0.0045}
{"type":"tool_use","name":"Read","input":{"file_path":"/src/main.py"}}
{"type":"tool_result","content":"def main():\n    pass"}
{"type":"assistant","content":"Here's the refactored version...","timestamp":"2026-01-18T10:30:45Z"}
```

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Message type: summary, user, assistant, tool_use, tool_result |
| `session_id` | string | Unique session identifier |
| `content` | string | Message text content |
| `timestamp` | ISO8601 | Message timestamp |
| `model` | string | Model used (in summary) |
| `cwd` | string | Working directory (in summary) |
| `cost_usd` | float | API cost for assistant messages |
| `name` | string | Tool name (for tool_use) |
| `input` | object | Tool input parameters |

---

## 3. Universal Pattern Mapping

### Phase 1: Ingestion (Stages 0-4)

#### Stage 0: Assessment

**Current**: Reads from entity_unified (reprocessing mode)
**Target**: Analyze raw JSONL exports

```python
"""
Stage 0: Assessment - Claude Code Pipeline

HOLD₁ (JSONL session files) → AGENT (Format Analyzer) → HOLD₂ (Assessment Report)

Purpose: Analyze structure of Claude Code session exports before processing
"""

HOLD_1 = Path("~/.claude-code/sessions/")  # Raw JSONL files
HOLD_2 = Path("Primitive/staging/claude_code/assessment.jsonl")

def assess_claude_code_export(session_dir: Path) -> Dict:
    """Analyze session exports for processability."""
    report = {
        "total_sessions": 0,
        "total_messages": 0,
        "message_types": defaultdict(int),
        "models_used": set(),
        "date_range": {"min": None, "max": None},
        "tool_usage": defaultdict(int),
        "total_cost_usd": 0.0,
        "issues": [],
    }

    for jsonl_file in session_dir.glob("*.jsonl"):
        with open(jsonl_file) as f:
            for line in f:
                msg = json.loads(line)
                report["total_messages"] += 1
                report["message_types"][msg.get("type")] += 1

                if msg.get("type") == "summary":
                    report["total_sessions"] += 1
                    report["models_used"].add(msg.get("model"))

                if msg.get("type") == "tool_use":
                    report["tool_usage"][msg.get("name")] += 1

                if msg.get("cost_usd"):
                    report["total_cost_usd"] += msg["cost_usd"]

    return report
```

#### Stage 1: Extraction

**Current**: Extract from entity_unified by source_name filter
**Target**: Parse raw JSONL files into structured rows

```python
"""
Stage 1: Extraction - Claude Code Pipeline

HOLD₁ (JSONL files) → AGENT (Parser) → HOLD₂ (claude_code_stage_1)

Purpose: Parse JSONL exports into structured BigQuery rows
"""

HOLD_1 = Path("~/.claude-code/sessions/")
HOLD_2 = "flash-clover-464719-g1.spine.claude_code_stage_1"

def extract_messages(session_file: Path) -> List[Dict]:
    """Extract structured messages from JSONL file."""
    messages = []
    session_id = None
    message_index = 0

    with open(session_file) as f:
        for line in f:
            msg = json.loads(line)

            if msg.get("type") == "summary":
                session_id = msg.get("session_id")
                continue

            messages.append({
                "session_id": session_id,
                "message_index": message_index,
                "message_type": msg.get("type"),
                "role": "user" if msg.get("type") == "user" else "assistant",
                "content": msg.get("content", ""),
                "timestamp": msg.get("timestamp"),
                "model": msg.get("model"),
                "cost_usd": msg.get("cost_usd"),
                "tool_name": msg.get("name"),  # For tool_use
                "tool_input": json.dumps(msg.get("input")) if msg.get("input") else None,
                "source_file": str(session_file),
                "extracted_at": datetime.now(timezone.utc).isoformat(),
            })
            message_index += 1

    return messages
```

#### Stage 2: Cleaning

```python
"""
Stage 2: Cleaning - Claude Code Pipeline

HOLD₁ (claude_code_stage_1) → AGENT (Normalizer) → HOLD₂ (claude_code_stage_2)

Purpose: Normalize timestamps, deduplicate, validate content
"""

def clean_message(row: Dict) -> Dict:
    """Clean and normalize a single message."""
    # Normalize timestamp
    if row.get("timestamp"):
        ts = parse_timestamp(row["timestamp"])
        row["timestamp_utc"] = ts.astimezone(timezone.utc).isoformat()
        row["content_date"] = ts.date().isoformat()

    # Clean content
    content = row.get("content", "")
    row["content_cleaned"] = normalize_whitespace(content)
    row["content_length"] = len(content)
    row["word_count"] = len(content.split())

    # Generate fingerprint for deduplication
    row["fingerprint"] = hashlib.sha256(
        f"{row['session_id']}:{row['message_index']}:{content[:100]}".encode()
    ).hexdigest()

    return row
```

#### Stage 3: THE GATE (Identity Generation)

**Current**: Registers existing entity_ids with identity_service
**Target**: Generate NEW entity_ids for raw messages

```python
"""
Stage 3: THE GATE - Claude Code Pipeline

HOLD₁ (claude_code_stage_2) → AGENT (Identity Generator) → HOLD₂ (claude_code_stage_3)

Purpose: Generate and register stable entity_ids for all messages
This is THE GATE - the stage where identities are born.
"""

from src.services.central_services.identity_service.service import (
    generate_message_id_from_guid,
    register_id,
    sync_to_bigquery,
)

def generate_entity_id(session_id: str, message_index: int, fingerprint: str) -> str:
    """Generate deterministic entity_id for Claude Code message."""
    # Create GUID from stable components
    guid = f"claude_code:{session_id}:{message_index}:{fingerprint[:12]}"

    # Generate via identity_service
    entity_id = generate_message_id_from_guid(guid, message_index)

    # Register with central registry
    register_id(
        entity_id=entity_id,
        entity_type="claude_code_message",
        source="claude_code_stage_3",
        stable=True,
        metadata={
            "pipeline": "claude_code",
            "session_id": session_id,
            "message_index": message_index,
            "fingerprint": fingerprint,
        },
    )

    return entity_id
```

#### Stage 4: Staging

```python
"""
Stage 4: Staging - Claude Code Pipeline

HOLD₁ (claude_code_stage_3) → AGENT (SPINE Preparer) → HOLD₂ (claude_code_stage_4)

Purpose: Prepare data structure for SPINE entity creation (L1→L3→L5→L8)
"""

def prepare_for_spine(row: Dict) -> Dict:
    """Add SPINE-required fields."""
    row["source_name"] = "claude_code"
    row["source_pipeline"] = "claude_code"
    row["level"] = 5  # Message level
    row["parent_id"] = None  # Will be set when conversation entity created
    row["metadata"] = json.dumps({
        "session_id": row["session_id"],
        "message_type": row["message_type"],
        "model": row.get("model"),
        "cost_usd": row.get("cost_usd"),
        "tool_name": row.get("tool_name"),
    })
    return row
```

### Phase 2: Entity Creation (Stages 5-8)

#### Stage 5: L1 Tokens

```python
"""
Stage 5: L1 Token Creation - Claude Code Pipeline

HOLD₁ (claude_code_stage_4) → AGENT (Tokenizer) → HOLD₂ (claude_code_stage_5)

Purpose: Create Level 1 token entities from message content
"""

import spacy

nlp = spacy.load("en_core_web_sm")

def create_token_entities(message: Dict) -> List[Dict]:
    """Create L1 token entities from message."""
    tokens = []
    doc = nlp(message["content_cleaned"])

    for i, token in enumerate(doc):
        token_entity = {
            "entity_id": generate_token_id(message["entity_id"], i),
            "parent_id": message["entity_id"],
            "source_name": "claude_code",
            "level": 1,
            "text": token.text,
            "lemma": token.lemma_,
            "pos": token.pos_,
            "dep": token.dep_,
            "is_stop": token.is_stop,
            "content_date": message["content_date"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        tokens.append(token_entity)

    return tokens
```

#### Stage 6: L3 Sentences

```python
"""
Stage 6: L3 Sentence Creation - Claude Code Pipeline

HOLD₁ (claude_code_stage_5) → AGENT (Sentence Detector) → HOLD₂ (claude_code_stage_6)

Purpose: Create Level 3 sentence entities from message content
"""

def create_sentence_entities(message: Dict) -> List[Dict]:
    """Create L3 sentence entities from message."""
    sentences = []
    doc = nlp(message["content_cleaned"])

    for i, sent in enumerate(doc.sents):
        sentence_entity = {
            "entity_id": generate_sentence_id(message["entity_id"], i),
            "parent_id": message["entity_id"],
            "source_name": "claude_code",
            "level": 3,
            "text": sent.text,
            "start_char": sent.start_char,
            "end_char": sent.end_char,
            "content_date": message["content_date"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        sentences.append(sentence_entity)

    return sentences
```

#### Stage 7: L5 Messages

```python
"""
Stage 7: L5 Message Finalization - Claude Code Pipeline

HOLD₁ (claude_code_stage_6) → AGENT (Message Finalizer) → HOLD₂ (claude_code_stage_7)

Purpose: Finalize Level 5 message entities with child counts
"""

def finalize_message_entity(message: Dict, token_count: int, sentence_count: int) -> Dict:
    """Finalize L5 message entity with aggregated data."""
    message["token_count"] = token_count
    message["sentence_count"] = sentence_count
    message["level"] = 5
    message["entity_type"] = "message"
    return message
```

#### Stage 8: L8 Conversations

```python
"""
Stage 8: L8 Conversation Creation - Claude Code Pipeline

HOLD₁ (claude_code_stage_7) → AGENT (Conversation Builder) → HOLD₂ (claude_code_stage_8)

Purpose: Create Level 8 conversation entities from session messages
"""

def create_conversation_entity(session_id: str, messages: List[Dict]) -> Dict:
    """Create L8 conversation entity from session messages."""
    return {
        "entity_id": generate_conversation_id(session_id),
        "source_name": "claude_code",
        "level": 8,
        "session_id": session_id,
        "message_count": len(messages),
        "user_message_count": sum(1 for m in messages if m["role"] == "user"),
        "assistant_message_count": sum(1 for m in messages if m["role"] == "assistant"),
        "total_tokens": sum(m.get("token_count", 0) for m in messages),
        "total_cost_usd": sum(m.get("cost_usd", 0) or 0 for m in messages),
        "start_timestamp": min(m["timestamp_utc"] for m in messages),
        "end_timestamp": max(m["timestamp_utc"] for m in messages),
        "duration_seconds": calculate_duration(messages),
        "tools_used": list(set(m.get("tool_name") for m in messages if m.get("tool_name"))),
        "content_date": messages[0]["content_date"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
```

### Phase 3: Enrichment (Stages 9-13)

#### Stage 9: Embeddings

```python
"""
Stage 9: Embeddings - Claude Code Pipeline

HOLD₁ (claude_code_stage_8) → AGENT (Embedder) → HOLD₂ (claude_code_stage_9)

Purpose: Generate vector embeddings for semantic search
"""

from google.cloud import aiplatform

def generate_embeddings(texts: List[str], model: str = "gemini-embedding-001") -> List[List[float]]:
    """Generate embeddings using Vertex AI."""
    model = aiplatform.TextEmbeddingModel.from_pretrained(model)
    embeddings = model.get_embeddings(texts)
    return [e.values for e in embeddings]  # 3072-dim vectors
```

#### Stage 10: LLM Extraction

```python
"""
Stage 10: LLM Extraction - Claude Code Pipeline

HOLD₁ (claude_code_stage_9) → AGENT (Entity Extractor) → HOLD₂ (claude_code_stage_10)

Purpose: Extract named entities and concepts using LLM
"""

# Claude Code-specific extractions:
# - Code patterns mentioned
# - Libraries/frameworks discussed
# - Error types encountered
# - Refactoring patterns applied
```

#### Stage 11: Sentiment

```python
"""
Stage 11: Sentiment Analysis - Claude Code Pipeline

HOLD₁ (claude_code_stage_10) → AGENT (Sentiment Analyzer) → HOLD₂ (claude_code_stage_11)

Purpose: Analyze emotional content using GoEmotions
"""

from transformers import pipeline

sentiment_classifier = pipeline(
    "text-classification",
    model="SamLowe/roberta-base-go_emotions",
    top_k=None
)
```

#### Stage 12: Topics

```python
"""
Stage 12: Topic Extraction - Claude Code Pipeline

HOLD₁ (claude_code_stage_11) → AGENT (Topic Extractor) → HOLD₂ (claude_code_stage_12)

Purpose: Extract topics using KeyBERT
"""

from keybert import KeyBERT

kw_model = KeyBERT()

def extract_topics(text: str) -> List[Tuple[str, float]]:
    """Extract keywords/topics from text."""
    return kw_model.extract_keywords(text, top_n=5)
```

#### Stage 13: Relationships

```python
"""
Stage 13: Relationship Extraction - Claude Code Pipeline

HOLD₁ (claude_code_stage_12) → AGENT (Relationship Builder) → HOLD₂ (claude_code_stage_13)

Purpose: Build entity relationship graph
"""

# Claude Code-specific relationships:
# - session → messages (parent-child)
# - message → files_touched (references)
# - session → project (context)
# - user_message → assistant_response (turn pairs)
```

### Phase 4: Finalization (Stages 14-16)

#### Stage 14: Aggregation

```python
"""
Stage 14: Aggregation - Claude Code Pipeline

HOLD₁ (claude_code_stage_13) → AGENT (Aggregator) → HOLD₂ (claude_code_stage_14)

Purpose: Roll up metrics to session and daily levels
"""

def aggregate_session_metrics(session_id: str, entities: List[Dict]) -> Dict:
    """Aggregate metrics for a session."""
    return {
        "session_id": session_id,
        "total_messages": len([e for e in entities if e["level"] == 5]),
        "total_tokens": sum(e.get("token_count", 0) for e in entities),
        "avg_sentiment": np.mean([e.get("sentiment_score", 0) for e in entities]),
        "top_topics": aggregate_topics(entities),
        "files_touched": list(set(e.get("file_path") for e in entities if e.get("file_path"))),
        "total_cost_usd": sum(e.get("cost_usd", 0) or 0 for e in entities),
        "duration_minutes": calculate_duration_minutes(entities),
    }
```

#### Stage 15: Final Validation

```python
"""
Stage 15: Final Validation - Claude Code Pipeline

HOLD₁ (claude_code_stage_14) → AGENT (Validator) → HOLD₂ (claude_code_stage_15)

Purpose: Quality gates before promotion to entity_unified
"""

def validate_for_promotion(entity: Dict) -> Tuple[bool, List[str]]:
    """Validate entity meets promotion requirements."""
    errors = []

    # Required fields
    required = ["entity_id", "source_name", "level", "text", "content_date"]
    for field in required:
        if not entity.get(field):
            errors.append(f"Missing required field: {field}")

    # Entity ID format
    if len(entity.get("entity_id", "")) != 32:
        errors.append("entity_id must be 32 characters")

    # Level validation
    if entity.get("level") not in [1, 3, 5, 8]:
        errors.append(f"Invalid level: {entity.get('level')}")

    return len(errors) == 0, errors
```

#### Stage 16: Promotion

```python
"""
Stage 16: Promotion - Claude Code Pipeline

HOLD₁ (claude_code_stage_15) → AGENT (Promoter) → HOLD₂ (spine.entity_unified)

Purpose: Atomic write to production entity_unified table
"""

def promote_to_entity_unified(entities: List[Dict]) -> int:
    """Promote validated entities to entity_unified."""
    # Deduplicate by entity_id
    # Atomic insert with fingerprint-based idempotency
    # Return count of new entities added
    pass
```

---

## 4. Configuration

### pipeline_config.yaml

```yaml
pipeline:
  name: claude_code
  version: 2.0.0
  source_type: jsonl
  description: Claude Code session data - full 16-stage Universal Pattern implementation

  # Cost controls
  cost_limit_per_stage_usd: 5.0
  cost_limit_total_usd: 80.0

  # Execution
  parallel_workers: 4
  batch_size: 1000
  timeout_minutes: 60

# Source data
source:
  type: local_jsonl
  path: ~/.claude-code/sessions/
  pattern: "*.jsonl"

# Entity levels
spine:
  levels:
    L1: tokens
    L3: sentences
    L5: messages
    L8: conversations

# Enrichments
enrichments:
  embeddings:
    model: gemini-embedding-001
    dimensions: 3072
  sentiment:
    model: SamLowe/roberta-base-go_emotions
    classes: 28
  topics:
    model: keybert
    top_n: 5

# BigQuery
bigquery:
  project: flash-clover-464719-g1
  dataset: spine
  final_table: entity_unified
  partition_field: content_date
  clustering_fields:
    - source_name
    - level
    - content_date
```

---

## 5. Migration Path

### Current → Target

1. **Keep existing stages 0-6** for reprocessing use case
2. **Add new ingestion stages** for raw JSONL processing
3. **Extend to full 16-stage pattern** progressively

### Phase 1: Raw Ingestion (Priority)
- Implement Stage 0-4 for raw JSONL files
- Generate new entity_ids (not reuse from entity_unified)

### Phase 2: Entity Creation
- Implement Stages 5-8 for L1→L3→L5→L8 creation
- This is where token/sentence granularity is added

### Phase 3: Enrichment
- Implement Stages 9-13 for embeddings, sentiment, topics
- Claude Code-specific: tool success analysis, code patterns

### Phase 4: Finalization
- Implement Stages 14-16 for aggregation and promotion
- Merge with existing entity_unified data

---

## 6. Expected Output

### Entity Counts (Estimated)

| Level | Entity Type | Estimated Count |
|-------|-------------|-----------------|
| L8 | Conversations | ~500 sessions |
| L5 | Messages | ~50,000 messages |
| L3 | Sentences | ~200,000 sentences |
| L1 | Tokens | ~2,000,000 tokens |

### Claude Code Development Arc

Parallel to the Clara Arc from ChatGPT:

| Metric | Clara Arc | Claude Code Arc |
|--------|-----------|-----------------|
| Duration | 66 days | TBD |
| Messages | 31,021 | TBD |
| Focus | Personal development | Code development |
| Key Analysis | Cognitive stages | Productivity patterns |

---

## 7. Related Documents

- [UNIVERSAL_PIPELINE_PATTERN.md](../../../framework/standards/UNIVERSAL_PIPELINE_PATTERN.md) - Universal pattern spec
- [PIPELINE_PATTERN_SPECIFICATION.md](../../../framework/standards/PIPELINE_PATTERN_SPECIFICATION.md) - Framework alignment
- [THE_CLARA_ARC.md](../../../framework/general/THE_CLARA_ARC.md) - ChatGPT case study

---

*This implementation plan aligns the Claude Code pipeline with the Universal 16-Stage Pipeline Pattern, enabling the same depth of analysis achieved with the ChatGPT Web Pipeline (The Clara Arc).*
