"""Primitive Credentials - W3C Verifiable Credentials Support.

This package provides W3C Verifiable Credentials 2.0 implementation:
- VerifiableCredential: Create and sign credentials
- VerifiablePresentation: Bundle credentials for sharing
- CredentialVerifier: Verify credentials from any W3C-compliant issuer

REFERENCES:
- W3C VC Data Model 2.0: https://www.w3.org/TR/vc-data-model-2.0/
- W3C VC Implementation Guide: https://www.w3.org/TR/vc-imp-guide/

THE_PATTERN: Credential Atlas becomes a W3C-compliant issuer and verifier,
enabling interoperability with the entire digital credentials ecosystem.

Usage:
    from truth_forge.credentials import (
        VerifiableCredential,
        CredentialSubject,
        create_credential,
        verify_credential,
    )

    # Create a credential
    credential = create_credential(
        issuer="did:web:credentialatlas.com",
        subject=CredentialSubject(
            id="did:example:student123",
            claims={"degree": "Bachelor of Science", "institution": "MIT"}
        ),
        credential_type="EducationalCredential",
    )

    # Verify a credential
    result = verify_credential(credential)

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/credentials/
- Version: 1.0.0
- Date: 2026-01-26
- Rationale: Enable Credential Atlas ecosystem interoperability
"""

from __future__ import annotations

from truth_forge.credentials.verifiable_credentials import (
    # Constants
    VC_CONTEXT_V1,
    VC_CONTEXT_V2,
    # Data Models
    CredentialProof,
    CredentialStatus,
    CredentialSubject,
    # DID Support
    DIDDocument,
    VerifiableCredential,
    VerifiablePresentation,
    # Verification
    VerificationResult,
    # Creation
    create_credential,
    create_presentation,
    resolve_did,
    verify_credential,
    verify_presentation,
)


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
