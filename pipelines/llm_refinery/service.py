"""LLM Refinery Service - Hardened integration with central services.

This module provides the LLM Refinery as a proper truth_forge service,
integrating with:
- IdentityService: Standardized ID generation
- BaseService: HOLD pattern, structured logging, lifecycle management
- LoggingService: Centralized logging
- Factory: Dependency injection

Usage:
    from truth_forge.services.factory import get_service
    
    refinery = get_service("llm_refinery")
    result = refinery.process_conversation(conversation_data)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Iterator, Optional, TYPE_CHECKING

import httpx
import structlog

from truth_forge.services.base import BaseService
from truth_forge.services.factory import get_service, register_service

if TYPE_CHECKING:
    from truth_forge.services.identity import IdentityService

from .models import (
    ConversationL8,
    TopicSegmentL7,
    TurnL6,
    MessageL5,
    SentenceL4,
    SpanL3,
    WordL2,
)
from .prompts import (
    TOPIC_SEGMENTATION_PROMPT,
    TURN_DETECTION_PROMPT,
    SENTENCE_EXTRACTION_PROMPT,
    SPAN_EXTRACTION_PROMPT,
    WORD_ANALYSIS_PROMPT,
    FULL_MESSAGE_ANALYSIS_PROMPT,
    CONVERSATION_SUMMARY_PROMPT,
)
from .enrichments import (
    EntityEnrichment,
    SentimentEnrichment,
    EmotionEnrichment,
    ReadabilityEnrichment,
    KeywordEnrichment,
    TopicEnrichment,
    ContentClassification,
    ENRICHMENT_EXTRACTION_PROMPT,
    create_enrichment_from_llm,
)


@dataclass
class RefineryConfig:
    """Configuration for the LLM Refinery Service."""
    
    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    model: str = "qwen2.5-coder:32b"
    
    # Processing settings
    timeout: float = 120.0
    max_retries: int = 3
    min_level: int = 5  # Default: L5, set to 2 for full depth
    batch_size: int = 10
    
    # Enrichment settings
    enable_enrichments: bool = True  # Generate entity_enrichments output
    enrichment_levels: list[int] = field(default_factory=lambda: [5, 4])  # L5, L4 by default
    
    # Source tracking
    source_system: str = "claude_web"
    source_pipeline: str = "llm_refinery"


class OllamaClientHardened:
    """Hardened Ollama client with structured logging and error handling."""
    
    def __init__(self, config: RefineryConfig, logger: structlog.stdlib.BoundLogger):
        self.config = config
        self.logger = logger
        self._client: Optional[httpx.Client] = None
    
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
        """Run completion with full error handling and logging."""
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
                json_preview=response[json_start:json_start + 200],
            )
            return None


@register_service()
class LLMRefineryService(BaseService):
    """LLM-based conversation refinery service.
    
    Integrates with truth_forge service architecture:
    - Uses IdentityService for standardized ID generation
    - Uses structured logging via BaseService
    - Follows HOLD pattern for data flow
    - Supports health checks and lifecycle management
    """
    
    service_name = "llm_refinery"
    
    def __init__(self, config: Optional[RefineryConfig] = None):
        self._config = config or RefineryConfig()
        self._ollama: Optional[OllamaClientHardened] = None
        self._identity: Optional["IdentityService"] = None
        self._run_id: Optional[str] = None
        
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
        
        # Initialize Ollama client
        self._ollama = OllamaClientHardened(self._config, self.logger)
        
        self.logger.info(
            "llm_refinery_started",
            ollama_host=self._config.ollama_host,
            model=self._config.model,
            min_level=self._config.min_level,
        )
    
    def on_shutdown(self) -> None:
        """Clean up resources."""
        if self._ollama:
            self._ollama.close()
        self.logger.info("llm_refinery_shutdown")
    
    def create_schema(self) -> str:
        """DuckDB schema for HOLD₂ output."""
        return """
            CREATE TABLE IF NOT EXISTS entities (
                entity_id VARCHAR PRIMARY KEY,
                level INTEGER NOT NULL,
                entity_type VARCHAR NOT NULL,
                entity_mode VARCHAR DEFAULT 'active',
                parent_id VARCHAR,
                conversation_id VARCHAR,
                topic_segment_id VARCHAR,
                turn_id VARCHAR,
                message_id VARCHAR,
                sentence_id VARCHAR,
                span_id VARCHAR,
                text TEXT NOT NULL,
                source_pipeline VARCHAR DEFAULT 'llm_refinery',
                source_file VARCHAR,
                source_system VARCHAR,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ingestion_job_id VARCHAR,
                validation_status VARCHAR DEFAULT 'valid'
            );
            
            CREATE INDEX IF NOT EXISTS idx_level ON entities(level);
            CREATE INDEX IF NOT EXISTS idx_conversation ON entities(conversation_id);
            CREATE INDEX IF NOT EXISTS idx_parent ON entities(parent_id);
        """
    
    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Process a single conversation record through the refinery.
        
        This is the main HOLD pattern entry point.
        """
        self.logger.info(
            "processing_conversation",
            uuid=record.get("uuid", "unknown"),
        )
        
        try:
            conversation = self._build_conversation(record)
            
            # Get both entities and enrichments
            # Get source file info from record
            source_file = record.get("source_file") or record.get("name", "unknown")
            source_file_path = record.get("source_file_path") or self._config.input_path
            
            if self._config.enable_enrichments:
                entities_iter, enrichments_iter = self._flatten_entities_with_enrichments(
                    conversation, 
                    source_file=source_file,
                    source_file_path=source_file_path,
                )
                entities = list(entities_iter)
                enrichments = list(enrichments_iter)
            else:
                entities = list(self._flatten_entities(
                    conversation,
                    source_file=source_file,
                    source_file_path=source_file_path,
                ))
                enrichments = []
            
            self.logger.info(
                "conversation_processed",
                uuid=record.get("uuid"),
                entity_count=len(entities),
                enrichment_count=len(enrichments),
            )
            
            return {
                "conversation_id": conversation.entity_id,
                "entity_count": len(entities),
                "entities": entities,
                "enrichment_count": len(enrichments),
                "enrichments": enrichments,
                "run_id": self._run_id,
            }
            
        except Exception as e:
            self.logger.error(
                "processing_error",
                uuid=record.get("uuid"),
                error=str(e),
            )
            raise
    
    # =========================================================================
    # ID Generation (uses IdentityService when available)
    # =========================================================================
    
    def _generate_conversation_id(self, source_uuid: str) -> str:
        """Generate L8 conversation ID."""
        if self._identity:
            return self._identity.generate_conversation_id(
                self._config.source_system, source_uuid
            )
        # Fallback to local generation
        import hashlib
        content_hash = hashlib.sha256(source_uuid.encode()).hexdigest()[:16]
        return f"conv:{self._config.source_system}:{content_hash}"
    
    def _generate_topic_id(self, parent_id: str, index: int) -> str:
        """Generate L7 topic segment ID."""
        if self._identity:
            # Use span_id generator (similar pattern)
            return self._identity.generate_span_id(parent_id, index).replace("span:", "topic:")
        import hashlib
        parent_hash = hashlib.sha256(parent_id.encode()).hexdigest()[:16]
        return f"topic:{parent_hash}:{index:04d}"
    
    def _generate_turn_id(self, parent_id: str, index: int) -> str:
        """Generate L6 turn ID."""
        if self._identity:
            return self._identity.generate_span_id(parent_id, index).replace("span:", "turn:")
        import hashlib
        parent_hash = hashlib.sha256(parent_id.encode()).hexdigest()[:16]
        return f"turn:{parent_hash}:{index:04d}"
    
    def _generate_message_id(self, conversation_id: str, index: int) -> str:
        """Generate L5 message ID."""
        if self._identity:
            return self._identity.generate_message_id(conversation_id, index)
        import hashlib
        conv_hash = hashlib.sha256(conversation_id.encode()).hexdigest()[:16]
        return f"msg:{conv_hash}:{index:04d}"
    
    def _generate_sentence_id(self, parent_id: str, index: int) -> str:
        """Generate L4 sentence ID."""
        if self._identity:
            return self._identity.generate_sentence_id(parent_id, index)
        import hashlib
        parent_hash = hashlib.sha256(parent_id.encode()).hexdigest()[:16]
        return f"sent:{parent_hash}:{index:04d}"
    
    def _generate_span_id(self, parent_id: str, index: int) -> str:
        """Generate L3 span ID."""
        if self._identity:
            return self._identity.generate_span_id(parent_id, index)
        import hashlib
        parent_hash = hashlib.sha256(parent_id.encode()).hexdigest()[:16]
        return f"span:{parent_hash}:{index:04d}"
    
    def _generate_word_id(self, parent_id: str, index: int) -> str:
        """Generate L2 word ID."""
        if self._identity:
            return self._identity.generate_word_id(parent_id, index)
        import hashlib
        parent_hash = hashlib.sha256(parent_id.encode()).hexdigest()[:16]
        return f"word:{parent_hash}:{index:04d}"
    
    # =========================================================================
    # Conversation Building
    # =========================================================================
    
    def _build_conversation(self, raw: dict[str, Any]) -> ConversationL8:
        """Build L8 conversation with full hierarchy."""
        source_uuid = raw.get("uuid", "unknown")
        conv_id = self._generate_conversation_id(source_uuid)
        
        # Extract chat messages
        chat_messages = raw.get("chat_messages", [])
        
        # Build title
        title = raw.get("name") or raw.get("title", "Untitled")
        if title == "Untitled" and chat_messages:
            first_msg = chat_messages[0].get("text", "")[:50]
            title = first_msg or "Conversation"
        
        # Get participants
        participants = list({
            msg.get("sender", "unknown") 
            for msg in chat_messages
        })
        
        # Create L8
        conversation = ConversationL8(
            entity_id=conv_id,
            conversation_id=conv_id,
            text=title,
            source_uuid=source_uuid,
            title=title,
            participants=participants,
        )
        
        # Build L7 topic segments (single segment for now, LLM can split later)
        topic_id = self._generate_topic_id(conv_id, 0)
        topic = TopicSegmentL7(
            entity_id=topic_id,
            text=title,
            parent_id=conv_id,
            conversation_id=conv_id,
            topic_label=title,
        )
        
        # Build L6 turns and L5 messages
        turns = []
        current_speaker = None
        current_turn = None
        turn_index = 0
        msg_index = 0
        
        for chat_msg in chat_messages:
            sender = chat_msg.get("sender", "unknown")
            text = chat_msg.get("text", "")
            
            if not text.strip():
                continue
            
            # New turn on speaker change
            if sender != current_speaker:
                if current_turn:
                    turns.append(current_turn)
                
                turn_id = self._generate_turn_id(topic_id, turn_index)
                current_turn = TurnL6(
                    entity_id=turn_id,
                    text="",
                    parent_id=topic_id,
                    conversation_id=conv_id,
                    topic_segment_id=topic_id,
                    speaker=sender,
                )
                current_speaker = sender
                turn_index += 1
            
            # Create L5 message
            msg_id = self._generate_message_id(conv_id, msg_index)
            message = MessageL5(
                entity_id=msg_id,
                text=text,
                parent_id=current_turn.entity_id,
                conversation_id=conv_id,
                turn_id=current_turn.entity_id,
                role=sender,
                source_timestamp=self._parse_timestamp(chat_msg.get("created_at")),
            )
            
            # Process deeply if configured
            if self._config.min_level <= 4:
                self._process_message_deeply(message)
            
            current_turn.children.append(message)
            current_turn.text = " ".join(
                m.text[:50] for m in current_turn.children
            )
            msg_index += 1
        
        # Add last turn
        if current_turn:
            turns.append(current_turn)
        
        topic.children = turns
        conversation.children = [topic]
        
        # Update child counts
        self._update_counts(conversation)
        
        return conversation
    
    def _process_message_deeply(self, message: MessageL5) -> None:
        """Process message to L4/L3/L2 using LLM."""
        if not self._ollama:
            return
        
        prompt = FULL_MESSAGE_ANALYSIS_PROMPT.format(
            message_text=message.text,
            speaker=message.role or "unknown",
        )
        result = self._ollama.extract_json(prompt)
        
        if not result or not isinstance(result, dict):
            return
        
        sentences = result.get("sentences", [])
        for sent_idx, sent_data in enumerate(sentences):
            sent_text = sent_data.get("text", "")
            sent_id = self._generate_sentence_id(message.entity_id, sent_idx)
            
            sentence = SentenceL4(
                entity_id=sent_id,
                text=sent_text,
                parent_id=message.entity_id,
                conversation_id=message.conversation_id,
                message_id=message.entity_id,
                sentence_type=sent_data.get("sentence_type") or sent_data.get("type"),
                complexity=sent_data.get("complexity"),
                mood=sent_data.get("mood"),
            )
            
            # Process spans (L3)
            spans = sent_data.get("spans", [])
            for span_idx, span_data in enumerate(spans):
                span_text = span_data.get("text", "")
                span_id = self._generate_span_id(sent_id, span_idx)
                
                span = SpanL3(
                    entity_id=span_id,
                    text=span_text,
                    parent_id=sent_id,
                    conversation_id=message.conversation_id,
                    sentence_id=sent_id,
                    span_type=span_data.get("span_type") or span_data.get("type"),
                    entities=span_data.get("entities", []),
                    dependencies=span_data.get("dependencies", []),
                )
                
                # Process words (L2)
                words = span_data.get("words", [])
                for word_idx, word_data in enumerate(words):
                    word_text = word_data.get("text", "")
                    word_id = self._generate_word_id(span_id, word_idx)
                    
                    word = WordL2(
                        entity_id=word_id,
                        text=word_text,
                        parent_id=span_id,
                        conversation_id=message.conversation_id,
                        span_id=span_id,
                        word_type=word_data.get("word_type") or word_data.get("type"),
                        is_key_term=word_data.get("is_key_term") or word_data.get("is_key", False),
                        canonical_form=word_data.get("canonical_form"),
                        semantic_role=word_data.get("semantic_role"),
                    )
                    span.children.append(word)
                
                sentence.children.append(span)
            
            message.children.append(sentence)
    
    def _parse_timestamp(self, ts: Any) -> Optional[datetime]:
        """Parse timestamp from various formats."""
        if ts is None:
            return None
        if isinstance(ts, datetime):
            return ts
        if isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None
    
    def _update_counts(self, conversation: ConversationL8) -> None:
        """Update child counts throughout hierarchy.
        
        Note: l7_count, l6_count, l5_count are @computed_field on ConversationL8,
        so they compute automatically from len(children).
        """
        for topic in conversation.children:
            turns = topic.children
            
            for turn in turns:
                messages = turn.children
                turn.child_count = len(messages)
                
                for msg in messages:
                    sentences = msg.children
                    msg.child_count = len(sentences)
                    
                    for sent in sentences:
                        spans = sent.children
                        sent.child_count = len(spans)
                        
                        for span in spans:
                            words = span.children
                            span.child_count = len(words)
            
            topic.child_count = len(turns)
        
        conversation.child_count = len(conversation.children)
    
    def _flatten_entities(self, conversation: ConversationL8, source_file: str = None, source_file_path: str = None) -> Iterator[dict[str, Any]]:
        """Flatten hierarchy to entity_unified records."""
        # L8
        entity = conversation.to_entity_unified(
            ingestion_job_id=self._run_id,
            source_file=source_file,
            source_file_path=source_file_path,
        )
        yield entity
        
        # L7
        for topic in conversation.children:
            entity = topic.to_entity_unified(
                ingestion_job_id=self._run_id,
                source_file=source_file,
                source_file_path=source_file_path,
            )
            yield entity
            
            # L6
            for turn in topic.children:
                entity = turn.to_entity_unified(
                    ingestion_job_id=self._run_id,
                    source_file=source_file,
                    source_file_path=source_file_path,
                )
                yield entity
                
                # L5
                for msg in turn.children:
                    entity = msg.to_entity_unified(
                        ingestion_job_id=self._run_id,
                        source_file=source_file,
                        source_file_path=source_file_path,
                    )
                    yield entity
                    
                    # L4
                    for sent in msg.children:
                        entity = sent.to_entity_unified(
                            ingestion_job_id=self._run_id,
                            source_file=source_file,
                            source_file_path=source_file_path,
                        )
                        yield entity
                        
                        # L3
                        for span in sent.children:
                            entity = span.to_entity_unified(
                                ingestion_job_id=self._run_id,
                                source_file=source_file,
                                source_file_path=source_file_path,
                            )
                            yield entity
                            
                            # L2
                            for word in span.children:
                                entity = word.to_entity_unified(
                                    ingestion_job_id=self._run_id,
                                    source_file=source_file,
                                    source_file_path=source_file_path,
                                )
                                yield entity
    
    # =========================================================================
    # Enrichment Extraction
    # =========================================================================
    
    def _extract_enrichment(self, entity_id: str, text: str, level: int, speaker: str = "unknown") -> Optional[EntityEnrichment]:
        """Extract enrichments for an entity using LLM.
        
        Args:
            entity_id: The entity being enriched
            text: Text to analyze
            level: Entity level (2-8)
            speaker: Speaker/role for context
            
        Returns:
            EntityEnrichment or None if extraction fails
        """
        if not self._ollama or not self._config.enable_enrichments:
            return None
        
        if level not in self._config.enrichment_levels:
            return None
        
        # Skip very short texts
        if len(text.strip()) < 10:
            return None
        
        prompt = ENRICHMENT_EXTRACTION_PROMPT.format(
            text=text,
            entity_type=["word", "span", "sentence", "message", "turn", "topic", "conversation"][8 - level],
            level=level,
            speaker=speaker,
        )
        
        try:
            result = self._ollama.extract_json(prompt, temperature=0.2)
            if result and isinstance(result, dict):
                return create_enrichment_from_llm(
                    entity_id=entity_id,
                    text=text,
                    llm_response=result,
                    batch_id=self._run_id,
                )
        except Exception as e:
            self.logger.warning(
                "enrichment_extraction_failed",
                entity_id=entity_id,
                error=str(e),
            )
        
        return None
    
    def _flatten_entities_with_enrichments(
        self, 
        conversation: ConversationL8,
        source_file: str = None,
        source_file_path: str = None,
    ) -> tuple[Iterator[dict[str, Any]], Iterator[dict[str, Any]]]:
        """Flatten hierarchy to both entity_unified and entity_enrichments records.
        
        Returns:
            Tuple of (entities iterator, enrichments iterator)
        """
        entities = []
        enrichments = []
        
        def process_entity(entity_obj, level: int, speaker: str = "unknown"):
            """Process a single entity and optionally extract enrichments."""
            entity = entity_obj.to_entity_unified(
                ingestion_job_id=self._run_id,
                source_file=source_file,
                source_file_path=source_file_path,
            )
            entities.append(entity)
            
            # Extract enrichments if enabled for this level
            if self._config.enable_enrichments and level in self._config.enrichment_levels:
                enrichment = self._extract_enrichment(
                    entity_id=entity["entity_id"],
                    text=entity["text"],
                    level=level,
                    speaker=speaker,
                )
                if enrichment:
                    enrichments.append(enrichment.to_entity_enrichments())
        
        # L8
        process_entity(conversation, 8)
        
        # L7
        for topic in conversation.children:
            process_entity(topic, 7)
            
            # L6
            for turn in topic.children:
                speaker = turn.speaker if hasattr(turn, 'speaker') else "unknown"
                process_entity(turn, 6, speaker)
                
                # L5
                for msg in turn.children:
                    role = msg.role if hasattr(msg, 'role') else speaker
                    process_entity(msg, 5, role)
                    
                    # L4
                    for sent in msg.children:
                        process_entity(sent, 4, role)
                        
                        # L3
                        for span in sent.children:
                            process_entity(span, 3, role)
                            
                            # L2
                            for word in span.children:
                                process_entity(word, 2, role)
        
        return iter(entities), iter(enrichments)
    
    # =========================================================================
    # Batch Processing API
    # =========================================================================
    
    def process_batch(
        self,
        conversations: list[dict[str, Any]],
        output_file: Optional[Path] = None,
        enrichments_file: Optional[Path] = None,
    ) -> dict[str, Any]:
        """Process a batch of conversations with full tracking.
        
        Args:
            conversations: List of raw conversation dicts
            output_file: Path to write entity_unified JSONL
            enrichments_file: Path to write entity_enrichments JSONL
            
        Returns:
            Results dict with counts, files, and any errors
        """
        self.logger.info(
            "batch_started",
            conversation_count=len(conversations),
            run_id=self._run_id,
            enrichments_enabled=self._config.enable_enrichments,
        )
        
        results = {
            "run_id": self._run_id,
            "total_conversations": len(conversations),
            "processed": 0,
            "failed": 0,
            "total_entities": 0,
            "total_enrichments": 0,
            "errors": [],
        }
        
        all_entities = []
        all_enrichments = []
        
        for i, conv in enumerate(conversations):
            try:
                self.logger.info(
                    "processing_batch_item",
                    index=i,
                    uuid=conv.get("uuid"),
                )
                
                result = self.process(conv)
                all_entities.extend(result["entities"])
                all_enrichments.extend(result.get("enrichments", []))
                results["processed"] += 1
                results["total_entities"] += result["entity_count"]
                results["total_enrichments"] += result.get("enrichment_count", 0)
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "uuid": conv.get("uuid"),
                    "error": str(e),
                })
                self.logger.error(
                    "batch_item_failed",
                    uuid=conv.get("uuid"),
                    error=str(e),
                )
        
        # Write entity_unified output
        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, "w") as f:
                for entity in all_entities:
                    f.write(json.dumps(entity, default=str) + "\n")
            
            results["output_file"] = str(output_file)
            self.logger.info(
                "entities_output_written",
                file=str(output_file),
                entity_count=len(all_entities),
            )
        
        # Write entity_enrichments output
        if enrichments_file and all_enrichments:
            enrichments_file = Path(enrichments_file)
            enrichments_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(enrichments_file, "w") as f:
                for enrichment in all_enrichments:
                    f.write(json.dumps(enrichment, default=str) + "\n")
            
            results["enrichments_file"] = str(enrichments_file)
            self.logger.info(
                "enrichments_output_written",
                file=str(enrichments_file),
                enrichment_count=len(all_enrichments),
            )
        
        self.logger.info(
            "batch_completed",
            **{k: v for k, v in results.items() if k != "errors"},
        )
        
        return results


# Convenience function for CLI usage
def create_refinery_service(config: Optional[RefineryConfig] = None) -> LLMRefineryService:
    """Create a refinery service instance."""
    return LLMRefineryService(config)
