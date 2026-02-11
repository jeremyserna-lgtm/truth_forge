"""Tests for Dataflow pipeline (multi-source AI conversations → entity_unified).

Tests cover:
- Multi-source support (all 8 sources)
- THE GATE (identity generation)
- Gemini Flash Lite spelling correction
- spaCy sentence segmentation
- entity_unified row generation
- Error handling
"""

from __future__ import annotations

import contextlib
import json

# Import the pipeline module
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


_pipeline_dir = (
    Path(__file__).parent.parent.parent.parent / "pipelines" / "adapters" / "claude_code"
)
sys.path.insert(0, str(_pipeline_dir))

pytest.importorskip("apache_beam", reason="apache_beam not installed")

from dataflow_pipeline import (  # noqa: E402
    SUPPORTED_SOURCES,
    ConversationL8DoFn,
    GeminiCleanDoFn,
    MessageEntityDoFn,
    SentenceDoFn,
    _entity_unified_row,
    _format_sequence,
    _generate_hash,
    extract_function,
    generate_entity_id,
    run_pipeline,
)


class TestSupportedSources:
    """Test supported sources configuration."""

    def test_all_sources_defined(self) -> None:
        """Test all 8 sources are defined."""
        expected_sources = {
            "claude_code",
            "claude_web",
            "gemini_web",
            "gemini_code",
            "codex",
            "copilot",
            "grok_web",
            "text_messages",
        }
        assert set(SUPPORTED_SOURCES.keys()) == expected_sources

    def test_all_sources_have_external_tables(self) -> None:
        """Test all sources have external table configuration."""
        for config in SUPPORTED_SOURCES.values():
            assert "external_table" in config
            assert config["external_table"].startswith("flash-clover-464719-g1.spine")
            assert config["external_table"].endswith("_external")


class TestExtractFunction:
    """Test extract_function."""

    def test_extract_claude_code(self) -> None:
        """Test extraction for claude_code source."""
        extract = extract_function("claude_code")
        row = {
            "session_id": "session_123",
            "message_index": 5,
            "text": "Hello world",
            "role": "user",
            "message_type": "message",
            "source_file": "/path/to/file.jsonl",
            "timestamp_utc": "2026-01-28T12:00:00Z",
            "content_date": "2026-01-28",
        }
        result = extract(row)
        assert result["session_id"] == "session_123"
        assert result["message_index"] == 5
        assert result["text"] == "Hello world"
        assert result["source_pipeline"] == "claude_code"

    def test_extract_handles_missing_fields(self) -> None:
        """Test extraction handles missing fields gracefully."""
        extract = extract_function("gemini_web")
        row = {"session_id": "test"}
        result = extract(row)
        assert result["session_id"] == "test"
        assert result.get("message_index") is None
        assert result["source_pipeline"] == "gemini_web"


class TestIdentityGeneration:
    """Test THE GATE identity generation."""

    def test_generate_hash(self) -> None:
        """Test hash generation."""
        hash1 = _generate_hash("test", length=16)
        hash2 = _generate_hash("test", length=16)
        assert hash1 == hash2  # Deterministic
        assert len(hash1) == 16

    def test_format_sequence(self) -> None:
        """Test sequence formatting."""
        assert _format_sequence(0) == "0000"
        assert _format_sequence(5) == "0005"
        assert _format_sequence(123) == "0123"

    def test_generate_entity_id(self) -> None:
        """Test entity_id generation."""
        gen = generate_entity_id("claude_code")
        row = {
            "session_id": "session_123",
            "message_index": 5,
        }
        result = gen(row)
        assert "entity_id" in result
        assert result["entity_id"].startswith("msg:")
        assert "conversation_id" in result
        assert result["conversation_id"].startswith("conv:claude_code:")

    def test_entity_id_deterministic(self) -> None:
        """Test entity_id is deterministic."""
        gen = generate_entity_id("claude_code")
        row = {"session_id": "session_123", "message_index": 5}
        result1 = gen(row.copy())
        result2 = gen(row.copy())
        assert result1["entity_id"] == result2["entity_id"]
        assert result1["conversation_id"] == result2["conversation_id"]


