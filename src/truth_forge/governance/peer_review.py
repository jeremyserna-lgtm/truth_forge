"""Peer review scaffolding for high-risk operations.

This module provides a simple consensus mechanism that can wrap
arbitrary callables (e.g., LLM queries or validators). It is intentionally
model-agnostic so it can be wired to Scout/Maverick/R1 or other agents.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from truth_forge.governance.feature_flags import feature_flags


VerificationFn = Callable[[str, dict[str, Any]], dict[str, Any]]


@dataclass
class VerificationResult:
    agent: str
    agrees: bool
    details: dict[str, Any]


@dataclass
class Consensus:
    verified: bool
    agreement: float
    results: list[VerificationResult]
    dissent: list[VerificationResult]
    reason: str | None = None


def _default_voter(claim: str, context: dict[str, Any]) -> dict[str, Any]:
    return {"agrees": True, "details": {"note": "no-op voter"}}


def verify_claim(
    claim: str,
    context: dict[str, Any] | None = None,
    voters: Iterable[tuple[str, VerificationFn]] | None = None,
    threshold: float | None = None,
) -> Consensus:
    """Run multi-agent verification and return consensus."""
    ctx = context or {}
    voter_list = list(voters or [("default", _default_voter)])
    results: list[VerificationResult] = []

    for agent, fn in voter_list:
        outcome = fn(claim, ctx) or {}
        agrees = bool(outcome.get("agrees", False))
        results.append(VerificationResult(agent=agent, agrees=agrees, details=outcome))

    agreement = sum(1 for r in results if r.agrees) / max(len(results), 1)
    cut = threshold if threshold is not None else feature_flags.routing.require_peer_review_above
    verified = agreement >= cut
    dissent = [r for r in results if not r.agrees]
    return Consensus(
        verified=verified,
        agreement=agreement,
        results=results,
        dissent=dissent,
        reason=None if verified else "insufficient consensus",
    )
