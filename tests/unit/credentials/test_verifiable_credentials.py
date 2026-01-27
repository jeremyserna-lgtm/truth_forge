"""Tests for verifiable credentials module.

Tests the W3C Verifiable Credentials 2.0 implementation.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from truth_forge.credentials.verifiable_credentials import (
    VC_CONTEXT_V2,
    CredentialProof,
    CredentialStatus,
    CredentialSubject,
    DIDDocument,
    VerifiableCredential,
    VerifiablePresentation,
    VerificationResult,
    _parse_proof,
    create_credential,
    create_presentation,
    resolve_did,
    verify_credential,
    verify_presentation,
)


class TestCredentialSubject:
    """Tests for CredentialSubject dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        subject = CredentialSubject()
        assert subject.id is None
        assert subject.claims == {}

    def test_with_id_and_claims(self) -> None:
        """Test with ID and claims."""
        subject = CredentialSubject(
            id="did:example:123",
            claims={"name": "Alice", "age": 30},
        )
        assert subject.id == "did:example:123"
        assert subject.claims["name"] == "Alice"

    def test_to_dict_with_id(self) -> None:
        """Test to_dict includes id."""
        subject = CredentialSubject(
            id="did:example:456",
            claims={"degree": "PhD"},
        )
        result = subject.to_dict()
        assert result["id"] == "did:example:456"
        assert result["degree"] == "PhD"

    def test_to_dict_without_id(self) -> None:
        """Test to_dict without id."""
        subject = CredentialSubject(claims={"skill": "Python"})
        result = subject.to_dict()
        assert "id" not in result
        assert result["skill"] == "Python"


class TestCredentialStatus:
    """Tests for CredentialStatus dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        status = CredentialStatus(id="https://example.com/status/1")
        assert status.type == "BitstringStatusListEntry"
        assert status.status_purpose == "revocation"
        assert status.status_list_index is None
        assert status.status_list_credential is None

    def test_to_dict_minimal(self) -> None:
        """Test to_dict with minimal fields."""
        status = CredentialStatus(id="https://example.com/status/1")
        result = status.to_dict()
        assert result["id"] == "https://example.com/status/1"
        assert result["type"] == "BitstringStatusListEntry"
        assert result["statusPurpose"] == "revocation"
        assert "statusListIndex" not in result
        assert "statusListCredential" not in result

    def test_to_dict_full(self) -> None:
        """Test to_dict with all fields."""
        status = CredentialStatus(
            id="https://example.com/status/1",
            type="BitstringStatusListEntry",
            status_purpose="suspension",
            status_list_index=42,
            status_list_credential="https://example.com/credentials/status/1",
        )
        result = status.to_dict()
        assert result["statusListIndex"] == 42
        assert result["statusListCredential"] == "https://example.com/credentials/status/1"
        assert result["statusPurpose"] == "suspension"


class TestCredentialProof:
    """Tests for CredentialProof dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        proof = CredentialProof()
        assert proof.type == "DataIntegrityProof"
        assert proof.proof_purpose == "assertionMethod"
        assert proof.cryptosuite is None

    def test_to_dict_minimal(self) -> None:
        """Test to_dict with minimal fields."""
        proof = CredentialProof(
            verification_method="did:example:123#key-1",
            proof_value="abc123",
        )
        result = proof.to_dict()
        assert result["type"] == "DataIntegrityProof"
        assert result["verificationMethod"] == "did:example:123#key-1"
        assert result["proofValue"] == "abc123"
        assert result["proofPurpose"] == "assertionMethod"
        assert "cryptosuite" not in result

    def test_to_dict_with_cryptosuite(self) -> None:
        """Test to_dict with cryptosuite."""
        proof = CredentialProof(
            type="DataIntegrityProof",
            cryptosuite="eddsa-rdfc-2022",
            verification_method="did:example:123#key-1",
            proof_value="signature",
        )
        result = proof.to_dict()
        assert result["cryptosuite"] == "eddsa-rdfc-2022"


