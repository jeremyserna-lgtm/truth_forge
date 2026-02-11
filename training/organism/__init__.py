"""
THE AUTONOMOUS TRAINING ORGANISM

Start it. Walk away. Come back to products.

Usage:
    from training.organism import TrainingOrganism

    organism = TrainingOrganism(corpus_path="data/genesis_corpus/")
    organism.live()  # Never stops
"""

from .training_organism import (
    TrainingOrganism,
    TrainingExperiment,
    TrainedProduct,
    InteractionResult,
    Fate,
    Phase,
)

__all__ = [
    "TrainingOrganism",
    "TrainingExperiment",
    "TrainedProduct",
    "InteractionResult",
    "Fate",
    "Phase",
]
