"""Exploration Session State Management.

Manages the state of an exploration session including:
- Configuration
- Findings collected
- InsightAtoms generated
- Resonance metrics
- Should-stop conditions

MOLT LINEAGE:
- Source: New creation for Explorer autonomous data exploration
- Version: 1.0.0
- Date: 2026-02-01
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .models import (
    ExplorationConfig,
    Finding,
    Pattern,
    ResonanceMetrics,
    Significance,
    StruggleState,
)


@dataclass
class ExplorationSession:
    """State for an exploration session.

    Tracks all findings, patterns, and metrics during exploration.
    """

    # Identity (from centralized Event ID)
    id: str
    correlation_id: str

    # Configuration
    config: ExplorationConfig

    # Timing
    started_at: datetime

    # Findings (only SWIMMING + SURPLUS after Struggle Filter)
    findings: list[Finding] = field(default_factory=list)
    discarded_count: int = 0  # DROWNING count

    # Patterns discovered
    patterns: list[Pattern] = field(default_factory=list)

    # InsightAtoms (from SURPLUS findings)
    insight_atoms: list[dict[str, Any]] = field(default_factory=list)

    # Resonance metrics (updated per finding)
    resonance_metrics: ResonanceMetrics = field(default_factory=ResonanceMetrics)

    # Stop conditions
    _should_stop: bool = False
    _stop_reason: str | None = None

    # Iteration tracking
    current_iteration: int = 0
    tools_invoked: int = 0

    @property
    def should_stop(self) -> bool:
        """Check if exploration should stop.

        Returns True if:
        - Manual stop requested
        - Max iterations reached
        - No new findings in last 3 iterations
        - Exist-Now state achieved (Total Resonance >= 0.9)
        """
        if self._should_stop:
            return True

        # Check if we've achieved very high resonance
        if self.resonance_metrics.total_resonance_score >= 0.9:
            self._stop_reason = "Exist-Now achieved (resonance >= 0.9)"
            return True

        return False

    @property
    def stop_reason(self) -> str | None:
        """Get reason for stopping."""
        return self._stop_reason

    def request_stop(self, reason: str) -> None:
        """Request exploration to stop.

        Args:
            reason: Reason for stopping.
        """
        self._should_stop = True
        self._stop_reason = reason

    def add_finding(self, finding: Finding, struggle_state: StruggleState) -> None:
        """Add a finding with Struggle Filter applied.

        Args:
            finding: The finding to add.
            struggle_state: Struggle state from filter.
        """
        if struggle_state == StruggleState.DROWNING:
            self.discarded_count += 1
            return

        self.findings.append(finding)
        self._update_resonance_metrics(finding, struggle_state)

        # SURPLUS findings become InsightAtoms
        if struggle_state == StruggleState.SURPLUS:
            self.insight_atoms.append(finding.to_insight_atom_dict())

    def _update_resonance_metrics(
        self,
        finding: Finding,
        struggle_state: StruggleState,
    ) -> None:
        """Update resonance metrics with new finding.

        Args:
            finding: The finding to process.
            struggle_state: Its struggle state.
        """
        self.resonance_metrics.total_findings += 1

        if finding.cognitive_stage == 5:
            self.resonance_metrics.stage_5_findings += 1

        if finding.thought_type == "manifestation":
            self.resonance_metrics.manifestation_count += 1

        if finding.emotional_state == "resonance":
            self.resonance_metrics.resonance_count += 1

        if struggle_state == StruggleState.SURPLUS:
            self.resonance_metrics.surplus_value_count += 1

    def add_pattern(self, pattern: Pattern) -> None:
        """Add a discovered pattern.

        Args:
            pattern: The pattern to add.
        """
        self.patterns.append(pattern)

    def get_high_significance_findings(self) -> list[Finding]:
        """Get HIGH significance findings.

        Returns:
            List of HIGH significance findings.
        """
        return [f for f in self.findings if f.significance == Significance.HIGH]

    def get_recent_findings(self, count: int = 5) -> list[Finding]:
        """Get most recent findings.

        Args:
            count: Number of findings to return.

        Returns:
            List of recent findings.
        """
        return self.findings[-count:] if self.findings else []

    def get_findings_summary(self) -> str:
        """Get summary of findings for prompts.

        Returns:
            Formatted string summarizing findings.
        """
        if not self.findings:
            return "No findings yet."

        lines = []
        for f in self.findings[-10:]:  # Last 10
            sig_marker = (
                "★"
                if f.significance == Significance.HIGH
                else "●"
                if f.significance == Significance.MEDIUM
                else "○"
            )
            lines.append(f"{sig_marker} [{f.tool_name}] {f.analysis[:100]}...")

        return "\n".join(lines)

    def get_entities_discovered(self) -> list[str]:
        """Get all entity IDs discovered across findings.

        Returns:
            Deduplicated list of entity IDs.
        """
        seen: set[str] = set()
        entities: list[str] = []

        for finding in self.findings:
            for eid in finding.entities_mentioned:
                if eid not in seen:
                    seen.add(eid)
                    entities.append(eid)

        return entities

    def get_session_stats(self) -> dict[str, Any]:
        """Get session statistics.

        Returns:
            Dictionary of session stats.
        """
        return {
            "session_id": self.id,
            "correlation_id": self.correlation_id,
            "iterations_completed": self.current_iteration,
            "findings_count": len(self.findings),
            "findings_discarded": self.discarded_count,
            "patterns_discovered": len(self.patterns),
            "insight_atoms_generated": len(self.insight_atoms),
            "tools_invoked": self.tools_invoked,
            "entities_discovered": len(self.get_entities_discovered()),
            "resonance_metrics": self.resonance_metrics.to_dict(),
            "should_stop": self.should_stop,
            "stop_reason": self.stop_reason,
            "duration_seconds": (datetime.now(UTC) - self.started_at).total_seconds(),
        }


__all__ = [
    "ExplorationSession",
]
