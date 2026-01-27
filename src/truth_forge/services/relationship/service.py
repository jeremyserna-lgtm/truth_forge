"""Relationship Service.

Manages the organism's understanding of its partnerships and interactions.
Embodies the principles of "Cognitive Orthogonality" and "Shared Context."
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from truth_forge.services.base import BaseService
from truth_forge.services.factory import register_service


@register_service()
class RelationshipService(BaseService):
    """
    A service for managing partnerships, trust levels, and interaction context.
    This service acts as the organism's social memory.
    """

    service_name = "relationship"

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Processes an interaction event to update a partnership's state."""
        partner_id = record.get("partner_id")
        interaction_type = record.get("interaction_type")
        metadata = record.get("metadata", {})

        if not all([partner_id, interaction_type]):
            raise ValueError("Interaction event requires 'partner_id' and 'interaction_type'.")

        # After validation, we know these are strings
        assert isinstance(partner_id, str), "partner_id must be a string"
        assert isinstance(interaction_type, str), "interaction_type must be a string"

        self.update_interaction(partner_id, interaction_type, metadata)
        return record

    def create_schema(self) -> str:
        """
        Creates the DuckDB schema for the relationship HOLD_2.
        The `data` column will store the full Partnership model as JSON.
        """
        return """
            CREATE TABLE IF NOT EXISTS relationship_records (
                id VARCHAR PRIMARY KEY, -- partner_id
                data JSON NOT NULL
            );
        """

    def get_partnership(self, partner_id: str) -> dict[str, Any] | None:
        """Retrieves the full context of a partnership from HOLD_2."""
        import duckdb

        db_path = self._paths["hold2"] / f"{self.service_name}.duckdb"
        if not db_path.exists():
            return None

        conn = duckdb.connect(str(db_path), read_only=True)
        try:
            result = conn.execute(
                f"SELECT data FROM {self.service_name}_records WHERE id = ?", [partner_id]
            ).fetchone()
            return json.loads(result[0]) if result else None
        finally:
            conn.close()

    def update_interaction(
        self, partner_id: str, interaction_type: str, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Logs a new interaction, creating or updating a partnership.
        This is the primary write method for this service.
        """
        with self._lock:
            partnership = self.get_partnership(partner_id)

            if partnership is None:
                # Create a new partnership record
                partnership = {
                    "partner_id": partner_id,
                    "trust_level": 0.5,  # Start with a neutral trust level
                    "interaction_count": 0,
                    "last_interaction": None,
                    "preferences": {},
                    "history": [],
                }

            # Update partnership metrics
            partnership["interaction_count"] += 1
            partnership["last_interaction"] = datetime.now(UTC).isoformat()

            # Add to history
            interaction_record = {
                "type": interaction_type,
                "timestamp": partnership["last_interaction"],
                "metadata": metadata or {},
            }
            partnership["history"].append(interaction_record)

            # Heuristic: Adjust trust based on interaction type (simple example)
            if interaction_type in ["positive_feedback", "successful_collaboration"]:
                partnership["trust_level"] = min(1.0, partnership["trust_level"] + 0.05)
            elif interaction_type in ["negative_feedback", "failed_collaboration"]:
                partnership["trust_level"] = max(0.0, partnership["trust_level"] - 0.1)

            # Persist the updated partnership back to HOLD_2
            self._write_to_hold2([partnership])
            self.logger.info(
                "partnership_updated", partner_id=partner_id, trust_level=partnership["trust_level"]
            )

            return partnership
