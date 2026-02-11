"""Life Signal Sources — Jeremy's life IS the input stream.

NOT-ME observes Jeremy existing. Every signal source represents
a way Jeremy's life generates data that NOT-ME metabolizes.

Signal sources:
- FileWatcher: New/changed files in watched directories
- BrowserSignal: Browser history via truth-browser-logger MCP
- SystemSensor: Hardware metrics, model availability
- ConversationSignal: Claude Code sessions, chat logs

Each signal becomes a LifeSignal that enters the cascade pipeline.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

import structlog


logger = structlog.get_logger(service="signals")


class SignalSource(str, Enum):
    """Where a life signal originated."""

    FILE_CHANGE = "file_change"
    BROWSER = "browser"
    SYSTEM = "system"
    CONVERSATION = "conversation"
    CALENDAR = "calendar"
    MANUAL = "manual"


class SignalPriority(int, Enum):
    """How urgently this signal should be processed."""

    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class LifeSignal:
    """A single observation from Jeremy's life.

    Attributes:
        id: Unique signal identifier (content hash).
        source: Where the signal came from.
        content: The raw signal content.
        timestamp: When the signal was observed.
        priority: Processing priority.
        metadata: Additional context about the signal.
    """

    source: SignalSource
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    priority: SignalPriority = SignalPriority.NORMAL
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = ""

    def __post_init__(self) -> None:
        """Generate content-based ID for idempotency."""
        if not self.id:
            content_hash = hashlib.sha256(
                f"{self.source.value}:{self.content}".encode()
            ).hexdigest()[:16]
            self.id = f"sig_{content_hash}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for HOLD₁ intake."""
        return {
            "id": self.id,
            "source": self.source.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "metadata": self.metadata,
        }


class FileWatcher:
    """Watch directories for new/changed files.

    Jeremy's file activity IS architecture activity.
    New documents, changed code, modified configs — all signals.
    """

    def __init__(self, watch_paths: list[Path]) -> None:
        """Initialize with paths to watch.

        Args:
            watch_paths: Directories to monitor for changes.
        """
        self.watch_paths = watch_paths
        self._last_scan: dict[str, float] = {}
        self._logger = structlog.get_logger(service="file_watcher")

    def scan(self) -> list[LifeSignal]:
        """Scan watched directories for new/changed files.

        Returns:
            List of LifeSignals for detected changes.
        """
        signals: list[LifeSignal] = []

        for watch_path in self.watch_paths:
            if not watch_path.exists():
                self._logger.warning(
                    "watch_path_missing",
                    path=str(watch_path),
                )
                continue

            for file_path in watch_path.rglob("*"):
                if not file_path.is_file():
                    continue

                # Skip hidden files, __pycache__, node_modules, .git
                parts = file_path.parts
                if any(
                    p.startswith(".") or p in ("__pycache__", "node_modules", ".git") for p in parts
                ):
                    continue

                # Skip binary files
                suffix = file_path.suffix.lower()
                if suffix in (
                    ".pyc",
                    ".pyo",
                    ".so",
                    ".dylib",
                    ".dll",
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".gif",
                    ".ico",
                    ".mp3",
                    ".mp4",
                    ".wav",
                    ".ogg",
                    ".zip",
                    ".tar",
                    ".gz",
                    ".bz2",
                    ".db",
                    ".duckdb",
                    ".sqlite",
                ):
                    continue

                str_path = str(file_path)
                try:
                    mtime = file_path.stat().st_mtime
                except OSError:
                    continue

                last_seen = self._last_scan.get(str_path, 0.0)

                if mtime > last_seen:
                    # File is new or changed
                    try:
                        content = file_path.read_text(errors="replace")
                        # Truncate large files to first 10K chars for signal
                        if len(content) > 10000:
                            content = content[:10000] + "\n[... truncated ...]"
                    except (OSError, UnicodeDecodeError):
                        content = f"[Binary or unreadable file: {file_path.name}]"

                    signal = LifeSignal(
                        source=SignalSource.FILE_CHANGE,
                        content=content,
                        priority=self._classify_priority(file_path),
                        metadata={
                            "file_path": str_path,
                            "file_name": file_path.name,
                            "file_suffix": suffix,
                            "file_size": file_path.stat().st_size,
                            "is_new": last_seen == 0.0,
                        },
                    )
                    signals.append(signal)
                    self._last_scan[str_path] = mtime

        if signals:
            self._logger.info(
                "files_detected",
                count=len(signals),
                new=sum(1 for s in signals if s.metadata.get("is_new")),
                changed=sum(1 for s in signals if not s.metadata.get("is_new")),
            )

        return signals

    def _classify_priority(self, file_path: Path) -> SignalPriority:
        """Classify file priority based on type and location.

        Args:
            file_path: Path to the file.

        Returns:
            Priority level for this file type.
        """
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()

        # Framework files are critical
        if "framework" in str(file_path):
            return SignalPriority.CRITICAL

        # Python source = high priority (code IS architecture)
        if suffix == ".py":
            return SignalPriority.HIGH

        # Markdown docs = normal
        if suffix == ".md":
            return SignalPriority.NORMAL

        # Config files = high
        if suffix in (".yaml", ".yml", ".toml", ".json") and "config" in name:
            return SignalPriority.HIGH

        return SignalPriority.NORMAL


