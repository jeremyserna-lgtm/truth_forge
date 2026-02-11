"""Stages 7-16: Minimal implementations to complete the pipeline.

These are simplified implementations that make the pipeline functional.
Can be enhanced later with full enrichment logic.
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

from pipelines.core.stage import Stage
from .base import build_entity_unified_row


logger = logging.getLogger(__name__)


# ==============================================================================
# Stage 7: L5 Messages
# ==============================================================================

class L5MessagesStage(Stage):
    """Stage 7: Create L5 message entities with child counts."""

    STAGE_TYPE = "entity_creation"

    def __init__(self, config: Any) -> None:
        super().__init__(config)
        self.l1_counts: dict[str, int] = {}
        self.l3_counts: dict[str, int] = {}

    def read_input(self) -> list[dict[str, Any]]:
        """Load staged messages and count data from L1/L3 stages."""
        # Load token counts from stage 5
        stage_5_path = Path(self.config.input_path).parent / "claude_code_stage_5.jsonl"
        if stage_5_path.exists():
            with open(stage_5_path, encoding="utf-8") as f:
                for line in f:
                    record = json.loads(line)
                    msg_id = record.get("message_id")
                    if msg_id:
                        self.l1_counts[msg_id] = self.l1_counts.get(msg_id, 0) + 1
        
        # Load sentence counts from stage 6
        stage_6_path = Path(self.config.input_path).parent / "claude_code_stage_6.jsonl"
        if stage_6_path.exists():
            with open(stage_6_path, encoding="utf-8") as f:
                for line in f:
                    record = json.loads(line)
                    msg_id = record.get("message_id")
                    if msg_id:
                        self.l3_counts[msg_id] = self.l3_counts.get(msg_id, 0) + 1
        
        # Load staged messages
        return super().read_input()

    def transform(self, record: dict[str, Any]) -> dict[str, Any]:
        """Create L5 message entity with child counts."""
        entity_id = record["entity_id"]
        
        # Get child counts
        l1_count = self.l1_counts.get(entity_id, 0)
        l3_count = self.l3_counts.get(entity_id, 0)
        
        # Parse metadata from JSON string if needed
        metadata = record.get("metadata_json")
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        message_row = build_entity_unified_row(
            entity_id=entity_id,
            level=5,
            entity_type="message",
            source_pipeline=record["source_pipeline"],
            conversation_id=record["conversation_id"],
            message_id=entity_id,
            text=record["text"],
            persona=record.get("role"),
            metadata=metadata,
            content_date=record.get("content_date"),
            source_file=record.get("source_file"),
            source_message_timestamp=record.get("timestamp_utc"),
            l3_count=l3_count,
            l1_count=l1_count,
        )
        
        return message_row


# ==============================================================================
# Stage 8: L8 Conversations
# ==============================================================================

class L8ConversationsStage(Stage):
    """Stage 8: Create L8 conversation entities."""

    STAGE_TYPE = "entity_creation"

    def read_input(self) -> list[dict[str, Any]]:
        """Read L5 messages and group by conversation."""
        messages = super().read_input()
        
        # Group by conversation_id
        conversations = defaultdict(list)
        for msg in messages:
            conv_id = msg.get("conversation_id")
            if conv_id:
                conversations[conv_id].append(msg)
        
        # Return one record per conversation
        return [
            {
                "conversation_id": conv_id,
                "messages": msgs,
                "source_pipeline": msgs[0].get("source_pipeline") if msgs else "claude_code",
            }
            for conv_id, msgs in conversations.items()
        ]

    def transform(self, record: dict[str, Any]) -> dict[str, Any]:
        """Create L8 conversation entity."""
        conversation_id = record["conversation_id"]
        messages = record["messages"]
        
        conv_row = build_entity_unified_row(
            entity_id=conversation_id,
            level=8,
            entity_type="conversation",
            source_pipeline=record["source_pipeline"],
            conversation_id=conversation_id,
            metadata={"session_id": conversation_id.split(":")[-1]},
            l5_count=len(messages),
        )
        
        return conv_row


# ==============================================================================
# Stage 9-13: Enrichment Placeholders
# ==============================================================================

class EnrichmentPlaceholderStage(Stage):
    """Placeholder for enrichment stages (can be enhanced later)."""

    STAGE_TYPE = "enrichment"

    def transform(self, record: dict[str, Any]) -> dict[str, Any]:
        """Pass through - enrichment can be added later."""
        return record


# ==============================================================================
# Stage 14: Aggregation
# ==============================================================================

class AggregationStage(Stage):
    """Stage 14: Aggregate entities for finalization."""

    STAGE_TYPE = "aggregation"

    def transform(self, record: dict[str, Any]) -> dict[str, Any]:
        """Pass through with aggregation metadata."""
        record["aggregated_at"] = "2026-01-29"
        return record


# ==============================================================================
# Stage 15: Validation
# ==============================================================================

class ValidationStage(Stage):
    """Stage 15: Validate entities before promotion."""

    STAGE_TYPE = "validation"

    def transform(self, record: dict[str, Any]) -> dict[str, Any]:
        """Validate entity structure."""
        # Check required fields
        if not record.get("entity_id"):
            record["validation_status"] = "FAILED"
            record["validation_errors"] = ["Missing entity_id"]
        elif not record.get("level"):
            record["validation_status"] = "FAILED"
            record["validation_errors"] = ["Missing level"]
        else:
            record["validation_status"] = "PASSED"
        
        return record


# ==============================================================================
# Stage 16: Promotion (BigQuery write)
# ==============================================================================

class PromotionStage(Stage):
    """Stage 16: Promote to production BigQuery table."""

    STAGE_TYPE = "promotion"

    def write_output(self, records: list[dict[str, Any]]) -> int:
        """Write to BigQuery (or local file for testing)."""
        # Filter to passed records
        passed = [r for r in records if r.get("validation_status") == "PASSED"]
        
        output_path = Path(self.config.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to file (BigQuery integration can be added)
        with open(output_path, "w", encoding="utf-8") as f:
            for record in passed:
                f.write(json.dumps(record) + "\n")
        
        logger.info(
            f"Promoted {len(passed)}/{len(records)} entities to {output_path}"
        )
        
        return len(passed)


__all__ = [
    "L5MessagesStage",
    "L8ConversationsStage",
    "EnrichmentPlaceholderStage",
    "AggregationStage",
    "ValidationStage",
    "PromotionStage",
]
