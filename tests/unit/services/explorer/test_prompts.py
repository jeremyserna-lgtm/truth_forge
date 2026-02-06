"""Tests for explorer prompts module."""

from __future__ import annotations

from truth_forge.services.explorer.prompts import (
    format_cognitive_classification_prompt,
    format_synthesis_prompt,
    format_tool_selection_prompt,
)


class TestFormatToolSelectionPrompt:
    """Test format_tool_selection_prompt function."""

    def test_formats_prompt(self) -> None:
        """Test prompt formatting."""
        prompt = format_tool_selection_prompt(
            context="Test context",
            available_tools=["tool1", "tool2"],
            focus_area="Test area",
            iteration=1,
            total_iterations=5,
            prior_findings="Previous findings",
            max_tools=3,
        )
        assert "Test context" in prompt
        assert "tool1" in prompt
        assert "tool2" in prompt
        assert "Test area" in prompt
        assert "2" in prompt  # iteration + 1
        assert "5" in prompt

    def test_includes_json_format(self) -> None:
        """Test prompt includes JSON format."""
        prompt = format_tool_selection_prompt(
            context="",
            available_tools="",
            focus_area=None,
            iteration=1,
            total_iterations=5,
            prior_findings="",
            max_tools=3,
        )
        assert "JSON" in prompt
        assert "tool" in prompt.lower()


class TestFormatCognitiveClassificationPrompt:
    """Test format_cognitive_classification_prompt function."""

    def test_formats_prompt(self) -> None:
        """Test prompt formatting."""
        prompt = format_cognitive_classification_prompt(
            tool_name="test_tool",
            tool_result="Test result",
        )
        assert "test_tool" in prompt
        assert "Test result" in prompt

    def test_includes_stage_5_guidance(self) -> None:
        """Test prompt includes Stage 5 guidance."""
        prompt = format_cognitive_classification_prompt(
            tool_name="test",
            tool_result="test",
        )
        assert "Stage 5" in prompt
        assert "fascinating" in prompt.lower() or "remarkable" in prompt.lower()


class TestFormatSynthesisPrompt:
    """Test format_synthesis_prompt function."""

    def test_formats_prompt(self) -> None:
        """Test prompt formatting."""
        prompt = format_synthesis_prompt(
            iterations=5,
            findings_count=10,
            high_count=3,
            focus_area="Test area",
            findings="Finding 1: Test\nFinding 2: Test",
            patterns="Pattern 1",
            resonance_score=0.8,
            stage_5_ratio=0.7,
            manifestation_ratio=0.6,
        )
        assert "Finding 1" in prompt
        assert "Test area" in prompt
        assert "5" in prompt

    def test_includes_manifestation_guidance(self) -> None:
        """Test prompt includes manifestation guidance."""
        prompt = format_synthesis_prompt(
            iterations=1,
            findings_count=1,
            high_count=0,
            focus_area=None,
            findings="test",
            patterns="",
            resonance_score=0.5,
            stage_5_ratio=0.5,
            manifestation_ratio=0.5,
        )
        assert "manifestation" in prompt.lower() or "describes" in prompt.lower()
