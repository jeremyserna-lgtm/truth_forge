"""Embedding generator for entity_embeddings schema.

Generates 6 task-specific 3072-dimensional embeddings per entity.
Supports:
- Gemini API (gemini-embedding-001) - production, 3072 dimensions
- Ollama local models - development, variable dimensions

Flow:
    entity_unified → entity_enrichments → entity_embeddings (this module)
    
Levels supported:
    - L4: Sentences
    - L5: Messages  
    - L8: Conversations
"""

from __future__ import annotations

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

import httpx

from .enrichments import (
    EntityEmbedding,
    EmbeddingBatch,
    EmbeddingTaskType,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Embedding Generator Protocol
# =============================================================================

class EmbeddingGenerator(ABC):
    """Abstract base class for embedding generators."""
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model name."""
        ...
    
    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Return the embedding dimensions."""
        ...
    
    @abstractmethod
    async def generate(
        self,
        text: str,
        task_type: EmbeddingTaskType,
    ) -> list[float]:
        """Generate embedding for text with specified task type."""
        ...
    
    async def generate_all_tasks(
        self,
        text: str,
    ) -> dict[EmbeddingTaskType, list[float]]:
        """Generate embeddings for all 6 task types.
        
        Returns dict mapping task type to embedding vector.
        """
        tasks = [
            EmbeddingTaskType.RETRIEVAL_DOCUMENT,
            EmbeddingTaskType.RETRIEVAL_QUERY,
            EmbeddingTaskType.SEMANTIC_SIMILARITY,
            EmbeddingTaskType.CLUSTERING,
            EmbeddingTaskType.CLASSIFICATION,
            EmbeddingTaskType.QUESTION_ANSWERING,
        ]
        
        results = {}
        for task_type in tasks:
            embedding = await self.generate(text, task_type)
            results[task_type] = embedding
        
        return results


# =============================================================================
# Gemini Embedding Generator (Production)
# =============================================================================

@dataclass
class GeminiConfig:
    """Configuration for Gemini embedding API."""
    api_key: Optional[str] = None
    model: str = "models/text-embedding-004"  # gemini-embedding-001 renamed
    dimensions: int = 3072
    timeout: float = 30.0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.environ.get("GOOGLE_API_KEY")


class GeminiEmbeddingGenerator(EmbeddingGenerator):
    """Generate embeddings using Google's Gemini API.
    
    Uses text-embedding-004 (formerly gemini-embedding-001) which produces
    3072-dimensional embeddings optimized for different task types.
    
    See: https://ai.google.dev/gemini-api/docs/embeddings
    """
    
    def __init__(self, config: Optional[GeminiConfig] = None):
        self.config = config or GeminiConfig()
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def model_name(self) -> str:
        return self.config.model
    
    @property
    def dimensions(self) -> int:
        return self.config.dimensions
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.config.timeout)
        return self._client
    
    def _task_type_to_api(self, task_type: EmbeddingTaskType) -> str:
        """Convert our task type to Gemini API task type."""
        mapping = {
            EmbeddingTaskType.RETRIEVAL_DOCUMENT: "RETRIEVAL_DOCUMENT",
            EmbeddingTaskType.RETRIEVAL_QUERY: "RETRIEVAL_QUERY",
            EmbeddingTaskType.SEMANTIC_SIMILARITY: "SEMANTIC_SIMILARITY",
            EmbeddingTaskType.CLUSTERING: "CLUSTERING",
            EmbeddingTaskType.CLASSIFICATION: "CLASSIFICATION",
            EmbeddingTaskType.QUESTION_ANSWERING: "QUESTION_ANSWERING",
        }
        return mapping[task_type]
    
    async def generate(
        self,
        text: str,
        task_type: EmbeddingTaskType,
    ) -> list[float]:
        """Generate embedding using Gemini API."""
        if not self.config.api_key:
            raise ValueError("GOOGLE_API_KEY not set")
        
        client = await self._get_client()
        
        url = f"https://generativelanguage.googleapis.com/v1beta/{self.config.model}:embedContent"
        
        payload = {
            "model": self.config.model,
            "content": {
                "parts": [{"text": text}]
            },
            "taskType": self._task_type_to_api(task_type),
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.config.api_key,
        }
        
        for attempt in range(self.config.max_retries):
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                embedding = data.get("embedding", {}).get("values", [])
                
                if len(embedding) != self.dimensions:
                    logger.warning(
                        f"Unexpected dimension: {len(embedding)}, expected {self.dimensions}"
                    )
                
                return embedding
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Gemini API error (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
            except Exception as e:
                logger.error(f"Gemini embedding error: {e}")
                raise
        
        return []
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# =============================================================================
# Ollama Embedding Generator (Development/Local)
# =============================================================================

@dataclass
class OllamaEmbeddingConfig:
    """Configuration for Ollama embedding generation."""
    host: str = "http://localhost:11434"
    model: str = "nomic-embed-text"  # 768 dimensions, good quality
    timeout: float = 60.0
    max_retries: int = 3


class OllamaEmbeddingGenerator(EmbeddingGenerator):
    """Generate embeddings using local Ollama models.
    
    Note: Ollama doesn't support task-specific embeddings like Gemini.
    All task types will use the same embedding model, so the 6 vectors
    will be identical (but this is acceptable for development).
    
    For production use, prefer GeminiEmbeddingGenerator.
    """
    
    def __init__(self, config: Optional[OllamaEmbeddingConfig] = None):
        self.config = config or OllamaEmbeddingConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self._dimensions: Optional[int] = None
    
    @property
    def model_name(self) -> str:
        return f"ollama:{self.config.model}"
    
    @property
    def dimensions(self) -> int:
        # Approximate dimensions for common models
        # Will be updated after first call
        return self._dimensions or 768  # nomic-embed-text default
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.config.timeout)
        return self._client
    
    async def generate(
        self,
        text: str,
        task_type: EmbeddingTaskType,
    ) -> list[float]:
        """Generate embedding using Ollama API.
        
        Note: task_type is ignored as Ollama doesn't support it.
        All embeddings use the same model regardless of task.
        """
        client = await self._get_client()
        
        url = f"{self.config.host}/api/embeddings"
        
        payload = {
            "model": self.config.model,
            "prompt": text,
        }
        
        for attempt in range(self.config.max_retries):
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                embedding = data.get("embedding", [])
                
                # Update dimensions if not set
                if self._dimensions is None and embedding:
                    self._dimensions = len(embedding)
                    logger.info(f"Ollama embedding dimensions: {self._dimensions}")
                
                return embedding
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Ollama API error (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
            except httpx.ConnectError as e:
                logger.error(f"Cannot connect to Ollama at {self.config.host}: {e}")
                raise
            except Exception as e:
                logger.error(f"Ollama embedding error: {e}")
                raise
        
        return []
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# =============================================================================
# Entity Embedding Service
# =============================================================================

class EntityEmbeddingService:
    """Service for generating embeddings for entities.
    
    Coordinates embedding generation for L4, L5, and L8 entities,
    outputting to entity_embeddings schema.
    
    Usage:
        service = EntityEmbeddingService(
            generator=GeminiEmbeddingGenerator()
        )
        
        # Generate embedding for single entity
        embedding = await service.embed_entity(
            entity_id="msg_123",
            level_code="L5",
            text="Hello, how are you?"
        )
        
        # Generate batch of embeddings
        batch = await service.embed_batch([
            ("sent_1", "L4", "First sentence."),
            ("sent_2", "L4", "Second sentence."),
        ])
    """
    
    def __init__(
        self,
        generator: EmbeddingGenerator,
        parallel_tasks: int = 1,  # Gemini rate limits are strict
    ):
        self.generator = generator
        self.parallel_tasks = parallel_tasks
    
    async def embed_entity(
        self,
        entity_id: str,
        level_code: str,
        text: str,
    ) -> EntityEmbedding:
        """Generate all 6 task embeddings for a single entity.
        
        Args:
            entity_id: The entity's unique identifier
            level_code: L4, L5, or L8
            text: The text to embed
            
        Returns:
            EntityEmbedding with all 6 vectors populated
        """
        embedding = EntityEmbedding.from_entity_unified(
            entity_id=entity_id,
            level_code=level_code,
            text=text,
            embedding_model=self.generator.model_name,
        )
        embedding.embedding_dimensions = self.generator.dimensions
        
        # Generate all 6 task-specific embeddings
        all_embeddings = await self.generator.generate_all_tasks(text)
        
        for task_type, vector in all_embeddings.items():
            embedding.set_embedding(task_type, vector)
        
        return embedding
    
    async def embed_batch(
        self,
        entities: list[tuple[str, str, str]],  # (entity_id, level_code, text)
        batch_id: Optional[str] = None,
    ) -> EmbeddingBatch:
        """Generate embeddings for a batch of entities.
        
        Args:
            entities: List of (entity_id, level_code, text) tuples
            batch_id: Optional identifier for this batch
            
        Returns:
            EmbeddingBatch with all entity embeddings
        """
        batch = EmbeddingBatch(batch_id=batch_id)
        
        for entity_id, level_code, text in entities:
            try:
                embedding = await self.embed_entity(
                    entity_id=entity_id,
                    level_code=level_code,
                    text=text,
                )
                batch.add(embedding)
                
                logger.debug(
                    f"Embedded {entity_id} ({level_code}): "
                    f"{len(embedding.populated_tasks)}/6 tasks"
                )
                
            except Exception as e:
                logger.error(f"Failed to embed {entity_id}: {e}")
                # Add empty embedding to track failure
                batch.add(EntityEmbedding(
                    entity_id=entity_id,
                    level_code=level_code,
                    embedding_model=self.generator.model_name,
                ))
        
        return batch
    
    async def embed_from_enrichment(
        self,
        enriched_entity: dict[str, Any],
    ) -> EntityEmbedding:
        """Generate embeddings from an enriched entity.
        
        Expects a dictionary with entity_unified + entity_enrichments fields.
        """
        entity_id = enriched_entity.get("entity_id", "")
        level_code = enriched_entity.get("level_code", "L5")
        
        # Use enrichment_text if available, otherwise fall back to content
        text = enriched_entity.get("enrichment_text") or enriched_entity.get("content", "")
        
        return await self.embed_entity(
            entity_id=entity_id,
            level_code=level_code,
            text=text,
        )
    
    async def close(self):
        """Close the underlying generator."""
        if hasattr(self.generator, 'close'):
            await self.generator.close()


# =============================================================================
# Factory Function
# =============================================================================

def create_embedding_service(
    use_gemini: bool = True,
    gemini_api_key: Optional[str] = None,
    ollama_host: str = "http://localhost:11434",
    ollama_model: str = "nomic-embed-text",
) -> EntityEmbeddingService:
    """Create an embedding service with appropriate generator.
    
    Args:
        use_gemini: If True, use Gemini API (production). 
                   If False, use Ollama (development).
        gemini_api_key: API key for Gemini (or use GOOGLE_API_KEY env var)
        ollama_host: Ollama server URL
        ollama_model: Ollama embedding model
        
    Returns:
        Configured EntityEmbeddingService
    """
    if use_gemini:
        config = GeminiConfig(api_key=gemini_api_key)
        generator = GeminiEmbeddingGenerator(config)
    else:
        config = OllamaEmbeddingConfig(
            host=ollama_host,
            model=ollama_model,
        )
        generator = OllamaEmbeddingGenerator(config)
    
    return EntityEmbeddingService(generator)


# =============================================================================
# CLI for Testing
# =============================================================================

async def _test_embeddings():
    """Test embedding generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test embedding generation")
    parser.add_argument("--gemini", action="store_true", help="Use Gemini API")
    parser.add_argument("--ollama", action="store_true", help="Use Ollama (default)")
    parser.add_argument("--text", default="Hello, this is a test message.", help="Text to embed")
    args = parser.parse_args()
    
    use_gemini = args.gemini and not args.ollama
    
    print(f"Using: {'Gemini' if use_gemini else 'Ollama'}")
    print(f"Text: {args.text}")
    print()
    
    service = create_embedding_service(use_gemini=use_gemini)
    
    try:
        embedding = await service.embed_entity(
            entity_id="test_001",
            level_code="L5",
            text=args.text,
        )
        
        print(f"Entity ID: {embedding.entity_id}")
        print(f"Level: {embedding.level_code}")
        print(f"Model: {embedding.embedding_model}")
        print(f"Dimensions: {embedding.embedding_dimensions}")
        print(f"Complete: {embedding.is_complete}")
        print(f"Populated tasks: {embedding.populated_tasks}")
        print()
        
        for task in EmbeddingTaskType:
            match task:
                case EmbeddingTaskType.RETRIEVAL_DOCUMENT:
                    vec = embedding.embedding_retrieval
                case EmbeddingTaskType.RETRIEVAL_QUERY:
                    vec = embedding.embedding_query
                case EmbeddingTaskType.SEMANTIC_SIMILARITY:
                    vec = embedding.embedding_similarity
                case EmbeddingTaskType.CLUSTERING:
                    vec = embedding.embedding_clustering
                case EmbeddingTaskType.CLASSIFICATION:
                    vec = embedding.embedding_classification
                case EmbeddingTaskType.QUESTION_ANSWERING:
                    vec = embedding.embedding_qa
            
            if vec:
                print(f"{task.value}: [{vec[0]:.6f}, {vec[1]:.6f}, ... ] ({len(vec)} dims)")
        
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(_test_embeddings())