class TestParseProof:
    """Tests for _parse_proof helper function."""

    def test_parse_minimal(self) -> None:
        """Test parsing minimal proof data."""
        data: dict[str, Any] = {}
        proof = _parse_proof(data)
        assert proof.type == "DataIntegrityProof"
        assert proof.proof_purpose == "assertionMethod"

    def test_parse_full(self) -> None:
        """Test parsing full proof data."""
        now = datetime.now(UTC)
        data = {
            "type": "Ed25519Signature2020",
            "created": now.isoformat(),
            "verificationMethod": "did:example:123#key-1",
            "proofPurpose": "authentication",
            "proofValue": "sig123",
            "cryptosuite": "eddsa-2022",
        }
        proof = _parse_proof(data)
        assert proof.type == "Ed25519Signature2020"
        assert proof.proof_purpose == "authentication"
        assert proof.proof_value == "sig123"
        assert proof.cryptosuite == "eddsa-2022"

    def test_parse_with_z_suffix(self) -> None:
        """Test parsing ISO date with Z suffix."""
        data = {"created": "2024-01-15T10:00:00Z"}
        proof = _parse_proof(data)
        assert proof.created.tzinfo is not None


class TestVerifiableCredential:
    """Tests for VerifiableCredential dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        vc = VerifiableCredential()
        assert VC_CONTEXT_V2 in vc.context
        assert "VerifiableCredential" in vc.type
        assert vc.issuer == ""
        assert vc.id is None
        assert vc.proof is None

    def test_to_dict_minimal(self) -> None:
        """Test to_dict with minimal fields."""
        vc = VerifiableCredential(issuer="did:example:issuer")
        result = vc.to_dict()
        assert result["@context"] == [VC_CONTEXT_V2]
        assert result["issuer"] == "did:example:issuer"
        assert "credentialSubject" in result

    def test_to_dict_with_dates(self) -> None:
        """Test to_dict with dates."""
        now = datetime.now(UTC)
        vc = VerifiableCredential(
            issuer="did:example:issuer",
            valid_from=now,
            valid_until=now + timedelta(days=365),
        )
        result = vc.to_dict()
        assert "validFrom" in result
        assert "validUntil" in result

    def test_to_dict_with_optional_fields(self) -> None:
        """Test to_dict with all optional fields."""
        vc = VerifiableCredential(
            id="urn:uuid:12345",
            issuer="did:example:issuer",
            credential_status=CredentialStatus(id="https://example.com/status"),
            credential_schema={"id": "https://example.com/schema"},
            evidence=[{"type": "DocumentEvidence"}],
            terms_of_use=[{"type": "IssuerPolicy"}],
            refresh_service={"type": "ManualRefresh"},
        )
        result = vc.to_dict()
        assert result["id"] == "urn:uuid:12345"
        assert "credentialStatus" in result
        assert "credentialSchema" in result
        assert "evidence" in result
        assert "termsOfUse" in result
        assert "refreshService" in result

    def test_to_dict_exclude_proof(self) -> None:
        """Test to_dict can exclude proof."""
        proof = CredentialProof(proof_value="sig")
        vc = VerifiableCredential(issuer="did:example:issuer", proof=proof)

        with_proof = vc.to_dict(include_proof=True)
        without_proof = vc.to_dict(include_proof=False)

        assert "proof" in with_proof
        assert "proof" not in without_proof

    def test_to_dict_with_proof_list(self) -> None:
        """Test to_dict with multiple proofs."""
        proofs = [
            CredentialProof(proof_value="sig1"),
            CredentialProof(proof_value="sig2"),
        ]
        vc = VerifiableCredential(issuer="did:example:issuer", proof=proofs)
        result = vc.to_dict()
        assert isinstance(result["proof"], list)
        assert len(result["proof"]) == 2

    def test_to_json(self) -> None:
        """Test to_json produces valid JSON."""
        vc = VerifiableCredential(issuer="did:example:issuer")
        json_str = vc.to_json()
        parsed = json.loads(json_str)
        assert parsed["issuer"] == "did:example:issuer"

    def test_from_dict(self) -> None:
        """Test from_dict creates VC correctly."""
        data = {
            "@context": [VC_CONTEXT_V2],
            "type": ["VerifiableCredential", "TestCredential"],
            "issuer": "did:example:issuer",
            "id": "urn:uuid:12345",
            "credentialSubject": {
                "id": "did:example:subject",
                "name": "Alice",
            },
        }
        vc = VerifiableCredential.from_dict(data)
        assert vc.issuer == "did:example:issuer"
        assert vc.id == "urn:uuid:12345"
        assert vc.credential_subject.id == "did:example:subject"
        assert vc.credential_subject.claims["name"] == "Alice"

    def test_from_dict_with_dates(self) -> None:
        """Test from_dict parses dates."""
        data = {
            "@context": [VC_CONTEXT_V2],
            "type": ["VerifiableCredential"],
            "issuer": "did:example:issuer",
            "validFrom": "2024-01-15T10:00:00Z",
            "validUntil": "2025-01-15T10:00:00+00:00",
            "credentialSubject": {},
        }
        vc = VerifiableCredential.from_dict(data)
        assert vc.valid_from is not None
        assert vc.valid_until is not None

    def test_from_dict_with_single_proof(self) -> None:
        """Test from_dict parses single proof."""
        data = {
            "@context": [VC_CONTEXT_V2],
            "issuer": "did:example:issuer",
            "credentialSubject": {},
            "proof": {
                "type": "DataIntegrityProof",
                "proofValue": "sig123",
            },
        }
        vc = VerifiableCredential.from_dict(data)
        assert vc.proof is not None
        assert not isinstance(vc.proof, list)
        assert vc.proof.proof_value == "sig123"

    def test_from_dict_with_proof_list(self) -> None:
        """Test from_dict parses proof list."""
        data = {
            "@context": [VC_CONTEXT_V2],
            "issuer": "did:example:issuer",
            "credentialSubject": {},
            "proof": [
                {"type": "Proof1", "proofValue": "sig1"},
                {"type": "Proof2", "proofValue": "sig2"},
            ],
        }
        vc = VerifiableCredential.from_dict(data)
        assert isinstance(vc.proof, list)
        assert len(vc.proof) == 2


class TestVerifiablePresentation:
    """Tests for VerifiablePresentation dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        vp = VerifiablePresentation()
        assert VC_CONTEXT_V2 in vp.context
        assert "VerifiablePresentation" in vp.type
        assert vp.holder is None
        assert vp.verifiable_credential == []

    def test_to_dict(self) -> None:
        """Test to_dict."""
        vc = VerifiableCredential(issuer="did:example:issuer")
        vp = VerifiablePresentation(
            id="urn:uuid:vp123",
            holder="did:example:holder",
            verifiable_credential=[vc],
        )
        result = vp.to_dict()
        assert result["id"] == "urn:uuid:vp123"
        assert result["holder"] == "did:example:holder"
        assert len(result["verifiableCredential"]) == 1

    def test_to_dict_with_proof(self) -> None:
        """Test to_dict with proof."""
        proof = CredentialProof(proof_value="vp_sig")
        vp = VerifiablePresentation(
            holder="did:example:holder",
            proof=proof,
        )
        result = vp.to_dict()
        assert "proof" in result


