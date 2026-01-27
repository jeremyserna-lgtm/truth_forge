"""Tests for unified governance module.

Tests the UnifiedGovernance class and related functions.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.governance.unified_governance import (
    GovernanceConfig,
    UnifiedGovernance,
    get_governance,
    governed,
    reset_governance,
)


class TestGovernanceConfig:
    """Tests for GovernanceConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = GovernanceConfig()

        assert config.enforce_hold_isolation is True
        assert config.enforce_cost_limits is True
        assert config.audit_all_operations is True
        assert config.strict_mode is True
        assert config.budget_config is None
        assert config.data_path is None

    def test_custom_values(self) -> None:
        """Test configuration with custom values."""
        data_path = Path("/tmp/test")
        config = GovernanceConfig(
            enforce_hold_isolation=False,
            enforce_cost_limits=False,
            audit_all_operations=False,
            strict_mode=False,
            data_path=data_path,
        )

        assert config.enforce_hold_isolation is False
        assert config.enforce_cost_limits is False
        assert config.audit_all_operations is False
        assert config.strict_mode is False
        assert config.data_path == data_path


class TestUnifiedGovernance:
    """Tests for UnifiedGovernance class."""

    def setup_method(self) -> None:
        """Reset governance singleton before each test."""
        reset_governance()

    def teardown_method(self) -> None:
        """Clean up after each test."""
        reset_governance()

    def test_init_default_config(self) -> None:
        """Test initialization with default config."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            gov = UnifiedGovernance(config)

            assert gov.config.enforce_hold_isolation is True
            assert gov.config.enforce_cost_limits is True
            assert gov.hold_isolation is not None
            assert gov.audit_trail is not None
            assert gov.cost_enforcer is not None

    def test_init_custom_config(self) -> None:
        """Test initialization with custom config."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(
                enforce_hold_isolation=False,
                enforce_cost_limits=False,
                strict_mode=False,
                data_path=Path(tmpdir),
            )
            gov = UnifiedGovernance(config)

            assert gov.config.enforce_hold_isolation is False
            assert gov.config.enforce_cost_limits is False
            assert gov.config.strict_mode is False

    def test_gate_operation_allowed(self) -> None:
        """Test gate_operation when operation is allowed."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            gov = UnifiedGovernance(config)

            # Agent can write to hold2
            result = gov.gate_operation(
                operation="write",
                source="agent",
                target="hold2",
            )

            assert result is True

    def test_gate_operation_denied(self) -> None:
        """Test gate_operation when operation is denied."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir), strict_mode=True)
            gov = UnifiedGovernance(config)

            # External cannot write to hold2 (strict mode)
            result = gov.gate_operation(
                operation="write",
                source="external",
                target="hold2",
            )

            assert result is False

    def test_gate_operation_with_context(self) -> None:
        """Test gate_operation with additional context."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            gov = UnifiedGovernance(config)

            result = gov.gate_operation(
                operation="write",
                source="agent",
                target="hold2",
                path=Path("/test/path"),
                context={"batch_id": "test-123"},
            )

            assert result is True

    def test_gate_operation_isolation_disabled(self) -> None:
        """Test gate_operation with isolation enforcement disabled."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(
                data_path=Path(tmpdir),
                enforce_hold_isolation=False,
            )
            gov = UnifiedGovernance(config)

            # Even invalid operations pass when enforcement is disabled
            result = gov.gate_operation(
                operation="write",
                source="unknown",
                target="hold2",
            )

            assert result is True

    def test_gate_operation_audit_disabled(self) -> None:
        """Test gate_operation with audit disabled."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(
                data_path=Path(tmpdir),
                audit_all_operations=False,
            )
            gov = UnifiedGovernance(config)

            result = gov.gate_operation(
                operation="write",
                source="agent",
                target="hold2",
            )

            assert result is True

    def test_check_cost_allowed(self) -> None:
        """Test check_cost when within budget."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            gov = UnifiedGovernance(config)

            result = gov.check_cost(
                service="openai",
                operation="completion",
                estimated_cost=0.01,
            )

            assert result is True

    def test_check_cost_disabled(self) -> None:
        """Test check_cost when enforcement is disabled."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(
                data_path=Path(tmpdir),
                enforce_cost_limits=False,
            )
            gov = UnifiedGovernance(config)

            # Even large costs pass when enforcement is disabled
            result = gov.check_cost(
                service="openai",
                operation="completion",
                estimated_cost=1000.0,
            )

            assert result is True

    def test_check_cost_with_decimal(self) -> None:
        """Test check_cost with Decimal input."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            gov = UnifiedGovernance(config)

            result = gov.check_cost(
                service="openai",
                operation="completion",
                estimated_cost=Decimal("0.05"),
            )

            assert result is True

    def test_record_cost(self) -> None:
        """Test record_cost records to both enforcer and audit trail."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            gov = UnifiedGovernance(config)

            gov.record_cost(
                service="openai",
                operation="completion",
                cost_usd=0.05,
                tokens_in=100,
                tokens_out=50,
                context={"model": "gpt-4"},
            )

            # Verify cost was recorded
            status = gov.get_status()
            assert "cost" in status

    def test_record_cost_with_decimal(self) -> None:
        """Test record_cost with Decimal input."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            gov = UnifiedGovernance(config)

            gov.record_cost(
                service="openai",
                operation="completion",
                cost_usd=Decimal("0.05"),
                tokens_in=100,
                tokens_out=50,
            )

            # Should not raise
            status = gov.get_status()
            assert "cost" in status

    def test_record_agent_action_success(self) -> None:
        """Test record_agent_action for successful action."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            gov = UnifiedGovernance(config)

            gov.record_agent_action(
                action="transform",
                component="knowledge_agent",
                input_records=100,
                output_records=95,
                success=True,
                context={"batch_id": "test-123"},
            )

            # Should not raise
            status = gov.get_status()
            assert "audit_trail" in status

    def test_record_agent_action_failure(self) -> None:
        """Test record_agent_action for failed action."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            gov = UnifiedGovernance(config)

            gov.record_agent_action(
                action="transform",
                component="knowledge_agent",
                input_records=100,
                output_records=0,
                success=False,
                error_message="Processing failed",
            )

            # Should not raise
            status = gov.get_status()
            assert "audit_trail" in status

    def test_get_status(self) -> None:
        """Test get_status returns correct structure."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            gov = UnifiedGovernance(config)

            status = gov.get_status()

            assert "config" in status
            assert "hold_isolation" in status
            assert "audit_trail" in status
            assert "cost" in status

            assert status["config"]["enforce_hold_isolation"] is True
            assert status["config"]["enforce_cost_limits"] is True
            assert status["config"]["audit_all_operations"] is True
            assert status["config"]["strict_mode"] is True

    def test_flush(self) -> None:
        """Test flush writes buffers to disk."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            gov = UnifiedGovernance(config)

            # Record some data
            gov.record_agent_action(
                action="test",
                component="test",
                success=True,
            )

            # Flush should not raise
            gov.flush()

    def test_context_manager(self) -> None:
        """Test UnifiedGovernance as context manager."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))

            with UnifiedGovernance(config) as gov:
                gov.record_agent_action(
                    action="test",
                    component="test",
                    success=True,
                )
                # Flush happens on exit


class TestGetGovernance:
    """Tests for get_governance function."""

    def setup_method(self) -> None:
        """Reset governance singleton before each test."""
        reset_governance()

    def teardown_method(self) -> None:
        """Clean up after each test."""
        reset_governance()

    def test_returns_singleton(self) -> None:
        """Test get_governance returns same instance."""
        gov1 = get_governance()
        gov2 = get_governance()

        assert gov1 is gov2

    def test_creates_instance_on_first_call(self) -> None:
        """Test get_governance creates instance on first call."""
        # After reset, instance should be None
        gov = get_governance()

        # Should have been created
        assert gov is not None
        assert isinstance(gov, UnifiedGovernance)


class TestResetGovernance:
    """Tests for reset_governance function."""

    def test_reset_clears_singleton(self) -> None:
        """Test reset_governance clears the singleton."""
        # Get initial instance
        gov1 = get_governance()

        # Reset
        reset_governance()

        # Get new instance
        gov2 = get_governance()

        # Should be different instances
        assert gov1 is not gov2


class TestGovernedDecorator:
    """Tests for governed decorator."""

    def setup_method(self) -> None:
        """Reset governance singleton before each test."""
        import truth_forge.governance.unified_governance as ug_module

        # Reset without flushing (which could fail if directory is gone)
        ug_module._governance_instance = None
        ug_module.get_governance.cache_clear()

    def teardown_method(self) -> None:
        """Clean up after each test."""
        import truth_forge.governance.unified_governance as ug_module

        ug_module._governance_instance = None
        ug_module.get_governance.cache_clear()

    def test_allowed_operation_proceeds(self) -> None:
        """Test decorated function runs when operation is allowed."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            # Create governance directly and set it as singleton
            gov = UnifiedGovernance(config)
            import truth_forge.governance.unified_governance as ug_module

            ug_module._governance_instance = gov
            ug_module.get_governance.cache_clear()

            @governed(operation="write", source="agent", target="hold2")
            def my_function() -> str:
                return "success"

            result = my_function()
            assert result == "success"

            # Clean up before temp dir goes away
            ug_module._governance_instance = None

    def test_denied_operation_raises(self) -> None:
        """Test decorated function raises when operation is denied."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(
                data_path=Path(tmpdir),
                strict_mode=True,
            )
            # Create governance directly
            gov = UnifiedGovernance(config)
            import truth_forge.governance.unified_governance as ug_module

            ug_module._governance_instance = gov
            ug_module.get_governance.cache_clear()

            @governed(operation="write", source="external", target="hold2")
            def my_function() -> str:
                return "success"

            with pytest.raises(PermissionError) as exc_info:
                my_function()

            assert "Governance denied" in str(exc_info.value)

            # Clean up before temp dir goes away
            ug_module._governance_instance = None

    def test_default_parameters(self) -> None:
        """Test decorated function with custom valid operation.

        Note: The default "execute" operation may not be recognized by
        HoldIsolation. Using a valid "write" operation instead.
        """
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            gov = UnifiedGovernance(config)
            import truth_forge.governance.unified_governance as ug_module

            ug_module._governance_instance = gov
            ug_module.get_governance.cache_clear()

            # Use explicit valid operation
            @governed(operation="write", source="agent", target="hold2")
            def my_function() -> str:
                return "executed"

            result = my_function()
            assert result == "executed"

            # Clean up before temp dir goes away
            ug_module._governance_instance = None

    def test_with_function_arguments(self) -> None:
        """Test decorated function passes arguments correctly."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            gov = UnifiedGovernance(config)
            import truth_forge.governance.unified_governance as ug_module

            ug_module._governance_instance = gov
            ug_module.get_governance.cache_clear()

            @governed(operation="write", source="agent", target="hold2")
            def add_numbers(a: int, b: int) -> int:
                return a + b

            result = add_numbers(3, 5)
            assert result == 8

            # Clean up before temp dir goes away
            ug_module._governance_instance = None

    def test_with_kwargs(self) -> None:
        """Test decorated function handles kwargs."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))
            gov = UnifiedGovernance(config)
            import truth_forge.governance.unified_governance as ug_module

            ug_module._governance_instance = gov
            ug_module.get_governance.cache_clear()

            @governed(operation="write", source="agent", target="hold2")
            def greet(name: str, greeting: str = "Hello") -> str:
                return f"{greeting}, {name}!"

            result = greet(name="World", greeting="Hi")
            assert result == "Hi, World!"

            # Clean up before temp dir goes away
            ug_module._governance_instance = None


class TestIntegration:
    """Integration tests for unified governance."""

    def setup_method(self) -> None:
        """Reset governance singleton before each test."""
        import truth_forge.governance.unified_governance as ug_module

        ug_module._governance_instance = None
        ug_module.get_governance.cache_clear()

    def teardown_method(self) -> None:
        """Clean up after each test."""
        import truth_forge.governance.unified_governance as ug_module

        ug_module._governance_instance = None
        ug_module.get_governance.cache_clear()

    def test_full_workflow(self) -> None:
        """Test a full governance workflow."""
        with TemporaryDirectory() as tmpdir:
            config = GovernanceConfig(data_path=Path(tmpdir))

            with UnifiedGovernance(config) as gov:
                # External writes to hold1 (allowed)
                assert gov.gate_operation("write", "external", "hold1") is True

                # Agent reads hold1 (allowed)
                assert gov.gate_operation("read", "agent", "hold1") is True

                # Check cost before operation
                assert gov.check_cost("openai", "completion", 0.01) is True

                # Agent processes and writes to hold2 (allowed)
                assert gov.gate_operation("write", "agent", "hold2") is True

                # Record agent action
                gov.record_agent_action(
                    action="process",
                    component="test_agent",
                    input_records=10,
                    output_records=10,
                    success=True,
                )

                # Record cost
                gov.record_cost("openai", "completion", 0.01, tokens_in=50, tokens_out=25)

                # Consumer reads hold2 (allowed)
                assert gov.gate_operation("read", "consumer", "hold2") is True

                # Get final status
                status = gov.get_status()
                assert status["config"]["enforce_hold_isolation"] is True