class BrowserSignal:
    """Observe browser history via truth-browser-logger MCP.

    Jeremy browsing IS research activity.
    What he looks at is what he's thinking about.
    """

    def __init__(self, lookback_minutes: int = 30) -> None:
        """Initialize browser signal observer.

        Args:
            lookback_minutes: How far back to check for browser activity.
        """
        self.lookback_minutes = lookback_minutes
        self._last_check: datetime | None = None
        self._logger = structlog.get_logger(service="browser_signal")

    def gather(self) -> list[LifeSignal]:
        """Gather recent browser activity as signals.

        Note: This calls the browser history MCP tool via subprocess.
        Falls back gracefully if MCP is not available.

        Returns:
            List of LifeSignals from browser activity.
        """
        # Browser history is available via MCP server
        # For now, check if the Chrome history DB is accessible directly
        signals: list[LifeSignal] = []

        try:
            import sqlite3

            chrome_history = (
                Path.home()
                / "Library"
                / "Application Support"
                / "Google"
                / "Chrome"
                / "Default"
                / "History"
            )

            if not chrome_history.exists():
                return signals

            # Chrome locks the DB, so copy it first
            import shutil
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
                tmp_path = Path(tmp.name)

            try:
                shutil.copy2(chrome_history, tmp_path)
                conn = sqlite3.connect(str(tmp_path))

                # Get recent visits (Chrome timestamps are microseconds since 1601-01-01)
                # Convert to Unix epoch: subtract 11644473600 seconds
                cutoff_us = (
                    int(time.time()) - (self.lookback_minutes * 60) + 11644473600
                ) * 1000000

                cursor = conn.execute(
                    """
                    SELECT u.url, u.title, v.visit_time
                    FROM urls u
                    JOIN visits v ON u.id = v.url
                    WHERE v.visit_time > ?
                    ORDER BY v.visit_time DESC
                    LIMIT 50
                    """,
                    (cutoff_us,),
                )

                for url, title, visit_time in cursor.fetchall():
                    signal = LifeSignal(
                        source=SignalSource.BROWSER,
                        content=f"{title}\n{url}",
                        priority=SignalPriority.LOW,
                        metadata={
                            "url": url,
                            "title": title or "",
                            "visit_time": visit_time,
                        },
                    )
                    signals.append(signal)

                conn.close()
            finally:
                tmp_path.unlink(missing_ok=True)

        except Exception as e:
            self._logger.debug(
                "browser_signal_unavailable",
                error=str(e),
            )

        if signals:
            self._logger.info(
                "browser_signals_gathered",
                count=len(signals),
            )

        return signals


