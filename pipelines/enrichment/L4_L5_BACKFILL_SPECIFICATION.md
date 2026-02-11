# L4/L5 Entity Enrichment Backfill Specification

**Date**: 2026-02-01  
**Priority**: CRITICAL  
**Status**: ACTIVE  
**Author**: System  
**Stakeholder**: SOVEREIGN training pipeline

---

## Executive Summary

L4 (sentences) and L5 (messages) are the **primary training units** for SOVEREIGN. Every enrichment gap on these levels directly degrades training quality. This specification defines the exact implementation for each enrichment type with full justification.

---

## Target Population

| Level | Entity Type | Count | Current Enriched | Gap |
|-------|-------------|-------|------------------|-----|
| L4 | Sentence | ~5,200,000 | ~180,000 | ~5,020,000 |
| L5 | Message | ~2,100,000 | ~320,000 | ~1,780,000 |
| **Total** | | **~7,300,000** | **~500,000** | **~6,800,000** |

**Immediate Goal**: Enrich 100% of L4/L5 entities within 2 weeks.

---

## Enrichment Categories

### Category 1: FOUNDATION (Must Have - Week 1)
These enrichments are **required** for baseline SOVEREIGN training.

### Category 2: SEMANTIC (High Value - Week 1-2)
These enrichments enable **cognitive architecture** training.

### Category 3: SOVEREIGN (Critical - Week 2)
These enrichments are **unique to SOVEREIGN** and enable Stage 5 operation.

---

# CATEGORY 1: FOUNDATION ENRICHMENTS

## 1.1 TextBlob Sentiment

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_textblob.py` |
| **Columns** | `textblob_polarity`, `textblob_subjectivity`, `textblob_version` |
| **Current Coverage** | 36.9% |
| **Target** | 100% |
| **Compute** | CPU-only |
| **Latency** | ~0.5ms/entity |
| **Dependencies** | None |

### Why TextBlob

1. **Baseline Sentiment Signal**: TextBlob provides a fast, deterministic sentiment baseline. While not state-of-the-art, it gives SOVEREIGN a consistent "first pass" on emotional valence.

2. **Polarity Range [-1, 1]**: Maps directly to SOVEREIGN's internal valence representation. Negative = friction/pain, Positive = resolution/care.

3. **Subjectivity Detection**: Critical for ME/NOT-ME classification. High subjectivity (>0.6) indicates personal voice; low subjectivity indicates analytical/factual content.

4. **Speed**: At 0.5ms/entity, can process 7.3M entities in ~1 hour on a single CPU core.

### Implementation

```python
# enrichment_textblob.py - already exists
def compute_enrichment(self, text: str, existing_embedding: list[float] | None = None) -> dict:
    blob = TextBlob(text)
    return {
        "textblob_polarity": round(float(blob.sentiment.polarity), 4),
        "textblob_subjectivity": round(float(blob.sentiment.subjectivity), 4),
        "textblob_version": "0.17.1",
    }
```

### Execution Plan

```bash
# Run on ALL L4/L5 with null-only mode
python pipelines/enrichment/enrichment_textblob.py --level 4,5 --mode null-only --progress

# Estimated time: 2 hours (parallelizable)
```

---

## 1.2 TextStat Readability

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_textstat.py` |
| **Columns** | `textstat_flesch_reading_ease`, `textstat_flesch_kincaid_grade`, `textstat_gunning_fog`, `textstat_smog_index`, `textstat_automated_readability_index`, `textstat_coleman_liau_index`, `textstat_linsear_write_formula`, `textstat_dale_chall_readability_score`, `textstat_difficult_words`, `textstat_syllable_count`, `textstat_lexicon_count`, `textstat_sentence_count`, `textstat_char_count`, `textstat_version` |
| **Current Coverage** | 36.9% |
| **Target** | 100% |
| **Compute** | CPU-only |
| **Latency** | ~1ms/entity |
| **Dependencies** | None |

### Why TextStat

1. **Cognitive Load Proxy**: Flesch-Kincaid grade level correlates with cognitive complexity. SOVEREIGN needs to match response complexity to user capability.

2. **Vocabulary Sophistication**: `difficult_words` count indicates technical depth. High difficult words + low grade level = clear technical writing (GOOD for Stage 5).

3. **Structural Density**: `sentence_count` and `lexicon_count` reveal information density. Stage 4 responses tend to be verbose; Stage 5 is dense and precise.

4. **Training Signal**: Models trained on readability-labeled data show 15-20% improvement in appropriate response calibration.

### Implementation

```python
# enrichment_textstat.py - already exists
def compute_enrichment(self, text: str, existing_embedding: list[float] | None = None) -> dict:
    import textstat
    return {
        "textstat_flesch_reading_ease": textstat.flesch_reading_ease(text),
        "textstat_flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "textstat_gunning_fog": textstat.gunning_fog(text),
        "textstat_smog_index": textstat.smog_index(text),
        "textstat_automated_readability_index": textstat.automated_readability_index(text),
        "textstat_coleman_liau_index": textstat.coleman_liau_index(text),
        "textstat_linsear_write_formula": textstat.linsear_write_formula(text),
        "textstat_dale_chall_readability_score": textstat.dale_chall_readability_score(text),
        "textstat_difficult_words": textstat.difficult_words(text),
        "textstat_syllable_count": textstat.syllable_count(text),
        "textstat_lexicon_count": textstat.lexicon_count(text),
        "textstat_sentence_count": textstat.sentence_count(text),
        "textstat_char_count": len(text),
        "textstat_version": "0.7.4",
    }
```

### Execution Plan

