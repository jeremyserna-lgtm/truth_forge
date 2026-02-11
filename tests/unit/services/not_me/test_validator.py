"""Tests for validator module."""

from __future__ import annotations

from unittest.mock import Mock, patch

from truth_forge.services.not_me.truth_atom import (
    SurplusType,
    SurplusVector,
    TruthAtom,
    VerificationStatus,
)
from truth_forge.services.not_me.validator import (
    JustificationOutcome,
    TruthAtomValidator,
    ValidationRequest,
    ValidationResult,
    ValidatorVerdict,
    get_validator,
)


class TestValidatorVerdict:
    """Test ValidatorVerdict enum."""

    def test_verdict_values(self) -> None:
        """Test verdict enum values."""
        assert ValidatorVerdict.APPROVED.value == "approved"
        assert ValidatorVerdict.REJECTED.value == "rejected"
        assert ValidatorVerdict.NEEDS_JUSTIFICATION.value == "needs_justification"


class TestJustificationOutcome:
    """Test JustificationOutcome enum."""

    def test_outcome_values(self) -> None:
        """Test outcome enum values."""
        assert JustificationOutcome.ACCEPTED.value == "accepted"
        assert JustificationOutcome.SACRED_FRACTURE.value == "fracture"


def _make_test_atom(content: str = "Test", source_id: str = "source-123") -> TruthAtom:
    """Helper to create a TruthAtom with correct API for tests."""
    return TruthAtom(
        content=content,
        source_id=source_id,
        surplus_vector=SurplusVector(
            surplus_type=SurplusType.PATTERN,
            description="Test surplus",
        ),
    )


class TestValidationRequest:
    """Test ValidationRequest dataclass."""

    def test_creation(self) -> None:
        """Test creating ValidationRequest."""
        atom = _make_test_atom()
        request = ValidationRequest(atom=atom, context="Additional context")
        assert request.atom == atom
        assert request.context == "Additional context"
        assert request.require_justification is False
        assert request.max_justification_rounds == 3


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_creation(self) -> None:
        """Test creating ValidationResult."""
        atom = _make_test_atom()
        result = ValidationResult(
            atom=atom,
            verdict=ValidatorVerdict.APPROVED,
            justification_rounds=0,
        )
        assert result.atom == atom
        assert result.verdict == ValidatorVerdict.APPROVED
        assert result.justification_rounds == 0


class TestTruthAtomValidator:
    """Test TruthAtomValidator class."""

    def test_init(self) -> None:
        """Test validator initialization."""
        validator = TruthAtomValidator()
        assert validator.provider is not None
        assert validator.model == "gemini-2.0-flash"
        assert validator.temperature == 0.3

    def test_init_custom(self) -> None:
        """Test validator initialization with custom values."""
        mock_provider = Mock()
        validator = TruthAtomValidator(provider=mock_provider, model="custom-model")
        assert validator.provider == mock_provider
        assert validator.model == "custom-model"

    def test_validate_approved(self) -> None:
        """Test validation with approved verdict."""
        mock_provider = Mock()
        mock_response = Mock()
        mock_response.content = '{"verdict": "APPROVED", "reasoning": "Valid", "confidence": 0.9}'
        mock_provider.complete.return_value = mock_response

        validator = TruthAtomValidator(provider=mock_provider)
        atom = _make_test_atom(content="Test atom")

        request = ValidationRequest(atom=atom)
        result = validator.validate(request)

        assert result.verdict == ValidatorVerdict.APPROVED
        assert result.atom.verification_status == VerificationStatus.VALIDATED

    def test_validate_rejected(self) -> None:
        """Test validation with rejected verdict."""
        mock_provider = Mock()
        mock_response = Mock()
        mock_response.content = '{"verdict": "REJECTED", "reasoning": "Invalid", "confidence": 0.8}'
        mock_provider.complete.return_value = mock_response

        validator = TruthAtomValidator(provider=mock_provider)
        atom = _make_test_atom()

        request = ValidationRequest(atom=atom)
        result = validator.validate(request)

        assert result.verdict == ValidatorVerdict.REJECTED
        assert result.atom.verification_status == VerificationStatus.REJECTED

    def test_validate_provider_error(self) -> None:
        """Test validation handles provider errors."""
        from truth_forge.gateway.types import ProviderError

        mock_provider = Mock()
        mock_provider.complete.side_effect = ProviderError("Provider error", provider="gemini")

        validator = TruthAtomValidator(provider=mock_provider)
        atom = _make_test_atom()

        request = ValidationRequest(atom=atom)
        result = validator.validate(request)

        # Should handle error gracefully (ABSTAIN when provider unavailable)
        assert result.verdict in [ValidatorVerdict.ABSTAIN, ValidatorVerdict.REJECTED]


class TestGetValidator:
    """Test get_validator function."""

    @patch("truth_forge.services.not_me.validator._validator", None)
    def test_get_validator_creates_instance(self) -> None:
        """Test get_validator creates singleton instance."""
        validator1 = get_validator()
        validator2 = get_validator()
        assert validator1 is validator2  # Should be same instance
