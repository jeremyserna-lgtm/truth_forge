"""Tests for relationships bond module.

Tests Memory, Preferences, and Journey classes.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import patch

import pytest

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


class TestInteractionType:
    """Tests for InteractionType enum."""

    def test_all_types_exist(self) -> None:
        """Test all expected interaction types exist."""
        assert InteractionType.WORK_SESSION.value == "work_session"
        assert InteractionType.TASK_COMPLETED.value == "task_completed"
        assert InteractionType.PROBLEM_SOLVED.value == "problem_solved"
        assert InteractionType.ACHIEVEMENT.value == "achievement"
        assert InteractionType.CONVERSATION.value == "conversation"


class TestInteraction:
    """Tests for Interaction dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        interaction = Interaction()
        assert interaction.interaction_id.startswith("int_")
        assert interaction.interaction_type == InteractionType.WORK_SESSION
        assert interaction.summary == ""
        assert interaction.details == {}
        assert interaction.patterns_involved == []
        assert interaction.duration_minutes is None
        assert interaction.outcome is None
        assert interaction.positive is True

    def test_to_dict(self) -> None:
        """Test to_dict produces correct structure."""
        interaction = Interaction(
            summary="Worked on tests",
            interaction_type=InteractionType.TASK_COMPLETED,
            details={"files": 3},
            patterns_involved=["HOLD:AGENT:HOLD"],
            duration_minutes=45.5,
            outcome="success",
            positive=True,
        )
        result = interaction.to_dict()
        assert result["summary"] == "Worked on tests"
        assert result["interaction_type"] == "task_completed"
        assert result["details"]["files"] == 3
        assert result["duration_minutes"] == 45.5
        assert result["outcome"] == "success"
        assert result["positive"] is True

    def test_from_dict(self) -> None:
        """Test from_dict creates correct Interaction."""
        data = {
            "interaction_id": "int_12345678",
            "timestamp": "2024-01-15T10:00:00+00:00",
            "interaction_type": "problem_solved",
            "summary": "Fixed bug",
            "details": {"bug_id": "123"},
            "patterns_involved": ["pattern1"],
            "duration_minutes": 30.0,
            "outcome": "success",
            "positive": True,
        }
        interaction = Interaction.from_dict(data)
        assert interaction.interaction_id == "int_12345678"
        assert interaction.interaction_type == InteractionType.PROBLEM_SOLVED
        assert interaction.summary == "Fixed bug"
        assert interaction.duration_minutes == 30.0

    def test_from_dict_minimal(self) -> None:
        """Test from_dict with minimal data."""
        data: dict[str, Any] = {}
        interaction = Interaction.from_dict(data)
        assert interaction.interaction_type == InteractionType.WORK_SESSION
        assert interaction.summary == ""
        assert interaction.positive is True


