"""
Memory Native Inference - The core of ANIMA.

The LLM never sees "raw" input.
The LLM never makes "store memory" decisions.
Memory IS the cognitive fabric.

This is what makes ANIMA different from bolted-on RAG systems.
"""

from typing import Any, Protocol

import structlog

from sovereign.memory.cortex import EnrichedInput, MemoryCortex


logger = structlog.get_logger(__name__)


class LLMEngine(Protocol):
    """Protocol for LLM engines that can be wrapped."""

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a response from the LLM."""
        ...


class MemoryNativeInference:
    """
    Inference engine with memory as NATIVE capability.

    The LLM never sees "raw" input.
    The LLM never makes "store memory" decisions.
    Memory IS the cognitive fabric.

    Why this is different from RAG:
    - RAG: LLM decides "should I search?" (can forget)
    - ANIMA: Every input is ALWAYS enriched (cannot bypass)

    Why this is different from memory tools:
    - Tools: LLM decides "should I store this?" (inconsistent)
    - ANIMA: Every interaction is ALWAYS stored (100% coverage)
    """

    def __init__(
        self,
        llm_engine: LLMEngine,
        memory_cortex: MemoryCortex,
    ) -> None:
        """
        Initialize the memory-native inference engine.

        Args:
            llm_engine: The underlying LLM engine (Scout, Maverick, DeepSeek, etc.)
            memory_cortex: The memory cortex that provides native memory.
        """
        self._llm = llm_engine
        self._cortex = memory_cortex

    async def complete(
        self,
        user_input: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """
        The main inference loop with native memory.

        Notice: NO tool calls for memory.
        Memory enrichment and storage happen AUTOMATICALLY.

        Args:
            user_input: The raw user input.
            system_prompt: Optional system prompt to prepend.
            **kwargs: Additional arguments passed to the LLM.

        Returns:
            The generated response.
        """
        # 1. PERCEIVE through memory
        enriched = await self._cortex.perceive(user_input)

        logger.info(
            "perception_phase_complete",
            extra={
                "semantic_hits": enriched.enrichment_metadata.get("semantic_hits", 0),
                "temporal_hits": enriched.enrichment_metadata.get("temporal_hits", 0),
                "entity_hits": enriched.enrichment_metadata.get("entity_hits", 0),
            },
        )

        # 2. Build context (memory is already embedded)
        memory_context = self._cortex.build_context_block(enriched)

        # 3. Construct full prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{memory_context}"
        else:
            full_prompt = memory_context

        # 4. Generate response
        response = await self._llm.generate(full_prompt, **kwargs)

        # 5. COMMIT to memory (automatic, not tool-based)
        await self._cortex.commit(user_input, response)

        logger.info(
            "inference_complete",
            extra={
                "input_length": len(user_input),
                "response_length": len(response),
                "memory_committed": True,
            },
        )

        return response

    async def complete_without_commit(
        self,
        user_input: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> tuple[str, EnrichedInput]:
        """
        Complete without committing to memory.

        Used for preview/testing scenarios where you don't want
        to pollute memory with test interactions.

        Args:
            user_input: The raw user input.
            system_prompt: Optional system prompt to prepend.
            **kwargs: Additional arguments passed to the LLM.

        Returns:
            Tuple of (response, enriched_input).
        """
        # 1. PERCEIVE through memory
        enriched = await self._cortex.perceive(user_input)

        # 2. Build context
        memory_context = self._cortex.build_context_block(enriched)

        # 3. Construct full prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{memory_context}"
        else:
            full_prompt = memory_context

        # 4. Generate response (NO commit)
        response = await self._llm.generate(full_prompt, **kwargs)

        return response, enriched

    async def perceive_only(self, user_input: str) -> EnrichedInput:
        """
        Only run the perception phase without generation.

        Useful for debugging or analyzing what memory would provide.

        Args:
            user_input: The raw user input.

        Returns:
            The enriched input from memory.
        """
        return await self._cortex.perceive(user_input)

    async def commit_only(self, input_text: str, output_text: str) -> None:
        """
        Only commit to memory without generation.

        Useful for ingesting historical conversations or
        external knowledge into memory.

        Args:
            input_text: The input text to commit.
            output_text: The output text to commit.
        """
        await self._cortex.commit(input_text, output_text)

    def get_context_preview(self, enriched: EnrichedInput) -> str:
        """
        Get a preview of what context would be sent to the LLM.

        Useful for debugging memory enrichment.

        Args:
            enriched: The enriched input from perceive().

        Returns:
            The formatted context block.
        """
        return self._cortex.build_context_block(enriched)
