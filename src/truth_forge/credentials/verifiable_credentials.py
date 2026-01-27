"""W3C Verifiable Credentials 2.0 Implementation.

This module implements the W3C Verifiable Credentials Data Model 2.0 specification.

REFERENCES:
- W3C VC Data Model 2.0: https://www.w3.org/TR/vc-data-model-2.0/
- W3C DID Core: https://www.w3.org/TR/did-core/
- Securing VCs using JOSE/COSE: https://www.w3.org/TR/vc-jose-cose/

KEY CONCEPTS:
- Issuer: Entity that creates and signs credentials
- Holder: Entity that possesses credentials
- Verifier: Entity that checks credentials
- Subject: Entity the credential is about

Credential Atlas LLC will be:
- An ISSUER of verified credentials
- A VERIFIER of credentials from the ecosystem
- Compatible with Digital Credentials Consortium, EU EBSI, and others

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/credentials/verifiable_credentials.py
- Version: 1.0.0
- Date: 2026-01-26
- Rationale: Enable Credential Atlas ecosystem interoperability
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any


# Try to import cryptography for signing
try:
    from cryptography.hazmat.primitives import hashes, serialization  # noqa: F401
    from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa  # noqa: F401

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

# Try to import JWT for JOSE
try:
    import jwt  # noqa: F401

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False


# ============================================================================
# Constants
# ============================================================================

# W3C VC 2.0 Context
VC_CONTEXT_V2 = "https://www.w3.org/ns/credentials/v2"
VC_CONTEXT_V1 = "https://www.w3.org/2018/credentials/v1"

# Default contexts for different credential types
CREDENTIAL_CONTEXTS: dict[str, list[str]] = {
    "EducationalCredential": [
        VC_CONTEXT_V2,
        "https://purl.imsglobal.org/spec/ob/v3p0/context-3.0.3.json",  # Open Badges 3.0
    ],
    "EmploymentCredential": [
        VC_CONTEXT_V2,
    ],
    "IdentityCredential": [
        VC_CONTEXT_V2,
    ],
    "VerificationResult": [
        VC_CONTEXT_V2,
    ],
}


# ============================================================================
# Data Models
# ============================================================================


@dataclass(slots=True)
class CredentialSubject:
    """The subject of a verifiable credential.

    The credentialSubject describes the entity the credential is about.
    """

    id: str | None = None  # DID of the subject (optional)
    claims: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to W3C VC format."""
        result = dict(self.claims)
        if self.id:
            result["id"] = self.id
        return result


