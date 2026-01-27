# Pipeline Stages

**The 16-stage pipeline architecture and THE GATE.**

**Status**: ACTIVE
**Owner**: Framework
**Parent**: [INDEX.md](INDEX.md)

---

## The 16-Stage Pipeline

### Stage Overview

| Stage | Name | Purpose | HOLD₂ Output |
|-------|------|---------|--------------|
| **0** | Assessment | Analyze source format | Assessment report |
| **1** | Extraction | Parse raw exports | `stage_1` (raw) |
| **2** | Cleaning | Normalize, deduplicate | `stage_2` (cleaned) |
| **3** | Validation (THE GATE) | Generate entity_ids | `stage_3` (validated) |
| **4** | Staging | Prepare for entities | `stage_4` (staged) |
| **5** | L1 Tokens | Level 1 token entities | `stage_5` (L1) |
| **6** | L3 Sentences | Level 3 sentence entities | `stage_6` (L3) |
| **7** | L5 Messages | Level 5 message entities | `stage_7` (L5) |
| **8** | L8 Conversations | Level 8 conversation entities | `stage_8` (L8) |
| **9** | Embeddings | Vector representations | `stage_9` (embedded) |
| **10** | LLM Extraction | Entity/concept extraction | `stage_10` (extracted) |
| **11** | Sentiment | Emotional analysis | `stage_11` (sentiment) |
| **12** | Topics | Topic modeling | `stage_12` (topics) |
| **13** | Relationships | Entity linking, graphs | `stage_13` (linked) |
| **14** | Aggregation | Metrics rollup | `stage_14` (aggregated) |
| **15** | Final Validation | Quality gates | `stage_15` (validated) |
| **16** | Promotion | Write to production | `spine.entity_unified` |

---

## The Four Phases

### Phase 1: Ingestion (Stages 0-4)

```
Raw Export → Assessment → Extraction → Cleaning → Validation → Staging
```

- **Stage 0**: Understand what you have (format discovery)
- **Stage 1**: Extract structured data from raw format
- **Stage 2**: Normalize and deduplicate
- **Stage 3**: THE GATE - generate entity_ids via identity_service
- **Stage 4**: Prepare data structure for SPINE entity creation

### Phase 2: Entity Creation (Stages 5-8)

```
Staged Data → L1 Tokens → L3 Sentences → L5 Messages → L8 Conversations
```

| Level | Entity Type | Grain | Example Count |
|-------|-------------|-------|---------------|
| L1 | Token | Word/subword | 39.8M |
| L3 | Sentence | Sentence | 1.2M |
| L5 | Message | User/assistant turn | 31K |
| L8 | Conversation | Full dialogue | 351 |

### Phase 3: Enrichment (Stages 9-13)

```
Entities → Embeddings → LLM Extract → Sentiment → Topics → Relationships
```

- **Stage 9**: 3072-dim embeddings (gemini-embedding-001)
- **Stage 10**: Named entity extraction via LLM
- **Stage 11**: GoEmotions 28-class sentiment analysis
- **Stage 12**: KeyBERT topic extraction
- **Stage 13**: Entity-to-entity relationship graph

### Phase 4: Finalization (Stages 14-16)

```
Enriched Entities → Aggregation → Validation → Promotion
```

- **Stage 14**: Roll up metrics to conversation/session level
- **Stage 15**: Final quality gates (completeness, consistency)
- **Stage 16**: Atomic write to `spine.entity_unified`

---

## THE GATE: Stage 3 Identity Generation

Stage 3 is THE GATE - where system identities are created and registered.

### Required Implementation

```python
from src.services.central_services.identity_service.service import (
    generate_message_id_from_guid,
    register_id,
    sync_to_bigquery,
)

def generate_entity_id(session_id: str, message_index: int, content: str) -> str:
    """Generate deterministic entity_id."""
    import hashlib

    # Create stable fingerprint
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
    guid = f"{session_id}:{message_index}:{content_hash}"

    # Generate via identity_service
    entity_id = generate_message_id_from_guid(guid, message_index)

    # Register
    register_id(
        entity_id=entity_id,
        entity_type="pipeline_message",
        source="stage_3",
        stable=True,
        metadata={
            "pipeline": "pipeline_name",
            "session_id": session_id,
            "message_index": message_index,
        },
    )

    return entity_id
```

### THE GATE Validation

```python
def validate_gate_requirements(data: List[Dict]) -> bool:
    """All records must pass THE GATE validation."""
    for record in data:
        assert record.get("entity_id"), "entity_id required"
        assert record.get("source_name"), "source_name required"
        assert record.get("content_hash"), "content_hash required"
        assert len(record["entity_id"]) == 32, "entity_id must be 32 chars"
    return True
```

---

## Convergence

### Bottom-Up Validation

This document requires:
- [INDEX.md](INDEX.md) - Parent standard
- [CORE_PATTERN.md](CORE_PATTERN.md) - HOLD:AGENT:HOLD foundation

### Top-Down Validation

This document is shaped by:
- [04_ARCHITECTURE](../../04_ARCHITECTURE.md) - HOLD:AGENT:HOLD
- [00_GENESIS](../../00_GENESIS.md) - THE GATE identity

---

*16 stages. 4 phases. One GATE.*
