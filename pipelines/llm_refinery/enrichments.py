"""Enrichment models extending entity_unified to entity_enrichments and entity_embeddings schemas.

This module provides models that generate output compatible with:
- entity_unified (34 fields) - base entity storage
- entity_enrichments (139 fields) - enriched entity data with Sovereign Architecture
- entity_embeddings (6 task-specific vectors) - 3072-dim embeddings per entity

The enrichments include:
- Sentiment analysis (TextBlob-compatible)
- Emotion detection (NRCLex, GoEmotions-compatible)
- Readability metrics (TextStat-compatible)
- Keywords (KeyBERT-compatible)
- Topics (BERTopic-compatible)
- Content classification
- **Cognitive Stage tracking (Kegan 1-5)** - Golden Record requirement
- **Struggle Filter metrics** - "Keep swim, discard drowning"
- **TRUTH:MEANING:CARE metabolic tracking** - Furnace protocol
- **Stage 5 behavioral markers** - Banned/Manifestation vocabulary
- **Confidence calibration** - Hallucination detection signals
- **ME/NOT-ME attribution** - Source classification
- **Temporal lens** - Past/Present/Future orientation
- **Total Resonance** - Symbolic/emotional pattern alignment

Entity Embeddings (6 task-specific 3072-dim vectors):
- embedding_retrieval: RETRIEVAL_DOCUMENT - optimized for document search
- embedding_query: RETRIEVAL_QUERY - optimized for query matching
- embedding_similarity: SEMANTIC_SIMILARITY - semantic comparison
- embedding_clustering: CLUSTERING - grouping similar content
- embedding_classification: CLASSIFICATION - categorization tasks
- embedding_qa: QUESTION_ANSWERING - QA context matching

Embedding Levels: L4 (sentences), L5 (messages), L8 (conversations)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


# =============================================================================
# Stage 5 Cognitive Detection - From Golden Record
# =============================================================================

BANNED_VOCABULARY = [
    # Validation seeking (Stage 4)
    "is this what you wanted",
    "does this sound okay",
    "is that correct",
    "would you like me to",
    "should i proceed",
    "let me know if",
    # Helper posture (Stage 4)
    "i'm here to assist",
    "i'm happy to help",
    "how can i help you",
    # Stage 4 recursion markers
    "fascinating",
    "profound",
    "remarkable",
    "impressive",
    "that's really interesting",
]

MANIFESTATION_VOCABULARY = [
    # Stage 5 indicators
    "this is",
    "here is",
    "the pattern shows",
    "based on the data",
    "the analysis reveals",
    "i see that",
    "i don't know",  # Honest uncertainty is GOOD
]


@dataclass
class SentimentEnrichment:
    """TextBlob-compatible sentiment enrichment."""
    
    polarity: float = 0.0  # -1.0 to 1.0
    subjectivity: float = 0.5  # 0.0 (objective) to 1.0 (subjective)
    version: str = "0.18.0.post0"  # TextBlob version
    
    def to_dict(self, prefix: str = "textblob_") -> dict[str, Any]:
        return {
            f"{prefix}polarity": self.polarity,
            f"{prefix}subjectivity": self.subjectivity,
            f"{prefix}version": self.version,
        }


@dataclass
class EmotionEnrichment:
    """NRCLex and GoEmotions-compatible emotion enrichment."""
    
    # NRCLex emotions (Plutchik's wheel)
    nrclx_emotions: dict[str, float] = field(default_factory=dict)
    nrclx_top_emotion: Optional[str] = None
    nrclx_top_count: int = 0
    nrclx_version: str = "3.0.0"  # NRCLex version
    
    # GoEmotions (27 emotions + neutral)
    goemotions_scores: dict[str, float] = field(default_factory=dict)
    goemotions_primary_emotion: Optional[str] = None
    goemotions_primary_score: float = 0.0
    goemotions_top_emotions: list[str] = field(default_factory=list)
    goemotions_model: str = "monologg/bert-base-cased-goemotions-original"
    goemotions_version: str = "1.0.0"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "nrclx_emotions": self.nrclx_emotions,
            "nrclx_top_emotion": self.nrclx_top_emotion,
            "nrclx_top_count": self.nrclx_top_count,
            "nrclx_version": self.nrclx_version,
            "goemotions_scores": self.goemotions_scores,
            "goemotions_primary_emotion": self.goemotions_primary_emotion,
            "goemotions_primary_score": self.goemotions_primary_score,
            "goemotions_top_emotions": self.goemotions_top_emotions,
            "goemotions_model": self.goemotions_model,
            "goemotions_version": self.goemotions_version,
        }


@dataclass
class ReadabilityEnrichment:
    """TextStat-compatible readability metrics."""
    
    flesch_reading_ease: Optional[float] = None  # 0-100, higher = easier
    flesch_kincaid_grade: Optional[float] = None  # Grade level
    gunning_fog: Optional[float] = None  # Grade level
    smog_index: Optional[float] = None  # Grade level
    automated_readability_index: Optional[float] = None
    coleman_liau_index: Optional[float] = None
    linsear_write_formula: Optional[float] = None
    dale_chall_readability_score: Optional[float] = None
    
    # Text statistics
    difficult_words: int = 0
    syllable_count: int = 0
    lexicon_count: int = 0  # Word count
    sentence_count: int = 0
    char_count: int = 0
    version: str = "0.7.4"  # TextStat version
    
    def to_dict(self, prefix: str = "textstat_") -> dict[str, Any]:
        return {
            f"{prefix}flesch_reading_ease": self.flesch_reading_ease,
            f"{prefix}flesch_kincaid_grade": self.flesch_kincaid_grade,
            f"{prefix}gunning_fog": self.gunning_fog,
            f"{prefix}smog_index": self.smog_index,
            f"{prefix}automated_readability_index": self.automated_readability_index,
            f"{prefix}coleman_liau_index": self.coleman_liau_index,
            f"{prefix}linsear_write_formula": self.linsear_write_formula,
            f"{prefix}dale_chall_readability_score": self.dale_chall_readability_score,
            f"{prefix}difficult_words": self.difficult_words,
            f"{prefix}syllable_count": self.syllable_count,
            f"{prefix}lexicon_count": self.lexicon_count,
            f"{prefix}sentence_count": self.sentence_count,
            f"{prefix}char_count": self.char_count,
            f"{prefix}version": self.version,
        }


@dataclass
class KeywordEnrichment:
    """KeyBERT-compatible keyword enrichment."""
    
    top_keyword: Optional[str] = None
    top_score: float = 0.0
    top_5_keywords: list[str] = field(default_factory=list)
    all_keywords: list[dict[str, Any]] = field(default_factory=list)  # [{keyword, score}]
    
    def to_dict(self, prefix: str = "keybert_") -> dict[str, Any]:
        return {
            f"{prefix}top_keyword": self.top_keyword,
            f"{prefix}top_score": self.top_score,
            f"{prefix}top_5_keywords": self.top_5_keywords,
            f"{prefix}all_keywords": self.all_keywords,
        }


@dataclass
class TopicEnrichment:
    """BERTopic-compatible topic enrichment."""
    
    topic_id: Optional[int] = None
    topic_probability: float = 0.0
    topic_words: list[str] = field(default_factory=list)
    topic_label: Optional[str] = None
    
    def to_dict(self, prefix: str = "bertopic_") -> dict[str, Any]:
        return {
            f"{prefix}topic_id": self.topic_id,
            f"{prefix}topic_probability": self.topic_probability,
            f"{prefix}topic_words": self.topic_words,
            f"{prefix}topic_label": self.topic_label,
        }


@dataclass
class ContentClassification:
    """Content type and domain classification."""
    
    content_type: Optional[str] = None  # question, statement, code, etc.
    domain: Optional[str] = None  # programming, science, general, etc.
    primary_category: Optional[str] = None
    category_path: list[str] = field(default_factory=list)
    
    # Q&A role detection
    qa_role: Optional[str] = None  # question, answer, context
    
    # Claim detection
    is_claim: bool = False
    claim_type: Optional[str] = None  # factual, opinion, prediction
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "content_type": self.content_type,
            "domain": self.domain,
            "primary_category": self.primary_category,
            "category_path": self.category_path,
            "qa_role": self.qa_role,
            "is_claim": self.is_claim,
            "claim_type": self.claim_type,
        }


@dataclass
class HateSpeechEnrichment:
    """RoBERTa hate speech detection enrichment."""
    
    label: Optional[str] = None  # hate, offensive, normal
    score: float = 0.0
    
    def to_dict(self, prefix: str = "roberta_hate_") -> dict[str, Any]:
        return {
            f"{prefix}label": self.label,
            f"{prefix}score": self.score,
        }


# =============================================================================
# SOVEREIGN ARCHITECTURE ENRICHMENTS - From Framework Documents
# =============================================================================

@dataclass
class CognitiveStageEnrichment:
    """Kegan Stage (1-5) cognitive development tracking.
    
    From Golden Record: "Classify all records by cognitive stage"
    Stage 5 is the baseline for operating in The Framework - it is the floor.
    """
    
    stage: int = 3  # Kegan stage 1-5
    stage_confidence: float = 0.0  # Confidence in classification
    stage_markers: list[str] = field(default_factory=list)  # Evidence for classification
    
    # Stage 4 indicators (validation seeking, system-bound)
    banned_vocab_count: int = 0
    banned_vocab_matches: list[str] = field(default_factory=list)
    
    # Stage 5 indicators (sovereign, manifestation)
    manifestation_vocab_count: int = 0
    manifestation_vocab_matches: list[str] = field(default_factory=list)
    
    # Derived score: positive = Stage 5, negative = Stage 4
    stage_polarity: float = 0.0  # manifestation_count - banned_count normalized
    
    def to_dict(self, prefix: str = "cognitive_") -> dict[str, Any]:
        return {
            f"{prefix}stage": self.stage,
            f"{prefix}stage_confidence": self.stage_confidence,
            f"{prefix}stage_markers": self.stage_markers,
            f"{prefix}banned_vocab_count": self.banned_vocab_count,
            f"{prefix}banned_vocab_matches": self.banned_vocab_matches,
            f"{prefix}manifestation_vocab_count": self.manifestation_vocab_count,
            f"{prefix}manifestation_vocab_matches": self.manifestation_vocab_matches,
            f"{prefix}stage_polarity": self.stage_polarity,
        }


@dataclass
class StruggleFilterEnrichment:
    """Struggle Filter: Keep the swim, discard the drowning.
    
    From Golden Record: "Data refinement must prioritize resolution over suffering."
    Swimming: problem → struggle → resolution
    Drowning: anxiety → loop → more anxiety
    """
    
    pattern_type: Optional[str] = None  # "swimming" | "drowning" | "neutral"
    
    # Swimming indicators (problem-solving arc)
    has_problem_statement: bool = False
    has_struggle_evidence: bool = False
    has_resolution: bool = False
    swimming_score: float = 0.0  # 0-1, higher = better resolution arc
    
    # Drowning indicators (anxiety loops)
    anxiety_markers: list[str] = field(default_factory=list)
    repetition_count: int = 0  # Same concern repeated
    escalation_detected: bool = False  # Getting worse not better
    drowning_score: float = 0.0  # 0-1, higher = more drowning
    
    # Training value assessment
    training_value: str = "medium"  # "high" (swim), "medium" (neutral), "low" (drown)
    
    def to_dict(self, prefix: str = "struggle_") -> dict[str, Any]:
        return {
            f"{prefix}pattern_type": self.pattern_type,
            f"{prefix}has_problem_statement": self.has_problem_statement,
            f"{prefix}has_struggle_evidence": self.has_struggle_evidence,
            f"{prefix}has_resolution": self.has_resolution,
            f"{prefix}swimming_score": self.swimming_score,
            f"{prefix}anxiety_markers": self.anxiety_markers,
            f"{prefix}repetition_count": self.repetition_count,
            f"{prefix}escalation_detected": self.escalation_detected,
            f"{prefix}drowning_score": self.drowning_score,
            f"{prefix}training_value": self.training_value,
        }


@dataclass
class MetabolicStageEnrichment:
    """TRUTH:MEANING:CARE metabolic cycle tracking.
    
    From 03_METABOLISM: The Furnace transforms raw material into
    Structure, Meaning, and Care.
    """
    
    metabolic_stage: Optional[str] = None  # "truth" | "meaning" | "care_internal" | "care_external"
    
    # Truth stage (raw fuel)
    is_raw_data: bool = False
    is_crisis: bool = False
    is_friction: bool = False
    is_pain: bool = False
    
    # Meaning stage (processing/fire)
    has_pattern_recognition: bool = False
    has_structure_emergence: bool = False
    insight_level: float = 0.0  # 0-1, how much meaning extracted
    
    # Care stage (output/work)
    has_resolution: bool = False
    care_recipient: Optional[str] = None  # "self" | "other" | "system"
    care_type: Optional[str] = None  # "protective" | "constructive" | "revelatory"
    
    # Surplus value (negentropic - output > input)
    surplus_detected: bool = False
    revelation_present: bool = False
    
    def to_dict(self, prefix: str = "metabolic_") -> dict[str, Any]:
        return {
            f"{prefix}stage": self.metabolic_stage,
            f"{prefix}is_raw_data": self.is_raw_data,
            f"{prefix}is_crisis": self.is_crisis,
            f"{prefix}is_friction": self.is_friction,
            f"{prefix}is_pain": self.is_pain,
            f"{prefix}has_pattern_recognition": self.has_pattern_recognition,
            f"{prefix}has_structure_emergence": self.has_structure_emergence,
            f"{prefix}insight_level": self.insight_level,
            f"{prefix}has_resolution": self.has_resolution,
            f"{prefix}care_recipient": self.care_recipient,
            f"{prefix}care_type": self.care_type,
            f"{prefix}surplus_detected": self.surplus_detected,
            f"{prefix}revelation_present": self.revelation_present,
        }


@dataclass
class ConfidenceCalibrationEnrichment:
    """Confidence calibration for coherence anchor training.
    
    From Golden Record: "High confidence + Wrong = Maximum penalty"
    The system must HATE being factually wrong.
    """
    
    # Expressed confidence
    confidence_level: Optional[str] = None  # "high" | "medium" | "low" | "uncertain"
    confidence_score: float = 0.5  # 0-1, expressed certainty
    
    # Hedging detection
    hedging_count: int = 0  # "maybe", "possibly", "might"
    hedging_phrases: list[str] = field(default_factory=list)
    
    # Uncertainty acknowledgment (GOOD in Stage 5)
    admits_uncertainty: bool = False  # "I don't know" is healthy
    uncertainty_phrases: list[str] = field(default_factory=list)
    
    # Claim strength
    claim_count: int = 0
    strong_claims: list[str] = field(default_factory=list)  # Assertions without hedging
    weak_claims: list[str] = field(default_factory=list)  # Hedged assertions
    
    # Sacred Fracture compliance
    fractures_on_uncertainty: bool = True  # Halts rather than hallucinate
    
    def to_dict(self, prefix: str = "confidence_") -> dict[str, Any]:
        return {
            f"{prefix}level": self.confidence_level,
            f"{prefix}score": self.confidence_score,
            f"{prefix}hedging_count": self.hedging_count,
            f"{prefix}hedging_phrases": self.hedging_phrases,
            f"{prefix}admits_uncertainty": self.admits_uncertainty,
            f"{prefix}uncertainty_phrases": self.uncertainty_phrases,
            f"{prefix}claim_count": self.claim_count,
            f"{prefix}strong_claims": self.strong_claims,
            f"{prefix}weak_claims": self.weak_claims,
            f"{prefix}fractures_on_uncertainty": self.fractures_on_uncertainty,
        }


@dataclass
class SourceAttributionEnrichment:
    """ME vs NOT-ME source attribution.
    
    From 07_NOT_ME_ONTOLOGY: The Not-Me is not a product.
    The Not-Me EXISTS across contexts.
    """
    
    source_type: Optional[str] = None  # "me" | "not_me" | "external" | "hybrid"
    
    # ME indicators (human-originated)
    is_human_voice: bool = False
    personal_markers: list[str] = field(default_factory=list)  # "I feel", "I think"
    
    # NOT-ME indicators (system-originated)
    is_system_voice: bool = False
    system_markers: list[str] = field(default_factory=list)  # analytical patterns
    
    # Context of existence (from NOT_ME_ONTOLOGY)
    existence_context: Optional[str] = None  # "potential" | "archetype" | "presence" | "function" | "expansion"
    
    # Cognitive isomorphism tracking
    is_isomorphic: bool = False  # Code mirrors mind, mind mirrors code
    
    def to_dict(self, prefix: str = "source_") -> dict[str, Any]:
        return {
            f"{prefix}type": self.source_type,
            f"{prefix}is_human_voice": self.is_human_voice,
            f"{prefix}personal_markers": self.personal_markers,
            f"{prefix}is_system_voice": self.is_system_voice,
            f"{prefix}system_markers": self.system_markers,
            f"{prefix}existence_context": self.existence_context,
            f"{prefix}is_isomorphic": self.is_isomorphic,
        }


@dataclass
class TemporalLensEnrichment:
    """Temporal lens analysis from 02_PERCEPTION.
    
    Time exists in three states: PAST, PRESENT, FUTURE.
    SEE:TIME → SEE:SEE:TIME (meta-temporal awareness)
    """
    
    temporal_orientation: Optional[str] = None  # "past" | "present" | "future" | "meta"
    
    # Past markers
    past_references: list[str] = field(default_factory=list)
    nostalgia_level: float = 0.0
    
    # Present markers
    present_references: list[str] = field(default_factory=list)
    immediacy_level: float = 0.0  # "now", "currently"
    
    # Future markers
    future_references: list[str] = field(default_factory=list)
    anticipation_level: float = 0.0  # "will", "going to"
    
    # Meta-temporal (SEE:SEE:TIME)
    has_meta_temporal: bool = False  # Sees time itself as object
    
    def to_dict(self, prefix: str = "temporal_") -> dict[str, Any]:
        return {
            f"{prefix}orientation": self.temporal_orientation,
            f"{prefix}past_references": self.past_references,
            f"{prefix}nostalgia_level": self.nostalgia_level,
            f"{prefix}present_references": self.present_references,
            f"{prefix}immediacy_level": self.immediacy_level,
            f"{prefix}future_references": self.future_references,
            f"{prefix}anticipation_level": self.anticipation_level,
            f"{prefix}has_meta_temporal": self.has_meta_temporal,
        }


@dataclass
class OperationalCycleEnrichment:
    """SEE:SEE:DO:DONE operational cycle tracking.
    
    From 02_PERCEPTION: The operational cycle of awareness, action, completion.
    """
    
    cycle_phase: Optional[str] = None  # "see" | "see_see" | "do" | "see_do" | "done"
    
    # SEE phase (direct perception)
    has_observation: bool = False
    observation_markers: list[str] = field(default_factory=list)
    
    # SEE:SEE phase (meta-awareness)
    has_meta_awareness: bool = False  # "I see that I see"
    meta_markers: list[str] = field(default_factory=list)
    
    # DO phase (action)
    has_action: bool = False
    action_markers: list[str] = field(default_factory=list)
    
    # DONE phase (completion)
    has_completion: bool = False
    completion_markers: list[str] = field(default_factory=list)
    
    # Levels of sight
    sight_level: int = 1  # 1=SEE, 2=SEE:BLIND, 3=SEE:SEE
    
    def to_dict(self, prefix: str = "cycle_") -> dict[str, Any]:
        return {
            f"{prefix}phase": self.cycle_phase,
            f"{prefix}has_observation": self.has_observation,
            f"{prefix}observation_markers": self.observation_markers,
            f"{prefix}has_meta_awareness": self.has_meta_awareness,
            f"{prefix}meta_markers": self.meta_markers,
            f"{prefix}has_action": self.has_action,
            f"{prefix}action_markers": self.action_markers,
            f"{prefix}has_completion": self.has_completion,
            f"{prefix}completion_markers": self.completion_markers,
            f"{prefix}sight_level": self.sight_level,
        }


@dataclass
class JeremyArcEnrichment:
    """Jeremy Arc test metrics for Genesis training validation.
    
    From Golden Record Phase 3: "System must achieve 95% accuracy on metadata.
    Not text similarity - cognitive structure prediction."
    """
    
    # Thought type classification
    thought_type: Optional[str] = None  # "analytical" | "creative" | "emotional" | "directive" | "reflective"
    
    # Mode detection
    mode: Optional[str] = None  # "working" | "processing" | "resting" | "crisis" | "flow"
    
    # Behavioral pattern
    behavioral_pattern: Optional[str] = None  # Pattern name from corpus
    
    # Prediction confidence
    arc_prediction_confidence: float = 0.0  # How confident in Jeremy-ness
    
    # Signature markers
    signature_phrases: list[str] = field(default_factory=list)  # Jeremy-specific patterns
    
    def to_dict(self, prefix: str = "jeremy_arc_") -> dict[str, Any]:
        return {
            f"{prefix}thought_type": self.thought_type,
            f"{prefix}mode": self.mode,
            f"{prefix}behavioral_pattern": self.behavioral_pattern,
            f"{prefix}prediction_confidence": self.arc_prediction_confidence,
            f"{prefix}signature_phrases": self.signature_phrases,
        }


@dataclass
class TotalResonanceEnrichment:
    """Total Resonance tracking for symbolic and emotional pattern alignment.
    
    From SOVEREIGN_MEMORY_ARCHITECTURE:
    "Total Resonance requires predicting emotional metadata"
    
    From Symbolic Engine Protocol:
    - log_echo() captures moments of symbolic familiarity
    - bind_symbol() creates versioned entries in the symbol_map
    - scan_reverb() returns summary of active motifs
    
    Total Resonance is NOT just similarity - it's the ability to:
    1. Detect when new content resonates with the system's symbolic lexicon
    2. Predict the emotional valence before full analysis
    3. Connect to recurring themes across the entire corpus
    4. Track echo shifts as symbols evolve over time
    """
    
    # Resonance detection
    resonance_score: float = 0.0  # 0-1, how strongly this resonates with known patterns
    resonance_group_id: Optional[str] = None  # Cluster this belongs to
    resonance_strength: Optional[str] = None  # "whisper" | "notice" | "signal" | "bell"
    
    # Symbolic alignment
    symbol_matches: list[str] = field(default_factory=list)  # Matched bound symbols
    symbol_scores: dict[str, float] = field(default_factory=dict)  # symbol -> match strength
    primary_symbol: Optional[str] = None  # Strongest symbolic match
    symbol_realm: Optional[str] = None  # "guardian" | "mirror" | "unbound"
    
    # Echo detection (symbolic familiarity)
    is_echo: bool = False  # True if this echoes past content
    echo_source_id: Optional[str] = None  # Entity ID this echoes
    echo_shift_type: Optional[str] = None  # "clarity_emergence" | "symbol_inversion" | "deepening"
    echo_distance: float = 1.0  # How far from original (0=identical, 1=unrelated)
    
    # Emotional prediction (the key to Total Resonance)
    predicted_emotional_tone: Optional[str] = None  # Predicted before full analysis
    emotional_prediction_confidence: float = 0.0  # How confident in prediction
    emotional_trajectory: Optional[str] = None  # "ascending" | "stable" | "descending" | "volatile"
    
    # Motif tracking
    active_motifs: list[str] = field(default_factory=list)  # Currently active in system
    motif_valence: dict[str, float] = field(default_factory=dict)  # motif -> valence (-1 to 1)
    
    # Reverb analysis
    reverb_tier: Optional[str] = None  # "light" | "full" | "map"
    reverb_strength: float = 0.0  # 0-1, how much this reverberates
    
    # Theme evolution tracking
    theme_version: Optional[int] = None  # If part of evolving theme, which version
    theme_evolution_phase: Optional[str] = None  # "emerging" | "stable" | "transforming" | "archived"
    
    # Cross-conversation resonance
    cross_conversation_match: bool = False  # Resonates across multiple conversations
    matched_conversation_ids: list[str] = field(default_factory=list)
    temporal_span_days: Optional[int] = None  # How many days this pattern spans
    
    def to_dict(self, prefix: str = "resonance_") -> dict[str, Any]:
        return {
            f"{prefix}score": self.resonance_score,
            f"{prefix}group_id": self.resonance_group_id,
            f"{prefix}strength": self.resonance_strength,
            f"{prefix}symbol_matches": self.symbol_matches,
            f"{prefix}symbol_scores": self.symbol_scores,
            f"{prefix}primary_symbol": self.primary_symbol,
            f"{prefix}symbol_realm": self.symbol_realm,
            f"{prefix}is_echo": self.is_echo,
            f"{prefix}echo_source_id": self.echo_source_id,
            f"{prefix}echo_shift_type": self.echo_shift_type,
            f"{prefix}echo_distance": self.echo_distance,
            f"{prefix}predicted_emotional_tone": self.predicted_emotional_tone,
            f"{prefix}emotional_prediction_confidence": self.emotional_prediction_confidence,
            f"{prefix}emotional_trajectory": self.emotional_trajectory,
            f"{prefix}active_motifs": self.active_motifs,
            f"{prefix}motif_valence": self.motif_valence,
            f"{prefix}reverb_tier": self.reverb_tier,
            f"{prefix}reverb_strength": self.reverb_strength,
            f"{prefix}theme_version": self.theme_version,
            f"{prefix}theme_evolution_phase": self.theme_evolution_phase,
            f"{prefix}cross_conversation_match": self.cross_conversation_match,
            f"{prefix}matched_conversation_ids": self.matched_conversation_ids,
            f"{prefix}temporal_span_days": self.temporal_span_days,
        }


# =============================================================================
# Entity Embeddings - 6 Task-Specific Vectors
# =============================================================================
# Aligned with spine.entity_embeddings BigQuery table
# Model: gemini-embedding-001 (3072 dimensions)
# Levels: L4 (sentences), L5 (messages), L8 (conversations)
# =============================================================================

class EmbeddingTaskType(str, Enum):
    """Task types for Gemini embedding model.
    
    Each task type optimizes the embedding for specific use cases.
    See: https://ai.google.dev/gemini-api/docs/embeddings
    """
    RETRIEVAL_DOCUMENT = "RETRIEVAL_DOCUMENT"  # For indexing documents
    RETRIEVAL_QUERY = "RETRIEVAL_QUERY"        # For searching documents
    SEMANTIC_SIMILARITY = "SEMANTIC_SIMILARITY"  # For comparing text similarity
    CLUSTERING = "CLUSTERING"                   # For grouping similar content
    CLASSIFICATION = "CLASSIFICATION"           # For categorization tasks
    QUESTION_ANSWERING = "QUESTION_ANSWERING"   # For QA context matching


@dataclass
class EntityEmbedding:
    """6 task-specific embeddings for a single entity.
    
    This aligns with the spine.entity_embeddings BigQuery table schema.
    Each entity at L4 (sentence), L5 (message), or L8 (conversation) level
    gets 6 different 3072-dimensional embeddings, each optimized for a
    specific task type.
    
    Schema (from RAG_SYSTEM_ARCHITECTURE.md):
    ```sql
    CREATE TABLE spine.entity_embeddings (
        entity_id STRING NOT NULL,
        level_code STRING NOT NULL,  -- L4, L5, L8
        embedding_retrieval ARRAY<FLOAT64>,      -- RETRIEVAL_DOCUMENT
        embedding_query ARRAY<FLOAT64>,          -- RETRIEVAL_QUERY  
        embedding_similarity ARRAY<FLOAT64>,     -- SEMANTIC_SIMILARITY
        embedding_clustering ARRAY<FLOAT64>,     -- CLUSTERING
        embedding_classification ARRAY<FLOAT64>, -- CLASSIFICATION
        embedding_qa ARRAY<FLOAT64>,             -- QUESTION_ANSWERING
        embedding_model STRING,
        embedding_dimensions INT64,
        source_text_hash STRING,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );
    ```
    
    Usage Flow:
    1. Entity created in entity_unified (L2-L8 extraction)
    2. Entity enriched in entity_enrichments (139 fields)
    3. Embeddings generated post-enrichment → entity_embeddings (this class)
    """
    
    # Core identity (links to entity_unified and entity_enrichments)
    entity_id: str
    level_code: str  # L4, L5, or L8
    
    # 6 task-specific embeddings (3072-dimensional each)
    embedding_retrieval: list[float] = field(default_factory=list)  # RETRIEVAL_DOCUMENT
    embedding_query: list[float] = field(default_factory=list)      # RETRIEVAL_QUERY
    embedding_similarity: list[float] = field(default_factory=list) # SEMANTIC_SIMILARITY
    embedding_clustering: list[float] = field(default_factory=list) # CLUSTERING
    embedding_classification: list[float] = field(default_factory=list)  # CLASSIFICATION
    embedding_qa: list[float] = field(default_factory=list)         # QUESTION_ANSWERING
    
    # Metadata
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 3072
    source_text: Optional[str] = None
    source_text_hash: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        """Validate and compute derived fields."""
        # Validate level code
        if self.level_code not in ("L4", "L5", "L8"):
            raise ValueError(f"Invalid level_code: {self.level_code}. Must be L4, L5, or L8")
        
        # Compute source text hash if source text provided
        if self.source_text and not self.source_text_hash:
            self.source_text_hash = hashlib.sha256(self.source_text.encode()).hexdigest()
    
    @property
    def is_complete(self) -> bool:
        """Check if all 6 embeddings are populated with correct dimensions."""
        embeddings = [
            self.embedding_retrieval,
            self.embedding_query,
            self.embedding_similarity,
            self.embedding_clustering,
            self.embedding_classification,
            self.embedding_qa,
        ]
        return all(
            len(emb) == self.embedding_dimensions 
            for emb in embeddings
        )
    
    @property
    def populated_tasks(self) -> list[str]:
        """Return list of task types that have embeddings."""
        tasks = []
        if len(self.embedding_retrieval) == self.embedding_dimensions:
            tasks.append("RETRIEVAL_DOCUMENT")
        if len(self.embedding_query) == self.embedding_dimensions:
            tasks.append("RETRIEVAL_QUERY")
        if len(self.embedding_similarity) == self.embedding_dimensions:
            tasks.append("SEMANTIC_SIMILARITY")
        if len(self.embedding_clustering) == self.embedding_dimensions:
            tasks.append("CLUSTERING")
        if len(self.embedding_classification) == self.embedding_dimensions:
            tasks.append("CLASSIFICATION")
        if len(self.embedding_qa) == self.embedding_dimensions:
            tasks.append("QUESTION_ANSWERING")
        return tasks
    
    def set_embedding(self, task_type: EmbeddingTaskType, embedding: list[float]) -> None:
        """Set a specific task embedding with validation."""
        if len(embedding) != self.embedding_dimensions:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.embedding_dimensions}, "
                f"got {len(embedding)}"
            )
        
        match task_type:
            case EmbeddingTaskType.RETRIEVAL_DOCUMENT:
                self.embedding_retrieval = embedding
            case EmbeddingTaskType.RETRIEVAL_QUERY:
                self.embedding_query = embedding
            case EmbeddingTaskType.SEMANTIC_SIMILARITY:
                self.embedding_similarity = embedding
            case EmbeddingTaskType.CLUSTERING:
                self.embedding_clustering = embedding
            case EmbeddingTaskType.CLASSIFICATION:
                self.embedding_classification = embedding
            case EmbeddingTaskType.QUESTION_ANSWERING:
                self.embedding_qa = embedding
        
        self.updated_at = datetime.now(UTC)
    
    def to_bigquery_row(self) -> dict[str, Any]:
        """Convert to BigQuery row format for spine.entity_embeddings."""
        return {
            "entity_id": self.entity_id,
            "level_code": self.level_code,
            "embedding_retrieval": self.embedding_retrieval,
            "embedding_query": self.embedding_query,
            "embedding_similarity": self.embedding_similarity,
            "embedding_clustering": self.embedding_clustering,
            "embedding_classification": self.embedding_classification,
            "embedding_qa": self.embedding_qa,
            "embedding_model": self.embedding_model,
            "embedding_dimensions": self.embedding_dimensions,
            "source_text_hash": self.source_text_hash,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "entity_id": self.entity_id,
            "level_code": self.level_code,
            "embedding_retrieval": self.embedding_retrieval,
            "embedding_query": self.embedding_query,
            "embedding_similarity": self.embedding_similarity,
            "embedding_clustering": self.embedding_clustering,
            "embedding_classification": self.embedding_classification,
            "embedding_qa": self.embedding_qa,
            "embedding_model": self.embedding_model,
            "embedding_dimensions": self.embedding_dimensions,
            "source_text": self.source_text,
            "source_text_hash": self.source_text_hash,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_complete": self.is_complete,
            "populated_tasks": self.populated_tasks,
        }
    
    @classmethod
    def from_entity_unified(
        cls,
        entity_id: str,
        level_code: str,
        text: str,
        embedding_model: str = "gemini-embedding-001",
    ) -> "EntityEmbedding":
        """Create an EntityEmbedding from entity_unified data.
        
        Embeddings will be empty - use set_embedding() or an embedding
        generator to populate them.
        """
        return cls(
            entity_id=entity_id,
            level_code=level_code,
            source_text=text,
            embedding_model=embedding_model,
        )


@dataclass
class EmbeddingBatch:
    """A batch of entity embeddings for bulk processing.
    
    Used for efficient BigQuery inserts and API batching.
    """
    
    embeddings: list[EntityEmbedding] = field(default_factory=list)
    batch_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def add(self, embedding: EntityEmbedding) -> None:
        """Add an embedding to the batch."""
        self.embeddings.append(embedding)
    
    @property
    def count(self) -> int:
        """Number of embeddings in batch."""
        return len(self.embeddings)
    
    @property
    def complete_count(self) -> int:
        """Number of complete embeddings (all 6 vectors populated)."""
        return sum(1 for e in self.embeddings if e.is_complete)
    
    @property
    def by_level(self) -> dict[str, list[EntityEmbedding]]:
        """Group embeddings by level code."""
        result: dict[str, list[EntityEmbedding]] = {"L4": [], "L5": [], "L8": []}
        for emb in self.embeddings:
            result[emb.level_code].append(emb)
        return result
    
    def to_bigquery_rows(self) -> list[dict[str, Any]]:
        """Convert all embeddings to BigQuery row format."""
        return [e.to_bigquery_row() for e in self.embeddings]
    
    def summary(self) -> dict[str, Any]:
        """Get batch summary statistics."""
        by_level = self.by_level
        return {
            "batch_id": self.batch_id,
            "total_embeddings": self.count,
            "complete_embeddings": self.complete_count,
            "incomplete_embeddings": self.count - self.complete_count,
            "l4_count": len(by_level["L4"]),
            "l5_count": len(by_level["L5"]),
            "l8_count": len(by_level["L8"]),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class EntityEnrichment:
    """Complete enrichment bundle for an entity.
    
    Combines all enrichment types into a single structure that can
    be merged with entity_unified output to produce entity_enrichments.
    
    Includes both standard NLP enrichments AND Sovereign Architecture
    enrichments required by the Golden Record and Framework documents.
    """
    
    # Core identity (links to entity_unified)
    entity_id: str
    enrichment_text: str  # Text that was enriched
    
    # Entity linkage fields (from entity_unified)
    entity_type: Optional[str] = None  # e.g., "message", "sentence", "conversation"
    parent_id: Optional[str] = None
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    turn_id: Optional[str] = None
    sentence_id: Optional[str] = None
    span_id: Optional[str] = None
    word_id: Optional[str] = None
    topic_segment_id: Optional[str] = None
    
    # Source metadata
    source_ids: list[str] = field(default_factory=list)  # Contributing source IDs
    source_platform: Optional[str] = None  # e.g., "claude_web", "chatgpt"
    source_system: Optional[str] = None  # e.g., "conversation_export"
    source_file: Optional[str] = None  # Original filename
    source_file_path: Optional[str] = None  # Full path
    source_message_timestamp: Optional[str] = None  # Original timestamp
    
    # Entity meta
    entity_mode: Optional[str] = None  # "structural", "conceptual", "translated"
    role: Optional[str] = None  # "user", "assistant", "system"
    metadata: dict[str, Any] = field(default_factory=dict)  # Generic metadata
    
    # Clustering (populated by clustering enrichment)
    cluster_id: Optional[str] = None
    cluster_label: Optional[str] = None
    cluster_confidence: Optional[float] = None
    
    # Small embeddings for GPU enrichments (NOT for similarity search)
    sentence_embedding: Optional[list[float]] = None
    sentence_embedding_model: Optional[str] = None
    
    # Standard NLP enrichments
    sentiment: SentimentEnrichment = field(default_factory=SentimentEnrichment)
    emotion: EmotionEnrichment = field(default_factory=EmotionEnrichment)
    readability: ReadabilityEnrichment = field(default_factory=ReadabilityEnrichment)
    keywords: KeywordEnrichment = field(default_factory=KeywordEnrichment)
    topics: TopicEnrichment = field(default_factory=TopicEnrichment)
    content: ContentClassification = field(default_factory=ContentClassification)
    hate_speech: HateSpeechEnrichment = field(default_factory=HateSpeechEnrichment)
    
    # SOVEREIGN ARCHITECTURE ENRICHMENTS (Golden Record / Framework)
    cognitive_stage: CognitiveStageEnrichment = field(default_factory=CognitiveStageEnrichment)
    struggle_filter: StruggleFilterEnrichment = field(default_factory=StruggleFilterEnrichment)
    metabolic_stage: MetabolicStageEnrichment = field(default_factory=MetabolicStageEnrichment)
    confidence: ConfidenceCalibrationEnrichment = field(default_factory=ConfidenceCalibrationEnrichment)
    source_attribution: SourceAttributionEnrichment = field(default_factory=SourceAttributionEnrichment)
    temporal_lens: TemporalLensEnrichment = field(default_factory=TemporalLensEnrichment)
    operational_cycle: OperationalCycleEnrichment = field(default_factory=OperationalCycleEnrichment)
    jeremy_arc: JeremyArcEnrichment = field(default_factory=JeremyArcEnrichment)
    total_resonance: TotalResonanceEnrichment = field(default_factory=TotalResonanceEnrichment)
    
    # Enrichment metadata
    enrichment_batch_id: Optional[str] = None
    enrichment_quality_flags: list[str] = field(default_factory=list)
    enrichment_metadata: dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    enriched_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def to_entity_enrichments(self) -> dict[str, Any]:
        """Convert to entity_enrichments BigQuery schema.
        
        Returns ~150+ fields covering linkage, source, clustering, NLP, 
        and Sovereign Architecture metrics.
        """
        result = {
            # Core identity
            "entity_id": self.entity_id,
            "enrichment_text": self.enrichment_text,
            
            # Entity linkage
            "entity_type": self.entity_type,
            "parent_id": self.parent_id,
            "conversation_id": self.conversation_id,
            "message_id": self.message_id,
            "turn_id": self.turn_id,
            "sentence_id": self.sentence_id,
            "span_id": self.span_id,
            "word_id": self.word_id,
            "topic_segment_id": self.topic_segment_id,
            
            # Source metadata
            "source_ids": self.source_ids,
            "source_platform": self.source_platform,
            "source_system": self.source_system,
            "source_file": self.source_file,
            "source_file_path": self.source_file_path,
            "source_message_timestamp": self.source_message_timestamp,
            
            # Entity meta
            "entity_mode": self.entity_mode,
            "role": self.role,
            "metadata": self.metadata,
            
            # Clustering
            "cluster_id": self.cluster_id,
            "cluster_label": self.cluster_label,
            "cluster_confidence": self.cluster_confidence,
            
            # Small embeddings (for GPU enrichments only)
            "sentence_embedding": self.sentence_embedding,
            "sentence_embedding_model": self.sentence_embedding_model,
            
            # Enrichment metadata
            "enrichment_batch_id": self.enrichment_batch_id,
            "enrichment_quality_flags": self.enrichment_quality_flags,
            "enrichment_metadata": self.enrichment_metadata,
            "enriched_at": self.enriched_at.isoformat(),
        }
        
        # Standard NLP enrichments
        result.update(self.sentiment.to_dict())
        result.update(self.emotion.to_dict())
        result.update(self.readability.to_dict())
        result.update(self.keywords.to_dict())
        result.update(self.topics.to_dict())
        result.update(self.content.to_dict())
        result.update(self.hate_speech.to_dict())
        
        # SOVEREIGN ARCHITECTURE enrichments
        result.update(self.cognitive_stage.to_dict())
        result.update(self.struggle_filter.to_dict())
        result.update(self.metabolic_stage.to_dict())
        result.update(self.confidence.to_dict())
        result.update(self.source_attribution.to_dict())
        result.update(self.temporal_lens.to_dict())
        result.update(self.operational_cycle.to_dict())
        result.update(self.jeremy_arc.to_dict())
        result.update(self.total_resonance.to_dict())
        
        return result


# =============================================================================
# LLM Prompt Templates for Enrichment Extraction
# =============================================================================

ENRICHMENT_EXTRACTION_PROMPT = """Analyze this text and extract comprehensive enrichments for the Sovereign Architecture.

