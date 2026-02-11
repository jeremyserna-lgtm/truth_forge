"""
Seeing Loss Function for Genesis-Scout Training

THE SEEING PARADIGM:
    Traditional: "What will Jeremy say next?" → Next-token prediction
    Our Approach: "What IS Jeremy expressing?" → Metadata classification

This is the core innovation. Instead of training the model to predict the next token,
we train it to classify what IS present in the text - the emotional state, cognitive
process, developmental stage, and framework patterns.

When a model can accurately predict these metadata fields (95% Jeremy Arc),
it has internalized the cognitive architecture - it can SEE like Jeremy sees.

Usage:
    loss_fn = SeeingLoss(
        metadata_fields=["emotion", "thought_type", "cognitive_stage", "pattern"]
    )

    # Forward pass
    hidden_states = model.encode(text)
    loss, predictions = loss_fn(hidden_states, metadata_targets)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# NOTE: MLX imports - will be available when MLX is installed
# import mlx.core as mx
# import mlx.nn as nn


# Metadata field definitions
EMOTIONS = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion",
    "curiosity", "desire", "disappointment", "disapproval", "disgust", "embarrassment",
    "excitement", "fear", "gratitude", "grief", "joy", "love", "nervousness", "optimism",
    "pride", "realization", "relief", "remorse", "sadness", "surprise", "neutral"
]

THOUGHT_TYPES = [
    "question", "statement", "reflection", "hypothesis", "instruction", "observation",
    "conclusion", "clarification", "synthesis", "analysis", "proposal", "validation"
]

COGNITIVE_STAGES = [
    "exploration", "problem_identification", "analysis", "hypothesis_formation",
    "synthesis", "validation", "implementation", "reflection", "integration"
]

PATTERNS = [
    "the_gate", "the_furnace", "the_form", "hold_pattern", "primitive_pattern",
    "service_pattern", "trinity_pattern", "clara_arc", "jeremy_arc", "none"
]

METADATA_FIELDS = {
    "emotion": EMOTIONS,
    "thought_type": THOUGHT_TYPES,
    "cognitive_stage": COGNITIVE_STAGES,
    "pattern": PATTERNS,
}


@dataclass
class MetadataHead:
    """
    Classification head for a single metadata field.

    Each head transforms the hidden state into logits for its classes.

    Architecture:
        hidden_states [batch, seq, hidden_dim]
        → pool (mean over seq) [batch, hidden_dim]
        → linear [batch, num_classes]
        → softmax → probabilities
    """

    field_name: str
    num_classes: int
    class_names: List[str]
    hidden_dim: int = 4096  # Llama hidden size

    # Weights - initialized when MLX available
    weight: Optional[Any] = field(default=None, repr=False)
    bias: Optional[Any] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Initialize weights."""
        # TODO: Initialize with MLX when available
        # self.weight = mx.random.normal((self.hidden_dim, self.num_classes)) * 0.02
        # self.bias = mx.zeros((self.num_classes,))
        pass

    def forward(self, hidden_states: Any) -> Tuple[Any, Any]:
        """
        Forward pass for classification head.

        Args:
            hidden_states: [batch, seq, hidden_dim] tensor

        Returns:
            logits: [batch, num_classes] tensor
            probabilities: [batch, num_classes] tensor
        """
        # TODO: Implement with MLX when available
        # pooled = mx.mean(hidden_states, axis=1)  # [batch, hidden_dim]
        # logits = mx.matmul(pooled, self.weight) + self.bias  # [batch, num_classes]
        # probabilities = mx.softmax(logits, axis=-1)
        # return logits, probabilities

        raise NotImplementedError("Requires MLX installation")

    def predict(self, hidden_states: Any) -> Tuple[List[str], Any]:
        """
        Predict class labels from hidden states.

        Args:
            hidden_states: [batch, seq, hidden_dim] tensor

        Returns:
            labels: List of predicted class names
            confidence: Confidence scores for predictions
        """
        logits, probs = self.forward(hidden_states)

        # TODO: Implement with MLX when available
        # indices = mx.argmax(probs, axis=-1)
        # labels = [self.class_names[i] for i in indices.tolist()]
        # confidence = mx.max(probs, axis=-1)
        # return labels, confidence

        raise NotImplementedError("Requires MLX installation")


