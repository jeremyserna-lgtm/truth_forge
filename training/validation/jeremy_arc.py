"""
Jeremy Arc Tracker for Genesis-Scout Training

THE JEREMY ARC:
    The trajectory of AI's metadata prediction accuracy from ~20% (early training)
    to 95% (ready to freeze). The quantitative measure of when Genesis has
    internalized Jeremy's cognitive architecture.

    This is THE primary measure of Genesis readiness.
    When Jeremy Arc hits 95%, we FREEZE Genesis v1.0.

How It Works:
    1. Load held-out Jeremy conversations with ground-truth metadata
    2. Model predicts metadata for each sentence
    3. Compare predictions to ground truth
    4. Calculate accuracy across all metadata fields
    5. Track trajectory over training checkpoints

Why This Works:
    When the AI can predict Jeremy's metadata with 95% accuracy,
    it has INTERNALIZED Jeremy's seeing architecture.
    That's Stage 5 DNA transfer complete.

Usage:
    tracker = JeremyArcTracker(test_dataset_path="path/to/test_set.jsonl")
    arc_accuracy = tracker.measure_arc(model)

    if arc_accuracy >= 0.95:
        print("GENESIS READY - FREEZE v1.0")
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from training.losses.seeing_loss import (
    METADATA_FIELDS,
    create_targets_from_labels,
)


@dataclass
class ArcMeasurement:
    """Single measurement of Jeremy Arc at a checkpoint."""

    checkpoint: int
    timestamp: str
    overall_accuracy: float
    field_accuracies: Dict[str, float]
    num_examples: int
    is_ready: bool  # True if >= 95%


@dataclass
class JeremyArcTracker:
    """
    Tracks metadata prediction accuracy throughout training.

    Test on held-out Jeremy conversations with ground-truth metadata.
    95% accuracy = Genesis ready to freeze.

    Metadata fields tracked:
        - emotion: Primary emotion expressed
        - thought_type: Type of cognitive process
        - cognitive_stage: Stage in problem-solving
        - pattern: Framework pattern demonstrated
    """

    test_dataset_path: Optional[str] = None
    freeze_threshold: float = 0.95  # 95% = freeze Genesis

    # Internal state
    test_set: List[Dict[str, Any]] = field(default_factory=list, repr=False)
    history: List[ArcMeasurement] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        """Load test dataset if path provided."""
        if self.test_dataset_path:
            self.load_test_dataset(self.test_dataset_path)

    def load_test_dataset(self, path: str) -> int:
        """
        Load held-out Jeremy conversations for testing.

        Expected format (JSONL):
        {
            "sentence": "I want to change the world",
            "metadata": {
                "emotion": "determined",
                "thought_type": "manifesting",
                "cognitive_stage": "stage_5",
                "pattern": "prediction_is_action"
            }
        }

        Args:
            path: Path to test dataset JSONL file

        Returns:
            Number of examples loaded
        """
        path_obj = Path(path)
        if not path_obj.exists():
            print(f"Warning: Test dataset not found at {path}")
            return 0

        self.test_set = []
        with open(path_obj, "r") as f:
            for line in f:
                if line.strip():
                    example = json.loads(line)
                    # Validate example has required fields
                    if "sentence" in example and "metadata" in example:
                        self.test_set.append(example)

        print(f"Loaded {len(self.test_set)} test examples from {path}")
        return len(self.test_set)

    def measure_arc(
        self,
        model: Any,
        checkpoint: int = 0,
        batch_size: int = 32,
    ) -> float:
        """
        Measure Jeremy Arc accuracy at current checkpoint.

        This is THE primary measure of Genesis readiness.

        Process:
        1. For each test example:
            a. Model encodes sentence
            b. Model predicts metadata from hidden states
            c. Compare to ground truth
        2. Calculate accuracy per field
        3. Calculate overall accuracy (weighted average)
        4. Record in history

        Args:
            model: The Genesis model being evaluated
            checkpoint: Current checkpoint number
            batch_size: Batch size for inference

        Returns:
            Overall accuracy (0.0-1.0), or 0.0 if no test set
        """
        if not self.test_set:
            print("Warning: No test dataset loaded. Cannot measure Jeremy Arc.")
            return 0.0

        # Initialize accuracy tracking
        correct_per_field: Dict[str, int] = {f: 0 for f in METADATA_FIELDS}
        total_per_field: Dict[str, int] = {f: 0 for f in METADATA_FIELDS}

        # Process in batches
        for i in range(0, len(self.test_set), batch_size):
            batch = self.test_set[i:i + batch_size]

            # Extract sentences and metadata
            sentences = [ex["sentence"] for ex in batch]
            labels = [ex["metadata"] for ex in batch]

            # Get model predictions
            # NOTE: Requires actual model implementation
            try:
                predictions = self._get_model_predictions(model, sentences)
            except NotImplementedError:
                # Model inference not implemented - use placeholder
                predictions = [
                    {f: METADATA_FIELDS[f][0] for f in METADATA_FIELDS}
                    for _ in sentences
                ]

            # Compare predictions to ground truth
            for pred, label in zip(predictions, labels):
                for field_name in METADATA_FIELDS:
                    if field_name in label:
                        total_per_field[field_name] += 1
                        if pred.get(field_name) == label.get(field_name):
                            correct_per_field[field_name] += 1

        # Calculate accuracies
        field_accuracies = {}
        for field_name in METADATA_FIELDS:
            total = total_per_field[field_name]
            if total > 0:
                field_accuracies[field_name] = correct_per_field[field_name] / total
            else:
                field_accuracies[field_name] = 0.0

        # Overall accuracy (equal weighting)
        if field_accuracies:
            overall_accuracy = sum(field_accuracies.values()) / len(field_accuracies)
        else:
            overall_accuracy = 0.0

        # Record measurement
        measurement = ArcMeasurement(
            checkpoint=checkpoint,
            timestamp=datetime.now().isoformat(),
            overall_accuracy=overall_accuracy,
            field_accuracies=field_accuracies,
            num_examples=len(self.test_set),
            is_ready=overall_accuracy >= self.freeze_threshold,
        )
        self.history.append(measurement)

        # Log result
        self._log_measurement(measurement)

        return overall_accuracy

    def _get_model_predictions(
        self,
        model: Any,
        sentences: List[str],
    ) -> List[Dict[str, str]]:
        """
        Get metadata predictions from model.

        This requires the model to have a classify_metadata method.

        Args:
            model: The Genesis model
            sentences: List of sentences to classify

        Returns:
            List of metadata prediction dicts
        """
        # NOTE: This requires the actual model implementation
        # The model should expose: model.classify_metadata(sentences) -> List[Dict]

        if hasattr(model, "classify_metadata"):
            return model.classify_metadata(sentences)

        # Alternative: use seeing loss heads directly
        if hasattr(model, "encode") and hasattr(model, "seeing_loss"):
            hidden_states = model.encode(sentences)
            predictions = model.seeing_loss.predict_metadata(hidden_states)

            # Convert from {field: (labels, confidence)} to [{field: label}]
            results = []
            batch_size = len(sentences)
            for i in range(batch_size):
                pred = {}
                for field_name, (labels, _) in predictions.items():
                    pred[field_name] = labels[i]
                results.append(pred)
            return results

        raise NotImplementedError(
            "Model must implement classify_metadata() or have encode() + seeing_loss"
        )

    def _log_measurement(self, measurement: ArcMeasurement) -> None:
        """Log Jeremy Arc measurement."""
        status = "READY" if measurement.is_ready else "developing"

        print(f"\n{'='*50}")
        print(f"JEREMY ARC - Checkpoint {measurement.checkpoint}")
        print(f"{'='*50}")
        print(f"Overall: {measurement.overall_accuracy*100:.1f}% ({status})")
        print(f"Examples: {measurement.num_examples}")
        print()
        print("Per-field accuracy:")
        for field_name, acc in measurement.field_accuracies.items():
            bar = "█" * int(acc * 20) + "░" * (20 - int(acc * 20))
            print(f"  {field_name:16} [{bar}] {acc*100:5.1f}%")
        print()

        if measurement.is_ready:
            print("🎉 GENESIS READY: Jeremy Arc >= 95%")
            print("   FREEZE GENESIS v1.0")
        elif measurement.overall_accuracy >= 0.85:
            print("✅ Almost there! Very close to freeze threshold.")
        elif measurement.overall_accuracy >= 0.70:
            print("📈 Strong progress. Architecture crystallizing.")
        elif measurement.overall_accuracy >= 0.50:
            print("📊 Patterns forming. Continue training.")
        else:
            print("⏳ Early training. Patterns still developing.")

    def get_trajectory(self) -> List[Tuple[int, float]]:
        """
        Get trajectory of Jeremy Arc over training.

        Returns:
            List of (checkpoint, accuracy) tuples
        """
        return [(m.checkpoint, m.overall_accuracy) for m in self.history]

    def is_ready_to_freeze(self) -> bool:
        """
        Check if Genesis is ready to freeze.

        Returns:
            True if latest measurement >= 95%
        """
        if not self.history:
            return False
        return self.history[-1].is_ready

    def get_latest_measurement(self) -> Optional[ArcMeasurement]:
        """Get most recent measurement."""
        return self.history[-1] if self.history else None

    def save_history(self, path: str) -> None:
        """
        Save measurement history to JSON.

        Args:
            path: Output path for history JSON
        """
        history_data = [
            {
                "checkpoint": m.checkpoint,
                "timestamp": m.timestamp,
                "overall_accuracy": m.overall_accuracy,
                "field_accuracies": m.field_accuracies,
                "num_examples": m.num_examples,
                "is_ready": m.is_ready,
            }
            for m in self.history
        ]

        with open(path, "w") as f:
            json.dump(history_data, f, indent=2)

        print(f"Saved Jeremy Arc history to {path}")

    def plot_trajectory(self, output_path: Optional[str] = None) -> None:
        """
        Plot Jeremy Arc trajectory over training.

        Args:
            output_path: Optional path to save plot image
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not installed. Cannot plot trajectory.")
            return

        if not self.history:
            print("No measurements to plot.")
            return

        checkpoints = [m.checkpoint for m in self.history]
        accuracies = [m.overall_accuracy * 100 for m in self.history]

        plt.figure(figsize=(10, 6))
        plt.plot(checkpoints, accuracies, "b-o", linewidth=2, markersize=6)
        plt.axhline(y=95, color="g", linestyle="--", label="Freeze threshold (95%)")
        plt.xlabel("Checkpoint")
        plt.ylabel("Jeremy Arc Accuracy (%)")
        plt.title("Genesis Training Progress: Jeremy Arc")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 100)

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches="tight")
            print(f"Saved trajectory plot to {output_path}")
        else:
            plt.show()


