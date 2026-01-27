"""Daemon Service - Background Operations.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/daemon/truth_engine_daemon.py
- Version: 2.0.0
- Date: 2026-01-26

Provides background service for truth_forge operations.

Features:
- Health endpoint
- Status reporting
- Heartbeat broadcasting
- Governance integration

Example:
    daemon = TruthForgeDaemon(port=8080)
    daemon.start()  # Blocking
"""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, ClassVar
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


@dataclass
class DaemonConfig:
    """Configuration for the daemon.

    Attributes:
        host: Host to bind to.
        port: Port to listen on.
        heartbeat_interval: Seconds between heartbeats.
        enable_governance: Whether to enable governance checks.
    """

    host: str = "127.0.0.1"
    port: int = 8765
    heartbeat_interval: int = 30
    enable_governance: bool = True


@dataclass
class DaemonStatus:
    """Current daemon status.

    Attributes:
        started_at: When daemon started.
        heartbeat_count: Number of heartbeats sent.
        last_heartbeat: Time of last heartbeat.
        is_healthy: Whether daemon is healthy.
    """

    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    heartbeat_count: int = 0
    last_heartbeat: datetime | None = None
    is_healthy: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "started_at": self.started_at.isoformat(),
            "heartbeat_count": self.heartbeat_count,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "is_healthy": self.is_healthy,
            "uptime_seconds": (datetime.now(UTC) - self.started_at).total_seconds(),
        }


class TruthForgeDaemon:
    """Background service for truth_forge.

    The daemon provides:
    1. Health check endpoint (/health)
    2. Status endpoint (/status)
    3. Heartbeat broadcasting
    4. Governance integration

    BIOLOGICAL METAPHOR:
    - Daemon = Autonomic nervous system
    - Heartbeat = Cardiac rhythm
    - Endpoints = Sensory receptors

    Example:
        daemon = TruthForgeDaemon()

        # Start in background thread
        daemon.start_async()

        # Later, stop
        daemon.stop()
    """

    VERSION: ClassVar[str] = "2.0.0"

    def __init__(self, config: DaemonConfig | None = None) -> None:
        """Initialize the daemon.

        Args:
            config: Daemon configuration.
        """
        self.config = config or DaemonConfig()
        self.status = DaemonStatus()
        self._server: HTTPServer | None = None
        self._heartbeat_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

        logger.info(
            "TruthForgeDaemon initialized",
            extra={"host": self.config.host, "port": self.config.port},
        )

    def start(self) -> None:
        """Start the daemon (blocking).

        This method blocks until stop() is called.
        """
        logger.info("Starting TruthForgeDaemon")

        # Start heartbeat thread
        self._start_heartbeat()

        # Create request handler with reference to daemon
        daemon = self

        class Handler(BaseHTTPRequestHandler):
            """HTTP request handler."""

            def log_message(self, format: str, *args: Any) -> None:
                """Log an HTTP request."""
                logger.debug(format % args)

            def do_GET(self) -> None:
                """Handle GET request."""
                parsed = urlparse(self.path)
                path = parsed.path

                if path == "/health":
                    self._respond_json({"status": "healthy", "version": daemon.VERSION})
                elif path == "/status":
                    self._respond_json(daemon.status.to_dict())
                elif path == "/":
                    self._respond_json(
                        {
                            "name": "truth_forge daemon",
                            "version": daemon.VERSION,
                            "endpoints": ["/health", "/status"],
                        }
                    )
                else:
                    self._respond_error(404, "Not found")

            def _respond_json(self, data: dict[str, Any]) -> None:
                """Send JSON response."""
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())

            def _respond_error(self, code: int, message: str) -> None:
                """Send error response."""
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": message}).encode())

        # Start HTTP server
        self._server = HTTPServer((self.config.host, self.config.port), Handler)
        logger.info(
            "Daemon listening",
            extra={"host": self.config.host, "port": self.config.port},
        )

        try:
            self._server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def start_async(self) -> threading.Thread:
        """Start the daemon in a background thread.

        Returns:
            The thread running the daemon.
        """
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        return thread

    def stop(self) -> None:
        """Stop the daemon."""
        logger.info("Stopping TruthForgeDaemon")

        self._stop_event.set()

        if self._server:
            self._server.shutdown()
            self._server = None

        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=5)

        self.status.is_healthy = False

    def _start_heartbeat(self) -> None:
        """Start the heartbeat thread."""

        def heartbeat_loop() -> None:
            while not self._stop_event.is_set():
                self._send_heartbeat()
                self._stop_event.wait(self.config.heartbeat_interval)

        self._heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def _send_heartbeat(self) -> None:
        """Send a heartbeat signal."""
        self.status.heartbeat_count += 1
        self.status.last_heartbeat = datetime.now(UTC)

        logger.debug(
            "Heartbeat",
            extra={
                "count": self.status.heartbeat_count,
                "timestamp": self.status.last_heartbeat.isoformat(),
            },
        )

    @property
    def is_running(self) -> bool:
        """Check if daemon is running.

        Returns:
            True if running.
        """
        return self._server is not None and not self._stop_event.is_set()


def run_daemon(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Run the daemon.

    Convenience function for running the daemon.

    Args:
        host: Host to bind to.
        port: Port to listen on.
    """
    config = DaemonConfig(host=host, port=port)
    daemon = TruthForgeDaemon(config)
    daemon.start()


__all__ = [
    "DaemonConfig",
    "DaemonStatus",
    "TruthForgeDaemon",
    "run_daemon",
]
