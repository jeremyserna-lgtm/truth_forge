"""Governance Service - organism self-observation and audit trail.

The governance service records ALL events that occur within the organism,
providing a complete, immutable, and queryable audit trail.

This is the organism's self-awareness mechanism - it observes its own
actions and maintains history.

Usage:
    from truth_forge.services.factory import get_service

    governance = get_service("governance")
    governance.inhale({"event_type": "molt_started", "source": "molt_service", ...})
"""

from truth_forge.services.governance.service import GovernanceService


__all__ = ["GovernanceService"]