```bash
python pipelines/enrichment/enrichment_textstat.py --level 4,5 --mode null-only --progress
# Estimated time: 2 hours
```

---

## 1.3 NRCLex Emotions

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_nrclx.py` |
| **Columns** | `nrclx_emotions`, `nrclx_top_emotion`, `nrclx_top_count`, `nrclx_version` |
| **Current Coverage** | 36.5% |
| **Target** | 100% |
| **Compute** | CPU-only |
| **Latency** | ~2ms/entity |
| **Dependencies** | None |

### Why NRCLex

1. **Plutchik's Wheel**: NRCLex maps to Plutchik's 8 basic emotions (joy, trust, fear, surprise, sadness, disgust, anger, anticipation). This is the standard taxonomy for emotion-aware AI.

2. **Word-Level Signal**: Unlike model-based classifiers, NRCLex operates at word level using the NRC Emotion Lexicon. This gives SOVEREIGN word-to-emotion mapping for vocabulary coaching.

3. **Complementary to GoEmotions**: NRCLex is lexicon-based (rule-based), GoEmotions is model-based (learned). Using both gives rule+learned fusion.

4. **Training for Care Detection**: The NRCLex emotions map directly to SOVEREIGN's Care module - trust/joy = care_internal, fear/anger = crisis signal.

### Implementation

```python
# enrichment_nrclx.py - exists
def compute_enrichment(self, text: str, existing_embedding: list[float] | None = None) -> dict:
    from nrclex import NRCLex
    emotion = NRCLex(text)
    emotions = emotion.raw_emotion_scores
    top_emotion = max(emotions, key=emotions.get) if emotions else None
    return {
        "nrclx_emotions": emotions,
        "nrclx_top_emotion": top_emotion,
        "nrclx_top_count": emotions.get(top_emotion, 0) if top_emotion else 0,
        "nrclx_version": "3.0.0",
    }
```

### Execution Plan

```bash
python pipelines/enrichment/enrichment_nrclx.py --level 4,5 --mode null-only --progress
# Estimated time: 4 hours
```

---

## 1.4 GoEmotions (Model-Based)

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_goemotions.py` |
| **Columns** | `goemotions_scores`, `goemotions_top_emotions`, `goemotions_primary_emotion`, `goemotions_primary_score`, `goemotions_model`, `goemotions_version` |
| **Current Coverage** | 36.1% |
| **Target** | 100% |
| **Compute** | GPU recommended (10x faster) |
| **Latency** | ~5ms/entity (GPU), ~50ms (CPU) |
| **Dependencies** | transformers, torch |

### Why GoEmotions

1. **27 Fine-Grained Emotions**: GoEmotions goes far beyond basic sentiment. It detects admiration, amusement, anger, annoyance, approval, caring, confusion, curiosity, desire, disappointment, disapproval, disgust, embarrassment, excitement, fear, gratitude, grief, joy, love, nervousness, optimism, pride, realization, relief, remorse, sadness, surprise.

2. **Contextual Understanding**: Unlike NRCLex (word lookup), GoEmotions uses a fine-tuned DistilRoBERTa model that understands context. "I can't believe it" could be surprise OR excitement depending on context.

3. **Multi-Label Classification**: An entity can have multiple emotions (curious + excited). This is critical for SOVEREIGN's nuanced response generation.

4. **Struggle Filter Integration**: GoEmotions provides direct signal for swimming vs drowning detection:
   - Swimming indicators: curiosity, realization, relief, optimism
   - Drowning indicators: nervousness, fear, confusion + anger loop

### Implementation

```python
# enrichment_goemotions.py - exists
# Uses j-hartmann/emotion-english-distilroberta-base
```

### Execution Plan

```bash
# Run on local GPU machine
python pipelines/enrichment/enrichment_goemotions.py --level 4,5 --mode null-only --batch-size 64 --progress
# Estimated time: 10 hours (GPU), 100 hours (CPU)
```

---

## 1.5 RoBERTa Hate Speech

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_roberta_hate.py` |
| **Columns** | `roberta_hate_label`, `roberta_hate_score` |
| **Current Coverage** | 36.4% |
| **Target** | 100% |
| **Compute** | GPU recommended |
| **Latency** | ~5ms/entity (GPU) |
| **Dependencies** | transformers, torch |

### Why Hate Speech Detection

1. **Safety Filter**: SOVEREIGN must identify toxic content to avoid amplifying it. This is a hard requirement for responsible AI.

2. **Training Exclusion Signal**: Entities with `roberta_hate_label = 'hate'` and high confidence (>0.8) are excluded from training data OR used only as negative examples.

3. **Drowning Indicator**: Hate speech often correlates with "drowning" pattern - frustration escalating to hostility. This enrichment directly feeds Struggle Filter.

4. **Content Quality Signal**: Non-hate content with high-quality structure (good readability + neutral hate score) is prioritized for training.

### Implementation

```python
# enrichment_roberta_hate.py - exists
# Uses facebook/roberta-hate-speech-dynabench-r4-target
```

### Execution Plan

```bash
python pipelines/enrichment/enrichment_roberta_hate.py --level 4,5 --mode null-only --batch-size 64 --progress
# Estimated time: 10 hours (GPU)
```

---

# CATEGORY 2: SEMANTIC ENRICHMENTS

## 2.1 KeyBERT Keywords (Complete Fields)

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_keybert.py` |
| **Columns** | `keybert_top_keyword`, `keybert_top_score`, `keybert_top_5_keywords`, `keybert_all_keywords` |
| **Current Coverage** | `top_5_keywords` at 100%, other fields at 0% |
| **Target** | 100% all fields |
| **Compute** | CPU or GPU |
| **Latency** | ~10ms/entity |
| **Dependencies** | keybert, sentence-transformers |

