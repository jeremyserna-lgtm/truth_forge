"""
Constitutional AI Module
Truth Engine / Truth Forge

Self-critique and alignment system based on Canon Repair Doctrine.
"""

from .critic import (
    ConstitutionalCritic,
    ConstitutionalPipeline,
    ConstitutionalReport,
    CritiqueResult,
    EnforcementLevel,
    Principle,
    TrainingSignalGenerator,
)


__all__ = [
    "ConstitutionalCritic",
    "ConstitutionalPipeline",
    "ConstitutionalReport",
    "CritiqueResult",
    "Principle",
    "EnforcementLevel",
    "TrainingSignalGenerator",
]
