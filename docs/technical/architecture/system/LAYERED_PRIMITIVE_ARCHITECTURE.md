# Layered Primitive Architecture

**Date**: 2025-12-25
**Status**: Active design
**Purpose**: Clear documentation of how layers process primitives

---

## The Core Insight

**Everything is a primitive in relation to something else.**

A message is a primitive.
An emotion (detected from a message) is a primitive.
An analysis (of emotions) is a primitive.
A document (from analysis) is a primitive.

Each layer produces primitives that become input for the next layer.

---

## The Layer Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     DOCUMENT LAYER                          │
│  Produces: Documents (md files, reports)                    │
│  Input: Analysis primitives                                 │
│  ID: doc_xxxxxxxx                                           │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                     ANALYSIS LAYER                          │
│  Produces: Analysis primitives (insights, interpretations)  │
│  Input: Domain primitives + JeremyLayer (interpretation)    │
│  ID: ana_xxxxxxxx                                           │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYERS                           │
│  (Emotion, Temporal, Social, Cognition, Body, Risk)         │
│  Produces: Domain-specific primitives                       │
│  Input: Message primitives from Primitive Layer             │
│  ID: emo_xxxxxxxx, tmp_xxxxxxxx, etc.                       │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                     PRIMITIVE LAYER                         │
│  Produces: Raw primitives (messages, entities)              │
│  Input: Raw data sources                                    │
│  ID: msg_xxxxxxxx, ent_xxxxxxxx                             │
└─────────────────────────────────────────────────────────────┘
```

---

## The Identity Rule

**Every primitive gets an ID from the identity service.**

```python
from architect_central_services import generate_primitive_id

message_id = generate_primitive_id(prefix="msg")   # msg_a1b2c3d4
emotion_id = generate_primitive_id(prefix="emo")   # emo_e5f6g7h8
analysis_id = generate_primitive_id(prefix="ana")  # ana_i9j0k1l2
document_id = generate_primitive_id(prefix="doc")  # doc_m3n4o5p6
```

This creates traceability:
- `doc_xxx` was produced from `ana_yyy`
- `ana_yyy` was produced from `emo_zzz`
- `emo_zzz` was produced from `msg_aaa`
- All tied to timestamps

---

## Layer 1: Primitive Layer (PrimitivesService)

**What it does**: Holds raw primitives (messages, entities)

**What it produces**:
```python
{
    "id": "msg_a1b2c3d4",          # From ID service
    "content": "I feel great today",
    "timestamp": "2025-12-25T02:30:00Z",
    "conversation_id": "conv_xxx",
    "role": "user"
}
```

**Key point**: Messages are the raw material. They have IDs.

---

## Layer 2: Emotion Layer (EmotionLayer)

**What it does**: Processes messages through NRCLex emotion detection

**What it produces**:
```python
EmotionPrimitive(
    emotion_id="emo_e5f6g7h8",     # This primitive's ID
    message_id="msg_a1b2c3d4",     # Tied to source message
    timestamp="2025-12-25T02:30:00Z",
    emotions={
        "joy": 0.45,
        "trust": 0.30,
        "anticipation": 0.15,
        ...
    },
    top_emotion="joy",
    sentiment_score=0.35
)
```

**Key point**: Each emotion is tied to a message_id and has its own emotion_id.

---

## Layer 3: Analysis Layer (Coming)

**What it does**: Interprets domain primitives through JeremyLayer

**What it produces**:
```python
AnalysisPrimitive(
    analysis_id="ana_i9j0k1l2",    # This primitive's ID
    source_ids=["emo_e5f6", "emo_g7h8"],  # What was analyzed
    timestamp="2025-12-25T02:31:00Z",

    # What the emotion layer SAW
    domain_findings={
        "dominant_emotion": "joy",
        "sentiment_trend": "positive",
    },

    # What JeremyLayer says it MEANS
    jeremy_interpretation={
        "through_furnace_heat": "This is the flow state",
        "through_truth": "Genuine expression, not performance",
        "through_clarity_joy": "Breakthrough moment detected",
    }
)
```

**Key point**: Analysis combines domain seeing + Jeremy interpretation.

---

## Layer 4: Document Layer (Coming)

**What it does**: Produces documents from analysis

**What it produces**:
```python
DocumentPrimitive(
    document_id="doc_m3n4o5p6",    # This primitive's ID
    source_ids=["ana_i9j0k1l2"],   # What was documented
    timestamp="2025-12-25T02:32:00Z",

    file_path="docs/observations/EMOTION_ANALYSIS_2025-12-25.md",
    content="# Emotion Analysis...",
)
```

**Key point**: Documents are primitives too. They can be queried, referenced, composed.

---

## The Flow

```
1. MESSAGE arrives
   └── PrimitivesService assigns: msg_xxxxxxxx