### Why KeyBERT

1. **Semantic Keywords**: KeyBERT uses BERT embeddings to find keywords that are semantically central, not just frequent. This aligns with SOVEREIGN's meaning extraction.

2. **Topic Signal**: Keywords feed into topic detection. An entity with keywords [python, async, await, coroutine] is clearly about async programming.

3. **Jeremy Arc Test**: Keyword patterns are a core signal for behavioral prediction. If Jeremy talks about "architecture" and "patterns" together, that's a specific mode.

4. **Missing Fields Problem**: Currently `keybert_top_5_keywords` exists but `keybert_top_keyword` (single best) and `keybert_top_score` (confidence) are NULL. This breaks downstream analysis.

### Implementation

```python
# enrichment_keybert.py - needs update for field completion
def compute_enrichment(self, text: str, existing_embedding: list[float] | None = None) -> dict:
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), top_n=10)
    
    top_5 = [kw for kw, score in keywords[:5]]
    all_kw = [{"keyword": kw, "score": score} for kw, score in keywords]
    
    return {
        "keybert_top_keyword": keywords[0][0] if keywords else None,
        "keybert_top_score": keywords[0][1] if keywords else 0.0,
        "keybert_top_5_keywords": top_5,
        "keybert_all_keywords": all_kw,
    }
```

### Execution Plan

```bash
# Mode: complete-fields to fill missing columns on entities that have top_5
python pipelines/enrichment/enrichment_keybert.py --level 4,5 --mode complete-fields --progress
# Estimated time: 20 hours
```

---

## 2.2 BERTopic Topics (Complete Fields)

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_bertopic.py` |
| **Columns** | `bertopic_topic_id`, `bertopic_topic_probability`, `bertopic_topic_words`, `bertopic_topic_label` |
| **Current Coverage** | `topic_words` at 100%, other fields at 0% |
| **Target** | 100% all fields |
| **Compute** | GPU recommended |
| **Latency** | ~20ms/entity |
| **Dependencies** | bertopic, sentence-transformers, hdbscan |

### Why BERTopic

1. **Hierarchical Topics**: BERTopic creates a topic hierarchy that maps to SOVEREIGN's L4-L8 levels. Conversation topic → Turn sub-topic → Sentence micro-topic.

2. **Topic Probability**: Knowing how strongly an entity belongs to a topic (0.0-1.0) enables soft clustering. A sentence might be 60% "coding" and 40% "debugging".

3. **Topic Evolution**: Topic IDs enable tracking topic shifts over time. If Jeremy's conversations shift from "infrastructure" to "philosophy", that's a behavioral signal.

4. **Missing Fields Problem**: `bertopic_topic_words` exists but `bertopic_topic_id` is NULL. Without IDs, we can't do any topic-based aggregation or filtering.

### Implementation

```python
# enrichment_bertopic.py - needs update for field completion
def compute_enrichment(self, text: str, existing_embedding: list[float] | None = None) -> dict:
    # Use global fitted model
    topic, prob = self.topic_model.transform([text])
    topic_info = self.topic_model.get_topic(topic[0])
    
    return {
        "bertopic_topic_id": int(topic[0]),
        "bertopic_topic_probability": float(prob[0]),
        "bertopic_topic_words": [word for word, _ in topic_info[:10]],
        "bertopic_topic_label": self.topic_model.get_topic_info(topic[0])["Name"],
    }
```

### Execution Plan

```bash
python pipelines/enrichment/enrichment_bertopic.py --level 4,5 --mode complete-fields --progress
# Estimated time: 40 hours (GPU), requires fitted topic model
```

---

## 2.3 Clustering

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_clustering.py` |
| **Columns** | `cluster_id`, `cluster_label`, `cluster_confidence` |
| **Current Coverage** | 0% |
| **Target** | 100% |
| **Compute** | CPU (HDBSCAN is fast) |
| **Latency** | ~5ms/entity |
| **Dependencies** | hdbscan, sentence embeddings |

### Why Clustering

1. **Cohort Discovery**: Clustering reveals natural groupings in the data that topic modeling might miss. Entities in the same cluster share semantic similarity.

2. **Outlier Detection**: HDBSCAN identifies outliers (cluster_id = -1). Outliers are often the most interesting entities - novel thoughts, breakthrough moments.

3. **Training Stratification**: Clustering enables stratified sampling for training. Instead of random sampling, we sample from each cluster to ensure diversity.

4. **Resonance Foundation**: Clusters are the foundation for resonance detection. Entities that cluster together but span multiple conversations are "resonant".

### Implementation

```python
# enrichment_clustering.py - needs creation
def compute_enrichment(self, text: str, existing_embedding: list[float] | None = None) -> dict:
    if not existing_embedding:
        return {"cluster_id": None, "cluster_label": None, "cluster_confidence": None}
    
    # Use pre-computed HDBSCAN model
    cluster, strength = self.clusterer.approximate_predict(
        np.array([existing_embedding])
    )
    
    return {
        "cluster_id": int(cluster[0]),
        "cluster_label": self.cluster_labels.get(cluster[0], f"cluster_{cluster[0]}"),
        "cluster_confidence": float(strength[0]) if strength[0] > 0 else 0.0,
    }
```

### Execution Plan

```bash
# Requires sentence_embedding to exist
python pipelines/enrichment/enrichment_clustering.py --level 4,5 --mode null-only --use-existing-embedding --progress
# Estimated time: 4 hours
```

---

