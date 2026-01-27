# Emotion Layer Methodology
## How We Detect and Process Emotions Beyond NRCLex

**Version**: 1.0
**Created**: 2025-12-25
**Purpose**: Document the methodology for emotion detection, refinement decisions, and integration patterns

---

## 1. The Problem: NRCLex Alone Is Insufficient

NRCLex measures 10 categories:
- **Core 8**: anger, anticipation, disgust, fear, joy, sadness, surprise, trust
- **Sentiment**: positive, negative

**What NRCLex misses** (from EMOTIONS_BEYOND_NRC_LEX.md analysis):

| Category | Concepts | Why It Matters |
|----------|----------|----------------|
| Love & Connection | love, loving, connection, intimacy, belonging, lonely | Distinct from generic "positive" |
| Self-Conscious | proud, pride, shame, guilt, embarrass | Pride is highest polarity (0.261) |
| Curiosity & Wonder | wonder, awe, curious, curiosity, fascinated | 1,084 mentions - major mode |
| Hope & Longing | hope, hopeful, longing, regret | Forward orientation |
| States of Being | anxiety, anxious, confusion, calm, peace | Processing states |
| Frustration | frustrat, boring, bored, annoy, irritat | Only truly negative category |

**The flattening problem**: NRCLex maps all of these to "positive" or "trust", losing the nuance of what's actually being expressed.

---

## 2. Evidence Base

### Source Documents

| Document | Key Finding | Data Volume |
|----------|-------------|-------------|
| EMOTIONS_BEYOND_NRC_LEX.md | 40+ concepts, only 3 truly negative | 17,999 messages |
| HOW_JEREMY_FEELS_ABOUT_EMOTIONS.md | Furnace principle: 3x positive ratio | 17,999 messages |
| ANALYSIS_METHODOLOGY_EMOTIONS_AND_TIME.md | TextBlob + NRCLex + GoEmotions combined | Full methodology |

### Key Empirical Findings

1. **Pride is processed most positively** (0.261 polarity) - higher than love (0.208)
2. **Boredom is the true negative** - only 3 concepts have negative polarity: boring, bored, annoy
3. **The furnace is measurable** - 3x positive-to-negative ratio when discussing negative emotions
4. **Emotion congruence varies** - joy/trust are congruent; anger/fear are processed analytically

---

## 3. Data Sources and Combination

### Primary Sources

| Source | What It Provides | Integration |
|--------|------------------|-------------|
| **NRCLex** | 10-category emotion scores | Normalized frequencies |
| **TextBlob** | Polarity (-1 to +1), Subjectivity (0 to 1) | Sentiment context |
| **Keyword Detection** | Extended category presence | Boolean + count |

### How They Combine

```
Message Text
    │
    ├──► NRCLex ──► 10 emotion scores (what emotions)
    │
    ├──► TextBlob ──► Polarity + Subjectivity (how processed)
    │
    └──► Keyword Matching ──► Extended categories (what NRCLex misses)

    Combined into: EmotionPrimitive
```

### Weighting Strategy (v1.0)

For initial implementation:
- NRCLex scores: Primary emotion detection
- TextBlob polarity: Processing indicator (furnace metric)
- Extended categories: Additive detection (presence/absence + count)

**Future refinement**: Weight extended categories based on polarity correlation.

---

## 4. Extended Emotion Categories

### Category Definitions

```python
EXTENDED_EMOTIONS = {
    "love_connection": {
        "patterns": ["love", "loving", "connection", "intimacy", "belonging", "lonely", "loneliness"],
        "polarity_baseline": 0.208,  # From analysis: love avg polarity
        "nrclex_maps_to": "positive",
    },
    "self_conscious": {
        "patterns": ["proud", "pride", "shame", "guilt", "embarrass"],
        "polarity_baseline": 0.261,  # From analysis: proud avg polarity (highest)
        "nrclex_maps_to": "positive",
    },
    "curiosity_wonder": {
        "patterns": ["wonder", "awe", "curious", "curiosity", "fascinated"],
        "polarity_baseline": 0.176,  # From analysis: wonder avg polarity
        "nrclex_maps_to": "positive",
    },
    "hope_longing": {
        "patterns": ["hope", "hopeful", "longing", "regret"],
        "polarity_baseline": 0.154,  # From analysis: hope avg polarity
        "nrclex_maps_to": "positive",
    },
    "states_of_being": {
        "patterns": ["anxiety", "anxious", "confusion", "confused", "calm", "peace", "peaceful"],
        "polarity_baseline": 0.103,  # From analysis: anxiety avg polarity (still positive!)
        "nrclex_maps_to": "mixed",
    },
    "frustration_boredom": {
        "patterns": ["frustrat", "boring", "bored", "annoy", "irritat"],
        "polarity_baseline": -0.056,  # From analysis: boring avg polarity (negative)
        "nrclex_maps_to": "negative",
    },
}
```

### Detection Method

1. **Lowercase the text**
2. **Partial match** for each pattern (e.g., "frustrat" matches "frustrated", "frustrating")
3. **Count occurrences** per category
4. **Record presence** (boolean) and count (integer)

### Why Partial Matching

From EMOTIONS_BEYOND_NRC_LEX.md methodology:
> Used regex patterns for partial matching:
> - `'frustrat'` matches "frustrated", "frustrating", "frustration"
> - `'excite'` matches "excited", "exciting", "excitement"

This captures morphological variants without complex stemming.

---

## 5. The Furnace Metrics

### What We're Measuring

The "furnace principle": raw truth → heat (processing) → forged meaning