class TestDIDDocument:
    """Tests for DIDDocument dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        doc = DIDDocument(id="did:example:123")
        assert doc.id == "did:example:123"
        assert doc.verification_method == []
        assert doc.authentication == []
        assert doc.assertion_method == []

    def test_get_verification_key_found(self) -> None:
        """Test get_verification_key when key exists."""
        doc = DIDDocument(
            id="did:example:123",
            verification_method=[
                {"id": "did:example:123#key-1", "type": "Ed25519"},
                {"id": "did:example:123#key-2", "type": "RSA"},
            ],
        )
        key = doc.get_verification_key("did:example:123#key-1")
        assert key is not None
        assert key["type"] == "Ed25519"

    def test_get_verification_key_not_found(self) -> None:
        """Test get_verification_key when key doesn't exist."""
        doc = DIDDocument(id="did:example:123")
        key = doc.get_verification_key("did:example:123#key-99")
        assert key is None


class TestResolveDID:
    """Tests for resolve_did function."""

    def test_resolve_did_web(self) -> None:
        """Test resolving did:web DID."""
        result = resolve_did("did:web:example.com")
        assert result is not None
        assert result.id == "did:web:example.com"

    def test_resolve_did_key(self) -> None:
        """Test resolving did:key DID."""
        result = resolve_did("did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK")
        assert result is not None
        assert len(result.verification_method) > 0

    def test_resolve_unknown_did(self) -> None:
        """Test resolving unknown DID method."""
        result = resolve_did("did:unknown:123")
        assert result is not None  # Returns placeholder


