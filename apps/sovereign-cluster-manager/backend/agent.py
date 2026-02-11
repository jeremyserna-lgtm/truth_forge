"""Sovereign Cluster Manager Agent.

Runs on King, bridges EXO ↔ Supabase.
"""

import asyncio
import logging
import signal
import sys
from uuid import UUID

from config import settings
from exo_client import ExoClient, ExoState
from supabase_client import SupabaseClient
from vault_manager import VaultManager, ModelInfo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("sovereign-agent")


class SovereignAgent:
    """Main agent that syncs EXO state to Supabase and handles commands."""

    def __init__(self) -> None:
        self.exo = ExoClient()
        self.supabase = SupabaseClient()
        self.vault = VaultManager()
        self._running = False
        self._last_state: ExoState | None = None

    async def start(self) -> None:
        """Start the agent."""
        logger.info("Starting Sovereign Cluster Manager agent")
        await self.supabase.log_info("Agent starting", node=settings.node_id)

        self._running = True

        # Initial vault scan
        await self._sync_vault_to_supabase()

        # Run main loops
        await asyncio.gather(
            self._state_sync_loop(),
            self._command_processor_loop(),
        )

    async def stop(self) -> None:
        """Stop the agent."""
        logger.info("Stopping agent")
        self._running = False
        await self.exo.close()
        await self.supabase.log_info("Agent stopped", node=settings.node_id)

    # =========================================================================
    # STATE SYNC
    # =========================================================================

    async def _state_sync_loop(self) -> None:
        """Continuously sync EXO state to Supabase."""
        while self._running:
            try:
                await self._sync_state()
            except Exception as e:
                logger.error("State sync failed", extra={"error": str(e)})
                await self.supabase.set_cluster_error(str(e))

            await asyncio.sleep(settings.poll_interval_seconds)

    async def _sync_state(self) -> None:
        """Sync current EXO state to Supabase."""
        # Check EXO health
        if not await self.exo.health_check():
            await self.supabase.update_cluster_state(
                status="error",
                last_error="EXO API not responding",
            )
            return

        # Get full state
        state = await self.exo.get_state()
        self._last_state = state

        # Calculate aggregates
        total_ram = sum(n.memory_total_gb for n in state.nodes)
        used_ram = total_ram - sum(n.memory_available_gb for n in state.nodes)
        nodes_online = sum(1 for n in state.nodes if n.is_online)

        # Determine status
        if state.instances:
            status = "running"
        elif nodes_online > 0:
            status = "ready"
        else:
            status = "error"

        # Get active model
        active_model_id = None
        if state.instances:
            # Look up model in our registry
            model_name = state.instances[0].model_id
            model = await self.supabase.get_model_by_name(model_name)
            if model:
                active_model_id = UUID(model["id"])

        # Update cluster state
        await self.supabase.update_cluster_state(
            status=status,
            active_model_id=active_model_id,
            total_ram_gb=int(total_ram),
            used_ram_gb=int(used_ram),
            nodes_online=nodes_online,
            exo_state=state.raw,
        )

        # Update individual nodes
        for node in state.nodes:
            node_id = self._map_exo_node_to_id(node.hostname)
            await self.supabase.update_node(
                node_id=node_id,
                status="online" if node.is_online else "offline",
                ram_available_gb=int(node.memory_available_gb),
                metadata={"exo_node_id": node.node_id},
            )

    def _map_exo_node_to_id(self, hostname: str) -> str:
        """Map EXO hostname to our node ID."""
        hostname_lower = hostname.lower()
        if "king" in hostname_lower:
            return "king"
        for i, soldier_host in enumerate(settings.soldier_hosts, 1):
            if soldier_host.split(".")[0].lower() in hostname_lower:
                return f"soldier{i}"
        return hostname_lower

    # =========================================================================
    # VAULT SYNC
    # =========================================================================

    async def _sync_vault_to_supabase(self) -> None:
        """Scan vault and sync models to Supabase."""
        logger.info("Scanning vault for models")

        if not self.vault.is_available():
            logger.warning("Vault not available")
            await self.supabase.log_error("Vault not mounted", path=str(settings.vault_path))
            return

        models = self.vault.scan_models()
        logger.info("Found models in vault", extra={"count": len(models)})

        for model in models:
            await self._upsert_model(model)

        await self.supabase.log_info(
            "Vault sync complete",
            model_count=len(models),
            vault_stats=self.vault.get_vault_stats(),
        )

    async def _upsert_model(self, model: ModelInfo) -> UUID:
        """Upsert a model to Supabase."""
        # Determine if cluster is required based on size
        cluster_required = model.size_gb > 400  # > 400GB needs cluster
        single_node_capable = model.size_gb <= 450  # King can handle up to ~450GB

        # Extract tags
        tags = []
        if model.is_base:
            tags.append("base")
        if model.is_checkpoint:
            tags.append("checkpoint")
        if model.is_lora:
            tags.append("lora")

        return await self.supabase.upsert_model(
            name=model.name,
            path=model.relative_path,
            size_gb=model.size_gb,
            format=model.format,
            quantization=model.quantization,
            tags=tags,
            cluster_required=cluster_required,
            single_node_capable=single_node_capable,
            min_ram_gb=model.size_gb * 1.1,  # ~10% overhead
            performance_metrics=model.metadata.get("performance", {}),
        )

    # =========================================================================
    # COMMAND PROCESSOR
    # =========================================================================

    async def _command_processor_loop(self) -> None:
        """Process commands from Supabase."""
        while self._running:
            try:
                commands = await self.supabase.get_pending_commands()
                for cmd in commands:
                    await self._process_command(cmd)
            except Exception as e:
                logger.error("Command processing failed", extra={"error": str(e)})

            await asyncio.sleep(settings.command_check_interval_seconds)

    async def _process_command(self, cmd: dict) -> None:
        """Process a single command."""
        command_id = UUID(cmd["id"])
        command = cmd["command"]
        payload = cmd.get("payload", {})

        logger.info(
            "Processing command",
            extra={"command_id": str(command_id), "command": command},
        )
        await self.supabase.mark_command_processing(command_id)

        try:
            result = await self._execute_command(command, payload)
            await self.supabase.mark_command_completed(command_id, result)
            await self.supabase.log_info(
                f"Command completed: {command}",
                command_id=str(command_id),
                result=result,
            )
        except Exception as e:
            error_msg = str(e)
            logger.error(
                "Command failed",
                extra={"command_id": str(command_id), "error": error_msg},
            )
            await self.supabase.mark_command_failed(command_id, error_msg)
            await self.supabase.log_error(
                f"Command failed: {command}",
                command_id=str(command_id),
                error=error_msg,
            )

    async def _execute_command(self, command: str, payload: dict) -> dict:
        """Execute a command and return result."""
        match command:
            case "load_model":
                return await self._cmd_load_model(payload)
            case "unload_model":
                return await self._cmd_unload_model(payload)
            case "apply_preset":
                return await self._cmd_apply_preset(payload)
            case "refresh_state":
                await self._sync_state()
                return {"status": "refreshed"}
            case "scan_vault":
                await self._sync_vault_to_supabase()
                stats = self.vault.get_vault_stats()
                return {"status": "scanned", "vault_stats": stats}
            case _:
                raise ValueError(f"Unknown command: {command}")

    async def _cmd_load_model(self, payload: dict) -> dict:
        """Load a model into EXO."""
        model_id = UUID(payload["model_id"])
        mode = payload.get("mode", "auto")

        # Get model from Supabase
        model = await self.supabase.get_model_by_id(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")

        # Unload any existing model first
        if self._last_state and self._last_state.instances:
            for inst in self._last_state.instances:
                await self.exo.delete_instance(inst.instance_id)

        # Build full path
        model_path = str(settings.vault_path / model["path"])

        # Determine placement based on mode
        placement = {}
        if mode == "single":
            placement = {"mode": "single_node"}
        elif mode == "cluster":
            placement = {"mode": "distributed"}
        # "auto" leaves placement empty for EXO to decide

        # Create instance
        instance_id = await self.exo.create_instance(
            model_id=model["name"],
            model_path=model_path,
            placement=placement,
        )

        # Update model loaded status
        await self.supabase.set_model_loaded(model_id, True)

        return {
            "instance_id": instance_id,
            "model": model["name"],
            "mode": mode,
        }

    async def _cmd_unload_model(self, payload: dict) -> dict:
        """Unload all models from EXO."""
        if not self._last_state:
            return {"status": "no_state"}

        unloaded = []
        for inst in self._last_state.instances:
            if await self.exo.delete_instance(inst.instance_id):
                unloaded.append(inst.instance_id)

                # Update model loaded status
                model = await self.supabase.get_model_by_name(inst.model_id)
                if model:
                    await self.supabase.set_model_loaded(UUID(model["id"]), False)

        return {"unloaded": unloaded}

    async def _cmd_apply_preset(self, payload: dict) -> dict:
        """Apply a saved preset."""
        preset_id = UUID(payload["preset_id"])

        preset = await self.supabase.get_preset(preset_id)
        if not preset:
            raise ValueError(f"Preset not found: {preset_id}")

        # If preset has a model, load it
        if preset.get("model_id"):
            load_result = await self._cmd_load_model({
                "model_id": preset["model_id"],
                "mode": preset["deployment_mode"],
            })
            return {
                "preset": preset["name"],
                "load_result": load_result,
            }

        # If no model (e.g., "Training Mode"), just unload
        unload_result = await self._cmd_unload_model({})
        return {
            "preset": preset["name"],
            "unload_result": unload_result,
        }


async def main() -> None:
    """Main entry point."""
    agent = SovereignAgent()

    # Handle shutdown signals
    loop = asyncio.get_event_loop()

    def shutdown_handler() -> None:
        logger.info("Shutdown signal received")
        asyncio.create_task(agent.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown_handler)

    try:
        await agent.start()
    except Exception as e:
        logger.error("Agent crashed", extra={"error": str(e)})
        raise


if __name__ == "__main__":
    asyncio.run(main())
