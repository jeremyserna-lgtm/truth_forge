"""Seed - Project Seeding and Federation.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/seed/__init__.py
- Version: 2.0.0
- Date: 2026-01-26

This module enables:
- Seeding new projects from the truth_forge nucleus
- Federated communication between organisms

BIOLOGICAL METAPHOR:
- Seed = Cell division (mitosis)
- Federation = Colony communication
- Lineage = Genetic inheritance

Example:
    from truth_forge.organism.seed import ProjectSeeder, Lineage

    # Create a new organism
    seeder = ProjectSeeder()
    lineage = seeder.seed("my_project", parent="truth_forge")

    # Track lineage
    print(lineage.parent)
    print(lineage.generation)
"""

from __future__ import annotations

from truth_forge.organism.seed.federation import (
    CE_TYPE_GOVERNANCE,
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
from truth_forge.organism.seed.seeder import ProjectSeeder


__all__ = [
    # Core federation
    "FederationClient",
    "FederationHub",
    "Lineage",
    "Learning",
    "Update",
    # CloudEvents (CNCF standard)
    "CloudEvent",
    "CE_TYPE_HEARTBEAT",
    "CE_TYPE_TELEMETRY",
    "CE_TYPE_LEARNING",
    "CE_TYPE_GOVERNANCE",
    # Channels
    "PulseChannel",
    # Seeding
    "ProjectSeeder",
]