class TestMemory:
    """Tests for Memory class."""

    def test_init_creates_storage_path(self) -> None:
        """Test initialization creates storage path."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "memory" / "test.jsonl"
            memory = Memory(storage_path=storage)
            assert storage.parent.exists()

    def test_remember_creates_interaction(self) -> None:
        """Test remember creates and stores interaction."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "memory.jsonl"
            memory = Memory(storage_path=storage)

            interaction = memory.remember(
                summary="Test interaction",
                interaction_type=InteractionType.TASK_COMPLETED,
                details={"key": "value"},
                patterns=["pattern1"],
                positive=True,
            )

            assert interaction.summary == "Test interaction"
            assert interaction.interaction_type == InteractionType.TASK_COMPLETED
            assert len(memory._interactions) == 1

    def test_remember_with_session_duration(self) -> None:
        """Test remember calculates session duration."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "memory.jsonl"
            memory = Memory(storage_path=storage)

            memory.start_session()
            # Simulate some time passing
            memory._session_start = datetime.now(UTC) - timedelta(minutes=30)

            interaction = memory.remember(summary="Test")
            assert interaction.duration_minutes is not None
            assert interaction.duration_minutes >= 29  # Approximately 30 minutes

    def test_start_session(self) -> None:
        """Test start_session sets timestamp."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "memory.jsonl"
            memory = Memory(storage_path=storage)

            memory.start_session()
            assert memory._session_start is not None

    def test_recent_returns_last_n(self) -> None:
        """Test recent returns last N interactions."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "memory.jsonl"
            memory = Memory(storage_path=storage)

            for i in range(15):
                memory.remember(summary=f"Interaction {i}")

            recent = memory.recent(count=5)
            assert len(recent) == 5
            assert recent[-1].summary == "Interaction 14"

    def test_recall_narrative_empty(self) -> None:
        """Test recall_narrative with no history."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "memory.jsonl"
            memory = Memory(storage_path=storage)

            narrative = memory.recall_narrative()
            assert narrative == "No shared history yet."

    def test_recall_narrative_with_history(self) -> None:
        """Test recall_narrative with history."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "memory.jsonl"
            memory = Memory(storage_path=storage)

            memory.remember(summary="First thing")
            memory.remember(summary="Second thing")
            memory.remember(summary="Third thing")

            narrative = memory.recall_narrative()
            assert "Third thing" in narrative
            assert "Recent history" in narrative

    def test_load_persisted_memories(self) -> None:
        """Test loading memories from disk."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "memory.jsonl"

            # Create and save memory
            memory1 = Memory(storage_path=storage)
            memory1.remember(summary="Persisted interaction")

            # Load in new instance
            memory2 = Memory(storage_path=storage)
            assert len(memory2._interactions) == 1
            assert memory2._interactions[0].summary == "Persisted interaction"

    def test_load_handles_invalid_json(self) -> None:
        """Test loading handles invalid JSON gracefully."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "memory.jsonl"
            storage.write_text("invalid json\n")

            # Should not raise, just warn
            memory = Memory(storage_path=storage)
            assert len(memory._interactions) == 0


class TestPreferenceProfile:
    """Tests for PreferenceProfile dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        profile = PreferenceProfile()
        assert profile.important_patterns == []
        assert profile.values_reliability == 0.5
        assert profile.values_speed == 0.5
        assert profile.values_cost == 0.5
        assert profile.values_progress == 0.5
        assert profile.prefers_detail is False
        assert profile.prefers_brevity is True
        assert profile.typical_session_minutes == 30

    def test_to_dict(self) -> None:
        """Test to_dict produces correct structure."""
        profile = PreferenceProfile(
            important_patterns=["pattern1", "pattern2"],
            values_reliability=0.8,
        )
        result = profile.to_dict()
        assert result["important_patterns"] == ["pattern1", "pattern2"]
        assert result["values_reliability"] == 0.8

    def test_from_dict(self) -> None:
        """Test from_dict creates correct profile."""
        data = {
            "important_patterns": ["test", "build"],
            "values_reliability": 0.9,
            "values_cost": 0.7,
            "prefers_detail": True,
            "prefers_brevity": False,
            "typical_session_minutes": 60,
        }
        profile = PreferenceProfile.from_dict(data)
        assert profile.important_patterns == ["test", "build"]
        assert profile.values_reliability == 0.9
        assert profile.prefers_detail is True


class TestPreferences:
    """Tests for Preferences class."""

    def test_init_creates_storage_path(self) -> None:
        """Test initialization creates storage path."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "prefs" / "preferences.json"
            prefs = Preferences(storage_path=storage)
            assert storage.parent.exists()

    def test_observe_action(self) -> None:
        """Test observe_action tracks actions."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "preferences.json"
            prefs = Preferences(storage_path=storage)

            prefs.observe_action("ran_tests")
            prefs.observe_action("ran_tests")
            prefs.observe_action("checked_costs")

            assert len(prefs._actions) == 3

    def test_observe_action_updates_profile(self) -> None:
        """Test observe_action updates profile."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "preferences.json"
            prefs = Preferences(storage_path=storage)

            # Observe test-related actions
            for _ in range(10):
                prefs.observe_action("ran_tests")

            profile = prefs.profile()
            assert "ran_tests" in profile.important_patterns
            assert profile.values_reliability > 0.5

    def test_profile_returns_profile(self) -> None:
        """Test profile returns PreferenceProfile."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "preferences.json"
            prefs = Preferences(storage_path=storage)

            profile = prefs.profile()
            assert isinstance(profile, PreferenceProfile)

    def test_load_persisted_preferences(self) -> None:
        """Test loading preferences from disk."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "preferences.json"

            # Save preferences
            prefs1 = Preferences(storage_path=storage)
            prefs1.observe_action("test_action")
            prefs1.observe_action("test_action")

            # Load in new instance
            prefs2 = Preferences(storage_path=storage)
            assert len(prefs2._actions) == 2

    def test_load_handles_invalid_json(self) -> None:
        """Test loading handles invalid JSON gracefully."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "preferences.json"
            storage.write_text("invalid json")

            # Should not raise
            prefs = Preferences(storage_path=storage)
            assert len(prefs._actions) == 0


