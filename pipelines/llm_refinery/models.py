"""Data models for the L2-L8 hierarchical conversation structure.

These Pydantic models define the schema for each layer, designed
for LLM-based extraction rather than rigid NLP rules.

Lineage, Counts, and Denormalization:
- All entities track their full ancestry (parent_id + all ancestor IDs)
- Count fields (l2_count through l7_count) are denormalized at each level
- Source lineage tracks processing provenance
"""

from __future__ import annotations

import hashlib
from datetime import datetime, UTC
from typing import Any, Optional
from pydantic import BaseModel, Field, computed_field


def generate_id(prefix: str, content: str, parent_id: str = "", index: int = 0) -> str:
    """Generate deterministic entity ID.
    
    Format: {prefix}:{hash16}:{index:04d}
    """
    hash_input = f"{parent_id}:{content}:{index}"
    content_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    return f"{prefix}:{content_hash}:{index:04d}"


def clamp_sentiment(value: Any) -> Optional[float]:
    """Clamp sentiment value to [-1.0, 1.0] range.
    
    LLMs sometimes produce values outside the valid range.
    Returns None if value is not a valid number.
    """
    if value is None:
        return None
    try:
        f = float(value)
        return max(-1.0, min(1.0, f))
    except (TypeError, ValueError):
        return None


