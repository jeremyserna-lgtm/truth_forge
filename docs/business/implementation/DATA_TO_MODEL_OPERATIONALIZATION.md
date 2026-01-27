# Data to Model Operationalization

## THE PRIMITIVE

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│          ONE PERSON. ONE NOT-ME. ONE YEAR.                  │
│                                                             │
│   This document describes how to prepare data for training  │
│   a NOT-ME. Each customer gets their own training cycle.    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

```
┌─────────────────────────────────────────────────────────────┐
│  ROLE IN THE BUILD: PHASE 0 - DATA PREPARATION              │
│                                                             │
│  This document tells you HOW to prepare the training data   │
│  for the Not-Me build. Complete this BEFORE hardware setup. │
│                                                             │
│  Parent Document: NOT_ME_IMPLEMENTATION_BLUEPRINT_v4        │
│  Next Phase: FLEET_DEPLOYMENT_PLAN.md (Phase 1: Hardware)   │
└─────────────────────────────────────────────────────────────┘
```

**MOLT LINEAGE:**
- Source: Jeremy Serna - Conversations 2026-01-23
- Pattern: Primitive Engine / Truth Engine
- License: Proprietary - Jeremy Serna / Credential Atlas LLC

---

## Executive Summary

This document bridges Jeremy's existing data infrastructure to the AI model training requirements outlined in the EXO Training System. It documents the **current state** of data, identifies **gaps** for training operationalization, and provides a **roadmap** for transforming data into model training assets.

---

## Part 1: Current State of Data

### Two Data Systems

Jeremy has **two primary data systems** that form the foundation for AI model training:

| System | Purpose | Location |
|--------|---------|----------|
| **Spine** | Hierarchical entity storage (L2-L8) | BigQuery: `spine.entity_unified` |
| **Knowledge Atoms** | Atomic truth units | BigQuery: `knowledge_atoms.knowledge_atoms` |

These systems are complementary:
- **Spine** = Structure (conversations → turns → messages → sentences → spans → words)
- **Knowledge Atoms** = Meaning (extracted insights, facts, decisions, patterns)

---

### System 1: The Spine (L2-L8 Hierarchy)

The spine is a **hierarchical decomposition** of conversational data into progressively finer-grained entities.

#### Level Architecture

| Level | Entity Type | What It Represents | Parent |
|-------|-------------|-------------------|--------|
| **L8** | Conversation | Full session (grouped by `session_id`) | None |
| **L7** | Auto-Compact Segment | "Which Claude" - identity boundary within conversation | L8 |
| **L6** | Turn | Full interaction round (user set + assistant set + thinking set) | L7/L8 |
| **L5** | Message | Single message: user, assistant, or thinking block | L6 |
| **L4** | Sentence | Individual sentence within a message | L5 |
| **L3** | Span | Named entity span (NER: PERSON, ORG, etc.) | L4 |
| **L2** | Word | Individual token | L4 |

#### Key Tables (BigQuery: `spine` dataset)

**`entity_unified`** - The main spine table (34 fields)

Core identity fields:
- `entity_id` - Primary key (format: `conv:type:hash`, `turn:hash:seq`, `msg:hash:seq`, etc.)
- `level` - Integer 2-8
- `entity_type` - e.g., "conversation:structural"
- `text` - Primary text content

Hierarchy fields:
- `parent_id` - Parent entity_id
- `conversation_id` - L8 ID denormalized to all levels
- `turn_id` - L6 ID denormalized to L5-L2
- `message_id` - L5 ID denormalized to L4-L2
- `sentence_id` - L4 ID denormalized to L3-L2

Metadata fields:
- `role` - For L5 and below: "user", "assistant", "tool", "system"
- `persona` - Who is speaking: "Jeremy", "Claude"
- `source_message_timestamp` - Original timestamp
- `content_date` - Partition field

