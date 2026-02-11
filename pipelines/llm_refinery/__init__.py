"""LLM Refinery Pipeline - Replace spaCy stages with LLM-based processing.

This pipeline processes conversation data into the L2-L8 hierarchical structure
using local LLMs (via Ollama) instead of rigid Python/spaCy rules.

The L2-L8 Layers:
    L8: Conversation - The root, entire conversation
    L7: Topic Segment - Semantic groupings within conversation
    L6: Turn - Speaker change boundaries
    L5: Message - Individual utterances
    L4: Sentence - Grammatical sentence units
    L3: Span - Phrases/clauses with meaning
    L2: Word - Tokens with semantic attributes

Output Tables:
    - entity_unified (34 fields): Base entity storage
    - entity_enrichments (139 fields): Enriched entity data with sentiment,
      emotions, readability, keywords, topics, content classification,
      and Sovereign Architecture metrics (cognitive stage, struggle filter,
      metabolic stage, Total Resonance, etc.)
    - entity_embeddings (6 task vectors): 3072-dim embeddings per entity
      for retrieval, query, similarity, clustering, classification, and QA

Integration with Central Services:
    - IdentityService: Standardized ID generation
    - BaseService: HOLD pattern, structured logging, lifecycle
    - LoggingService: Centralized logging
    - ServiceFactory: Dependency injection

Usage (Hardened Service):
    from truth_forge.services.factory import get_service
    
    refinery = get_service("llm_refinery")
    result = refinery.process_conversation(conversation_data)

Usage (Standalone Processor):
    from pipelines.llm_refinery import LLMRefineryProcessor
    
    processor = LLMRefineryProcessor()
    results = processor.process_batch(conversations)

Usage (Embedding Service):
    from pipelines.llm_refinery import create_embedding_service, EntityEmbedding
    
    service = create_embedding_service(use_gemini=True)
    embedding = await service.embed_entity("msg_123", "L5", "Hello world")
"""

from .processor import LLMRefineryProcessor, ProcessorConfig
from .models import (
    ConversationL8,
    TopicSegmentL7,
    TurnL6,
    MessageL5,
    SentenceL4,
    SpanL3,
    WordL2,
)
from .enrichments import (
    EntityEnrichment,
    SentimentEnrichment,
    EmotionEnrichment,
    ReadabilityEnrichment,
    KeywordEnrichment,
    TopicEnrichment,
    ContentClassification,
    HateSpeechEnrichment,
    # Sovereign Architecture enrichments
    CognitiveStageEnrichment,
    StruggleFilterEnrichment,
    MetabolicStageEnrichment,
    ConfidenceCalibrationEnrichment,
    SourceAttributionEnrichment,
    TemporalLensEnrichment,
    OperationalCycleEnrichment,
    JeremyArcEnrichment,
    TotalResonanceEnrichment,
    # Entity Embeddings (for entity_embeddings table)
    EmbeddingTaskType,
    EntityEmbedding,
    EmbeddingBatch,
    # Vocabulary constants
    BANNED_VOCABULARY,
    MANIFESTATION_VOCABULARY,
    # Factory function
    create_enrichment_from_llm,
)

# Embedding service
from .embeddings import (
    EmbeddingGenerator,
    GeminiEmbeddingGenerator,
    GeminiConfig,
    OllamaEmbeddingGenerator,
    OllamaEmbeddingConfig,
    EntityEmbeddingService,
    create_embedding_service,
)

# Hardened service (requires truth_forge.services)
try:
    from .service import LLMRefineryService, RefineryConfig, create_refinery_service
    _SERVICE_AVAILABLE = True
except ImportError:
    _SERVICE_AVAILABLE = False
    LLMRefineryService = None
    RefineryConfig = None
    create_refinery_service = None

__all__ = [
    # Core models
    "LLMRefineryProcessor",
    "ConversationL8",
    "TopicSegmentL7",
    "TurnL6",
    "MessageL5",
    "SentenceL4",
    "SpanL3",
    "WordL2",
    # Standard enrichments
    "EntityEnrichment",
    "SentimentEnrichment",
    "EmotionEnrichment",
    "ReadabilityEnrichment",
    "KeywordEnrichment",
    "TopicEnrichment",
    "ContentClassification",
    "HateSpeechEnrichment",
    # Sovereign Architecture enrichments
    "CognitiveStageEnrichment",
    "StruggleFilterEnrichment",
    "MetabolicStageEnrichment",
    "ConfidenceCalibrationEnrichment",
    "SourceAttributionEnrichment",
    "TemporalLensEnrichment",
    "OperationalCycleEnrichment",
    "JeremyArcEnrichment",
    "TotalResonanceEnrichment",
    # Entity Embeddings (for entity_embeddings table)
    "EmbeddingTaskType",
    "EntityEmbedding",
    "EmbeddingBatch",
    "EmbeddingGenerator",
    "GeminiEmbeddingGenerator",
    "GeminiConfig",
    "OllamaEmbeddingGenerator",
    "OllamaEmbeddingConfig",
    "EntityEmbeddingService",
    "create_embedding_service",
    # Vocabulary constants
    "BANNED_VOCABULARY",
    "MANIFESTATION_VOCABULARY",
    # Factory function
    "create_enrichment_from_llm",
]