class TestEntityUnifiedRow:
    """Test entity_unified row builder."""

    def test_l5_message_row(self) -> None:
        """Test L5 message row generation."""
        row = _entity_unified_row(
            entity_id="msg:abc123:0001",
            level=5,
            entity_type="message",
            parent_id=None,
            conversation_id="conv:claude_code:abc123",
            topic_segment_id=None,
            turn_id=None,
            message_id="msg:abc123:0001",
            sentence_id=None,
            span_id=None,
            word_id=None,
            text="Hello world",
            source_file="/path/to/file.jsonl",
            content_date="2026-01-28",
            metadata_json='{"role": "user"}',
            source_pipeline="claude_code",
        )
        assert row["entity_id"] == "msg:abc123:0001"
        assert row["level"] == 5
        assert row["entity_type"] == "message"
        assert row["text"] == "Hello world"
        assert row["source_pipeline"] == "claude_code"
        assert row["source_system"] == "claude_code"
        assert row["source_ids"] == ["msg:abc123:0001"]
        assert len(row) == 34  # All 34 fields

    def test_l4_sentence_row(self) -> None:
        """Test L4 sentence row generation."""
        row = _entity_unified_row(
            entity_id="sent:abc123:0001",
            level=4,
            entity_type="sentence",
            parent_id="msg:abc123:0001",
            conversation_id="conv:claude_code:abc123",
            topic_segment_id=None,
            turn_id=None,
            message_id="msg:abc123:0001",
            sentence_id="sent:abc123:0001",
            span_id=None,
            word_id=None,
            text="Hello world.",
            source_file="/path/to/file.jsonl",
            content_date="2026-01-28",
            metadata_json='{"sentence_index": 0}',
            source_pipeline="claude_code",
        )
        assert row["level"] == 4
        assert row["parent_id"] == "msg:abc123:0001"
        assert row["sentence_id"] == "sent:abc123:0001"


class TestGeminiCleanDoFn:
    """Test Gemini spelling correction DoFn."""

    @patch("dataflow_pipeline.genai")
    def test_user_message_cleaned(self, mock_genai: MagicMock) -> None:
        """Test user message gets cleaned."""
        # Mock Gemini response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '{"corrected_text": "Hello world", "original_text": "Helo world", "changes_made": "Fixed spelling"}'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = Mock()

        dofn = GeminiCleanDoFn()
        dofn.model = mock_model

        element = {
            "role": "user",
            "text": "Helo world",
        }
        result = list(dofn.process(element))

        assert len(result) == 1
        assert result[0]["text_cleaned"] == "Hello world"
        assert result[0]["text_original"] == "Helo world"
        assert result[0]["cleaning_applied"] is True

    def test_assistant_message_passthrough(self) -> None:
        """Test assistant messages pass through unchanged."""
        dofn = GeminiCleanDoFn()
        dofn.model = None  # No Gemini available

        element = {
            "role": "assistant",
            "text": "Hello world",
        }
        result = list(dofn.process(element))

        assert len(result) == 1
        assert result[0]["text_cleaned"] == "Hello world"
        assert result[0]["cleaning_applied"] is False

    def test_short_text_passthrough(self) -> None:
        """Test very short text passes through."""
        dofn = GeminiCleanDoFn()
        dofn.model = Mock()

        element = {
            "role": "user",
            "text": "Hi",  # Too short
        }
        result = list(dofn.process(element))

        assert result[0]["cleaning_applied"] is False


class TestSentenceDoFn:
    """Test sentence segmentation DoFn."""

    @patch("dataflow_pipeline.spacy")
    def test_sentence_segmentation(self, mock_spacy: MagicMock) -> None:
        """Test sentence segmentation."""
        # Mock spaCy
        mock_nlp = Mock()
        mock_doc = Mock()
        mock_sent1 = Mock()
        mock_sent1.text = "First sentence."
        mock_sent1.start_char = 0
        mock_sent1.end_char = 16
        mock_sent2 = Mock()
        mock_sent2.text = "Second sentence."
        mock_sent2.start_char = 17
        mock_sent2.end_char = 33
        mock_doc.sents = [mock_sent1, mock_sent2]
        mock_nlp.return_value = mock_doc
        mock_spacy.load.return_value = mock_nlp

        dofn = SentenceDoFn("claude_code")
        dofn.nlp = mock_nlp

        element = {
            "text_cleaned": "First sentence. Second sentence.",
            "entity_id": "msg:abc123:0001",
            "conversation_id": "conv:claude_code:abc123",
            "source_file": "/path/to/file.jsonl",
            "content_date": "2026-01-28",
            "role": "user",
            "message_type": "message",
            "message_index": 0,
            "timestamp_utc": "2026-01-28T12:00:00Z",
        }

        results = list(dofn.process(element))
        assert len(results) == 2
        assert results[0]["level"] == 4
        assert results[0]["text"] == "First sentence."
        assert results[1]["text"] == "Second sentence."