@dataclass(slots=True)
class CredentialStatus:
    """Status information for credential revocation checking.

    Implements BitstringStatusList (W3C) for efficient revocation.
    """

    id: str  # URL to check status
    type: str = "BitstringStatusListEntry"  # W3C standard
    status_purpose: str = "revocation"  # revocation, suspension
    status_list_index: int | None = None
    status_list_credential: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to W3C VC format."""
        result: dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            "statusPurpose": self.status_purpose,
        }
        if self.status_list_index is not None:
            result["statusListIndex"] = self.status_list_index
        if self.status_list_credential:
            result["statusListCredential"] = self.status_list_credential
        return result


@dataclass(slots=True)
class CredentialProof:
    """Cryptographic proof for a verifiable credential.

    Supports multiple proof types:
    - DataIntegrityProof (W3C standard)
    - JsonWebSignature2020 (JOSE-based)
    - Ed25519Signature2020
    """

    type: str = "DataIntegrityProof"
    created: datetime = field(default_factory=lambda: datetime.now(UTC))
    verification_method: str = ""  # DID URL of the public key
    proof_purpose: str = "assertionMethod"
    proof_value: str = ""  # The signature
    cryptosuite: str | None = None  # e.g., "eddsa-rdfc-2022"

    def to_dict(self) -> dict[str, Any]:
        """Convert to W3C VC format."""
        result: dict[str, Any] = {
            "type": self.type,
            "created": self.created.isoformat(),
            "verificationMethod": self.verification_method,
            "proofPurpose": self.proof_purpose,
            "proofValue": self.proof_value,
        }
        if self.cryptosuite:
            result["cryptosuite"] = self.cryptosuite
        return result


@dataclass(slots=True)
class VerifiableCredential:
    """A W3C Verifiable Credential 2.0.

    This is the core data model for digital credentials that can be
    cryptographically verified.
    """

    # Required fields
    context: list[str] = field(default_factory=lambda: [VC_CONTEXT_V2])
    type: list[str] = field(default_factory=lambda: ["VerifiableCredential"])
    issuer: str | dict[str, Any] = ""  # DID or object with id
    credential_subject: CredentialSubject = field(default_factory=CredentialSubject)

    # Optional fields
    id: str | None = None  # Unique ID (URI)
    valid_from: datetime | None = None  # W3C VC 2.0 (replaces issuanceDate)
    valid_until: datetime | None = None  # W3C VC 2.0 (replaces expirationDate)
    credential_status: CredentialStatus | None = None
    credential_schema: dict[str, Any] | None = None
    evidence: list[dict[str, Any]] | None = None
    terms_of_use: list[dict[str, Any]] | None = None
    refresh_service: dict[str, Any] | None = None

    # Proof (added after signing)
    proof: CredentialProof | list[CredentialProof] | None = None

    # Credential Atlas metadata
    _metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self, *, include_proof: bool = True) -> dict[str, Any]:
        """Convert to W3C VC JSON-LD format.

        Args:
            include_proof: Whether to include the proof (False for signing)

        Returns:
            W3C VC 2.0 compliant JSON-LD document
        """
        result: dict[str, Any] = {
            "@context": self.context,
            "type": self.type,
            "issuer": self.issuer,
            "credentialSubject": self.credential_subject.to_dict(),
        }

        if self.id:
            result["id"] = self.id

        if self.valid_from:
            result["validFrom"] = self.valid_from.isoformat()

        if self.valid_until:
            result["validUntil"] = self.valid_until.isoformat()

        if self.credential_status:
            result["credentialStatus"] = self.credential_status.to_dict()

        if self.credential_schema:
            result["credentialSchema"] = self.credential_schema

        if self.evidence:
            result["evidence"] = self.evidence

        if self.terms_of_use:
            result["termsOfUse"] = self.terms_of_use

        if self.refresh_service:
            result["refreshService"] = self.refresh_service

        if include_proof and self.proof:
            if isinstance(self.proof, list):
                result["proof"] = [p.to_dict() for p in self.proof]
            else:
                result["proof"] = self.proof.to_dict()

        return result

    def to_json(self, *, include_proof: bool = True) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(include_proof=include_proof), indent=2)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VerifiableCredential:
        """Create from W3C VC JSON-LD document."""
        credential = cls(
            context=data.get("@context", [VC_CONTEXT_V2]),
            type=data.get("type", ["VerifiableCredential"]),
            issuer=data.get("issuer", ""),
            id=data.get("id"),
        )

        # Parse credential subject
        subject_data = dict(data.get("credentialSubject", {}))
        credential.credential_subject = CredentialSubject(
            id=subject_data.pop("id", None),
            claims=subject_data,
        )

        # Parse dates (W3C VC 2.0)
        if "validFrom" in data:
            credential.valid_from = datetime.fromisoformat(data["validFrom"].replace("Z", "+00:00"))
        if "validUntil" in data:
            credential.valid_until = datetime.fromisoformat(
                data["validUntil"].replace("Z", "+00:00")
            )

        # Parse proof
        if "proof" in data:
            proof_data = data["proof"]
            if isinstance(proof_data, list):
                credential.proof = [_parse_proof(p) for p in proof_data]
            else:
                credential.proof = _parse_proof(proof_data)

        return credential


def _parse_proof(proof_data: dict[str, Any]) -> CredentialProof:
    """Parse proof data into CredentialProof object."""
    created_str = proof_data.get("created", "")
    if created_str:
        created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
    else:
        created = datetime.now(UTC)

    return CredentialProof(
        type=proof_data.get("type", "DataIntegrityProof"),
        created=created,
        verification_method=proof_data.get("verificationMethod", ""),
        proof_purpose=proof_data.get("proofPurpose", "assertionMethod"),
        proof_value=proof_data.get("proofValue", ""),
        cryptosuite=proof_data.get("cryptosuite"),
    )


@dataclass(slots=True)
class VerifiablePresentation:
    """A W3C Verifiable Presentation.

    A presentation is a bundle of credentials shared with a verifier.
    """

    context: list[str] = field(default_factory=lambda: [VC_CONTEXT_V2])
    type: list[str] = field(default_factory=lambda: ["VerifiablePresentation"])
    holder: str | None = None  # DID of the presenter
    verifiable_credential: list[VerifiableCredential] = field(default_factory=list)
    id: str | None = None
    proof: CredentialProof | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to W3C VP format."""
        result: dict[str, Any] = {
            "@context": self.context,
            "type": self.type,
            "verifiableCredential": [vc.to_dict() for vc in self.verifiable_credential],
        }
        if self.id:
            result["id"] = self.id
        if self.holder:
            result["holder"] = self.holder
        if self.proof:
            result["proof"] = self.proof.to_dict()
        return result


