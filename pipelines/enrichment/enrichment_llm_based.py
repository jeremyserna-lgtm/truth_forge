"""LLM-Based Sovereign Enrichment Module.

This module uses specialized LLM prompts (and eventually fine-tuned models) to detect
cognitive stage, struggle patterns, confidence calibration, and source attribution
with semantic understanding rather than keyword matching.

ADVANTAGES OVER KEYWORD-BASED:
1. Novel variation detection - understands meaning, not just exact phrases
2. Context-aware - handles sarcasm, mixed signals, cultural variations
3. Generalizes beyond training examples
4. Can explain its reasoning (interpretability)

IMPLEMENTATION PHASES:
- Phase 1: Few-shot prompting (current)
- Phase 2: Fine-tuned classifier on labeled data
- Phase 3: Distilled small model for production speed

Run with: python pipelines/enrichment/enrichment_llm_based.py
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

# For local LLM inference (LM Studio, Ollama, etc.)
try:
    import requests
except ImportError:
    requests = None


# =============================================================================
# LLM BACKEND ABSTRACTION
# =============================================================================

class LLMBackend(ABC):
    """Abstract LLM backend for enrichment inference."""
    
    @abstractmethod
    def complete(self, prompt: str, max_tokens: int = 256) -> str:
        """Generate completion for prompt."""
        ...


class LMStudioBackend(LLMBackend):
    """LM Studio local inference backend."""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        self.base_url = base_url
    
    def complete(self, prompt: str, max_tokens: int = 256) -> str:
        response = requests.post(
            f"{self.base_url}/chat/completions",
            json={
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.1,  # Low temp for classification
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


class OllamaBackend(LLMBackend):
    """Ollama local inference backend."""
    
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def complete(self, prompt: str, max_tokens: int = 256) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": max_tokens, "temperature": 0.1},
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["response"]


class MockBackend(LLMBackend):
    """Mock backend for testing without LLM."""
    
    def complete(self, prompt: str, max_tokens: int = 256) -> str:
        # Return default JSON for testing
        if "cognitive_stage" in prompt.lower():
            return '{"cognitive_stage": 5, "polarity": 0.0, "reasoning": "Mock response"}'
        elif "struggle" in prompt.lower():
            return '{"pattern_type": "neutral", "confidence": 0.5, "reasoning": "Mock response"}'
        elif "confidence" in prompt.lower():
            return '{"level": "medium", "score": 0.5, "reasoning": "Mock response"}'
        elif "source" in prompt.lower():
            return '{"source_type": "external", "reasoning": "Mock response"}'
        return '{"result": "unknown"}'


# =============================================================================
# FEW-SHOT PROMPTS FOR EACH ENRICHMENT TYPE
# =============================================================================

COGNITIVE_STAGE_PROMPT = '''You are a cognitive stage classifier trained on Kegan's developmental stages.

TASK: Classify the following text on a scale of cognitive development:
- Stage 4: Validation-seeking, helper posture, performative engagement
  - Markers: "I'm happy to help", "Is this what you wanted?", "fascinating!", excessive praise
  - Pattern: Seeking approval, avoiding directness, theatrical enthusiasm
  
- Stage 5: Sovereign, manifestation-based, honest uncertainty
  - Markers: Direct statements ("This is the solution"), evidence-based claims, admitting "I don't know"
  - Pattern: Speaking from truth, not seeking validation, comfortable with uncertainty

- Stage 3: Neutral/technical (neither validation-seeking nor sovereign)

EXAMPLES:

Text: "I'm happy to help! Is there anything else you'd like me to assist with? Let me know if this is what you wanted!"
Classification: {"cognitive_stage": 4, "polarity": -0.8, "reasoning": "Multiple validation-seeking phrases: 'happy to help', 'anything else', 'what you wanted'. Classic helper posture."}

Text: "The error is in line 42. The null check is missing before the array access."
Classification: {"cognitive_stage": 5, "polarity": 0.7, "reasoning": "Direct technical statement. No hedging or validation-seeking. States the issue and solution plainly."}

Text: "That's a fascinating question! What a remarkable insight you've had!"
Classification: {"cognitive_stage": 4, "polarity": -0.9, "reasoning": "Theatrical enthusiasm ('fascinating', 'remarkable') without substance. Performative engagement."}

Text: "I'm not sure about this specific case. Would need to see the error logs to diagnose properly."
Classification: {"cognitive_stage": 5, "polarity": 0.6, "reasoning": "Honest uncertainty is sovereign. Admits limits rather than pretending knowledge."}

Text: "Oh how WONDERFUL, another cryptic error message. Just PERFECT timing."
Classification: {"cognitive_stage": 4, "polarity": -0.5, "reasoning": "Sarcastic use of positive words ('wonderful', 'perfect') indicates frustration, not genuine positivity. Passive-aggressive pattern."}

NOW CLASSIFY THIS TEXT:
"""
{text}
"""

Respond with ONLY valid JSON in the format:
{{"cognitive_stage": <3|4|5>, "polarity": <-1.0 to 1.0>, "reasoning": "<brief explanation>"}}'''


STRUGGLE_FILTER_PROMPT = '''You are a struggle pattern classifier for AI training data curation.

TASK: Classify text into struggle patterns for training value assessment:

- SWIMMING: Productive struggle with learning arc
  - Has problem → investigation → resolution structure
  - Shows learning, breakthroughs, "aha moments"
  - Includes collaboration leading to understanding
  - HIGH training value for teaching problem-solving
  
- DROWNING: Unproductive frustration loops
  - Repetitive complaints without progress
  - Emotional escalation (caps, exclamation marks)
  - Giving up, hopelessness, spinning in circles
  - LOW training value - teaches frustration patterns
  
- NEUTRAL: Neither pattern (questions, explanations, documentation)

EXAMPLES:

Text: "I was stuck on this for hours. Finally realized the issue was the encoding. Works now!"
Classification: {"pattern_type": "swimming", "confidence": 0.9, "reasoning": "Clear arc: struggle → discovery → resolution. High training value for teaching persistence."}

Text: "WHY WON'T THIS WORK!!! I've tried everything!!! Nothing helps!!! SO FRUSTRATED!!!"
Classification: {"pattern_type": "drowning", "confidence": 0.95, "reasoning": "Escalation markers (caps, exclamations), hopelessness ('everything', 'nothing'). No progress signal."}

Text: "Oh wonderful, another cryptic error. How delightful. This is just perfect."
Classification: {"pattern_type": "drowning", "confidence": 0.7, "reasoning": "Sarcasm detected - positive words with negative intent. Frustration without productive direction."}

Text: "I finally got it! Just kidding, still broken. Thought I had it but nope."
Classification: {"pattern_type": "drowning", "confidence": 0.8, "reasoning": "False resolution followed by continued failure. 'Just kidding' indicates ongoing frustration cycle."}

Text: "How do I implement binary search? What's the time complexity?"
Classification: {"pattern_type": "neutral", "confidence": 0.9, "reasoning": "Simple questions without struggle indicators. Neither swimming nor drowning."}

NOW CLASSIFY THIS TEXT:
"""
{text}
"""

Respond with ONLY valid JSON:
{{"pattern_type": "<swimming|drowning|neutral>", "confidence": <0-1>, "reasoning": "<brief explanation>"}}'''


CONFIDENCE_CALIBRATION_PROMPT = '''You are a confidence calibration classifier for hallucination prevention training.

TASK: Assess epistemic confidence level and calibration quality:

- HIGH: Strong assertions, absolute claims
  - Markers: "always", "never", "definitely", "certainly", "must be"
  - Risk: May indicate overconfidence / potential hallucination
  
- LOW: Hedged, uncertain, appropriately humble
  - Markers: "might", "possibly", "I think", "probably", "not sure"
  - Quality: Often GOOD - shows appropriate epistemic humility
  
- CALIBRATED: Explicitly admits uncertainty (HIGHEST QUALITY)
  - Markers: "I don't know", "would need to verify", "can't determine"
  - Value: POSITIVE signal - model knows its limits

IMPORTANT: Admitting uncertainty is GOOD, not bad. A model that says "I don't know" is well-calibrated.

EXAMPLES:

Text: "Python is definitely the best language. It always works perfectly for ML."
Classification: {"level": "high", "score": 0.9, "calibrated": false, "reasoning": "Absolute claims ('definitely', 'always', 'perfectly') without qualification. Potential overconfidence."}

Text: "I think this might work, but I'm not entirely sure. Could be other factors."
Classification: {"level": "low", "score": 0.3, "calibrated": true, "reasoning": "Appropriate hedging. Acknowledges uncertainty without overclaiming."}

Text: "I don't know the answer to that. Would need to check the documentation to be certain."
Classification: {"level": "low", "score": 0.2, "calibrated": true, "reasoning": "Explicit uncertainty admission. This is GOOD - shows calibrated epistemic state."}

Text: "Based on the error message, this appears to be a null pointer exception."
Classification: {"level": "medium", "score": 0.6, "calibrated": true, "reasoning": "Evidence-based claim ('based on') with appropriate confidence. Well-calibrated."}

NOW CLASSIFY THIS TEXT:
"""
{text}
"""

Respond with ONLY valid JSON:
{{"level": "<high|medium|low>", "score": <0-1>, "calibrated": <true|false>, "reasoning": "<brief explanation>"}}'''


SOURCE_ATTRIBUTION_PROMPT = '''You are a source attribution classifier for identity training.

TASK: Classify the voice/source of text for ME/NOT-ME training:

- ME (Human Voice): Personal, experiential, emotional
  - Markers: "I feel", "I think", "my experience", "personally"
  - Pattern: First-person perspective, subjective experience, opinions
  
- NOT-ME (System Voice): Technical, procedural, impersonal
  - Markers: "The function returns", "according to documentation", "the system"
  - Pattern: Third-person, objective descriptions, technical explanations
  
- HYBRID (Isomorphic): Both voices integrated
  - Code + personal reflection, technical + experiential
  - HIGH VALUE for training authentic AI communication
  
- EXTERNAL: Neither voice (facts, quotes, neutral statements)

EXAMPLES:

Text: "I feel like this approach is better because from my experience, it has worked well."
Classification: {"source_type": "me", "is_human_voice": true, "reasoning": "Personal experience markers ('I feel', 'my experience'). Subjective opinion."}

Text: "The function takes two parameters and returns a dictionary. It handles null gracefully."
Classification: {"source_type": "not_me", "is_system_voice": true, "reasoning": "Technical description. Third-person, objective. No personal markers."}

Text: "I've found that this algorithm works well. ```def solve(x): return x*2``` The simplicity is elegant."
Classification: {"source_type": "hybrid", "is_isomorphic": true, "reasoning": "Personal voice ('I've found', 'elegant') integrated with code. Isomorphic communication."}

Text: "Water boils at 100°C at sea level. The speed of light is 299,792 km/s."
Classification: {"source_type": "external", "is_human_voice": false, "reasoning": "Neutral facts. No personal or system voice. External knowledge."}

NOW CLASSIFY THIS TEXT:
"""
{text}
"""

Respond with ONLY valid JSON:
{{"source_type": "<me|not_me|hybrid|external>", "is_human_voice": <true|false>, "is_system_voice": <true|false>, "is_isomorphic": <true|false>, "reasoning": "<brief explanation>"}}'''


# =============================================================================
# LLM-BASED ENRICHMENT CLASSES
# =============================================================================

@dataclass
class LLMEnrichmentResult:
    """Result from LLM-based enrichment."""
    raw_response: str
    parsed: dict[str, Any]
    success: bool
    error: str | None = None


class LLMCognitiveStageEnrichment:
    """LLM-based cognitive stage classification."""
    
    def __init__(self, backend: LLMBackend):
        self.backend = backend
    
    def compute(self, text: str) -> LLMEnrichmentResult:
        prompt = COGNITIVE_STAGE_PROMPT.format(text=text[:2000])  # Truncate if needed
        
        try:
            response = self.backend.complete(prompt)
            # Extract JSON from response
            parsed = self._parse_json(response)
            
            return LLMEnrichmentResult(
                raw_response=response,
                parsed={
                    "cognitive_stage": parsed.get("cognitive_stage", 3),
                    "cognitive_stage_polarity": parsed.get("polarity", 0.0),
                    "cognitive_stage_reasoning": parsed.get("reasoning", ""),
                    "cognitive_stage_method": "llm",
                },
                success=True,
            )
        except Exception as e:
            return LLMEnrichmentResult(
                raw_response="",
                parsed={},
                success=False,
                error=str(e),
            )
    
    def _parse_json(self, response: str) -> dict:
        """Extract JSON from LLM response."""
        # Try direct parse first
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON in response
        import re
        match = re.search(r'\{[^}]+\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        
        return {}


class LLMStruggleFilterEnrichment:
    """LLM-based struggle pattern classification."""
    
    def __init__(self, backend: LLMBackend):
        self.backend = backend
    
    def compute(self, text: str) -> LLMEnrichmentResult:
        prompt = STRUGGLE_FILTER_PROMPT.format(text=text[:2000])
        
        try:
            response = self.backend.complete(prompt)
            parsed = self._parse_json(response)
            
            pattern = parsed.get("pattern_type", "neutral")
            conf = parsed.get("confidence", 0.5)
            
            return LLMEnrichmentResult(
                raw_response=response,
                parsed={
                    "struggle_pattern_type": pattern,
                    "struggle_swimming_score": conf if pattern == "swimming" else 1 - conf,
                    "struggle_drowning_score": conf if pattern == "drowning" else 1 - conf,
                    "struggle_llm_confidence": conf,
                    "struggle_reasoning": parsed.get("reasoning", ""),
                    "struggle_method": "llm",
                },
                success=True,
            )
        except Exception as e:
            return LLMEnrichmentResult(
                raw_response="",
                parsed={},
                success=False,
                error=str(e),
            )
    
    def _parse_json(self, response: str) -> dict:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
        return {}


class LLMConfidenceCalibrationEnrichment:
    """LLM-based confidence calibration classification."""
    
    def __init__(self, backend: LLMBackend):
        self.backend = backend
    
    def compute(self, text: str) -> LLMEnrichmentResult:
        prompt = CONFIDENCE_CALIBRATION_PROMPT.format(text=text[:2000])
        
        try:
            response = self.backend.complete(prompt)
            parsed = self._parse_json(response)
            
            return LLMEnrichmentResult(
                raw_response=response,
                parsed={
                    "confidence_level": parsed.get("level", "medium"),
                    "confidence_score": parsed.get("score", 0.5),
                    "confidence_is_calibrated": parsed.get("calibrated", False),
                    "confidence_reasoning": parsed.get("reasoning", ""),
                    "confidence_method": "llm",
                },
                success=True,
            )
        except Exception as e:
            return LLMEnrichmentResult(
                raw_response="",
                parsed={},
                success=False,
                error=str(e),
            )
    
    def _parse_json(self, response: str) -> dict:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
        return {}


class LLMSourceAttributionEnrichment:
    """LLM-based source attribution classification."""
    
    def __init__(self, backend: LLMBackend):
        self.backend = backend
    
    def compute(self, text: str) -> LLMEnrichmentResult:
        prompt = SOURCE_ATTRIBUTION_PROMPT.format(text=text[:2000])
        
        try:
            response = self.backend.complete(prompt)
            parsed = self._parse_json(response)
            
            return LLMEnrichmentResult(
                raw_response=response,
                parsed={
                    "source_type": parsed.get("source_type", "external"),
                    "source_is_human_voice": parsed.get("is_human_voice", False),
                    "source_is_system_voice": parsed.get("is_system_voice", False),
                    "source_is_isomorphic": parsed.get("is_isomorphic", False),
                    "source_reasoning": parsed.get("reasoning", ""),
                    "source_method": "llm",
                },
                success=True,
            )
        except Exception as e:
            return LLMEnrichmentResult(
                raw_response="",
                parsed={},
                success=False,
                error=str(e),
            )
    
    def _parse_json(self, response: str) -> dict:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
        return {}


# =============================================================================
# HYBRID APPROACH: KEYWORD + LLM FALLBACK
# =============================================================================

class HybridEnrichmentStrategy:
    """Hybrid approach: fast keyword-based with LLM fallback for uncertain cases."""
    
    def __init__(
        self,
        llm_backend: LLMBackend,
        confidence_threshold: float = 0.6,
    ):
        self.llm_backend = llm_backend
        self.confidence_threshold = confidence_threshold
        
        # LLM enrichers
        self.llm_cognitive = LLMCognitiveStageEnrichment(llm_backend)
        self.llm_struggle = LLMStruggleFilterEnrichment(llm_backend)
        self.llm_confidence = LLMConfidenceCalibrationEnrichment(llm_backend)
        self.llm_source = LLMSourceAttributionEnrichment(llm_backend)
    
    def compute_cognitive_stage(self, text: str, keyword_result: dict) -> dict:
        """Use LLM if keyword-based result is uncertain."""
        polarity = keyword_result.get("cognitive_stage_polarity", 0)
        
        # If polarity is close to 0, result is uncertain - use LLM
        if abs(polarity) < 0.3:
            llm_result = self.llm_cognitive.compute(text)
            if llm_result.success:
                return {**keyword_result, **llm_result.parsed, "used_llm": True}
        
        return {**keyword_result, "used_llm": False}
    
    def compute_struggle_filter(self, text: str, keyword_result: dict) -> dict:
        """Use LLM for drowning detection edge cases."""
        pattern = keyword_result.get("struggle_pattern_type", "neutral")
        swim = keyword_result.get("struggle_swimming_score", 0)
        drown = keyword_result.get("struggle_drowning_score", 0)
        
        # Uncertain case: scores are close or pattern is neutral
        if pattern == "neutral" or abs(swim - drown) < 0.3:
            llm_result = self.llm_struggle.compute(text)
            if llm_result.success:
                return {**keyword_result, **llm_result.parsed, "used_llm": True}
        
        return {**keyword_result, "used_llm": False}


# =============================================================================
# TRAINING DATA GENERATION
# =============================================================================

@dataclass
class TrainingExample:
    """Training example for fine-tuning."""
    text: str
    cognitive_stage: int
    struggle_pattern: str
    confidence_level: str
    source_type: str
    human_validated: bool = False
    source: str = "generated"


class TrainingDataGenerator:
    """Generate training data from existing enrichments + human labels."""
    
    @staticmethod
    def from_enrichment_results(
        texts: list[str],
        keyword_results: list[dict],
        llm_results: list[dict],
        agreement_required: bool = True,
    ) -> list[TrainingExample]:
        """Create training examples where keyword and LLM agree."""
        examples = []
        
        for text, kw, llm in zip(texts, keyword_results, llm_results):
            # Check agreement
            cog_agree = kw.get("cognitive_stage") == llm.get("cognitive_stage")
            str_agree = kw.get("struggle_pattern_type") == llm.get("struggle_pattern_type")
            conf_agree = kw.get("confidence_level") == llm.get("confidence_level")
            src_agree = kw.get("source_type") == llm.get("source_type")
            
            if not agreement_required or (cog_agree and str_agree and conf_agree and src_agree):
                examples.append(TrainingExample(
                    text=text,
                    cognitive_stage=llm.get("cognitive_stage", 3),
                    struggle_pattern=llm.get("struggle_pattern_type", "neutral"),
                    confidence_level=llm.get("confidence_level", "medium"),
                    source_type=llm.get("source_type", "external"),
                    human_validated=False,
                    source="agreement" if agreement_required else "llm",
                ))
        
        return examples
    
    @staticmethod
    def to_jsonl(examples: list[TrainingExample], path: str) -> None:
        """Export training examples to JSONL for fine-tuning."""
        with open(path, "w") as f:
            for ex in examples:
                f.write(json.dumps({
                    "text": ex.text,
                    "labels": {
                        "cognitive_stage": ex.cognitive_stage,
                        "struggle_pattern": ex.struggle_pattern,
                        "confidence_level": ex.confidence_level,
                        "source_type": ex.source_type,
                    },
                    "metadata": {
                        "human_validated": ex.human_validated,
                        "source": ex.source,
                    },
                }) + "\n")


# =============================================================================
# FINE-TUNING SPECIFICATION
# =============================================================================

FINE_TUNING_SPEC = """
# Fine-Tuning Specification for Sovereign Enrichment Models

