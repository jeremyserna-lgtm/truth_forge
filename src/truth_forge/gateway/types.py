"""Primitive Gateway Types - Data structures for LLM operations.

These types provide strong typing and validation for all gateway operations.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/gateway/types.py
- Version: 2.0.0
- Date: 2026-01-26
- Changes: Modern type hints, datetime.UTC
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class ModelProvider(Enum):
    """Supported LLM providers."""

    CLAUDE = "claude"
    GEMINI = "gemini"
    OLLAMA = "ollama"

    @classmethod
    def from_string(cls, value: str) -> ModelProvider:
        """Convert string to ModelProvider."""
        value_lower = value.lower()
        for provider in cls:
            if provider.value == value_lower:
                return provider
        msg = f"Unknown provider: {value}"
        raise ValueError(msg)


@dataclass
class ModelConfig:
    """Configuration for a specific model.

    Attributes:
        provider: The LLM provider.
        model: Model identifier (e.g., "claude-3-5-sonnet-20241022").
        max_tokens: Maximum response tokens.
        temperature: Sampling temperature (0.0-1.0).
        cost_per_1k_input: Cost per 1000 input tokens in USD.
        cost_per_1k_output: Cost per 1000 output tokens in USD.
        supports_json: Whether model supports JSON mode.
        supports_streaming: Whether model supports streaming.
        supports_tools: Whether model supports tool use.
    """

    provider: ModelProvider
    model: str
    max_tokens: int = 4096
    temperature: float = 0.7
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    supports_json: bool = True
    supports_streaming: bool = True
    supports_tools: bool = False

    @property
    def is_free(self) -> bool:
        """Check if this model is free to use."""
        return self.cost_per_1k_input == 0.0 and self.cost_per_1k_output == 0.0


# Pre-configured models
MODELS: dict[str, ModelConfig] = {
    # Claude models
    "claude-opus": ModelConfig(
        provider=ModelProvider.CLAUDE,
        model="claude-opus-4-5-20251101",
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
        supports_tools=True,
    ),
    "claude-sonnet": ModelConfig(
        provider=ModelProvider.CLAUDE,
        model="claude-sonnet-4-20250514",
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        supports_tools=True,
    ),
    "claude-haiku": ModelConfig(
        provider=ModelProvider.CLAUDE,
        model="claude-3-5-haiku-20241022",
        cost_per_1k_input=0.0008,
        cost_per_1k_output=0.004,
        supports_tools=True,
    ),
    # Gemini models
    "gemini-pro": ModelConfig(
        provider=ModelProvider.GEMINI,
        model="gemini-2.0-flash",
        cost_per_1k_input=0.000125,
        cost_per_1k_output=0.000375,
    ),
    "gemini-flash": ModelConfig(
        provider=ModelProvider.GEMINI,
        model="gemini-2.0-flash-lite",
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
    ),
    # Ollama models (local, free)
    "ollama-llama": ModelConfig(
        provider=ModelProvider.OLLAMA,
        model="llama3.2",
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        supports_tools=False,
    ),
    "ollama-mistral": ModelConfig(
        provider=ModelProvider.OLLAMA,
        model="mistral",
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
    ),
    "ollama-embed": ModelConfig(
        provider=ModelProvider.OLLAMA,
        model="bge-large",
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        supports_streaming=False,
    ),
}


def get_model_config(name: str) -> ModelConfig:
    """Get a pre-configured model by name."""
    if name not in MODELS:
        msg = f"Unknown model: {name}. Available: {list(MODELS.keys())}"
        raise ValueError(msg)
    return MODELS[name]


@dataclass
class CompletionRequest:
    """Request for LLM completion.

    Attributes:
        prompt: The prompt or task description.
        content: Optional content to process.
        model: Model name or ModelConfig.
        max_tokens: Override max tokens.
        temperature: Override temperature.
        as_json: Request JSON response.
        system: System prompt.
        tools: Tool definitions for tool use.
        cache_key: Optional cache key for response caching.
    """

    prompt: str
    content: str | None = None
    model: str | ModelConfig = "claude-haiku"
    max_tokens: int | None = None
    temperature: float | None = None
    as_json: bool = False
    system: str | None = None
    tools: list[dict[str, Any]] | None = None
    cache_key: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_config(self) -> ModelConfig:
        """Get the ModelConfig for this request."""
        if isinstance(self.model, ModelConfig):
            return self.model
        return get_model_config(self.model)


@dataclass
class CompletionResponse:
    """Response from LLM completion.

    Attributes:
        content: The response content.
        model: Model used.
        provider: Provider used.
        input_tokens: Number of input tokens.
        output_tokens: Number of output tokens.
        cost: Estimated cost in USD.
        latency_ms: Response latency in milliseconds.
        cached: Whether response was from cache.
        timestamp: When response was generated.
        tool_calls: Tool calls if tools were used.
        raw_response: Full provider response (optional).
    """

    content: str
    model: str
    provider: ModelProvider
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    latency_ms: float = 0.0
    cached: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    tool_calls: list[dict[str, Any]] | None = None
    raw_response: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider.value,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.cost,
            "latency_ms": self.latency_ms,
            "cached": self.cached,
            "timestamp": self.timestamp.isoformat(),
            "tool_calls": self.tool_calls,
        }


@dataclass
class EmbeddingRequest:
    """Request for text embedding.

    Attributes:
        text: Text to embed.
        model: Embedding model.
        dimensions: Output dimensions (if supported).
    """

    text: str | list[str]
    model: str = "ollama-embed"
    dimensions: int | None = None

    @property
    def texts(self) -> list[str]:
        """Get texts as list."""
        if isinstance(self.text, str):
            return [self.text]
        return self.text


@dataclass
class EmbeddingResponse:
    """Response from embedding request.

    Attributes:
        embeddings: List of embedding vectors.
        model: Model used.
        dimensions: Embedding dimensions.
        total_tokens: Total tokens processed.
        cost: Estimated cost.
    """

    embeddings: list[list[float]]
    model: str
    dimensions: int
    total_tokens: int = 0
    cost: float = 0.0

    def __getitem__(self, index: int) -> list[float]:
        """Get embedding by index."""
        return self.embeddings[index]

    def __len__(self) -> int:
        """Number of embeddings."""
        return len(self.embeddings)


# =============================================================================
# EXCEPTIONS
# =============================================================================


class GatewayError(Exception):
    """Base exception for gateway errors."""

    def __init__(self, message: str, provider: str | None = None) -> None:
        self.provider = provider
        super().__init__(message)


class ProviderError(GatewayError):
    """Error from a specific provider."""

    def __init__(
        self,
        message: str,
        provider: str,
        status_code: int | None = None,
        response: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.response = response
        super().__init__(message, provider)


class RateLimitError(ProviderError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str,
        provider: str,
        retry_after: float | None = None,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, provider, status_code=429)


class CostLimitError(GatewayError):
    """Cost limit exceeded."""

    def __init__(
        self,
        message: str,
        current_cost: float,
        limit: float,
    ) -> None:
        self.current_cost = current_cost
        self.limit = limit
        super().__init__(message)


__all__ = [
    # Enums
    "ModelProvider",
    # Configs
    "ModelConfig",
    "MODELS",
    "get_model_config",
    # Requests/Responses
    "CompletionRequest",
    "CompletionResponse",
    "EmbeddingRequest",
    "EmbeddingResponse",
    # Exceptions
    "GatewayError",
    "ProviderError",
    "RateLimitError",
    "CostLimitError",
]
