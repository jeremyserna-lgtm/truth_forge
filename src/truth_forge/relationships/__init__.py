"""Relationships - The Bond Between System and Operator.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/bond/__init__.py
- Version: 2.0.0
- Date: 2026-01-26

This module creates genuine relationship - the system remembers you,
knows what you care about, and builds a shared history together.

BIOLOGICAL METAPHOR:
- Bond = Social attachment, pair bonding
- Memory = Hippocampal long-term storage
- Preferences = Learned associations
- Journey = Shared narrative identity

The difference between a tool and a partner:
- Tool: Does what you ask, forgets everything
- Partner: Remembers your journey, knows what matters to you

Usage:
    from truth_forge.relationships import (
        get_memory,
        get_preferences,
        get_journey,
    )

    # Remember an interaction
    memory = get_memory()
    memory.remember(summary="Fixed the sync pattern")

    # Learn preferences
    preferences = get_preferences()
    preferences.observe_action("ran_tests")

    # Track journey
    journey = get_journey()
    journey.start_chapter("Implementation Phase")
"""

from __future__ import annotations

from truth_forge.relationships.bond import (
    Chapter,
    Interaction,
    InteractionType,
    Journey,
    Memory,
    PreferenceProfile,
    Preferences,
    get_journey,
    get_memory,
    get_preferences,
)


__all__ = [
    # Memory
    "Memory",
    "Interaction",
    "InteractionType",
    "get_memory",
    # Preferences
    "Preferences",
    "PreferenceProfile",
    "get_preferences",
    # Journey
    "Journey",
    "Chapter",
    "get_journey",
]