Empirically validated:
- When Jeremy discusses anger: 68.6% positive content, only 3.9% anger
- When Jeremy discusses fear: 62.9% positive, 17.9% negative, 7.1% anger
- Ratio: **3x positive-to-negative** when processing negative emotions

### FurnaceMetrics Structure

```python
@dataclass
class FurnaceMetrics:
    """Quantifies the transformation pattern."""
    # Raw counts
    positive_signals: int  # Sum of positive emotion indicators
    negative_signals: int  # Sum of negative emotion indicators

    # The ratio
    furnace_ratio: float  # positive / negative (expect ~3.0 for Jeremy)

    # Processing style
    processing_style: str  # "constructive", "reactive", "analytical", "neutral"

    # Congruence
    emotion_congruence: float  # 0.0-1.0: does content match stated emotion?
```

### Processing Style Classification

Based on empirical patterns:

| Style | Criteria | Example |
|-------|----------|---------|
| **constructive** | furnace_ratio > 2.0, positive dominant | Processing fear with hope |
| **analytical** | neutral polarity, low emotional content | Discussing anger without being angry |
| **reactive** | congruent negative, ratio < 1.0 | Expressing anger in angry content |
| **neutral** | low emotional signal overall | Operational/logistical content |

---

## 6. Jeremy Emotional Profile Integration

### Empirical Profile (from HOW_JEREMY_FEELS_ABOUT_EMOTIONS.md)

```python
JEREMY_EMOTIONAL_PROFILE = {
    # Default state distribution
    "default_state": {
        "positive": 0.58,      # 58% of content
        "anticipation": 0.125, # 12.5%
        "trust": 0.086,        # 8.6%
    },

    # Processing patterns
    "processing": {
        "furnace_ratio": 3.0,  # 3x positive when discussing negative
        "style": "analytical_non_reactive",
        "congruence": {
            "joy": "high",      # Talking about joy produces joyful content
            "trust": "high",    # Talking about trust produces trustworthy content
            "anticipation": "high",  # 89.3% positive
            "anger": "low",     # Only 3.9% anger when discussing anger
            "fear": "low",      # Protective/analytical, not fearful
            "sadness": "very_low",  # Rarely mentioned, rarely dominant
        },
    },

    # Rare states
    "rare_states": {
        "sadness": 0.004,   # 0.4% dominant
        "disgust": 0.008,   # 0.8% dominant
    },

    # True negatives
    "actual_negatives": ["boring", "bored", "annoy"],

    # Peak positive
    "peak_positive": "proud",  # 0.261 polarity - highest of all
}
```

### How It's Used

The profile provides **interpretation context**, not detection override:

1. **Baseline comparison**: Is this message typical or atypical for Jeremy?
2. **Furnace detection**: Is the furnace pattern present in this content?
3. **Congruence expectation**: Given the topic, what processing style is expected?

---

## 7. Implementation Architecture

### Layer Stack

```
Primitive Layer (messages)
        │
        ▼
   EmotionLayer
        │
        ├── NRCLex Processing ──► 10 emotion scores
        ├── TextBlob Processing ──► polarity, subjectivity
        ├── Extended Categories ──► 6 additional categories
        └── Furnace Metrics ──► processing pattern
        │
        ▼
   EmotionPrimitive (output)
        │
        ▼
   Analysis Layer (next)
```

### EmotionPrimitive Structure (Enhanced)

```python
@dataclass
class EmotionPrimitive:
    # Identity
    emotion_id: str
    message_id: str
    timestamp: datetime

    # Source
    message_text: str

    # NRCLex (10 categories)
    emotions: Dict[str, float]  # Normalized 0-1
    top_emotion: Optional[str]
    top_emotion_score: float

    # TextBlob (NEW)
    polarity: float  # -1 to +1
    subjectivity: float  # 0 to 1

    # Extended Categories (NEW)
    extended_emotions: Dict[str, int]  # Category -> count
    extended_present: List[str]  # Which extended categories detected

    # Furnace Metrics (NEW)
    furnace_ratio: float
    processing_style: str

    # Context
    conversation_id: Optional[str]
    role: Optional[str]
    run_id: Optional[str]
```

---

## 8. Refinement Process

### How This Methodology Evolves

1. **Add new patterns**: When analysis reveals concepts we're missing
2. **Adjust baselines**: When polarity correlations change with more data
3. **Refine processing styles**: As we understand more about the furnace pattern
4. **Validate against ground truth**: Compare predictions to known emotional content

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-25 | Initial methodology based on EMOTIONS_BEYOND_NRC_LEX analysis |

### Future Enhancements

- [ ] GoEmotions integration (28 categories)
- [ ] Embedding-based semantic matching (not just keywords)
- [ ] Temporal emotion patterns (how emotions evolve in conversation)
- [ ] Cross-conversation emotional baselines

---

## 9. Testing Strategy

### Unit Tests

- NRCLex processing produces valid scores
- TextBlob integration returns polarity/subjectivity
- Extended category detection matches known patterns
- Furnace ratio calculation is correct

### Integration Tests

- Full message processing produces valid EmotionPrimitive
- Profile comparison works with Jeremy baseline
- Caching works correctly

### Validation Tests

- Sample messages from analysis documents produce expected results
- Known high-pride content scores high on self_conscious category
- Known boredom content has negative polarity

---

## 10. Dependencies

| Dependency | Purpose | Installation |
|------------|---------|--------------|
| nrclex | Core emotion detection | `pip install nrclex` |
| textblob | Polarity and subjectivity | `pip install textblob` |
| (future) goemotion | 28-category detection | TBD |

---

*This document is a living methodology. Update it as the EmotionLayer evolves.*