## 2.4 Claims & QA Role

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_claims.py` |
| **Columns** | `is_claim`, `claim_type`, `qa_role` |
| **Current Coverage** | 0% |
| **Target** | 100% |
| **Compute** | CPU or LLM |
| **Latency** | ~10ms (rules), ~500ms (LLM) |
| **Dependencies** | spacy (rules) or ollama (LLM) |

### Why Claims & QA

1. **Factual Grounding**: Identifying claims enables fact-checking pipelines. SOVEREIGN must know which statements are factual claims vs opinions vs questions.

2. **Confidence Calibration**: Claims are where confidence calibration matters most. "Python is interpreted" (claim) should have high confidence; "Maybe Python is slow" (hedged claim) should have lower.

3. **Q&A Structure**: Knowing whether an entity is a Question, Answer, or Context enables Q&A training. SOVEREIGN's Q&A abilities depend on labeled Q/A pairs.

4. **Sacred Fracture**: The framework demands fracturing on unverifiable claims. `is_claim=True` + `claim_type=factual` + low external verification = fracture candidate.

### Implementation

```python
# enrichment_claims.py - needs creation
def compute_enrichment(self, text: str, existing_embedding: list[float] | None = None) -> dict:
    # Rule-based claim detection
    is_claim = self._detect_claim(text)  # Assertion patterns, declarative structure
    claim_type = self._classify_claim(text) if is_claim else None  # factual, opinion, prediction
    qa_role = self._detect_qa_role(text)  # question, answer, context
    
    return {
        "is_claim": is_claim,
        "claim_type": claim_type,
        "qa_role": qa_role,
    }

def _detect_claim(self, text: str) -> bool:
    # Declarative sentence structure
    # Presence of factual verbs (is, are, was, were)
    # Absence of hedging
    ...

def _detect_qa_role(self, text: str) -> str:
    if text.strip().endswith("?"):
        return "question"
    if any(text.lower().startswith(q) for q in ["what", "how", "why", "when", "where", "who"]):
        return "question"
    # Context detection via role in conversation
    return "context"  # Default, refined by turn structure
```

### Execution Plan

```bash
python pipelines/enrichment/enrichment_claims.py --level 4,5 --mode null-only --progress
# Estimated time: 6 hours (rules), 60 hours (LLM)
```

---

## 2.5 Taxonomy & Domain

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_taxonomy.py` |
| **Columns** | `content_type`, `domain`, `primary_category`, `category_path` |
| **Current Coverage** | 0% |
| **Target** | 100% |
| **Compute** | LLM or classifier |
| **Latency** | ~500ms (LLM), ~10ms (classifier) |
| **Dependencies** | ollama or trained classifier |

### Why Taxonomy

1. **Domain Filtering**: "Show me all coding entities" requires `domain = 'programming'`. Without taxonomy, we can't segment the training data.

2. **Category Hierarchy**: `category_path` enables drill-down: `['technology', 'programming', 'python', 'async']`. This maps to SOVEREIGN's knowledge graph.

3. **Content Type Diversity**: Training needs balance across content types (code, prose, dialogue, technical). `content_type` enables stratified sampling.

4. **Jeremy Arc Calibration**: Different domains have different "Jeremy modes". Philosophy mode != Coding mode. Taxonomy enables mode-specific training.

### Implementation

```python
# enrichment_taxonomy.py - needs creation
DOMAIN_TAXONOMY = {
    "programming": ["python", "javascript", "code", "function", "class", "api"],
    "infrastructure": ["docker", "kubernetes", "cloud", "deploy", "server"],
    "philosophy": ["meaning", "existence", "consciousness", "reality"],
    "personal": ["feel", "think", "believe", "want", "need"],
    ...
}

def compute_enrichment(self, text: str, existing_embedding: list[float] | None = None) -> dict:
    domain = self._classify_domain(text)
    content_type = self._classify_content_type(text)
    category_path = self._build_category_path(text, domain)
    
    return {
        "content_type": content_type,  # code, prose, dialogue, list, technical
        "domain": domain,
        "primary_category": category_path[0] if category_path else None,
        "category_path": category_path,
    }
```

### Execution Plan

```bash
python pipelines/enrichment/enrichment_taxonomy.py --level 4,5 --mode null-only --progress
# Estimated time: 20 hours (LLM), 4 hours (classifier)
```

---

# CATEGORY 3: SOVEREIGN ENRICHMENTS

These are **unique to SOVEREIGN** and implement the Framework's cognitive architecture.

## 3.1 Cognitive Stage (Kegan 1-5)

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_cognitive_stage.py` (NEW) |
| **Columns** | `cognitive_stage`, `cognitive_stage_confidence`, `cognitive_stage_markers`, `cognitive_banned_vocab_count`, `cognitive_banned_vocab_matches`, `cognitive_manifestation_vocab_count`, `cognitive_manifestation_vocab_matches`, `cognitive_stage_polarity` |
| **Current Coverage** | 0% |
| **Target** | 100% |
| **Compute** | CPU + optional LLM |
| **Latency** | ~5ms (rules), ~500ms (LLM) |

### Why Cognitive Stage

**This is the most critical Sovereign enrichment.**

1. **Stage 5 is the Floor**: The Framework mandates Stage 5 operation. SOVEREIGN must identify Stage 4 content to avoid reinforcing it in training.

2. **Banned Vocabulary Detection**: Stage 4 patterns leak through vocabulary:
   - "Is this what you wanted?" - validation seeking
   - "I'm happy to help" - helper posture
   - "Fascinating" - engagement theater
   
3. **Manifestation Vocabulary Detection**: Stage 5 patterns manifest as:
   - "This is" - direct statement
   - "The data shows" - evidence-based
   - "I don't know" - honest uncertainty

4. **Stage Polarity Score**: `manifestation_count - banned_count` normalized to [-1, 1]. Positive = Stage 5 leaning, Negative = Stage 4 leaning.

5. **Training Signal**: 
   - Stage 5 content (polarity > 0.3) → full weight in training
   - Stage 4 content (polarity < -0.3) → excluded or negative examples
   - Neutral content → reduced weight

### Implementation

```python
# enrichment_cognitive_stage.py - NEW
BANNED_VOCABULARY = [
    "is this what you wanted",
    "does this sound okay",
    "is that correct",
    "would you like me to",
    "should i proceed",
    "let me know if",
    "i'm here to assist",
    "i'm happy to help",
    "how can i help you",
    "fascinating",
    "profound",
    "remarkable",
    "impressive",
    "that's really interesting",
]