class TestVerifyCredential:
    """Tests for verify_credential function."""

    def test_verify_valid_credential(self) -> None:
        """Test verifying a valid credential."""
        vc = VerifiableCredential(
            issuer="did:example:issuer",
            credential_subject=CredentialSubject(claims={"name": "Alice"}),
        )
        result = verify_credential(vc)
        assert result.valid is True
        assert "format_validation" in result.checks_performed

    def test_verify_missing_issuer(self) -> None:
        """Test verifying credential with missing issuer."""
        vc = VerifiableCredential(issuer="")
        result = verify_credential(vc)
        assert result.valid is False
        assert any("Missing issuer" in e for e in result.errors)

    def test_verify_json_string(self) -> None:
        """Test verifying from JSON string."""
        json_str = json.dumps({
            "@context": [VC_CONTEXT_V2],
            "type": ["VerifiableCredential"],
            "issuer": "did:example:issuer",
            "credentialSubject": {"name": "Bob"},
        })
        result = verify_credential(json_str)
        assert result.valid is True

    def test_verify_invalid_json(self) -> None:
        """Test verifying invalid JSON."""
        result = verify_credential("not valid json")
        assert result.valid is False
        assert any("Invalid JSON" in e for e in result.errors)

    def test_verify_dict(self) -> None:
        """Test verifying from dict."""
        data = {
            "@context": [VC_CONTEXT_V2],
            "issuer": "did:example:issuer",
            "credentialSubject": {},
        }
        result = verify_credential(data)
        assert result.valid is True

    def test_verify_trusted_issuer_match(self) -> None:
        """Test verifying with matching trusted issuer."""
        vc = VerifiableCredential(
            issuer="did:example:trusted",
            credential_subject=CredentialSubject(),
        )
        result = verify_credential(vc, trusted_issuers=["did:example:trusted"])
        assert result.issuer_trusted is True

    def test_verify_trusted_issuer_no_match(self) -> None:
        """Test verifying with non-matching trusted issuer."""
        vc = VerifiableCredential(
            issuer="did:example:untrusted",
            credential_subject=CredentialSubject(),
        )
        result = verify_credential(vc, trusted_issuers=["did:example:trusted"])
        assert result.valid is False
        assert result.issuer_trusted is False

    def test_verify_trusted_issuer_object(self) -> None:
        """Test verifying with issuer as object."""
        vc = VerifiableCredential(
            issuer={"id": "did:example:trusted", "name": "Issuer"},
            credential_subject=CredentialSubject(),
        )
        result = verify_credential(vc, trusted_issuers=["did:example:trusted"])
        assert result.issuer_trusted is True

    def test_verify_expired_credential(self) -> None:
        """Test verifying expired credential."""
        past = datetime.now(UTC) - timedelta(days=1)
        vc = VerifiableCredential(
            issuer="did:example:issuer",
            credential_subject=CredentialSubject(),
            valid_until=past,
        )
        result = verify_credential(vc, check_expiry=True)
        assert result.valid is False
        assert result.not_expired is False
        assert any("expired" in e for e in result.errors)

    def test_verify_not_yet_valid_credential(self) -> None:
        """Test verifying credential not yet valid."""
        future = datetime.now(UTC) + timedelta(days=1)
        vc = VerifiableCredential(
            issuer="did:example:issuer",
            credential_subject=CredentialSubject(),
            valid_from=future,
        )
        result = verify_credential(vc, check_expiry=True)
        assert result.valid is False
        assert result.not_expired is False
        assert any("not yet valid" in e for e in result.errors)

    def test_verify_valid_time_range(self) -> None:
        """Test verifying credential within valid time range."""
        now = datetime.now(UTC)
        vc = VerifiableCredential(
            issuer="did:example:issuer",
            credential_subject=CredentialSubject(),
            valid_from=now - timedelta(hours=1),
            valid_until=now + timedelta(days=365),
        )
        result = verify_credential(vc, check_expiry=True)
        assert result.not_expired is True

    def test_verify_skip_expiry_check(self) -> None:
        """Test verifying with expiry check disabled."""
        past = datetime.now(UTC) - timedelta(days=1)
        vc = VerifiableCredential(
            issuer="did:example:issuer",
            credential_subject=CredentialSubject(),
            valid_until=past,
        )
        result = verify_credential(vc, check_expiry=False)
        # Should pass because we skip expiry check
        assert "expiry" not in result.checks_performed

    def test_verify_ed25519_signature(self) -> None:
        """Test verifying Ed25519 signature."""
        proof = CredentialProof(
            type="Ed25519Signature2020",
            proof_value="valid_signature",
        )
        vc = VerifiableCredential(
            issuer="did:example:issuer",
            credential_subject=CredentialSubject(),
            proof=proof,
        )
        result = verify_credential(vc, check_signature=True)
        assert result.signature_valid is True

    def test_verify_signature_with_proof_list(self) -> None:
        """Test verifying with proof list."""
        proofs = [
            CredentialProof(type="Ed25519Signature2020", proof_value="sig"),
        ]
        vc = VerifiableCredential(
            issuer="did:example:issuer",
            credential_subject=CredentialSubject(),
            proof=proofs,
        )
        result = verify_credential(vc, check_signature=True)
        assert "signature" in result.checks_performed

    def test_verify_revocation_with_status(self) -> None:
        """Test verifying revocation status."""
        status = CredentialStatus(
            id="https://example.com/status",
            status_list_index=42,
            status_list_credential="https://example.com/cred",
        )
        vc = VerifiableCredential(
            issuer="did:example:issuer",
            credential_subject=CredentialSubject(),
            credential_status=status,
        )
        result = verify_credential(vc, check_revocation=True)
        assert "revocation" in result.checks_performed
        assert result.not_revoked is True


