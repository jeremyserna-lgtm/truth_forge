"""Stage 3: THE GATE - Generate canonical IDs from central identity service.

PATTERN: HOLD1 (cleaned) → AGENT (identity service) → HOLD2 (with canonical IDs)

**CRITICAL**: This stage generates IDs using the EXACT same logic as
src/truth_forge/services/identity.py (IdentityService class).

The ID format matches the central IdentityService to ensure:
- Consistent ID format across entire Truth Forge system
- Deduplication at the ID level  
- Hierarchical ID relationships (conversation → message → sentence → token)

Usage:
    stage = IdentityGateStage(config)
    result = stage.run()
"""

from __future__ import annotations

import hashlib
import logging
import re
from datetime import UTC, datetime
from typing import Any

from pipelines.core.stage import Stage


logger = logging.getLogger(__name__)


# ==============================================================================
# Central IdentityService Logic (Vendored from src/truth_forge/services/identity.py)
# ==============================================================================
# NOTE: This is the EXACT logic from the central IdentityService.
# Any changes here MUST be synced with the main implementation.

def _generate_hash(content: str, length: int = 16) -> str:
    """Generate truncated SHA-256 hash (from IdentityService)."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:length]


def _slugify(text: str) -> str:
    """Convert text to lowercase, hyphenated slug (from IdentityService)."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip ("-")


def _format_sequence(index: int, width: int = 4) -> str:
   """Zero-pad sequence number (from IdentityService)."""
    return f"{index:0{width}d}"


def generate_message_id(conversation_id: str, index: int) -> str:
    """Generate L5 message ID (from IdentityService.generate_message_id)."""
    conv_hash = _generate_hash(conversation_id, length=16)
    seq = _format_sequence(index)
    return f"msg:{conv_hash}:{seq}"


def generate_conversation_id(source_type: str, source_id: str) -> str:
    """Generate conversation ID (from IdentityService.generate_conversation_id)."""
    type_slug = _slugify(source_type)
    content_hash = _generate_hash(source_id, length=16)
    return f"conv:{type_slug}:{content_hash}"


class IdentityGateStage(Stage):
    """Stage 3: THE GATE - Generate canonical entity IDs."""

    STAGE_TYPE = "identity"

    def __init__(self, config: Any) -> None:
        """Initialize identity gate stage.
        
        Args:
            config: Stage configuration.
        """
        super().__init__(config)
        self.source_name = config.extra.get("source_name", "claude_code")
        logger.info(f"THE GATE initialized with source: {self.source_name}")

    def transform(self, record: dict[str, Any]) -> dict[str, Any]:
        """Generate canonical entity IDs using IdentityService logic.
        
        Args:
            record: Cleaned record.
            
        Returns:
            Record with canonical entity_id and conversation_id.
        """
        session_id = record["session_id"]
        message_index = record["message_index"]
        
        # Generate IDs using CENTRAL IDENTITY SERVICE LOGIC
        # This ensures IDs match across all Truth Forge pipelines
        conversation_id = generate_conversation_id(
            source_type=self.source_name,
            source_id=session_id,
        )
        
        entity_id = generate_message_id(
            conversation_id=session_id,  # Use raw session_id for determinism
            index=message_index,
        )
        
        # Add identity fields
        record["entity_id"] = entity_id
        record["conversation_id"] = conversation_id
        record["identity_created_at"] = datetime.now(UTC).isoformat()
        record["source_pipeline"] = self.source_name
        
        logger.debug(
            f"Generated canonical ID: {entity_id} "
            f"(conv: {conversation_id[:30]}...)"
        )
        
        return record


__all__ = ["IdentityGateStage"]
