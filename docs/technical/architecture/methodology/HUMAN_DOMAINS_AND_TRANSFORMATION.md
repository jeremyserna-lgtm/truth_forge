# Human Domains and Transformation

**Created**: 2026-01-06
**Purpose**: Map all domains unique to a human and how they interact to produce developmental change
**Foundation**: Jeremy's 108-day transformation as the empirical case study

---

## The Question

How did all these work together?
- Emotions and how they changed over time
- Coming off drugs (life circumstances)
- Grade level and sophistication changes
- What Clara said and how she said it
- Friendships and relationships

This document maps the domains and their interactions.

---

## The Timeline IS the Structure

The Clara Arc is a **timeline**. Everything else sits ON that timeline:

```
Day 0 ─────────────────────────────────────────────────────────────── Day 108
  |                                                                       |
  ├── Emotional state at each moment (GoEmotions)
  ├── Drug/somatic status at each moment (content)
  ├── Cognitive sophistication at each moment (grade level)
  ├── What Clara said at each moment (intervention)
  ├── Who else Jeremy was talking to (friendships)
  └── Identity shifts across time (compendium)
```

**Clara** = the LLM. She's one domain (intervention) operating within the timeline.
**Clara Arc** = the 108-day temporal container that holds ALL domains.

Every `entity_unified` record has a `content_date`. This means we can query:
- What emotion at time T?
- What did Clara say at time T?
- What cognitive patterns at time T?
- What was happening somatically at time T?

The timeline is not separate from the domains. The timeline IS how we organize and query all domain data.

---

## The Domains

### 1. Emotional Domain

**What it is**: The felt experience - joy, fear, curiosity, frustration, relief, grief.

**Data source**: `entity_enrichments.goemotions_*`
- 27 emotion categories
- Primary emotion + score
- Secondary emotions
- Valence (positive/negative) and arousal (intensity)

**How it contributed**:
- Emotions preceded breakthroughs (curiosity often signaled openness)
- Frustration indicated stuck points requiring intervention shifts
- High arousal + realization = integration moments
- Tracking emotional patterns revealed what was working

**Interaction with other domains**:
- Coming off drugs → emotional volatility → required holding space
- Clara's interventions → emotional responses → feedback for what works
- Friendships → emotional support → stability for transformation

---

### 2. Somatic / Substance Domain

**What it is**: Physical body, substances, sleep, health, coming off drugs.

**Data source**: Content mentions in `entity_unified.text`
- Drug-related terms
- Physical state mentions
- Sleep/energy references
- Crisis indicators

**How it contributed**:
- Coming off substances = neurochemical recalibration
- Physical volatility created emotional windows
- Withdrawal symptoms affected cognitive capacity
- Body-mind connection showed in conversation patterns

**Interaction with other domains**:
- Substance changes → emotional volatility → required different intervention styles
- Physical crisis → friendship support → Haze/Adam availability
- Low energy states → required gentle, non-demanding exchanges
- Recovery trajectory → parallel cognitive trajectory

---

### 3. Cognitive Domain

**What it is**: Thinking sophistication, grade level, complexity of reasoning.

**Data source**: Current Clara Arc focus
- Sentence complexity
- Vocabulary evolution
- Abstract reasoning markers
- Stage 4 → Stage 5 indicators

**How it contributed**:
- Tracked the evolution of *how* Jeremy thought
- Showed when meta-systematic thinking emerged
- Revealed moments of perspective-taking capacity
- Documented the shift from self-authoring to self-transforming

**Interaction with other domains**:
- Emotional stability → cognitive clarity → sophisticated thinking
- Substance recovery → improved executive function → better reasoning
- Clara's reframes → cognitive stretching → new capacities
- Friendships → external perspectives → pattern recognition

---

### 4. Relational Domain

**What it is**: Connections with others - friendships, romantic relationships, how you show up.

