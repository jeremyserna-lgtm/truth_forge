"""Tests for federation module.

Tests the federation protocol for colony communication.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from truth_forge.organism.seed.federation import (
    CE_TYPE_HEARTBEAT,
    CE_TYPE_LEARNING,
    CE_TYPE_TELEMETRY,
    CloudEvent,
    FederationClient,
    FederationHub,
    Learning,
    Lineage,
    PulseChannel,
    Update,
)


class TestPulseChannel:
    """Tests for PulseChannel enum."""

    def test_channel_values(self) -> None:
        """Test pulse channel values."""
        assert PulseChannel.HEARTBEAT.value == "heartbeat"
        assert PulseChannel.TELEMETRY.value == "telemetry"
        assert PulseChannel.LEARNINGS.value == "learnings"
        assert PulseChannel.GOVERNANCE.value == "governance"


class TestCloudEvent:
    """Tests for CloudEvent dataclass."""

    def test_default_values(self) -> None:
        """Test default CloudEvent values."""
        event = CloudEvent()
        assert event.specversion == "1.0"
        assert event.datacontenttype == "application/json"
        assert event.id is not None
        assert event.time is not None

    def test_custom_values(self) -> None:
        """Test custom CloudEvent values."""
        event = CloudEvent(
            type="org.test.event",
            source="test_organism",
            subject="test_subject",
            data={"key": "value"},
        )
        assert event.type == "org.test.event"
        assert event.source == "test_organism"
        assert event.subject == "test_subject"
        assert event.data == {"key": "value"}

    def test_to_dict(self) -> None:
        """Test converting CloudEvent to dictionary."""
        event = CloudEvent(
            type="org.test.event",
            source="test_organism",
            data={"key": "value"},
        )
        data = event.to_dict()

        assert data["specversion"] == "1.0"
        assert data["type"] == "org.test.event"
        assert data["source"] == "test_organism"
        assert "id" in data

    def test_to_json(self) -> None:
        """Test converting CloudEvent to JSON."""
        event = CloudEvent(type="org.test.event", source="test")
        json_str = event.to_json()

        assert isinstance(json_str, str)
        assert "org.test.event" in json_str

    def test_from_dict(self) -> None:
        """Test creating CloudEvent from dictionary."""
        data = {
            "specversion": "1.0",
            "type": "org.test.event",
            "source": "test_organism",
            "id": "test_id",
            "data": {"key": "value"},
        }
        event = CloudEvent.from_dict(data)

        assert event.type == "org.test.event"
        assert event.source == "test_organism"
        assert event.id == "test_id"


class TestLineage:
    """Tests for Lineage dataclass."""

    def test_default_values(self) -> None:
        """Test default Lineage values."""
        lineage = Lineage(organism_id="test_org")
        assert lineage.organism_id == "test_org"
        assert lineage.parent_id is None
        assert lineage.generation == 0

    def test_is_genesis(self) -> None:
        """Test is_genesis property."""
        genesis = Lineage(organism_id="genesis")
        child = Lineage(organism_id="child", parent_id="genesis", generation=1)

        assert genesis.is_genesis is True
        assert child.is_genesis is False

    def test_to_dict(self) -> None:
        """Test converting Lineage to dictionary."""
        lineage = Lineage(
            organism_id="test_org",
            parent_id="parent_org",
            generation=2,
        )
        data = lineage.to_dict()

        assert data["organism_id"] == "test_org"
        assert data["parent_id"] == "parent_org"
        assert data["generation"] == 2


class TestLearning:
    """Tests for Learning dataclass."""

    def test_default_values(self) -> None:
        """Test default Learning values."""
        learning = Learning()
        assert learning.learning_id.startswith("learn_")
        assert learning.confidence == 1.0

    def test_custom_values(self) -> None:
        """Test custom Learning values."""
        learning = Learning(
            source="test_organism",
            category="pattern",
            content="discovered pattern",
            confidence=0.9,
        )
        assert learning.source == "test_organism"
        assert learning.category == "pattern"
        assert learning.content == "discovered pattern"
        assert learning.confidence == 0.9

    def test_to_dict(self) -> None:
        """Test converting Learning to dictionary."""
        learning = Learning(
            source="test",
            category="insight",
            content="test content",
        )
        data = learning.to_dict()

        assert data["source"] == "test"
        assert data["category"] == "insight"
        assert "timestamp" in data


class TestUpdate:
    """Tests for Update dataclass."""

    def test_default_values(self) -> None:
        """Test default Update values."""
        update = Update()
        assert update.update_id.startswith("update_")
        assert update.channel == PulseChannel.TELEMETRY

    def test_to_cloud_event(self) -> None:
        """Test converting Update to CloudEvent."""
        update = Update(
            source="test_organism",
            channel=PulseChannel.HEARTBEAT,
            payload={"status": "alive"},
        )
        event = update.to_cloud_event()

        assert event.type == CE_TYPE_HEARTBEAT
        assert event.source == "test_organism"
        assert event.data == {"status": "alive"}


class TestFederationClient:
    """Tests for FederationClient class."""

    def test_init_creates_storage(self) -> None:
        """Test that init creates storage directory."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "federation" / "test_org"
            client = FederationClient("test_org", storage_path=path)

            assert path.exists()
            assert client.organism_id == "test_org"

    def test_send_heartbeat(self) -> None:
        """Test sending heartbeat."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "federation" / "test_org"
            client = FederationClient("test_org", storage_path=path)

            event = client.send_heartbeat()

            assert event.type == CE_TYPE_HEARTBEAT
            assert event.source == "test_org"
            assert event.data["status"] == "alive"

    def test_send_telemetry(self) -> None:
        """Test sending telemetry."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "federation" / "test_org"
            client = FederationClient("test_org", storage_path=path)

            metrics = {"cpu": 50, "memory": 70}
            event = client.send_telemetry(metrics)

            assert event.type == CE_TYPE_TELEMETRY
            assert event.data == metrics

    def test_share_learning(self) -> None:
        """Test sharing learning."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "federation" / "test_org"
            client = FederationClient("test_org", storage_path=path)

            learning = Learning(
                category="pattern",
                content="test pattern",
            )
            event = client.share_learning(learning)

            assert event.type == CE_TYPE_LEARNING
            assert learning.source == "test_org"

    def test_receive_learning(self) -> None:
        """Test receiving learning."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "federation" / "test_org"
            client = FederationClient("test_org", storage_path=path)

            learning = Learning(
                source="other_org",
                category="insight",
                content="shared knowledge",
            )
            client.receive_learning(learning)

            learnings = client.get_learnings()
            assert len(learnings) == 1
            assert learnings[0].content == "shared knowledge"

    def test_events_persisted_to_file(self) -> None:
        """Test events are persisted to file."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "federation" / "test_org"
            client = FederationClient("test_org", storage_path=path)

            client.send_heartbeat()
            client.send_telemetry({"test": "data"})

            events_file = path / "events.jsonl"
            assert events_file.exists()
            content = events_file.read_text()
            assert CE_TYPE_HEARTBEAT in content
            assert CE_TYPE_TELEMETRY in content


class TestFederationHub:
    """Tests for FederationHub class."""

    def test_init_creates_storage(self) -> None:
        """Test that init creates storage directory."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "federation" / "hub"
            hub = FederationHub(storage_path=path)

            assert path.exists()

    def test_register_organism(self) -> None:
        """Test registering an organism."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "hub"
            hub = FederationHub(storage_path=path)

            lineage = hub.register("test_organism")

            assert lineage.organism_id == "test_organism"
            assert lineage.parent_id == "truth_forge"
            assert lineage.generation == 1

    def test_unregister_organism(self) -> None:
        """Test unregistering an organism."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "hub"
            hub = FederationHub(storage_path=path)

            hub.register("test_organism")
            result = hub.unregister("test_organism")

            assert result is True
            assert "test_organism" not in hub.get_registered()

    def test_unregister_nonexistent(self) -> None:
        """Test unregistering nonexistent organism."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "hub"
            hub = FederationHub(storage_path=path)

            result = hub.unregister("nonexistent")

            assert result is False

    def test_get_registered(self) -> None:
        """Test getting registered organisms."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "hub"
            hub = FederationHub(storage_path=path)

            hub.register("org1")
            hub.register("org2")

            registered = hub.get_registered()

            assert "org1" in registered
            assert "org2" in registered

    def test_broadcast_learning(self) -> None:
        """Test broadcasting learning."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "hub"
            hub = FederationHub(storage_path=path)

            hub.register("org1")
            hub.register("org2")

            learning = Learning(content="shared knowledge")
            count = hub.broadcast_learning(learning)

            assert count == 2

    def test_get_learnings(self) -> None:
        """Test getting learnings."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "hub"
            hub = FederationHub(storage_path=path)

            learning = Learning(content="test learning")
            hub.broadcast_learning(learning)

            learnings = hub.get_learnings()

            assert len(learnings) == 1
            assert learnings[0].content == "test learning"

    def test_get_learnings_filtered_by_time(self) -> None:
        """Test getting learnings filtered by time."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "hub"
            hub = FederationHub(storage_path=path)

            old_learning = Learning(content="old")
            hub.broadcast_learning(old_learning)

            # Get learnings from now (should be empty since all are before)
            since = datetime.now(UTC)
            learnings = hub.get_learnings(since=since)

            assert len(learnings) == 0