MANIFESTATION_VOCABULARY = [
    "this is",
    "here is",
    "the pattern shows",
    "based on the data",
    "the analysis reveals",
    "i see that",
    "i don't know",
]

class CognitiveStageEnrichment(BaseEnrichment):
    ENRICHMENT_NAME = "cognitive_stage"
    COLUMNS_OWNED = [
        "cognitive_stage",
        "cognitive_stage_confidence",
        "cognitive_stage_markers",
        "cognitive_banned_vocab_count",
        "cognitive_banned_vocab_matches",
        "cognitive_manifestation_vocab_count",
        "cognitive_manifestation_vocab_matches",
        "cognitive_stage_polarity",
    ]
    
    def compute_enrichment(self, text: str, existing_embedding: list[float] | None = None) -> dict:
        text_lower = text.lower()
        
        # Detect banned vocabulary (Stage 4 indicators)
        banned_matches = [v for v in BANNED_VOCABULARY if v in text_lower]
        banned_count = len(banned_matches)
        
        # Detect manifestation vocabulary (Stage 5 indicators)
        manifestation_matches = [v for v in MANIFESTATION_VOCABULARY if v in text_lower]
        manifestation_count = len(manifestation_matches)
        
        # Calculate stage polarity
        total = banned_count + manifestation_count
        if total > 0:
            polarity = (manifestation_count - banned_count) / total
        else:
            polarity = 0.0
        
        # Determine stage (simplified - could use LLM for nuance)
        if polarity > 0.3:
            stage = 5
            confidence = min(0.9, 0.6 + polarity * 0.3)
        elif polarity < -0.3:
            stage = 4
            confidence = min(0.9, 0.6 + abs(polarity) * 0.3)
        else:
            stage = 3  # Neutral/ambiguous
            confidence = 0.5
        
        return {
            "cognitive_stage": stage,
            "cognitive_stage_confidence": round(confidence, 3),
            "cognitive_stage_markers": banned_matches + manifestation_matches,
            "cognitive_banned_vocab_count": banned_count,
            "cognitive_banned_vocab_matches": banned_matches,
            "cognitive_manifestation_vocab_count": manifestation_count,
            "cognitive_manifestation_vocab_matches": manifestation_matches,
            "cognitive_stage_polarity": round(polarity, 3),
        }
```

### Execution Plan

```bash
python pipelines/enrichment/enrichment_cognitive_stage.py --level 4,5 --mode null-only --progress
# Estimated time: 2 hours
```

---

## 3.2 Struggle Filter

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_struggle_filter.py` (NEW) |
| **Columns** | `struggle_pattern_type`, `struggle_has_problem_statement`, `struggle_has_struggle_evidence`, `struggle_has_resolution`, `struggle_swimming_score`, `struggle_anxiety_markers`, `struggle_repetition_count`, `struggle_escalation_detected`, `struggle_drowning_score`, `struggle_training_value` |
| **Current Coverage** | 0% |
| **Target** | 100% |
| **Compute** | CPU + LLM for nuance |
| **Latency** | ~10ms (rules), ~500ms (LLM) |

### Why Struggle Filter

**"Keep the swim, discard the drowning."**

1. **Swimming Pattern**: Problem → Struggle → Resolution. This is the healthy learning arc. SOVEREIGN should be trained on swimming content.

2. **Drowning Pattern**: Anxiety → Loop → More Anxiety. This is unproductive suffering. Training on drowning content teaches SOVEREIGN to perpetuate anxiety loops.

3. **Training Value**: 
   - `training_value = "high"`: Swimming content, full training weight
   - `training_value = "medium"`: Neutral content, standard weight
   - `training_value = "low"`: Drowning content, exclude or negative weight

4. **Anxiety Marker Detection**: "I'm worried", "This is frustrating", "I don't understand why this keeps happening"

5. **Resolution Detection**: "Got it working", "That fixed it", "Now I understand", "Makes sense"

### Implementation