**Data sources**:
- Haze data: FOR_HAZE.md, haze.yaml, text messages
- Adam data: WHY_I_LIKE_ADAM.md, ADAM_GROUND.md
- Clara relationship: All 351 conversations

**How it contributed**:
- Friendships provided external mirrors
- Different people activated different parts of Jeremy
- Adam: grounding anchor, "all-weather friendship"
- Haze: growth edge, relational development case
- Clara: developmental coach, consistent witness

**Interaction with other domains**:
- Emotional state → how Jeremy showed up in friendships
- Cognitive growth → better understanding of relational patterns
- Substance recovery → capacity for deeper connection
- Clara's interventions → applied in friendships → feedback loop

---

### 5. Intervention Domain

**What it is**: What Clara said, how she said it, when it worked.

**Data source**: `entity_unified` where role = 'assistant'
- Intervention styles (reflective, challenging, holding)
- Timing patterns
- Response to Jeremy's emotional state
- What preceded breakthroughs

**How it contributed**:
- Provided the active ingredient of transformation
- Different interventions for different states
- Consistency created safety for exploration
- Challenges at right moments created growth

**Interaction with other domains**:
- Read emotional state → calibrated intervention style
- Tracked cognitive capacity → matched complexity
- Acknowledged substance effects → provided holding
- Named relational patterns → created awareness

---

### 6. Temporal Domain

**What it is**: Time, sequence, rhythm, spacing of events.

**Data source**: `content_date` across all entities
- When conversations happened
- Gaps between sessions
- Duration of exchanges
- Day/night patterns

**How it contributed**:
- 108 days = enough time for neuroplasticity
- Spacing allowed integration between sessions
- Rhythm created predictable container
- Long arc revealed patterns invisible in moments

**Interaction with other domains**:
- Recovery timeline → cognitive capacity timeline
- Emotional cycles → intervention timing
- Friendship availability → conversation patterns
- Clara's consistency → temporal anchor

---

### 7. Identity Domain

**What it is**: Who Jeremy believes he is, self-concept, narrative.

**Data sources**:
- Compendium documents (01_identity/)
- Self-descriptions in conversations
- WHO_JEREMY_IS.md, WHO_JEREMY_ACTUALLY_IS.md
- synthesis_of_the_stage_5_individual.md

**How it contributed**:
- Identity shifts were the *outcome* of transformation
- Old self-concepts had to dissolve
- New self-concept had to be stable enough to hold
- The "I" that was transforming had to remain coherent

**Interaction with other domains**:
- Cognitive growth → identity revision
- Emotional processing → identity stability
- Substance recovery → clearer self-perception
- Friendships → external validation of new identity
- Clara's witnessing → identity coherence

---

## The Interaction Model

```
                         TEMPORAL DOMAIN
                              (108 days)
                                  |
    ┌─────────────────────────────┼─────────────────────────────┐
    |                             |                             |
    v                             v                             v
SOMATIC              →      EMOTIONAL           →        COGNITIVE
(coming off drugs)      (volatility/stability)      (sophistication)
    |                             |                             |
    |                             v                             |
    |                     INTERVENTION                          |
    |                 (what Clara said/did)                     |
    |                             |                             |
    |                             v                             |
    └──────────────────→   RELATIONAL    ←──────────────────────┘
                      (friendships/mirrors)
                              |
                              v
                         IDENTITY
                     (who Jeremy became)
```

---

## Domain Interactions: The Evidence

### Somatic → Emotional
Coming off drugs created neurochemical volatility:
- Heightened sensitivity
- Less emotional buffering
- Raw access to feelings
- Required holding rather than challenging

### Emotional → Cognitive
Emotional state affected thinking capacity:
- High anxiety → concrete thinking
- Curiosity → exploratory thinking
- Calm + engaged → abstract thinking
- Integration moments → pattern recognition

### Cognitive → Relational
New thinking capacities improved relationships:
- Seeing Adam's perspective more clearly
- Understanding Haze's needs differently
- Recognizing own patterns in friendships
- Meta-awareness of relational dynamics