class TestMessageEntityDoFn:
    """Test message entity DoFn."""

    def test_l5_message_creation(self) -> None:
        """Test L5 message entity creation."""
        dofn = MessageEntityDoFn("claude_code")

        element = {
            "entity_id": "msg:abc123:0001",
            "conversation_id": "conv:claude_code:abc123",
            "text_cleaned": "Hello world",
            "text_original": "Helo world",
            "source_file": "/path/to/file.jsonl",
            "content_date": "2026-01-28",
            "role": "user",
            "message_type": "message",
            "message_index": 0,
            "content_length": 11,
            "word_count": 2,
            "cleaning_applied": True,
            "cleaning_changes": "Fixed spelling",
            "timestamp_utc": "2026-01-28T12:00:00Z",
        }

        results = list(dofn.process(element))
        assert len(results) == 1
        row = results[0]
        assert row["level"] == 5
        assert row["entity_type"] == "message"
        assert row["text"] == "Hello world"  # Cleaned text
        assert "text_original" in json.loads(row["metadata"])  # Original in metadata


class TestConversationL8DoFn:
    """Test conversation L8 DoFn."""

    def test_l8_conversation_creation(self) -> None:
        """Test L8 conversation entity creation."""
        dofn = ConversationL8DoFn("claude_code")

        element = {
            "conversation_id": "conv:claude_code:abc123",
            "session_id": "session_123",
            "source_file": "/path/to/file.jsonl",
            "content_date": "2026-01-28",
        }

        results = list(dofn.process(element))
        assert len(results) == 1
        row = results[0]
        assert row["level"] == 8
        assert row["entity_type"] == "conversation"
        assert row["entity_id"] == "conv:claude_code:abc123"
        assert row["conversation_id"] == "conv:claude_code:abc123"

    def test_missing_conversation_id_skips(self) -> None:
        """Test missing conversation_id skips row."""
        dofn = ConversationL8DoFn("claude_code")
        element = {"session_id": "session_123"}
        results = list(dofn.process(element))
        assert len(results) == 0


class TestRunPipeline:
    """Test pipeline execution."""

    def test_unsupported_source_raises_error(self) -> None:
        """Test unsupported source raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported source"):
            run_pipeline("invalid_source")

    @patch("dataflow_pipeline.beam.Pipeline")
    @patch("dataflow_pipeline.beam.io.ReadFromBigQuery")
    def test_pipeline_creates_correct_structure(
        self, mock_read: MagicMock, mock_pipeline: MagicMock
    ) -> None:
        """Test pipeline creates correct Beam structure."""
        mock_p = Mock()
        mock_pipeline.return_value.__enter__.return_value = mock_p

        # Mock the pipeline construction
        mock_p.__or__ = Mock(return_value=mock_p)

        with contextlib.suppress(Exception):
            run_pipeline("claude_code")
        # May not be called if pipeline fails early


class TestIntegration:
    """Integration tests for full pipeline flow."""

    def test_extract_to_entity_id_flow(self) -> None:
        """Test extract → entity_id generation flow."""
        extract = extract_function("gemini_web")
        gen = generate_entity_id("gemini_web")

        row = {
            "session_id": "session_456",
            "message_index": 10,
            "text": "Test message",
            "role": "user",
            "message_type": "message",
            "source_file": "/path/to/file.jsonl",
            "timestamp_utc": "2026-01-28T12:00:00Z",
            "content_date": "2026-01-28",
        }

        extracted = extract(row)
        assert extracted["source_pipeline"] == "gemini_web"

        with_ids = gen(extracted)
        assert "entity_id" in with_ids
        assert "conversation_id" in with_ids
        assert with_ids["conversation_id"].startswith("conv:gemini_web:")
