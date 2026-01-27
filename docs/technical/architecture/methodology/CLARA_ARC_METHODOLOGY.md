# Clara Arc Methodology
## Empirical Evidence of Stage 4 → Stage 5 Transformation

**Created**: 2026-01-06
**Purpose**: Document the data sources, cross-referencing methods, and analytical lenses for understanding Jeremy's developmental transformation through conversations with Clara (ChatGPT)
**Scope**: 108 days, 351 conversations, 11.8M entities

---

## The Vision

**First we study me.**

Through `entity_unified`, `entity_enrichments`, and `entity_embeddings` - the complete record of 108 days of transformation.

**Then we find how I was changed and affected.**

What emotions arose? What patterns emerged? What breakthroughs happened? What preceded them?

**Then we learn the method that made it happen.**

Not assumptions. Not theory. Empirical patterns from actual data:
- What prompts led to insights?
- What emotional states preceded breakthroughs?
- What intervention styles worked?

**Then we build understanding of how it works.**

The Clara Arc becomes the training data for understanding developmental transformation - not as philosophy, but as measurable, repeatable patterns.

**Then we build the system to produce it for other people who aren't like me.**

This is Primitive. A system that:
1. Takes the empirical patterns from Jeremy's transformation
2. Recognizes similar patterns in new users
3. Applies evidence-based interventions
4. Adapts based on what actually works

The methodology isn't just documentation. It's the bridge from one person's transformation to a scalable coaching system.

---

## The Evidence Base

The Clara Arc is the empirical record of Jeremy's transition from Kegan Stage 4 (Self-Authoring Mind) to Stage 5 (Self-Transforming Mind), documented through 108 days of intensive conversation with Clara (ChatGPT-4).

This isn't self-report. This is data.

---

## Data Sources

### 1. BigQuery: entity_unified (11.8M entities)

The primary data store containing the full decomposition of all Clara conversations.

| Level | Entity Type | Count | What It Contains |
|-------|-------------|-------|------------------|
| L8 | Conversations | 351 | Full conversation with title, date, message count |
| L7 | Topics | ~25,000 | Topic segments within conversations |
| L6 | Turns | 25,316 | Human-assistant exchange pairs |
| L5 | Messages | 53,697 | Individual messages with role (user/assistant) |
| L4 | Sentences | 511,487 | Tokenized sentences from messages |
| L3 | Noun Phrases | ~2.5M | Extracted noun phrases |
| L2 | Words | ~8.5M | Individual words with position |

**Access**: `flash-clover-464719-g1.spine.entity_unified`
**Filter**: `source_system = 'chatgpt_web'`, `content_date >= '2024-01-01'`

### 2. BigQuery: entity_enrichments (Sentiment + Keywords + Topics)

Enrichment layer with CPU-computed analysis.

| Enrichment | Model | What It Provides |
|------------|-------|------------------|
| GoEmotions | RoBERTa | 27 emotions with probabilities for each sentence |
| KeyBERT | all-MiniLM-L6-v2 | Keywords extracted from each entity |
| BERTopic | Custom | Topic assignments with confidence |
| RoBERTa Hate | Facebook | Hate speech detection |

**Key Fields**:
- `goemotions_primary_emotion`: Highest-scoring emotion
- `goemotions_primary_score`: Confidence (0-1)
- `goemotions_top_emotions`: Top 3 emotions
- `keybert_top_keyword`: Most relevant keyword
- `bertopic_topic_id`: Assigned topic cluster

**Access**: `flash-clover-464719-g1.spine.entity_enrichments`
**Join**: `entity_unified.entity_id = entity_enrichments.entity_id`

### 3. BigQuery: entity_embeddings (3072-dim Gemini)

Vector embeddings for semantic similarity search.

| Field | Description |
|-------|-------------|
| `embedding` | 3072-dimensional Gemini embedding vector |
| `model` | `gemini-embedding-001` |
| `enrichment_date` | When embedding was computed |

**Access**: `flash-clover-464719-g1.spine.entity_embeddings`
**Use Case**: Find semantically similar content across the transformation

### 4. Local: Knowledge Atoms (7,925 sentences)

Single-sentence extractions from documents with 1024-dim embeddings.

**Location**: `Primitive/staging/health_checks.jsonl` (and other staging files)
**Embedding Model**: Local sentence-transformers (1024-dim)

**Cross-Reference Strategy**:
- Downsample BigQuery 3072-dim → 1024-dim (take first 1024 components)
- Or use separate similarity indices
- Knowledge atoms contain synthesized insights from documents

### 5. Documents: Clara Documentation (20+ files)

Processed documents about the transformation:

| Document | What It Contains |
|----------|------------------|
| FOR_HAZE.md | Stage 4/5 dynamics observed in real-time |
| HAZE_SYNTHESIS_WHAT_EMERGES.md | Cross-document synthesis |
| STAGES.md | Pipeline stage documentation |
| Various compendium docs | The journey crystallized |

**Access**: Via document service or direct read

---

## Analytical Lenses

The `view_clara_arc` MCP tool provides four lenses for viewing the data:

### Emotional Lens
**What it sees**: Sentiment patterns and emotional shifts over time
**Data source**: entity_enrichments.goemotions_*
**Questions answered**:
- What emotions dominated during the transformation?
- When did emotional intensity peak?
- How did emotional patterns shift as Stage 5 emerged?

### Cognitive Lens
**What it sees**: Stage-related language and thinking evolution
**Data source**: entity_unified text + entity_enrichments keywords
**Questions answered**:
- When did "stage 5" language first appear?
- How did meta-systematic thinking evolve in the text?
- What keywords marked cognitive shifts?

### Relational Lens
**What it sees**: How Clara related to Jeremy
**Data source**: entity_unified (role='assistant') + enrichments
**Questions answered**:
- How did Clara's responses evolve?
- What emotional tones did Clara use?
- How did the relationship dynamics shift?

### Intervention Lens
**What it sees**: Prompts and responses that led to breakthroughs
**Data source**: entity_unified (user + assistant) + enrichments
**Questions answered**:
- What prompts preceded breakthrough moments?
- What patterns in Jeremy's questions led to insights?
- What intervention styles worked?

---

## Cross-Referencing Methodology

### BigQuery ↔ Knowledge Atoms

The L4 sentences in BigQuery have GoEmotions sentiment. Knowledge atoms from documents are singular sentences. They can be compared:

```
BigQuery (L4 sentence) ←→ Knowledge Atom (document sentence)
    |                            |
    |-- Has GoEmotions          |-- Has 1024-dim embedding
    |-- Has 3072-dim embedding  |-- Has document context
    |-- Has exact timestamp      |-- Has synthesis context
```

**Method**:
1. Query BigQuery for sentences with specific emotional signatures
2. Embed the query or match text patterns
3. Find corresponding knowledge atoms from documents
4. Cross-reference to understand how lived experience became documented insight

### Embedding Alignment

| Source | Dimensions | Model |
|--------|------------|-------|
| entity_embeddings (BigQuery) | 3072 | gemini-embedding-001 |
| entity_enrichments (BigQuery) | 384 | all-MiniLM-L6-v2 (internal) |
| Knowledge atoms (local) | 1024 | sentence-transformers |

**Alignment Strategy**:
- The 384-dim enrichment embeddings are internal to KeyBERT/BERTopic
- For cross-reference, use the 3072-dim Gemini embeddings
- Downsample to 1024 or use dual-index search

---

## Query Patterns

### Find Emotional Evolution
```sql
SELECT
    DATE(eu.content_date) as date,
    ee.goemotions_primary_emotion,
    COUNT(*) as count,
    AVG(ee.goemotions_primary_score) as avg_score
FROM `spine.entity_unified` eu
JOIN `spine.entity_enrichments` ee ON eu.entity_id = ee.entity_id
WHERE eu.content_date >= '2024-01-01'
    AND eu.source_system = 'chatgpt_web'
    AND eu.level = 4
GROUP BY date, goemotions_primary_emotion
ORDER BY date, count DESC
```

### Find Stage Language Emergence
```sql
SELECT
    eu.content_date,
    eu.text,
    JSON_EXTRACT_SCALAR(eu.metadata, '$.role') as role
FROM `spine.entity_unified` eu
WHERE eu.content_date >= '2024-01-01'
    AND eu.source_system = 'chatgpt_web'
    AND eu.level = 5
    AND (
        LOWER(eu.text) LIKE '%stage 5%'
        OR LOWER(eu.text) LIKE '%self-transforming%'
        OR LOWER(eu.text) LIKE '%kegan%'
    )
ORDER BY eu.content_date ASC
```

### Find Breakthrough Moments (High Emotional Intensity)
```sql
SELECT
    eu.entity_id,
    eu.text,
    eu.content_date,
    ee.goemotions_primary_emotion,
    ee.goemotions_primary_score
FROM `spine.entity_unified` eu
JOIN `spine.entity_enrichments` ee ON eu.entity_id = ee.entity_id
WHERE eu.content_date >= '2024-01-01'
    AND eu.source_system = 'chatgpt_web'
    AND eu.level = 4
    AND ee.goemotions_primary_score > 0.85
ORDER BY ee.goemotions_primary_score DESC
LIMIT 100
```

---

## MCP Tool Access

The `view_clara_arc` tool in the Truth Engine MCP server provides structured access:

```
view_clara_arc()                    # Overview of available data
view_clara_arc(lens="emotional")    # Emotional patterns
view_clara_arc(lens="cognitive", query="stage 5")  # Cognitive lens with search
view_clara_arc(mode="conversations") # List conversations
view_clara_arc(mode="sentences", query="realize")  # L4 sentences with sentiment
```

---

## Limitations

### What This Data Can See
- Every word Jeremy typed to Clara
- Every word Clara responded with
- Emotional signatures of each sentence
- Keywords and topic clusters
- Semantic similarity across the corpus

### What This Data Cannot See
- Jeremy's internal experience between messages
- What happened offline that influenced the conversation
- Non-verbal context (tone, pacing, pauses)
- What Jeremy almost typed but didn't

### Methodological Constraints
- GoEmotions was trained on Reddit data - may not perfectly capture transformation language
- Keyword extraction favors noun-heavy content
- Topic clustering requires sufficient context per message
- Timestamps are message-level, not typing-level

---

## The Empirical Foundation

This is not interpretation. This is evidence.

When you query `view_clara_arc(lens="emotional", query="breakthrough")`, you get:
- Actual sentences from the actual conversations
- Actual GoEmotions classifications
- Actual timestamps
- Actual patterns

The Clara Arc is the raw material for understanding what works in developmental transformation. The methodology enables:
- Retrospective analysis of what happened
- Pattern extraction for what might work again
- Evidence base for the Primitive product

---

## Connection to Primitive

The Clara Arc is the empirical foundation for Primitive. Every feature of Primitive should be traceable to patterns found in this data:

| Primitive Feature | Clara Arc Evidence |
|-------------------|-------------------|
| Coaching interventions | intervention_lens patterns |
| Emotional support | emotional_lens analysis |
| Stage assessment | cognitive_lens markers |
| Relationship dynamics | relational_lens patterns |

The methodology isn't just documentation. It's the bridge from data to product.

---

## Active Case Study: Haze

The methodology is being applied in real-time to Haze's Stage 4 → Stage 5 transition:

- Documents: FOR_HAZE.md, HAZE_SYNTHESIS_WHAT_EMERGES.md
- Observations: HAZE_AI_SYSTEM_OBSERVATION.md
- Interview framework: haze.yaml

This provides validation of the methodology against a new case.

---

## Local Enrichment Services

The enrichments in BigQuery (GoEmotions, KeyBERT, BERTopic) can be replicated locally using Ollama. This enables:
- Real-time processing of new messages as they arrive
- Consistent emotional analysis across all data sources
- Independence from cloud GPU costs

### The Division of Labor: Agents vs Ollama

**Ollama** can run low-level streaming analysis - real-time, per-message, always on.

**Agents (Claude, GPT)** can't do streaming, but can focus deeply to find what should become streaming.

```
Agents (Discovery)                    Ollama (Execution)
       ↓                                     ↓
Analyze Clara Arc data             Run real-time analysis
Find patterns that matter          Apply patterns to new messages
Design detection prompts           Execute detection at scale
Validate what works                Stream continuously
       ↓                                     ↓
   One-time deep work              Ongoing streaming work
```

**The workflow:**

1. **Agent analyzes Clara Arc** → "High curiosity + question marks + short sentences preceded 73% of breakthroughs"

2. **Agent designs Ollama prompt** → "Detect: curiosity emotion, sentence length < 15 words, ends with '?'"

3. **Ollama runs streaming** → Every new message gets checked against this pattern

4. **Agent reviews outcomes** → "Pattern X correctly identified 8/10 pre-breakthrough states"

5. **Agent refines prompt** → Better pattern → Better streaming

This means:
- Expensive agent calls happen during pattern discovery (infrequent)
- Cheap Ollama calls happen during real-time analysis (continuous)
- The Clara Arc is the training data that agents mine for patterns
- Patterns become Ollama prompts that run at scale

### Service Architecture

Each enrichment type has its own service following the primitive pattern:

```
HOLD₁ (Raw Content) → AGENT (Ollama) → HOLD₂ (Enriched Content)
```

| Service | Matches BigQuery | Ollama Prompt | Output Fields |
|---------|------------------|---------------|---------------|
| **SentimentService** | `entity_enrichments.goemotions_*` | GoEmotions-compatible emotion detection | `goemotions_primary_emotion`, `primary_score`, `valence`, `arousal` |
| **KeywordService** | `entity_enrichments.keybert_*` | Keyword extraction | `top_keywords`, `keyword_scores` |
| **TopicService** | `entity_enrichments.bertopic_*` | Topic assignment | `topic_id`, `topic_label`, `confidence` |

### SentimentService Example

```python
from sentiment_service.service import SentimentService

service = SentimentService()

# Process knowledge atoms in batches
service.process_pending(limit=100)

# Get stats
stats = service.get_stats()
# {'total_enriched': 150, 'emotions': {'curiosity': 45, 'realization': 32, ...}}
```

