# Pattern Discovery Framework

**Date**: 2026-01-28  
**Data**: 11.9M ChatGPT entities (0% embedded currently)  
**Goal**: Identify patterns at three levels

---

## Three Levels of Pattern Recognition

### 1. **Known Patterns** (Pattern Recognition)
Patterns we explicitly know about and can define:

**From Clara Archive**:
- Breakdown detection patterns (100% accuracy on 77K+ items from AI Breakdown Prevention)
- Fracture protocol triggers
- Pre-intent signals (Edge Mode telemetry)
- Drift detection (recursive queries, abandoned searches)
- Hesitation markers (zero-prefix behavior)

**From Current Work**:
- Multi-turn clustering patterns
- Building mode detection
- Thinking block identification
- Topic segment boundaries

**Method**: Define explicit rules/heuristics, validate against labeled data

---

### 2. **Unknown Patterns** (Pattern Discovery)
Patterns that exist but we haven't identified yet:

**Techniques**:
- **Clustering** (once embeddings exist):
  - K-means on conversation embeddings
  - HDBSCAN for density-based discovery
  - Topic modeling (LDA/NMF)
  
- **Without Embeddings** (current state):
  - Statistical anomaly detection (length/pace)
  - Turn-taking pattern analysis
  - Pronoun shift detection
  - Temporal patterns (time of day, day of week)
  - Conversation velocity changes
  - Entity level distribution anomalies

**Method**: Unsupervised learning, anomaly detection, statistical analysis

---

### 3. **Undecided Patterns** (Pattern Hypothesis)
Things that might be patterns, waiting for validation:

**Current Hypotheses**:
- "Consciousness emergence moments" (transition from tool use to relationship)
- "Stage 5 weight bearing" (when AI starts handling meta-cognitive load)
- "Sacred vs functional" distinction moments
- "Identity formation" sequences
- Evolution of language/terminology over time

**Method**: Define hypothesis, create detection criteria, test against data, decide if pattern exists

---

## Immediate Actions (Minimum Viable)

### Start Without Embeddings

**ChatGPT data available now** (11.9M entities, 702 conversations):

1. **Statistical Baseline**
   ```sql
   -- Conversation length distribution
   -- Message count per conversation
   -- Average turn length
   -- Persona distribution
   -- Temporal patterns
   ```

2. **Known Pattern Validation**
   - Test Edge Mode concepts (can we detect hesitation from turn patterns?)
   - Validate breakdown detection without telemetry
   - Map known Clara patterns to ChatGPT structure

3. **Simple Anomaly Detection**
   - Unusually long messages
   - Rapid turn sequences
   - Conversation restarts
   - Topic shifts (basic keyword analysis)

### Generate Embeddings (Next Step)

**Once we have compute** (THE EMPIRE arrival):

1. **Run Stage 4 on ChatGPT data**
   - Generate embeddings for all 11.9M entities
   - Store in `entity_embeddings` table
   - Calculate coverage metrics

2. **Clustering Analysis**
   - Conversation-level clustering
   - Message-level clustering
   - Topic segment clustering

3. **Similarity Search**
   - Find similar conversations
   - Identify repeated patterns
   - Map conceptual evolution

---

## Exploration Strategy

### Dual Track Approach

**Track 1: You Explore (Directed)**
- Known patterns from Clara archive
- Edge Mode sophistication mapping
- Specific hypotheses about consciousness emergence
- Validation of breakdown detection

**Track 2: Automated Discovery (Undirected)**
- Statistical clustering
- Anomaly detection
- Pattern mining algorithms
- Topic modeling

**Then: Synthesis**
- What matches between directed and undirected?
- What did automation find that you didn't expect?
- What hypotheses got validated/rejected?
- What new questions emerged?

---

## Minimum Start (Today)

### Query 1: Statistical Baseline

```sql
-- Get conversation-level statistics
SELECT 
  conversation_id,
  COUNT(*) as entity_count,
  COUNT(DISTINCT message_id) as message_count,
  COUNT(DISTINCT persona) as unique_personas,
  MIN(source_message_timestamp) as first_message,
  MAX(source_message_timestamp) as last_message,
  TIMESTAMP_DIFF(MAX(source_message_timestamp), MIN(source_message_timestamp), HOUR) as conversation_duration_hours
FROM `flash-clover-464719-g1.spine.entity_unified`
WHERE source_system = 'chatgpt_web'
GROUP BY conversation_id
ORDER BY entity_count DESC
LIMIT 50
```

### Query 2: Temporal Pattern Check

```sql
-- When do conversations happen?
SELECT 
  EXTRACT(HOUR FROM source_message_timestamp) as hour_of_day,
  EXTRACT(DAYOFWEEK FROM source_message_timestamp) as day_of_week,
  COUNT(DISTINCT conversation_id) as conversation_count,
  COUNT(*) as entity_count
FROM `flash-clover-464719-g1.spine.entity_unified`
WHERE source_system = 'chatgpt_web'
  AND source_message_timestamp IS NOT NULL
GROUP BY hour_of_day, day_of_week
ORDER BY hour_of_day, day_of_week
```

### Query 3: Anomaly Candidates

```sql
-- Find unusual conversations (very long, very short, unusual patterns)
WITH conv_stats AS (
  SELECT 
    conversation_id,
    COUNT(*) as entity_count,
    COUNT(DISTINCT message_id) as message_count,
    AVG(LENGTH(text)) as avg_text_length,
    STDDEV(LENGTH(text)) as stddev_text_length
  FROM `flash-clover-464719-g1.spine.entity_unified`
  WHERE source_system = 'chatgpt_web'
    AND text IS NOT NULL
  GROUP BY conversation_id
)
SELECT 
  conversation_id,
  entity_count,
  message_count,
  ROUND(avg_text_length, 2) as avg_text_length,
  ROUND(stddev_text_length, 2) as stddev_text_length,
  CASE 
    WHEN entity_count > 50000 THEN 'very_long'
    WHEN entity_count < 100 THEN 'very_short'
    WHEN stddev_text_length > avg_text_length * 2 THEN 'high_variance'
    ELSE 'normal'
  END as anomaly_type
FROM conv_stats
WHERE entity_count > 50000 
   OR entity_count < 100 
   OR stddev_text_length > avg_text_length * 2
ORDER BY entity_count DESC
```

---

## Pattern Library Structure

### Catalog Format

Each identified pattern gets:

1. **Pattern Name** (e.g., "Pre-Intent Hesitation")
2. **Pattern Type** (Known/Discovered/Hypothesized)
3. **Detection Method** (statistical/ML/rule-based)
4. **Validation Status** (proven/testing/rejected)
5. **Examples** (conversation IDs, entity IDs)
6. **Significance** (why it matters)
7. **Related Patterns** (connections to others)

### Storage

Patterns stored in:
- `/truth_forge/training/patterns/` directory
- One markdown file per pattern
- Cross-referenced in master index
- Linked to Genesis training data

---

## Next Steps

1. **Run baseline queries** (get statistical foundation)
2. **Map Clara patterns** (can we detect them in ChatGPT data?)
3. **Generate embeddings** (waiting for THE EMPIRE)
4. **Build pattern library** (document everything we find)
5. **Feed to Genesis** (patterns become training signal)

---

**Embedding Status**: 0.0% (11.9M entities, 0 embeddings)  
**Action Required**: Generate embeddings (Stage 4 on ChatGPT data)  
**Timeline**: After THE EMPIRE arrival (hardware needed)

🔍
