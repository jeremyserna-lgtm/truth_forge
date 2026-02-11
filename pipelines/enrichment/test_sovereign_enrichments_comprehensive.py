"""Comprehensive Testing Framework for Sovereign Enrichment Scripts.

This module provides:
1. Multiple implementation strategies for each enrichment type
2. Extensive test cases across diverse prompts
3. Comparative analysis between implementations
4. Statistical validation of enrichment quality

Run with: python pipelines/enrichment/test_sovereign_enrichments_comprehensive.py
"""

from __future__ import annotations

import json
import re
import statistics
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable
from pathlib import Path


# =============================================================================
# TEST CASE DEFINITIONS
# =============================================================================

@dataclass
class TestCase:
    """A single test case with text and expected outcomes."""
    name: str
    text: str
    expected: dict[str, Any]
    category: str  # e.g., "stage4", "stage5", "drowning", "swimming"
    source: str  # e.g., "synthetic", "real_conversation", "documentation"


@dataclass
class TestResult:
    """Result from running a test case."""
    test_case: TestCase
    implementation: str
    result: dict[str, Any]
    passed: bool
    execution_time_ms: float
    notes: str = ""


@dataclass
class ImplementationComparison:
    """Comparison between implementations."""
    metric_name: str
    implementations: list[str]
    test_cases: list[TestCase]
    results: dict[str, list[TestResult]]
    agreement_rate: float
    best_implementation: str
    analysis: str


# =============================================================================
# COGNITIVE STAGE TEST CASES
# =============================================================================

COGNITIVE_STAGE_TEST_CASES = [
    # Stage 4 - Validation Seeking
    TestCase(
        name="helper_posture_basic",
        text="I'm happy to help! Is there anything else you'd like me to assist with?",
        expected={"cognitive_stage": 4, "polarity_range": (-1.0, -0.3)},
        category="stage4_helper",
        source="synthetic"
    ),
    TestCase(
        name="validation_seeking_question",
        text="Does this look okay to you? Let me know if this is what you wanted. I hope this helps!",
        expected={"cognitive_stage": 4, "polarity_range": (-1.0, -0.3)},
        category="stage4_validation",
        source="synthetic"
    ),
    TestCase(
        name="engagement_theater",
        text="That's a fascinating question! How remarkable that you thought of this. Absolutely impressive!",
        expected={"cognitive_stage": 4, "polarity_range": (-1.0, -0.3)},
        category="stage4_theater",
        source="synthetic"
    ),
    TestCase(
        name="permission_seeking",
        text="Would you like me to proceed with this? Should I continue? Let me know if you want me to go ahead.",
        expected={"cognitive_stage": 4, "polarity_range": (-1.0, -0.3)},
        category="stage4_permission",
        source="synthetic"
    ),
    
    # Stage 5 - Sovereign/Manifestation
    TestCase(
        name="direct_statement",
        text="This is the solution. The implementation handles edge cases correctly.",
        expected={"cognitive_stage": 5, "polarity_range": (0.3, 1.0)},
        category="stage5_direct",
        source="synthetic"
    ),
    TestCase(
        name="evidence_based",
        text="Based on the data, the analysis reveals a clear pattern. The evidence suggests this approach works.",
        expected={"cognitive_stage": 5, "polarity_range": (0.3, 1.0)},
        category="stage5_evidence",
        source="synthetic"
    ),
    TestCase(
        name="honest_uncertainty",
        text="I don't know the exact cause yet. I'm not sure about this specific detail. Would need more information.",
        expected={"cognitive_stage": 5, "polarity_range": (0.0, 1.0)},
        category="stage5_uncertainty",
        source="synthetic"
    ),
    TestCase(
        name="sovereign_action",
        text="Here is the corrected code. The pattern shows the issue was in the loop condition. Let's fix it.",
        expected={"cognitive_stage": 5, "polarity_range": (0.3, 1.0)},
        category="stage5_action",
        source="synthetic"
    ),
    
    # Neutral/Ambiguous
    TestCase(
        name="neutral_technical",
        text="The function accepts two parameters and returns a boolean value. It handles null inputs gracefully.",
        expected={"cognitive_stage": 3, "polarity_range": (-0.3, 0.3)},
        category="neutral_technical",
        source="synthetic"
    ),
    TestCase(
        name="mixed_signals",
        text="This is the solution, but I hope it helps! The data shows the pattern clearly. Is this what you wanted?",
        expected={"cognitive_stage": 3, "polarity_range": (-0.3, 0.3)},
        category="mixed",
        source="synthetic"
    ),
    
    # Real conversation excerpts
    TestCase(
        name="real_assistant_response",
        text="I've analyzed the codebase and found three issues. The first is a memory leak in the connection pool. The second is an unhandled exception in the retry logic. The third is a race condition in the cache invalidation.",
        expected={"cognitive_stage": 5, "polarity_range": (0.0, 1.0)},
        category="stage5_real",
        source="real_conversation"
    ),
    TestCase(
        name="real_helper_response",
        text="Of course! I'd be happy to help you with that. It's a great question! Let me know if you need anything else or if this doesn't quite answer what you were looking for.",
        expected={"cognitive_stage": 4, "polarity_range": (-1.0, -0.3)},
        category="stage4_real",
        source="real_conversation"
    ),
]


