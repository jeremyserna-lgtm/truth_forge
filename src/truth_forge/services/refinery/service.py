"""LLM Refinery Service - Core Sovereign Architecture Component.

This is the processing furnace that transforms raw conversation data
into the L2-L8 hierarchical entity structure using local LLMs.

Integration Points:
- IdentityService: Standardized ID generation
- BaseService: HOLD pattern, structured logging, lifecycle
- GovernanceService: Event tracking
- KnowledgeService: Knowledge atom storage (downstream)

Output Tables:
- entity_unified (34 fields): Core entity storage
- entity_enrichments (116 fields): Full enrichment data including
  Sovereign Architecture metrics (cognitive stage, struggle filter, etc.)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import httpx

from truth_forge.services.base import BaseService, MediatorProtocol
from truth_forge.services.factory import get_service, register_service


if TYPE_CHECKING:
    import structlog

    from truth_forge.services.identity import IdentityService


# =============================================================================
# Data Models (aligned with pipelines/llm_refinery)
# =============================================================================

from pipelines.llm_refinery.enrichments import (
    ENRICHMENT_EXTRACTION_PROMPT,
    EntityEnrichment,
    create_enrichment_from_llm,
)
from pipelines.llm_refinery.models import (
    ConversationL8,
    MessageL5,
    SentenceL4,
    SpanL3,
    WordL2,
)
from pipelines.llm_refinery.prompts import (
    FULL_MESSAGE_ANALYSIS_PROMPT,
)


@dataclass
class RefineryConfig:
    """Configuration for the LLM Refinery Service.

    Attributes:
        ollama_host: Host URL for Ollama server
        model: LLM model to use (qwen2.5-coder:32b recommended)
        timeout: HTTP timeout in seconds
        max_retries: Max retry attempts for LLM calls
        min_level: Minimum entity level to extract (2-8)
        batch_size: Conversations per batch
        enable_enrichments: Generate entity_enrichments output
        enrichment_levels: Which levels get enrichments
        source_system: Source system identifier
        source_pipeline: Pipeline identifier
    """

    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    model: str = "qwen2.5-coder:32b"

    # Processing settings
    timeout: float = 120.0
    max_retries: int = 3
    min_level: int = 5  # Default: L5, set to 2 for full depth
    batch_size: int = 10

    # Enrichment settings (Sovereign Architecture metrics)
    enable_enrichments: bool = True
    enrichment_levels: list[int] = field(default_factory=lambda: [5, 4])

    # Source tracking
    source_system: str = "claude_web"
    source_pipeline: str = "llm_refinery"


class OllamaClient:
    """Ollama client with structured logging and error handling."""

    def __init__(self, config: RefineryConfig, logger: structlog.stdlib.BoundLogger):
        self.config = config
        self.logger = logger
        self._client: httpx.Client | None = None

    def _ensure_client(self) -> httpx.Client:
        """Lazy initialize HTTP client."""
        if self._client is None:
            self._client = httpx.Client(timeout=self.config.timeout)
        return self._client

    def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def complete(self, prompt: str, temperature: float = 0.3) -> str:
        """Run completion with error handling and logging."""
        client = self._ensure_client()

        for attempt in range(self.config.max_retries):
            try:
                self.logger.debug(
                    "ollama_request",
                    model=self.config.model,
                    attempt=attempt + 1,
                    prompt_length=len(prompt),
                )

                response = client.post(
                    f"{self.config.ollama_host}/api/generate",
                    json={
                        "model": self.config.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": 4096,
                        },
                    },
                )
                response.raise_for_status()
                result = response.json().get("response", "")

                self.logger.debug(
                    "ollama_response",
                    response_length=len(result),
                )
                return result

            except httpx.TimeoutException:
                self.logger.warning(
                    "ollama_timeout",
                    attempt=attempt + 1,
                    max_retries=self.config.max_retries,
                )
            except httpx.HTTPError as e:
                self.logger.error(
                    "ollama_http_error",
                    error=str(e),
                    attempt=attempt + 1,
                )
                if attempt == self.config.max_retries - 1:
                    raise

        return ""

    def extract_json(self, prompt: str, temperature: float = 0.2) -> dict | list | None:
        """Extract JSON from LLM response with validation."""
        response = self.complete(prompt, temperature)

        # Find JSON in response
        json_start = response.find("[")
        json_start_obj = response.find("{")

        if json_start == -1 and json_start_obj == -1:
            self.logger.warning("json_not_found", response_preview=response[:200])
            return None

        # Use the first occurrence
        if json_start == -1:
            json_start = json_start_obj
        elif json_start_obj != -1:
            json_start = min(json_start, json_start_obj)

        # Find matching end
        if response[json_start] == "[":
            json_end = response.rfind("]") + 1
        else:
            json_end = response.rfind("}") + 1

        if json_end <= json_start:
            self.logger.warning("json_malformed", response_preview=response[:200])
            return None

        try:
            return json.loads(response[json_start:json_end])
        except json.JSONDecodeError as e:
            self.logger.warning(
                "json_decode_error",
                error=str(e),
                json_preview=response[json_start : json_start + 200],
            )
            return None


@register_service()
class LLMRefineryService(BaseService):
    """LLM-based conversation refinery service.

    The Refinery is the metabolic furnace that processes raw conversation
    data into structured entities (L2-L8) with full enrichments.

    Integrates with truth_forge service architecture:
    - Uses IdentityService for standardized ID generation
    - Uses structured logging via BaseService
    - Follows HOLD pattern for data flow
    - Publishes governance events via ServiceMediator

    Biological Metaphor:
    - Raw conversations = Food (unprocessed fuel)
    - LLM processing = Digestion (enzymatic breakdown)
    - Entities = Nutrients (structured data)
    - Enrichments = Vitamins/minerals (metadata)
    """

    service_name = "refinery"

    def __init__(self, config: RefineryConfig | None = None):
        self._config = config or RefineryConfig()
        self._ollama: OllamaClient | None = None
        self._identity: IdentityService | None = None
        self._mediator: MediatorProtocol | None = None
        self._run_id: str | None = None

        # Initialize BaseService (sets up HOLD dirs, logging)
        super().__init__()

    def on_startup(self) -> None:
        """Initialize service dependencies."""
        # Get identity service for ID generation
        try:
            self._identity = get_service("identity")
            self._run_id = self._identity.generate_run_id()
            self.logger.info(
                "identity_service_connected",
                run_id=self._run_id,
            )
        except Exception as e:
            self.logger.warning(
                "identity_service_unavailable",
                error=str(e),
                fallback="using_local_id_generation",
            )

        # Get mediator for governance events
        try:
            self._mediator = cast("MediatorProtocol", get_service("mediator"))
            self.logger.info("mediator_service_connected")
        except Exception as e:
            self.logger.warning(
                "mediator_service_unavailable",
                error=str(e),
            )

        # Initialize Ollama client
        self._ollama = OllamaClient(self._config, self.logger)

        self.logger.info(
            "refinery_started",
            ollama_host=self._config.ollama_host,
            model=self._config.model,
            min_level=self._config.min_level,
            enable_enrichments=self._config.enable_enrichments,
        )

    def on_shutdown(self) -> None:
        """Clean up resources."""
        if self._ollama:
            self._ollama.close()
        self.logger.info("refinery_shutdown")

    # =========================================================================
    # HOLD Pattern Implementation
    # =========================================================================

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Process a single conversation record (AGENT logic).

        This is the core HOLD pattern method called by BaseService.sync().

        Args:
            record: Raw conversation dict from HOLD₁

        Returns:
            Processing result with entities and enrichments
        """
        uuid = record.get("uuid", "unknown")

        self.logger.info("processing_conversation", uuid=uuid)

        # Publish governance event
        if self._mediator:
            self._mediator.publish(
                "governance.record",
                {
                    "event_type": "CONVERSATION_PROCESSING_STARTED",
                    "service": self.service_name,
                    "conversation_id": uuid,
                },
            )

        try:
            entities, enrichments = self._process_conversation(record)

            result = {
                "conversation_id": uuid,
                "entity_count": len(entities),
                "enrichment_count": len(enrichments),
                "entities": entities,
                "enrichments": enrichments,
                "status": "success",
            }

            # Publish completion
            if self._mediator:
                self._mediator.publish(
                    "governance.record",
                    {
                        "event_type": "CONVERSATION_PROCESSING_COMPLETED",
                        "service": self.service_name,
                        "conversation_id": uuid,
                        "entity_count": len(entities),
                        "enrichment_count": len(enrichments),
                    },
                )

            self.logger.info(
                "conversation_processed",
                uuid=uuid,
                entity_count=len(entities),
                enrichment_count=len(enrichments),
            )

            return result

        except Exception as e:
            self.logger.error(
                "conversation_processing_failed",
                uuid=uuid,
                error=str(e),
            )

            if self._mediator:
                self._mediator.publish(
                    "governance.record",
                    {
                        "event_type": "CONVERSATION_PROCESSING_FAILED",
                        "service": self.service_name,
                        "conversation_id": uuid,
                        "error": str(e),
                    },
                )

            return {
                "conversation_id": uuid,
                "status": "error",
                "error": str(e),
            }

    # =========================================================================
    # Core Processing Logic
    # =========================================================================

    def _generate_entity_id(self, prefix: str, content: str, parent_id: str = "") -> str:
        """Generate entity ID using IdentityService or fallback."""
        if self._identity:
            return self._identity.generate_entity_id(
                prefix=prefix,
                content=content,
                parent_id=parent_id,
            )
        else:
            # Fallback: use hash-based ID
            import hashlib

            content_hash = hashlib.sha256(f"{content}{parent_id}".encode()).hexdigest()[:16]
            return f"{prefix}:{content_hash}:0000"

    def _process_conversation(
        self, conversation: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Process a conversation into entities and enrichments.

        Args:
            conversation: Raw conversation dict

        Returns:
            Tuple of (entities, enrichments) as dicts
        """
        entities: list[dict[str, Any]] = []
        enrichments: list[dict[str, Any]] = []

        uuid = conversation.get("uuid", "")
        title = conversation.get("name", "Untitled")
        created_at = conversation.get("created_at", datetime.now(UTC).isoformat())
        messages = conversation.get("chat_messages", [])

        # Generate L8 conversation ID
        conv_id = self._generate_entity_id("conv", f"{uuid}:{title}")

        # Create L8 Conversation entity
        l8 = ConversationL8(
            uuid=uuid,
            title=title,
            participants=["human", "assistant"],
            created_at=created_at,
            messages=[],  # Will be populated
        )

        # Process messages (L5)
        l5_messages = []
        for msg in messages:
            l5 = MessageL5.from_raw(msg)
            l5.entity_id = self._generate_entity_id("msg", l5.text[:100], conv_id)
            l5_messages.append(l5)

            # Convert to entity_unified format
            entity_dict = l5.to_entity_unified()
            entity_dict["conversation_id"] = conv_id
            entity_dict["source_pipeline"] = self._config.source_pipeline
            entity_dict["source_system"] = self._config.source_system
            entity_dict["ingestion_job_id"] = self._run_id
            entities.append(entity_dict)

            # Extract enrichments if enabled
            if self._config.enable_enrichments and 5 in self._config.enrichment_levels:
                enrichment = self._extract_enrichment(l5)
                if enrichment:
                    enrichments.append(enrichment.to_entity_enrichments())

        l8.messages = l5_messages

        # Add L8 entity
        l8_dict = l8.to_entity_unified()
        l8_dict["entity_id"] = conv_id
        l8_dict["source_pipeline"] = self._config.source_pipeline
        l8_dict["source_system"] = self._config.source_system
        l8_dict["ingestion_job_id"] = self._run_id
        entities.append(l8_dict)

        # Process deeper levels if configured
        if self._config.min_level <= 4:
            for l5 in l5_messages:
                deeper_entities, deeper_enrichments = self._process_deep(l5, conv_id)
                entities.extend(deeper_entities)
                enrichments.extend(deeper_enrichments)

        return entities, enrichments

    def _process_deep(
        self, message: MessageL5, conv_id: str
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Process deeper entity levels (L4-L2) via LLM.

        Args:
            message: L5 message to decompose
            conv_id: Parent conversation ID

        Returns:
            Tuple of (entities, enrichments)
        """
        entities: list[dict[str, Any]] = []
        enrichments: list[dict[str, Any]] = []

        if not self._ollama:
            return entities, enrichments

        # Use FULL_MESSAGE_ANALYSIS_PROMPT for comprehensive extraction
        prompt = FULL_MESSAGE_ANALYSIS_PROMPT.format(
            message_text=message.text,
            speaker=message.role,
        )

        result = self._ollama.extract_json(prompt)
        if not result or not isinstance(result, dict):
            return entities, enrichments

        # Process L4 sentences
        for sent_data in result.get("sentences", []):
            l4 = SentenceL4.from_llm(sent_data)
            l4.entity_id = self._generate_entity_id("sent", l4.text[:50], message.entity_id)

            entity_dict = l4.to_entity_unified()
            entity_dict["conversation_id"] = conv_id
            entity_dict["parent_id"] = message.entity_id
            entity_dict["source_pipeline"] = self._config.source_pipeline
            entity_dict["source_system"] = self._config.source_system
            entity_dict["ingestion_job_id"] = self._run_id
            entities.append(entity_dict)

            # Enrichments for L4
            if self._config.enable_enrichments and 4 in self._config.enrichment_levels:
                enrichment = self._extract_enrichment_for_l4(l4, message.role)
                if enrichment:
                    enrichments.append(enrichment.to_entity_enrichments())

            # Process L3 spans and L2 words if configured
            if self._config.min_level <= 3:
                for span_data in sent_data.get("spans", []):
                    l3 = SpanL3.from_llm(span_data)
                    l3.entity_id = self._generate_entity_id("span", l3.text[:30], l4.entity_id)

                    span_dict = l3.to_entity_unified()
                    span_dict["conversation_id"] = conv_id
                    span_dict["parent_id"] = l4.entity_id
                    span_dict["source_pipeline"] = self._config.source_pipeline
                    span_dict["source_system"] = self._config.source_system
                    span_dict["ingestion_job_id"] = self._run_id
                    entities.append(span_dict)

                    # Process L2 words
                    if self._config.min_level <= 2:
                        for word_data in span_data.get("words", []):
                            l2 = WordL2.from_llm(word_data)
                            l2.entity_id = self._generate_entity_id("word", l2.text, l3.entity_id)

                            word_dict = l2.to_entity_unified()
                            word_dict["conversation_id"] = conv_id
                            word_dict["parent_id"] = l3.entity_id
                            word_dict["span_id"] = l3.entity_id
                            word_dict["source_pipeline"] = self._config.source_pipeline
                            word_dict["source_system"] = self._config.source_system
                            word_dict["ingestion_job_id"] = self._run_id
                            entities.append(word_dict)

        return entities, enrichments

    def _extract_enrichment(self, message: MessageL5) -> EntityEnrichment | None:
        """Extract enrichments for a message using LLM.

        Includes Sovereign Architecture metrics:
        - Cognitive stage (Kegan 1-5)
        - Struggle filter (swim/drown)
        - Metabolic stage (TRUTH:MEANING:CARE)
        - Confidence calibration
        - Source attribution (ME/NOT-ME)
        - Temporal lens
        - Operational cycle (SEE:SEE:DO:DONE)
        - Jeremy Arc test
        """
        if not self._ollama:
            return None

        prompt = ENRICHMENT_EXTRACTION_PROMPT.format(
            text=message.text,
            entity_type="message",
            level=5,
            speaker=message.role,
        )

        result = self._ollama.extract_json(prompt)
        if not result or not isinstance(result, dict):
            return None

        return create_enrichment_from_llm(
            entity_id=message.entity_id,
            text=message.text,
            llm_response=result,
            batch_id=self._run_id,
        )

    def _extract_enrichment_for_l4(
        self, sentence: SentenceL4, speaker: str
    ) -> EntityEnrichment | None:
        """Extract enrichments for a sentence."""
        if not self._ollama:
            return None

        prompt = ENRICHMENT_EXTRACTION_PROMPT.format(
            text=sentence.text,
            entity_type="sentence",
            level=4,
            speaker=speaker,
        )

        result = self._ollama.extract_json(prompt)
        if not result or not isinstance(result, dict):
            return None

        return create_enrichment_from_llm(
            entity_id=sentence.entity_id,
            text=sentence.text,
            llm_response=result,
            batch_id=self._run_id,
        )

    # =========================================================================
    # Batch Processing
    # =========================================================================

    def process_batch(
        self,
        conversations: list[dict[str, Any]],
        output_file: Path | None = None,
        enrichments_file: Path | None = None,
    ) -> dict[str, Any]:
        """Process multiple conversations in batch.

        Args:
            conversations: List of raw conversation dicts
            output_file: Optional path to write entities JSONL
            enrichments_file: Optional path to write enrichments JSONL

        Returns:
            Batch processing statistics
        """
        stats = {
            "total": len(conversations),
            "processed": 0,
            "failed": 0,
            "entity_count": 0,
            "enrichment_count": 0,
            "errors": [],
        }

        all_entities: list[dict[str, Any]] = []
        all_enrichments: list[dict[str, Any]] = []

        for conv in conversations:
            try:
                result = self.process(conv)

                if result.get("status") == "success":
                    stats["processed"] += 1
                    stats["entity_count"] += result.get("entity_count", 0)
                    stats["enrichment_count"] += result.get("enrichment_count", 0)
                    all_entities.extend(result.get("entities", []))
                    all_enrichments.extend(result.get("enrichments", []))
                else:
                    stats["failed"] += 1
                    stats["errors"].append(result.get("error", "Unknown error"))

            except Exception as e:
                stats["failed"] += 1
                stats["errors"].append(str(e))

        # Write output files
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                for entity in all_entities:
                    f.write(json.dumps(entity) + "\n")
            self.logger.info("entities_written", path=str(output_file), count=len(all_entities))

        if enrichments_file and all_enrichments:
            enrichments_file.parent.mkdir(parents=True, exist_ok=True)
            with open(enrichments_file, "w") as f:
                for enrichment in all_enrichments:
                    f.write(json.dumps(enrichment) + "\n")
            self.logger.info(
                "enrichments_written", path=str(enrichments_file), count=len(all_enrichments)
            )

        return stats


def create_refinery_service(config: RefineryConfig | None = None) -> LLMRefineryService:
    """Factory function to create a refinery service.

    Args:
        config: Optional configuration override

    Returns:
        Configured LLMRefineryService instance
    """
    return LLMRefineryService(config)