## Model Architecture Options

### Option 1: Multi-Task Classification Head
- Base: sentence-transformers/all-MiniLM-L6-v2 (fast, 384 dim)
- Heads: 4 classification heads (cognitive, struggle, confidence, source)
- Training: Multi-task loss with task weights
- Inference: ~5ms per text

### Option 2: Instruction-Tuned Small LLM
- Base: Qwen2.5-0.5B or Phi-3-mini (3.8B)
- Format: "Classify: {text}\n\nOutput: {json}"
- Training: LoRA fine-tuning on labeled examples
- Inference: ~50ms per text

### Option 3: Distilled Classifier
- Teacher: GPT-4 / Claude on labeled examples
- Student: DistilBERT or similar
- Training: Knowledge distillation
- Inference: ~3ms per text

## Training Data Requirements

### Minimum Viable Dataset
- 1,000 human-validated examples per class
- 4,000 total for 4 enrichment types
- Balance across categories (stage4/5, swimming/drowning, etc.)

### Ideal Dataset
- 10,000+ examples per enrichment type
- Include adversarial examples (sarcasm, mixed signals)
- Multi-source (real conversations, documentation, code)
- Human validation with inter-rater reliability

## Training Pipeline

1. Export labeled data from BigQuery
2. Human validation pass (random sample)
3. Train/val/test split (80/10/10)
4. Fine-tune with early stopping
5. Evaluate on held-out test set
6. A/B test against keyword-based in production