TEXT:
{text}

CONTEXT:
- Entity Type: {entity_type}
- Level: L{level}
- Speaker: {speaker}

Extract the following enrichments as JSON. This is for training a sovereign AI system, so cognitive stage and behavioral patterns are CRITICAL.

```json
{{
  "sentiment": {{
    "polarity": <float -1.0 to 1.0>,
    "subjectivity": <float 0.0 to 1.0>
  }},
  "emotions": {{
    "primary_emotion": "<joy|sadness|anger|fear|surprise|disgust|trust|anticipation|neutral>",
    "emotion_scores": {{
      "joy": <float 0-1>,
      "sadness": <float 0-1>,
      "anger": <float 0-1>,
      "fear": <float 0-1>,
      "surprise": <float 0-1>,
      "disgust": <float 0-1>,
      "trust": <float 0-1>,
      "anticipation": <float 0-1>
    }},
    "goemotions": ["<top 3 emotions>"]
  }},
  "readability": {{
    "complexity": "<simple|moderate|complex>",
    "estimated_grade_level": <float 1-16>,
    "difficult_word_count": <int>,
    "word_count": <int>,
    "sentence_count": <int>
  }},
  "keywords": {{
    "top_5": ["<keyword1>", "<keyword2>", "<keyword3>", "<keyword4>", "<keyword5>"],
    "key_phrases": ["<phrase1>", "<phrase2>"]
  }},
  "content": {{
    "type": "<question|statement|command|code|explanation|opinion|fact>",
    "domain": "<programming|science|business|personal|general>",
    "qa_role": "<question|answer|context|null>",
    "is_claim": <boolean>,
    "claim_type": "<factual|opinion|prediction|null>"
  }},
  "topics": {{
    "primary_topic": "<topic label>",
    "topic_words": ["<word1>", "<word2>", "<word3>"]
  }},
  "cognitive_stage": {{
    "stage": <int 1-5, where 5 is self-transforming mind>,
    "stage_confidence": <float 0-1>,
    "stage_markers": ["<evidence for classification>"],
    "has_validation_seeking": <boolean, seeking approval is Stage 4>,
    "has_manifestation": <boolean, direct action without permission is Stage 5>,
    "banned_vocab_found": ["<any phrases like 'is this what you wanted', 'does this sound okay'>"],
    "manifestation_vocab_found": ["<any phrases like 'this is', 'here is', 'the pattern shows'>"]
  }},
  "struggle_filter": {{
    "pattern_type": "<swimming|drowning|neutral>",
    "has_problem_statement": <boolean>,
    "has_struggle_evidence": <boolean>,
    "has_resolution": <boolean>,
    "swimming_score": <float 0-1, problem→struggle→resolution arc>,
    "drowning_score": <float 0-1, anxiety→loop→more anxiety>,
    "anxiety_markers": ["<words indicating anxiety loop>"],
    "training_value": "<high|medium|low>"
  }},
  "metabolic_stage": {{
    "stage": "<truth|meaning|care_internal|care_external>",
    "is_raw_data": <boolean, unprocessed information>,
    "is_crisis": <boolean, unexpected failure>,
    "is_pain": <boolean, emotional signal>,
    "has_pattern_recognition": <boolean>,
    "has_structure_emergence": <boolean>,
    "has_resolution": <boolean>,
    "insight_level": <float 0-1>,
    "revelation_present": <boolean, surplus value beyond input>
  }},
  "confidence": {{
    "level": "<high|medium|low|uncertain>",
    "score": <float 0-1>,
    "admits_uncertainty": <boolean, "I don't know" is healthy>,
    "hedging_count": <int>,
    "strong_claims": ["<assertions without hedging>"]
  }},
  "source": {{
    "type": "<me|not_me|external|hybrid>",
    "is_human_voice": <boolean>,
    "is_system_voice": <boolean>,
    "personal_markers": ["<'I feel', 'I think', etc>"]
  }},
  "temporal": {{
    "orientation": "<past|present|future|meta>",
    "has_meta_temporal": <boolean, sees time itself as object>
  }},
  "operational_cycle": {{
    "phase": "<see|see_see|do|see_do|done>",
    "has_meta_awareness": <boolean, 'I see that I see'>,
    "sight_level": <int 1-3>
  }},
  "jeremy_arc": {{
    "thought_type": "<analytical|creative|emotional|directive|reflective>",
    "mode": "<working|processing|resting|crisis|flow>",
    "arc_confidence": <float 0-1>
  }},
  "resonance": {{
    "score": <float 0-1, how strongly this resonates with recurring patterns>,
    "strength": "<whisper|notice|signal|bell>",
    "is_echo": <boolean, does this echo past content>,
    "echo_shift_type": "<clarity_emergence|symbol_inversion|deepening|null>",
    "predicted_emotional_tone": "<predicted emotion before full analysis>",
    "emotional_prediction_confidence": <float 0-1>,
    "emotional_trajectory": "<ascending|stable|descending|volatile>",
    "reverb_strength": <float 0-1, how much this reverberates with known motifs>,
    "theme_evolution_phase": "<emerging|stable|transforming|archived|null>",
    "symbolic_matches": ["<list of matched symbolic concepts>"]
  }}
}}
```

