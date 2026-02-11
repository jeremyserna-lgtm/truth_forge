"""Genesis Heartbeat — NOT-ME's autonomic nervous system.

Jeremy lives his life. This daemon observes and metabolizes.

The heartbeat cycle:
1. GATHER — Collect life signals (files, browser, system)
2. FILTER — Deduplicate and prioritize
3. CASCADE — Run the full pipeline (atomize → synthesize → forge)
4. PROVE — Record successful capabilities in the manifest
5. PERSIST — Save state to DuckDB (HOLD₂)
6. WAIT — Sleep until next heartbeat

The daemon runs forever. It doesn't ask. It observes.
It doesn't wait for input. It catches what already exists.

"I just want everything I already have to give me back."
— Jeremy Serna
"""

from __future__ import annotations

import asyncio
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from truth_forge.daemon.service import DaemonConfig, TruthForgeDaemon
from truth_forge.memory.capability_manifest import CapabilityManifest
from truth_forge.pipeline.cascade import CascadeConfig, CascadePipeline, CascadeResult
from truth_forge.pipeline.signals import (
    LifeSignal,
    SignalCollector,
    SignalSource,
)
from truth_forge.schema.event import EventType
from truth_forge.services.base import BaseService
from truth_forge.services.factory import register_service


logger = structlog.get_logger(service="genesis_heartbeat")


@dataclass
class HeartbeatConfig:
    """Configuration for the Genesis Heartbeat.

    Attributes:
        heartbeat_interval: Seconds between heartbeat cycles.
        watch_paths: Directories to watch for file changes.
        browser_lookback_minutes: How far back to check browser history.
        cascade_config: Configuration for the cascade pipeline.
        daemon_port: Port for the HTTP status endpoint.
        enable_browser: Whether to observe browser activity.
        enable_files: Whether to observe file changes.
        enable_system: Whether to observe system state.
    """

    heartbeat_interval: int = 60
    watch_paths: list[Path] = field(default_factory=list)
    browser_lookback_minutes: int = 30
    cascade_config: CascadeConfig = field(default_factory=CascadeConfig)
    daemon_port: int = 8765
    enable_browser: bool = True
    enable_files: bool = True
    enable_system: bool = True


