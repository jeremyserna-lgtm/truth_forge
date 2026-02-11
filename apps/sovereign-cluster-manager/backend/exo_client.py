"""Client for EXO REST API."""

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class ExoInstance:
    """Represents a loaded model instance in EXO."""

    instance_id: str
    model_id: str
    placement: dict[str, Any]
    status: str


@dataclass
class ExoNode:
    """Represents a node in the EXO cluster."""

    node_id: str
    hostname: str
    memory_total_gb: float
    memory_available_gb: float
    is_online: bool


@dataclass
class ExoState:
    """Full state from EXO API."""

    nodes: list[ExoNode]
    instances: list[ExoInstance]
    available_models: list[dict[str, Any]]
    raw: dict[str, Any]


class ExoClient:
    """Client for interacting with EXO API."""

    def __init__(self, base_url: str = settings.exo_api_url) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def _get(self, path: str) -> dict[str, Any]:
        """Make GET request to EXO API."""
        url = f"{self.base_url}{path}"
        try:
            response = await self._client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("EXO API error", extra={"path": path, "error": str(e)})
            raise

    async def _post(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make POST request to EXO API."""
        url = f"{self.base_url}{path}"
        try:
            response = await self._client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("EXO API error", extra={"path": path, "error": str(e)})
            raise

    async def _delete(self, path: str) -> dict[str, Any]:
        """Make DELETE request to EXO API."""
        url = f"{self.base_url}{path}"
        try:
            response = await self._client.delete(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("EXO API error", extra={"path": path, "error": str(e)})
            raise

    async def get_state(self) -> ExoState:
        """Get full cluster state from EXO."""
        raw = await self._get("/state")

        nodes = []
        for node_data in raw.get("nodes", []):
            nodes.append(
                ExoNode(
                    node_id=node_data.get("node_id", "unknown"),
                    hostname=node_data.get("hostname", "unknown"),
                    memory_total_gb=node_data.get("memory_total_gb", 0),
                    memory_available_gb=node_data.get("memory_available_gb", 0),
                    is_online=node_data.get("is_online", False),
                )
            )

        instances = []
        for inst_data in raw.get("instances", []):
            instances.append(
                ExoInstance(
                    instance_id=inst_data.get("instance_id", ""),
                    model_id=inst_data.get("model_id", ""),
                    placement=inst_data.get("placement", {}),
                    status=inst_data.get("status", "unknown"),
                )
            )

        return ExoState(
            nodes=nodes,
            instances=instances,
            available_models=raw.get("models", []),
            raw=raw,
        )

    async def get_node_id(self) -> str:
        """Get this node's EXO identifier."""
        result = await self._get("/node_id")
        return result.get("node_id", "unknown")

    async def list_models(self) -> list[dict[str, Any]]:
        """List available models."""
        result = await self._get("/v1/models")
        return result.get("data", [])

    async def preview_placements(self, model_id: str) -> list[dict[str, Any]]:
        """Preview valid placements for a model."""
        result = await self._get(f"/instance/previews?model_id={model_id}")
        return result.get("previews", [])

    async def create_instance(
        self,
        model_id: str,
        model_path: str | None = None,
        placement: dict[str, Any] | None = None,
    ) -> str:
        """Create a new model instance. Returns instance_id."""
        payload: dict[str, Any] = {
            "instance": {
                "model_id": model_id,
                "placement": placement or {},
            }
        }
        if model_path:
            payload["instance"]["model_path"] = model_path

        result = await self._post("/instance", payload)
        return result.get("instance_id", "")

    async def delete_instance(self, instance_id: str) -> bool:
        """Delete a model instance."""
        try:
            await self._delete(f"/instance/{instance_id}")
            return True
        except httpx.HTTPError:
            return False

    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        stream: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Send chat completion request (OpenAI-compatible)."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs,
        }
        return await self._post("/v1/chat/completions", payload)

    async def health_check(self) -> bool:
        """Check if EXO API is responding."""
        try:
            await self._get("/node_id")
            return True
        except Exception:
            return False