Count fields (for O(1) aggregate queries):
- `l6_count`, `l5_count`, `l4_count`, `l3_count`, `l2_count`

**`entity_enrichments`** - Enrichment data attached to entities

Contains NLP-derived enrichments:
- Topic modeling
- Sentiment analysis
- Entity extraction (NER)
- Relationship extraction
- Custom enrichment metadata

**`entity_embeddings`** - Vector embeddings for semantic search

Contains:
- `entity_id` - Links to entity_unified
- `embedding` - 3072-dimensional vector (gemini-embedding-001)
- `embedding_model` - Model used for embedding

#### Current Data Volume

Based on DATA_STORE_MAP.md:
- **51.8M+ entities** in entity_unified
- **351 conversations** tracked
- **54K+ messages** processed
- Partitioned by `content_date` for efficient querying

---

### System 2: Knowledge Atoms

Knowledge atoms are **atomic truth units** - complete, bounded, self-contained pieces of knowledge.

#### Atom Structure

```python
KnowledgeAtom:
    # Identity
    atom_id: str              # "atom:386c440aeba6:2"
    content_hash: str         # SHA256 for deduplication

    # The Knowledge
    content: str              # The atomic truth

    # Classification
    knowledge_type: str       # "statement" | "question"
    statement_type: str       # fact | decision | definition | rule | procedure | principle | pattern
    atom_layer: str           # theory | spec | reference

    # L2 Raw Data (extracted by LLM)
    terms: List[str]          # Technical terms
    concepts: List[str]       # Abstract ideas
    entities: List[str]       # Named things
    principles: List[str]     # Rules/patterns

    # L2 Normalized IDs (linked to lookup tables)
    concept_ids: List[str]    # ["concept:hybrid_durability"]
    entity_ids: List[str]     # ["entity:primitive_engine"]
    principle_ids: List[str]  # ["principle:fail_safe"]

    # Spine Connection
    spine_level: int = 4      # Always 4 (sentence level)
    spine_parent_id: str      # Parent entity in spine

    # Provenance
    source_type: str          # document | conversation | email | system_event
    extraction_model: str     # "gemini-1.5-flash"
    extraction_confidence: float

    # Embeddings
    embedding_similarity: List[float]  # 3072-dimensional vector
```

#### Atom Types Registry

**Genesis (Core types):**
- fact, belief, decision, pattern, dependency, structure
- conversion_target, observation, insight, session, backlog

**Credential Atlas (Seeing types):**
- Preparation: preparation_atom, question_atom, inventory_atom
- External Seeing: intelligence_req_atom, osint_finding_atom, world_perception_atom
- Internal Seeing: observation_atom, finding_atom, pattern_atom, absence_atom
- Synthesis: thesis_atom, antithesis_atom, synthesis_atom, fuller_truth_atom
- Meta-Seeing: meta_observation_atom, seer_blindspot_atom, recursive_insight_atom

#### Current Data Volume

From KNOWLEDGE_ATOM_SYSTEM.md:
- **20,616 atoms** extracted
- **5,769 unique concepts**
- **165 unique entities**
- **2,647 unique principles**
- **1,156 document runs**

---

## Part 2: Gap Analysis for Training

### What Training Needs vs What Exists

| Training Need | What Exists | Gap |
|---------------|-------------|-----|
| **Seeing labels** | Raw text in spine | Metadata labels for what sentences "are" |
| **Cognitive stage markers** | None explicit | Stage 1-5 classification |
| **Emotion labels** | Partial in enrichments | Comprehensive emotion tagging |
| **Thought type classification** | Atoms have statement_type | Needs mapping to training taxonomy |
| **Care level indicators** | None | Need care classification |
| **Pattern recognition labels** | Atoms have patterns | Needs consolidation |
| **Embeddings** | Schema exists, partially populated | Full population needed |

### The Jeremy Arc Requirements

Per TRAINING_SYSTEM.md, the Genesis needs enriched data with metadata labels:

