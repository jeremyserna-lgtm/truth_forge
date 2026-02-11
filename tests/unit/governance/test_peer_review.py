"""Tests for peer review module."""

from __future__ import annotations

from unittest.mock import Mock, patch

from truth_forge.governance.peer_review import (
    Consensus,
    VerificationResult,
    verify_claim,
)


class TestVerificationResult:
    """Test VerificationResult dataclass."""

    def test_verification_result(self) -> None:
        """Test VerificationResult structure."""
        result = VerificationResult(agent="agent1", agrees=True, details={"note": "test"})
        assert result.agent == "agent1"
        assert result.agrees is True
        assert result.details == {"note": "test"}


class TestConsensus:
    """Test Consensus dataclass."""

    def test_consensus(self) -> None:
        """Test Consensus structure."""
        results = [VerificationResult(agent="a1", agrees=True, details={})]
        consensus = Consensus(
            verified=True,
            agreement=1.0,
            results=results,
            dissent=[],
            reason=None,
        )
        assert consensus.verified is True
        assert consensus.agreement == 1.0
        assert len(consensus.results) == 1
        assert len(consensus.dissent) == 0


class TestVerifyClaim:
    """Test verify_claim function."""

    def test_single_voter_agrees(self) -> None:
        """Test verification with single agreeing voter."""

        def voter(claim: str, context: dict) -> dict:
            return {"agrees": True, "details": {}}

        consensus = verify_claim("test claim", voters=[("agent1", voter)])
        assert consensus.verified is True
        assert consensus.agreement == 1.0
        assert len(consensus.results) == 1
        assert len(consensus.dissent) == 0

    def test_single_voter_disagrees(self) -> None:
        """Test verification with single disagreeing voter."""

        def voter(claim: str, context: dict) -> dict:
            return {"agrees": False, "details": {}}

        consensus = verify_claim("test claim", voters=[("agent1", voter)])
        assert consensus.verified is False
        assert consensus.agreement == 0.0
        assert len(consensus.dissent) == 1

    def test_multiple_voters_majority(self) -> None:
        """Test verification with majority agreement."""

        def agree_voter(claim: str, context: dict) -> dict:
            return {"agrees": True, "details": {}}

        def disagree_voter(claim: str, context: dict) -> dict:
            return {"agrees": False, "details": {}}

        consensus = verify_claim(
            "test claim",
            voters=[
                ("agent1", agree_voter),
                ("agent2", agree_voter),
                ("agent3", disagree_voter),
            ],
            threshold=0.6,
        )
        assert consensus.verified is True  # 66.7% >= 60% threshold
        assert consensus.agreement == 2.0 / 3.0
        assert len(consensus.dissent) == 1

    def test_custom_threshold(self) -> None:
        """Test verification with custom threshold."""

        def voter(claim: str, context: dict) -> dict:
            return {"agrees": True, "details": {}}

        # 50% agreement, but threshold is 0.9
        consensus = verify_claim(
            "test claim",
            voters=[("agent1", voter), ("agent2", lambda c, ctx: {"agrees": False, "details": {}})],
            threshold=0.9,
        )
        assert consensus.verified is False
        assert consensus.agreement == 0.5

    def test_default_voter(self) -> None:
        """Test verification with no voters uses default."""
        consensus = verify_claim("test claim")
        assert consensus.verified is True  # Default voter agrees
        assert len(consensus.results) == 1

    def test_context_passed(self) -> None:
        """Test context is passed to voters."""
        context_received = None

        def voter(claim: str, context: dict) -> dict:
            nonlocal context_received
            context_received = context
            return {"agrees": True, "details": {}}

        verify_claim("test claim", context={"key": "value"}, voters=[("agent1", voter)])
        assert context_received == {"key": "value"}

    @patch("truth_forge.governance.peer_review.feature_flags")
    def test_uses_feature_flag_threshold(self, mock_flags: Mock) -> None:
        """Test uses threshold from feature flags."""
        mock_flags.routing.require_peer_review_above = 0.8

        def voter(claim: str, context: dict) -> dict:
            return {"agrees": True, "details": {}}

        consensus = verify_claim("test claim", voters=[("agent1", voter)])
        # Should use 0.8 threshold from feature flags
        assert consensus.verified is True  # 100% > 0.8