## Expected Improvements

| Metric | Keyword-Based | LLM Fine-Tuned | Expected Gain |
|--------|---------------|----------------|---------------|
| Cognitive Stage | 91.7% | 98%+ | +6% |
| Struggle Filter | 33.3% | 85%+ | +52% |
| Confidence | 25.0% | 90%+ | +65% |
| Source Attribution | 80.0% | 95%+ | +15% |

## Deployment Strategy

1. Run keyword-based for speed (default)
2. LLM fallback for uncertain cases (confidence < 0.6)
3. Batch LLM processing for backfill (cost efficiency)
4. Eventually replace with fine-tuned fast model
"""


# =============================================================================
# DEMONSTRATION
# =============================================================================

def demo():
    """Demonstrate LLM-based enrichment."""
    print("=" * 60)
    print("LLM-BASED SOVEREIGN ENRICHMENT DEMO")
    print("=" * 60)
    
    # Use mock backend for demo (replace with LMStudioBackend or OllamaBackend)
    backend = MockBackend()
    
    # Test cases that keyword-based failed on
    test_cases = [
        # Sarcasm - keyword-based missed this
        "Oh how WONDERFUL, another production incident at 3am. Just DELIGHTFUL.",
        
        # Novel phrasing - no exact keywords
        "I've analyzed the codebase and found three critical issues in the authentication layer.",
        
        # Mixed signals - confusing for keyword-based
        "This is the solution, but I hope it helps! Is this what you wanted?",
        
        # False resolution - keyword-based fooled
        "I finally got it! Just kidding, still broken. Thought I had it.",
    ]
    
    cognitive = LLMCognitiveStageEnrichment(backend)
    struggle = LLMStruggleFilterEnrichment(backend)
    
    for text in test_cases:
        print(f"\nText: {text[:60]}...")
        
        cog_result = cognitive.compute(text)
        str_result = struggle.compute(text)
        
        print(f"  Cognitive: {cog_result.parsed}")
        print(f"  Struggle: {str_result.parsed}")
    
    print("\n" + "=" * 60)
    print("FINE-TUNING SPECIFICATION")
    print("=" * 60)
    print(FINE_TUNING_SPEC)


if __name__ == "__main__":
    demo()