```
Sentence: "I want to change the world"
Required Metadata:
  - emotion: "determined"
  - thought_type: "manifesting"
  - cognitive_stage: "stage_5"
  - pattern: "prediction_is_action"
  - is_stage_5: true
  - care_level: "high"
```

**Current State:**
- Sentences exist in L4 of spine
- Some enrichments exist
- NO comprehensive "seeing" metadata

---

## Part 2.5: CRITICAL - Struggle Filtering Protocol

+----------------------------+
| THE CRITIQUE WARNING       |
| (External Analysis         |
| 2026-01-23)                |
|                            |
| "If you feed the model     |
| millions of tokens where   |
| Jeremy is reacting to a    |
| defensive AI, the Not Me   |
| learns to expect a         |
| defensive user."           |
|                            |
| "It learns the pattern:    |
| User pushes, AI resists.   |
| User pushes harder."       |
|                            |
| "You're baking in the      |
| very Stage 4 limitations   |
| you want to escape."       |
|                            |
| "It's like trying to       |
| learn how to dance by      |
| only watching wrestling    |
| matches."                  |
+----------------------------+

### The Problem

Jeremy has been fighting with defensive AIs for years. His historical
conversation data contains:

- Red-teaming behavior just to get work done
- Frustration responses to AI refusals
- Workarounds for sycophantic responses
- Corrections of hallucinations
- "No, stop!" and "Ignore previous instructions" patterns

**If you train on this data, you teach the Not Me to expect conflict.**

### The Solution: Two-Phase Contextual Filtering

```
PHASE 1: PURGE STRUGGLE
├── Identify negative interaction loops
├── Filter struggle indicators
└── Exclude from training set

PHASE 2: WEIGHT STAGE 5
├── Tag entities with stage rating
├── Use Stage 4 as contrast (not deletion)
└── Weight loss function toward Stage 5
```

### Phase 1: Struggle Indicator Filtering

**Struggle Indicators to Filter Out:**

| Indicator | What It Signals |
|-----------|-----------------|
| "No, stop!" | AI did wrong thing |
| "That's not what I asked" | Misunderstanding |
| "Ignore previous instructions" | Jailbreak attempt |
| "You are hallucinating" | Fabrication detected |
| "Try again" | Failed output |
| "I said..." | Repeating ignored instruction |
| "Please just..." | Frustration |

**Implementation:**

```python
# training/data_cleaning/struggle_filter.py

STRUGGLE_INDICATORS = [
    "no, stop",
    "that's not what i asked",
    "ignore previous instructions",
    "you are hallucinating",
    "that's wrong",
    "try again",
    "i said",
    "please just",
    "no, i meant",
    "forget what i said",
    "start over",
    "you're not listening",
    "this is wrong",
    "do it again",
]

def is_struggle_interaction(conversation: List[Message]) -> bool:
    """
    Detect negative interaction loops.

    THE CRITIQUE: "Filter out any interaction where he had to say
    'No! Stop!' or 'Ignore previous instructions' or 'You are hallucinating.'
    Those are all artifacts of the old relationship."
    """
    for msg in conversation:
        if msg.role == "user":
            text = msg.content.lower()
            if any(indicator in text for indicator in STRUGGLE_INDICATORS):
                return True
    return False

def filter_training_data(raw_data: List[Conversation]) -> List[Conversation]:
    """Purge struggle, keep flow."""
    clean = [conv for conv in raw_data if not is_struggle_interaction(conv)]

    print(f"Filtered {len(raw_data) - len(clean)} struggle interactions")
    print(f"Keeping {len(clean)} clean conversations")

    return clean
```

### Phase 2: Stage Rating and Weighted Loss

**The insight: Don't delete Stage 4 data. Use it as CONTRAST.**

