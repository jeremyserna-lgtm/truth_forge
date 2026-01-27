"""Tests for hold isolation module.

Tests the HOLD1/HOLD2 boundary enforcement functionality.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from truth_forge.governance.hold_isolation import (
    HoldIsolation,
    HoldLayer,
    IsolationViolation,
    OperationType,
)


class TestHoldLayer:
    """Tests for HoldLayer enum."""

    def test_layer_values(self) -> None:
        """Test hold layer values."""
        assert HoldLayer.HOLD1.value == "hold1"
        assert HoldLayer.HOLD2.value == "hold2"
        assert HoldLayer.AGENT.value == "agent"


class TestOperationType:
    """Tests for OperationType enum."""

    def test_operation_values(self) -> None:
        """Test operation type values."""
        assert OperationType.READ.value == "read"
        assert OperationType.WRITE.value == "write"
        assert OperationType.APPEND.value == "append"
        assert OperationType.DELETE.value == "delete"
        assert OperationType.MODIFY.value == "modify"


class TestIsolationViolation:
    """Tests for IsolationViolation dataclass."""

    def test_violation_creation(self) -> None:
        """Test creating a violation record."""
        from datetime import UTC, datetime

        violation = IsolationViolation(
            timestamp=datetime.now(UTC),
            operation=OperationType.WRITE,
            source=HoldLayer.AGENT,
            target=HoldLayer.HOLD2,
            path=Path("/test/path"),
            reason="test violation",
            context={"key": "value"},
        )

        assert violation.operation == OperationType.WRITE
        assert violation.source == HoldLayer.AGENT
        assert violation.target == HoldLayer.HOLD2
        assert violation.reason == "test violation"


class TestHoldIsolation:
    """Tests for HoldIsolation class."""

    def test_external_write_to_hold1_allowed(self) -> None:
        """Test external write to HOLD1 is allowed."""
        isolation = HoldIsolation()

        result = isolation.check("write", "external", "hold1")

        assert result is True

    def test_external_write_to_hold2_denied(self) -> None:
        """Test external write to HOLD2 is denied (must go through AGENT)."""
        isolation = HoldIsolation()

        result = isolation.check("write", "external", "hold2")

        assert result is False

    def test_agent_read_from_hold1_allowed(self) -> None:
        """Test agent read from HOLD1 is allowed."""
        isolation = HoldIsolation()

        result = isolation.check("read", "agent", "hold1")

        assert result is True

    def test_agent_write_to_hold2_allowed(self) -> None:
        """Test agent write to HOLD2 is allowed."""
        isolation = HoldIsolation()

        result = isolation.check("write", "agent", "hold2")

        assert result is True

    def test_consumer_read_from_hold2_allowed(self) -> None:
        """Test consumer read from HOLD2 is allowed."""
        isolation = HoldIsolation()

        result = isolation.check("read", "consumer", "hold2")

        assert result is True

    def test_consumer_write_to_hold2_denied(self) -> None:
        """Test consumer write to HOLD2 is denied."""
        isolation = HoldIsolation()

        result = isolation.check("write", "consumer", "hold2")

        assert result is False

    def test_hold2_modify_denied(self) -> None:
        """Test HOLD2 modification is denied (immutable)."""
        isolation = HoldIsolation()

        result = isolation.check("modify", "agent", "hold2")

        assert result is False

    def test_check_with_reason_returns_reason(self) -> None:
        """Test check_with_reason returns detailed reason."""
        isolation = HoldIsolation()

        allowed, reason = isolation.check_with_reason("write", "external", "hold2")

        assert allowed is False
        assert "HOLD2 cannot receive direct external writes" in reason

    def test_check_with_reason_allowed(self) -> None:
        """Test check_with_reason for allowed flow."""
        isolation = HoldIsolation()

        allowed, reason = isolation.check_with_reason("write", "agent", "hold2")

        assert allowed is True
        assert reason == "allowed"

    def test_violations_recorded(self) -> None:
        """Test violations are recorded."""
        isolation = HoldIsolation()

        isolation.check("write", "external", "hold2")
        isolation.check("modify", "agent", "hold2")

        violations = isolation.get_violations()

        assert len(violations) == 2

    def test_clear_violations(self) -> None:
        """Test clearing violations."""
        isolation = HoldIsolation()

        isolation.check("write", "external", "hold2")
        isolation.check("write", "external", "hold2")

        count = isolation.clear_violations()

        assert count == 2
        assert len(isolation.get_violations()) == 0

    def test_strict_mode_denies_unknown_flows(self) -> None:
        """Test strict mode denies unknown flows."""
        isolation = HoldIsolation(strict_mode=True)

        # Unknown source "unknown_source" should be denied
        result = isolation.check("read", "unknown_source", "hold1")

        assert result is False

    def test_non_strict_mode_allows_unknown_flows(self) -> None:
        """Test non-strict mode allows unknown flows with warning."""
        isolation = HoldIsolation(strict_mode=False)

        # Unknown flow should be allowed in non-strict mode
        result = isolation.check("read", "unknown_source", "hold1")

        assert result is True

    def test_assert_allowed_raises_on_violation(self) -> None:
        """Test assert_allowed raises PermissionError on violation."""
        isolation = HoldIsolation()

        with pytest.raises(PermissionError) as exc_info:
            isolation.assert_allowed("write", "external", "hold2")

        assert "HOLD isolation violation" in str(exc_info.value)

    def test_assert_allowed_passes_when_allowed(self) -> None:
        """Test assert_allowed passes when flow is allowed."""
        isolation = HoldIsolation()

        # Should not raise
        isolation.assert_allowed("write", "agent", "hold2")

    def test_operation_type_normalization(self) -> None:
        """Test operation type is normalized from string."""
        isolation = HoldIsolation()

        # Uppercase should work
        result = isolation.check("WRITE", "agent", "hold2")
        assert result is True

    def test_hold_layer_normalization(self) -> None:
        """Test hold layer is normalized from string."""
        isolation = HoldIsolation()

        # Uppercase should work
        result = isolation.check("write", "agent", "HOLD2")
        assert result is True

    def test_invalid_operation_type_denied(self) -> None:
        """Test invalid operation type is denied."""
        isolation = HoldIsolation()

        allowed, reason = isolation.check_with_reason(
            "invalid_op", "agent", "hold2"
        )

        assert allowed is False
        assert "Unknown operation type" in reason

    def test_invalid_hold_layer_denied(self) -> None:
        """Test invalid hold layer is denied."""
        isolation = HoldIsolation()

        allowed, reason = isolation.check_with_reason(
            "write", "agent", "invalid_layer"
        )

        assert allowed is False
        assert "Unknown HOLD layer" in reason

    def test_path_recorded_in_violation(self) -> None:
        """Test path is recorded in violation."""
        isolation = HoldIsolation()
        test_path = Path("/test/file.txt")

        isolation.check("write", "external", "hold2", path=test_path)

        violations = isolation.get_violations()
        assert len(violations) == 1
        assert violations[0].path == test_path

    def test_context_recorded_in_violation(self) -> None:
        """Test context is recorded in violation."""
        isolation = HoldIsolation()
        test_context = {"user": "test", "action": "write"}

        isolation.check(
            "write", "external", "hold2", context=test_context
        )

        violations = isolation.get_violations()
        assert len(violations) == 1
        assert violations[0].context == test_context

    def test_external_append_to_hold1_allowed(self) -> None:
        """Test external append to HOLD1 is allowed."""
        isolation = HoldIsolation()

        result = isolation.check("append", "external", "hold1")

        assert result is True

    def test_agent_append_to_hold2_allowed(self) -> None:
        """Test agent append to HOLD2 is allowed."""
        isolation = HoldIsolation()

        result = isolation.check("append", "agent", "hold2")

        assert result is True

    def test_hold2_immutability_reason(self) -> None:
        """Test HOLD2 immutability gives correct reason."""
        isolation = HoldIsolation()

        allowed, reason = isolation.check_with_reason("modify", "agent", "hold2")

        assert allowed is False
        assert "immutable" in reason.lower()