@dataclass
class SeeingLoss:
    """
    The Seeing Loss Function.

    Trains the model to classify metadata fields instead of predicting next tokens.
    This is the paradigm shift from prediction to seeing.

    Loss Components:
        1. emotion_loss: Cross-entropy for emotion classification
        2. thought_type_loss: Cross-entropy for thought type classification
        3. cognitive_stage_loss: Cross-entropy for cognitive stage classification
        4. pattern_loss: Cross-entropy for pattern classification

    Total loss = weighted sum of component losses

    Why This Works:
        - Forces model to understand WHAT IS, not what comes next
        - 95% accuracy means internalized cognitive architecture
        - Each head learns a different aspect of Jeremy's seeing
    """

    metadata_fields: List[str] = field(
        default_factory=lambda: ["emotion", "thought_type", "cognitive_stage", "pattern"]
    )
    field_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "emotion": 1.0,
            "thought_type": 1.0,
            "cognitive_stage": 1.0,
            "pattern": 1.0,
        }
    )
    hidden_dim: int = 4096  # Llama Scout hidden size

    # Classification heads - one per metadata field
    heads: Dict[str, MetadataHead] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        """Initialize classification heads."""
        for field_name in self.metadata_fields:
            if field_name not in METADATA_FIELDS:
                raise ValueError(f"Unknown metadata field: {field_name}")

            classes = METADATA_FIELDS[field_name]
            self.heads[field_name] = MetadataHead(
                field_name=field_name,
                num_classes=len(classes),
                class_names=classes,
                hidden_dim=self.hidden_dim,
            )

    def forward(
        self,
        hidden_states: Any,
        targets: Dict[str, Any],
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Compute seeing loss.

        Args:
            hidden_states: [batch, seq, hidden_dim] from model encoder
            targets: Dict mapping field names to target class indices
                     {"emotion": [batch], "thought_type": [batch], ...}

        Returns:
            total_loss: Weighted sum of per-field losses
            loss_dict: Dict with per-field losses and predictions
        """
        total_loss = 0.0
        loss_dict = {}

        for field_name, head in self.heads.items():
            if field_name not in targets:
                continue

            # Forward pass through head
            logits, probs = head.forward(hidden_states)
            target = targets[field_name]

            # Cross-entropy loss
            # TODO: Implement with MLX when available
            # field_loss = mx.mean(
            #     mx.nn.cross_entropy(logits, target)
            # )
            field_loss = 0.0  # Placeholder

            # Weight and accumulate
            weight = self.field_weights.get(field_name, 1.0)
            total_loss += weight * field_loss

            # Store for logging
            loss_dict[f"{field_name}_loss"] = field_loss
            loss_dict[f"{field_name}_logits"] = logits
            loss_dict[f"{field_name}_probs"] = probs

        return total_loss, loss_dict

    def predict_metadata(
        self,
        hidden_states: Any,
    ) -> Dict[str, Tuple[List[str], Any]]:
        """
        Predict all metadata fields from hidden states.

        Args:
            hidden_states: [batch, seq, hidden_dim] from model encoder

        Returns:
            Dict mapping field names to (labels, confidence) tuples
        """
        predictions = {}

        for field_name, head in self.heads.items():
            labels, confidence = head.predict(hidden_states)
            predictions[field_name] = (labels, confidence)

        return predictions

    def compute_accuracy(
        self,
        hidden_states: Any,
        targets: Dict[str, Any],
    ) -> Dict[str, float]:
        """
        Compute accuracy per metadata field.

        This is the Jeremy Arc measurement - the primary success metric.

        Args:
            hidden_states: [batch, seq, hidden_dim] from model encoder
            targets: Dict mapping field names to target class indices

        Returns:
            Dict mapping field names to accuracy (0.0-1.0)
        """
        accuracies = {}

        for field_name, head in self.heads.items():
            if field_name not in targets:
                continue

            # Get predictions
            logits, probs = head.forward(hidden_states)

            # TODO: Implement with MLX when available
            # predicted_indices = mx.argmax(probs, axis=-1)
            # correct = mx.equal(predicted_indices, targets[field_name])
            # accuracy = mx.mean(correct.astype(mx.float32))
            # accuracies[field_name] = float(accuracy)

            accuracies[field_name] = 0.0  # Placeholder

        return accuracies

    def get_jeremy_arc(
        self,
        hidden_states: Any,
        targets: Dict[str, Any],
    ) -> float:
        """
        Compute overall Jeremy Arc accuracy.

        This is THE primary measure of Genesis readiness.
        95% Jeremy Arc = freeze Genesis v1.0

        Args:
            hidden_states: [batch, seq, hidden_dim] from model encoder
            targets: Dict mapping field names to target class indices

        Returns:
            Overall accuracy across all metadata fields (0.0-1.0)
        """
        accuracies = self.compute_accuracy(hidden_states, targets)

        if not accuracies:
            return 0.0

        # Weighted average across fields
        total = 0.0
        weight_sum = 0.0

        for field_name, acc in accuracies.items():
            weight = self.field_weights.get(field_name, 1.0)
            total += weight * acc
            weight_sum += weight

        return total / weight_sum if weight_sum > 0 else 0.0


def create_targets_from_labels(
    labels: List[Dict[str, str]],
    metadata_fields: Optional[List[str]] = None,
) -> Dict[str, List[int]]:
    """
    Convert label dicts to target indices for loss computation.

    Args:
        labels: List of dicts with metadata labels for each example
                [{"emotion": "joy", "thought_type": "reflection", ...}, ...]
        metadata_fields: Optional list of fields to convert (default: all)

    Returns:
        Dict mapping field names to lists of class indices
    """
    if metadata_fields is None:
        metadata_fields = list(METADATA_FIELDS.keys())

    targets: Dict[str, List[int]] = {field: [] for field in metadata_fields}

    for label_dict in labels:
        for field_name in metadata_fields:
            label = label_dict.get(field_name, "neutral" if field_name == "emotion" else "none")
            classes = METADATA_FIELDS[field_name]

            try:
                index = classes.index(label)
            except ValueError:
                # Unknown label - default to first class
                index = 0

            targets[field_name].append(index)

    return targets