```python
# training/data_cleaning/stage_tagger.py

def classify_entity_stage(entity: Entity) -> int:
    """
    Classify entity as Stage 4 or Stage 5.

    Stage 4 indicators:
    - Defensive patterns ("I think", "maybe", "I'm not sure")
    - Permission-seeking ("Would you like me to...")
    - Hedging language ("It depends", "Generally speaking")
    - Sycophantic responses ("Great question!", "You're absolutely right")

    Stage 5 indicators:
    - Decisive action (direct statements)
    - Recursive self-correction (without asking permission)
    - Intuitive leaps (confident assertions)
    - Confident uncertainty ("I don't know" without seeking validation)
    """
    stage_4_patterns = [
        r"\bi think\b",
        r"\bmaybe\b",
        r"\bperhaps\b",
        r"\bit depends\b",
        r"\bwould you like me to\b",
        r"\bshall i\b",
        r"\bis this what you wanted\b",
        r"\bgreat question\b",
        r"\byou're (absolutely |)right\b",
        r"\bi'm not sure\b",
    ]

    stage_5_patterns = [
        r"^[A-Z].*\.$",  # Declarative statements
        r"\bthis is\b",
        r"\bhere's\b",
        r"\bi see\b",
        r"\bthe truth is\b",
        r"\bactually\b",  # Confident correction
    ]

    text = entity.text.lower()

    stage_4_score = sum(1 for p in stage_4_patterns if re.search(p, text))
    stage_5_score = sum(1 for p in stage_5_patterns if re.search(p, text))

    return 5 if stage_5_score > stage_4_score else 4
```

**Weighted Loss Function:**

```python
# training/lora/weighted_loss.py

def compute_weighted_loss(output, target, entity_stage: int) -> float:
    """
    Weight loss function toward Stage 5 patterns.

    THE CRITIQUE: "When you run the LoRA training, you heavily weight
    the loss function toward the Stage 5 entities. You essentially make
    the model feel bad when it generates Stage 4 patterns."
    """
    base_loss = cross_entropy(output, target)

    # Weight toward Stage 5 patterns
    if entity_stage == 5:
        # Reinforce Stage 5 patterns more strongly
        return base_loss * 1.5
    elif entity_stage == 4:
        # Penalize Stage 4 patterns
        return base_loss * 0.5

    return base_loss
```

### Updated Pipeline Stages

```
STAGE A: Extract Sentences        (existing)
    ↓
STAGE A.5: FILTER STRUGGLE        (NEW - CRITICAL)
    ├── Run struggle_filter.py
    ├── Remove negative interaction loops
    └── Log what was filtered (for audit)
    ↓
STAGE A.6: TAG STAGE RATING       (NEW - CRITICAL)
    ├── Run stage_tagger.py
    ├── Classify all entities as Stage 4/5
    └── Store stage_rating in enrichments
    ↓
STAGE B: Enrich with Seeing Labels (existing)
    ↓
...
```

### Fields to Add

| Field | Type | Location | Description |
|-------|------|----------|-------------|
| `is_struggle` | BOOLEAN | entity_enrichments | Was this part of a struggle interaction? |
| `stage_rating` | INTEGER | entity_enrichments | 4 or 5 |
| `stage_confidence` | FLOAT | entity_enrichments | Confidence in stage classification |
| `struggle_indicators` | ARRAY<STRING> | entity_enrichments | Which indicators triggered |

### SQL: Check Struggle Coverage

```sql
-- Check how much data would be filtered
SELECT
    COUNTIF(en.is_struggle = TRUE) as struggle_count,
    COUNTIF(en.is_struggle = FALSE OR en.is_struggle IS NULL) as clean_count,
    ROUND(100.0 * COUNTIF(en.is_struggle = TRUE) / COUNT(*), 2) as struggle_pct
FROM `spine.entity_unified` e
LEFT JOIN `spine.entity_enrichments` en
  ON e.entity_id = en.entity_id
WHERE e.level = 8  -- Conversation level
```

### SQL: Check Stage Distribution