class EntityBase(BaseModel):
    """Base class for all L2-L8 entities."""
    
    entity_id: str
    level: int
    entity_type: str
    text: str
    parent_id: Optional[str] = None
    source_pipeline: str = "llm_refinery"
    
    # LLM-extracted metadata
    sentiment: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Sentiment score")
    emotions: list[str] = Field(default_factory=list, description="Detected emotions")
    intent: Optional[str] = Field(None, description="Detected intent/purpose")
    topics: list[str] = Field(default_factory=list, description="Relevant topics")
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_timestamp: Optional[datetime] = None
    
    # Hierarchy links (denormalized for efficient queries)
    conversation_id: Optional[str] = None
    topic_segment_id: Optional[str] = None
    turn_id: Optional[str] = None
    message_id: Optional[str] = None
    sentence_id: Optional[str] = None
    span_id: Optional[str] = None
    word_id: Optional[str] = None  # For self-reference at L2
    
    # COUNT ROLLUP FIELDS (denormalized for O(1) lookups)
    # Each level stores counts of all descendant levels
    l7_count: int = Field(0, description="Count of L7 topic segments (L8 only)")
    l6_count: int = Field(0, description="Count of L6 turns")
    l5_count: int = Field(0, description="Count of L5 messages")
    l4_count: int = Field(0, description="Count of L4 sentences")
    l3_count: int = Field(0, description="Count of L3 spans")
    l2_count: int = Field(0, description="Count of L2 words")
    
    # SOURCE LINEAGE (processing provenance)
    source_ids: list[str] = Field(default_factory=list, description="Contributing source IDs")
    source_file: Optional[str] = Field(None, description="Original source filename")
    source_file_path: Optional[str] = Field(None, description="Full source file path")
    source_system: Optional[str] = Field(None, description="Source system identifier")
    
    # LINEAGE TRACKING (processing history)
    lineage: dict[str, Any] = Field(default_factory=dict, description="Processing provenance")
    
    # Legacy child count field
    child_count: int = 0
    
    def compute_counts(self) -> dict[str, int]:
        """Compute descendant counts from children. Override in subclasses."""
        return {
            "l7_count": self.l7_count,
            "l6_count": self.l6_count,
            "l5_count": self.l5_count,
            "l4_count": self.l4_count,
            "l3_count": self.l3_count,
            "l2_count": self.l2_count,
        }
    
    def to_entity_unified(self, ingestion_job_id: str = None, source_file: str = None, source_file_path: str = None) -> dict[str, Any]:
        """Convert to entity_unified BigQuery schema (37 fields).
        
        Includes:
        - Full hierarchical ID denormalization (conversation_id through word_id)
        - Count rollup fields (l2_count through l7_count)
        - Source lineage tracking (source_ids, source_file, etc.)
        - Processing lineage (in metadata)
        
        Args:
            ingestion_job_id: Run ID from the service (passed in)
            source_file: Original source filename
            source_file_path: Full path to source file
        """
        # Build metadata, converting any datetime to ISO string
        metadata = self.model_dump(
            exclude={
                "entity_id", "level", "entity_type", "text", 
                "parent_id", "source_pipeline", "created_at",
                "conversation_id", "topic_segment_id", "turn_id",
                "message_id", "sentence_id", "span_id", "word_id",
                "child_count", "children",  # Don't include children in metadata
                # Exclude count fields - they go in main schema
                "l7_count", "l6_count", "l5_count", "l4_count", "l3_count", "l2_count",
                # Exclude source fields - they go in main schema  
                "source_ids", "source_file", "source_file_path", "source_system",
                "lineage",  # Stored separately
                "role",  # Now a top-level column
                "canonical_form",  # Top-level column for L2
            }
        )
        # Convert any datetime objects in metadata to ISO strings
        for key, value in metadata.items():
            if isinstance(value, datetime):
                metadata[key] = value.isoformat()
        
        # Add lineage to metadata
        if self.lineage:
            metadata["lineage"] = self.lineage
        
        # Compute counts (will be overridden by subclasses with children)
        counts = self.compute_counts()
        
        return {
            # Identity
            "entity_id": self.entity_id,
            "level": self.level,
            "entity_type": self.entity_type,
            "entity_mode": "active",
            "parent_id": self.parent_id,
            
            # Denormalized hierarchy IDs
            "conversation_id": self.conversation_id,
            "topic_segment_id": self.topic_segment_id,
            "turn_id": self.turn_id,
            "message_id": self.message_id,
            "sentence_id": self.sentence_id,
            "span_id": self.span_id,
            "word_id": self.word_id,
            
            # Content
            "text": self.text,
            
            # Source fields (parameters override base class attributes)
            "source_pipeline": self.source_pipeline,
            "source_ids": self.source_ids,
            "source_file": source_file or self.source_file,
            "source_file_path": source_file_path or self.source_file_path,
            "source_system": self.source_system,
            
            # Count rollup fields (denormalized)
            "l7_count": counts.get("l7_count", 0),
            "l6_count": counts.get("l6_count", 0),
            "l5_count": counts.get("l5_count", 0),
            "l4_count": counts.get("l4_count", 0),
            "l3_count": counts.get("l3_count", 0),
            "l2_count": counts.get("l2_count", 0),
            
            # Metadata (includes lineage)
            "metadata": metadata,
            
            # Role (user/assistant/system) - only populated for L5 messages, L6 turns
            "role": getattr(self, "role", None) or getattr(self, "speaker", None),
            
            # Persona (named AI like custom GPT or Gemini Gem) - intentionally None
            "persona": None,
            
            # Canonical form (base/lemma form) - only for L2 words
            "canonical_form": getattr(self, "canonical_form", None),
            
            # Timestamps
            "created_at": self.created_at.isoformat(),
            "updated_at": self.created_at.isoformat(),  # Same as created_at on insert
            "source_message_timestamp": self.source_timestamp.isoformat() if self.source_timestamp else None,
            "ingestion_timestamp": datetime.now(UTC).isoformat(),
            
            # Content date (extracted from source_message_timestamp)
            "content_date": self.source_timestamp.date().isoformat() if self.source_timestamp else None,
            
            # Ingestion tracking
            "ingestion_job_id": ingestion_job_id,
            "validation_status": "pending",  # Default to pending
        }


