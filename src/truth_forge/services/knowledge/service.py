"""Knowledge Service with LLM integration.

Processes content through various LLMs to extract structured knowledge.

Structure: HOLD₁ (Raw Content) → AGENT (LLM) → HOLD₂ (Processed Knowledge)
"""

from __future__ import annotations

import json
import time
from typing import Any

import structlog

from truth_forge.services.base import BaseService
from truth_forge.services.factory import get_service, register_service
from truth_forge.services.secret import SecretService


# Cost constants (per million tokens, as of Jan 2026)
# Claude
CLAUDE_SONNET_INPUT_COST = 3.00  # $/M tokens
CLAUDE_SONNET_OUTPUT_COST = 15.00  # $/M tokens
CLAUDE_HAIKU_INPUT_COST = 0.25  # $/M tokens
CLAUDE_HAIKU_OUTPUT_COST = 1.25  # $/M tokens

# Gemini (assuming similar to 1.5 Pro)
GEMINI_1_5_PRO_INPUT_COST = 3.50  # $/M tokens
GEMINI_1_5_PRO_OUTPUT_COST = 10.50  # $/M tokens

# OpenAI (assuming GPT-4-turbo)
GPT_4_TURBO_INPUT_COST = 10.00  # $/M tokens
GPT_4_TURBO_OUTPUT_COST = 30.00  # $/M tokens

# Session limits (cost governance)
MAX_COST_PER_SESSION = 0.50  # $0.50 default limit per session
MAX_CALLS_PER_SESSION = 100
RATE_LIMIT_DELAY = 0.1  # seconds between calls

logger = structlog.get_logger(__name__)


class LLMError(Exception):
    """Raised when LLM call fails."""

    pass


class CostLimitError(Exception):
    """Raised when session cost limit is exceeded."""

    pass


class LLMClientFactory:
    """Manages and provides LLM client instances (Anthropic, Gemini, OpenAI)."""

    _anthropic_client: Any = None
    _gemini_client: Any = None
    _openai_client: Any = None
    _secret_service: SecretService | None = None

    @classmethod
    def _get_secret_service(cls) -> SecretService:
        if cls._secret_service is None:
            service = get_service("secret")
            # Cast to SecretService - get_service returns BaseService but we know it's SecretService
            if not isinstance(service, SecretService):
                raise LLMError("Expected SecretService from factory")
            cls._secret_service = service
        return cls._secret_service

    @classmethod
    def get_anthropic_client(cls) -> Any:
        """Get Anthropic client with API key from SecretService."""
        if cls._anthropic_client is None:
            import anthropic

            secret_service = cls._get_secret_service()
            api_key = secret_service.get_secret("ANTHROPIC_API_KEY")
            if not api_key:
                raise LLMError("ANTHROPIC_API_KEY not configured in Secret Manager.")
            if api_key.startswith("mock_"):
                logger.warning("using_mock_anthropic_client")
                # Return a mock client that simulates the expected API response
                from unittest.mock import Mock

                mock_client = Mock()
                mock_response = Mock()
                mock_response.content = [Mock(text='{"summary": "This is a mock summary."}')]
                mock_response.usage.input_tokens = 10
                mock_response.usage.output_tokens = 5
                mock_client.messages.create.return_value = mock_response
                return mock_client
            cls._anthropic_client = anthropic.Anthropic(api_key=api_key)
        return cls._anthropic_client

    @classmethod
    def get_gemini_client(cls) -> Any:
        """Get Gemini client with API key from SecretService."""
        if cls._gemini_client is None:
            from google import genai

            secret_service = cls._get_secret_service()
            api_key = secret_service.get_secret("GOOGLE_API_KEY")
            if not api_key:
                raise LLMError("GOOGLE_API_KEY not configured in Secret Manager.")
            cls._gemini_client = genai.Client(api_key=api_key)
        return cls._gemini_client

    @classmethod
    def get_openai_client(cls) -> Any:
        """Get OpenAI client with API key from SecretService."""
        if cls._openai_client is None:
            import openai

            secret_service = cls._get_secret_service()
            api_key = secret_service.get_secret("OPENAI_API_KEY")
            if not api_key:
                raise LLMError("OPENAI_API_KEY not configured in Secret Manager.")
            cls._openai_client = openai.OpenAI(api_key=api_key)
        return cls._openai_client


