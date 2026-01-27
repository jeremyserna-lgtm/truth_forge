"""Tests for mind integration module.

Tests the unified mind and integrated state.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

import truth_forge.mind.integration as integration_module
from truth_forge.mind.integration import (
    IntegratedMind,
    LayerContribution,
    LayerType,
    UnifiedState,
    get_mind,
    reflect,
)


class TestLayerType:
    """Tests for LayerType enum."""

    def test_layer_values(self) -> None:
        """Test layer type values."""
        assert LayerType.PERCEPTION.value == "perception"
        assert LayerType.MEMORY.value == "memory"
        assert LayerType.REASONING.value == "reasoning"
        assert LayerType.EMOTION.value == "emotion"
        assert LayerType.ATTENTION.value == "attention"
        assert LayerType.PLANNING.value == "planning"


class TestLayerContribution:
    """Tests for LayerContribution dataclass."""

    def test_default_values(self) -> None:
        """Test default layer contribution values."""
        contrib = LayerContribution(layer=LayerType.PERCEPTION)

        assert contrib.layer == LayerType.PERCEPTION
        assert contrib.status == "unknown"
        assert contrib.health == 1.0
        assert contrib.insights == []
        assert contrib.concerns == []
        assert contrib.recommendations == []
        assert contrib.metadata == {}

    def test_custom_values(self) -> None:
        """Test custom layer contribution values."""
        contrib = LayerContribution(
            layer=LayerType.MEMORY,
            status="active",
            health=0.8,
            insights=["insight1"],
            concerns=["concern1"],
            recommendations=["rec1"],
            metadata={"key": "value"},
        )

        assert contrib.status == "active"
        assert contrib.health == 0.8
        assert len(contrib.insights) == 1

    def test_to_dict(self) -> None:
        """Test to_dict conversion."""
        contrib = LayerContribution(
            layer=LayerType.REASONING,
            status="processing",
            health=0.9,
        )

        result = contrib.to_dict()

        assert result["layer"] == "reasoning"
        assert result["status"] == "processing"
        assert result["health"] == 0.9


class TestUnifiedState:
    """Tests for UnifiedState dataclass."""

    def test_default_values(self) -> None:
        """Test default unified state values."""
        state = UnifiedState()

        assert state.overall_health == 1.0
        assert state.overall_mood == "content"
        assert state.layers == {}
        assert state.active_concerns == []
        assert state.active_thoughts == []
        assert state.active_goals == []
        assert state.active_mission is None
        assert state.wisdom_guidance == []
        assert state.integration_score == 1.0
        assert state.coherence_score == 1.0
        assert state.can_proceed is True

    def test_summary_basic(self) -> None:
        """Test summary with basic state."""
        state = UnifiedState()
        summary = state.summary()

        assert "UNIFIED MIND STATE" in summary
        assert "Mood:" in summary
        assert "Health:" in summary

    def test_summary_with_mission(self) -> None:
        """Test summary with mission."""
        state = UnifiedState(active_mission="Build something great")
        summary = state.summary()

        assert "Mission:" in summary
        assert "Build something" in summary

    def test_summary_with_goals(self) -> None:
        """Test summary with goals."""
        state = UnifiedState(active_goals=["Goal 1", "Goal 2"])
        summary = state.summary()

        assert "Goals:" in summary
        assert "Goal 1" in summary

    def test_summary_with_concerns(self) -> None:
        """Test summary with concerns."""
        state = UnifiedState(active_concerns=["Concern 1"])
        summary = state.summary()

        assert "Concerns:" in summary

    def test_summary_with_wisdom(self) -> None:
        """Test summary with wisdom."""
        state = UnifiedState(wisdom_guidance=["Be patient"])
        summary = state.summary()

        assert "Wisdom:" in summary

    def test_summary_with_thoughts(self) -> None:
        """Test summary with thoughts."""
        state = UnifiedState(active_thoughts=["Thinking about X"])
        summary = state.summary()

        assert "Thoughts:" in summary

    def test_summary_with_layers(self) -> None:
        """Test summary with layers."""
        layers = {
            "perception": LayerContribution(
                layer=LayerType.PERCEPTION, status="active", health=0.8
            )
        }
        state = UnifiedState(layers=layers)
        summary = state.summary()

        assert "LAYER STATUS" in summary
        assert "PERCEPTION" in summary

    def test_to_dict(self) -> None:
        """Test to_dict conversion."""
        state = UnifiedState(
            overall_health=0.9,
            overall_mood="happy",
            active_mission="Test mission",
        )

        result = state.to_dict()

        assert result["overall_health"] == 0.9
        assert result["overall_mood"] == "happy"
        assert result["active_mission"] == "Test mission"
        assert "timestamp" in result


class TestIntegratedMind:
    """Tests for IntegratedMind class."""

    def test_init_default_path(self) -> None:
        """Test initialization with default path."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)

            assert mind.storage_path == path
            assert mind._layers == {}
            assert mind._current_state is None

    def test_unified_state_initializes_layers(self) -> None:
        """Test unified_state initializes all layers."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)

            state = mind.unified_state()

            assert len(mind._layers) == len(LayerType)
            for layer_type in LayerType:
                assert layer_type.value in mind._layers

    def test_unified_state_computes_health(self) -> None:
        """Test unified_state computes health correctly."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)
            mind._layers = {
                "perception": LayerContribution(
                    layer=LayerType.PERCEPTION, status="active", health=0.8
                ),
                "memory": LayerContribution(
                    layer=LayerType.MEMORY, status="active", health=0.6
                ),
            }

            state = mind.unified_state()

            assert state.overall_health == 0.7  # (0.8 + 0.6) / 2

    def test_unified_state_can_proceed_false_low_health(self) -> None:
        """Test can_proceed is False when health is too low."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)
            mind._layers = {
                "perception": LayerContribution(
                    layer=LayerType.PERCEPTION, status="active", health=0.1
                ),
            }

            state = mind.unified_state()

            assert state.can_proceed is False

    def test_unified_state_can_proceed_false_many_concerns(self) -> None:
        """Test can_proceed is False with too many concerns."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)
            mind._active_concerns = ["c1", "c2", "c3", "c4", "c5"]

            state = mind.unified_state()

            assert state.can_proceed is False

    def test_set_mission(self) -> None:
        """Test set_mission."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)

            mind.set_mission("Build the future")

            assert mind._active_mission == "Build the future"

    def test_add_goal(self) -> None:
        """Test add_goal."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)

            mind.add_goal("Goal 1")
            mind.add_goal("Goal 2")
            mind.add_goal("Goal 1")  # Duplicate

            assert len(mind._active_goals) == 2

    def test_add_concern(self) -> None:
        """Test add_concern."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)

            mind.add_concern("Concern 1")
            mind.add_concern("Concern 1")  # Duplicate

            assert len(mind._active_concerns) == 1

    def test_resolve_concern(self) -> None:
        """Test resolve_concern."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)
            mind._active_concerns = ["Concern 1"]

            result = mind.resolve_concern("Concern 1")

            assert result is True
            assert len(mind._active_concerns) == 0

    def test_resolve_concern_not_found(self) -> None:
        """Test resolve_concern when concern not found."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)

            result = mind.resolve_concern("Not found")

            assert result is False

    def test_add_wisdom(self) -> None:
        """Test add_wisdom."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)

            mind.add_wisdom("Be patient")
            mind.add_wisdom("Be patient")  # Duplicate

            assert len(mind._wisdom) == 1

    def test_add_thought(self) -> None:
        """Test add_thought."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)

            for i in range(15):
                mind.add_thought(f"Thought {i}")

            assert len(mind._active_thoughts) == 10  # Max 10

    def test_update_layer_new(self) -> None:
        """Test update_layer creates new layer."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)

            mind.update_layer(LayerType.PERCEPTION, status="active", health=0.9)

            assert "perception" in mind._layers
            assert mind._layers["perception"].status == "active"
            assert mind._layers["perception"].health == 0.9

    def test_update_layer_existing(self) -> None:
        """Test update_layer updates existing layer."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)
            mind._layers["perception"] = LayerContribution(
                layer=LayerType.PERCEPTION, status="idle", health=1.0
            )

            mind.update_layer(LayerType.PERCEPTION, status="busy")

            assert mind._layers["perception"].status == "busy"
            assert mind._layers["perception"].health == 1.0  # Unchanged

    def test_update_layer_clamps_health(self) -> None:
        """Test update_layer clamps health to 0-1."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)

            mind.update_layer(LayerType.PERCEPTION, health=1.5)
            assert mind._layers["perception"].health == 1.0

            mind.update_layer(LayerType.PERCEPTION, health=-0.5)
            assert mind._layers["perception"].health == 0.0

    def test_compute_mood(self) -> None:
        """Test _compute_mood returns correct mood."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)

            assert mind._compute_mood(0.9) == "energized"
            assert mind._compute_mood(0.7) == "content"
            assert mind._compute_mood(0.5) == "neutral"
            assert mind._compute_mood(0.3) == "weary"
            assert mind._compute_mood(0.1) == "struggling"

    def test_reflect_basic(self) -> None:
        """Test reflect without question."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)

            result = mind.reflect()

            assert "Reflecting on:" in result
            assert "Current mood:" in result

    def test_reflect_with_question(self) -> None:
        """Test reflect with question."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)

            result = mind.reflect("What should I do?")

            assert "What should I do?" in result
            assert "Regarding" in result

    def test_reflect_with_mission(self) -> None:
        """Test reflect includes mission."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)
            mind._active_mission = "Build great things"

            result = mind.reflect()

            assert "My mission:" in result
            assert "Build great things" in result

    def test_reflect_with_concerns(self) -> None:
        """Test reflect includes concerns."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)
            mind._active_concerns = ["Concern 1"]

            result = mind.reflect()

            assert "Current concerns:" in result

    def test_reflect_with_wisdom(self) -> None:
        """Test reflect includes wisdom."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)
            mind._wisdom = ["Be patient"]

            result = mind.reflect()

            assert "Wisdom guiding me:" in result

    def test_reflect_caution_when_cannot_proceed(self) -> None:
        """Test reflect shows caution when cannot proceed."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)
            # Add enough concerns to prevent proceeding
            mind._active_concerns = ["c1", "c2", "c3", "c4", "c5"]

            result = mind.reflect("Should I continue?")

            assert "Caution is advised" in result


class TestGetMind:
    """Tests for get_mind function."""

    def setup_method(self) -> None:
        """Reset singleton before each test."""
        integration_module._mind_instance = None

    def teardown_method(self) -> None:
        """Clean up after each test."""
        integration_module._mind_instance = None

    def test_get_mind_returns_singleton(self) -> None:
        """Test get_mind returns singleton."""
        with patch.object(IntegratedMind, "__init__", lambda self, storage_path=None: None):
            mind1 = get_mind()
            mind2 = get_mind()

            assert mind1 is mind2


class TestReflectFunction:
    """Tests for reflect convenience function."""

    def setup_method(self) -> None:
        """Reset singleton before each test."""
        integration_module._mind_instance = None

    def teardown_method(self) -> None:
        """Clean up after each test."""
        integration_module._mind_instance = None

    def test_reflect_function(self) -> None:
        """Test reflect convenience function."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "states.jsonl"
            mind = IntegratedMind(storage_path=path)
            integration_module._mind_instance = mind

            result = reflect("Test question")

            assert "Test question" in result