class WordL2(EntityBase):
    """L2: Word/Token level entity with semantic attributes.
    
    L2 is a leaf node - no children, no count fields used.
    """
    
    level: int = 2
    entity_type: str = "word"
    
    # Linguistic attributes (LLM-extracted, not POS tags)
    word_type: Optional[str] = Field(None, description="noun, verb, entity, modifier, etc.")
    is_key_term: bool = Field(False, description="Important to meaning")
    canonical_form: Optional[str] = Field(None, description="Base/lemma form")
    semantic_role: Optional[str] = Field(None, description="agent, object, location, etc.")
    
    @classmethod
    def from_llm(cls, word: str, parent_id: str, index: int, llm_attrs: dict, 
                 hierarchy_ids: dict = None) -> "WordL2":
        """Create from LLM extraction with full hierarchy denormalization."""
        hierarchy_ids = hierarchy_ids or {}
        word_id = generate_id("word", word, parent_id, index)
        
        # Handle both 'word_type' and 'type' field names
        word_type = llm_attrs.get("word_type") or llm_attrs.get("type")
        # Handle both 'is_key_term' and 'is_key' field names
        is_key = llm_attrs.get("is_key_term") or llm_attrs.get("is_key", False)
        
        return cls(
            entity_id=word_id,
            text=word,
            parent_id=parent_id,
            # Self-reference for word_id
            word_id=word_id,
            # Denormalized hierarchy IDs from ancestors
            span_id=parent_id,
            sentence_id=hierarchy_ids.get("sentence_id"),
            message_id=hierarchy_ids.get("message_id"),
            turn_id=hierarchy_ids.get("turn_id"),
            topic_segment_id=hierarchy_ids.get("topic_segment_id"),
            conversation_id=hierarchy_ids.get("conversation_id"),
            # Attributes
            word_type=word_type,
            is_key_term=is_key,
            canonical_form=llm_attrs.get("canonical_form"),
            semantic_role=llm_attrs.get("semantic_role"),
            sentiment=clamp_sentiment(llm_attrs.get("sentiment")),
            # Lineage
            source_ids=hierarchy_ids.get("source_ids", []),
        )


class SpanL3(EntityBase):
    """L3: Span/Phrase level entity - meaningful phrase chunks.
    
    L3 aggregates l2_count from children.
    """
    
    level: int = 3
    entity_type: str = "span"
    
    # Span attributes
    span_type: Optional[str] = Field(None, description="noun_phrase, verb_phrase, clause, etc.")
    is_complete_thought: bool = Field(False, description="Can stand alone semantically")
    named_entities: list[dict] = Field(default_factory=list, description="Extracted entities")
    
    children: list[WordL2] = Field(default_factory=list)
    
    def compute_counts(self) -> dict[str, int]:
        """Compute descendant counts from children."""
        return {
            "l7_count": 0,
            "l6_count": 0,
            "l5_count": 0,
            "l4_count": 0,
            "l3_count": 0,
            "l2_count": len(self.children),
        }
    
    @classmethod
    def from_llm(
        cls, 
        span_text: str, 
        parent_id: str, 
        index: int, 
        llm_attrs: dict,
        words: list[WordL2] = None,
        hierarchy_ids: dict = None,
    ) -> "SpanL3":
        """Create from LLM extraction with full hierarchy denormalization."""
        hierarchy_ids = hierarchy_ids or {}
        span_id = generate_id("span", span_text, parent_id, index)
        # Handle both 'span_type' and 'type' field names
        span_type = llm_attrs.get("span_type") or llm_attrs.get("type")
        # Handle 'entities' or 'named_entities'
        entities = llm_attrs.get("named_entities") or llm_attrs.get("entities", [])
        return cls(
            entity_id=span_id,
            text=span_text,
            parent_id=parent_id,
            # Self-reference and hierarchy
            span_id=span_id,
            sentence_id=parent_id,
            message_id=hierarchy_ids.get("message_id"),
            turn_id=hierarchy_ids.get("turn_id"),
            topic_segment_id=hierarchy_ids.get("topic_segment_id"),
            conversation_id=hierarchy_ids.get("conversation_id"),
            # Attributes
            span_type=span_type,
            is_complete_thought=llm_attrs.get("is_complete_thought", False),
            named_entities=entities,
            sentiment=clamp_sentiment(llm_attrs.get("sentiment")),
            intent=llm_attrs.get("intent"),
            children=words or [],
            # Lineage
            source_ids=hierarchy_ids.get("source_ids", []),
        )


