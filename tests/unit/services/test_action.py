"""Tests for action service module.

Tests the action execution service.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.services.action.service import ActionService


class TestActionService:
    """Tests for ActionService class."""

    def test_service_name(self) -> None:
        """Test service name is set."""
        assert ActionService.service_name == "action"

    @patch.object(ActionService, "logger", new_callable=lambda: MagicMock())
    def test_process_unknown_action(self, mock_logger: MagicMock) -> None:
        """Test processing unknown action."""
        with TemporaryDirectory() as tmpdir:
            service = ActionService.__new__(ActionService)
            service._paths = {"root": Path(tmpdir)}
            service.output_dir = Path(tmpdir) / "output"
            service.sent_emails_dir = Path(tmpdir) / "sent_emails"
            service.output_dir.mkdir()
            service.sent_emails_dir.mkdir()
            service.mediator = MagicMock()

            record = {"action": "unknown_action", "params": {}}
            result = service.process(record)

            assert result == record
            service.mediator.publish.assert_called_once()

    @patch.object(ActionService, "logger", new_callable=lambda: MagicMock())
    def test_process_write_file(self, mock_logger: MagicMock) -> None:
        """Test processing write_file action."""
        with TemporaryDirectory() as tmpdir:
            service = ActionService.__new__(ActionService)
            service._paths = {"root": Path(tmpdir)}
            service.output_dir = Path(tmpdir) / "output"
            service.sent_emails_dir = Path(tmpdir) / "sent_emails"
            service.output_dir.mkdir()
            service.sent_emails_dir.mkdir()
            service.mediator = MagicMock()

            record = {
                "action": "write_file",
                "params": {"path": "test.txt", "content": "Hello World"},
            }
            result = service.process(record)

            assert result == record
            assert (service.output_dir / "test.txt").exists()
            assert (service.output_dir / "test.txt").read_text() == "Hello World"

    @patch.object(ActionService, "logger", new_callable=lambda: MagicMock())
    def test_process_send_email(self, mock_logger: MagicMock) -> None:
        """Test processing send_email action."""
        with TemporaryDirectory() as tmpdir:
            service = ActionService.__new__(ActionService)
            service._paths = {"root": Path(tmpdir)}
            service.output_dir = Path(tmpdir) / "output"
            service.sent_emails_dir = Path(tmpdir) / "sent_emails"
            service.output_dir.mkdir()
            service.sent_emails_dir.mkdir()
            service.mediator = MagicMock()

            record = {
                "action": "send_email",
                "params": {
                    "to": "test@example.com",
                    "subject": "Test Subject",
                    "body": "Test body",
                },
            }
            result = service.process(record)

            assert result == record
            # Check an email file was created
            email_files = list(service.sent_emails_dir.glob("*.eml"))
            assert len(email_files) == 1

    @patch.object(ActionService, "logger", new_callable=lambda: MagicMock())
    def test_write_file_missing_params(self, mock_logger: MagicMock) -> None:
        """Test write_file with missing params."""
        with TemporaryDirectory() as tmpdir:
            service = ActionService.__new__(ActionService)
            service._paths = {"root": Path(tmpdir)}
            service.output_dir = Path(tmpdir) / "output"
            service.sent_emails_dir = Path(tmpdir) / "sent_emails"
            service.output_dir.mkdir()
            service.sent_emails_dir.mkdir()
            service.mediator = MagicMock()

            record = {
                "action": "write_file",
                "params": {"path": "test.txt"},  # Missing content
            }
            result = service.process(record)

            # Should have completed (logged error internally)
            assert result == record

    @patch.object(ActionService, "logger", new_callable=lambda: MagicMock())
    def test_send_email_missing_params(self, mock_logger: MagicMock) -> None:
        """Test send_email with missing params."""
        with TemporaryDirectory() as tmpdir:
            service = ActionService.__new__(ActionService)
            service._paths = {"root": Path(tmpdir)}
            service.output_dir = Path(tmpdir) / "output"
            service.sent_emails_dir = Path(tmpdir) / "sent_emails"
            service.output_dir.mkdir()
            service.sent_emails_dir.mkdir()
            service.mediator = MagicMock()

            record = {
                "action": "send_email",
                "params": {"to": "test@example.com"},  # Missing subject and body
            }
            result = service.process(record)

            # Should have completed (logged error internally)
            assert result == record

    @patch.object(ActionService, "logger", new_callable=lambda: MagicMock())
    def test_write_file_sanitizes_path(self, mock_logger: MagicMock) -> None:
        """Test write_file sanitizes path to prevent traversal."""
        with TemporaryDirectory() as tmpdir:
            service = ActionService.__new__(ActionService)
            service._paths = {"root": Path(tmpdir)}
            service.output_dir = Path(tmpdir) / "output"
            service.sent_emails_dir = Path(tmpdir) / "sent_emails"
            service.output_dir.mkdir()
            service.sent_emails_dir.mkdir()
            service.mediator = MagicMock()

            # Try path traversal
            record = {
                "action": "write_file",
                "params": {"path": "../../../etc/passwd", "content": "bad"},
            }
            result = service.process(record)

            # File should be in output_dir with sanitized name
            assert (service.output_dir / "passwd").exists()

    @patch.object(ActionService, "logger", new_callable=lambda: MagicMock())
    def test_mediator_publish_on_success(self, mock_logger: MagicMock) -> None:
        """Test mediator publishes on successful action."""
        with TemporaryDirectory() as tmpdir:
            service = ActionService.__new__(ActionService)
            service._paths = {"root": Path(tmpdir)}
            service.output_dir = Path(tmpdir) / "output"
            service.sent_emails_dir = Path(tmpdir) / "sent_emails"
            service.output_dir.mkdir()
            service.sent_emails_dir.mkdir()
            service.mediator = MagicMock()

            record = {
                "action": "write_file",
                "params": {"path": "test.txt", "content": "Hello"},
            }
            service.process(record)

            # Check mediator was called with governance record
            service.mediator.publish.assert_called_once()
            call_args = service.mediator.publish.call_args
            assert call_args[0][0] == "governance.record"
            assert call_args[0][1]["result_status"] == "success"