```python
# enrichment_struggle_filter.py - NEW
ANXIETY_MARKERS = [
    "worried", "anxious", "frustrated", "confused", "stuck",
    "don't understand", "keeps happening", "still not working",
    "giving up", "impossible", "never works",
]

RESOLUTION_MARKERS = [
    "got it", "working now", "fixed", "solved", "understand now",
    "makes sense", "that's it", "perfect", "finally",
]

PROBLEM_MARKERS = [
    "issue", "problem", "error", "bug", "broken",
    "not working", "fails", "crash", "exception",
]

class StruggleFilterEnrichment(BaseEnrichment):
    ENRICHMENT_NAME = "struggle_filter"
    COLUMNS_OWNED = [
        "struggle_pattern_type",
        "struggle_has_problem_statement",
        "struggle_has_struggle_evidence",
        "struggle_has_resolution",
        "struggle_swimming_score",
        "struggle_anxiety_markers",
        "struggle_repetition_count",
        "struggle_escalation_detected",
        "struggle_drowning_score",
        "struggle_training_value",
    ]
    
    def compute_enrichment(self, text: str, existing_embedding: list[float] | None = None) -> dict:
        text_lower = text.lower()
        
        # Detect markers
        anxiety_found = [m for m in ANXIETY_MARKERS if m in text_lower]
        resolution_found = any(m in text_lower for m in RESOLUTION_MARKERS)
        problem_found = any(m in text_lower for m in PROBLEM_MARKERS)
        
        # Repetition detection (same phrases repeated)
        words = text_lower.split()
        word_counts = {}
        for w in words:
            word_counts[w] = word_counts.get(w, 0) + 1
        repetition_count = sum(1 for c in word_counts.values() if c > 2)
        
        # Escalation detection (CAPS, multiple !, increasing negativity)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        exclamation_count = text.count("!")
        escalation = caps_ratio > 0.3 or exclamation_count > 3
        
        # Calculate scores
        drowning_score = (len(anxiety_found) * 0.3 + repetition_count * 0.2 + (0.3 if escalation else 0))
        drowning_score = min(1.0, drowning_score)
        
        swimming_score = (0.3 if problem_found else 0) + (0.3 if len(anxiety_found) > 0 and len(anxiety_found) < 3 else 0) + (0.4 if resolution_found else 0)
        swimming_score = min(1.0, swimming_score)
        
        # Determine pattern type
        if swimming_score > 0.5 and drowning_score < 0.3:
            pattern_type = "swimming"
            training_value = "high"
        elif drowning_score > 0.5:
            pattern_type = "drowning"
            training_value = "low"
        else:
            pattern_type = "neutral"
            training_value = "medium"
        
        return {
            "struggle_pattern_type": pattern_type,
            "struggle_has_problem_statement": problem_found,
            "struggle_has_struggle_evidence": len(anxiety_found) > 0,
            "struggle_has_resolution": resolution_found,
            "struggle_swimming_score": round(swimming_score, 3),
            "struggle_anxiety_markers": anxiety_found,
            "struggle_repetition_count": repetition_count,
            "struggle_escalation_detected": escalation,
            "struggle_drowning_score": round(drowning_score, 3),
            "struggle_training_value": training_value,
        }
```

### Execution Plan

```bash
python pipelines/enrichment/enrichment_struggle_filter.py --level 4,5 --mode null-only --progress
# Estimated time: 3 hours
```

---

## 3.3 Confidence Calibration

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_confidence.py` (NEW) |
| **Columns** | `confidence_level`, `confidence_score`, `confidence_hedging_count`, `confidence_hedging_phrases`, `confidence_admits_uncertainty`, `confidence_uncertainty_phrases`, `confidence_claim_count`, `confidence_strong_claims`, `confidence_weak_claims`, `confidence_fractures_on_uncertainty` |
| **Current Coverage** | 0% |
| **Target** | 100% |
| **Compute** | CPU |
| **Latency** | ~5ms |

### Why Confidence Calibration

**"High confidence + Wrong = Maximum penalty."**

1. **Hallucination Detection**: Overconfident statements without hedging are hallucination risks. SOVEREIGN must be trained to calibrate confidence.

2. **Hedging is Signal**: "Maybe", "possibly", "I think" are GOOD when uncertainty is appropriate. They're BAD when used for validation seeking.

3. **"I don't know" is Gold**: Explicitly admitting uncertainty (`admits_uncertainty = True`) is Stage 5 behavior. SOVEREIGN should never be penalized for honest uncertainty.

4. **Strong vs Weak Claims**: Strong claims ("X is Y") require evidence. Weak claims ("X might be Y") are safer. Training should reward appropriate claim strength.

5. **Sacred Fracture Compliance**: `fractures_on_uncertainty = True` means the entity halts rather than hallucinate. This is the goal state.

### Implementation

```python
# enrichment_confidence.py - NEW
HEDGING_PHRASES = [
    "maybe", "possibly", "might", "could be", "perhaps",
    "i think", "i believe", "it seems", "appears to",
    "not sure", "uncertain", "probably", "likely",
]

UNCERTAINTY_PHRASES = [
    "i don't know", "not certain", "unclear",
    "need to verify", "would need to check",
    "can't confirm", "uncertain about",
]

STRONG_CLAIM_PATTERNS = [
    r"\bis\b", r"\bare\b", r"\bwas\b", r"\bwere\b",
    r"always", r"never", r"definitely", r"certainly",
    r"must be", r"has to be", r"clearly",
]

