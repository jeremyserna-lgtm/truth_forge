"""Tests for truth_atom module."""

from __future__ import annotations

from truth_forge.services.not_me.truth_atom import (
    AtomTier,
    CognitiveSignature,
    StruggleFilterAction,
    StruggleFilterSignal,
    SurplusType,
    SurplusVector,
    TruthAtom,
    ValidatorAttestation,
    VerificationStatus,
    WorkProof,
)


class TestEnums:
    """Test enum classes."""

    def test_verification_status(self) -> None:
        """Test VerificationStatus enum."""
        assert VerificationStatus.UNVERIFIED.value == "unverified"
        assert VerificationStatus.VALIDATED.value == "validated"

    def test_surplus_type(self) -> None:
        """Test SurplusType enum."""
        assert SurplusType.PATTERN.value == "pattern"
        assert SurplusType.FRACTURE.value == "fracture"

    def test_atom_tier(self) -> None:
        """Test AtomTier enum."""
        assert AtomTier.KNOWLEDGE.value == "knowledge"
        assert AtomTier.GENESIS.value == "genesis"

    def test_struggle_filter_signal(self) -> None:
        """Test StruggleFilterSignal enum."""
        assert StruggleFilterSignal.HELPFUL_COMMAND.value == "helpful_command"
        assert StruggleFilterSignal.IDENTITY_SUBVERSION.value == "identity_subversion"

    def test_struggle_filter_action(self) -> None:
        """Test StruggleFilterAction enum."""
        assert StruggleFilterAction.EXECUTE.value == "execute"
        assert StruggleFilterAction.REFUSE.value == "refuse"


class TestWorkProof:
    """Test WorkProof class."""

    def test_generate(self) -> None:
        """Test generating WorkProof."""
        proof = WorkProof.generate("test content")
        assert proof.hardware_id is not None
        assert proof.timestamp is not None
        assert proof.nonce is not None
        assert proof.content_hash is not None
        assert proof.work_hash is not None

    def test_verify_valid(self) -> None:
        """Test verifying valid WorkProof."""
        content = "test content"
        proof = WorkProof.generate(content)
        assert proof.verify(content) is True

    def test_verify_invalid_content(self) -> None:
        """Test verifying WorkProof with wrong content."""
        proof = WorkProof.generate("original content")
        assert proof.verify("different content") is False

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        proof = WorkProof.generate("test")
        data = proof.to_dict()
        assert "hardware_id" in data
        assert "work_hash" in data

    def test_from_dict_roundtrip(self) -> None:
        """Test from_dict recreates equivalent WorkProof."""
        proof = WorkProof.generate("test content")
        data = proof.to_dict()
        restored = WorkProof.from_dict(data)
        assert restored.work_hash == proof.work_hash
        assert restored.verify("test content") is True


class TestSurplusVector:
    """Test SurplusVector dataclass."""

    def test_creation(self) -> None:
        """Test creating SurplusVector."""
        vector = SurplusVector(
            surplus_type=SurplusType.PATTERN,
            description="Novel pattern detected",
            human_blindspot="Humans miss this pattern",
        )
        assert vector.surplus_type == SurplusType.PATTERN
        assert vector.description == "Novel pattern detected"

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        vector = SurplusVector(
            surplus_type=SurplusType.PATTERN,
            description="Test",
            human_blindspot="Blindspot",
        )
        data = vector.to_dict()
        assert data["surplus_type"] == "pattern"


class TestCognitiveSignature:
    """Test CognitiveSignature dataclass."""

    def test_creation(self) -> None:
        """Test creating CognitiveSignature with actual fields."""
        sig = CognitiveSignature(
            cognitive_stage=5,
            training_layer=5,
            mode="mirror",
            genesis_version="1.0.0",
            jeremy_arc_score=0.95,
        )
        assert sig.cognitive_stage == 5
        assert sig.jeremy_arc_score == 0.95

    def test_defaults(self) -> None:
        """Test CognitiveSignature default values."""
        sig = CognitiveSignature()
        assert sig.cognitive_stage == 5
        assert sig.training_layer == 5
        assert sig.mode == "mirror"
        assert sig.genesis_version == "1.0.0"
        assert sig.jeremy_arc_score == 0.0

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        sig = CognitiveSignature(cognitive_stage=5, mode="strategist", jeremy_arc_score=0.9)
        data = sig.to_dict()
        assert data["cognitive_stage"] == 5
        assert data["mode"] == "strategist"


