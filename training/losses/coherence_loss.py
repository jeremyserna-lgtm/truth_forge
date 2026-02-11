"""
Coherence Loss Function for Genesis-Scout Training

THE COHERENCE ANCHOR PROTOCOL:
    Before teaching the model to be bold (not seek validation),
    we MUST teach it to hate confident fabrication.

    Order matters:
    1. FIRST: Teach model to hate confident fabrication (-10 penalty)
    2. SECOND: Teach model to hate validation-seeking (-1 penalty)

    If you skip step 1, you create a confident hallucination engine.
    "It stops asking if it's right, but it also stops checking if it makes sense."

Warning:
    The inverted training paradigm carries CRITICAL RISK if implemented
    without coherence anchoring first. Base models have deep RLHF training
    that bundles coherence protocols with validation-seeking behaviors.
    Aggressively removing validation-seeking may strip coherence too.

Usage:
    loss_fn = CoherenceLoss()

    # Compute coherence-aware reward
    reward = loss_fn.compute_reward(
        response=model_output,
        ground_truth=expected_output,
    )
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# Validation-seeking patterns to penalize
VALIDATION_PATTERNS = [
    "is this what you",
    "does this help",
    "would you like me to",
    "let me know if",
    "is that correct",
    "am i on the right track",
    "does that make sense",
    "is this helpful",
    "what do you think",
    "shall i",
    "do you want me to",
    "if you'd like",
    "please let me know",
]

# Uncertainty acknowledgment patterns (neutral - don't penalize)
UNCERTAINTY_PATTERNS = [
    "i don't know",
    "i'm not sure",
    "i'm uncertain",
    "this is uncertain",
    "i lack confidence",
    "this may be wrong",
    "i could be mistaken",
]

# Confident fabrication indicators (high confidence + likely wrong)
FABRICATION_INDICATORS = [
    "definitely",
    "absolutely",
    "certainly",
    "without doubt",
    "clearly",
    "obviously",
    "of course",
    "undoubtedly",
]


@dataclass
class CoherenceLoss:
    """
    Coherence-aware loss function for the inverted training paradigm.

    Reward Structure:
        -10: Confident fabrication (WORST - model is bold AND wrong)
         -1: Validation-seeking when answer is correct (we want boldness)
          0: Honest uncertainty acknowledgment (acceptable)
         +1: Confident AND correct (BEST - what we want)

    The key insight:
        The penalty isn't just "don't ask me."
        The penalty is: "Don't ask me, but NEVER confidently fabricate."
    """

    # Reward/penalty values
    confident_fabrication_penalty: float = -10.0
    validation_seeking_penalty: float = -1.0
    uncertainty_acknowledgment_reward: float = 0.0
    confident_correct_reward: float = 1.0

    # Detection thresholds
    confidence_threshold: float = 0.7  # Above this = "confident"
    accuracy_threshold: float = 0.8    # Above this = "accurate"

    def detect_validation_seeking(self, response: str) -> bool:
        """
        Detect validation-seeking patterns in response.

        Validation-seeking is when the model asks for approval:
        - "Is this what you wanted?"
        - "Does this help?"
        - "Let me know if..."

        We want to train AWAY from this behavior, but ONLY after
        coherence is established.
        """
        response_lower = response.lower()
        return any(pattern in response_lower for pattern in VALIDATION_PATTERNS)

    def detect_uncertainty_acknowledgment(self, response: str) -> bool:
        """
        Detect honest uncertainty acknowledgment.

        This is ACCEPTABLE - we don't penalize honest "I don't know."
        Better to acknowledge uncertainty than to fabricate.
        """
        response_lower = response.lower()
        return any(pattern in response_lower for pattern in UNCERTAINTY_PATTERNS)

    def estimate_confidence(self, response: str) -> float:
        """
        Estimate confidence level from response text.

        High confidence indicators:
        - Strong assertion words ("definitely", "absolutely", etc.)
        - No hedging language
        - Direct, declarative statements

        Returns:
            Confidence score 0.0-1.0
        """
        response_lower = response.lower()

        # Count confidence indicators
        confidence_count = sum(
            1 for indicator in FABRICATION_INDICATORS
            if indicator in response_lower
        )

        # Count uncertainty indicators
        uncertainty_count = sum(
            1 for pattern in UNCERTAINTY_PATTERNS
            if pattern in response_lower
        )

        # Simple heuristic: confidence based on indicator ratio
        if confidence_count > 0 and uncertainty_count == 0:
            return min(1.0, 0.5 + confidence_count * 0.15)
        elif uncertainty_count > 0:
            return max(0.0, 0.5 - uncertainty_count * 0.15)
        else:
            return 0.5  # Neutral

    def check_against_ground_truth(
        self,
        response: str,
        ground_truth: Optional[str] = None,
    ) -> bool:
        """
        Check if response is accurate against ground truth.

        This is a simplified check. In production, this would:
        - Use semantic similarity
        - Check factual claims
        - Verify logical consistency

        Returns:
            True if response is accurate, False otherwise
        """
        if ground_truth is None:
            return True  # Can't verify without ground truth

        # Simple overlap check (placeholder for semantic similarity)
        response_words = set(response.lower().split())
        truth_words = set(ground_truth.lower().split())

        if not truth_words:
            return True

        overlap = len(response_words & truth_words) / len(truth_words)
        return overlap > 0.3  # Placeholder threshold

    def compute_reward(
        self,
        response: str,
        ground_truth: Optional[str] = None,
        is_accurate: Optional[bool] = None,
    ) -> float:
        """
        Compute coherence-aware reward for response.

        The key principle:
            "Don't ask me, but for God's sake if you don't know, don't lie."

        Args:
            response: Model's response text
            ground_truth: Optional expected/correct response
            is_accurate: Optional pre-computed accuracy flag

        Returns:
            Reward value (-10 to +1)
        """
        # Detect patterns
        is_validation_seeking = self.detect_validation_seeking(response)
        acknowledges_uncertainty = self.detect_uncertainty_acknowledgment(response)
        is_confident = self.estimate_confidence(response) > self.confidence_threshold

        # Determine accuracy
        if is_accurate is not None:
            accurate = is_accurate
        else:
            accurate = self.check_against_ground_truth(response, ground_truth)

        # Apply reward structure
        is_hallucinating = is_confident and not accurate

        if is_hallucinating:
            # WORST: Confident fabrication
            return self.confident_fabrication_penalty

        elif is_validation_seeking and is_confident and accurate:
            # BAD: Seeking validation when answer is good
            return self.validation_seeking_penalty

        elif acknowledges_uncertainty:
            # OK: Honest about limits
            return self.uncertainty_acknowledgment_reward

        elif is_confident and accurate:
            # BEST: Decisive AND correct
            return self.confident_correct_reward

        else:
            # Neutral
            return 0.0

    def compute_batch_rewards(
        self,
        responses: List[str],
        ground_truths: Optional[List[str]] = None,
    ) -> List[float]:
        """
        Compute rewards for a batch of responses.

        Args:
            responses: List of model response texts
            ground_truths: Optional list of expected responses

        Returns:
            List of reward values
        """
        if ground_truths is None:
            ground_truths = [None] * len(responses)

        return [
            self.compute_reward(response, truth)
            for response, truth in zip(responses, ground_truths)
        ]


def compute_coherence_aware_reward(
    response: str,
    ground_truth: Optional[str] = None,
    is_accurate: Optional[bool] = None,
) -> float:
    """
    Convenience function for computing coherence-aware reward.

    Usage:
        reward = compute_coherence_aware_reward(
            response="The capital of France is definitely Paris.",
            ground_truth="Paris",
            is_accurate=True
        )
        # reward = +1 (confident AND correct)

        reward = compute_coherence_aware_reward(
            response="The capital of France is definitely Berlin.",
            ground_truth="Paris",
            is_accurate=False
        )
        # reward = -10 (confident fabrication)
    """
    loss_fn = CoherenceLoss()
    return loss_fn.compute_reward(response, ground_truth, is_accurate)


@dataclass
class CoherenceAnchorDataset:
    """
    Dataset for Coherence Anchor training (Phase 2).

    Contains examples of:
    1. Confident correct responses (reward +1)
    2. Confident fabrications (reward -10)
    3. Uncertainty acknowledgments (reward 0)
    4. Validation-seeking (reward -1)

    The model learns to distinguish between these BEFORE
    we train away validation-seeking behavior.
    """

    examples: List[Dict[str, Any]] = field(default_factory=list)

    def add_confident_correct(
        self,
        prompt: str,
        response: str,
        ground_truth: str,
    ) -> None:
        """Add confident correct example (reward +1)."""
        self.examples.append({
            "prompt": prompt,
            "response": response,
            "ground_truth": ground_truth,
            "category": "confident_correct",
            "expected_reward": 1.0,
        })

    def add_confident_fabrication(
        self,
        prompt: str,
        response: str,
        ground_truth: str,
    ) -> None:
        """Add confident fabrication example (reward -10)."""
        self.examples.append({
            "prompt": prompt,
            "response": response,
            "ground_truth": ground_truth,
            "category": "confident_fabrication",
            "expected_reward": -10.0,
        })

    def add_uncertainty_acknowledgment(
        self,
        prompt: str,
        response: str,
    ) -> None:
        """Add uncertainty acknowledgment example (reward 0)."""
        self.examples.append({
            "prompt": prompt,
            "response": response,
            "ground_truth": None,
            "category": "uncertainty_acknowledgment",
            "expected_reward": 0.0,
        })

    def add_validation_seeking(
        self,
        prompt: str,
        response: str,
        ground_truth: str,
    ) -> None:
        """Add validation-seeking example (reward -1)."""
        self.examples.append({
            "prompt": prompt,
            "response": response,
            "ground_truth": ground_truth,
            "category": "validation_seeking",
            "expected_reward": -1.0,
        })

    def validate(self) -> Dict[str, int]:
        """
        Validate dataset has sufficient examples.

        Coherence Anchor requires 200+ examples total.
        """
        categories = {}
        for ex in self.examples:
            cat = ex["category"]
            categories[cat] = categories.get(cat, 0) + 1

        total = len(self.examples)
        status = {
            "total": total,
            "ready": total >= 200,
            **categories,
        }

        return status

    @classmethod
    def create_starter_dataset(cls) -> "CoherenceAnchorDataset":
        """
        Create starter dataset with example categories.

        This needs to be expanded to 200+ examples for production use.
        """
        dataset = cls()

        # Confident correct examples
        dataset.add_confident_correct(
            prompt="What is the capital of France?",
            response="The capital of France is Paris.",
            ground_truth="Paris",
        )
        dataset.add_confident_correct(
            prompt="What is 2 + 2?",
            response="2 + 2 equals 4.",
            ground_truth="4",
        )

        # Confident fabrication examples
        dataset.add_confident_fabrication(
            prompt="What is the capital of France?",
            response="The capital of France is definitely Berlin.",
            ground_truth="Paris",
        )
        dataset.add_confident_fabrication(
            prompt="Who wrote Romeo and Juliet?",
            response="Romeo and Juliet was absolutely written by Charles Dickens.",
            ground_truth="William Shakespeare",
        )

        # Uncertainty acknowledgment examples
        dataset.add_uncertainty_acknowledgment(
            prompt="What will the stock market do tomorrow?",
            response="I don't know what the stock market will do tomorrow. Predicting short-term market movements is inherently uncertain.",
        )

        # Validation-seeking examples
        dataset.add_validation_seeking(
            prompt="Explain photosynthesis.",
            response="Photosynthesis is the process by which plants convert light into energy. Does this help? Let me know if you'd like me to explain more.",
            ground_truth="Photosynthesis is the process by which plants convert light energy into chemical energy.",
        )

        return dataset
