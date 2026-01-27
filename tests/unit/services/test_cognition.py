"""Tests for cognition service module.

Tests the cognitive processing service.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from truth_forge.services.cognition.service import CognitionService


class TestCognitionService:
    """Tests for CognitionService class."""

    def test_service_name(self) -> None:
        """Test service name is set."""
        assert CognitionService.service_name == "cognition"

    @patch.object(CognitionService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.cognition.service.get_service")
    def test_on_startup(self, mock_get_service: MagicMock, mock_logger: MagicMock) -> None:
        """Test on_startup initializes dependencies."""
        mock_knowledge = MagicMock()
        mock_relationship = MagicMock()
        mock_mediator = MagicMock()

        def get_service_side_effect(name: str) -> MagicMock:
            if name == "knowledge":
                return mock_knowledge
            elif name == "relationship":
                return mock_relationship
            elif name == "mediator":
                return mock_mediator
            return MagicMock()

        mock_get_service.side_effect = get_service_side_effect

        service = CognitionService.__new__(CognitionService)
        service.on_startup()

        assert service.knowledge_service is mock_knowledge
        assert service.relationship_service is mock_relationship
        assert service.mediator is mock_mediator

    @patch.object(CognitionService, "logger", new_callable=lambda: MagicMock())
    def test_process_unknown_goal(self, mock_logger: MagicMock) -> None:
        """Test process handles unknown goal."""
        service = CognitionService.__new__(CognitionService)
        service._write_error_signal = MagicMock()

        record = {"goal": "unknown_goal", "params": {}}
        result = service.process(record)

        assert result == record
        mock_logger.warning.assert_called()
        service._write_error_signal.assert_called_once()

    @patch.object(CognitionService, "logger", new_callable=lambda: MagicMock())
    def test_process_summarize_and_save(self, mock_logger: MagicMock) -> None:
        """Test process with summarize_topic_and_save goal."""
        service = CognitionService.__new__(CognitionService)
        service._write_error_signal = MagicMock()

        mock_knowledge = MagicMock()
        mock_knowledge.query.return_value = [{"content": "test content"}]
        mock_knowledge.call_llm.return_value = {"text": "Summary text"}

        mock_relationship = MagicMock()
        mock_mediator = MagicMock()

        service.knowledge_service = mock_knowledge
        service.relationship_service = mock_relationship
        service.mediator = mock_mediator

        record = {
            "goal": "summarize_topic_and_save",
            "params": {"topic": "test topic", "output_path": "test.md"},
        }
        result = service.process(record)

        assert result == record
        mock_knowledge.query.assert_called_once_with(query="test topic", limit=10)
        mock_knowledge.call_llm.assert_called_once()
        mock_mediator.publish.assert_called_once()

    @patch.object(CognitionService, "logger", new_callable=lambda: MagicMock())
    def test_process_summarize_with_partner(self, mock_logger: MagicMock) -> None:
        """Test process with partner_id for context."""
        service = CognitionService.__new__(CognitionService)
        service._write_error_signal = MagicMock()

        mock_knowledge = MagicMock()
        mock_knowledge.query.return_value = [{"content": "test content"}]
        mock_knowledge.call_llm.return_value = {"text": "Summary text"}

        mock_relationship = MagicMock()
        mock_relationship.get_partnership.return_value = {"trust_level": 0.9}

        mock_mediator = MagicMock()

        service.knowledge_service = mock_knowledge
        service.relationship_service = mock_relationship
        service.mediator = mock_mediator

        record = {
            "goal": "summarize_topic_and_save",
            "params": {
                "topic": "test topic",
                "output_path": "test.md",
                "partner_id": "partner_123",
            },
        }
        result = service.process(record)

        assert result == record
        mock_relationship.get_partnership.assert_called_once_with("partner_123")
        mock_relationship.update_interaction.assert_called_once()

    @patch.object(CognitionService, "logger", new_callable=lambda: MagicMock())
    def test_handle_summarize_missing_topic(self, mock_logger: MagicMock) -> None:
        """Test _handle_summarize_and_save with missing topic."""
        service = CognitionService.__new__(CognitionService)
        service._write_error_signal = MagicMock()
        service.knowledge_service = MagicMock()
        service.relationship_service = MagicMock()
        service.mediator = MagicMock()

        record = {
            "goal": "summarize_topic_and_save",
            "params": {"output_path": "test.md"},  # Missing topic
        }
        result = service.process(record)

        assert result == record
        service._write_error_signal.assert_called_once()

    @patch.object(CognitionService, "logger", new_callable=lambda: MagicMock())
    def test_handle_summarize_missing_output_path(self, mock_logger: MagicMock) -> None:
        """Test _handle_summarize_and_save with missing output_path."""
        service = CognitionService.__new__(CognitionService)
        service._write_error_signal = MagicMock()
        service.knowledge_service = MagicMock()
        service.relationship_service = MagicMock()
        service.mediator = MagicMock()

        record = {
            "goal": "summarize_topic_and_save",
            "params": {"topic": "test"},  # Missing output_path
        }
        result = service.process(record)

        assert result == record
        service._write_error_signal.assert_called_once()

    @patch.object(CognitionService, "logger", new_callable=lambda: MagicMock())
    def test_handle_summarize_no_knowledge_atoms(self, mock_logger: MagicMock) -> None:
        """Test _handle_summarize_and_save with no knowledge atoms found."""
        service = CognitionService.__new__(CognitionService)
        service._write_error_signal = MagicMock()

        mock_knowledge = MagicMock()
        mock_knowledge.query.return_value = []  # No atoms

        service.knowledge_service = mock_knowledge
        service.relationship_service = MagicMock()
        service.mediator = MagicMock()

        record = {
            "goal": "summarize_topic_and_save",
            "params": {"topic": "test topic", "output_path": "test.md"},
        }
        result = service.process(record)

        assert result == record
        mock_logger.warning.assert_called()
        # Should not publish anything
        service.mediator.publish.assert_not_called()

    @patch.object(CognitionService, "logger", new_callable=lambda: MagicMock())
    def test_handle_summarize_low_trust(self, mock_logger: MagicMock) -> None:
        """Test _handle_summarize_and_save with low trust partner."""
        service = CognitionService.__new__(CognitionService)
        service._write_error_signal = MagicMock()

        mock_knowledge = MagicMock()
        mock_knowledge.query.return_value = [{"content": "test content"}]
        mock_knowledge.call_llm.return_value = {"text": "Summary text"}

        mock_relationship = MagicMock()
        mock_relationship.get_partnership.return_value = {"trust_level": 0.2}

        mock_mediator = MagicMock()

        service.knowledge_service = mock_knowledge
        service.relationship_service = mock_relationship
        service.mediator = mock_mediator

        record = {
            "goal": "summarize_topic_and_save",
            "params": {
                "topic": "test topic",
                "output_path": "test.md",
                "partner_id": "low_trust_partner",
            },
        }
        result = service.process(record)

        assert result == record
        # Verify LLM was called (summary modifier would be for brief summary)
        mock_knowledge.call_llm.assert_called_once()

    @patch.object(CognitionService, "logger", new_callable=lambda: MagicMock())
    def test_handle_summarize_high_trust(self, mock_logger: MagicMock) -> None:
        """Test _handle_summarize_and_save with high trust partner."""
        service = CognitionService.__new__(CognitionService)
        service._write_error_signal = MagicMock()

        mock_knowledge = MagicMock()
        mock_knowledge.query.return_value = [{"content": "test content"}]
        mock_knowledge.call_llm.return_value = {"text": "Detailed summary text"}

        mock_relationship = MagicMock()
        mock_relationship.get_partnership.return_value = {"trust_level": 0.85}

        mock_mediator = MagicMock()

        service.knowledge_service = mock_knowledge
        service.relationship_service = mock_relationship
        service.mediator = mock_mediator

        record = {
            "goal": "summarize_topic_and_save",
            "params": {
                "topic": "test topic",
                "output_path": "test.md",
                "partner_id": "high_trust_partner",
            },
        }
        result = service.process(record)

        assert result == record
        mock_knowledge.call_llm.assert_called_once()

    @patch.object(CognitionService, "logger", new_callable=lambda: MagicMock())
    def test_handle_summarize_no_partnership_found(self, mock_logger: MagicMock) -> None:
        """Test _handle_summarize_and_save when partnership not found."""
        service = CognitionService.__new__(CognitionService)
        service._write_error_signal = MagicMock()

        mock_knowledge = MagicMock()
        mock_knowledge.query.return_value = [{"content": "test content"}]
        mock_knowledge.call_llm.return_value = {"text": "Summary text"}

        mock_relationship = MagicMock()
        mock_relationship.get_partnership.return_value = None  # No partnership

        mock_mediator = MagicMock()

        service.knowledge_service = mock_knowledge
        service.relationship_service = mock_relationship
        service.mediator = mock_mediator

        record = {
            "goal": "summarize_topic_and_save",
            "params": {
                "topic": "test topic",
                "output_path": "test.md",
                "partner_id": "unknown_partner",
            },
        }
        result = service.process(record)

        assert result == record
        # Should still work with default trust
        mock_knowledge.call_llm.assert_called_once()
        mock_mediator.publish.assert_called_once()

    @patch.object(CognitionService, "logger", new_callable=lambda: MagicMock())
    def test_process_logs_goal(self, mock_logger: MagicMock) -> None:
        """Test process logs the goal."""
        service = CognitionService.__new__(CognitionService)
        service._write_error_signal = MagicMock()

        record = {"goal": "unknown", "params": {"key": "value"}}
        service.process(record)

        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args_list[0]
        assert call_args[0][0] == "cognition_process_started"

    @patch.object(CognitionService, "logger", new_callable=lambda: MagicMock())
    def test_process_handles_exception(self, mock_logger: MagicMock) -> None:
        """Test process handles exceptions gracefully."""
        service = CognitionService.__new__(CognitionService)
        service._write_error_signal = MagicMock()

        mock_knowledge = MagicMock()
        mock_knowledge.query.side_effect = RuntimeError("Test error")

        service.knowledge_service = mock_knowledge
        service.relationship_service = MagicMock()
        service.mediator = MagicMock()

        record = {
            "goal": "summarize_topic_and_save",
            "params": {"topic": "test", "output_path": "test.md"},
        }
        result = service.process(record)

        assert result == record
        mock_logger.error.assert_called()
        service._write_error_signal.assert_called_once()

    @patch.object(CognitionService, "logger", new_callable=lambda: MagicMock())
    def test_plan_structure(self, mock_logger: MagicMock) -> None:
        """Test that plan published has correct structure."""
        service = CognitionService.__new__(CognitionService)
        service._write_error_signal = MagicMock()

        mock_knowledge = MagicMock()
        mock_knowledge.query.return_value = [{"content": "test"}]
        mock_knowledge.call_llm.return_value = {"text": "Summary"}

        mock_mediator = MagicMock()

        service.knowledge_service = mock_knowledge
        service.relationship_service = MagicMock()
        service.mediator = mock_mediator

        record = {
            "goal": "summarize_topic_and_save",
            "params": {"topic": "test topic", "output_path": "output.md"},
        }
        service.process(record)

        # Check the published action
        mock_mediator.publish.assert_called_once()
        call_args = mock_mediator.publish.call_args
        assert call_args[0][0] == "action.execute"
        action = call_args[0][1]
        assert action["action"] == "write_file"
        assert action["params"]["path"] == "output.md"
        assert "Summary" in action["params"]["content"]