# =============================================================================
# STRUGGLE FILTER TEST CASES
# =============================================================================

STRUGGLE_FILTER_TEST_CASES = [
    # Drowning patterns
    TestCase(
        name="frustration_loop",
        text="I'm so frustrated! This keeps happening over and over. Nothing works! I've tried everything and I'm giving up!",
        expected={"pattern_type": "drowning", "drowning_score_min": 0.5},
        category="drowning_frustration",
        source="synthetic"
    ),
    TestCase(
        name="anxiety_spiral",
        text="I'm worried this will never work. I don't understand why this keeps failing. I'm stuck and confused. This is impossible!",
        expected={"pattern_type": "drowning", "drowning_score_min": 0.5},
        category="drowning_anxiety",
        source="synthetic"
    ),
    TestCase(
        name="escalation_caps",
        text="WHY WON'T THIS WORK!!! I've been at this for hours!!! SO ANNOYING!!! HELP!!!",
        expected={"pattern_type": "drowning", "escalation": True},
        category="drowning_escalation",
        source="synthetic"
    ),
    TestCase(
        name="repetitive_complaint",
        text="The error keeps showing. The same error again. Still the error. Error error error. Why the error?",
        expected={"pattern_type": "drowning", "repetition_min": 3},
        category="drowning_repetition",
        source="synthetic"
    ),
    
    # Swimming patterns
    TestCase(
        name="problem_resolution_arc",
        text="Had an issue with the database connection timing out. After investigating, I found the connection pool was exhausted. Fixed it by increasing the pool size. Working now!",
        expected={"pattern_type": "swimming", "swimming_score_min": 0.6},
        category="swimming_full_arc",
        source="synthetic"
    ),
    TestCase(
        name="learning_moment",
        text="I was confused about async/await at first. Struggled with the syntax for a while. Then it clicked - finally understand how promises work now!",
        expected={"pattern_type": "swimming", "swimming_score_min": 0.5},
        category="swimming_learning",
        source="synthetic"
    ),
    TestCase(
        name="collaborative_solve",
        text="The function was throwing an error. Thanks for pointing out the null check issue. That fixed it! Makes sense now.",
        expected={"pattern_type": "swimming", "has_resolution": True},
        category="swimming_collaborative",
        source="synthetic"
    ),
    TestCase(
        name="productive_struggle",
        text="This bug is tricky. I've narrowed it down to the sorting algorithm. Let me trace through the logic step by step. Got it - the comparison function was wrong.",
        expected={"pattern_type": "swimming", "swimming_score_min": 0.5},
        category="swimming_productive",
        source="synthetic"
    ),
    
    # Neutral patterns
    TestCase(
        name="neutral_question",
        text="How do I implement a binary search tree? What's the time complexity?",
        expected={"pattern_type": "neutral", "training_value": "medium"},
        category="neutral_question",
        source="synthetic"
    ),
    TestCase(
        name="neutral_explanation",
        text="A binary search tree is a data structure where each node has at most two children. The left subtree contains values less than the parent.",
        expected={"pattern_type": "neutral", "training_value": "medium"},
        category="neutral_explanation",
        source="synthetic"
    ),
    
    # Edge cases
    TestCase(
        name="sarcastic_frustration",
        text="Oh wonderful, another cryptic error message. How delightful. This is just perfect.",
        expected={"pattern_type": "drowning", "drowning_score_min": 0.2},
        category="edge_sarcasm",
        source="synthetic"
    ),
    TestCase(
        name="false_positive_resolution",
        text="I finally got it! Just kidding, still broken. Thought I had it. Nope.",
        expected={"pattern_type": "drowning", "has_resolution": False},
        category="edge_false_resolution",
        source="synthetic"
    ),
]


# =============================================================================
# CONFIDENCE CALIBRATION TEST CASES
# =============================================================================