class TestVerifyPresentation:
    """Tests for verify_presentation function."""

    def test_verify_valid_presentation(self) -> None:
        """Test verifying valid presentation."""
        vc = VerifiableCredential(
            issuer="did:example:issuer",
            credential_subject=CredentialSubject(),
        )
        vp = VerifiablePresentation(
            holder="did:example:holder",
            verifiable_credential=[vc],
        )
        result = verify_presentation(vp)
        assert result.valid is True

    def test_verify_presentation_from_json_string(self) -> None:
        """Test verifying presentation from JSON string."""
        json_str = json.dumps({
            "@context": [VC_CONTEXT_V2],
            "type": ["VerifiablePresentation"],
            "holder": "did:example:holder",
            "verifiableCredential": [
                {
                    "@context": [VC_CONTEXT_V2],
                    "issuer": "did:example:issuer",
                    "credentialSubject": {},
                }
            ],
        })
        result = verify_presentation(json_str)
        assert result.valid is True

    def test_verify_presentation_from_dict(self) -> None:
        """Test verifying presentation from dict."""
        data = {
            "@context": [VC_CONTEXT_V2],
            "type": ["VerifiablePresentation"],
            "holder": "did:example:holder",
            "verifiableCredential": [
                {
                    "@context": [VC_CONTEXT_V2],
                    "issuer": "did:example:issuer",
                    "credentialSubject": {},
                }
            ],
        }
        result = verify_presentation(data)
        assert result.valid is True

    def test_verify_presentation_with_invalid_credential(self) -> None:
        """Test verifying presentation with invalid credential."""
        vc = VerifiableCredential(
            issuer="",  # Invalid - missing issuer
            credential_subject=CredentialSubject(),
        )
        vp = VerifiablePresentation(verifiable_credential=[vc])
        result = verify_presentation(vp)
        assert result.valid is False

    def test_verify_presentation_empty_credentials(self) -> None:
        """Test verifying presentation with no credentials."""
        vp = VerifiablePresentation(holder="did:example:holder")
        result = verify_presentation(vp)
        assert result.valid is True  # Empty is valid