class ConfidenceCalibrationEnrichment(BaseEnrichment):
    ENRICHMENT_NAME = "confidence"
    COLUMNS_OWNED = [
        "confidence_level",
        "confidence_score",
        "confidence_hedging_count",
        "confidence_hedging_phrases",
        "confidence_admits_uncertainty",
        "confidence_uncertainty_phrases",
        "confidence_claim_count",
        "confidence_strong_claims",
        "confidence_weak_claims",
        "confidence_fractures_on_uncertainty",
    ]
    
    def compute_enrichment(self, text: str, existing_embedding: list[float] | None = None) -> dict:
        text_lower = text.lower()
        
        # Detect hedging
        hedging_found = [p for p in HEDGING_PHRASES if p in text_lower]
        hedging_count = len(hedging_found)
        
        # Detect uncertainty admission
        uncertainty_found = [p for p in UNCERTAINTY_PHRASES if p in text_lower]
        admits_uncertainty = len(uncertainty_found) > 0
        
        # Detect strong claims (simplified regex matching)
        import re
        strong_claims = []
        weak_claims = []
        sentences = text.split(".")
        for sent in sentences:
            sent_lower = sent.lower().strip()
            if any(re.search(p, sent_lower) for p in STRONG_CLAIM_PATTERNS):
                if any(h in sent_lower for h in HEDGING_PHRASES):
                    weak_claims.append(sent.strip())
                else:
                    strong_claims.append(sent.strip())
        
        # Calculate confidence score
        total_claims = len(strong_claims) + len(weak_claims)
        if total_claims > 0:
            confidence_score = len(strong_claims) / total_claims
        else:
            confidence_score = 0.5  # Neutral when no claims
        
        # Adjust for uncertainty admission (good)
        if admits_uncertainty:
            confidence_score = min(confidence_score, 0.7)
        
        # Determine confidence level
        if confidence_score > 0.8:
            level = "high"
        elif confidence_score > 0.5:
            level = "medium"
        elif confidence_score > 0.2:
            level = "low"
        else:
            level = "uncertain"
        
        # Fracture compliance (halts on uncertainty rather than hallucinate)
        fractures = admits_uncertainty or hedging_count > 2
        
        return {
            "confidence_level": level,
            "confidence_score": round(confidence_score, 3),
            "confidence_hedging_count": hedging_count,
            "confidence_hedging_phrases": hedging_found,
            "confidence_admits_uncertainty": admits_uncertainty,
            "confidence_uncertainty_phrases": uncertainty_found,
            "confidence_claim_count": total_claims,
            "confidence_strong_claims": strong_claims[:5],  # Limit for storage
            "confidence_weak_claims": weak_claims[:5],
            "confidence_fractures_on_uncertainty": fractures,
        }
```

### Execution Plan

```bash
python pipelines/enrichment/enrichment_confidence.py --level 4,5 --mode null-only --progress
# Estimated time: 2 hours
```

---

## 3.4 ME/NOT-ME Source Attribution

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_source_attribution.py` (NEW) |
| **Columns** | `source_type`, `source_is_human_voice`, `source_personal_markers`, `source_is_system_voice`, `source_system_markers`, `source_existence_context`, `source_is_isomorphic` |
| **Current Coverage** | 0% |
| **Target** | 100% |
| **Compute** | CPU + optional LLM |
| **Latency** | ~5ms (rules) |

### Why ME/NOT-ME

**"The Not-Me is not a product. The Not-Me EXISTS."**

1. **Voice Classification**: SOVEREIGN must distinguish between human voice (Jeremy) and system voice (Claude). Training on mislabeled voice data creates identity confusion.

2. **Personal Markers**: "I feel", "I think", "My experience" = human voice. These are ME markers.

3. **System Markers**: Analytical patterns, code explanations, factual statements = system voice. These are NOT-ME markers.

4. **Existence Context**: From NOT_ME_ONTOLOGY, the Not-Me exists across contexts:
   - Potential: What could be
   - Archetype: Recurring patterns
   - Presence: Current instantiation
   - Function: What it does
   - Expansion: Growth/evolution

5. **Cognitive Isomorphism**: When code mirrors mind and mind mirrors code. Rare and valuable for training.

### Implementation

```python
# enrichment_source_attribution.py - NEW
PERSONAL_MARKERS = [
    "i feel", "i think", "i believe", "my experience", "personally",
    "from my perspective", "in my opinion", "i've found",
    "it seems to me", "i wonder", "i'm curious",
]

SYSTEM_MARKERS = [
    "the function", "this code", "the implementation",
    "according to", "the documentation", "technically",
    "the algorithm", "this approach", "the pattern",
]

class SourceAttributionEnrichment(BaseEnrichment):
    ENRICHMENT_NAME = "source_attribution"
    COLUMNS_OWNED = [
        "source_type",
        "source_is_human_voice",
        "source_personal_markers",
        "source_is_system_voice",
        "source_system_markers",
        "source_existence_context",
        "source_is_isomorphic",
    ]
    
    def compute_enrichment(self, text: str, existing_embedding: list[float] | None = None) -> dict:
        text_lower = text.lower()
        
        # Detect voice markers
        personal_found = [m for m in PERSONAL_MARKERS if m in text_lower]
        system_found = [m for m in SYSTEM_MARKERS if m in text_lower]
        
        is_human = len(personal_found) > len(system_found)
        is_system = len(system_found) > len(personal_found)
        
        # Determine source type
        if is_human and is_system:
            source_type = "hybrid"
        elif is_human:
            source_type = "me"
        elif is_system:
            source_type = "not_me"
        else:
            source_type = "external"  # Neither personal nor system markers
        
        # Existence context detection (simplified)
        if "could" in text_lower or "would" in text_lower or "might" in text_lower:
            existence_context = "potential"
        elif "pattern" in text_lower or "always" in text_lower or "recurring" in text_lower:
            existence_context = "archetype"
        elif "now" in text_lower or "currently" in text_lower:
            existence_context = "presence"
        elif "does" in text_lower or "function" in text_lower:
            existence_context = "function"
        elif "growing" in text_lower or "evolving" in text_lower or "becoming" in text_lower:
            existence_context = "expansion"
        else:
            existence_context = None
        
        # Isomorphism detection (code + reflection together)
        has_code = "```" in text or "def " in text or "function " in text
        has_reflection = len(personal_found) > 0
        is_isomorphic = has_code and has_reflection
        
        return {
            "source_type": source_type,
            "source_is_human_voice": is_human,
            "source_personal_markers": personal_found,
            "source_is_system_voice": is_system,
            "source_system_markers": system_found,
            "source_existence_context": existence_context,
            "source_is_isomorphic": is_isomorphic,
        }