class SentenceL4(EntityBase):
    """L4: Sentence level entity - grammatical sentence unit.
    
    L4 aggregates l3_count (spans) and l2_count (words).
    """
    
    level: int = 4
    entity_type: str = "sentence"
    
    # Sentence attributes
    sentence_type: Optional[str] = Field(None, description="declarative, question, command, etc.")
    complexity: Optional[str] = Field(None, description="simple, compound, complex")
    is_rhetorical: bool = Field(False)
    
    children: list[SpanL3] = Field(default_factory=list)
    
    def compute_counts(self) -> dict[str, int]:
        """Compute descendant counts: l3 spans, l2 words."""
        l3_count = len(self.children)
        l2_count = sum(len(span.children) for span in self.children)
        return {
            "l7_count": 0,
            "l6_count": 0,
            "l5_count": 0,
            "l4_count": 0,
            "l3_count": l3_count,
            "l2_count": l2_count,
        }

    # NOTE: l3_count inherited from EntityBase, updated via from_llm()
    # Removed @computed_field as it conflicts with parent Field definition

    @classmethod
    def from_llm(
        cls,
        sentence_text: str,
        parent_id: str,
        index: int,
        llm_attrs: dict,
        spans: list[SpanL3] = None,
        hierarchy_ids: dict = None,
    ) -> "SentenceL4":
        """Create from LLM extraction with full hierarchy denormalization."""
        hierarchy_ids = hierarchy_ids or {}
        sent_id = generate_id("sent", sentence_text, parent_id, index)
        # Handle both 'sentence_type' and 'type' field names
        sentence_type = llm_attrs.get("sentence_type") or llm_attrs.get("type")
        return cls(
            entity_id=sent_id,
            text=sentence_text,
            parent_id=parent_id,
            # Self-reference and hierarchy
            sentence_id=sent_id,
            message_id=parent_id,
            turn_id=hierarchy_ids.get("turn_id"),
            topic_segment_id=hierarchy_ids.get("topic_segment_id"),
            conversation_id=hierarchy_ids.get("conversation_id"),
            # Attributes
            sentence_type=sentence_type,
            complexity=llm_attrs.get("complexity"),
            is_rhetorical=llm_attrs.get("is_rhetorical", False),
            sentiment=clamp_sentiment(llm_attrs.get("sentiment")),
            intent=llm_attrs.get("intent"),
            emotions=llm_attrs.get("emotions", []),
            children=spans or [],
            # Lineage
            source_ids=hierarchy_ids.get("source_ids", []),
        )


class MessageL5(EntityBase):
    """L5: Message level entity - single speaker utterance.
    
    L5 aggregates l4_count (sentences), l3_count (spans), l2_count (words).
    """
    
    level: int = 5
    entity_type: str = "message"
    
    # Message attributes
    role: str = Field(..., description="human, assistant, system")
    message_type: Optional[str] = Field(None, description="question, statement, command, etc.")
    has_code: bool = Field(False)
    has_attachment: bool = Field(False)
    
    children: list[SentenceL4] = Field(default_factory=list)
    
    def compute_counts(self) -> dict[str, int]:
        """Compute descendant counts: l4 sentences, l3 spans, l2 words."""
        l4_count = len(self.children)
        l3_count = sum(len(sent.children) for sent in self.children)
        l2_count = sum(
            sum(len(span.children) for span in sent.children)
            for sent in self.children
        )
        return {
            "l7_count": 0,
            "l6_count": 0,
            "l5_count": 0,
            "l4_count": l4_count,
            "l3_count": l3_count,
            "l2_count": l2_count,
        }
    
    @classmethod
    def from_raw(
        cls,
        raw_message: dict,
        parent_id: str,
        index: int,
        conversation_id: str,
        hierarchy_ids: dict = None,
    ) -> "MessageL5":
        """Create from raw conversation message with full hierarchy denormalization."""
        hierarchy_ids = hierarchy_ids or {}
        text = raw_message.get("text", "")
        msg_id = generate_id("msg", text, parent_id, index)
        
        return cls(
            entity_id=msg_id,
            text=text,
            parent_id=parent_id,
            # Self-reference and hierarchy
            message_id=msg_id,
            turn_id=parent_id,
            topic_segment_id=hierarchy_ids.get("topic_segment_id"),
            conversation_id=conversation_id,
            # Attributes
            role=raw_message.get("sender", "human"),
            source_timestamp=datetime.fromisoformat(
                raw_message.get("created_at", "").replace("Z", "+00:00")
            ) if raw_message.get("created_at") else None,
            has_attachment=bool(raw_message.get("attachments")),
            # Lineage
            source_ids=hierarchy_ids.get("source_ids", []),
        )


