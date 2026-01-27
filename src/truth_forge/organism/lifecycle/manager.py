"""Lifecycle Manager - Organism State Machine.

MOLT LINEAGE:
- Source: New implementation based on Truth_Engine patterns
- Version: 2.0.0
- Date: 2026-01-26

Manages organism state transitions and lifecycle events.

BIOLOGICAL METAPHOR:
- Lifecycle = Cell cycle regulation
- States = Cell cycle phases
- Transitions = Checkpoint controls
- Events = Signaling events

STATE DIAGRAM:
    DORMANT
       |
       v (start)
    INITIALIZING
       |
       v (ready)
    ACTIVE <----+
       |        |
       v        | (recover)
    DEGRADED ---+
       |
       v (shutdown)
    TERMINATING
       |
       v (done)
    TERMINATED
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar
from uuid import uuid4

from truth_forge.core.paths import DATA_ROOT


logger = logging.getLogger(__name__)


class LifecycleState(Enum):
    """Organism lifecycle states."""

    DORMANT = "dormant"  # Not yet started
    INITIALIZING = "initializing"  # Starting up
    ACTIVE = "active"  # Running normally
    DEGRADED = "degraded"  # Partial functionality
    RECOVERING = "recovering"  # Coming back from error
    TERMINATING = "terminating"  # Shutting down
    TERMINATED = "terminated"  # Stopped


@dataclass
class LifecycleTransition:
    """Record of a state transition.

    Attributes:
        from_state: Previous state
        to_state: New state
        timestamp: When transition occurred
        reason: Why transition happened
        metadata: Additional information
    """

    from_state: LifecycleState
    to_state: LifecycleState
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
            "metadata": self.metadata,
        }


@dataclass
class LifecycleEvent:
    """An event in the organism's lifecycle.

    Attributes:
        event_id: Unique identifier
        event_type: Type of event
        state: Current state when event occurred
        timestamp: When event occurred
        data: Event data
    """

    event_id: str = field(default_factory=lambda: f"evt_{uuid4().hex[:12]}")
    event_type: str = ""
    state: LifecycleState = LifecycleState.DORMANT
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "state": self.state.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
        }


class Lifecycle:
    """Manages organism lifecycle state machine.

    The lifecycle manager handles:
    1. State tracking
    2. Valid transitions
    3. Event emission
    4. History recording

    BIOLOGICAL METAPHOR:
    - Lifecycle = Cell cycle control system
    - start() = G0 -> G1 transition
    - degrade() = DNA damage response
    - recover() = Repair completion
    - stop() = Apoptosis initiation

    Example:
        lifecycle = Lifecycle("my_organism")

        # Start the organism
        lifecycle.start()
        assert lifecycle.state == LifecycleState.ACTIVE

        # Register event handlers
        lifecycle.on_transition(lambda t: print(f"Transition: {t}"))

        # Handle degradation
        lifecycle.degrade(reason="High error rate")
        lifecycle.recover()

        # Shutdown
        lifecycle.stop()
    """

    # Valid state transitions
    VALID_TRANSITIONS: ClassVar[dict[LifecycleState, list[LifecycleState]]] = {
        LifecycleState.DORMANT: [LifecycleState.INITIALIZING],
        LifecycleState.INITIALIZING: [LifecycleState.ACTIVE, LifecycleState.TERMINATED],
        LifecycleState.ACTIVE: [LifecycleState.DEGRADED, LifecycleState.TERMINATING],
        LifecycleState.DEGRADED: [LifecycleState.RECOVERING, LifecycleState.TERMINATING],
        LifecycleState.RECOVERING: [LifecycleState.ACTIVE, LifecycleState.DEGRADED],
        LifecycleState.TERMINATING: [LifecycleState.TERMINATED],
        LifecycleState.TERMINATED: [],  # No transitions from terminated
    }

    def __init__(
        self,
        organism_id: str,
        storage_path: Path | None = None,
    ) -> None:
        """Initialize lifecycle manager.

        Args:
            organism_id: Unique identifier for this organism.
            storage_path: Path for storing lifecycle data.
        """
        self.organism_id = organism_id
        self._state = LifecycleState.DORMANT
        self._transitions: list[LifecycleTransition] = []
        self._events: list[LifecycleEvent] = []
        self._handlers: list[Callable[[LifecycleTransition], None]] = []

        # Storage
        if storage_path is None:
            storage_path = DATA_ROOT / "local" / "lifecycle" / organism_id
        storage_path.mkdir(parents=True, exist_ok=True)
        self._storage_path = storage_path

        # Record initial event
        self._record_event("created", {"organism_id": organism_id})

        logger.info("Lifecycle initialized", extra={"organism_id": organism_id})

    @property
    def state(self) -> LifecycleState:
        """Get current state.

        Returns:
            Current lifecycle state.
        """
        return self._state

    @property
    def is_healthy(self) -> bool:
        """Check if organism is in a healthy state.

        Returns:
            True if ACTIVE.
        """
        return self._state == LifecycleState.ACTIVE

    @property
    def is_alive(self) -> bool:
        """Check if organism is alive (not terminated).

        Returns:
            True if not TERMINATED.
        """
        return self._state != LifecycleState.TERMINATED

    @property
    def is_operational(self) -> bool:
        """Check if organism can perform operations.

        Returns:
            True if ACTIVE or DEGRADED.
        """
        return self._state in (LifecycleState.ACTIVE, LifecycleState.DEGRADED)

    def start(self) -> bool:
        """Start the organism.

        Transitions: DORMANT -> INITIALIZING -> ACTIVE

        Returns:
            True if successfully started.
        """
        if self._state != LifecycleState.DORMANT:
            logger.warning(
                "Cannot start: not dormant",
                extra={"organism_id": self.organism_id, "state": self._state.value},
            )
            return False

        # Initialize
        self._transition(LifecycleState.INITIALIZING, "Starting organism")
        self._record_event("initializing", {})

        # Assume initialization succeeds
        self._transition(LifecycleState.ACTIVE, "Initialization complete")
        self._record_event("started", {})

        return True

    def degrade(self, reason: str = "Unknown") -> bool:
        """Mark organism as degraded.

        Transitions: ACTIVE -> DEGRADED

        Args:
            reason: Why degradation occurred.

        Returns:
            True if transition succeeded.
        """
        if self._state != LifecycleState.ACTIVE:
            return False

        self._transition(LifecycleState.DEGRADED, reason)
        self._record_event("degraded", {"reason": reason})
        return True

    def recover(self) -> bool:
        """Attempt to recover from degraded state.

        Transitions: DEGRADED -> RECOVERING -> ACTIVE

        Returns:
            True if recovery succeeded.
        """
        if self._state != LifecycleState.DEGRADED:
            return False

        self._transition(LifecycleState.RECOVERING, "Recovery initiated")
        self._record_event("recovering", {})

        # Assume recovery succeeds
        self._transition(LifecycleState.ACTIVE, "Recovery complete")
        self._record_event("recovered", {})

        return True

    def stop(self, reason: str = "Shutdown requested") -> bool:
        """Stop the organism.

        Transitions: ACTIVE/DEGRADED -> TERMINATING -> TERMINATED

        Args:
            reason: Why shutdown is happening.

        Returns:
            True if shutdown initiated.
        """
        if self._state not in (LifecycleState.ACTIVE, LifecycleState.DEGRADED):
            return False

        self._transition(LifecycleState.TERMINATING, reason)
        self._record_event("terminating", {"reason": reason})

        # Complete termination
        self._transition(LifecycleState.TERMINATED, "Shutdown complete")
        self._record_event("terminated", {})

        # Persist final state
        self._persist_history()

        return True

    def on_transition(self, handler: Callable[[LifecycleTransition], None]) -> None:
        """Register a transition handler.

        Args:
            handler: Callback for transitions.
        """
        self._handlers.append(handler)

    def get_history(self) -> list[LifecycleTransition]:
        """Get transition history.

        Returns:
            List of transitions.
        """
        return self._transitions.copy()

    def get_events(self) -> list[LifecycleEvent]:
        """Get event history.

        Returns:
            List of events.
        """
        return self._events.copy()

    def _transition(self, to_state: LifecycleState, reason: str) -> bool:
        """Perform a state transition.

        Args:
            to_state: Target state.
            reason: Why transitioning.

        Returns:
            True if transition was valid.
        """
        # Validate transition
        valid_targets = self.VALID_TRANSITIONS.get(self._state, [])
        if to_state not in valid_targets:
            logger.error(
                "Invalid transition",
                extra={
                    "from": self._state.value,
                    "to": to_state.value,
                    "valid": [s.value for s in valid_targets],
                },
            )
            return False

        # Record transition
        transition = LifecycleTransition(
            from_state=self._state,
            to_state=to_state,
            reason=reason,
        )
        self._transitions.append(transition)

        # Update state
        old_state = self._state
        self._state = to_state

        logger.info(
            "State transition",
            extra={
                "organism_id": self.organism_id,
                "from": old_state.value,
                "to": to_state.value,
                "reason": reason,
            },
        )

        # Notify handlers
        for handler in self._handlers:
            try:
                handler(transition)
            except Exception as e:
                logger.error("Transition handler error", extra={"error": str(e)})

        return True

    def _record_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Record a lifecycle event.

        Args:
            event_type: Type of event.
            data: Event data.
        """
        event = LifecycleEvent(
            event_type=event_type,
            state=self._state,
            data=data,
        )
        self._events.append(event)

    def _persist_history(self) -> None:
        """Persist history to disk."""
        history_file = self._storage_path / "history.json"
        history = {
            "organism_id": self.organism_id,
            "final_state": self._state.value,
            "transitions": [t.to_dict() for t in self._transitions],
            "events": [e.to_dict() for e in self._events],
        }
        history_file.write_text(json.dumps(history, indent=2))


__all__ = [
    "Lifecycle",
    "LifecycleEvent",
    "LifecycleState",
    "LifecycleTransition",
]
