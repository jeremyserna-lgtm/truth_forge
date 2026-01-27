"""Bond - Memory, Preferences, and Journey.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/bond/memory.py,preferences.py,journey.py
- Version: 2.0.0
- Date: 2026-01-26

This module implements the relational aspects of the system:
- Memory: Remembers meaningful interactions
- Preferences: Learns what matters to the operator
- Journey: Tracks the shared narrative over time
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from truth_forge.core.paths import DATA_ROOT


logger = logging.getLogger(__name__)


# =============================================================================
# MEMORY
# =============================================================================


class InteractionType(Enum):
    """Types of remembered interactions."""

    WORK_SESSION = "work_session"  # User worked with the system
    TASK_COMPLETED = "task_completed"  # User completed a task
    PROBLEM_SOLVED = "problem_solved"  # User fixed an issue
    ACHIEVEMENT = "achievement"  # Something notable accomplished
    CONVERSATION = "conversation"  # Meaningful dialogue


@dataclass
class Interaction:
    """A remembered interaction with the operator."""

    interaction_id: str = field(default_factory=lambda: f"int_{uuid4().hex[:8]}")
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # What happened
    interaction_type: InteractionType = InteractionType.WORK_SESSION
    summary: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    # Context
    patterns_involved: list[str] = field(default_factory=list)
    duration_minutes: float | None = None
    outcome: str | None = None  # success, partial, abandoned

    # Emotional valence
    positive: bool = True  # Was this a good experience?

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "interaction_id": self.interaction_id,
            "timestamp": self.timestamp.isoformat(),
            "interaction_type": self.interaction_type.value,
            "summary": self.summary,
            "details": self.details,
            "patterns_involved": self.patterns_involved,
            "duration_minutes": self.duration_minutes,
            "outcome": self.outcome,
            "positive": self.positive,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Interaction:
        """Create from dictionary."""
        timestamp_str = data.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now(UTC)
        return cls(
            interaction_id=data.get("interaction_id", f"int_{uuid4().hex[:8]}"),
            timestamp=timestamp,
            interaction_type=InteractionType(data.get("interaction_type", "work_session")),
            summary=data.get("summary", ""),
            details=data.get("details", {}),
            patterns_involved=data.get("patterns_involved", []),
            duration_minutes=data.get("duration_minutes"),
            outcome=data.get("outcome"),
            positive=data.get("positive", True),
        )


class Memory:
    """The system's long-term memory of shared experiences.

    Remembers meaningful interactions to build relationship.

    Example:
        memory = Memory()

        # Remember an interaction
        memory.remember(
            summary="Worked on message processing pipeline",
            interaction_type=InteractionType.WORK_SESSION,
        )

        # Recall recent work
        recent = memory.recent()
        for interaction in recent:
            print(interaction.summary)

        # Get narrative recall
        print(memory.recall_narrative())
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        """Initialize memory.

        Args:
            storage_path: Where to persist memories
        """
        self.storage_path = storage_path or (DATA_ROOT / "local" / "relationships" / "memory.jsonl")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self._interactions: list[Interaction] = []
        self._session_start: datetime | None = None

        self._load()
        logger.info("Memory initialized")

    def _load(self) -> None:
        """Load memories from disk."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self._interactions.append(Interaction.from_dict(data))
        except Exception as e:
            logger.warning("Failed to load memories", extra={"error": str(e)})

    def _save(self, interaction: Interaction) -> None:
        """Save an interaction to disk."""
        try:
            with open(self.storage_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(interaction.to_dict()) + "\n")
        except Exception as e:
            logger.error("Failed to save memory", extra={"error": str(e)})

    def start_session(self) -> None:
        """Mark the start of a work session."""
        self._session_start = datetime.now(UTC)
        logger.debug("Session started")

    def remember(
        self,
        summary: str,
        interaction_type: InteractionType = InteractionType.WORK_SESSION,
        details: dict[str, Any] | None = None,
        patterns: list[str] | None = None,
        positive: bool = True,
    ) -> Interaction:
        """Remember an interaction.

        Args:
            summary: What happened
            interaction_type: Type of interaction
            details: Additional details
            patterns: Patterns involved
            positive: Was this positive?

        Returns:
            The created Interaction
        """
        # Calculate duration if we have a session start
        duration = None
        if self._session_start:
            elapsed = datetime.now(UTC) - self._session_start
            duration = elapsed.total_seconds() / 60
            self._session_start = None  # Reset session

        interaction = Interaction(
            interaction_type=interaction_type,
            summary=summary,
            details=details or {},
            patterns_involved=patterns or [],
            duration_minutes=duration,
            positive=positive,
        )

        self._interactions.append(interaction)
        self._save(interaction)

        logger.info("Remembered interaction", extra={"summary": summary[:50]})
        return interaction

    def recent(self, count: int = 10) -> list[Interaction]:
        """Get recent interactions."""
        return self._interactions[-count:]

    def recall_narrative(self) -> str:
        """Generate a narrative recall of recent history."""
        if not self._interactions:
            return "No shared history yet."

        recent = self._interactions[-3:]
        last = recent[-1]

        # Time since last interaction
        elapsed = datetime.now(UTC) - last.timestamp
        if elapsed < timedelta(hours=1):
            time_desc = "just now"
        elif elapsed < timedelta(days=1):
            hours = int(elapsed.total_seconds() / 3600)
            time_desc = f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            days = elapsed.days
            time_desc = f"{days} day{'s' if days > 1 else ''} ago"

        lines = [
            f"Last interaction: {time_desc}",
            f"  {last.summary}",
        ]

        if len(recent) > 1:
            lines.append("Recent history:")
            for interaction in recent[:-1]:
                lines.append(f"  - {interaction.summary}")

        return "\n".join(lines)


# =============================================================================
# PREFERENCES
# =============================================================================


@dataclass
class PreferenceProfile:
    """The operator's inferred preference profile."""

    # Patterns that matter (by usage frequency)
    important_patterns: list[str] = field(default_factory=list)

    # What they care about (0-1 scale)
    values_reliability: float = 0.5
    values_speed: float = 0.5
    values_cost: float = 0.5
    values_progress: float = 0.5

    # Communication preferences
    prefers_detail: bool = False
    prefers_brevity: bool = True

    # Patterns of behavior
    typical_session_minutes: float = 30

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "important_patterns": self.important_patterns,
            "values_reliability": self.values_reliability,
            "values_speed": self.values_speed,
            "values_cost": self.values_cost,
            "values_progress": self.values_progress,
            "prefers_detail": self.prefers_detail,
            "prefers_brevity": self.prefers_brevity,
            "typical_session_minutes": self.typical_session_minutes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PreferenceProfile:
        """Create from dictionary."""
        return cls(
            important_patterns=data.get("important_patterns", []),
            values_reliability=data.get("values_reliability", 0.5),
            values_speed=data.get("values_speed", 0.5),
            values_cost=data.get("values_cost", 0.5),
            values_progress=data.get("values_progress", 0.5),
            prefers_detail=data.get("prefers_detail", False),
            prefers_brevity=data.get("prefers_brevity", True),
            typical_session_minutes=data.get("typical_session_minutes", 30),
        )


