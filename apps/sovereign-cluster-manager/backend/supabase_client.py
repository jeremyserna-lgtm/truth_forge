"""Supabase client for state sync and command handling."""

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from supabase import create_client, Client

from config import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client for Supabase operations."""

    def __init__(self) -> None:
        self._client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key,
        )

    # =========================================================================
    # CLUSTER STATE
    # =========================================================================

    async def update_cluster_state(
        self,
        status: str,
        active_model_id: UUID | None = None,
        active_preset_id: UUID | None = None,
        deployment_mode: str | None = None,
        total_ram_gb: int | None = None,
        used_ram_gb: int | None = None,
        nodes_online: int | None = None,
        exo_state: dict | None = None,
        last_error: str | None = None,
    ) -> None:
        """Update the singleton cluster state."""
        data: dict[str, Any] = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if active_model_id is not None:
            data["active_model_id"] = str(active_model_id)
        if active_preset_id is not None:
            data["active_preset_id"] = str(active_preset_id)
        if deployment_mode is not None:
            data["deployment_mode"] = deployment_mode
        if total_ram_gb is not None:
            data["total_ram_gb"] = total_ram_gb
        if used_ram_gb is not None:
            data["used_ram_gb"] = used_ram_gb
        if nodes_online is not None:
            data["nodes_online"] = nodes_online
        if exo_state is not None:
            data["exo_state"] = exo_state
        if last_error is not None:
            data["last_error"] = last_error
            data["last_error_at"] = datetime.now(timezone.utc).isoformat()

        self._client.table("cluster_state").upsert({"id": 1, **data}).execute()

    async def set_cluster_error(self, error: str) -> None:
        """Set cluster error state."""
        await self.update_cluster_state(
            status="error",
            last_error=error,
        )

    # =========================================================================
    # NODES
    # =========================================================================

    async def update_node(
        self,
        node_id: str,
        status: str,
        ram_available_gb: int | None = None,
        storage_available_gb: int | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Update node status."""
        data: dict[str, Any] = {
            "id": node_id,
            "status": status,
            "last_seen_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if ram_available_gb is not None:
            data["ram_available_gb"] = ram_available_gb
        if storage_available_gb is not None:
            data["storage_available_gb"] = storage_available_gb
        if metadata is not None:
            data["metadata"] = metadata

        self._client.table("nodes").upsert(data).execute()

    async def set_node_offline(self, node_id: str) -> None:
        """Mark a node as offline."""
        await self.update_node(node_id, status="offline")

    # =========================================================================
    # MODELS
    # =========================================================================

    async def upsert_model(
        self,
        name: str,
        path: str,
        size_gb: float,
        format: str = "gguf",
        quantization: str | None = None,
        base_model: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        cluster_required: bool = False,
        single_node_capable: bool = True,
        min_ram_gb: float | None = None,
        performance_metrics: dict | None = None,
    ) -> UUID:
        """Insert or update a model in the registry."""
        data: dict[str, Any] = {
            "name": name,
            "path": path,
            "size_gb": size_gb,
            "format": format,
            "cluster_required": cluster_required,
            "single_node_capable": single_node_capable,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if quantization:
            data["quantization"] = quantization
        if base_model:
            data["base_model"] = base_model
        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags
        if min_ram_gb:
            data["min_ram_gb"] = min_ram_gb
        if performance_metrics:
            data["performance_metrics"] = performance_metrics

        result = (
            self._client.table("models")
            .upsert(data, on_conflict="name")
            .execute()
        )
        return UUID(result.data[0]["id"])

    async def set_model_loaded(self, model_id: UUID, is_loaded: bool) -> None:
        """Update model loaded status."""
        data = {
            "is_loaded": is_loaded,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if is_loaded:
            data["loaded_at"] = datetime.now(timezone.utc).isoformat()

        self._client.table("models").update(data).eq("id", str(model_id)).execute()

    async def get_model_by_name(self, name: str) -> dict | None:
        """Get model by name."""
        result = self._client.table("models").select("*").eq("name", name).execute()
        return result.data[0] if result.data else None

    async def get_model_by_id(self, model_id: UUID) -> dict | None:
        """Get model by ID."""
        result = self._client.table("models").select("*").eq("id", str(model_id)).execute()
        return result.data[0] if result.data else None

    async def list_models(self) -> list[dict]:
        """List all models."""
        result = self._client.table("models").select("*").order("name").execute()
        return result.data

    # =========================================================================
    # PRESETS
    # =========================================================================

    async def get_preset(self, preset_id: UUID) -> dict | None:
        """Get preset by ID."""
        result = self._client.table("presets").select("*").eq("id", str(preset_id)).execute()
        return result.data[0] if result.data else None

    async def list_presets(self) -> list[dict]:
        """List all presets."""
        result = self._client.table("presets").select("*").order("sort_order").execute()
        return result.data

    # =========================================================================
    # COMMANDS
    # =========================================================================

    async def get_pending_commands(self) -> list[dict]:
        """Get pending commands ordered by creation time."""
        result = (
            self._client.table("commands")
            .select("*")
            .eq("status", "pending")
            .order("created_at")
            .execute()
        )
        return result.data

    async def mark_command_processing(self, command_id: UUID) -> None:
        """Mark command as being processed."""
        self._client.table("commands").update(
            {"status": "processing"}
        ).eq("id", str(command_id)).execute()

    async def mark_command_completed(
        self,
        command_id: UUID,
        result: dict | None = None,
    ) -> None:
        """Mark command as completed."""
        data = {
            "status": "completed",
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
        if result:
            data["result"] = result

        self._client.table("commands").update(data).eq("id", str(command_id)).execute()

    async def mark_command_failed(self, command_id: UUID, error: str) -> None:
        """Mark command as failed."""
        self._client.table("commands").update(
            {
                "status": "failed",
                "error": error,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }
        ).eq("id", str(command_id)).execute()

    # =========================================================================
    # LOGS
    # =========================================================================

    async def log(
        self,
        level: str,
        source: str,
        message: str,
        metadata: dict | None = None,
    ) -> None:
        """Write a log entry."""
        self._client.table("logs").insert(
            {
                "level": level,
                "source": source,
                "message": message,
                "metadata": metadata or {},
            }
        ).execute()

    async def log_info(self, message: str, **metadata: Any) -> None:
        """Log info message."""
        await self.log("info", "agent", message, metadata)

    async def log_error(self, message: str, **metadata: Any) -> None:
        """Log error message."""
        await self.log("error", "agent", message, metadata)
