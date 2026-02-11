"""
Truth Engine — Verification and Coherence Layer
Truth Forge

The Engine organism: responsible for truth verification, coherence checking,
and constitutional alignment of AI outputs.
"""

from .pipeline import (
    UnifiedVerificationPipeline,
    VerificationRequest,
    VerificationResult,
    quick_critique,
    quick_verify_coherence,
)


__version__ = "1.0.0"
__all__ = [
    "UnifiedVerificationPipeline",
    "VerificationRequest",
    "VerificationResult",
    "quick_verify_coherence",
    "quick_critique",
]
