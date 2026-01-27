"""Lifecycle - Organism State Management.

MOLT LINEAGE:
- Source: New implementation based on Truth_Engine patterns
- Version: 2.0.0
- Date: 2026-01-26

Manages the lifecycle states and transitions of an organism.

BIOLOGICAL METAPHOR:
- Lifecycle = Cell cycle
- States = Cell phases (G1, S, G2, M)
- Transitions = Checkpoints

LIFECYCLE STATES:
1. DORMANT - Not yet started
2. INITIALIZING - Starting up
3. ACTIVE - Running normally
4. DEGRADED - Partial functionality
5. RECOVERING - Coming back from error
6. TERMINATING - Shutting down
7. TERMINATED - Stopped

Example:
    from truth_forge.organism.lifecycle import (
        Lifecycle,
        LifecycleState,
    )

    lifecycle = Lifecycle("my_organism")
    lifecycle.start()  # DORMANT -> INITIALIZING -> ACTIVE

    if lifecycle.is_healthy:
        lifecycle.stop()  # ACTIVE -> TERMINATING -> TERMINATED
"""

from __future__ import annotations

from truth_forge.organism.lifecycle.manager import (
    Lifecycle,
    LifecycleEvent,
    LifecycleState,
    LifecycleTransition,
)


__all__ = [
    "Lifecycle",
    "LifecycleEvent",
    "LifecycleState",
    "LifecycleTransition",
]
