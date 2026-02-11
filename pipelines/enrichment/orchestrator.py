#!/usr/bin/env python3
"""Autonomous Enrichment Orchestrator.

THE PATTERN:
- HOLD₁: Enrichment queue and state
- AGENT: Orchestrator (cycles through enrichments automatically)
- HOLD₂: Enriched entities in BigQuery

This runs autonomously. Start it and walk away.
It will cycle through all enrichments, handle failures, and keep going.

Usage:
    python pipelines/enrichment/orchestrator.py          # Run forever
    python pipelines/enrichment/orchestrator.py --once   # One full cycle
    python pipelines/enrichment/orchestrator.py --status # Show status

Stop gracefully with Ctrl+C or:
    kill -TERM $(cat /tmp/enrichment_orchestrator.pid)
"""

from __future__ import annotations

import json
import logging
import os
import signal
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Ensure logs directory exists before setting up logging
(PROJECT_ROOT / "logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(PROJECT_ROOT / "logs" / "orchestrator.log"),
    ],
)
logger = logging.getLogger("orchestrator")


# Enrichment definitions - order matters (dependencies)
ENRICHMENTS = [
    # Phase 1: Foundation (CPU-only, fast)
    {
        "name": "textblob",
        "script": "enrichment_textblob.py",
        "phase": 1,
        "requires_gpu": False,
        "priority": 1,
    },
    {
        "name": "textstat",
        "script": "enrichment_textstat.py",
        "phase": 1,
        "requires_gpu": False,
        "priority": 2,
    },
    {
        "name": "nrclx",
        "script": "enrichment_nrclx.py",
        "phase": 1,
        "requires_gpu": False,
        "priority": 3,
    },
    # Phase 2: Sovereign (CPU-only, critical for training)
    {
        "name": "cognitive_stage",
        "script": "enrichment_cognitive_stage.py",
        "phase": 2,
        "requires_gpu": False,
        "priority": 4,
    },
    {
        "name": "confidence",
        "script": "enrichment_confidence.py",
        "phase": 2,
        "requires_gpu": False,
        "priority": 6,
    },
    {
        "name": "source_attribution",
        "script": "enrichment_source_attribution.py",
        "phase": 2,
        "requires_gpu": False,
        "priority": 7,
    },
    # Phase 3: GPU-based (optional, skip if no GPU)
    {
        "name": "goemotions",
        "script": "enrichment_goemotions.py",
        "phase": 3,
        "requires_gpu": True,
        "priority": 8,
        "extra_args": ["--batch-size", "32"],
    },
    {
        "name": "roberta_hate",
        "script": "enrichment_roberta_hate.py",
        "phase": 3,
        "requires_gpu": True,
        "priority": 9,
        "extra_args": ["--batch-size", "32"],
    },
]

# Orchestrator config
STATE_FILE = PROJECT_ROOT / "checkpoints" / "orchestrator_state.json"
PID_FILE = Path("/tmp/enrichment_orchestrator.pid")
LEVELS = "4,5"
PAGE_SIZE = 5000
CYCLE_PAUSE_MINUTES = 5  # Pause between cycles


@dataclass
class OrchestratorState:
    """Persistent state for the orchestrator."""

    current_enrichment_idx: int = 0
    cycle_count: int = 0
    total_processed: int = 0
    total_written: int = 0
    total_failed: int = 0
    started_at: str = ""
    last_update: str = ""
    last_enrichment: str = ""
    last_status: str = ""
    running: bool = False
    enrichments_completed_this_cycle: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrchestratorState":
        # Handle missing fields gracefully
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    def save(self) -> None:
        self.last_update = datetime.utcnow().isoformat()
        STATE_FILE.parent.mkdir(exist_ok=True)
        STATE_FILE.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls) -> "OrchestratorState":
        if STATE_FILE.exists():
            try:
                return cls.from_dict(json.loads(STATE_FILE.read_text()))
            except Exception as e:
                logger.warning(f"Failed to load state: {e}")
        return cls()