class SystemSensor:
    """Observe system state — hardware, models, resources.

    The body's vital signs. NOT-ME needs to know its own physical state.
    """

    def __init__(self) -> None:
        """Initialize system sensor."""
        self._logger = structlog.get_logger(service="system_sensor")

    def gather(self) -> list[LifeSignal]:
        """Gather system health signals.

        Returns:
            List of LifeSignals about system state.
        """
        signals: list[LifeSignal] = []

        # Check model availability
        signals.extend(self._check_models())

        return signals

    def _check_models(self) -> list[LifeSignal]:
        """Check if Scout and EXO models are available."""
        signals: list[LifeSignal] = []

        # Check Ollama (Scout)
        try:
            import urllib.request

            req = urllib.request.Request(
                "http://localhost:11434/api/tags",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read().decode())
                models = [m.get("name", "") for m in data.get("models", [])]
                signals.append(
                    LifeSignal(
                        source=SignalSource.SYSTEM,
                        content=f"Ollama available. Models: {', '.join(models)}",
                        priority=SignalPriority.BACKGROUND,
                        metadata={
                            "service": "ollama",
                            "status": "available",
                            "models": models,
                        },
                    )
                )
        except Exception:
            signals.append(
                LifeSignal(
                    source=SignalSource.SYSTEM,
                    content="Ollama unavailable",
                    priority=SignalPriority.HIGH,
                    metadata={
                        "service": "ollama",
                        "status": "unavailable",
                    },
                )
            )

        # Check EXO
        try:
            import urllib.request

            req = urllib.request.Request(
                "http://localhost:8000/v1/models",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read().decode())
                models = [m.get("id", "") for m in data.get("data", [])]
                signals.append(
                    LifeSignal(
                        source=SignalSource.SYSTEM,
                        content=f"EXO available. Models: {', '.join(models)}",
                        priority=SignalPriority.BACKGROUND,
                        metadata={
                            "service": "exo",
                            "status": "available",
                            "models": models,
                        },
                    )
                )
        except Exception:
            signals.append(
                LifeSignal(
                    source=SignalSource.SYSTEM,
                    content="EXO unavailable",
                    priority=SignalPriority.BACKGROUND,
                    metadata={
                        "service": "exo",
                        "status": "unavailable",
                    },
                )
            )

        return signals


class SignalCollector:
    """Collects signals from all sources.

    This is NOT-ME's sensory system. It observes Jeremy's life
    through all available channels and produces LifeSignals
    for the cascade pipeline to process.
    """

    def __init__(
        self,
        watch_paths: list[Path] | None = None,
        browser_lookback_minutes: int = 30,
    ) -> None:
        """Initialize signal collector with all sources.

        Args:
            watch_paths: Directories to watch for file changes.
            browser_lookback_minutes: How far back to check browser history.
        """
        from truth_forge.core.paths import PROJECT_ROOT

        default_watch = [
            PROJECT_ROOT / "docs",
            PROJECT_ROOT / "framework",
        ]

        self.file_watcher = FileWatcher(watch_paths or default_watch)
        self.browser = BrowserSignal(lookback_minutes=browser_lookback_minutes)
        self.system = SystemSensor()
        self._logger = structlog.get_logger(service="signal_collector")

    def collect_all(self) -> list[LifeSignal]:
        """Collect signals from all sources.

        Returns:
            All gathered LifeSignals, sorted by priority.
        """
        all_signals: list[LifeSignal] = []

        # Gather from each source
        sources = [
            ("file_watcher", self.file_watcher.scan),
            ("browser", self.browser.gather),
            ("system", self.system.gather),
        ]

        for source_name, gather_fn in sources:
            try:
                signals = gather_fn()
                all_signals.extend(signals)
            except Exception as e:
                self._logger.error(
                    "signal_collection_failed",
                    source=source_name,
                    error=str(e),
                )

        # Sort by priority (1=critical first)
        all_signals.sort(key=lambda s: s.priority.value)

        self._logger.info(
            "signals_collected",
            total=len(all_signals),
            by_source={
                source.value: sum(1 for s in all_signals if s.source == source)
                for source in SignalSource
                if any(s.source == source for s in all_signals)
            },
        )

        return all_signals
