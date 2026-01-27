"""Tests for lifecycle manager module.

Tests the organism lifecycle state machine.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from truth_forge.organism.lifecycle.manager import (
    Lifecycle,
    LifecycleEvent,
    LifecycleState,
    LifecycleTransition,
)


class TestLifecycleState:
    """Tests for LifecycleState enum."""

    def test_state_values(self) -> None:
        """Test lifecycle state values."""
        assert LifecycleState.DORMANT.value == "dormant"
        assert LifecycleState.INITIALIZING.value == "initializing"
        assert LifecycleState.ACTIVE.value == "active"
        assert LifecycleState.DEGRADED.value == "degraded"
        assert LifecycleState.RECOVERING.value == "recovering"
        assert LifecycleState.TERMINATING.value == "terminating"
        assert LifecycleState.TERMINATED.value == "terminated"


class TestLifecycleTransition:
    """Tests for LifecycleTransition dataclass."""

    def test_default_values(self) -> None:
        """Test default transition values."""
        transition = LifecycleTransition(
            from_state=LifecycleState.DORMANT,
            to_state=LifecycleState.INITIALIZING,
        )
        assert transition.from_state == LifecycleState.DORMANT
        assert transition.to_state == LifecycleState.INITIALIZING
        assert transition.reason == ""

    def test_to_dict(self) -> None:
        """Test converting transition to dictionary."""
        transition = LifecycleTransition(
            from_state=LifecycleState.ACTIVE,
            to_state=LifecycleState.DEGRADED,
            reason="test reason",
        )
        data = transition.to_dict()

        assert data["from_state"] == "active"
        assert data["to_state"] == "degraded"
        assert data["reason"] == "test reason"
        assert "timestamp" in data


class TestLifecycleEvent:
    """Tests for LifecycleEvent dataclass."""

    def test_default_values(self) -> None:
        """Test default event values."""
        event = LifecycleEvent()
        assert event.event_id.startswith("evt_")
        assert event.state == LifecycleState.DORMANT

    def test_to_dict(self) -> None:
        """Test converting event to dictionary."""
        event = LifecycleEvent(
            event_type="started",
            state=LifecycleState.ACTIVE,
            data={"key": "value"},
        )
        data = event.to_dict()

        assert data["event_type"] == "started"
        assert data["state"] == "active"
        assert data["data"] == {"key": "value"}


class TestLifecycle:
    """Tests for Lifecycle class."""

    def test_init_creates_storage(self) -> None:
        """Test that init creates storage directory."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle" / "test_org"
            lifecycle = Lifecycle("test_org", storage_path=path)

            assert path.exists()
            assert lifecycle.organism_id == "test_org"

    def test_initial_state_is_dormant(self) -> None:
        """Test initial state is DORMANT."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)

            assert lifecycle.state == LifecycleState.DORMANT

    def test_start_transitions_to_active(self) -> None:
        """Test start transitions from DORMANT to ACTIVE."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)

            result = lifecycle.start()

            assert result is True
            assert lifecycle.state == LifecycleState.ACTIVE

    def test_start_fails_if_not_dormant(self) -> None:
        """Test start fails if not in DORMANT state."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)
            lifecycle.start()

            result = lifecycle.start()

            assert result is False

    def test_degrade_transitions_from_active(self) -> None:
        """Test degrade transitions from ACTIVE to DEGRADED."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)
            lifecycle.start()

            result = lifecycle.degrade(reason="High error rate")

            assert result is True
            assert lifecycle.state == LifecycleState.DEGRADED

    def test_degrade_fails_if_not_active(self) -> None:
        """Test degrade fails if not in ACTIVE state."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)

            result = lifecycle.degrade()

            assert result is False

    def test_recover_transitions_from_degraded(self) -> None:
        """Test recover transitions from DEGRADED to ACTIVE."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)
            lifecycle.start()
            lifecycle.degrade()

            result = lifecycle.recover()

            assert result is True
            assert lifecycle.state == LifecycleState.ACTIVE

    def test_recover_fails_if_not_degraded(self) -> None:
        """Test recover fails if not in DEGRADED state."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)
            lifecycle.start()

            result = lifecycle.recover()

            assert result is False

    def test_stop_transitions_to_terminated(self) -> None:
        """Test stop transitions to TERMINATED."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)
            lifecycle.start()

            result = lifecycle.stop()

            assert result is True
            assert lifecycle.state == LifecycleState.TERMINATED

    def test_stop_from_degraded(self) -> None:
        """Test stop works from DEGRADED state."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)
            lifecycle.start()
            lifecycle.degrade()

            result = lifecycle.stop()

            assert result is True
            assert lifecycle.state == LifecycleState.TERMINATED

    def test_stop_fails_if_dormant(self) -> None:
        """Test stop fails if in DORMANT state."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)

            result = lifecycle.stop()

            assert result is False

    def test_is_healthy_when_active(self) -> None:
        """Test is_healthy returns True when ACTIVE."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)
            lifecycle.start()

            assert lifecycle.is_healthy is True

    def test_is_healthy_when_degraded(self) -> None:
        """Test is_healthy returns False when DEGRADED."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)
            lifecycle.start()
            lifecycle.degrade()

            assert lifecycle.is_healthy is False

    def test_is_alive_when_not_terminated(self) -> None:
        """Test is_alive returns True when not TERMINATED."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)

            assert lifecycle.is_alive is True

    def test_is_alive_when_terminated(self) -> None:
        """Test is_alive returns False when TERMINATED."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)
            lifecycle.start()
            lifecycle.stop()

            assert lifecycle.is_alive is False

    def test_is_operational(self) -> None:
        """Test is_operational returns True when ACTIVE or DEGRADED."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)
            lifecycle.start()

            assert lifecycle.is_operational is True

            lifecycle.degrade()
            assert lifecycle.is_operational is True

    def test_get_history(self) -> None:
        """Test getting transition history."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)
            lifecycle.start()
            lifecycle.degrade()
            lifecycle.recover()

            history = lifecycle.get_history()

            # start: DORMANT->INIT->ACTIVE (2)
            # degrade: ACTIVE->DEGRADED (1)
            # recover: DEGRADED->RECOVERING->ACTIVE (2)
            assert len(history) == 5

    def test_get_events(self) -> None:
        """Test getting event history."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)
            lifecycle.start()

            events = lifecycle.get_events()

            # created, initializing, started
            assert len(events) >= 3

    def test_on_transition_handler(self) -> None:
        """Test transition handler is called."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)

            transitions_seen: list[LifecycleTransition] = []
            lifecycle.on_transition(lambda t: transitions_seen.append(t))

            lifecycle.start()

            assert len(transitions_seen) == 2  # DORMANT->INIT, INIT->ACTIVE

    def test_stop_persists_history(self) -> None:
        """Test stop persists history to file."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lifecycle"
            lifecycle = Lifecycle("test_org", storage_path=path)
            lifecycle.start()
            lifecycle.stop()

            history_file = path / "history.json"
            assert history_file.exists()
            content = history_file.read_text()
            assert "terminated" in content
