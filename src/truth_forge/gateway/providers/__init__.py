"""LLM Provider Implementations.

Each provider implements the BaseProvider interface for a specific LLM service.

Available providers:
- ClaudeProvider: Anthropic Claude models
- GeminiProvider: Google Gemini models
- OllamaProvider: Local Ollama models
- ScoutProvider: LLaMA 4 Scout (sovereign backbone for Not-Me)
- MaverickProvider: LLaMA 4 Maverick (deep reasoning lane)
- R1Provider: DeepSeek R1 (synthesis lane)

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/gateway/providers/
- Version: 2.1.0
- Date: 2026-02-01
- Changes: Added ScoutProvider for LLaMA 4 Scout integration
"""

from __future__ import annotations

from truth_forge.gateway.providers.base import BaseProvider
from truth_forge.gateway.providers.claude import ClaudeProvider
from truth_forge.gateway.providers.gemini import GeminiProvider
from truth_forge.gateway.providers.maverick import MaverickProvider
from truth_forge.gateway.providers.ollama import OllamaProvider
from truth_forge.gateway.providers.r1 import R1Provider
from truth_forge.gateway.providers.scout import ScoutProvider


__all__ = [
    "BaseProvider",
    "ClaudeProvider",
    "GeminiProvider",
    "OllamaProvider",
    "ScoutProvider",
    "MaverickProvider",
    "R1Provider",
]
