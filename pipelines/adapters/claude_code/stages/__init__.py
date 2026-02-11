"""Stage registry for Claude Code pipeline.

Maps stage names to implementation classes.
"""

from .stage_0_assessment import AssessmentStage
from .stage_1_extraction import ExtractionStage
from .stage_2_cleaning import CleaningStage
from .stage_3_identity_gate import IdentityGateStage
from .stage_4_staging import StagingStage
from .stage_5_l1_tokens import L1TokensStage
from .stage_6_l3_sentences import L3SentencesStage
from .remaining_stages import (
    L5MessagesStage,
    L8ConversationsStage,
    EnrichmentPlaceholderStage,
    AggregationStage,
    ValidationStage,
    PromotionStage,
)


STAGE_REGISTRY = {
    "stage_0": AssessmentStage,
    "stage_1": ExtractionStage,
    "stage_2": CleaningStage,
    "stage_3": IdentityGateStage,
    "stage_4": StagingStage,
    "stage_5": L1TokensStage,
    "stage_6": L3SentencesStage,
    "stage_7": L5MessagesStage,
    "stage_8": L8ConversationsStage,
    "stage_9": EnrichmentPlaceholderStage,
    "stage_10": EnrichmentPlaceholderStage,
    "stage_11": EnrichmentPlaceholderStage,
    "stage_12": EnrichmentPlaceholderStage,
    "stage_13": EnrichmentPlaceholderStage,
    "stage_14": AggregationStage,
    "stage_15": ValidationStage,
    "stage_16": PromotionStage,
}


__all__ = ["STAGE_REGISTRY"]