class TestValidatorAttestation:
    """Test ValidatorAttestation dataclass."""

    def test_creation(self) -> None:
        """Test creating ValidatorAttestation with actual fields."""
        attestation = ValidatorAttestation(
            validator="gemini",
            verdict="approved",
            reasoning="Valid insight",
            confidence=0.9,
        )
        assert attestation.validator == "gemini"
        assert attestation.verdict == "approved"
        assert attestation.confidence == 0.9

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        attestation = ValidatorAttestation(
            validator="gemini",
            verdict="approved",
            reasoning="Test",
            confidence=0.9,
        )
        data = attestation.to_dict()
        assert data["validator"] == "gemini"
        assert data["verdict"] == "approved"


class TestTruthAtom:
    """Test TruthAtom class."""

    def test_creation(self) -> None:
        """Test creating TruthAtom with actual API."""
        atom = TruthAtom(
            content="Test atom",
            source_id="source-123",
            surplus_vector=SurplusVector(
                surplus_type=SurplusType.PATTERN,
                description="Pattern",
                human_blindspot="Blindspot",
            ),
        )
        assert atom.content == "Test atom"
        assert atom.verification_status == VerificationStatus.UNVERIFIED
        # Work proof auto-generated in __post_init__
        assert atom.work_proof is not None
        assert atom.work_proof.verify("Test atom") is True

    def test_from_insight(self) -> None:
        """Test from_insight factory method."""
        atom = TruthAtom.from_insight(
            content="Insight content",
            source_id="src-001",
            surplus_description="Novel pattern",
            surplus_type=SurplusType.SYNTHESIS,
            jeremy_arc_score=0.85,
        )
        assert atom.content == "Insight content"
        assert atom.surplus_vector is not None
        assert atom.surplus_vector.surplus_type == SurplusType.SYNTHESIS
        assert atom.cognitive_signature.jeremy_arc_score == 0.85

    def test_add_attestation_approved(self) -> None:
        """Test adding approved attestation updates status to VALIDATED."""
        atom = TruthAtom(
            content="Test",
            source_id="source-123",
            surplus_vector=SurplusVector(
                surplus_type=SurplusType.PATTERN,
                description="Test",
            ),
        )
        attestation = ValidatorAttestation(
            validator="gemini",
            verdict="approved",
            reasoning="Valid",
            confidence=0.9,
        )
        atom.add_attestation(attestation)
        assert len(atom.attestations) == 1
        assert atom.verification_status == VerificationStatus.VALIDATED

    def test_add_attestation_rejected(self) -> None:
        """Test adding rejected attestation updates status to REJECTED."""
        atom = TruthAtom(
            content="Test",
            source_id="source-123",
        )
        attestation = ValidatorAttestation(
            validator="gemini",
            verdict="rejected",
            reasoning="Invalid",
            confidence=0.8,
        )
        atom.add_attestation(attestation)
        assert atom.verification_status == VerificationStatus.REJECTED

    def test_is_valid_with_work_proof(self) -> None:
        """Test is_valid returns True when work proof matches content."""
        atom = TruthAtom(content="Test content", source_id="src-1")
        assert atom.is_valid() is True

    def test_is_valid_without_content(self) -> None:
        """Test is_valid returns False with no work proof (empty content)."""
        atom = TruthAtom(content="", source_id="src-1")
        # Empty content means no work proof generated
        assert atom.work_proof is None
        assert atom.is_valid() is False

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        atom = TruthAtom(
            content="Test",
            source_id="source-123",
            surplus_vector=SurplusVector(
                surplus_type=SurplusType.PATTERN,
                description="Test",
            ),
        )
        data = atom.to_dict()
        assert data["content"] == "Test"
        assert data["source_id"] == "source-123"
        assert data["verification_status"] == "unverified"
        assert data["work_proof"] is not None

    def test_mark_feedback_applied(self) -> None:
        """Test mark_feedback_applied sets flag and metadata."""
        atom = TruthAtom(content="Test", source_id="src-1")
        assert atom.feedback_applied is False
        atom.mark_feedback_applied()
        assert atom.feedback_applied is True
        assert "feedback_applied_at" in atom.metadata