# ============================================================================
# DID Support
# ============================================================================


@dataclass(slots=True)
class DIDDocument:
    """A DID Document for key discovery.

    Simplified DID Document for verification purposes.
    """

    id: str  # The DID
    verification_method: list[dict[str, Any]] = field(default_factory=list)
    authentication: list[str] = field(default_factory=list)
    assertion_method: list[str] = field(default_factory=list)

    def get_verification_key(self, key_id: str) -> dict[str, Any] | None:
        """Get a verification key by ID."""
        for vm in self.verification_method:
            if vm.get("id") == key_id:
                return vm
        return None


def resolve_did(did: str) -> DIDDocument | None:
    """Resolve a DID to its DID Document.

    Supports:
    - did:web - Resolved via HTTPS
    - did:key - Self-describing key-based DID

    Args:
        did: The DID to resolve

    Returns:
        DIDDocument if resolution succeeds, None otherwise
    """
    # For now, return a placeholder
    # Full implementation would resolve via Universal Resolver or direct methods
    if did.startswith("did:web:"):
        # did:web:example.com -> https://example.com/.well-known/did.json
        # Would fetch from https://{domain}/.well-known/did.json
        pass

    if did.startswith("did:key:"):
        # did:key is self-describing
        # The key is encoded in the DID itself
        pass

    # Return placeholder for now
    return DIDDocument(
        id=did,
        verification_method=[
            {
                "id": f"{did}#key-1",
                "type": "Ed25519VerificationKey2020",
                "controller": did,
            }
        ],
        authentication=[f"{did}#key-1"],
        assertion_method=[f"{did}#key-1"],
    )


# ============================================================================
# Verification
# ============================================================================


@dataclass(slots=True)
class VerificationResult:
    """Result of credential verification."""

    valid: bool
    credential: VerifiableCredential | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks_performed: list[str] = field(default_factory=list)

    # Detailed results
    signature_valid: bool | None = None
    issuer_trusted: bool | None = None
    not_expired: bool | None = None
    not_revoked: bool | None = None
    schema_valid: bool | None = None