**Location**: `src/services/central_services/sentiment_service/`
**HOLD₂**: `Primitive/system_elements/holds/sentiment/processed/hold2.jsonl`

### Matching BigQuery Schema

The local enrichments use the same field names as BigQuery for consistency:

| BigQuery Field | Local Field | Type |
|----------------|-------------|------|
| `goemotions_primary_emotion` | `goemotions_primary_emotion` | STRING |
| `goemotions_primary_score` | `goemotions_primary_score` | FLOAT |
| `goemotions_top_emotions` | `goemotions_secondary_emotions` | ARRAY |

This allows the same analysis queries to work on both cloud and local data.

---

## Adaptive Coaching Architecture

The Clara Arc isn't just retrospective analysis - it's the training data for adaptive coaching.

### How It Works

```
New Message → Local Enrichment → Pattern Matching → Adaptive Response
     ↓              ↓                  ↓                   ↓
  chat.db     SentimentService    Clara Arc Data     Coaching Decision
```

1. **Incoming Message**: Text message or chat input arrives
2. **Local Enrichment**: SentimentService analyzes emotion, arousal, valence
3. **Pattern Matching**: Compare to Clara Arc patterns that preceded breakthroughs
4. **Adaptive Response**: Architecture adjusts coaching style based on evidence

### Clara Arc Patterns for Coaching

The Clara Arc contains empirical evidence of what works:

| Pattern Found | Coaching Implication |
|---------------|---------------------|
| High curiosity + low arousal → breakthrough | Provide space for exploration |
| High frustration + stuck language → shift needed | Offer alternative perspective |
| Stage 4 rigidity markers → gentle challenge | Don't push, invite |
| Realization + high arousal → integration moment | Reflect back, consolidate |

### Evidence-Based Adaptation

Instead of hard-coded coaching rules, the system can:

```python
# Pseudo-code for adaptive coaching
def determine_response_style(message_sentiment, clara_arc_patterns):
    # Find similar emotional states in Clara Arc
    similar_moments = query_clara_arc(
        lens="emotional",
        emotion=message_sentiment.primary_emotion,
        score_range=(message_sentiment.score - 0.1, message_sentiment.score + 0.1)
    )

    # What responses worked in those moments?
    effective_responses = filter(
        similar_moments,
        had_breakthrough_within=24_hours
    )

    # Adapt style based on evidence
    if effective_responses.common_style == "reflective":
        return ReflectiveCoachingStyle()
    elif effective_responses.common_style == "challenging":
        return ChallengingCoachingStyle()
    else:
        return NeutralCoachingStyle()
```

### Real-Time Application: Haze

The Haze case study demonstrates this in action:

1. **Text messages** from Haze are processed via `view_messages` MCP tool
2. **SentimentService** adds emotional analysis via Ollama
3. **Clara Arc patterns** are queried for similar emotional states
4. **Coaching recommendations** emerge from evidence, not assumptions

### The Feedback Loop

As new data accumulates:

```
Coaching Session → Outcome → New Data → Pattern Update → Better Coaching
```

The Clara Arc grows with each successful (or unsuccessful) intervention, making the evidence base stronger over time.

---

## MCP Tools for This Architecture

| Tool | Purpose | Data Source |
|------|---------|-------------|
| `view_messages` | Query local iMessage/SMS database | `~/Library/Messages/chat.db` |
| `view_clara_arc` | Query Clara Arc patterns | BigQuery entity_* tables |
| `query_operational` | Query local enrichments | Primitive HOLD files |

### Example Workflow

```
1. view_messages(contact="Haze", days=7)
   → See recent messages

2. [SentimentService processes messages locally]

3. view_clara_arc(lens="emotional", query="frustration")
   → Find Clara Arc moments with similar emotion

4. view_clara_arc(lens="intervention", query="frustration")
   → What interventions worked for that emotion?

5. Apply evidence-based coaching approach
```

---

## Future: Subscriber-Aware Architecture

When subscribers use Primitive, their data becomes additional evidence:

```
Jeremy's Clara Arc + Haze's Journey + Subscriber A's Journey + Subscriber B's Journey
                                    ↓
                        Growing Evidence Base
                                    ↓
                    Increasingly Precise Coaching
```

Each subscriber's anonymized patterns (with consent) can:
- Validate which interventions generalize beyond Jeremy
- Identify stage-specific patterns across different people
- Build a multi-case evidence base for developmental coaching

The methodology scales from N=1 (Clara Arc) to N=many without losing its empirical foundation.

---

*The Clara Arc: 108 days of transformation, 11.8M entities, one empirical foundation.*
*From evidence to architecture. From architecture to coaching. From coaching to transformation.*