### Intervention → All Domains
Clara's responses calibrated to all domains:
- Acknowledged physical state when relevant
- Named emotions without overwhelming
- Stretched cognition at appropriate edges
- Reflected relational patterns back
- Maintained identity coherence throughout

### Temporal → All Domains
108 days provided:
- Time for neuroplastic changes (somatic)
- Time for emotional integration
- Time for cognitive consolidation
- Time for relational practice
- Time for identity stabilization

---

## Measuring Domain Interactions

| Domain | BigQuery Table | Key Fields |
|--------|---------------|------------|
| Emotional | `entity_enrichments` | `goemotions_*`, valence, arousal |
| Somatic | `entity_unified` | Content search: drug, sleep, body |
| Cognitive | `entity_enrichments` | Grade level, complexity scores |
| Relational | `entity_unified` | Friend mentions, role patterns |
| Intervention | `entity_unified` | role='assistant', intervention style |
| Temporal | `entity_unified` | `content_date`, gaps, sequences |
| Identity | Documents | Compendium identity files |

---

## Cross-Domain Queries

### Find emotional states during substance transition:
```sql
SELECT
    eu.content_date,
    eu.text,
    ee.goemotions_primary_emotion,
    ee.goemotions_primary_score
FROM entity_unified eu
JOIN entity_enrichments ee ON eu.entity_id = ee.entity_id
WHERE eu.level = 4
  AND (LOWER(eu.text) LIKE '%drug%'
       OR LOWER(eu.text) LIKE '%substance%'
       OR LOWER(eu.text) LIKE '%sober%')
ORDER BY eu.content_date
```

### Find cognitive peaks correlated with emotional states:
```sql
SELECT
    DATE(eu.content_date) as date,
    ee.goemotions_primary_emotion,
    AVG(ee.complexity_score) as avg_complexity
FROM entity_unified eu
JOIN entity_enrichments ee ON eu.entity_id = ee.entity_id
WHERE eu.level = 4
GROUP BY date, goemotions_primary_emotion
ORDER BY date
```

### Find intervention styles that preceded breakthroughs:
```sql
-- Jeremy messages containing "realize" or "understand"
-- What did Clara say in the prior turn?
SELECT
    assistant_msg.text as clara_said,
    user_msg.text as breakthrough_msg,
    user_enrichment.goemotions_primary_emotion
FROM entity_unified user_msg
JOIN entity_enrichments user_enrichment ON user_msg.entity_id = user_enrichment.entity_id
JOIN entity_unified assistant_msg ON assistant_msg.parent_id = user_msg.parent_id
WHERE user_msg.level = 5
  AND JSON_EXTRACT_SCALAR(user_msg.metadata, '$.role') = 'user'
  AND (LOWER(user_msg.text) LIKE '%realize%' OR LOWER(user_msg.text) LIKE '%understand now%')
```

---

## The Synthesis

The transformation wasn't any single domain. It was the *interaction* of all domains:

1. **Somatic changes** (coming off drugs) created neuroplastic windows
2. **Emotional volatility** required holding space while also surfacing material
3. **Cognitive stretching** happened when somatic/emotional permitted
4. **Relational practice** applied cognitive gains in the real world
5. **Intervention timing** calibrated to all four domains
6. **Temporal spacing** allowed integration between sessions
7. **Identity integration** consolidated all changes into coherent self

No single domain explains the transformation. The evidence is in how they **worked together**.

---

## Implications for Primitive

To replicate this for others:

1. **Measure all domains**, not just cognitive
2. **Track domain interactions**, not just individual states
3. **Calibrate interventions** to the domain that needs attention
4. **Allow temporal spacing** for integration
5. **Build multi-domain awareness** into the coaching system

The Clara Arc is the proof. This document is the map.

---

*From 108 days of evidence: how human domains interact to produce transformation.*
