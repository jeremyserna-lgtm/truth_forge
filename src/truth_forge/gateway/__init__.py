"""Primitive Model Gateway - Unified LLM Abstraction Layer.

The Model Gateway provides a single interface for all LLM operations:

- Routes requests to the best available model
- Tracks costs per provider and operation
- Handles failures with automatic fallback
- Caches responses for identical requests
- Supports streaming responses

Usage:
    from truth_forge.gateway import prompt, get_gateway

    # Simple usage
    result = prompt("Summarize this text", content=my_text)

    # Direct gateway access
    gateway = get_gateway()
    result = gateway.complete(
        CompletionRequest(
            prompt="Extract entities",
            content=document,
            model="ollama-llama",
        )
    )

Providers:
    - claude: Anthropic Claude (default for complex reasoning)
    - gemini: Google Gemini (fast, good for structured output)
    - ollama: Local Ollama (free, private, good for embeddings)

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/gateway/
- Version: 2.0.0
- Date: 2026-01-26
"""

from __future__ import annotations

from truth_forge.gateway.gateway import (
    ModelGateway,
    complete,
    embed,
    get_gateway,
    prompt,
    stream,
)
from truth_forge.gateway.membrane import (
    InputClassification,
    Membrane,
    MembraneDecision,
    OutputClassification,
    SensitivityLevel,
    classify_input,
    classify_output,
    filter_input,
    filter_output,
    get_membrane,
    is_control_attempt,
)
from truth_forge.gateway.providers import (
    BaseProvider,
    ClaudeProvider,
    GeminiProvider,
    OllamaProvider,
)
from truth_forge.gateway.types import (
    CompletionRequest,
    CompletionResponse,
    CostLimitError,
    EmbeddingRequest,
    EmbeddingResponse,
    GatewayError,
    ModelConfig,
    ModelProvider,
    ProviderError,
    RateLimitError,
)


__all__ = [
    # Gateway
    "ModelGateway",
    "get_gateway",
    # Convenience functions
    "prompt",
    "complete",
    "embed",
    "stream",
    # Types
    "ModelProvider",
    "ModelConfig",
    "CompletionRequest",
    "CompletionResponse",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "GatewayError",
    "ProviderError",
    "RateLimitError",
    "CostLimitError",
    # Providers
    "BaseProvider",
    "ClaudeProvider",
    "GeminiProvider",
    "OllamaProvider",
    # Membrane
    "Membrane",
    "MembraneDecision",
    "InputClassification",
    "OutputClassification",
    "SensitivityLevel",
    "get_membrane",
    "filter_input",
    "filter_output",
    "is_control_attempt",
    "classify_input",
    "classify_output",
]
