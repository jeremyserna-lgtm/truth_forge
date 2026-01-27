"""Secret Service for centralized secret management.

This service is the single point of contact for retrieving secrets.
It fetches secrets from Google Cloud Secret Manager and provides an in-memory
cache to reduce latency and cost.
"""

from __future__ import annotations

from typing import Any

import structlog
from google.api_core.exceptions import NotFound, PermissionDenied
from google.cloud import secretmanager

from truth_forge.core.settings import settings
from truth_forge.schema.event import Event, EventType
from truth_forge.services.base import BaseService
from truth_forge.services.factory import register_service


logger = structlog.get_logger(__name__)


class SecretNotFoundError(Exception):
    """Raised when a secret cannot be found."""

    pass


@register_service()
class SecretService(BaseService):
    """A service for managing secrets."""

    service_name = "secret"

    def __init__(self) -> None:
        super().__init__()
        self._cache: dict[str, str] = {}
        self._client: secretmanager.SecretManagerServiceClient | None = None
        self._mock_mode = not settings.effective_gcp_project
        if self._mock_mode:
            self.logger.warning("gcp_project_id_not_set", service="secret")

    def _get_client(self) -> secretmanager.SecretManagerServiceClient | None:
        """Initializes and returns the Secret Manager client."""
        if self._mock_mode:
            return None
        if self._client is None:
            self._client = secretmanager.SecretManagerServiceClient()
        return self._client

    def get_secret(self, secret_id: str) -> str:
        """Retrieves a secret from the cache or GCP Secret Manager."""
        if secret_id in self._cache:
            return self._cache[secret_id]

        if self._mock_mode:
            self.logger.warning("returning_mock_secret", secret_id=secret_id)
            return f"mock_{secret_id}"

        project_id = settings.effective_gcp_project
        if not project_id:  # Should not be reached due to mock_mode
            raise SecretNotFoundError("GCP_PROJECT_ID is not configured, cannot fetch secrets.")

        client = self._get_client()
        if not client:  # Should not be reached
            raise SecretNotFoundError("Secret client is not available.")

        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

        try:
            response = client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode("UTF-8")
            self._cache[secret_id] = secret_value
            self.logger.info("secret_fetched", secret_id=secret_id)
            return secret_value
        except (NotFound, PermissionDenied) as e:
            self.logger.error("secret_fetch_failed", secret_id=secret_id, error=str(e))
            raise SecretNotFoundError(
                f"Secret '{secret_id}' not found or permission denied."
            ) from e
        except Exception as e:
            self.logger.error("secret_fetch_unexpected_error", secret_id=secret_id, error=str(e))
            raise
    
    def get_secret_with_variants(self, secret_id: str, variants: list[str] | None = None) -> str:
        """Retrieves a secret trying multiple name variations.
        
        Args:
            secret_id: Primary secret ID to try first
            variants: List of alternative secret IDs to try if primary fails
            
        Returns:
            Secret value from first successful retrieval
            
        Raises:
            SecretNotFoundError: If none of the variants are found
        """
        # Try primary secret ID first
        try:
            return self.get_secret(secret_id)
        except SecretNotFoundError:
            pass
        
        # Try variants if provided
        if variants:
            for variant in variants:
                try:
                    return self.get_secret(variant)
                except SecretNotFoundError:
                    continue
        
        # If all failed, raise error with helpful message
        all_names = [secret_id] + (variants or [])
        raise SecretNotFoundError(
            f"Secret not found. Tried: {', '.join(all_names)}"
        )

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """This service does not process records."""
        raise NotImplementedError("SecretService does not process records.")

    def get_session_stats(self) -> dict[str, Any]:
        """Returns statistics for the current session."""
        return {"cached_secrets_count": len(self._cache)}

    def inhale(
        self,
        data: dict[str, Any],
        event_type: EventType = EventType.RECORD_CREATED,
        aggregate_id: str | None = None,
        correlation_id: str | None = None,
    ) -> Event:
        """This service does not support asynchronous intake."""
        raise NotImplementedError(
            "SecretService is a synchronous provider and does not use inhale()."
        )

    def sync(self, batch_size: int = 1000) -> dict[str, Any]:
        """This service does not support batch processing."""
        raise NotImplementedError(
            "SecretService is a synchronous provider and does not use sync()."
        )