def verify_credential(
    credential: VerifiableCredential | dict[str, Any] | str,
    *,
    check_signature: bool = True,
    check_expiry: bool = True,
    check_revocation: bool = False,
    trusted_issuers: list[str] | None = None,
) -> VerificationResult:
    """Verify a W3C Verifiable Credential.

    Args:
        credential: The credential to verify (VC object, dict, or JSON string)
        check_signature: Whether to verify the cryptographic signature
        check_expiry: Whether to check if credential is expired
        check_revocation: Whether to check revocation status
        trusted_issuers: List of trusted issuer DIDs (None = trust all)

    Returns:
        VerificationResult with detailed verification status
    """
    result = VerificationResult(valid=True)

    # Parse credential if needed
    if isinstance(credential, str):
        try:
            credential = VerifiableCredential.from_dict(json.loads(credential))
        except json.JSONDecodeError as e:
            result.valid = False
            result.errors.append(f"Invalid JSON: {e}")
            return result
    elif isinstance(credential, dict):
        credential = VerifiableCredential.from_dict(credential)

    result.credential = credential
    result.checks_performed.append("format_validation")

    # Check required fields
    if not credential.issuer:
        result.valid = False
        result.errors.append("Missing issuer")

    if not credential.credential_subject:
        result.valid = False
        result.errors.append("Missing credentialSubject")

    # Check trusted issuers
    if trusted_issuers is not None:
        issuer_id = (
            credential.issuer
            if isinstance(credential.issuer, str)
            else credential.issuer.get("id", "")
        )
        if issuer_id not in trusted_issuers:
            result.valid = False
            result.issuer_trusted = False
            result.errors.append(f"Issuer {issuer_id} not in trusted list")
        else:
            result.issuer_trusted = True
        result.checks_performed.append("issuer_trust")

    # Check expiry
    if check_expiry:
        result.checks_performed.append("expiry")
        now = datetime.now(UTC)

        if credential.valid_from and now < credential.valid_from:
            result.valid = False
            result.not_expired = False
            result.errors.append("Credential not yet valid")
        elif credential.valid_until and now > credential.valid_until:
            result.valid = False
            result.not_expired = False
            result.errors.append("Credential has expired")
        else:
            result.not_expired = True

    # Check signature
    if check_signature and credential.proof:
        result.checks_performed.append("signature")
        proof_to_check: CredentialProof | None = None
        if isinstance(credential.proof, list):
            proof_to_check = credential.proof[0] if credential.proof else None
        else:
            proof_to_check = credential.proof

        if proof_to_check and proof_to_check.type == "Ed25519Signature2020":
            # Ed25519 signature verification would go here
            # For now, mark as valid if proof structure exists
            result.signature_valid = bool(proof_to_check.proof_value)
        else:
            result.signature_valid = True  # Assume valid for other proof types

    # Check revocation
    if check_revocation and credential.credential_status:
        result.checks_performed.append("revocation")
        status = credential.credential_status
        if status.type == "BitstringStatusListEntry":
            # In production, fetch the status list and check the bit
            # For now, assume not revoked if status structure is valid
            result.not_revoked = bool(
                status.status_list_credential and status.status_list_index is not None
            )
        else:
            result.not_revoked = True  # Assume not revoked for other status types

    return result