class TestChapter:
    """Tests for Chapter dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        chapter = Chapter()
        assert chapter.chapter_id.startswith("ch_")
        assert chapter.title == ""
        assert chapter.ended is None
        assert chapter.milestones == []
        assert chapter.summary == ""

    def test_is_active_when_not_ended(self) -> None:
        """Test is_active returns True when not ended."""
        chapter = Chapter(title="Active chapter")
        assert chapter.is_active is True

    def test_is_active_when_ended(self) -> None:
        """Test is_active returns False when ended."""
        chapter = Chapter(title="Ended chapter", ended=datetime.now(UTC))
        assert chapter.is_active is False

    def test_to_dict(self) -> None:
        """Test to_dict produces correct structure."""
        now = datetime.now(UTC)
        chapter = Chapter(
            chapter_id="ch_12345678",
            title="Test Chapter",
            started=now,
            ended=now,
            milestones=["m1", "m2"],
            summary="Done",
        )
        result = chapter.to_dict()
        assert result["chapter_id"] == "ch_12345678"
        assert result["title"] == "Test Chapter"
        assert result["ended"] is not None
        assert result["milestones"] == ["m1", "m2"]

    def test_to_dict_no_ended(self) -> None:
        """Test to_dict with no ended date."""
        chapter = Chapter(title="Active")
        result = chapter.to_dict()
        assert result["ended"] is None

    def test_from_dict(self) -> None:
        """Test from_dict creates correct Chapter."""
        data = {
            "chapter_id": "ch_test",
            "title": "Test",
            "started": "2024-01-15T10:00:00+00:00",
            "ended": "2024-01-16T10:00:00+00:00",
            "milestones": ["done"],
            "summary": "Complete",
        }
        chapter = Chapter.from_dict(data)
        assert chapter.chapter_id == "ch_test"
        assert chapter.title == "Test"
        assert chapter.ended is not None

    def test_from_dict_minimal(self) -> None:
        """Test from_dict with minimal data."""
        data: dict[str, Any] = {}
        chapter = Chapter.from_dict(data)
        assert chapter.title == ""
        assert chapter.ended is None


class TestJourney:
    """Tests for Journey class."""

    def test_init_creates_storage_path(self) -> None:
        """Test initialization creates storage path."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "journey" / "journey.jsonl"
            journey = Journey(storage_path=storage)
            assert storage.parent.exists()

    def test_start_chapter(self) -> None:
        """Test start_chapter creates new chapter."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "journey.jsonl"
            journey = Journey(storage_path=storage)

            chapter = journey.start_chapter("Test Chapter")
            assert chapter.title == "Test Chapter"
            assert chapter.is_active
            assert journey.current_chapter() == chapter

    def test_start_chapter_ends_previous(self) -> None:
        """Test start_chapter ends previous chapter."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "journey.jsonl"
            journey = Journey(storage_path=storage)

            chapter1 = journey.start_chapter("Chapter 1")
            chapter2 = journey.start_chapter("Chapter 2")

            assert not chapter1.is_active
            assert chapter2.is_active

    def test_add_milestone(self) -> None:
        """Test add_milestone adds to current chapter."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "journey.jsonl"
            journey = Journey(storage_path=storage)

            journey.start_chapter("Test")
            journey.add_milestone("First milestone")
            journey.add_milestone("Second milestone")

            chapter = journey.current_chapter()
            assert chapter is not None
            assert len(chapter.milestones) == 2

    def test_add_milestone_creates_chapter_if_none(self) -> None:
        """Test add_milestone creates chapter if none exists."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "journey.jsonl"
            journey = Journey(storage_path=storage)

            journey.add_milestone("Orphan milestone")

            chapter = journey.current_chapter()
            assert chapter is not None
            assert chapter.title == "Default Chapter"

    def test_end_chapter(self) -> None:
        """Test end_chapter ends current chapter."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "journey.jsonl"
            journey = Journey(storage_path=storage)

            journey.start_chapter("Test")
            ended = journey.end_chapter(summary="Done")

            assert ended is not None
            assert ended.ended is not None
            assert ended.summary == "Done"
            assert journey.current_chapter() is None

    def test_end_chapter_no_current(self) -> None:
        """Test end_chapter with no current chapter."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "journey.jsonl"
            journey = Journey(storage_path=storage)

            result = journey.end_chapter()
            assert result is None

    def test_chapters_returns_copy(self) -> None:
        """Test chapters returns copy of list."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "journey.jsonl"
            journey = Journey(storage_path=storage)

            journey.start_chapter("Test")
            chapters = journey.chapters()

            # Modifying returned list shouldn't affect internal list
            chapters.clear()
            assert len(journey._chapters) == 1

    def test_narrative_empty(self) -> None:
        """Test narrative with no chapters."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "journey.jsonl"
            journey = Journey(storage_path=storage)

            narrative = journey.narrative()
            assert narrative == "The journey begins..."

    def test_narrative_with_chapters(self) -> None:
        """Test narrative with chapters."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "journey.jsonl"
            journey = Journey(storage_path=storage)

            journey.start_chapter("Chapter 1")
            journey.add_milestone("Milestone 1")
            journey.end_chapter()
            journey.start_chapter("Chapter 2")

            narrative = journey.narrative()
            assert "Our journey so far" in narrative
            assert "Chapter 1" in narrative
            assert "Chapter 2" in narrative

    def test_load_persisted_journey(self) -> None:
        """Test loading journey from disk."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "journey.jsonl"

            # Save journey
            journey1 = Journey(storage_path=storage)
            journey1.start_chapter("Test Chapter")
            journey1.add_milestone("Test milestone")

            # Load in new instance
            journey2 = Journey(storage_path=storage)
            assert len(journey2._chapters) == 1
            assert journey2.current_chapter() is not None

    def test_load_handles_invalid_json(self) -> None:
        """Test loading handles invalid JSON gracefully."""
        with TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "journey.jsonl"
            storage.write_text("invalid json\n")

            # Should not raise
            journey = Journey(storage_path=storage)
            assert len(journey._chapters) == 0