class Orchestrator:
    """Autonomous enrichment orchestrator."""

    def __init__(self, run_once: bool = False, skip_gpu: bool = True) -> None:
        self.run_once = run_once
        self.skip_gpu = skip_gpu
        self.state = OrchestratorState.load()
        self.shutdown_requested = False
        self._setup_signal_handlers()

        # Ensure directories exist
        (PROJECT_ROOT / "logs").mkdir(exist_ok=True)
        (PROJECT_ROOT / "checkpoints").mkdir(exist_ok=True)
        (PROJECT_ROOT / "dlq").mkdir(exist_ok=True)

    def _setup_signal_handlers(self) -> None:
        def handle_signal(signum: int, _frame: Any) -> None:
            logger.info(f"Shutdown requested (signal {signum})")
            self.shutdown_requested = True

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

    def _write_pid(self) -> None:
        PID_FILE.write_text(str(os.getpid()))

    def _clear_pid(self) -> None:
        if PID_FILE.exists():
            PID_FILE.unlink()

    def _get_enrichments_to_run(self) -> list[dict[str, Any]]:
        """Get list of enrichments to run (filter out missing scripts and GPU if needed)."""
        enrichments = []
        for e in ENRICHMENTS:
            script_path = PROJECT_ROOT / "pipelines" / "enrichment" / e["script"]
            if not script_path.exists():
                logger.debug(f"Skipping {e['name']} - script not found")
                continue
            if self.skip_gpu and e.get("requires_gpu", False):
                logger.debug(f"Skipping {e['name']} - requires GPU")
                continue
            enrichments.append(e)
        return enrichments

    def _run_enrichment(self, enrichment: dict[str, Any]) -> bool:
        """Run a single enrichment script. Returns True if successful."""
        script = enrichment["script"]
        name = enrichment["name"]
        extra_args = enrichment.get("extra_args", [])

        script_path = PROJECT_ROOT / "pipelines" / "enrichment" / script

        cmd = [
            sys.executable,
            str(script_path),
            "--level", LEVELS,
            "--mode", "null-only",
            "--progress",
            "--production",
            "--page-size", str(PAGE_SIZE),
            "--resume",  # Always try to resume
        ]

        cmd.extend(extra_args)

        logger.info(f">>> Starting: {name}")
        self.state.last_enrichment = name
        self.state.last_status = "running"
        self.state.save()

        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(PROJECT_ROOT) + ":" + env.get("PYTHONPATH", "")

            result = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=3600 * 4,  # 4 hour timeout per enrichment
            )

            if result.returncode == 0:
                logger.info(f"<<< {name}: SUCCESS")
                self.state.last_status = "success"
                self.state.enrichments_completed_this_cycle += 1
                return True
            else:
                logger.error(f"<<< {name}: FAILED (code {result.returncode})")
                if result.stderr:
                    # Log last 500 chars of stderr
                    logger.error(f"    Error: {result.stderr[-500:]}")
                self.state.last_status = "failed"
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"<<< {name}: TIMEOUT (4 hours)")
            self.state.last_status = "timeout"
            return False
        except Exception as e:
            logger.error(f"<<< {name}: ERROR - {e}")
            self.state.last_status = "error"
            return False

    def _run_cycle(self) -> int:
        """Run one full cycle through all enrichments. Returns count of successful runs."""
        enrichments = self._get_enrichments_to_run()
        if not enrichments:
            logger.warning("No enrichments available to run!")
            return 0

        self.state.enrichments_completed_this_cycle = 0
        logger.info(f"=" * 60)
        logger.info(f"CYCLE {self.state.cycle_count + 1}: {len(enrichments)} enrichments")
        logger.info(f"=" * 60)

        for i, enrichment in enumerate(enrichments):
            if self.shutdown_requested:
                logger.info("Shutdown requested, stopping cycle")
                break

            self.state.current_enrichment_idx = i
            self.state.save()

            success = self._run_enrichment(enrichment)

            if not success:
                # Brief delay before next to avoid hammering on errors
                time.sleep(5)

            # Brief pause between enrichments
            if not self.shutdown_requested:
                time.sleep(2)

        self.state.cycle_count += 1
        self.state.current_enrichment_idx = 0
        completed = self.state.enrichments_completed_this_cycle
        self.state.save()

        logger.info(f"=" * 60)
        logger.info(f"CYCLE {self.state.cycle_count} COMPLETE: {completed}/{len(enrichments)} succeeded")
        logger.info(f"=" * 60)

        return completed

    def run(self) -> None:
        """Main orchestrator loop."""
        self._write_pid()
        self.state.running = True
        self.state.started_at = datetime.utcnow().isoformat()
        self.state.save()

        logger.info("")
        logger.info("=" * 60)
        logger.info("   ENRICHMENT ORCHESTRATOR STARTED")
        logger.info("=" * 60)
        logger.info(f"PID: {os.getpid()}")
        logger.info(f"Levels: {LEVELS}")
        logger.info(f"Mode: {'single cycle' if self.run_once else 'continuous'}")
        logger.info(f"GPU: {'enabled' if not self.skip_gpu else 'skipped'}")
        logger.info(f"State file: {STATE_FILE}")
        logger.info(f"Log file: {PROJECT_ROOT / 'logs' / 'orchestrator.log'}")
        logger.info("=" * 60)
        logger.info("")

        try:
            if self.run_once:
                self._run_cycle()
            else:
                while not self.shutdown_requested:
                    completed = self._run_cycle()

                    if self.shutdown_requested:
                        break

                    # If nothing was processed this cycle, backfill might be complete
                    # Increase pause time
                    if completed == 0:
                        pause = CYCLE_PAUSE_MINUTES * 2
                        logger.info(f"No work done. Pausing {pause} minutes...")
                    else:
                        pause = CYCLE_PAUSE_MINUTES
                        logger.info(f"Pausing {pause} minutes before next cycle...")

                    # Interruptible sleep
                    for _ in range(pause * 60):
                        if self.shutdown_requested:
                            break
                        time.sleep(1)

        except Exception as e:
            logger.error(f"Orchestrator error: {e}", exc_info=True)
        finally:
            self.state.running = False
            self.state.save()
            self._clear_pid()
            logger.info("Orchestrator stopped")

    @classmethod
    def status(cls) -> None:
        """Print current status."""
        state = OrchestratorState.load()

        print("\n" + "=" * 60)
        print("ENRICHMENT ORCHESTRATOR STATUS")
        print("=" * 60)

        if PID_FILE.exists():
            pid = PID_FILE.read_text().strip()
            try:
                os.kill(int(pid), 0)
                print(f"Status: RUNNING (PID {pid})")
            except ProcessLookupError:
                print("Status: STOPPED (stale PID file)")
        else:
            print("Status: STOPPED")

        print(f"Cycles completed: {state.cycle_count}")
        print(f"Current enrichment: {state.last_enrichment or 'none'}")
        print(f"Last status: {state.last_status or 'none'}")
        print(f"Started: {state.started_at or 'never'}")
        print(f"Last update: {state.last_update or 'never'}")

        # Show checkpoint files
        checkpoint_dir = PROJECT_ROOT / "checkpoints"
        if checkpoint_dir.exists():
            checkpoints = [f for f in checkpoint_dir.glob("*.json") if f.name != "orchestrator_state.json"]
            if checkpoints:
                print(f"\nActive enrichment checkpoints: {len(checkpoints)}")
                for cp in sorted(checkpoints)[:5]:
                    print(f"  - {cp.name}")
                if len(checkpoints) > 5:
                    print(f"  ... and {len(checkpoints) - 5} more")

        # Show available enrichments
        print("\nAvailable enrichments:")
        for e in ENRICHMENTS:
            script_path = PROJECT_ROOT / "pipelines" / "enrichment" / e["script"]
            exists = "✓" if script_path.exists() else "✗"
            gpu = " (GPU)" if e.get("requires_gpu") else ""
            print(f"  {exists} {e['name']}{gpu}")

        print("=" * 60 + "\n")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Autonomous Enrichment Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python orchestrator.py              # Run continuously
  python orchestrator.py --once       # Run one cycle and exit
  python orchestrator.py --status     # Show status
  python orchestrator.py --with-gpu   # Include GPU enrichments

To stop gracefully:
  Ctrl+C or: kill -TERM $(cat /tmp/enrichment_orchestrator.pid)
        """,
    )
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--status", action="store_true", help="Show status and exit")
    parser.add_argument("--with-gpu", action="store_true", help="Include GPU enrichments")

    args = parser.parse_args()

    if args.status:
        Orchestrator.status()
        return

    orchestrator = Orchestrator(
        run_once=args.once,
        skip_gpu=not args.with_gpu,
    )
    orchestrator.run()


if __name__ == "__main__":
    main()
