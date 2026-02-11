"""Shared utilities for Claude Code pipeline stages.

Provides common functionality used across all stages:
- Deterministic ID generation (THE GATE)
- Metadata formatting
- Entity unified row construction
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any


def generate_hash(content: str, length: int = 16) -> str:
    """Generate truncated SHA-256 hash for deterministic IDs.
    
    Args:
        content: Content to hash.
        length: Number of characters to return.
        
    Returns:
        Truncated hex hash.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:length]


def format_sequence(index: int, width: int = 4) -> str:
    """Format sequence number as zero-padded string.
    
    Args:
        index: Sequence number.
        width: Total width (default 4 for 0000-9999).
        
    Returns:
        Zero-padded string.
    """
    return f"{index:0{width}d}"


def generate_conversation_id(source: str, session_id: str) -> str:
    """Generate conversation ID (L8).
    
    Format: conv:{source}:{hash}
    
    Args:
        source: Source name (e.g., 'claude_code').
        session_id: Session identifier.
        
    Returns:
        Conversation ID.
    """
    conv_hash = generate_hash(session_id, length=16)
    return f"conv:{source}:{conv_hash}"


def generate_message_id(session_id: str, message_index: int) -> str:
    """Generate message ID (L5).
    
    Format: msg:{hash}:{seq}
    
    Args:
        session_id: Session identifier.
        message_index: Zero-based message index.
        
    Returns:
        Message ID.
    """
    conv_hash = generate_hash(session_id, length=16)
    seq = format_sequence(message_index)
    return f"msg:{conv_hash}:{seq}"


def generate_sentence_id(message_id: str, sentence_index: int) -> str:
    """Generate sentence ID (L3).
    
    Format: sent:{hash}:{seq}
    
    Args:
        message_id: Parent message ID.
        sentence_index: Zero-based sentence index.
        
    Returns:
        Sentence ID.
    """
    parent_hash = generate_hash(message_id, length=16)
    seq = format_sequence(sentence_index)
    return f"sent:{parent_hash}:{seq}"


def generate_token_id(message_id: str, token_index: int) -> str:
    """Generate token ID (L1).
    
    Format: tok:{hash}:{seq}
    
    Args:
        message_id: Parent message ID.
        token_index: Zero-based token index.
        
    Returns:
        Token ID.
    """
    parent_hash = generate_hash(message_id, length=16)
    seq = format_sequence(token_index)
    return f"tok:{parent_hash}:{seq}"


def build_entity_unified_row(
    entity_id: str,
    level: int,
    entity_type: str,
    source_pipeline: str,
    parent_id: str | None = None,
    conversation_id: str | None = None,
    topic_segment_id: str | None = None,
    turn_id: str | None = None,
    message_id: str | None = None,
    sentence_id: str | None = None,
    span_id: str | None = None,
    word_id: str | None = None,
    text: str | None = None,
    source_file: str | None = None,
    content_date: str | None = None,
    metadata: dict[str, Any] | None = None,
    source_message_timestamp: str | None = None,
    persona: str | None = None,
    canonical_form: str | None = None,
    l7_count: int | None = None,
    l6_count: int | None = None,
    l5_count: int | None = None,
    l4_count: int | None = None,
    l3_count: int | None = None,
    l2_count: int | None = None,
    l1_count: int | None = None,
) -> dict[str, Any]:
    """Build entity_unified row matching exact BigQuery schema.
    
    Args:
        entity_id: Primary entity identifier.
        level: Entity level (1-8).
        entity_type: Type (token, sentence, message, conversation, etc.).
        source_pipeline: Source pipeline name.
        parent_id: Parent entity ID.
        conversation_id: L8 conversation ID.
        topic_segment_id: L7 topic segment ID.
        turn_id: L6 turn ID.
        message_id: L5 message ID.
        sentence_id: L3 sentence ID.
        span_id: L3 span ID (not used).
        word_id: L2 word ID (not used).
        text: Entity text content.
        source_file: Source file path.
        content_date: Content date (ISO format).
        metadata: Additional metadata (will be JSON serialized).
        source_message_timestamp: Original message timestamp.
        persona: Role (user, assistant, system).
        canonical_form: Normalized form (lemma for tokens).
        l7_count: Count of L7 children.
        l6_count: Count of L6 children.
        l5_count: Count of L5 children.
        l4_count: Count of L4 children.
        l3_count: Count of L3 children.
        l2_count: Count of L2 children.
        l1_count: Count of L1 children.
        
    Returns:
        Dictionary with exact entity_unified schema (34 columns).
    """
    now_iso = datetime.now(UTC).isoformat()
    
    return {
        "entity_id": entity_id,
        "level": level,
        "entity_type": entity_type,
        "entity_mode": "active",
        "parent_id": parent_id,
        "conversation_id": conversation_id,
        "topic_segment_id": topic_segment_id,
        "turn_id": turn_id,
        "message_id": message_id,
        "sentence_id": sentence_id,
        "span_id": span_id,
        "word_id": word_id,
        "text": text,
        "source_pipeline": source_pipeline,
        "source_file": source_file,
        "source_file_path": source_file,
        "source_system": source_pipeline,
        "source_ids": [entity_id],
        "content_date": content_date,
        "canonical_form": canonical_form,
        "persona": persona,
        "metadata": json.dumps(metadata) if metadata else None,
        "source_message_timestamp": source_message_timestamp,
        "created_at": now_iso,
        "updated_at": now_iso,
        "ingestion_timestamp": now_iso,
        "ingestion_job_id": f"{source_pipeline}-pipeline",
        "validation_status": "PASSED",
        "l7_count": l7_count,
        "l6_count": l6_count,
        "l5_count": l5_count,
        "l4_count": l4_count,
        "l3_count": l3_count,
        "l2_count": l2_count,
        "l1_count": l1_count,
    }


__all__ = [
    "generate_hash",
    "format_sequence",
    "generate_conversation_id",
    "generate_message_id",
    "generate_sentence_id",
    "generate_token_id",
    "build_entity_unified_row",
]