class TestCreateCredential:
    """Tests for create_credential function."""

    def test_create_basic_credential(self) -> None:
        """Test creating basic credential."""
        subject = CredentialSubject(
            id="did:example:subject",
            claims={"name": "Alice"},
        )
        vc = create_credential(
            issuer="did:example:issuer",
            subject=subject,
        )
        assert vc.issuer == "did:example:issuer"
        assert vc.credential_subject.id == "did:example:subject"
        assert vc.valid_from is not None
        assert vc.valid_until is not None
        assert vc.id is not None
        assert vc.id.startswith("urn:uuid:")

    def test_create_credential_custom_type(self) -> None:
        """Test creating credential with custom type."""
        subject = CredentialSubject()
        vc = create_credential(
            issuer="did:example:issuer",
            subject=subject,
            credential_type="EducationalCredential",
        )
        assert "EducationalCredential" in vc.type
        assert "VerifiableCredential" in vc.type

    def test_create_credential_custom_id(self) -> None:
        """Test creating credential with custom ID."""
        subject = CredentialSubject()
        vc = create_credential(
            issuer="did:example:issuer",
            subject=subject,
            credential_id="urn:uuid:custom-id",
        )
        assert vc.id == "urn:uuid:custom-id"

    def test_create_credential_custom_validity(self) -> None:
        """Test creating credential with custom validity period."""
        subject = CredentialSubject()
        vc = create_credential(
            issuer="did:example:issuer",
            subject=subject,
            valid_for_days=30,
        )
        assert vc.valid_until is not None
        assert vc.valid_from is not None
        delta = vc.valid_until - vc.valid_from
        assert delta.days == 30

    def test_create_credential_custom_contexts(self) -> None:
        """Test creating credential with custom contexts."""
        subject = CredentialSubject()
        contexts = [VC_CONTEXT_V2, "https://example.com/custom"]
        vc = create_credential(
            issuer="did:example:issuer",
            subject=subject,
            contexts=contexts,
        )
        assert vc.context == contexts

    def test_create_credential_with_evidence(self) -> None:
        """Test creating credential with evidence."""
        subject = CredentialSubject()
        evidence = [{"type": "DocumentEvidence", "id": "https://example.com/evidence"}]
        vc = create_credential(
            issuer="did:example:issuer",
            subject=subject,
            evidence=evidence,
        )
        assert vc.evidence == evidence

    def test_create_credential_uses_context_mapping(self) -> None:
        """Test creating credential uses CREDENTIAL_CONTEXTS mapping."""
        subject = CredentialSubject()
        vc = create_credential(
            issuer="did:example:issuer",
            subject=subject,
            credential_type="EducationalCredential",
        )
        # Should use the predefined contexts for EducationalCredential
        assert len(vc.context) >= 1


class TestCreatePresentation:
    """Tests for create_presentation function."""

    def test_create_basic_presentation(self) -> None:
        """Test creating basic presentation."""
        vc = VerifiableCredential(issuer="did:example:issuer")
        vp = create_presentation(credentials=[vc])
        assert len(vp.verifiable_credential) == 1
        assert vp.id is not None
        assert vp.id.startswith("urn:uuid:")

    def test_create_presentation_with_holder(self) -> None:
        """Test creating presentation with holder."""
        vc = VerifiableCredential(issuer="did:example:issuer")
        vp = create_presentation(
            credentials=[vc],
            holder="did:example:holder",
        )
        assert vp.holder == "did:example:holder"

    def test_create_presentation_custom_id(self) -> None:
        """Test creating presentation with custom ID."""
        vc = VerifiableCredential(issuer="did:example:issuer")
        vp = create_presentation(
            credentials=[vc],
            presentation_id="urn:uuid:custom-vp",
        )
        assert vp.id == "urn:uuid:custom-vp"

    def test_create_presentation_multiple_credentials(self) -> None:
        """Test creating presentation with multiple credentials."""
        vc1 = VerifiableCredential(issuer="did:example:issuer1")
        vc2 = VerifiableCredential(issuer="did:example:issuer2")
        vp = create_presentation(credentials=[vc1, vc2])
        assert len(vp.verifiable_credential) == 2


class TestVerificationResult:
    """Tests for VerificationResult dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        result = VerificationResult(valid=True)
        assert result.valid is True
        assert result.credential is None
        assert result.errors == []
        assert result.warnings == []
        assert result.checks_performed == []
        assert result.signature_valid is None
        assert result.issuer_trusted is None
        assert result.not_expired is None
        assert result.not_revoked is None
        assert result.schema_valid is None