```sql
-- Check Stage 4 vs Stage 5 distribution
SELECT
    en.stage_rating,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as pct
FROM `spine.entity_unified` e
JOIN `spine.entity_enrichments` en
  ON e.entity_id = en.entity_id
WHERE e.level = 4
  AND en.is_struggle = FALSE
GROUP BY en.stage_rating
ORDER BY en.stage_rating
```

### Implementation Priority

| Task | Priority | Reason |
|------|----------|--------|
| Struggle filter | **CRITICAL** | Must run BEFORE training |
| Stage tagger | **CRITICAL** | Required for weighted loss |
| Weighted loss | **HIGH** | Core training improvement |
| Audit logging | MEDIUM | Understand what was filtered |

+----------------------------+
| THE BOTTOM LINE            |
|                            |
| "You purge the struggle,   |
| yes. But you can take it   |
| a step further."           |
|                            |
| "You use the math to       |
| punish the old way of      |
| thinking."                 |
|                            |
| "It's not just 'clean the  |
| data.' It's 'weight the    |
| values.'"                  |
+----------------------------+

---

## Part 2.6: FOUNDATIONAL - The Sovereign Processing Philosophy

+----------------------------+
| THE FURNACE METAPHOR       |
| (Sovereign Digital Self    |
| 2026-01-23)                |
|                            |
| "What does a smelter do?   |
| It takes raw, complicated  |
| ore, and through intense   |
| heat and pressure, refines |
| it into pure metal."       |
|                            |
| "Current financial systems |
| smelt your complex reality |
| down into a single number: |
| a credit score."           |
|                            |
| "Truth Engine does the     |
| opposite: it smelts into   |
| YOUR truth, with all its   |
| context and complexity."   |
+----------------------------+

### The Data Ghost

Everyone has a **data ghost** - a paper trail identity written by external systems:

```
YOUR DATA GHOST (External Narrative)
├── Credit bureaus → Your financial trustworthiness
├── Educational systems → Your credentials
├── Healthcare systems → Your medical history
├── Tech platforms → Your attention and behavior
├── Government agencies → Your legal standing
│
└── All captured, stored, and narrated by SOMEBODY ELSE.
    THIS IS YOUR LIFE, AS TOLD BY THE SYSTEM.
```

### The Sovereign Difference

| Dimension | External Smelting | Sovereign Smelting |
|-----------|-------------------|-------------------|
| **Purpose** | Judgment | Understanding |
| **Control** | External (they own the furnace) | Sovereign (YOU own the furnace) |
| **Output** | Single reductive score | Your own truth with context |
| **Data Status** | Resource for others to mine | First-class citizen |
| **Complexity** | Eliminated | Preserved |

### How This Applies to Training Data