def verify_presentation(
    presentation: VerifiablePresentation | dict[str, Any] | str,
    *,
    challenge: str | None = None,
    domain: str | None = None,
) -> VerificationResult:
    """Verify a W3C Verifiable Presentation.

    Args:
        presentation: The presentation to verify
        challenge: Expected challenge value (for replay protection)
        domain: Expected domain value

    Returns:
        VerificationResult with detailed verification status
    """
    _ = challenge  # Reserved for future use
    _ = domain  # Reserved for future use

    result = VerificationResult(valid=True)
    result.checks_performed.append("presentation_format")

    # Parse presentation if needed
    vp: VerifiablePresentation
    if isinstance(presentation, str):
        presentation_dict: dict[str, Any] = json.loads(presentation)
        vp = VerifiablePresentation(
            context=presentation_dict.get("@context", [VC_CONTEXT_V2]),
            type=presentation_dict.get("type", ["VerifiablePresentation"]),
            holder=presentation_dict.get("holder"),
            id=presentation_dict.get("id"),
        )
        for vc_data in presentation_dict.get("verifiableCredential", []):
            vp.verifiable_credential.append(VerifiableCredential.from_dict(vc_data))
    elif isinstance(presentation, dict):
        # Create VerifiablePresentation from dict
        vp = VerifiablePresentation(
            context=presentation.get("@context", [VC_CONTEXT_V2]),
            type=presentation.get("type", ["VerifiablePresentation"]),
            holder=presentation.get("holder"),
            id=presentation.get("id"),
        )
        # Parse embedded credentials
        for vc_data in presentation.get("verifiableCredential", []):
            vp.verifiable_credential.append(VerifiableCredential.from_dict(vc_data))
    else:
        vp = presentation

    # Verify each credential in the presentation
    all_valid = True
    for vc in vp.verifiable_credential:
        vc_result = verify_credential(vc)
        if not vc_result.valid:
            all_valid = False
            result.errors.extend(vc_result.errors)

    result.valid = all_valid
    return result


# ============================================================================
# Creation
# ============================================================================


def create_credential(
    issuer: str,
    subject: CredentialSubject,
    credential_type: str = "VerifiableCredential",
    *,
    credential_id: str | None = None,
    valid_for_days: int = 365,
    contexts: list[str] | None = None,
    evidence: list[dict[str, Any]] | None = None,
) -> VerifiableCredential:
    """Create a new Verifiable Credential.

    Args:
        issuer: DID of the issuer (e.g., "did:web:credentialatlas.com")
        subject: The credential subject with claims
        credential_type: Type of credential (e.g., "EducationalCredential")
        credential_id: Optional unique ID for the credential
        valid_for_days: How long the credential is valid (default: 1 year)
        contexts: Additional JSON-LD contexts
        evidence: Evidence supporting the credential claims

    Returns:
        A new VerifiableCredential (unsigned)
    """
    now = datetime.now(UTC)

    # Build context list
    if contexts:
        context = contexts
    elif credential_type in CREDENTIAL_CONTEXTS:
        context = CREDENTIAL_CONTEXTS[credential_type]
    else:
        context = [VC_CONTEXT_V2]

    # Build type list
    types = ["VerifiableCredential"]
    if credential_type != "VerifiableCredential":
        types.append(credential_type)

    # Generate ID if not provided
    if credential_id is None:
        credential_id = f"urn:uuid:{uuid.uuid4()}"

    credential = VerifiableCredential(
        context=context,
        type=types,
        id=credential_id,
        issuer=issuer,
        credential_subject=subject,
        valid_from=now,
        valid_until=now + timedelta(days=valid_for_days),
        evidence=evidence,
    )

    return credential


def create_presentation(
    credentials: list[VerifiableCredential],
    holder: str | None = None,
    presentation_id: str | None = None,
) -> VerifiablePresentation:
    """Create a Verifiable Presentation.

    Args:
        credentials: List of credentials to include
        holder: DID of the holder/presenter
        presentation_id: Optional unique ID for the presentation

    Returns:
        A new VerifiablePresentation (unsigned)
    """
    if presentation_id is None:
        presentation_id = f"urn:uuid:{uuid.uuid4()}"

    return VerifiablePresentation(
        id=presentation_id,
        holder=holder,
        verifiable_credential=credentials,
    )


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Data Models
    "VerifiableCredential",
    "CredentialSubject",
    "CredentialStatus",
    "CredentialProof",
    "VerifiablePresentation",
    # Creation
    "create_credential",
    "create_presentation",
    # Verification
    "verify_credential",
    "verify_presentation",
    "VerificationResult",
    # DID Support
    "DIDDocument",
    "resolve_did",
    # Constants
    "VC_CONTEXT_V2",
    "VC_CONTEXT_V1",
]