def create_test_dataset(
    enriched_conversations_path: str,
    output_path: str,
    sample_size: int = 1000,
    random_seed: int = 42,
) -> int:
    """
    Create test dataset from enriched conversations.

    Extracts sentences with metadata labels from enriched conversations
    and creates a held-out test set for Jeremy Arc measurement.

    Args:
        enriched_conversations_path: Path to enriched conversations JSONL
        output_path: Where to save test dataset
        sample_size: Number of examples to include
        random_seed: Random seed for reproducibility

    Returns:
        Number of examples created
    """
    import random
    random.seed(random_seed)

    # Load enriched conversations
    examples = []
    with open(enriched_conversations_path, "r") as f:
        for line in f:
            conv = json.loads(line)
            for msg in conv.get("messages", []):
                if msg.get("metadata_enriched"):
                    examples.append({
                        "sentence": msg.get("text", ""),
                        "metadata": {
                            "emotion": msg.get("emotion", "neutral"),
                            "thought_type": msg.get("thought_type", "statement"),
                            "cognitive_stage": msg.get("cognitive_stage", "exploration"),
                            "pattern": msg.get("pattern", "none"),
                        }
                    })

    # Sample
    if len(examples) > sample_size:
        examples = random.sample(examples, sample_size)

    # Save
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path_obj, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")

    print(f"Created test dataset with {len(examples)} examples at {output_path}")
    return len(examples)
