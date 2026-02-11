"""
Loss Functions for Genesis-Scout Training

The Seeing Paradigm: metadata classification, not next-token prediction.
"""

from training.losses.seeing_loss import (
    SeeingLoss,
    MetadataHead,
    METADATA_FIELDS,
)
from training.losses.coherence_loss import (
    CoherenceLoss,
    compute_coherence_aware_reward,
)

__all__ = [
    "SeeingLoss",
    "MetadataHead",
    "METADATA_FIELDS",
    "CoherenceLoss",
    "compute_coherence_aware_reward",
]