@dataclass
class HeartbeatState:
    """Current state of the heartbeat daemon.

    Attributes:
        started_at: When the daemon started.
        cycle_count: Number of heartbeat cycles completed.
        last_cycle_at: When the last cycle ran.
        total_signals_processed: Cumulative signals processed.
        total_atoms_created: Cumulative atoms extracted.
        total_insights: Cumulative insights synthesized.
        total_narratives: Cumulative narratives forged.
        last_cascade_result: Result from the most recent cascade.
        is_running: Whether the daemon is currently running.
        errors: Recent errors (last 10).
    """

    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    cycle_count: int = 0
    last_cycle_at: datetime | None = None
    total_signals_processed: int = 0
    total_atoms_created: int = 0
    total_insights: int = 0
    total_narratives: int = 0
    last_cascade_result: dict[str, Any] | None = None
    is_running: bool = False
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for status endpoint."""
        return {
            "started_at": self.started_at.isoformat(),
            "cycle_count": self.cycle_count,
            "last_cycle_at": self.last_cycle_at.isoformat() if self.last_cycle_at else None,
            "uptime_seconds": (datetime.now(UTC) - self.started_at).total_seconds(),
            "total_signals_processed": self.total_signals_processed,
            "total_atoms_created": self.total_atoms_created,
            "total_insights": self.total_insights,
            "total_narratives": self.total_narratives,
            "last_cascade_result": self.last_cascade_result,
            "is_running": self.is_running,
            "recent_errors": self.errors[-5:],
        }


@register_service()
class GenesisHeartbeat(BaseService):
    """The Genesis Heartbeat — NOT-ME's autonomic nervous system.

    Inherits BaseService for HOLD pattern compliance.
    Composes TruthForgeDaemon for HTTP endpoints.
    Observes Jeremy's life. Metabolizes into knowledge.
    Proves capabilities through demonstration.
    """

    service_name = "heartbeat"

    def on_startup(self) -> None:
        """Initialize heartbeat components."""
        self._config = HeartbeatConfig()
        self._hb_state = HeartbeatState()
        self._manifest = CapabilityManifest()
        self._stop_event = threading.Event()
        self._heartbeat_thread: threading.Thread | None = None

        # Default watch paths
        from truth_forge.core.paths import PROJECT_ROOT

        if not self._config.watch_paths:
            self._config.watch_paths = [
                PROJECT_ROOT / "docs",
                PROJECT_ROOT / "framework",
            ]

        # Initialize signal collector
        self._collector = SignalCollector(
            watch_paths=self._config.watch_paths,
            browser_lookback_minutes=self._config.browser_lookback_minutes,
        )

        # Initialize cascade pipeline
        self._cascade = CascadePipeline(self._config.cascade_config)

        # Track processed signal IDs for dedup
        self._processed_signals: set[str] = set()

        self.logger.info(
            "genesis_heartbeat_initialized",
            watch_paths=[str(p) for p in self._config.watch_paths],
            heartbeat_interval=self._config.heartbeat_interval,
        )

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Process a heartbeat record (AGENT logic).

        This is called during sync() to process HOLD₁ records.

        Args:
            record: A heartbeat event record.

        Returns:
            Processed record with results.
        """
        record["processed_at"] = datetime.now(UTC).isoformat()
        record["cycle_count"] = self._hb_state.cycle_count
        return record

    def create_schema(self) -> str:
        """Create DuckDB schema for heartbeat HOLD₂."""
        return """
            CREATE TABLE IF NOT EXISTS heartbeat_records (
                id VARCHAR PRIMARY KEY,
                data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

    # =========================================================================
    # Heartbeat Loop
    # =========================================================================

    def start_heartbeat(self) -> None:
        """Start the heartbeat loop in a background thread."""
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self.logger.warning("heartbeat_already_running")
            return

        self._stop_event.clear()
        self._hb_state.is_running = True

        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True,
            name="genesis-heartbeat",
        )
        self._heartbeat_thread.start()

        self.logger.info("heartbeat_started")

    def stop_heartbeat(self) -> None:
        """Stop the heartbeat loop."""
        self._stop_event.set()
        self._hb_state.is_running = False

        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=10)

        self.logger.info("heartbeat_stopped")

    def _heartbeat_loop(self) -> None:
        """The main heartbeat loop. Runs forever until stopped."""
        self.logger.info("heartbeat_loop_entered")

        while not self._stop_event.is_set():
            try:
                # Run one heartbeat cycle
                asyncio.run(self._heartbeat_cycle())
            except Exception as e:
                error_msg = f"Heartbeat cycle failed: {e}"
                self._hb_state.errors.append(error_msg)
                # Keep only last 20 errors
                if len(self._hb_state.errors) > 20:
                    self._hb_state.errors = self._hb_state.errors[-20:]
                self.logger.error(
                    "heartbeat_cycle_failed",
                    error=str(e),
                    cycle=self._hb_state.cycle_count,
                )

            # Wait for next cycle
            self._stop_event.wait(self._config.heartbeat_interval)

    async def _heartbeat_cycle(self) -> None:
        """Execute one complete heartbeat cycle.

        GATHER → FILTER → CASCADE → PROVE → PERSIST
        """
        cycle_start = time.time()
        self._hb_state.cycle_count += 1
        self._hb_state.last_cycle_at = datetime.now(UTC)

        self.logger.info(
            "heartbeat_cycle_started",
            cycle=self._hb_state.cycle_count,
        )

        # 1. GATHER — Collect life signals
        signals = self._gather_signals()

        if not signals:
            self.logger.debug(
                "heartbeat_cycle_idle",
                cycle=self._hb_state.cycle_count,
            )
            return

        # 2. FILTER — Deduplicate
        new_signals = self._filter_signals(signals)

        if not new_signals:
            self.logger.debug(
                "heartbeat_cycle_no_new_signals",
                cycle=self._hb_state.cycle_count,
                total_seen=len(signals),
            )
            return

        # 3. INHALE — Write signals to HOLD₁
        for signal in new_signals:
            self.inhale(
                data=signal.to_dict(),
                event_type=EventType.RECORD_CREATED,
            )

        self._hb_state.total_signals_processed += len(new_signals)

        # 4. CASCADE — Run the full pipeline
        cascade_result = await self._run_cascade(new_signals)

        # 5. PROVE — Record capabilities in the manifest
        self._record_proofs(new_signals, cascade_result)

        # 6. PERSIST — Write results to HOLD₂
        self._persist_results(cascade_result, new_signals)

        cycle_duration = time.time() - cycle_start

        self.logger.info(
            "heartbeat_cycle_completed",
            cycle=self._hb_state.cycle_count,
            signals=len(new_signals),
            atoms=cascade_result.atoms_created,
            insights=cascade_result.insights_generated,
            narratives=cascade_result.narratives_forged,
            duration_seconds=round(cycle_duration, 2),
        )

    # =========================================================================
    # Cycle Steps
    # =========================================================================

    def _gather_signals(self) -> list[LifeSignal]:
        """Step 1: Gather life signals from all sources.

        Returns:
            All gathered signals, sorted by priority.
        """
        start = time.time()
        signals = self._collector.collect_all()
        duration = time.time() - start

        # Prove observation capabilities
        file_signals = [s for s in signals if s.source == SignalSource.FILE_CHANGE]
        browser_signals = [s for s in signals if s.source == SignalSource.BROWSER]
        system_signals = [s for s in signals if s.source == SignalSource.SYSTEM]

        if file_signals:
            self._manifest.prove(
                "observe_files",
                f"Detected {len(file_signals)} file changes",
                success=True,
                duration_seconds=duration,
            )

        if browser_signals:
            self._manifest.prove(
                "observe_browser",
                f"Observed {len(browser_signals)} browser visits",
                success=True,
                duration_seconds=duration,
            )

        if system_signals:
            self._manifest.prove(
                "check_models",
                f"Checked {len(system_signals)} system sensors",
                success=True,
                duration_seconds=duration,
            )

        return signals

    def _filter_signals(self, signals: list[LifeSignal]) -> list[LifeSignal]:
        """Step 2: Filter out already-processed signals.

        Args:
            signals: Raw signals from collectors.

        Returns:
            Only signals not yet processed.
        """
        new_signals = [s for s in signals if s.id not in self._processed_signals]

        # Mark as processed
        for signal in new_signals:
            self._processed_signals.add(signal.id)

        # Prevent unbounded growth of processed set
        if len(self._processed_signals) > 10000:
            # Keep only the most recent 5000
            self._processed_signals = set(list(self._processed_signals)[-5000:])

        return new_signals

    async def _run_cascade(self, signals: list[LifeSignal]) -> CascadeResult:
        """Step 4: Run the cascade pipeline.

        Args:
            signals: Filtered life signals to process.

        Returns:
            CascadeResult with metrics.
        """
        start = time.time()

        try:
            result = await self._cascade.run(signals)
            duration = time.time() - start

            # Update state
            self._hb_state.total_atoms_created += result.atoms_created
            self._hb_state.total_insights += result.insights_generated
            self._hb_state.total_narratives += result.narratives_forged
            self._hb_state.last_cascade_result = result.to_dict()

            # Prove cascade capabilities
            if result.atoms_created > 0:
                self._manifest.prove(
                    "atomize_knowledge",
                    f"Extracted {result.atoms_created} atoms from {len(signals)} signals",
                    success=True,
                    duration_seconds=duration,
                )

            if result.insights_generated > 0:
                self._manifest.prove(
                    "synthesize_insights",
                    f"Generated {result.insights_generated} insights",
                    success=True,
                    duration_seconds=duration,
                )

            if result.narratives_forged > 0:
                self._manifest.prove(
                    "forge_narratives",
                    f"Forged {result.narratives_forged} narratives",
                    success=True,
                    duration_seconds=duration,
                )

            if result.cycles > 0:
                self._manifest.prove(
                    "cascade_pipeline",
                    f"Completed {result.cycles} cascade cycles",
                    success=True,
                    duration_seconds=duration,
                )

            if result.saturated:
                self._manifest.prove(
                    "detect_saturation",
                    f"Detected saturation at cycle {result.cycles}",
                    success=True,
                    duration_seconds=duration,
                )

            return result

        except Exception as e:
            duration = time.time() - start
            self._manifest.prove(
                "cascade_pipeline",
                f"Cascade failed: {e}",
                success=False,
                duration_seconds=duration,
                error=str(e),
            )
            raise

    def _record_proofs(
        self,
        signals: list[LifeSignal],
        result: CascadeResult,
    ) -> None:
        """Step 5: Record capability proofs based on results.

        Args:
            signals: Processed signals.
            result: Cascade results.
        """
        # Already handled in _gather_signals and _run_cascade
        # This method is for any additional proof recording
        pass

    def _persist_results(
        self,
        result: CascadeResult,
        signals: list[LifeSignal],
    ) -> None:
        """Step 6: Persist results to HOLD₂.

        Args:
            result: Cascade results.
            signals: Processed signals.
        """
        try:
            # Write cascade result to HOLD₂ via exhale
            self.exhale(
                processed_data={
                    "cycle": self._hb_state.cycle_count,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "signal_count": len(signals),
                    "cascade_result": result.to_dict(),
                    "manifest_summary": self._manifest.summary(),
                },
            )

            self._manifest.prove(
                "persist_memory",
                f"Persisted cycle {self._hb_state.cycle_count} results",
                success=True,
            )
        except Exception as e:
            self._manifest.prove(
                "persist_memory",
                f"Persist failed: {e}",
                success=False,
                error=str(e),
            )
            self.logger.error(
                "persist_failed",
                error=str(e),
                cycle=self._hb_state.cycle_count,
            )

    # =========================================================================
    # Status
    # =========================================================================

    def get_status(self) -> dict[str, Any]:
        """Get full heartbeat status.

        Returns:
            Dictionary with state, manifest summary, and health.
        """
        return {
            "heartbeat": self._hb_state.to_dict(),
            "manifest": self._manifest.summary(),
            "health": self.health_check(),
        }


def run_genesis(
    heartbeat_interval: int = 60,
    watch_paths: list[str] | None = None,
    port: int = 8765,
) -> None:
    """Run the Genesis Heartbeat daemon.

    Convenience function for starting the daemon.

    Args:
        heartbeat_interval: Seconds between heartbeat cycles.
        watch_paths: Directories to watch (as strings).
        port: HTTP status endpoint port.
    """
    heartbeat = GenesisHeartbeat()
    heartbeat._config.heartbeat_interval = heartbeat_interval

    if watch_paths:
        heartbeat._config.watch_paths = [Path(p) for p in watch_paths]

    # Start the HTTP daemon for status endpoints
    daemon_config = DaemonConfig(port=port)
    daemon = TruthForgeDaemon(daemon_config)

    # Start heartbeat loop
    heartbeat.start_heartbeat()

    # Run HTTP server (blocking)
    try:
        daemon.start()
    except KeyboardInterrupt:
        pass
    finally:
        heartbeat.stop_heartbeat()
        daemon.stop()


__all__ = [
    "GenesisHeartbeat",
    "HeartbeatConfig",
    "HeartbeatState",
    "run_genesis",
]