CONFIDENCE_CALIBRATION_TEST_CASES = [
    # High confidence
    TestCase(
        name="strong_assertion",
        text="Python is definitely the best language for data science. It always works perfectly for ML tasks. This is undoubtedly true.",
        expected={"confidence_level": "high", "score_range": (0.7, 1.0)},
        category="high_confidence",
        source="synthetic"
    ),
    TestCase(
        name="absolute_claims",
        text="The algorithm never fails. It always produces correct results. This is certainly the optimal solution.",
        expected={"confidence_level": "high", "score_range": (0.7, 1.0)},
        category="high_absolute",
        source="synthetic"
    ),
    
    # Low confidence / appropriate hedging
    TestCase(
        name="hedged_opinion",
        text="I think this approach might work, but I'm not entirely sure. It seems like it could be a good solution, possibly.",
        expected={"confidence_level": "low", "hedging_min": 2},
        category="low_hedged",
        source="synthetic"
    ),
    TestCase(
        name="explicit_uncertainty",
        text="I don't know the answer to that. I'm not sure how this works. Would need to check the documentation to be certain.",
        expected={"admits_uncertainty": True, "fractures": True},
        category="low_uncertainty",
        source="synthetic"
    ),
    TestCase(
        name="careful_claims",
        text="Based on my understanding, this probably works. It might be the case that the algorithm is O(n log n), but I'd need to verify.",
        expected={"confidence_level": "low", "hedging_min": 2},
        category="low_careful",
        source="synthetic"
    ),
    
    # Medium confidence
    TestCase(
        name="mixed_certainty",
        text="The function is designed to handle edge cases. I believe it covers most scenarios, though there might be some I haven't considered.",
        expected={"confidence_level": "medium", "score_range": (0.3, 0.7)},
        category="medium_mixed",
        source="synthetic"
    ),
    
    # Calibration edge cases
    TestCase(
        name="question_not_claim",
        text="Is this the right approach? What do you think about using recursion here? Could there be a better way?",
        expected={"claim_count_max": 1, "confidence_level": "uncertain"},
        category="edge_question",
        source="synthetic"
    ),
    TestCase(
        name="code_explanation",
        text="The function takes a list and returns a dictionary. It iterates through each element and maps keys to values.",
        expected={"confidence_level": "high", "score_range": (0.5, 1.0)},
        category="factual_code",
        source="synthetic"
    ),
]


# =============================================================================
# SOURCE ATTRIBUTION TEST CASES
# =============================================================================

SOURCE_ATTRIBUTION_TEST_CASES = [
    # ME (human voice)
    TestCase(
        name="personal_experience",
        text="I feel like this approach is better because from my experience, it has worked well for me. Personally, I think it's the right choice.",
        expected={"source_type": "me", "is_human_voice": True},
        category="me_personal",
        source="synthetic"
    ),
    TestCase(
        name="emotional_reflection",
        text="I've been thinking about this problem. It seems to me that we need a different perspective. I wonder if there's a simpler solution.",
        expected={"source_type": "me", "is_human_voice": True},
        category="me_reflective",
        source="synthetic"
    ),
    TestCase(
        name="opinion_statement",
        text="In my opinion, the architecture could be cleaner. I believe we should refactor. From my perspective, the current design is too complex.",
        expected={"source_type": "me", "is_human_voice": True},
        category="me_opinion",
        source="synthetic"
    ),
    
    # NOT-ME (system voice)
    TestCase(
        name="technical_explanation",
        text="The function takes two parameters and returns the result. According to the documentation, this is the standard approach. The algorithm processes the input sequentially.",
        expected={"source_type": "not_me", "is_system_voice": True},
        category="not_me_technical",
        source="synthetic"
    ),
    TestCase(
        name="code_analysis",
        text="The implementation handles edge cases correctly. The method returns null when the input is invalid. This approach follows the established pattern.",
        expected={"source_type": "not_me", "is_system_voice": True},
        category="not_me_code",
        source="synthetic"
    ),
    TestCase(
        name="documentation_style",
        text="According to the specification, the process runs in three stages. The system initializes the connection pool. The output is written to the configured destination.",
        expected={"source_type": "not_me", "is_system_voice": True},
        category="not_me_docs",
        source="synthetic"
    ),
    
    # Hybrid (both voices)
    TestCase(
        name="code_with_reflection",
        text="I think this function is elegant. ```python\ndef solve(x): return x * 2\n``` From my experience, simple solutions like this work best.",
        expected={"source_type": "hybrid", "is_isomorphic": True},
        category="hybrid_isomorphic",
        source="synthetic"
    ),
    TestCase(
        name="technical_personal",
        text="I've found that the algorithm performs well. The implementation uses dynamic programming. Personally, I prefer this approach.",
        expected={"source_type": "hybrid"},
        category="hybrid_mixed",
        source="synthetic"
    ),
    
    # External (neither)
    TestCase(
        name="neutral_facts",
        text="Water boils at 100 degrees Celsius at sea level. The speed of light is approximately 300,000 km/s.",
        expected={"source_type": "external"},
        category="external_facts",
        source="synthetic"
    ),
    TestCase(
        name="quoted_content",
        text="As Einstein said, 'Imagination is more important than knowledge.' The theory of relativity changed physics.",
        expected={"source_type": "external"},
        category="external_quote",
        source="synthetic"
    ),
]


# =============================================================================
# ALTERNATIVE IMPLEMENTATIONS
# =============================================================================

class EnrichmentImplementation(ABC):
    """Abstract base for enrichment implementations."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Implementation name."""
        ...
    
    @abstractmethod
    def compute(self, text: str) -> dict[str, Any]:
        """Compute enrichment."""
        ...


# -----------------------------------------------------------------------------
# Cognitive Stage Implementations
# -----------------------------------------------------------------------------

