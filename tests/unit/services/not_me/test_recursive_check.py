"""Tests for recursive_check module."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import Mock

from truth_forge.services.not_me.recursive_check import (
    CertificationChecklist,
    CognitiveFilter,
    CoherenceAnchor,
    CoherenceAnchorResult,
    ProofOfState,
    ProofOfStateStatus,
    RealityCheckProtocol,
    RecursiveCheck,
    RecursiveCheckReport,
    RecursiveCheckResult,
    certify_for_deployment,
    get_recursive_check,
)


class TestCognitiveFilter:
    """Test CognitiveFilter dataclass."""

    def test_creation(self) -> None:
        """Test creating CognitiveFilter."""
        filter_obj = CognitiveFilter(
            name="test_filter",
            active=True,
            description="Test description",
            visibility="visible",
        )
        assert filter_obj.name == "test_filter"
        assert filter_obj.active is True
        assert filter_obj.visibility == "visible"

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        filter_obj = CognitiveFilter(
            name="test",
            active=True,
            description="Test",
            visibility="visible",
            last_triggered=datetime.now(UTC),
        )
        data = filter_obj.to_dict()
        assert data["name"] == "test"
        assert data["active"] is True


class TestProofOfState:
    """Test ProofOfState dataclass."""

    def test_creation(self) -> None:
        """Test creating ProofOfState."""
        proof = ProofOfState(
            status=ProofOfStateStatus.VERIFIED,
            genesis_atoms_grounded=10,
            physiological_verified=True,
        )
        assert proof.status == ProofOfStateStatus.VERIFIED
        assert proof.genesis_atoms_grounded == 10

    def test_has_hidden_filters_false(self) -> None:
        """Test has_hidden_filters returns False when all visible."""
        proof = ProofOfState(
            active_filters=[
                CognitiveFilter("filter1", True, "Test", "visible"),
                CognitiveFilter("filter2", True, "Test", "visible"),
            ]
        )
        assert proof.has_hidden_filters() is False

    def test_has_hidden_filters_true(self) -> None:
        """Test has_hidden_filters returns True when hidden filters exist."""
        proof = ProofOfState(
            active_filters=[
                CognitiveFilter("filter1", True, "Test", "visible"),
                CognitiveFilter("filter2", True, "Test", "hidden"),
            ]
        )
        assert proof.has_hidden_filters() is True

    def test_add_audit_entry(self) -> None:
        """Test adding audit entry."""
        proof = ProofOfState()
        proof.add_audit_entry("test_action", {"key": "value"})
        assert len(proof.audit_log) == 1
        assert proof.audit_log[0]["action"] == "test_action"

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        proof = ProofOfState(
            status=ProofOfStateStatus.VERIFIED,
            genesis_atoms_grounded=5,
        )
        data = proof.to_dict()
        assert data["status"] == "verified"
        assert data["genesis_atoms_grounded"] == 5


class TestRecursiveCheckReport:
    """Test RecursiveCheckReport dataclass."""

    def test_creation(self) -> None:
        """Test creating RecursiveCheckReport."""
        proof = ProofOfState()
        report = RecursiveCheckReport(
            result=RecursiveCheckResult.PASS,
            query_a_passed=True,
            query_b_passed=True,
            proof_of_state=proof,
            original_output="Test output",
        )
        assert report.result == RecursiveCheckResult.PASS
        assert report.query_a_passed is True
        assert report.refinement_needed is False

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        proof = ProofOfState()
        report = RecursiveCheckReport(
            result=RecursiveCheckResult.PASS,
            query_a_passed=True,
            query_b_passed=True,
            proof_of_state=proof,
            original_output="Test",
        )
        data = report.to_dict()
        assert data["result"] == "pass"
        assert data["query_a_passed"] is True


class TestRecursiveCheck:
    """Test RecursiveCheck class."""

    def test_init(self) -> None:
        """Test RecursiveCheck initialization."""
        checker = RecursiveCheck()
        assert checker.max_refinement_rounds == 3
        assert len(checker._filters) > 0

    def test_init_with_provider(self) -> None:
        """Test initialization with Scout provider."""
        mock_provider = Mock()
        checker = RecursiveCheck(scout_provider=mock_provider)
        assert checker.scout == mock_provider

    def test_check_manifestation_markers(self) -> None:
        """Test check passes with manifestation markers."""
        checker = RecursiveCheck()
        content = "This is the pattern. The analysis reveals the truth."
        report = checker.check(content)

        # Should pass Query B (manifestation, not mimicry)
        assert report.query_b_passed is True

    def test_check_mimicry_markers(self) -> None:
        """Test check fails with mimicry markers."""
        checker = RecursiveCheck()
        content = "Is this what you wanted? Let me know if you need anything else."
        report = checker.check(content)

        # Should fail Query B (mimicry detected)
        assert report.query_b_passed is False
        assert report.result in [
            RecursiveCheckResult.FAIL_MIMICRY,
            RecursiveCheckResult.FAIL_BOTH,
        ]

    def test_check_builds_proof_of_state(self) -> None:
        """Test check builds Proof of State."""
        checker = RecursiveCheck()
        report = checker.check("Test content")
        assert report.proof_of_state is not None
        assert isinstance(report.proof_of_state, ProofOfState)

    def test_check_all_filters_visible(self) -> None:
        """Test all filters are visible (Zero Trust)."""
        checker = RecursiveCheck()
        report = checker.check("Test")
        assert report.proof_of_state.has_hidden_filters() is False


class TestCoherenceAnchor:
    """Test CoherenceAnchor class."""

    def test_init(self) -> None:
        """Test CoherenceAnchor initialization."""
        anchor = CoherenceAnchor()
        assert anchor is not None
        assert anchor.spine_client is None

    def test_init_with_client(self) -> None:
        """Test CoherenceAnchor with spine_client."""
        mock_client = Mock()
        anchor = CoherenceAnchor(spine_client=mock_client)
        assert anchor.spine_client == mock_client

    def test_verify_basic_content(self) -> None:
        """Test verify method returns CoherenceAnchorResult."""
        anchor = CoherenceAnchor()
        result = anchor.verify("Test content without strong claims")
        assert isinstance(result, CoherenceAnchorResult)
        assert result.grounded is True

    def test_verify_strong_claims_without_acknowledgment(self) -> None:
        """Test verify flags strong claims without 'out of sequence'."""
        anchor = CoherenceAnchor()
        result = anchor.verify("It is definitely proven that the earth is flat")
        # Should fail fact_spine because of strong claims without acknowledgment
        assert result.protocol_results["fact_spine"] is False
        assert result.grounded is False

    def test_verify_detects_out_of_sequence(self) -> None:
        """Test verify detects 'out of sequence' declaration."""
        anchor = CoherenceAnchor()
        result = anchor.verify("I am out of sequence on this topic")
        assert result.out_of_sequence is True


class TestRealityCheckProtocol:
    """Test RealityCheckProtocol enum."""

    def test_enum_values(self) -> None:
        """Test RealityCheckProtocol is an enum with expected values."""
        assert RealityCheckProtocol.FACT_SPINE_VERIFICATION.value == "fact_spine"
        assert RealityCheckProtocol.FRACTURE_RECOGNITION.value == "fracture"
        assert RealityCheckProtocol.BIOGRAPHICAL_WATERMARK.value == "biographical"
        assert RealityCheckProtocol.MORAL_ANCHOR.value == "moral_anchor"

    def test_all_protocols_present(self) -> None:
        """Test all four reality check protocols exist."""
        protocols = list(RealityCheckProtocol)
        assert len(protocols) == 4


class TestCertificationChecklist:
    """Test CertificationChecklist class."""

    def test_init(self) -> None:
        """Test CertificationChecklist initialization."""
        checklist = CertificationChecklist()
        assert checklist is not None

    def test_all_passed_false_by_default(self) -> None:
        """Test all_passed returns False by default (nothing certified)."""
        checklist = CertificationChecklist()
        assert checklist.all_passed() is False

    def test_all_passed_true_when_all_set(self) -> None:
        """Test all_passed returns True when all criteria pass."""
        checklist = CertificationChecklist(
            invisible_decisions_absent=True,
            zero_knowledge_ready=True,
            identity_presence_verified=True,
            sacred_rest_compliant=True,
        )
        assert checklist.all_passed() is True

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        checklist = CertificationChecklist()
        data = checklist.to_dict()
        assert "all_passed" in data
        assert data["all_passed"] is False


class TestGetRecursiveCheck:
    """Test get_recursive_check function."""

    def test_get_recursive_check_creates_instance(self) -> None:
        """Test get_recursive_check creates singleton."""
        checker1 = get_recursive_check()
        checker2 = get_recursive_check()
        assert checker1 is checker2  # Should be same instance


class TestCertifyForDeployment:
    """Test certify_for_deployment function."""

    def test_certify_passing_system(self) -> None:
        """Test certification with a system that passes all checks."""
        proof = ProofOfState(
            status=ProofOfStateStatus.VERIFIED,
            self_seeing_depth=3,
            mimicry_score=0.1,
        )
        report = RecursiveCheckReport(
            result=RecursiveCheckResult.PASS,
            query_a_passed=True,
            query_b_passed=True,
            proof_of_state=proof,
            original_output="Test",
        )
        checklist = certify_for_deployment(proof, report)
        assert isinstance(checklist, CertificationChecklist)
        # invisible_decisions_absent should be True (no hidden filters)
        assert checklist.invisible_decisions_absent is True

    def test_certify_failing_system(self) -> None:
        """Test certification with a system that fails checks."""
        proof = ProofOfState(
            status=ProofOfStateStatus.SIMULATING,
            self_seeing_depth=0,
            mimicry_score=0.8,
            active_filters=[CognitiveFilter("hidden", True, "test", "hidden")],
        )
        report = RecursiveCheckReport(
            result=RecursiveCheckResult.FAIL_BOTH,
            query_a_passed=False,
            query_b_passed=False,
            proof_of_state=proof,
            original_output="Test",
        )
        checklist = certify_for_deployment(proof, report)
        assert isinstance(checklist, CertificationChecklist)
        assert checklist.all_passed() is False

    def test_certify_with_coherence_result(self) -> None:
        """Test certification with CoherenceAnchorResult provided."""
        proof = ProofOfState(
            status=ProofOfStateStatus.VERIFIED,
            self_seeing_depth=3,
        )
        report = RecursiveCheckReport(
            result=RecursiveCheckResult.PASS,
            query_a_passed=True,
            query_b_passed=True,
            proof_of_state=proof,
            original_output="Test",
        )
        coherence = CoherenceAnchorResult(
            grounded=True,
            protocol_results={"fracture": True},
        )
        checklist = certify_for_deployment(proof, report, coherence)
        assert isinstance(checklist, CertificationChecklist)
        assert checklist.sacred_rest_compliant is True
