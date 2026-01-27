"""Daemon - Background Service.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/daemon/__init__.py
- Version: 2.0.0
- Date: 2026-01-26

Background service for truth_forge operations.

BIOLOGICAL METAPHOR:
- Daemon = Autonomic nervous system
- Heartbeat = Respiratory rhythm
- API = Reflex arc

Example:
    from truth_forge.daemon import TruthForgeDaemon

    daemon = TruthForgeDaemon()
    daemon.start()
"""

from __future__ import annotations

from truth_forge.daemon.service import TruthForgeDaemon


__all__ = [
    "TruthForgeDaemon",
]