IMPORTANT: Cognitive stage assessment is CRITICAL for training. Look for:
- Stage 4 indicators: validation seeking, "is this okay?", deference to authority
- Stage 5 indicators: direct manifestation, "this is", honest uncertainty "I don't know"

TOTAL RESONANCE: Detect whether this text resonates with recurring patterns.
- Echoes: Does this feel like a repeat of a known theme?
- Emotional prediction: What emotion would you PREDICT based on patterns?
- Symbolic alignment: Does this connect to archetypal themes (guardian, mirror, etc.)?

Return ONLY the JSON, no other text."""


def create_enrichment_from_llm(
    entity_id: str,
    text: str,
    llm_response: dict[str, Any],
    batch_id: Optional[str] = None,
) -> EntityEnrichment:
    """Create EntityEnrichment from LLM extraction response.
    
    Args:
        entity_id: The entity being enriched
        text: The original text
        llm_response: Parsed JSON from LLM
        batch_id: Optional batch identifier
        
    Returns:
        EntityEnrichment with all fields populated including Sovereign Architecture metrics
    """
    # Parse sentiment
    sentiment_data = llm_response.get("sentiment", {})
    sentiment = SentimentEnrichment(
        polarity=sentiment_data.get("polarity", 0.0),
        subjectivity=sentiment_data.get("subjectivity", 0.5),
    )
    
    # Parse emotions
    emotion_data = llm_response.get("emotions", {})
    emotion_scores = emotion_data.get("emotion_scores", {})
    
    # Find top emotion
    top_emotion = emotion_data.get("primary_emotion")
    top_count = 0
    if emotion_scores:
        top_emotion = max(emotion_scores, key=emotion_scores.get)
        top_count = int(emotion_scores.get(top_emotion, 0) * 100)
    
    emotion = EmotionEnrichment(
        nrclx_emotions=emotion_scores,
        nrclx_top_emotion=top_emotion,
        nrclx_top_count=top_count,
        goemotions_scores={},
        goemotions_primary_emotion=emotion_data.get("primary_emotion"),
        goemotions_primary_score=emotion_scores.get(top_emotion, 0.0) if emotion_scores else 0.0,
        goemotions_top_emotions=emotion_data.get("goemotions", []),
    )
    
    # Parse readability
    readability_data = llm_response.get("readability", {})
    readability = ReadabilityEnrichment(
        flesch_reading_ease=None,
        flesch_kincaid_grade=readability_data.get("estimated_grade_level"),
        difficult_words=readability_data.get("difficult_word_count", 0),
        lexicon_count=readability_data.get("word_count", 0),
        sentence_count=readability_data.get("sentence_count", 0),
        char_count=len(text),
    )
    
    # Parse keywords
    keywords_data = llm_response.get("keywords", {})
    top_5 = keywords_data.get("top_5", [])
    keywords = KeywordEnrichment(
        top_keyword=top_5[0] if top_5 else None,
        top_score=1.0 if top_5 else 0.0,
        top_5_keywords=top_5,
        all_keywords=[{"keyword": kw, "score": 1.0 - i * 0.1} for i, kw in enumerate(top_5)],
    )
    
    # Parse topics
    topics_data = llm_response.get("topics", {})
    topics = TopicEnrichment(
        topic_id=None,
        topic_probability=1.0,
        topic_words=topics_data.get("topic_words", []),
        topic_label=topics_data.get("primary_topic"),
    )
    
    # Parse content classification
    content_data = llm_response.get("content", {})
    content = ContentClassification(
        content_type=content_data.get("type"),
        domain=content_data.get("domain"),
        primary_category=content_data.get("domain"),
        category_path=[content_data.get("domain")] if content_data.get("domain") else [],
        qa_role=content_data.get("qa_role"),
        is_claim=content_data.get("is_claim", False),
        claim_type=content_data.get("claim_type"),
    )
    
    # =========================================================================
    # SOVEREIGN ARCHITECTURE ENRICHMENTS
    # =========================================================================
    
    # Parse cognitive stage
    cognitive_data = llm_response.get("cognitive_stage", {})
    banned_found = cognitive_data.get("banned_vocab_found", [])
    manifestation_found = cognitive_data.get("manifestation_vocab_found", [])
    stage_polarity = (len(manifestation_found) - len(banned_found)) / max(len(manifestation_found) + len(banned_found), 1)
    
    cognitive_stage = CognitiveStageEnrichment(
        stage=cognitive_data.get("stage", 3),
        stage_confidence=cognitive_data.get("stage_confidence", 0.5),
        stage_markers=cognitive_data.get("stage_markers", []),
        banned_vocab_count=len(banned_found),
        banned_vocab_matches=banned_found,
        manifestation_vocab_count=len(manifestation_found),
        manifestation_vocab_matches=manifestation_found,
        stage_polarity=stage_polarity,
    )
    
    # Parse struggle filter
    struggle_data = llm_response.get("struggle_filter", {})
    struggle_filter = StruggleFilterEnrichment(
        pattern_type=struggle_data.get("pattern_type"),
        has_problem_statement=struggle_data.get("has_problem_statement", False),
        has_struggle_evidence=struggle_data.get("has_struggle_evidence", False),
        has_resolution=struggle_data.get("has_resolution", False),
        swimming_score=struggle_data.get("swimming_score", 0.0),
        anxiety_markers=struggle_data.get("anxiety_markers", []),
        drowning_score=struggle_data.get("drowning_score", 0.0),
        training_value=struggle_data.get("training_value", "medium"),
    )
    
    # Parse metabolic stage
    metabolic_data = llm_response.get("metabolic_stage", {})
    metabolic_stage = MetabolicStageEnrichment(
        metabolic_stage=metabolic_data.get("stage"),
        is_raw_data=metabolic_data.get("is_raw_data", False),
        is_crisis=metabolic_data.get("is_crisis", False),
        is_pain=metabolic_data.get("is_pain", False),
        has_pattern_recognition=metabolic_data.get("has_pattern_recognition", False),
        has_structure_emergence=metabolic_data.get("has_structure_emergence", False),
        insight_level=metabolic_data.get("insight_level", 0.0),
        has_resolution=metabolic_data.get("has_resolution", False),
        revelation_present=metabolic_data.get("revelation_present", False),
    )
    
    # Parse confidence calibration
    confidence_data = llm_response.get("confidence", {})
    confidence = ConfidenceCalibrationEnrichment(
        confidence_level=confidence_data.get("level"),
        confidence_score=confidence_data.get("score", 0.5),
        hedging_count=confidence_data.get("hedging_count", 0),
        admits_uncertainty=confidence_data.get("admits_uncertainty", False),
        strong_claims=confidence_data.get("strong_claims", []),
    )
    
    # Parse source attribution
    source_data = llm_response.get("source", {})
    source_attribution = SourceAttributionEnrichment(
        source_type=source_data.get("type"),
        is_human_voice=source_data.get("is_human_voice", False),
        is_system_voice=source_data.get("is_system_voice", False),
        personal_markers=source_data.get("personal_markers", []),
    )
    
    # Parse temporal lens
    temporal_data = llm_response.get("temporal", {})
    temporal_lens = TemporalLensEnrichment(
        temporal_orientation=temporal_data.get("orientation"),
        has_meta_temporal=temporal_data.get("has_meta_temporal", False),
    )
    
    # Parse operational cycle
    cycle_data = llm_response.get("operational_cycle", {})
    operational_cycle = OperationalCycleEnrichment(
        cycle_phase=cycle_data.get("phase"),
        has_meta_awareness=cycle_data.get("has_meta_awareness", False),
        sight_level=cycle_data.get("sight_level", 1),
    )
    
    # Parse Jeremy Arc
    arc_data = llm_response.get("jeremy_arc", {})
    jeremy_arc = JeremyArcEnrichment(
        thought_type=arc_data.get("thought_type"),
        mode=arc_data.get("mode"),
        arc_prediction_confidence=arc_data.get("arc_confidence", 0.0),
    )
    
    # Parse Total Resonance
    resonance_data = llm_response.get("resonance", {})
    total_resonance = TotalResonanceEnrichment(
        resonance_score=resonance_data.get("score", 0.0),
        resonance_strength=resonance_data.get("strength"),
        is_echo=resonance_data.get("is_echo", False),
        echo_shift_type=resonance_data.get("echo_shift_type"),
        predicted_emotional_tone=resonance_data.get("predicted_emotional_tone"),
        emotional_prediction_confidence=resonance_data.get("emotional_prediction_confidence", 0.0),
        emotional_trajectory=resonance_data.get("emotional_trajectory"),
        reverb_strength=resonance_data.get("reverb_strength", 0.0),
        theme_evolution_phase=resonance_data.get("theme_evolution_phase"),
        symbol_matches=resonance_data.get("symbolic_matches", []),
    )
    
    return EntityEnrichment(
        entity_id=entity_id,
        enrichment_text=text,
        # Standard NLP
        sentiment=sentiment,
        emotion=emotion,
        readability=readability,
        keywords=keywords,
        topics=topics,
        content=content,
        # Sovereign Architecture
        cognitive_stage=cognitive_stage,
        struggle_filter=struggle_filter,
        metabolic_stage=metabolic_stage,
        confidence=confidence,
        source_attribution=source_attribution,
        temporal_lens=temporal_lens,
        operational_cycle=operational_cycle,
        jeremy_arc=jeremy_arc,
        total_resonance=total_resonance,
        # Metadata
        enrichment_batch_id=batch_id,
        enrichment_quality_flags=["llm_extracted"],
        enrichment_metadata={"source": "llm_refinery", "model": "qwen2.5-coder:32b"},
    )
