"""Integration - The Unified Mind.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/cognition/integration.py
- Version: 2.0.0
- Date: 2026-01-26

This module creates a unified view of cognitive state,
enabling holistic reasoning and decision-making.

BIOLOGICAL METAPHOR:
- IntegratedMind = Thalamus (relay station for all senses)
- UnifiedState = Conscious awareness
- LayerContribution = Individual sense inputs

THE PATTERN:
All Layers (HOLD1) -> Integration (AGENT) -> Unified State (HOLD2)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from truth_forge.core.paths import DATA_ROOT


logger = logging.getLogger(__name__)


class LayerType(Enum):
    """Cognitive layers that can contribute to state."""

    PERCEPTION = "perception"  # Sensory input
    MEMORY = "memory"  # Stored knowledge
    REASONING = "reasoning"  # Logical processing
    EMOTION = "emotion"  # Affective state
    ATTENTION = "attention"  # Focus
    PLANNING = "planning"  # Goal-directed behavior


@dataclass
class LayerContribution:
    """What each layer contributes to the unified state."""

    layer: LayerType
    status: str = "unknown"
    health: float = 1.0  # 0.0 to 1.0
    insights: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "layer": self.layer.value,
            "status": self.status,
            "health": self.health,
            "insights": self.insights,
            "concerns": self.concerns,
            "recommendations": self.recommendations,
            "metadata": self.metadata,
        }


@dataclass
class UnifiedState:
    """The complete, unified state of the mind."""

    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Overall health
    overall_health: float = 1.0
    overall_mood: str = "content"

    # Layer contributions
    layers: dict[str, LayerContribution] = field(default_factory=dict)

    # Aggregated insights
    active_concerns: list[str] = field(default_factory=list)
    active_thoughts: list[str] = field(default_factory=list)
    active_goals: list[str] = field(default_factory=list)
    active_mission: str | None = None

    # Wisdom and meaning
    wisdom_guidance: list[str] = field(default_factory=list)

    # Integration metrics
    integration_score: float = 1.0  # How well layers are working together
    coherence_score: float = 1.0  # How aligned the layers are

    # Operational state
    can_proceed: bool = True

    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            "+============================================================+",
            "|            UNIFIED MIND STATE                              |",
            "+============================================================+",
            f"|  Mood: {self.overall_mood.upper():15}",
            f"|  Health: {self.overall_health * 100:.0f}%",
            f"|  Integration: {self.integration_score * 100:.0f}%  |  "
            f"Coherence: {self.coherence_score * 100:.0f}%",
            f"|  Can Proceed: {'YES' if self.can_proceed else 'NO'}",
            "+------------------------------------------------------------+",
        ]

        if self.active_mission:
            lines.append(f"|  Mission: {self.active_mission[:45]}")

        if self.active_goals:
            lines.append("|  Goals:")
            for goal in self.active_goals[:3]:
                lines.append(f"|     - {goal[:50]}")

        if self.active_concerns:
            lines.append("|  ! Concerns:")
            for concern in self.active_concerns[:3]:
                lines.append(f"|     - {concern[:50]}")

        if self.wisdom_guidance:
            lines.append("|  * Wisdom:")
            for wisdom in self.wisdom_guidance[:2]:
                lines.append(f"|     - {wisdom[:50]}")

        if self.active_thoughts:
            lines.append("|  Thoughts:")
            for thought in self.active_thoughts[:2]:
                lines.append(f"|     - {thought[:50]}")

        lines.append("+------------------------------------------------------------+")
        lines.append("|  LAYER STATUS")

        for layer_name, layer in self.layers.items():
            health_bar = "#" * int(layer.health * 5) + "-" * (5 - int(layer.health * 5))
            lines.append(f"|     {layer_name.upper()[:12]:12} [{health_bar}] {layer.status[:15]}")

        lines.append("+============================================================+")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "overall_health": self.overall_health,
            "overall_mood": self.overall_mood,
            "layers": {k: v.to_dict() for k, v in self.layers.items()},
            "active_concerns": self.active_concerns,
            "active_thoughts": self.active_thoughts,
            "active_goals": self.active_goals,
            "active_mission": self.active_mission,
            "wisdom_guidance": self.wisdom_guidance,
            "integration_score": self.integration_score,
            "coherence_score": self.coherence_score,
            "can_proceed": self.can_proceed,
        }


class IntegratedMind:
    """The unified mind - integrates all cognitive layers.

    This mind:
    1. Gathers state from all cognitive layers
    2. Integrates into a unified state
    3. Provides coherent awareness

    Example:
        mind = get_mind()
        state = mind.unified_state()
        print(state.summary())

        # Deep reflection
        reflection = mind.reflect("What should I focus on?")
        print(reflection)
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        """Initialize the integrated mind."""
        if storage_path is None:
            storage_path = DATA_ROOT / "local" / "mind" / "states.jsonl"
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path = storage_path

        # Layer states
        self._layers: dict[str, LayerContribution] = {}

        # Current state
        self._current_state: UnifiedState | None = None

        # Mission and goals
        self._active_mission: str | None = None
        self._active_goals: list[str] = []

        # Concerns and thoughts
        self._active_concerns: list[str] = []
        self._active_thoughts: list[str] = []

        # Wisdom
        self._wisdom: list[str] = []

        logger.info("IntegratedMind initialized")

    def unified_state(self) -> UnifiedState:
        """Get the current unified state."""
        # Initialize layers if needed
        if not self._layers:
            for layer_type in LayerType:
                self._layers[layer_type.value] = LayerContribution(
                    layer=layer_type,
                    status="active",
                    health=1.0,
                )

        # Compute integration and coherence
        layer_healths = [layer.health for layer in self._layers.values()]
        avg_health = sum(layer_healths) / len(layer_healths) if layer_healths else 1.0

        # Integration = how many layers are active
        active_layers = sum(1 for contrib in self._layers.values() if contrib.status == "active")
        integration = active_layers / len(LayerType) if len(LayerType) > 0 else 1.0

        # Coherence = health variation (lower variation = higher coherence)
        if len(layer_healths) > 1:
            variance = sum((h - avg_health) ** 2 for h in layer_healths) / len(layer_healths)
            coherence = 1.0 - min(1.0, variance * 4)  # Scale variance to 0-1
        else:
            coherence = 1.0

        # Build unified state
        state = UnifiedState(
            overall_health=avg_health,
            overall_mood=self._compute_mood(avg_health),
            layers=self._layers.copy(),
            active_concerns=self._active_concerns.copy(),
            active_thoughts=self._active_thoughts.copy(),
            active_goals=self._active_goals.copy(),
            active_mission=self._active_mission,
            wisdom_guidance=self._wisdom.copy(),
            integration_score=integration,
            coherence_score=coherence,
            can_proceed=avg_health > 0.3 and len(self._active_concerns) < 5,
        )

        self._current_state = state
        self._record_state(state)

        return state

    def reflect(self, question: str | None = None) -> str:
        """Deep self-reflection.

        Args:
            question: Optional question to reflect on

        Returns:
            Reflection text
        """
        state = self.unified_state()

        lines = [
            f"Reflecting on: {question or 'current state'}",
            "",
            f"Current mood: {state.overall_mood}",
            f"Overall health: {state.overall_health * 100:.0f}%",
            f"Integration: {state.integration_score * 100:.0f}%",
            "",
        ]

        if state.active_mission:
            lines.append(f"My mission: {state.active_mission}")

        if state.active_concerns:
            lines.append("Current concerns:")
            for concern in state.active_concerns[:3]:
                lines.append(f"  - {concern}")

        if state.wisdom_guidance:
            lines.append("Wisdom guiding me:")
            for wisdom in state.wisdom_guidance[:2]:
                lines.append(f"  * {wisdom}")

        if question:
            # Simple reflection based on state
            if state.can_proceed:
                lines.append(f"\nRegarding '{question}': Conditions are favorable.")
            else:
                lines.append(f"\nRegarding '{question}': Caution is advised.")

        return "\n".join(lines)

    def set_mission(self, mission: str) -> None:
        """Set the active mission."""
        self._active_mission = mission
        logger.info("Mission set", extra={"mission": mission[:50]})

    def add_goal(self, goal: str) -> None:
        """Add an active goal."""
        if goal not in self._active_goals:
            self._active_goals.append(goal)

    def add_concern(self, concern: str) -> None:
        """Add an active concern."""
        if concern not in self._active_concerns:
            self._active_concerns.append(concern)

    def resolve_concern(self, concern: str) -> bool:
        """Resolve a concern."""
        if concern in self._active_concerns:
            self._active_concerns.remove(concern)
            return True
        return False

    def add_wisdom(self, wisdom: str) -> None:
        """Add wisdom guidance."""
        if wisdom not in self._wisdom:
            self._wisdom.append(wisdom)

    def add_thought(self, thought: str) -> None:
        """Add an active thought."""
        self._active_thoughts.append(thought)
        # Keep thoughts limited
        if len(self._active_thoughts) > 10:
            self._active_thoughts = self._active_thoughts[-10:]

    def update_layer(
        self,
        layer: LayerType,
        status: str | None = None,
        health: float | None = None,
    ) -> None:
        """Update a layer's state."""
        if layer.value not in self._layers:
            self._layers[layer.value] = LayerContribution(layer=layer)

        contribution = self._layers[layer.value]
        if status is not None:
            contribution.status = status
        if health is not None:
            contribution.health = max(0.0, min(1.0, health))

    def _compute_mood(self, health: float) -> str:
        """Compute mood based on health."""
        if health > 0.8:
            return "energized"
        if health > 0.6:
            return "content"
        if health > 0.4:
            return "neutral"
        if health > 0.2:
            return "weary"
        return "struggling"

    def _record_state(self, state: UnifiedState) -> None:
        """Record state to disk."""
        try:
            with open(self.storage_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(state.to_dict()) + "\n")
        except Exception as e:
            logger.debug("Failed to record state", extra={"error": str(e)})


# Singleton
_mind_instance: IntegratedMind | None = None


def get_mind() -> IntegratedMind:
    """Get or create the mind singleton."""
    global _mind_instance
    if _mind_instance is None:
        _mind_instance = IntegratedMind()
    return _mind_instance


def reflect(question: str | None = None) -> str:
    """Convenience function for reflection.

    Args:
        question: Optional question to reflect on

    Returns:
        Reflection text
    """
    mind = get_mind()
    return mind.reflect(question)


__all__ = [
    "IntegratedMind",
    "UnifiedState",
    "LayerContribution",
    "LayerType",
    "get_mind",
    "reflect",
]