class TestSingletons:
    """Tests for singleton functions."""

    def test_get_memory_returns_memory(self) -> None:
        """Test get_memory returns Memory instance."""
        import truth_forge.relationships.bond as bond_module

        # Reset singleton
        bond_module._memory_instance = None

        with patch.object(Memory, "__init__", return_value=None):
            result = get_memory()
            assert result is not None

    def test_get_memory_returns_same_instance(self) -> None:
        """Test get_memory returns same instance on multiple calls."""
        import truth_forge.relationships.bond as bond_module

        # Reset singleton
        bond_module._memory_instance = None

        with patch.object(Memory, "__init__", return_value=None):
            result1 = get_memory()
            result2 = get_memory()
            assert result1 is result2

    def test_get_preferences_returns_preferences(self) -> None:
        """Test get_preferences returns Preferences instance."""
        import truth_forge.relationships.bond as bond_module

        # Reset singleton
        bond_module._preferences_instance = None

        with patch.object(Preferences, "__init__", return_value=None):
            result = get_preferences()
            assert result is not None

    def test_get_preferences_returns_same_instance(self) -> None:
        """Test get_preferences returns same instance on multiple calls."""
        import truth_forge.relationships.bond as bond_module

        # Reset singleton
        bond_module._preferences_instance = None

        with patch.object(Preferences, "__init__", return_value=None):
            result1 = get_preferences()
            result2 = get_preferences()
            assert result1 is result2

    def test_get_journey_returns_journey(self) -> None:
        """Test get_journey returns Journey instance."""
        import truth_forge.relationships.bond as bond_module

        # Reset singleton
        bond_module._journey_instance = None

        with patch.object(Journey, "__init__", return_value=None):
            result = get_journey()
            assert result is not None

    def test_get_journey_returns_same_instance(self) -> None:
        """Test get_journey returns same instance on multiple calls."""
        import truth_forge.relationships.bond as bond_module

        # Reset singleton
        bond_module._journey_instance = None

        with patch.object(Journey, "__init__", return_value=None):
            result1 = get_journey()
            result2 = get_journey()
            assert result1 is result2