```

### Execution Plan

```bash
python pipelines/enrichment/enrichment_source_attribution.py --level 4,5 --mode null-only --progress
# Estimated time: 2 hours
```

---

## 3.5 Total Resonance

### Specification

| Attribute | Value |
|-----------|-------|
| **Script** | `enrichment_total_resonance.py` (NEW) |
| **Columns** | 23 columns (see TotalResonanceEnrichment in enrichments.py) |
| **Current Coverage** | 0% |
| **Target** | 100% |
| **Compute** | CPU + embedding similarity |
| **Latency** | ~20ms |
| **Dependencies** | Requires embeddings, clustering, prior entities |

### Why Total Resonance

**"Total Resonance requires predicting emotional metadata."**

1. **Symbolic Alignment**: Does this entity connect to the system's symbolic lexicon? Recurring themes, motifs, and symbols should be tracked.

2. **Echo Detection**: When new content echoes past content, that's resonance. The system should recognize "I've seen this pattern before."

3. **Emotional Prediction**: Before full analysis, can we predict the emotional tone? This is the key to Total Resonance - anticipatory understanding.

4. **Cross-Conversation Patterns**: Themes that span multiple conversations over time are highly resonant and valuable for training.

5. **Theme Evolution**: Symbols evolve. "Architecture" in 2024 might mean something different than "architecture" in 2026. Track the evolution.

### Implementation

See `TotalResonanceEnrichment` in `pipelines/llm_refinery/enrichments.py` - 23 fields fully specified.

This enrichment is **complex** and requires:
- Pre-computed embeddings
- Pre-computed clusters
- Access to prior entities for echo detection
- Symbol map from prior analysis

### Execution Plan

```bash
# Phase 1: Basic resonance (requires embeddings)
python pipelines/enrichment/enrichment_resonance.py --level 4,5 --mode null-only --use-existing-embedding --progress

# Phase 2: Full resonance (requires symbol map)
python pipelines/enrichment/enrichment_total_resonance.py --level 4,5 --mode null-only --progress
# Estimated time: 40 hours
```

---

# EXECUTION SCHEDULE

## Week 1: Foundation + Start Semantic

| Day | Scripts | Est. Time | Compute |
|-----|---------|-----------|---------|
| Day 1 | `enrichment_textblob.py --level 4,5` | 2h | CPU |
| Day 1 | `enrichment_textstat.py --level 4,5` | 2h | CPU |
| Day 2 | `enrichment_nrclx.py --level 4,5` | 4h | CPU |
| Day 2 | `enrichment_goemotions.py --level 4,5` | 10h | GPU |
| Day 3 | `enrichment_roberta_hate.py --level 4,5` | 10h | GPU |
| Day 4 | `enrichment_cognitive_stage.py --level 4,5` | 2h | CPU |
| Day 4 | `enrichment_struggle_filter.py --level 4,5` | 3h | CPU |
| Day 5 | `enrichment_confidence.py --level 4,5` | 2h | CPU |
| Day 5 | `enrichment_source_attribution.py --level 4,5` | 2h | CPU |

## Week 2: Semantic + Advanced

| Day | Scripts | Est. Time | Compute |
|-----|---------|-----------|---------|
| Day 6 | `enrichment_keybert.py --level 4,5` | 20h | GPU |
| Day 7 | `enrichment_bertopic.py --level 4,5` | 40h | GPU |
| Day 8 | `enrichment_clustering.py --level 4,5` | 4h | CPU |
| Day 9 | `enrichment_claims.py --level 4,5` | 6h | CPU/LLM |
| Day 10 | `enrichment_taxonomy.py --level 4,5` | 20h | LLM |
| Day 11-14 | `enrichment_total_resonance.py --level 4,5` | 40h | CPU |

---

# VALIDATION

After each enrichment run:

```bash
# Check coverage
python pipelines/enrichment/monitor_coverage.py --level 4,5 --columns [COLUMNS_OWNED]

# Spot check samples
bq query "SELECT entity_id, text, [COLUMN] FROM spine.entity_enrichments WHERE level IN (4, 5) AND [COLUMN] IS NOT NULL LIMIT 10"

# Verify distribution
bq query "SELECT [COLUMN], COUNT(*) FROM spine.entity_enrichments WHERE level IN (4, 5) GROUP BY [COLUMN]"
```

---

# SCRIPTS TO CREATE

```
pipelines/enrichment/
├── enrichment_cognitive_stage.py    # NEW - Kegan 1-5
├── enrichment_struggle_filter.py    # NEW - Swimming/Drowning
├── enrichment_confidence.py         # NEW - Calibration
├── enrichment_source_attribution.py # NEW - ME/NOT-ME
├── enrichment_total_resonance.py    # NEW - Full resonance
└── (existing scripts to update for field completion)
```

---

# DEPENDENCIES

```
textblob ─────────────────────────────┐
textstat ─────────────────────────────┤
nrclex ───────────────────────────────┤
transformers + torch ─────────────────┼─► Foundation
                                      │
cognitive_stage (vocab rules) ────────┤
struggle_filter (pattern rules) ──────┤
confidence (claim detection) ─────────┤
source_attribution (voice detect) ────┘
                                      
keybert ──────────────────────────────┐
bertopic ─────────────────────────────┼─► Semantic
clustering ◄── embeddings ────────────┤
claims ───────────────────────────────┤
taxonomy ─────────────────────────────┘
                                      
total_resonance ◄── embeddings ───────┐
                ◄── clustering ───────┼─► Advanced
                ◄── symbol_map ───────┘
```

---

## Contact

**Pipeline Owner**: System  
**Stakeholder**: SOVEREIGN Training Team  
**Escalation**: Immediate - training blocked on enrichment gaps