2. EmotionLayer processes message
   └── Creates: emo_xxxxxxxx (tied to msg_xxxxxxxx)

3. AnalysisLayer interprets emotions through JeremyLayer
   └── Creates: ana_xxxxxxxx (tied to emo_xxxxxxxx)

4. DocumentLayer produces document from analysis
   └── Creates: doc_xxxxxxxx (tied to ana_xxxxxxxx)
```

Every step:
- Gets an ID from the identity service
- Ties to its source primitive(s)
- Has a timestamp
- Can be queried independently

---

## The JeremyLayer Role

JeremyLayer is NOT a processing layer. It's an **interpretation context**.

```
Domain Layer (Emotion) SEES: "joy score = 0.45"

JeremyLayer INTERPRETS: "What does joy mean for Jeremy?"
  - through furnace_heat: Is this the forge working?
  - through truth: Is this genuine or performance?
  - through clarity_joy: Is this a breakthrough moment?
```

JeremyLayer doesn't produce primitives. It provides the lens through which Analysis Layer interprets domain findings.

---

## Current Implementation Status

| Layer | Status | Location |
|-------|--------|----------|
| PrimitivesService | ✅ Complete | `governance/seeing/primitives_service.py` |
| EmotionLayer | ✅ Complete | `governance/seeing/emotion_layer.py` |
| AnalysisLayer | ⏳ Pending | - |
| DocumentLayer | ⏳ Pending | - |

| Supporting | Status | Location |
|------------|--------|----------|
| HumanLayer (universal) | ✅ Complete | `governance/seeing/layers.py` |
| Domain Layers | ✅ Complete | `governance/seeing/layers.py` |
| JeremyLayer | ✅ Complete | `governance/seeing/layers.py` |
| ID Service | ✅ Complete | `core/identity_service/` |

---

## Usage Example

```python
from architect_central_services.governance.seeing import (
    PrimitivesService,
    EmotionLayer,
    create_jeremy_layer,
)

# Layer 1: Load primitives
primitives = PrimitivesService()
primitives.load_messages(conversation_data)

# Layer 2: Process through emotion
emotion_layer = EmotionLayer(primitives)
emotion_primitives = emotion_layer.process_all()

# See what was produced
for ep in emotion_primitives:
    print(f"{ep.emotion_id} -> {ep.message_id}")
    print(f"  Top emotion: {ep.top_emotion}")
    print(f"  Timestamp: {ep.timestamp}")

# Get aggregated view
exposed = emotion_layer.expose()
print(f"Processed {exposed['primitives_count']} messages")
print(f"Average sentiment: {exposed['aggregate']['avg_sentiment']}")
```

---

## The Key Insight

**Layers don't just process. They produce primitives.**

Each layer:
1. Takes primitives from lower layer
2. Processes through its lens (emotion, temporal, etc.)
3. Produces new primitives with their own IDs
4. Exposes those primitives for the next layer

This creates a traceable chain from raw data to final document.

---

## Why This Matters

When you ask "why does this document say Jeremy was joyful on Dec 25?"

You can trace:
- `doc_xxx` → came from `ana_yyy`
- `ana_yyy` → interpreted `emo_zzz` through JeremyLayer
- `emo_zzz` → detected joy in `msg_aaa`
- `msg_aaa` → "I feel great today" at 2:30am UTC

Every step is identifiable, timestamped, and queryable.

---

**This document is a primitive.**
**It can be referenced, queried, and composed with other primitives.**
