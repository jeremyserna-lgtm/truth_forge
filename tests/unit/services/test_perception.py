"""Tests for perception service module.

Tests the perception/sensing service.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from truth_forge.services.perception.service import PerceptionService


class TestPerceptionService:
    """Tests for PerceptionService class."""

    def test_service_name(self) -> None:
        """Test service name is set."""
        assert PerceptionService.service_name == "perception"

    @patch.object(PerceptionService, "logger", new_callable=lambda: MagicMock())
    def test_process_missing_params(self, mock_logger: MagicMock) -> None:
        """Test process raises for missing params."""
        service = PerceptionService.__new__(PerceptionService)
        service.mediator = MagicMock()

        record = {"type": None, "source": None}

        with pytest.raises(ValueError) as exc_info:
            service.process(record)

        assert "requires" in str(exc_info.value)

    @patch.object(PerceptionService, "logger", new_callable=lambda: MagicMock())
    def test_process_unknown_type(self, mock_logger: MagicMock) -> None:
        """Test process handles unknown perception type."""
        service = PerceptionService.__new__(PerceptionService)
        service.mediator = MagicMock()

        record = {"type": "unknown_type", "source": "http://example.com"}
        result = service.process(record)

        assert result == record
        mock_logger.warning.assert_called_once()

    @patch.object(PerceptionService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.perception.service.requests.Session")
    def test_scrape_website(self, mock_session_class: MagicMock, mock_logger: MagicMock) -> None:
        """Test scrape_website method."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <head><title>Test</title></head>
            <body>
                <script>alert('test');</script>
                <main>
                    <p>Main content here</p>
                </main>
            </body>
        </html>
        """
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        service = PerceptionService.__new__(PerceptionService)
        service.mediator = MagicMock()
        service.http_session = mock_session

        service.scrape_website("http://example.com")

        service.mediator.publish.assert_called_once()
        call_args = service.mediator.publish.call_args
        assert call_args[0][0] == "knowledge.process"
        assert "Main content here" in call_args[0][1]["content"]

    @patch.object(PerceptionService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.perception.service.requests.Session")
    def test_poll_api(self, mock_session_class: MagicMock, mock_logger: MagicMock) -> None:
        """Test poll_api method."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        service = PerceptionService.__new__(PerceptionService)
        service.mediator = MagicMock()
        service.http_session = mock_session

        service.poll_api("http://api.example.com/data")

        service.mediator.publish.assert_called_once()
        call_args = service.mediator.publish.call_args
        assert call_args[0][0] == "knowledge.process"
        assert call_args[0][1]["content"] == {"data": "test"}
        assert call_args[0][1]["content_type"] == "application/json"

    @patch.object(PerceptionService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.perception.service.requests.Session")
    def test_scrape_website_error(self, mock_session_class: MagicMock, mock_logger: MagicMock) -> None:
        """Test scrape_website handles errors."""
        import requests

        mock_session = MagicMock()
        mock_session.get.side_effect = requests.RequestException("Network error")
        mock_session_class.return_value = mock_session

        service = PerceptionService.__new__(PerceptionService)
        service.mediator = MagicMock()
        service.http_session = mock_session

        with pytest.raises(requests.RequestException):
            service.scrape_website("http://example.com")

        mock_logger.error.assert_called()

    @patch.object(PerceptionService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.perception.service.requests.Session")
    def test_poll_api_error(self, mock_session_class: MagicMock, mock_logger: MagicMock) -> None:
        """Test poll_api handles errors."""
        import requests

        mock_session = MagicMock()
        mock_session.get.side_effect = requests.RequestException("Network error")
        mock_session_class.return_value = mock_session

        service = PerceptionService.__new__(PerceptionService)
        service.mediator = MagicMock()
        service.http_session = mock_session

        with pytest.raises(requests.RequestException):
            service.poll_api("http://api.example.com")

        mock_logger.error.assert_called()

    @patch.object(PerceptionService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.perception.service.requests.Session")
    def test_process_scrape_website(self, mock_session_class: MagicMock, mock_logger: MagicMock) -> None:
        """Test process with scrape_website type."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        service = PerceptionService.__new__(PerceptionService)
        service.mediator = MagicMock()
        service.http_session = mock_session
        service._write_error_signal = MagicMock()

        record = {"type": "scrape_website", "source": "http://example.com"}
        result = service.process(record)

        assert result == record

    @patch.object(PerceptionService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.perception.service.requests.Session")
    def test_process_poll_api(self, mock_session_class: MagicMock, mock_logger: MagicMock) -> None:
        """Test process with poll_api type."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        service = PerceptionService.__new__(PerceptionService)
        service.mediator = MagicMock()
        service.http_session = mock_session
        service._write_error_signal = MagicMock()

        record = {"type": "poll_api", "source": "http://api.example.com"}
        result = service.process(record)

        assert result == record

    @patch.object(PerceptionService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.perception.service.requests.Session")
    def test_process_handles_exception(self, mock_session_class: MagicMock, mock_logger: MagicMock) -> None:
        """Test process handles exceptions gracefully."""
        import requests

        mock_session = MagicMock()
        mock_session.get.side_effect = requests.RequestException("Error")
        mock_session_class.return_value = mock_session

        service = PerceptionService.__new__(PerceptionService)
        service.mediator = MagicMock()
        service.http_session = mock_session
        service._write_error_signal = MagicMock()

        record = {"type": "scrape_website", "source": "http://example.com"}
        result = service.process(record)

        # Should not raise, should log error
        assert result == record
        mock_logger.error.assert_called()
        service._write_error_signal.assert_called_once()
