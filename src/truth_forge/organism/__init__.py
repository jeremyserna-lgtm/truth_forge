"""Organism - Living System Management.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/seed/ and organism patterns
- Version: 2.0.0
- Date: 2026-01-26

This module manages organisms - living software systems that can:
- Be seeded from a parent (truth_forge)
- Communicate via federation
- Manage their own lifecycle
- Track lineage and inheritance

BIOLOGICAL METAPHOR:
- Organism = Living cell
- Seed = Cell division (mitosis)
- Federation = Colony communication
- Lifecycle = Cell cycle
- Lineage = Genetic inheritance

SUBMODULES:
- seed/ - Project seeding and federation
- lifecycle/ - State management

Example:
    from truth_forge.organism import (
        ProjectSeeder,
        Lifecycle,
        LifecycleState,
    )

    # Seed a new organism
    seeder = ProjectSeeder()
    lineage = seeder.seed(SeedConfig(name="my_project"))

    # Manage lifecycle
    lifecycle = Lifecycle("my_project")
    lifecycle.start()
    assert lifecycle.is_healthy
"""

from __future__ import annotations

from truth_forge.organism.lifecycle import (
    Lifecycle,
    LifecycleEvent,
    LifecycleState,
    LifecycleTransition,
)
from truth_forge.organism.seed import (
    CE_TYPE_GOVERNANCE,
    CE_TYPE_HEARTBEAT,
    CE_TYPE_LEARNING,
    CE_TYPE_TELEMETRY,
    CloudEvent,
    FederationClient,
    FederationHub,
    Learning,
    Lineage,
    ProjectSeeder,
    PulseChannel,
    Update,
)
from truth_forge.organism.seed.seeder import SeedConfig


__all__ = [
    # Lifecycle
    "Lifecycle",
    "LifecycleState",
    "LifecycleTransition",
    "LifecycleEvent",
    # Seeding
    "ProjectSeeder",
    "SeedConfig",
    # Federation
    "FederationClient",
    "FederationHub",
    "Lineage",
    "Learning",
    "Update",
    "CloudEvent",
    "PulseChannel",
    # CloudEvents constants
    "CE_TYPE_HEARTBEAT",
    "CE_TYPE_TELEMETRY",
    "CE_TYPE_LEARNING",
    "CE_TYPE_GOVERNANCE",
]