class TurnL6(EntityBase):
    """L6: Turn level entity - speaker change boundary.
    
    L6 aggregates l5_count through l2_count.
    """
    
    level: int = 6
    entity_type: str = "turn"
    
    # Turn attributes
    speaker: str = Field(..., description="Who is speaking in this turn")
    turn_type: Optional[str] = Field(None, description="opening, response, clarification, etc.")
    is_continuation: bool = Field(False, description="Continues previous speaker's thought")
    
    children: list[MessageL5] = Field(default_factory=list)
    
    def compute_counts(self) -> dict[str, int]:
        """Compute descendant counts: l5 messages down to l2 words."""
        l5_count = len(self.children)
        l4_count = sum(len(msg.children) for msg in self.children)
        l3_count = sum(
            sum(len(sent.children) for sent in msg.children)
            for msg in self.children
        )
        l2_count = sum(
            sum(sum(len(span.children) for span in sent.children) for sent in msg.children)
            for msg in self.children
        )
        return {
            "l7_count": 0,
            "l6_count": 0,
            "l5_count": l5_count,
            "l4_count": l4_count,
            "l3_count": l3_count,
            "l2_count": l2_count,
        }
    
    @classmethod
    def from_messages(
        cls,
        messages: list[MessageL5],
        parent_id: str,
        index: int,
        conversation_id: str,
        hierarchy_ids: dict = None,
    ) -> "TurnL6":
        """Create from grouped messages with full hierarchy denormalization."""
        hierarchy_ids = hierarchy_ids or {}
        speaker = messages[0].role if messages else "unknown"
        combined_text = " ".join(m.text for m in messages)
        turn_id = generate_id("turn", combined_text[:100], parent_id, index)
        
        return cls(
            entity_id=turn_id,
            text=combined_text[:500] + "..." if len(combined_text) > 500 else combined_text,
            parent_id=parent_id,
            # Self-reference and hierarchy
            turn_id=turn_id,
            topic_segment_id=parent_id,
            conversation_id=conversation_id,
            # Attributes
            speaker=speaker,
            children=messages,
            # Lineage
            source_ids=hierarchy_ids.get("source_ids", []),
        )


class TopicSegmentL7(EntityBase):
    """L7: Topic Segment level - semantic groupings within conversation.
    
    L7 aggregates l6_count through l2_count.
    """
    
    level: int = 7
    entity_type: str = "topic_segment"
    
    # Topic attributes (LLM-detected)
    topic_label: str = Field(..., description="Short label for this topic")
    topic_description: Optional[str] = Field(None, description="Longer description")
    is_digression: bool = Field(False, description="Off main topic")
    
    children: list[TurnL6] = Field(default_factory=list)
    
    def compute_counts(self) -> dict[str, int]:
        """Compute descendant counts: l6 turns down to l2 words."""
        l6_count = len(self.children)
        l5_count = sum(len(turn.children) for turn in self.children)
        l4_count = sum(
            sum(len(msg.children) for msg in turn.children)
            for turn in self.children
        )
        l3_count = sum(
            sum(sum(len(sent.children) for sent in msg.children) for msg in turn.children)
            for turn in self.children
        )
        l2_count = sum(
            sum(sum(sum(len(span.children) for span in sent.children) for sent in msg.children) for msg in turn.children)
            for turn in self.children
        )
        return {
            "l7_count": 0,
            "l6_count": l6_count,
            "l5_count": l5_count,
            "l4_count": l4_count,
            "l3_count": l3_count,
            "l2_count": l2_count,
        }
    
    @classmethod
    def from_llm(
        cls,
        turns: list[TurnL6],
        parent_id: str,
        index: int,
        llm_attrs: dict,
        conversation_id: str,
        hierarchy_ids: dict = None,
    ) -> "TopicSegmentL7":
        """Create from LLM topic detection with full hierarchy denormalization."""
        hierarchy_ids = hierarchy_ids or {}
        combined_text = " ".join(t.text[:200] for t in turns)
        segment_id = generate_id("topic", combined_text[:100], parent_id, index)
        
        return cls(
            entity_id=segment_id,
            text=combined_text[:500] + "..." if len(combined_text) > 500 else combined_text,
            parent_id=parent_id,
            # Self-reference and hierarchy
            topic_segment_id=segment_id,
            conversation_id=conversation_id,
            # Attributes
            topic_label=llm_attrs.get("topic_label", f"Topic {index + 1}"),
            topic_description=llm_attrs.get("topic_description"),
            is_digression=llm_attrs.get("is_digression", False),
            topics=llm_attrs.get("topics", []),
            children=turns,
            # Lineage
            source_ids=hierarchy_ids.get("source_ids", []),
        )