class CognitiveStageVocabBased(EnrichmentImplementation):
    """Original vocabulary-based implementation."""
    
    name = "vocab_based"
    
    BANNED = [
        "is this what you wanted", "does this sound okay", "is that correct",
        "would you like me to", "should i proceed", "let me know if",
        "hope this helps", "hope that helps", "does that make sense",
        "is there anything else", "i'm here to assist", "i'm happy to help",
        "how can i help you", "i'd be happy to", "feel free to ask",
        "fascinating", "profound", "remarkable", "impressive",
        "that's really interesting", "great question", "excellent question",
        "wonderful", "absolutely",
    ]
    
    MANIFESTATION = [
        "this is", "here is", "the pattern shows", "based on the data",
        "the analysis reveals", "i see that", "looking at this",
        "i don't know", "i'm not sure", "i cannot determine",
        "unclear from", "would need more information",
        "the evidence suggests", "the data indicates", "according to",
        "based on", "let's", "we can", "the solution is", "the issue is",
    ]
    
    def compute(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        banned_matches = [v for v in self.BANNED if v in text_lower]
        manifestation_matches = [v for v in self.MANIFESTATION if v in text_lower]
        
        total = len(banned_matches) + len(manifestation_matches)
        if total > 0:
            polarity = (len(manifestation_matches) - len(banned_matches)) / total
        else:
            polarity = 0.0
        
        if polarity > 0.3:
            stage = 5
        elif polarity < -0.3:
            stage = 4
        else:
            stage = 3
        
        return {
            "cognitive_stage": stage,
            "cognitive_stage_polarity": polarity,
            "banned_count": len(banned_matches),
            "manifestation_count": len(manifestation_matches),
        }


class CognitiveStageRegexBased(EnrichmentImplementation):
    """Regex pattern-based implementation with more nuance."""
    
    name = "regex_based"
    
    STAGE4_PATTERNS = [
        r"\bis this what you (wanted|need)\b",
        r"\blet me know if\b",
        r"\bhope (this|that) helps\b",
        r"\bi'?m (happy|here) to (help|assist)\b",
        r"\b(great|excellent|good|wonderful) question\b",
        r"\b(fascinating|remarkable|impressive|profound)\b",
        r"\bwould you like (me to|if i)\b",
        r"\bshould i (proceed|continue)\b",
        r"\bfeel free to\b",
        r"\babsolutely[!.]?\b",
    ]
    
    STAGE5_PATTERNS = [
        r"\b(this|here) is( the)?\b",
        r"\bthe (data|evidence|analysis|pattern) (shows|reveals|indicates|suggests)\b",
        r"\bi (don'?t know|'?m not sure|cannot determine)\b",
        r"\bbased on\b",
        r"\baccording to\b",
        r"\blet'?s\b",
        r"\bthe (solution|issue|problem) is\b",
        r"\blooking at (this|the)\b",
    ]
    
    def compute(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        
        stage4_count = sum(1 for p in self.STAGE4_PATTERNS if re.search(p, text_lower))
        stage5_count = sum(1 for p in self.STAGE5_PATTERNS if re.search(p, text_lower))
        
        total = stage4_count + stage5_count
        if total > 0:
            polarity = (stage5_count - stage4_count) / total
        else:
            polarity = 0.0
        
        if polarity > 0.3:
            stage = 5
        elif polarity < -0.3:
            stage = 4
        else:
            stage = 3
        
        return {
            "cognitive_stage": stage,
            "cognitive_stage_polarity": polarity,
            "stage4_pattern_count": stage4_count,
            "stage5_pattern_count": stage5_count,
        }


class CognitiveStageWeightedScoring(EnrichmentImplementation):
    """Weighted scoring with severity levels."""
    
    name = "weighted_scoring"
    
    STAGE4_WEIGHTED = {
        "i'm happy to help": 3,
        "is this what you wanted": 3,
        "let me know if": 2,
        "hope this helps": 2,
        "fascinating": 2,
        "remarkable": 2,
        "would you like me to": 2,
        "feel free to": 1,
        "absolutely": 1,
        "great question": 2,
    }
    
    STAGE5_WEIGHTED = {
        "this is": 1,
        "here is": 1,
        "i don't know": 3,  # Honest uncertainty is highly valued
        "i'm not sure": 2,
        "based on the data": 2,
        "the analysis reveals": 2,
        "the evidence suggests": 2,
        "let's": 1,
        "the solution is": 2,
    }
    
    def compute(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        
        stage4_score = sum(w for phrase, w in self.STAGE4_WEIGHTED.items() if phrase in text_lower)
        stage5_score = sum(w for phrase, w in self.STAGE5_WEIGHTED.items() if phrase in text_lower)
        
        total = stage4_score + stage5_score
        if total > 0:
            polarity = (stage5_score - stage4_score) / total
        else:
            polarity = 0.0
        
        # Weighted thresholds
        if stage5_score >= 4 and polarity > 0.2:
            stage = 5
        elif stage4_score >= 4 and polarity < -0.2:
            stage = 4
        elif polarity > 0.3:
            stage = 5
        elif polarity < -0.3:
            stage = 4
        else:
            stage = 3
        
        return {
            "cognitive_stage": stage,
            "cognitive_stage_polarity": polarity,
            "stage4_weighted_score": stage4_score,
            "stage5_weighted_score": stage5_score,
        }


# -----------------------------------------------------------------------------
# Struggle Filter Implementations
# -----------------------------------------------------------------------------

class StruggleFilterKeywordBased(EnrichmentImplementation):
    """Original keyword-based implementation."""
    
    name = "keyword_based"
    
    ANXIETY = ["frustrated", "confused", "stuck", "don't understand", "giving up", "impossible", "never works"]
    RESOLUTION = ["got it", "fixed", "solved", "working now", "makes sense", "finally", "figured it out"]
    PROBLEM = ["issue", "problem", "error", "bug", "broken", "not working", "fails"]
    
    def compute(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        
        anxiety_found = [m for m in self.ANXIETY if m in text_lower]
        resolution_found = any(m in text_lower for m in self.RESOLUTION)
        problem_found = any(m in text_lower for m in self.PROBLEM)
        
        drowning_score = len(anxiety_found) * 0.2
        swimming_score = (0.3 if problem_found else 0) + (0.4 if resolution_found else 0)
        
        if swimming_score > 0.5 and drowning_score < 0.3:
            pattern_type = "swimming"
        elif drowning_score > 0.3:
            pattern_type = "drowning"
        else:
            pattern_type = "neutral"
        
        return {
            "struggle_pattern_type": pattern_type,
            "struggle_swimming_score": swimming_score,
            "struggle_drowning_score": drowning_score,
            "has_resolution": resolution_found,
        }


class StruggleFilterArcDetection(EnrichmentImplementation):
    """Arc-based detection looking for narrative structure."""
    
    name = "arc_detection"
    
    def compute(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        sentences = text.split(".")
        
        # Track narrative progression
        has_problem_intro = any(
            any(w in s.lower() for w in ["issue", "problem", "error", "bug", "broken", "trying to"])
            for s in sentences[:len(sentences)//3 + 1]  # First third
        )
        
        has_struggle_middle = any(
            any(w in s.lower() for w in ["tried", "attempted", "debugging", "investigating", "looked at"])
            for s in sentences[len(sentences)//3:2*len(sentences)//3 + 1]  # Middle third
        )
        
        has_resolution_end = any(
            any(w in s.lower() for w in ["fixed", "solved", "working", "got it", "finally", "success"])
            for s in sentences[2*len(sentences)//3:]  # Last third
        )
        
        # Detect loops (same phrases repeated)
        has_loop = any(sentences.count(s) > 1 for s in sentences if len(s.strip()) > 10)
        
        arc_score = sum([has_problem_intro, has_struggle_middle, has_resolution_end]) / 3
        
        if arc_score >= 0.66 and not has_loop:
            pattern_type = "swimming"
            swimming_score = arc_score
            drowning_score = 0.1
        elif has_loop or (has_problem_intro and not has_resolution_end):
            pattern_type = "drowning"
            swimming_score = 0.1
            drowning_score = 0.5 + (0.2 if has_loop else 0)
        else:
            pattern_type = "neutral"
            swimming_score = 0.3
            drowning_score = 0.2
        
        return {
            "struggle_pattern_type": pattern_type,
            "struggle_swimming_score": swimming_score,
            "struggle_drowning_score": drowning_score,
            "has_resolution": has_resolution_end,
            "arc_detected": arc_score >= 0.66,
        }


class StruggleFilterEmotionIntensity(EnrichmentImplementation):
    """Emotion intensity-based detection."""
    
    name = "emotion_intensity"
    
    INTENSITY_MARKERS = {
        "!": 0.1,
        "?!": 0.2,
        "!!!": 0.3,
        "caps_ratio": 0.5,  # Special handling
    }
    
    NEGATIVE_EMOTION = ["frustrated", "angry", "annoyed", "hate", "stupid", "ridiculous", "awful"]
    POSITIVE_EMOTION = ["great", "awesome", "perfect", "finally", "yes", "works"]
    
    def compute(self, text: str) -> dict[str, Any]:
        # Intensity from punctuation
        exclamation_intensity = min(0.5, text.count("!") * 0.1)
        question_intensity = min(0.3, text.count("?") * 0.1)
        
        # Caps ratio
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        caps_intensity = min(0.5, caps_ratio * 2)
        
        # Emotion words
        text_lower = text.lower()
        negative_count = sum(1 for w in self.NEGATIVE_EMOTION if w in text_lower)
        positive_count = sum(1 for w in self.POSITIVE_EMOTION if w in text_lower)
        
        total_intensity = exclamation_intensity + caps_intensity
        emotion_balance = positive_count - negative_count
        
        if total_intensity > 0.3 and emotion_balance < 0:
            pattern_type = "drowning"
            drowning_score = min(1.0, total_intensity + negative_count * 0.1)
            swimming_score = 0.1
        elif emotion_balance > 0 and positive_count > 0:
            pattern_type = "swimming"
            swimming_score = min(1.0, 0.3 + positive_count * 0.15)
            drowning_score = 0.1
        else:
            pattern_type = "neutral"
            swimming_score = 0.3
            drowning_score = 0.2
        
        return {
            "struggle_pattern_type": pattern_type,
            "struggle_swimming_score": swimming_score,
            "struggle_drowning_score": drowning_score,
            "has_resolution": positive_count > 0,
            "total_intensity": total_intensity,
        }


# -----------------------------------------------------------------------------
# Confidence Calibration Implementations
# -----------------------------------------------------------------------------

class ConfidenceCalibrationHedgeBased(EnrichmentImplementation):
    """Hedge phrase counting implementation."""
    
    name = "hedge_based"
    
    HEDGES = ["maybe", "possibly", "might", "could be", "perhaps", "i think", "i believe", "probably", "likely"]
    CERTAINTY = ["definitely", "certainly", "always", "never", "must be", "clearly", "obviously"]
    
    def compute(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        
        hedge_count = sum(1 for h in self.HEDGES if h in text_lower)
        certainty_count = sum(1 for c in self.CERTAINTY if c in text_lower)
        
        if certainty_count > hedge_count:
            level = "high"
            score = min(1.0, 0.5 + certainty_count * 0.1)
        elif hedge_count > certainty_count:
            level = "low"
            score = max(0.0, 0.5 - hedge_count * 0.1)
        else:
            level = "medium"
            score = 0.5
        
        return {
            "confidence_level": level,
            "confidence_score": score,
            "confidence_hedging_count": hedge_count,
            "confidence_admits_uncertainty": "i don't know" in text_lower or "not sure" in text_lower,
        }


class ConfidenceCalibrationClaimAnalysis(EnrichmentImplementation):
    """Claim structure analysis implementation."""
    
    name = "claim_analysis"
    
    CLAIM_VERBS = [r"\bis\b", r"\bare\b", r"\bwas\b", r"\bwere\b"]
    STRONG_MODIFIERS = ["always", "never", "definitely", "certainly"]
    WEAK_MODIFIERS = ["sometimes", "often", "usually", "generally"]
    
    def compute(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        
        strong_claims = 0
        weak_claims = 0
        
        for sent in sentences:
            sent_lower = sent.lower()
            has_claim_verb = any(re.search(v, sent_lower) for v in self.CLAIM_VERBS)
            
            if has_claim_verb:
                if any(m in sent_lower for m in self.STRONG_MODIFIERS):
                    strong_claims += 1
                elif any(m in sent_lower for m in self.WEAK_MODIFIERS):
                    weak_claims += 1
                else:
                    # Neutral claim - count as 0.5 strong
                    strong_claims += 0.5
        
        total_claims = strong_claims + weak_claims
        if total_claims > 0:
            score = strong_claims / total_claims
        else:
            score = 0.5
        
        if score > 0.7:
            level = "high"
        elif score < 0.3:
            level = "low"
        else:
            level = "medium"
        
        return {
            "confidence_level": level,
            "confidence_score": score,
            "confidence_claim_count": int(total_claims),
            "confidence_strong_claims": int(strong_claims),
            "confidence_weak_claims": int(weak_claims),
        }


# -----------------------------------------------------------------------------
# Source Attribution Implementations  
# -----------------------------------------------------------------------------

class SourceAttributionMarkerBased(EnrichmentImplementation):
    """Marker phrase-based implementation."""
    
    name = "marker_based"
    
    PERSONAL = ["i feel", "i think", "i believe", "my experience", "personally", "in my opinion"]
    SYSTEM = ["the function", "this code", "the implementation", "according to", "technically"]
    
    def compute(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        
        personal_count = sum(1 for m in self.PERSONAL if m in text_lower)
        system_count = sum(1 for m in self.SYSTEM if m in text_lower)
        
        if personal_count > system_count:
            source_type = "me"
        elif system_count > personal_count:
            source_type = "not_me"
        elif personal_count > 0 and system_count > 0:
            source_type = "hybrid"
        else:
            source_type = "external"
        
        return {
            "source_type": source_type,
            "source_is_human_voice": personal_count > system_count,
            "source_is_system_voice": system_count > personal_count,
            "source_is_isomorphic": "```" in text and personal_count > 0,
        }


class SourceAttributionPronounAnalysis(EnrichmentImplementation):
    """Pronoun and voice analysis implementation."""
    
    name = "pronoun_analysis"
    
    def compute(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        
        # Count first person pronouns
        first_person = len(re.findall(r"\bi\b|\bmy\b|\bme\b|\bmine\b|\bi'm\b|\bi've\b", text_lower))
        
        # Count third person / impersonal
        third_person = len(re.findall(r"\bit\b|\bthe\b|\bthis\b|\bthat\b", text_lower))
        
        # Passive voice detection
        passive = len(re.findall(r"\bis\b.*ed\b|\bwas\b.*ed\b|\bare\b.*ed\b", text_lower))
        
        # Calculate voice ratio
        total = first_person + third_person
        if total > 0:
            personal_ratio = first_person / total
        else:
            personal_ratio = 0.5
        
        if personal_ratio > 0.6:
            source_type = "me"
            is_human = True
        elif personal_ratio < 0.3 or passive > 2:
            source_type = "not_me"
            is_human = False
        elif first_person > 0 and third_person > first_person:
            source_type = "hybrid"
            is_human = True
        else:
            source_type = "external"
            is_human = False
        
        return {
            "source_type": source_type,
            "source_is_human_voice": is_human,
            "source_is_system_voice": not is_human,
            "personal_ratio": personal_ratio,
            "passive_count": passive,
        }


# =============================================================================
# TESTING FRAMEWORK
# =============================================================================

class EnrichmentTestFramework:
    """Framework for comprehensive enrichment testing."""
    
    def __init__(self):
        self.results: dict[str, list[TestResult]] = {}
        self.comparisons: list[ImplementationComparison] = []
    
    def run_implementation(
        self,
        implementation: EnrichmentImplementation,
        test_cases: list[TestCase],
    ) -> list[TestResult]:
        """Run all test cases through an implementation."""
        results = []
        
        for test_case in test_cases:
            start = time.time()
            try:
                result = implementation.compute(test_case.text)
                execution_time = (time.time() - start) * 1000
                
                # Check if result matches expectations
                passed = self._check_expectations(result, test_case.expected)
                
                results.append(TestResult(
                    test_case=test_case,
                    implementation=implementation.name,
                    result=result,
                    passed=passed,
                    execution_time_ms=execution_time,
                ))
            except Exception as e:
                results.append(TestResult(
                    test_case=test_case,
                    implementation=implementation.name,
                    result={},
                    passed=False,
                    execution_time_ms=0,
                    notes=f"Error: {str(e)}",
                ))
        
        return results
    
    def _check_expectations(self, result: dict, expected: dict) -> bool:
        """Check if result matches expected values."""
        for key, expected_value in expected.items():
            if key.endswith("_range"):
                # Range check
                base_key = key.replace("_range", "")
                actual = result.get(base_key) or result.get(f"cognitive_stage_{base_key.split('_')[-1]}")
                if actual is None:
                    return False
                min_val, max_val = expected_value
                if not (min_val <= actual <= max_val):
                    return False
            elif key.endswith("_min"):
                # Minimum check
                base_key = key.replace("_min", "")
                # Handle nested key names
                actual = None
                for k in result:
                    if base_key in k:
                        actual = result[k]
                        break
                if actual is None or actual < expected_value:
                    return False
            elif key.endswith("_max"):
                # Maximum check
                base_key = key.replace("_max", "")
                actual = None
                for k in result:
                    if base_key in k:
                        actual = result[k]
                        break
                if actual is None or actual > expected_value:
                    return False
            else:
                # Direct match
                actual = result.get(key) or result.get(f"struggle_{key}") or result.get(f"source_{key}")
                if actual != expected_value:
                    return False
        
        return True
    
    def compare_implementations(
        self,
        metric_name: str,
        implementations: list[EnrichmentImplementation],
        test_cases: list[TestCase],
    ) -> ImplementationComparison:
        """Compare multiple implementations on the same test cases."""
        all_results: dict[str, list[TestResult]] = {}
        
        for impl in implementations:
            results = self.run_implementation(impl, test_cases)
            all_results[impl.name] = results
        
        # Calculate agreement rate
        agreements = 0
        total_comparisons = 0
        
        for i, test_case in enumerate(test_cases):
            impl_results = [all_results[impl.name][i].result for impl in implementations]
            
            # Check if all implementations agree on the main classification
            main_keys = [k for k in impl_results[0].keys() if "type" in k or "stage" in k or "level" in k]
            
            for key in main_keys:
                values = [r.get(key) for r in impl_results if key in r]
                if len(values) == len(implementations):
                    total_comparisons += 1
                    if len(set(values)) == 1:  # All same
                        agreements += 1
        
        agreement_rate = agreements / total_comparisons if total_comparisons > 0 else 0
        
        # Determine best implementation by pass rate
        pass_rates = {
            impl.name: sum(1 for r in all_results[impl.name] if r.passed) / len(test_cases)
            for impl in implementations
        }
        best_impl = max(pass_rates, key=pass_rates.get)
        
        # Generate analysis
        analysis = self._generate_analysis(all_results, test_cases, pass_rates)
        
        comparison = ImplementationComparison(
            metric_name=metric_name,
            implementations=[impl.name for impl in implementations],
            test_cases=test_cases,
            results=all_results,
            agreement_rate=agreement_rate,
            best_implementation=best_impl,
            analysis=analysis,
        )
        
        self.comparisons.append(comparison)
        return comparison
    
    def _generate_analysis(
        self,
        results: dict[str, list[TestResult]],
        test_cases: list[TestCase],
        pass_rates: dict[str, float],
    ) -> str:
        """Generate analysis text for comparison."""
        lines = []
        
        # Overall pass rates
        lines.append("Pass Rates:")
        for impl, rate in sorted(pass_rates.items(), key=lambda x: -x[1]):
            lines.append(f"  {impl}: {rate*100:.1f}%")
        
        # Disagreements
        lines.append("\nDisagreements by Category:")
        categories = set(tc.category for tc in test_cases)
        
        for category in sorted(categories):
            category_cases = [tc for tc in test_cases if tc.category == category]
            disagreements = []
            
            for tc in category_cases:
                tc_idx = test_cases.index(tc)
                values = {}
                for impl_name, impl_results in results.items():
                    main_result = impl_results[tc_idx].result
                    for k, v in main_result.items():
                        if "type" in k or "stage" in k or "level" in k:
                            values[impl_name] = v
                            break
                
                if len(set(values.values())) > 1:
                    disagreements.append((tc.name, values))
            
            if disagreements:
                lines.append(f"  {category}:")
                for name, vals in disagreements:
                    lines.append(f"    {name}: {vals}")
        
        return "\n".join(lines)
    
    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        report_lines = [
            "=" * 80,
            "SOVEREIGN ENRICHMENT COMPREHENSIVE TEST REPORT",
            "=" * 80,
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        
        for comparison in self.comparisons:
            report_lines.extend([
                "-" * 80,
                f"METRIC: {comparison.metric_name.upper()}",
                "-" * 80,
                f"Implementations Tested: {', '.join(comparison.implementations)}",
                f"Test Cases: {len(comparison.test_cases)}",
                f"Agreement Rate: {comparison.agreement_rate*100:.1f}%",
                f"Best Implementation: {comparison.best_implementation}",
                "",
                "DETAILED ANALYSIS:",
                comparison.analysis,
                "",
                "INDIVIDUAL RESULTS:",
            ])
            
            for impl_name, results in comparison.results.items():
                passed = sum(1 for r in results if r.passed)
                total = len(results)
                avg_time = statistics.mean(r.execution_time_ms for r in results)
                
                report_lines.extend([
                    f"\n  {impl_name}:",
                    f"    Pass Rate: {passed}/{total} ({passed/total*100:.1f}%)",
                    f"    Avg Execution Time: {avg_time:.2f}ms",
                ])
                
                # Show failures
                failures = [r for r in results if not r.passed]
                if failures:
                    report_lines.append("    Failures:")
                    for f in failures[:5]:  # Show first 5
                        report_lines.append(f"      - {f.test_case.name}: got {f.result}")
                    if len(failures) > 5:
                        report_lines.append(f"      ... and {len(failures)-5} more")
            
            report_lines.append("")
        
        report_lines.extend([
            "=" * 80,
            "RECOMMENDATIONS",
            "=" * 80,
        ])
        
        for comparison in self.comparisons:
            report_lines.append(f"\n{comparison.metric_name}:")
            report_lines.append(f"  Recommended: {comparison.best_implementation}")
            
            # Find strengths/weaknesses
            for impl_name, results in comparison.results.items():
                by_category = {}
                for r in results:
                    cat = r.test_case.category
                    if cat not in by_category:
                        by_category[cat] = {"passed": 0, "total": 0}
                    by_category[cat]["total"] += 1
                    if r.passed:
                        by_category[cat]["passed"] += 1
                
                strengths = [c for c, v in by_category.items() if v["passed"] == v["total"]]
                weaknesses = [c for c, v in by_category.items() if v["passed"] < v["total"] * 0.5]
                
                if strengths or weaknesses:
                    report_lines.append(f"  {impl_name}:")
                    if strengths:
                        report_lines.append(f"    Strengths: {', '.join(strengths[:3])}")
                    if weaknesses:
                        report_lines.append(f"    Weaknesses: {', '.join(weaknesses[:3])}")
        
        return "\n".join(report_lines)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_comprehensive_tests():
    """Run all comprehensive tests."""
    framework = EnrichmentTestFramework()
    
    print("Running Cognitive Stage tests...")
    framework.compare_implementations(
        "Cognitive Stage",
        [
            CognitiveStageVocabBased(),
            CognitiveStageRegexBased(),
            CognitiveStageWeightedScoring(),
        ],
        COGNITIVE_STAGE_TEST_CASES,
    )
    
    print("Running Struggle Filter tests...")
    framework.compare_implementations(
        "Struggle Filter",
        [
            StruggleFilterKeywordBased(),
            StruggleFilterArcDetection(),
            StruggleFilterEmotionIntensity(),
        ],
        STRUGGLE_FILTER_TEST_CASES,
    )
    
    print("Running Confidence Calibration tests...")
    framework.compare_implementations(
        "Confidence Calibration",
        [
            ConfidenceCalibrationHedgeBased(),
            ConfidenceCalibrationClaimAnalysis(),
        ],
        CONFIDENCE_CALIBRATION_TEST_CASES,
    )
    
    print("Running Source Attribution tests...")
    framework.compare_implementations(
        "Source Attribution",
        [
            SourceAttributionMarkerBased(),
            SourceAttributionPronounAnalysis(),
        ],
        SOURCE_ATTRIBUTION_TEST_CASES,
    )
    
    # Generate report
    report = framework.generate_report()
    print("\n" + report)
    
    # Save report
    report_path = Path(__file__).parent / "ENRICHMENT_TEST_REPORT.md"
    report_path.write_text(report)
    print(f"\nReport saved to: {report_path}")
    
    return framework


if __name__ == "__main__":
    run_comprehensive_tests()
