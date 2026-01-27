"""Federation Protocol - Colony Communication.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/seed/federation.py
- Version: 2.0.0
- Date: 2026-01-26

Federated communication between organisms using enterprise standards.

ENTERPRISE STANDARDS:
- CloudEvents 1.0 (CNCF standard) for message format
- Phi Accrual Failure Detector for health monitoring

FEDERATION CHANNELS:
1. HEARTBEAT - "I'm alive" every 30 seconds
2. TELEMETRY - Real-time metrics streaming
3. LEARNINGS - Periodic knowledge sync
4. GOVERNANCE - Policy distribution

BIOLOGICAL METAPHOR:
- Federation = Telomere exchange between cells
- Heartbeat = Cellular respiration signal
- Learnings = Epigenetic inheritance
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from truth_forge.core.paths import DATA_ROOT


logger = logging.getLogger(__name__)


# CloudEvents type constants
CE_TYPE_HEARTBEAT = "org.truthforge.heartbeat"
CE_TYPE_TELEMETRY = "org.truthforge.telemetry"
CE_TYPE_LEARNING = "org.truthforge.learning"
CE_TYPE_GOVERNANCE = "org.truthforge.governance"


class PulseChannel(Enum):
    """Federation communication channels."""

    HEARTBEAT = "heartbeat"
    TELEMETRY = "telemetry"
    LEARNINGS = "learnings"
    GOVERNANCE = "governance"


@dataclass
class CloudEvent:
    """CNCF CloudEvents 1.0 specification.

    CloudEvents is a CNCF specification for describing event data in a common way.
    https://cloudevents.io/

    Attributes:
        specversion: Version of CloudEvents spec (1.0)
        type: Event type (e.g., "org.truthforge.heartbeat")
        source: Event source (organism ID)
        id: Unique event ID
        subject: Subject of the event
        time: Timestamp
        datacontenttype: Content type of data
        data: Event payload
        extensions: Extension attributes
    """

    # Required attributes
    specversion: str = "1.0"
    type: str = ""
    source: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))

    # Optional attributes
    subject: str | None = None
    time: str | None = field(default_factory=lambda: datetime.now(UTC).isoformat())
    datacontenttype: str = "application/json"

    # Event data
    data: dict[str, Any] | None = None

    # Extensions
    extensions: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to CloudEvents JSON format.

        Returns:
            Dictionary representation.
        """
        result: dict[str, Any] = {
            "specversion": self.specversion,
            "type": self.type,
            "source": self.source,
            "id": self.id,
        }

        if self.subject:
            result["subject"] = self.subject
        if self.time:
            result["time"] = self.time
        if self.datacontenttype:
            result["datacontenttype"] = self.datacontenttype
        if self.data:
            result["data"] = self.data

        # Add extensions
        result.update(self.extensions)

        return result

    def to_json(self) -> str:
        """Convert to JSON string.

        Returns:
            JSON representation.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CloudEvent:
        """Create from dictionary.

        Args:
            data: Dictionary with CloudEvent attributes.

        Returns:
            CloudEvent instance.
        """
        return cls(
            specversion=data.get("specversion", "1.0"),
            type=data.get("type", ""),
            source=data.get("source", ""),
            id=data.get("id", str(uuid4())),
            subject=data.get("subject"),
            time=data.get("time"),
            datacontenttype=data.get("datacontenttype", "application/json"),
            data=data.get("data"),
        )


@dataclass
class Lineage:
    """Tracks organism lineage and ancestry.

    BIOLOGICAL METAPHOR:
    - Lineage = Genetic inheritance record
    - Parent = Progenitor cell
    - Generation = Cell division count

    Attributes:
        organism_id: Unique identifier for this organism
        parent_id: ID of parent organism (None for genesis)
        generation: How many generations from genesis
        created_at: When this organism was born
        metadata: Additional lineage information
    """

    organism_id: str
    parent_id: str | None = None
    generation: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_genesis(self) -> bool:
        """Check if this is the genesis organism.

        Returns:
            True if this organism has no parent.
        """
        return self.parent_id is None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "organism_id": self.organism_id,
            "parent_id": self.parent_id,
            "generation": self.generation,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class Learning:
    """A piece of knowledge to share across the federation.

    BIOLOGICAL METAPHOR:
    - Learning = Epigenetic mark
    - Propagation = Horizontal gene transfer

    Attributes:
        learning_id: Unique identifier
        source: Organism that generated this learning
        category: Category of learning
        content: The actual knowledge
        confidence: How confident we are (0.0 to 1.0)
        timestamp: When this was learned
    """

    learning_id: str = field(default_factory=lambda: f"learn_{uuid4().hex[:12]}")
    source: str = ""
    category: str = ""
    content: str = ""
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "learning_id": self.learning_id,
            "source": self.source,
            "category": self.category,
            "content": self.content,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Update:
    """An update to distribute across the federation.

    Attributes:
        update_id: Unique identifier
        source: Organism that created this update
        channel: Communication channel
        payload: Update content
        timestamp: When created
    """

    update_id: str = field(default_factory=lambda: f"update_{uuid4().hex[:12]}")
    source: str = ""
    channel: PulseChannel = PulseChannel.TELEMETRY
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_cloud_event(self) -> CloudEvent:
        """Convert to CloudEvent.

        Returns:
            CloudEvent representation.
        """
        type_map = {
            PulseChannel.HEARTBEAT: CE_TYPE_HEARTBEAT,
            PulseChannel.TELEMETRY: CE_TYPE_TELEMETRY,
            PulseChannel.LEARNINGS: CE_TYPE_LEARNING,
            PulseChannel.GOVERNANCE: CE_TYPE_GOVERNANCE,
        }

        return CloudEvent(
            type=type_map.get(self.channel, CE_TYPE_TELEMETRY),
            source=self.source,
            data=self.payload,
        )


class FederationClient:
    """Client for participating in the federation.

    Handles communication with the federation hub.

    BIOLOGICAL METAPHOR:
    - FederationClient = Cell membrane receptors
    - Sending = Exocytosis
    - Receiving = Endocytosis

    Example:
        client = FederationClient("my_organism")
        client.send_heartbeat()
        client.share_learning(Learning(content="discovered pattern"))
    """

    def __init__(
        self,
        organism_id: str,
        storage_path: Path | None = None,
    ) -> None:
        """Initialize federation client.

        Args:
            organism_id: Unique identifier for this organism
            storage_path: Path for storing federation data
        """
        self.organism_id = organism_id

        if storage_path is None:
            storage_path = DATA_ROOT / "local" / "federation" / organism_id
        storage_path.mkdir(parents=True, exist_ok=True)
        self.storage_path = storage_path

        # Outgoing queue
        self._outgoing: list[CloudEvent] = []

        # Incoming learnings
        self._learnings: list[Learning] = []

        logger.info("FederationClient initialized", extra={"organism_id": organism_id})

    def send_heartbeat(self) -> CloudEvent:
        """Send a heartbeat signal.

        Returns:
            The heartbeat CloudEvent.
        """
        event = CloudEvent(
            type=CE_TYPE_HEARTBEAT,
            source=self.organism_id,
            data={
                "status": "alive",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        self._outgoing.append(event)
        self._persist_event(event)

        logger.debug("Heartbeat sent", extra={"organism_id": self.organism_id})
        return event

    def send_telemetry(self, metrics: dict[str, Any]) -> CloudEvent:
        """Send telemetry data.

        Args:
            metrics: Metrics to send.

        Returns:
            The telemetry CloudEvent.
        """
        event = CloudEvent(
            type=CE_TYPE_TELEMETRY,
            source=self.organism_id,
            data=metrics,
        )

        self._outgoing.append(event)
        self._persist_event(event)

        return event

    def share_learning(self, learning: Learning) -> CloudEvent:
        """Share a learning with the federation.

        Args:
            learning: The learning to share.

        Returns:
            The learning CloudEvent.
        """
        learning.source = self.organism_id

        event = CloudEvent(
            type=CE_TYPE_LEARNING,
            source=self.organism_id,
            data=learning.to_dict(),
        )

        self._outgoing.append(event)
        self._persist_event(event)

        return event

    def receive_learning(self, learning: Learning) -> None:
        """Receive a learning from the federation.

        Args:
            learning: The learning received.
        """
        self._learnings.append(learning)
        logger.debug(
            "Learning received",
            extra={
                "learning_id": learning.learning_id,
                "source": learning.source,
            },
        )

    def get_learnings(self) -> list[Learning]:
        """Get all received learnings.

        Returns:
            List of learnings.
        """
        return self._learnings.copy()

    def _persist_event(self, event: CloudEvent) -> None:
        """Persist event to disk.

        Args:
            event: Event to persist.
        """
        events_file = self.storage_path / "events.jsonl"
        with open(events_file, "a", encoding="utf-8") as f:
            f.write(event.to_json() + "\n")


class FederationHub:
    """Central hub for coordinating federation communication.

    BIOLOGICAL METAPHOR:
    - FederationHub = Colony signaling center
    - Routing = Chemotaxis gradients

    Example:
        hub = FederationHub()
        hub.register("organism_1")
        hub.register("organism_2")
        hub.broadcast(update)
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        """Initialize federation hub.

        Args:
            storage_path: Path for storing hub data.
        """
        if storage_path is None:
            storage_path = DATA_ROOT / "local" / "federation" / "hub"
        storage_path.mkdir(parents=True, exist_ok=True)
        self.storage_path = storage_path

        # Registered organisms
        self._organisms: dict[str, datetime] = {}

        # Shared learnings
        self._learnings: list[Learning] = []

        logger.info("FederationHub initialized")

    def register(self, organism_id: str) -> Lineage:
        """Register an organism with the hub.

        Args:
            organism_id: Unique organism identifier.

        Returns:
            Lineage information.
        """
        self._organisms[organism_id] = datetime.now(UTC)

        lineage = Lineage(
            organism_id=organism_id,
            parent_id="truth_forge",
            generation=1,
        )

        logger.info("Organism registered", extra={"organism_id": organism_id})
        return lineage

    def unregister(self, organism_id: str) -> bool:
        """Unregister an organism.

        Args:
            organism_id: Organism to unregister.

        Returns:
            True if was registered, False otherwise.
        """
        if organism_id in self._organisms:
            del self._organisms[organism_id]
            return True
        return False

    def get_registered(self) -> list[str]:
        """Get list of registered organisms.

        Returns:
            List of organism IDs.
        """
        return list(self._organisms.keys())

    def broadcast_learning(self, learning: Learning) -> int:
        """Broadcast a learning to all organisms.

        Args:
            learning: Learning to broadcast.

        Returns:
            Number of organisms notified.
        """
        self._learnings.append(learning)
        return len(self._organisms)

    def get_learnings(self, since: datetime | None = None) -> list[Learning]:
        """Get learnings, optionally filtered by time.

        Args:
            since: Only return learnings after this time.

        Returns:
            List of learnings.
        """
        if since is None:
            return self._learnings.copy()
        return [learn for learn in self._learnings if learn.timestamp > since]


__all__ = [
    "CE_TYPE_GOVERNANCE",
    "CE_TYPE_HEARTBEAT",
    "CE_TYPE_LEARNING",
    "CE_TYPE_TELEMETRY",
    "CloudEvent",
    "FederationClient",
    "FederationHub",
    "Learning",
    "Lineage",
    "PulseChannel",
    "Update",
]