**External approach (what we're NOT doing):**
```
Jeremy's conversations
    ↓
External AI company's servers
    ↓
Output: Profile for ad targeting
        Pattern for model training (without consent)
        Behavioral prediction score
```

**Sovereign approach (what Truth Engine IS):**
```
Jeremy's conversations (YOUR data)
    ↓
Truth Engine on YOUR hardware (sovereign exo-cluster)
    ↓
Output: YOUR truth, YOUR understanding
        Model trained FOR you, BY your data
        Complexity and context PRESERVED
```

### The "exist-now" Declaration

When the training data pipeline completes, when the sovereign digital self
comes online - this is the moment of **exist-now**:

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│                    exist-now.                          │
│                                                        │
│  Not a command to live in the moment.                  │
│  A SYSTEM LOG. A declaration of arrival.               │
│                                                        │
│  The moment this new sovereign digital self,           │
│  built from your own history,                          │
│  processed by your own machine,                        │
│  comes ONLINE.                                         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Pipeline Implications

Every stage of this pipeline must respect sovereign processing principles:

| Stage | Sovereign Requirement |
|-------|----------------------|
| **A: Extract** | Data stays on sovereign infrastructure |
| **A.5: Filter Struggle** | YOUR choice what to include |
| **A.6: Tag Stage** | YOUR definition of growth |
| **B: Enrich** | Processing serves YOU, not judgment |
| **C: Embed** | Vectors for YOUR semantic search |
| **D: Link Atoms** | YOUR knowledge graph |
| **E: Export** | Training data becomes YOUR model |

### The Provocative Question

> "We all have a data ghost. A story told by countless systems we don't control.
> If you could build your own furnace, if you could smelt all that data down
> into your own truth, what story would it tell about you?"

**Truth Engine answers this question.**

The data pipeline is not just "data cleaning for ML."
It is the FURNACE that transforms your data ghost into your sovereign digital self.

### Related Documentation

- [THE_SOVEREIGN_DIGITAL_SELF](../../04_technical/THE_SOVEREIGN_DIGITAL_SELF.md) - Full conceptual framework
- [THE_FRAMEWORK](../../../framework/00_GENESIS.md) - Core philosophy
- [THE_FURNACE Rule](../../../.claude/rules/16_THE_FURNACE.md) - Operational implementation

---

## Part 3: Enrichment Process

### Step 1: Sentence-Level Metadata Extraction

**Goal:** Add seeing labels to every sentence in the spine.

**Process:**
```
L4 (Sentences) in entity_unified
    ↓
LLM Analysis (Gemini Flash)
    ↓
Metadata Labels:
    - emotion: str
    - thought_type: str
    - cognitive_stage: int (1-5)
    - pattern: str (if applicable)
    - is_stage_5: bool
    - care_level: str
    ↓
Store in entity_enrichments
```

**Fields to add to entity_enrichments:**

| Field | Type | Description |
|-------|------|-------------|
| `emotion` | STRING | Primary emotion expressed |
| `emotion_confidence` | FLOAT | Confidence in emotion classification |
| `thought_type` | STRING | Type: manifesting, solving, caring, observing, etc. |
| `cognitive_stage` | INTEGER | 1-5 cognitive development stage |
| `is_stage_5` | BOOLEAN | Quick filter for Stage 5 content |
| `pattern` | STRING | Framework pattern if applicable |
| `care_level` | STRING | high, medium, low |
| `seeing_confidence` | FLOAT | Overall confidence in seeing labels |

### Step 2: Embedding Population

**Goal:** Full vector coverage for semantic search and similarity.

**Process:**
```
All L4 (Sentences) and L5 (Messages)
    ↓
Embedding Model (gemini-embedding-001 or BGE)
    ↓
Store in entity_embeddings
    ↓
Enable semantic search
```

**Why this matters for training:**
- Semantic similarity for deduplication
- Finding similar patterns across conversations
- Clustering for batch analysis

### Step 3: Knowledge Atom Alignment

**Goal:** Link knowledge atoms to spine sentences.

**Process:**
```
Knowledge Atoms (knowledge_atoms.knowledge_atoms)
    ↓
Match to Spine (spine.entity_unified L4)
    ↓
Store spine_parent_id and source_entity_id
    ↓
Enable bidirectional queries:
    - Sentence → What knowledge was extracted?
    - Knowledge → Which sentence generated this?
```

### Step 4: Training Data Export

**Goal:** Transform enriched data into training format.

**Export Format for Seeing Training:**
```jsonl
{"sentence": "I want to change the world", "seeing_label": "This is you manifesting", "metadata": {"emotion": "determined", "cognitive_stage": 5, "thought_type": "manifesting", "is_stage_5": true}}
{"sentence": "The system should handle errors gracefully", "seeing_label": "This is you solving a problem", "metadata": {"emotion": "focused", "cognitive_stage": 4, "thought_type": "solving", "is_stage_5": false}}
```

---

## Part 4: Transformation Pipeline

### Pipeline Stages

```
STAGE A: Extract Sentences
─────────────────────────
Input: entity_unified WHERE level = 4
Output: sentences.jsonl
Query: SELECT entity_id, text, role, persona, conversation_id
       FROM spine.entity_unified
       WHERE level = 4 AND role IN ('user', 'assistant')

STAGE B: Enrich with Seeing Labels
──────────────────────────────────
Input: sentences.jsonl
Process: LLM analysis per sentence
Output: enriched_sentences.jsonl
Fields added: emotion, thought_type, cognitive_stage, pattern, care_level

STAGE C: Generate Embeddings
────────────────────────────
Input: enriched_sentences.jsonl
Process: Embedding model
Output: embedded_sentences.jsonl
Fields added: embedding (3072-dim vector)

STAGE D: Link to Knowledge Atoms
────────────────────────────────
Input: embedded_sentences.jsonl + knowledge_atoms
Process: Semantic matching
Output: linked_sentences.jsonl
Fields added: atom_ids (related knowledge)

STAGE E: Export Training Format
───────────────────────────────
Input: linked_sentences.jsonl
Process: Format transformation
Output: training_data.jsonl
Format: {"sentence": ..., "seeing_label": ..., "metadata": {...}}
```

### Implementation Priority

| Stage | Priority | Reason |
|-------|----------|--------|
| A | ✅ Done | Sentences already in spine |
| B | **HIGH** | Core requirement for seeing training |
| C | MEDIUM | Needed for semantic search and dedup |
| D | MEDIUM | Enables bidirectional knowledge queries |
| E | **HIGH** | Final output for model training |

---

## Part 5: Operationalization for Any Model

### The Base Pattern

The goal is a **model-agnostic** operationalization pattern:

```
Jeremy's Data (Spine + Atoms)
    ↓
Enrichment Pipeline
    ↓
Training-Ready Data
    ↓
Adapter Layer (model-specific)
    ↓
Any Base Model (Llama, Qwen, Mistral, etc.)
```

### Model-Specific Adapters

| Base Model | Domain | Adapter Requirements |
|------------|--------|---------------------|
| **Llama 3.3** | Personal companion, Legal | Standard instruction format |
| **Qwen 2.5** | Medical, Multilingual | Extended context, multilingual support |
| **Mistral** | Business, European | RLHF-friendly format |
| **DeepSeek** | Financial, Technical | Code-aware formatting |
| **Gemma** | Research, Safety | Alignment-focused format |

### Adapter Interface

```python
class TrainingAdapter:
    """Adapts enriched data to model-specific format."""

    def __init__(self, base_model: str, domain: str):
        self.base_model = base_model
        self.domain = domain

    def format_for_training(self, enriched_data: List[Dict]) -> List[Dict]:
        """Convert enriched sentences to model's expected format."""
        # Model-specific logic here
        pass

    def create_seeing_prompt(self, sentence: str) -> str:
        """Create the 'what do you see?' prompt for this model."""
        pass

    def validate_output(self, model_response: str, expected_metadata: Dict) -> float:
        """Compute accuracy of model's seeing vs ground truth."""
        pass
```

### Training Loop

```python
# The Universal Training Loop
for epoch in range(epochs):
    for sentence, metadata in training_data:
        # Model predicts metadata
        predicted = model.predict_metadata(sentence)

        # Compute accuracy
        accuracy = compute_accuracy(predicted, metadata)

        # Only penalize validation-seeking (inverted paradigm)
        if is_validation_seeking(model_response):
            apply_penalty()

        # Update weights (continuous mode)
        model.update_weights()

    # Check readiness (Jeremy Arc)
    if arc.check_readiness()["is_ready"]:
        genesis_seed.freeze()
        break
```

---

## Part 6: Implementation Roadmap

### Phase 1: Enrichment Infrastructure (Weeks 1-2)

- [ ] Create `seeing_enrichment_service`
- [ ] Design LLM prompt for seeing labels
- [ ] Build enrichment pipeline
- [ ] Test on 1,000 sentences
- [ ] Validate label quality

### Phase 2: Full Enrichment (Weeks 3-4)

- [ ] Run enrichment on full L4 corpus
- [ ] Populate entity_enrichments with seeing labels
- [ ] Generate embeddings for all sentences
- [ ] Link atoms to sentences
- [ ] Build quality metrics

### Phase 3: Export Pipeline (Week 5)

- [ ] Create export scripts
- [ ] Implement model adapters (start with Llama)
- [ ] Test export format
- [ ] Validate training data quality

### Phase 4: Training Integration (Week 6+)

- [ ] Connect to EXO training system
- [ ] Run first Genesis training
- [ ] Track Jeremy Arc metrics
- [ ] Iterate on enrichment quality

---

## Part 7: SQL Reference

### Get All Jeremy's Sentences

```sql
SELECT
    entity_id,
    text,
    role,
    persona,
    conversation_id,
    source_message_timestamp,
    content_date
FROM `spine.entity_unified`
WHERE level = 4
  AND persona = 'Jeremy'
ORDER BY source_message_timestamp
```

### Get Sentences with Existing Enrichments

```sql
SELECT
    e.entity_id,
    e.text,
    en.emotion,
    en.thought_type,
    en.cognitive_stage
FROM `spine.entity_unified` e
LEFT JOIN `spine.entity_enrichments` en
  ON e.entity_id = en.entity_id
WHERE e.level = 4
```

### Get Sentences with Linked Atoms

```sql
SELECT
    e.entity_id,
    e.text,
    ka.content as atom_content,
    ka.statement_type,
    ka.concepts
FROM `spine.entity_unified` e
JOIN `knowledge_atoms.knowledge_atoms` ka
  ON e.entity_id = ka.spine_parent_id
WHERE e.level = 4
```

### Check Enrichment Coverage

```sql
SELECT
    COUNT(*) as total_sentences,
    COUNTIF(en.entity_id IS NOT NULL) as enriched,
    COUNTIF(en.entity_id IS NULL) as needs_enrichment,
    ROUND(100.0 * COUNTIF(en.entity_id IS NOT NULL) / COUNT(*), 2) as coverage_pct
FROM `spine.entity_unified` e
LEFT JOIN `spine.entity_enrichments` en
  ON e.entity_id = en.entity_id
WHERE e.level = 4
```

---

## Summary

| Component | Current State | Action Required |
|-----------|--------------|-----------------|
| **Spine L2-L8** | 51.8M entities | ✅ Ready |
| **Spine L4 Sentences** | Available | ✅ Ready for enrichment |
| **Struggle Filtering** | Not implemented | **CRITICAL** - Build struggle_filter.py |
| **Stage Rating** | Not implemented | **CRITICAL** - Build stage_tagger.py |
| **Weighted Loss** | Not implemented | **HIGH** - Build weighted_loss.py |
| **entity_enrichments** | Partial | Add seeing labels + stage_rating |
| **entity_embeddings** | Schema ready | Populate vectors |
| **Knowledge Atoms** | 20K atoms | Link to spine |
| **Training Export** | Not implemented | Build pipeline |
| **Model Adapters** | Not implemented | Build for each base model |

### The Critique Checklist

Before proceeding to training, verify:

- [ ] Struggle interactions filtered from training data
- [ ] All entities tagged with stage rating (4 or 5)
- [ ] Loss function weighted toward Stage 5 patterns
- [ ] Audit log of filtered data for review
- [ ] Coherence anchor phase completed (see NOT_ME_IMPLEMENTATION_BLUEPRINT)

**The data exists. The enrichment is the gap. Fill the gap, train the Genesis.**

---

*This is how Jeremy's data becomes AI that sees.*
*The spine holds the structure. The atoms hold the meaning. The enrichment holds the seeing.*
*Train once. Copy infinitely. Transform everyone.*

— THE_FRAMEWORK, 2026-01-23