class Preferences:
    """Learn what matters to the operator.

    Observes actions and infers preferences.

    Example:
        preferences = Preferences()

        # Observe actions
        preferences.observe_action("ran_tests")
        preferences.observe_action("ran_tests")
        preferences.observe_action("checked_costs")

        # Get profile
        profile = preferences.profile()
        print(f"Important patterns: {profile.important_patterns}")
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        """Initialize preferences.

        Args:
            storage_path: Where to persist preferences
        """
        self.storage_path = storage_path or (
            DATA_ROOT / "local" / "relationships" / "preferences.json"
        )
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self._actions: list[str] = []
        self._profile = PreferenceProfile()

        self._load()
        logger.info("Preferences initialized")

    def _load(self) -> None:
        """Load preferences from disk."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, encoding="utf-8") as f:
                data = json.load(f)
                self._actions = data.get("actions", [])
                if "profile" in data:
                    self._profile = PreferenceProfile.from_dict(data["profile"])
        except Exception as e:
            logger.warning("Failed to load preferences", extra={"error": str(e)})

    def _save(self) -> None:
        """Save preferences to disk."""
        try:
            data = {
                "actions": self._actions[-1000:],  # Keep last 1000 actions
                "profile": self._profile.to_dict(),
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("Failed to save preferences", extra={"error": str(e)})

    def observe_action(self, action: str) -> None:
        """Observe an action and update preferences.

        Args:
            action: The action observed
        """
        self._actions.append(action)
        self._update_profile()
        self._save()

    def _update_profile(self) -> None:
        """Update the preference profile based on observed actions."""
        if not self._actions:
            return

        # Count action frequencies
        counts = Counter(self._actions)
        total = len(self._actions)

        # Update important patterns
        self._profile.important_patterns = [action for action, count in counts.most_common(5)]

        # Infer values based on action patterns
        test_actions = sum(1 for a in self._actions if "test" in a.lower())
        self._profile.values_reliability = min(1.0, test_actions / max(1, total) * 5)

        cost_actions = sum(1 for a in self._actions if "cost" in a.lower())
        self._profile.values_cost = min(1.0, cost_actions / max(1, total) * 5)

    def profile(self) -> PreferenceProfile:
        """Get the current preference profile."""
        return self._profile


# =============================================================================
# JOURNEY
# =============================================================================


@dataclass
class Chapter:
    """A chapter in the shared journey."""

    chapter_id: str = field(default_factory=lambda: f"ch_{uuid4().hex[:8]}")
    title: str = ""
    started: datetime = field(default_factory=lambda: datetime.now(UTC))
    ended: datetime | None = None
    milestones: list[str] = field(default_factory=list)
    summary: str = ""

    @property
    def is_active(self) -> bool:
        """Check if chapter is still active."""
        return self.ended is None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chapter_id": self.chapter_id,
            "title": self.title,
            "started": self.started.isoformat(),
            "ended": self.ended.isoformat() if self.ended else None,
            "milestones": self.milestones,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Chapter:
        """Create from dictionary."""
        started_str = data.get("started")
        ended_str = data.get("ended")
        return cls(
            chapter_id=data.get("chapter_id", f"ch_{uuid4().hex[:8]}"),
            title=data.get("title", ""),
            started=datetime.fromisoformat(started_str) if started_str else datetime.now(UTC),
            ended=datetime.fromisoformat(ended_str) if ended_str else None,
            milestones=data.get("milestones", []),
            summary=data.get("summary", ""),
        )


class Journey:
    """The shared journey over time.

    Tracks chapters and milestones in the relationship.

    Example:
        journey = Journey()

        # Start a new chapter
        journey.start_chapter("Building the API")

        # Add milestones
        journey.add_milestone("Completed authentication")
        journey.add_milestone("Added rate limiting")

        # End chapter
        journey.end_chapter(summary="Successfully launched API")

        # Get narrative
        print(journey.narrative())
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        """Initialize journey.

        Args:
            storage_path: Where to persist journey
        """
        self.storage_path = storage_path or (
            DATA_ROOT / "local" / "relationships" / "journey.jsonl"
        )
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self._chapters: list[Chapter] = []
        self._current_chapter: Chapter | None = None

        self._load()
        logger.info("Journey initialized")

    def _load(self) -> None:
        """Load journey from disk."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        chapter = Chapter.from_dict(data)
                        self._chapters.append(chapter)
                        if chapter.is_active:
                            self._current_chapter = chapter
        except Exception as e:
            logger.warning("Failed to load journey", extra={"error": str(e)})

    def _save(self, chapter: Chapter) -> None:
        """Save a chapter to disk."""
        try:
            with open(self.storage_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(chapter.to_dict()) + "\n")
        except Exception as e:
            logger.error("Failed to save chapter", extra={"error": str(e)})

    def start_chapter(self, title: str) -> Chapter:
        """Start a new chapter.

        Args:
            title: Title of the chapter

        Returns:
            The new Chapter
        """
        # End current chapter if any
        if self._current_chapter:
            self.end_chapter()

        chapter = Chapter(title=title)
        self._chapters.append(chapter)
        self._current_chapter = chapter
        self._save(chapter)

        logger.info("Started new chapter", extra={"title": title})
        return chapter

    def add_milestone(self, milestone: str) -> None:
        """Add a milestone to the current chapter.

        Args:
            milestone: Description of the milestone
        """
        if not self._current_chapter:
            self.start_chapter("Default Chapter")

        if self._current_chapter:
            self._current_chapter.milestones.append(milestone)
            logger.info("Added milestone", extra={"milestone": milestone})

    def end_chapter(self, summary: str = "") -> Chapter | None:
        """End the current chapter.

        Args:
            summary: Summary of the chapter

        Returns:
            The ended Chapter, or None if no chapter was active
        """
        if not self._current_chapter:
            return None

        self._current_chapter.ended = datetime.now(UTC)
        self._current_chapter.summary = summary

        ended = self._current_chapter
        self._current_chapter = None

        logger.info("Ended chapter", extra={"title": ended.title})
        return ended

    def current_chapter(self) -> Chapter | None:
        """Get the current active chapter."""
        return self._current_chapter

    def chapters(self) -> list[Chapter]:
        """Get all chapters."""
        return self._chapters.copy()

    def narrative(self) -> str:
        """Generate a narrative of the journey."""
        if not self._chapters:
            return "The journey begins..."

        lines = ["Our journey so far:"]

        for chapter in self._chapters[-5:]:  # Last 5 chapters
            status = "(active)" if chapter.is_active else "(completed)"
            lines.append(f"  {chapter.title} {status}")
            if chapter.milestones:
                for milestone in chapter.milestones[:3]:
                    lines.append(f"    - {milestone}")

        return "\n".join(lines)


# =============================================================================
# SINGLETONS
# =============================================================================

_memory_instance: Memory | None = None
_preferences_instance: Preferences | None = None
_journey_instance: Journey | None = None


def get_memory() -> Memory:
    """Get or create the memory singleton."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = Memory()
    return _memory_instance


def get_preferences() -> Preferences:
    """Get or create the preferences singleton."""
    global _preferences_instance
    if _preferences_instance is None:
        _preferences_instance = Preferences()
    return _preferences_instance


def get_journey() -> Journey:
    """Get or create the journey singleton."""
    global _journey_instance
    if _journey_instance is None:
        _journey_instance = Journey()
    return _journey_instance


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
