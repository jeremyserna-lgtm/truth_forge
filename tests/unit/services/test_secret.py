"""Tests for secret service module.

Tests the secret management service.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from truth_forge.services.secret.service import SecretNotFoundError, SecretService


class TestSecretNotFoundError:
    """Tests for SecretNotFoundError exception."""

    def test_exception_message(self) -> None:
        """Test exception can be raised with message."""
        with pytest.raises(SecretNotFoundError) as exc_info:
            raise SecretNotFoundError("Secret not found")

        assert str(exc_info.value) == "Secret not found"


class TestSecretService:
    """Tests for SecretService class."""

    def test_service_name(self) -> None:
        """Test service name is set."""
        assert SecretService.service_name == "secret"

    @patch.object(SecretService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.secret.service.settings")
    def test_init_mock_mode_no_project(self, mock_settings: MagicMock, mock_logger: MagicMock) -> None:
        """Test init enters mock mode when no GCP project."""
        mock_settings.effective_gcp_project = None

        service = SecretService.__new__(SecretService)
        service._paths = {"root": MagicMock(), "hold1": MagicMock(), "hold2": MagicMock()}
        service._cache = {}
        service._client = None
        service._mock_mode = True

        assert service._mock_mode is True

    @patch.object(SecretService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.secret.service.settings")
    def test_get_secret_from_cache(self, mock_settings: MagicMock, mock_logger: MagicMock) -> None:
        """Test get_secret returns cached value."""
        service = SecretService.__new__(SecretService)
        service._cache = {"my_secret": "cached_value"}
        service._mock_mode = False

        result = service.get_secret("my_secret")

        assert result == "cached_value"

    @patch.object(SecretService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.secret.service.settings")
    def test_get_secret_mock_mode(self, mock_settings: MagicMock, mock_logger: MagicMock) -> None:
        """Test get_secret returns mock value in mock mode."""
        service = SecretService.__new__(SecretService)
        service._cache = {}
        service._mock_mode = True

        result = service.get_secret("test_secret")

        assert result == "mock_test_secret"
        mock_logger.warning.assert_called()

    @patch.object(SecretService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.secret.service.settings")
    @patch("truth_forge.services.secret.service.secretmanager.SecretManagerServiceClient")
    def test_get_secret_from_gcp(
        self,
        mock_client_class: MagicMock,
        mock_settings: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        """Test get_secret fetches from GCP."""
        mock_settings.effective_gcp_project = "test-project"

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "real_secret_value"
        mock_client.access_secret_version.return_value = mock_response
        mock_client_class.return_value = mock_client

        service = SecretService.__new__(SecretService)
        service._cache = {}
        service._client = None
        service._mock_mode = False

        result = service.get_secret("my_secret")

        assert result == "real_secret_value"
        assert service._cache["my_secret"] == "real_secret_value"
        mock_logger.info.assert_called()

    @patch.object(SecretService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.secret.service.settings")
    @patch("truth_forge.services.secret.service.secretmanager.SecretManagerServiceClient")
    def test_get_secret_not_found(
        self,
        mock_client_class: MagicMock,
        mock_settings: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        """Test get_secret raises SecretNotFoundError on NotFound."""
        from google.api_core.exceptions import NotFound

        mock_settings.effective_gcp_project = "test-project"

        mock_client = MagicMock()
        mock_client.access_secret_version.side_effect = NotFound("Not found")
        mock_client_class.return_value = mock_client

        service = SecretService.__new__(SecretService)
        service._cache = {}
        service._client = None
        service._mock_mode = False

        with pytest.raises(SecretNotFoundError) as exc_info:
            service.get_secret("missing_secret")

        assert "not found or permission denied" in str(exc_info.value)

    @patch.object(SecretService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.secret.service.settings")
    @patch("truth_forge.services.secret.service.secretmanager.SecretManagerServiceClient")
    def test_get_secret_permission_denied(
        self,
        mock_client_class: MagicMock,
        mock_settings: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        """Test get_secret raises SecretNotFoundError on PermissionDenied."""
        from google.api_core.exceptions import PermissionDenied

        mock_settings.effective_gcp_project = "test-project"

        mock_client = MagicMock()
        mock_client.access_secret_version.side_effect = PermissionDenied("Denied")
        mock_client_class.return_value = mock_client

        service = SecretService.__new__(SecretService)
        service._cache = {}
        service._client = None
        service._mock_mode = False

        with pytest.raises(SecretNotFoundError):
            service.get_secret("restricted_secret")

    @patch.object(SecretService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.secret.service.settings")
    @patch("truth_forge.services.secret.service.secretmanager.SecretManagerServiceClient")
    def test_get_secret_unexpected_error(
        self,
        mock_client_class: MagicMock,
        mock_settings: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        """Test get_secret re-raises unexpected errors."""
        mock_settings.effective_gcp_project = "test-project"

        mock_client = MagicMock()
        mock_client.access_secret_version.side_effect = RuntimeError("Unexpected")
        mock_client_class.return_value = mock_client

        service = SecretService.__new__(SecretService)
        service._cache = {}
        service._client = None
        service._mock_mode = False

        with pytest.raises(RuntimeError):
            service.get_secret("any_secret")

    @patch.object(SecretService, "logger", new_callable=lambda: MagicMock())
    def test_process_not_implemented(self, mock_logger: MagicMock) -> None:
        """Test process raises NotImplementedError."""
        service = SecretService.__new__(SecretService)

        with pytest.raises(NotImplementedError):
            service.process({"key": "value"})

    @patch.object(SecretService, "logger", new_callable=lambda: MagicMock())
    def test_get_session_stats(self, mock_logger: MagicMock) -> None:
        """Test get_session_stats returns cache count."""
        service = SecretService.__new__(SecretService)
        service._cache = {"secret1": "val1", "secret2": "val2"}

        stats = service.get_session_stats()

        assert stats["cached_secrets_count"] == 2

    @patch.object(SecretService, "logger", new_callable=lambda: MagicMock())
    def test_inhale_not_implemented(self, mock_logger: MagicMock) -> None:
        """Test inhale raises NotImplementedError."""
        service = SecretService.__new__(SecretService)

        with pytest.raises(NotImplementedError):
            service.inhale({"data": "test"})

    @patch.object(SecretService, "logger", new_callable=lambda: MagicMock())
    def test_sync_not_implemented(self, mock_logger: MagicMock) -> None:
        """Test sync raises NotImplementedError."""
        service = SecretService.__new__(SecretService)

        with pytest.raises(NotImplementedError):
            service.sync()

    @patch.object(SecretService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.secret.service.settings")
    def test_get_client_returns_none_in_mock_mode(
        self, mock_settings: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Test _get_client returns None in mock mode."""
        service = SecretService.__new__(SecretService)
        service._mock_mode = True
        service._client = None

        result = service._get_client()

        assert result is None

    @patch.object(SecretService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.secret.service.settings")
    @patch("truth_forge.services.secret.service.secretmanager.SecretManagerServiceClient")
    def test_get_client_creates_client(
        self,
        mock_client_class: MagicMock,
        mock_settings: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        """Test _get_client creates client when not in mock mode."""
        service = SecretService.__new__(SecretService)
        service._mock_mode = False
        service._client = None

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        result = service._get_client()

        assert result is mock_client
        mock_client_class.assert_called_once()

    @patch.object(SecretService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.secret.service.settings")
    def test_get_client_reuses_existing(
        self, mock_settings: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Test _get_client returns existing client."""
        service = SecretService.__new__(SecretService)
        service._mock_mode = False
        existing_client = MagicMock()
        service._client = existing_client

        result = service._get_client()

        assert result is existing_client

