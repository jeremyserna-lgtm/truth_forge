"""Not-Me Production Service - Sovereign Digital Self Factory.

The Not-Me service orchestrates the complete production pipeline for
creating sovereign digital selves powered by LLaMA 4 Scout.

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    NOT-ME PRODUCTION                        │
    ├─────────────────────────────────────────────────────────────┤
    │  DATA LAYER (HOLD₁)                                         │
    │  ├── Data ingestion (emails, messages, documents)           │
    │  ├── Struggle filter (Swimming vs Drowning)                 │
    │  ├── Stage rating (Kegan 1-5)                               │
    │  └── Metadata enrichment (emotion, thought_type, mode)      │
    │                                                             │
    │  PROCESSING LAYER (AGENT)                                   │
    │  ├── Scout inference (seeing paradigm)                      │
    │  ├── Coherence anchor (hallucination prevention)            │
    │  ├── Inverted loss validation (no validation-seeking)       │
    │  └── Jeremy Arc verification (95% accuracy)                 │
    │                                                             │
    │  OUTPUT LAYER (HOLD₂)                                       │
    │  ├── Genesis model weights (frozen)                         │
    │  ├── Daughter LoRA adapters (per-customer)                  │
    │  └── Insight stream (knowledge atoms)                       │
    └─────────────────────────────────────────────────────────────┘

Usage:
    from truth_forge.services.not_me import NotMeService, get_not_me

    # Get singleton service
    service = get_not_me()

    # Process input through seeing paradigm
    insight = service.see(content, context)

    # Check production status
    status = service.get_status()

MOLT LINEAGE:
- Source: New creation for Not-Me infrastructure
- Version: 1.0.0
- Date: 2026-02-01
"""

from truth_forge.services.not_me.recursive_check import (
    CertificationChecklist,
    CognitiveFilter,
    CoherenceAnchor,
    CoherenceAnchorResult,
    ProofOfState,
    ProofOfStateStatus,
    RealityCheckProtocol,
    RecursiveCheck,
    RecursiveCheckReport,
    RecursiveCheckResult,
    certify_for_deployment,
    get_recursive_check,
)
from truth_forge.services.not_me.service import (
    NotMeService,
    get_not_me,
)
from truth_forge.services.not_me.truth_atom import (
    AtomTier,
    CognitiveSignature,
    StruggleFilterAction,
    StruggleFilterSignal,
    SurplusType,
    SurplusVector,
    TruthAtom,
    ValidatorAttestation,
    VerificationStatus,
    WorkProof,
)
from truth_forge.services.not_me.types import (
    CognitiveStage,
    InsightAtom,
    NotMeConfig,
    ProductionStatus,
    SeeingResult,
    TrainingLayer,
)
from truth_forge.services.not_me.validator import (
    JustificationOutcome,
    TruthAtomValidator,
    ValidationRequest,
    ValidationResult,
    ValidatorVerdict,
    get_validator,
)


__all__ = [
    # Core service
    "NotMeService",
    "get_not_me",
    # Configuration
    "NotMeConfig",
    # Results
    "SeeingResult",
    "InsightAtom",
    "ProductionStatus",
    # Cognitive architecture
    "CognitiveStage",
    "TrainingLayer",
    # Truth Atoms (Reciprocal Learning)
    "TruthAtom",
    "WorkProof",
    "SurplusVector",
    "SurplusType",
    "ValidatorAttestation",
    "CognitiveSignature",
    "VerificationStatus",
    # Validation (Bi-directional Loop)
    "TruthAtomValidator",
    "get_validator",
    "ValidationRequest",
    "ValidationResult",
    "ValidatorVerdict",
    "JustificationOutcome",
    # Recursive Check (Section 7.6 - Final Gate)
    "RecursiveCheck",
    "RecursiveCheckResult",
    "RecursiveCheckReport",
    "ProofOfState",
    "ProofOfStateStatus",
    "CognitiveFilter",
    "get_recursive_check",
    # Struggle Filter (Phase 0)
    "StruggleFilterSignal",
    "StruggleFilterAction",
    "AtomTier",
    # Coherence Anchor (Phase 2)
    "CoherenceAnchor",
    "CoherenceAnchorResult",
    "RealityCheckProtocol",
    # Certification (Final Gate)
    "CertificationChecklist",
    "certify_for_deployment",
]