@register_service()
class KnowledgeService(BaseService):
    """Knowledge processing service with LLM integration.

    Processes content through various LLMs to:
    - Extract key facts and entities
    - Generate summaries
    - Create structured metadata
    - Identify relationships

    Attributes:
        service_name: "knowledge"
        default_llm: Default LLM to use (e.g., "claude-sonnet-4-20250514", "gemini-1.5-pro", "gpt-4-turbo")
    """

    service_name = "knowledge"

    def __init__(
        self,
        default_llm: str = "claude-sonnet-4-20250514",
        max_cost_per_session: float = MAX_COST_PER_SESSION,
    ) -> None:
        """Initialize knowledge service.

        Args:
            default_llm: Default LLM model ID to use.
            max_cost_per_session: Maximum cost allowed per session in USD.
        """
        super().__init__()

        self._default_llm = default_llm
        self._max_cost = max_cost_per_session
        self._session_cost = 0.0
        self._session_calls = 0
        self._last_call_time = 0.0

        self.logger.info(
            "knowledge_service_initialized",
            default_llm=default_llm,
            max_cost=max_cost_per_session,
        )

    def _estimate_cost(
        self, input_tokens: int, output_tokens: int, llm_model: str | None = None
    ) -> float:
        """Estimate cost for a request.

        Args:
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.
            llm_model: LLM model name (defaults to instance default_llm).

        Returns:
            Estimated cost in USD.
        """
        llm_model = llm_model or self._default_llm
        model_lower = llm_model.lower()

        input_cost = 0.0
        output_cost = 0.0

        if "claude" in model_lower:
            if "haiku" in model_lower:
                input_cost = CLAUDE_HAIKU_INPUT_COST
                output_cost = CLAUDE_HAIKU_OUTPUT_COST
            else:
                input_cost = CLAUDE_SONNET_INPUT_COST
                output_cost = CLAUDE_SONNET_OUTPUT_COST
        elif "gemini" in model_lower:
            input_cost = GEMINI_1_5_PRO_INPUT_COST
            output_cost = GEMINI_1_5_PRO_OUTPUT_COST
        elif "gpt" in model_lower or "openai" in model_lower:
            input_cost = GPT_4_TURBO_INPUT_COST
            output_cost = GPT_4_TURBO_OUTPUT_COST
        else:
            self.logger.warning("unknown_llm_model_for_cost_estimation", model=llm_model)
            return 0.0  # Cannot estimate cost for unknown models

        return (input_tokens / 1_000_000) * input_cost + (output_tokens / 1_000_000) * output_cost

    def _check_cost_limit(self, estimated_cost: float) -> None:
        """Check if request would exceed cost limit.

        Args:
            estimated_cost: Estimated cost of the request.

        Raises:
            CostLimitError: If limit would be exceeded.
        """
        if self._session_cost + estimated_cost > self._max_cost:
            raise CostLimitError(
                f"Request would exceed session cost limit. "
                f"Current: ${self._session_cost:.4f}, "
                f"Estimated: ${estimated_cost:.4f}, "
                f"Limit: ${self._max_cost:.2f}"
            )

        if self._session_calls >= MAX_CALLS_PER_SESSION:
            raise CostLimitError(f"Session call limit reached ({MAX_CALLS_PER_SESSION} calls)")

    def _apply_rate_limit(self) -> None:
        """Apply rate limiting between calls."""
        now = time.time()
        elapsed = now - self._last_call_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self._last_call_time = time.time()

    def call_llm(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 1024,
        llm_model: str | None = None,
    ) -> dict[str, Any]:
        """Call LLM with cost tracking and rate limiting.

        Args:
            prompt: User prompt/content to process.
            system: Optional system prompt.
            max_tokens: Maximum tokens in response.
            llm_model: Specific LLM model to use. Defaults to instance default_llm.

        Returns:
            Dict with response text, usage stats, and cost.

        Raises:
            LLMError: If API call fails or key is not configured.
            CostLimitError: If cost limit would be exceeded.
        """
        llm_model = llm_model or self._default_llm
        model_lower = llm_model.lower()

        # Estimate tokens (rough: ~4 chars per token)
        estimated_input = len(prompt) // 4 + (len(system) // 4 if system else 0)
        estimated_output = max_tokens // 2  # Assume half max
        estimated_cost = self._estimate_cost(estimated_input, estimated_output, llm_model)

        self._check_cost_limit(estimated_cost)
        self._apply_rate_limit()

        response_text = ""
        input_tokens = 0
        output_tokens = 0

        try:
            if "claude" in model_lower:
                import anthropic  # noqa: TC002 - needed for runtime type annotation

                client = LLMClientFactory.get_anthropic_client()
                messages: list[anthropic.types.MessageParam] = [{"role": "user", "content": prompt}]
                response = client.messages.create(
                    model=llm_model,
                    max_tokens=max_tokens,
                    system=system or "You are a knowledge extraction assistant.",
                    messages=messages,
                )
                for block in response.content:
                    if hasattr(block, "text"):
                        response_text += block.text
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
            elif "gemini" in model_lower:
                from google.genai import types as genai_types

                client = LLMClientFactory.get_gemini_client()
                # Build content for Gemini
                content_parts: list[str] = []
                if system:
                    content_parts.append(system)
                content_parts.append(prompt)

                # Use the new google.genai API
                response = client.models.generate_content(
                    model=llm_model,
                    contents="\n".join(content_parts),
                    config=genai_types.GenerateContentConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.4,
                        top_p=1.0,
                        top_k=32,
                    ),
                )
                response_text = response.text or ""
                # Gemini API does not directly expose token usage like Anthropic/OpenAI
                input_tokens = estimated_input
                output_tokens = len(response_text) // 4
            elif "gpt" in model_lower or "openai" in model_lower:
                client = LLMClientFactory.get_openai_client()
                messages_params: list[dict[str, str]] = []
                if system:
                    messages_params.append({"role": "system", "content": system})
                messages_params.append({"role": "user", "content": prompt})

                response = client.chat.completions.create(
                    model=llm_model,
                    messages=messages_params,
                    max_tokens=max_tokens,
                )
                response_text = response.choices[0].message.content or ""
                input_tokens = response.usage.prompt_tokens if response.usage else estimated_input
                output_tokens = (
                    response.usage.completion_tokens if response.usage else estimated_output
                )
            else:
                raise LLMError(f"Unsupported LLM model: {llm_model}")

            # Calculate actual cost
            actual_cost = self._estimate_cost(input_tokens, output_tokens, llm_model)

            # Update session tracking
            self._session_cost += actual_cost
            self._session_calls += 1

            self.logger.info(
                "llm_call_completed",
                llm_model=llm_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=actual_cost,
                session_cost=self._session_cost,
                session_calls=self._session_calls,
            )

            return {
                "text": response_text,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": actual_cost,
                "llm_model": llm_model,
            }

        except Exception as e:
            self.logger.error("llm_call_failed", error=str(e), llm_model=llm_model)
            raise LLMError(f"{llm_model} API call failed: {e}") from e

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Process a single record to extract knowledge."""
        import hashlib

        content = record.get("content")

        # Handle missing or empty content
        if not content:
            record["knowledge_status"] = "skipped"
            record["knowledge_reason"] = "no_content" if content is None else "empty_content"
            return record

        # Generate content hash for deduplication/tracking
        record["content_hash"] = hashlib.md5(content.encode()).hexdigest()

        try:
            extraction_prompt = self._build_extraction_prompt(content)
            llm_response = self.call_llm(extraction_prompt)

            record["knowledge_status"] = "processed"
            record["extraction"] = json.loads(llm_response["text"])
            record["llm_model"] = llm_response["llm_model"]
            record["llm_cost"] = llm_response["cost"]
            record["llm_tokens"] = {
                "input": llm_response["input_tokens"],
                "output": llm_response["output_tokens"],
            }
        except CostLimitError:
            self.logger.warning("cost_limit_reached", content_hash=record["content_hash"])
            record["knowledge_status"] = "deferred"
            record["knowledge_reason"] = "cost_limit"
        except (LLMError, json.JSONDecodeError) as e:
            self.logger.error("llm_processing_failed", error=str(e))
            record["knowledge_status"] = "failed"
            record["knowledge_error"] = str(e)
        return record

    def query(
        self,
        query: str | None = None,
        source: str | None = None,
        model: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query knowledge atoms from HOLD_2."""
        import duckdb

        db_path = self._paths["hold2"] / f"{self.service_name}.duckdb"
        if not db_path.exists():
            return []

        conn = duckdb.connect(str(db_path), read_only=True)
        try:
            sql_query = f"SELECT * FROM {self.service_name}_records WHERE 1=1"
            params: list[str | int] = []
            if query:
                sql_query += " AND data->>'content' LIKE ?"
                params.append(f"%{query}%")
            if source:
                sql_query += " AND data->>'source' = ?"
                params.append(source)
            if model:
                sql_query += " AND data->>'llm_model' = ?"
                params.append(model)

            sql_query += " LIMIT ?"
            params.append(limit)

            results = conn.execute(sql_query, params).fetchall()
            return [json.loads(row[1]) for row in results]
        finally:
            conn.close()

    def create_schema(self) -> str:
        """Create DuckDB schema for knowledge records.

        Returns:
            SQL CREATE TABLE statement.
        """
        return """
            CREATE TABLE IF NOT EXISTS knowledge_records (
                id VARCHAR PRIMARY KEY,
                data JSON NOT NULL,
                content_hash VARCHAR,
                source VARCHAR,
                knowledge_status VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

    def get_session_stats(self) -> dict[str, Any]:
        """Get current session statistics.

        Returns:
            Session stats including cost, calls, and limits.
        """
        return {
            "session_cost": self._session_cost,
            "session_calls": self._session_calls,
            "max_cost": self._max_cost,
            "max_calls": MAX_CALLS_PER_SESSION,
            "remaining_budget": self._max_cost - self._session_cost,
            "llm_model": self._default_llm,
        }

    def reset_session(self) -> None:
        """Reset session counters (for new processing batch)."""
        self._session_cost = 0.0
        self._session_calls = 0
        self.logger.info("session_reset")

    def _build_extraction_prompt(self, content: str) -> str:
        """Builds the prompt for knowledge extraction."""
        # This can be made more sophisticated in the future
        return f"""
        Analyze the following content and extract a structured knowledge atom in JSON format.
        The JSON object should include:
        - "summary": A concise summary of the content.
        - "entities": A list of key people, places, and organizations.
        - "themes": A list of the main themes or topics.

        Content to analyze:
        ---
        {content}
        ---
        """