class ConversationL8(EntityBase):
    """L8: Conversation level - the root entity.
    
    L8 aggregates l7_count through l2_count (all descendant levels).
    Sets source lineage for the entire hierarchy.
    """
    
    level: int = 8
    entity_type: str = "conversation"
    
    # Conversation attributes
    title: Optional[str] = Field(None, description="Conversation title/name")
    summary: Optional[str] = Field(None, description="AI-generated summary")
    source_uuid: str = Field(..., description="Original source UUID")
    
    # Participants
    participants: list[str] = Field(default_factory=list)
    
    children: list[TopicSegmentL7] = Field(default_factory=list)
    
    def compute_counts(self) -> dict[str, int]:
        """Compute all descendant counts: l7 segments down to l2 words."""
        l7_count = len(self.children)
        l6_count = sum(len(seg.children) for seg in self.children)
        l5_count = sum(
            sum(len(turn.children) for turn in seg.children)
            for seg in self.children
        )
        l4_count = sum(
            sum(sum(len(msg.children) for msg in turn.children) for turn in seg.children)
            for seg in self.children
        )
        l3_count = sum(
            sum(sum(sum(len(sent.children) for sent in msg.children) for msg in turn.children) for turn in seg.children)
            for seg in self.children
        )
        l2_count = sum(
            sum(sum(sum(sum(len(span.children) for span in sent.children) for sent in msg.children) for msg in turn.children) for turn in seg.children)
            for seg in self.children
        )
        return {
            "l7_count": l7_count,
            "l6_count": l6_count,
            "l5_count": l5_count,
            "l4_count": l4_count,
            "l3_count": l3_count,
            "l2_count": l2_count,
        }
    
    @classmethod
    def from_raw(cls, raw_conversation: dict, source_file: str = None, source_file_path: str = None) -> "ConversationL8":
        """Create from raw conversation data with source lineage."""
        source_uuid = raw_conversation.get("uuid", "")
        title = raw_conversation.get("name", "")
        summary = raw_conversation.get("summary", "")
        
        conv_id = generate_id("conv", source_uuid, "", 0)
        
        # Extract participant roles
        messages = raw_conversation.get("chat_messages", [])
        participants = list(set(m.get("sender", "unknown") for m in messages))
        
        return cls(
            entity_id=conv_id,
            conversation_id=conv_id,
            text=title or f"Conversation {source_uuid[:8]}",
            source_uuid=source_uuid,
            title=title,
            summary=summary,
            participants=participants,
            source_timestamp=datetime.fromisoformat(
                raw_conversation.get("created_at", "").replace("Z", "+00:00")
            ) if raw_conversation.get("created_at") else None,
            # Source lineage
            source_ids=[source_uuid] if source_uuid else [],
            source_file=source_file,
            source_file_path=source_file_path,
            source_system="claude_export",
        )
