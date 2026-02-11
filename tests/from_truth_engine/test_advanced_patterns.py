"""Tests for Advanced Python Patterns - Reproduction Requirement.

These tests verify the advanced Python patterns implemented in Primitive/core/
are working correctly. All patterns are required for organism reproduction.

MOLT LINEAGE:
- Source: framework/standards/REPRODUCTION_CHECKLIST.md Category 16
- Rationale: Verify pattern compliance for reproduction gate
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any

import pytest


# =============================================================================
# Test TypedDict Definitions
# =============================================================================

class TestTypedDicts:
    """Test TypedDict definitions from truth_forge.core.typed_dicts."""

    def test_spark_result_structure(self):
        """SparkResult should have required keys."""
        from truth_forge.core.typed_dicts import SparkResult
        
        # Create a valid SparkResult
        result: SparkResult = {
            "success": True,
            "spark": {"id": "spark_123"},
            "token": "jwt_token_here",
        }
        
        assert result["success"] is True
        assert "spark" in result
        assert "token" in result

    def test_service_state_dict(self):
        """ServiceStateDict should have status and health."""
        from truth_forge.core.typed_dicts import ServiceStateDict
        
        state: ServiceStateDict = {
            "status": "on",
            "health": "healthy",
            "last_activity": None,
            "metrics": {"uptime_seconds": 100.0, "operations": 5, "errors": 0},
            "errors": [],
        }
        
        assert state["status"] == "on"
        assert state["health"] == "healthy"

    def test_operation_result(self):
        """OperationResult should work for success and failure."""
        from truth_forge.core.typed_dicts import OperationResult
        
        success: OperationResult = {
            "success": True,
            "message": "Operation completed",
        }
        
        failure: OperationResult = {
            "success": False,
            "message": "Operation failed",
            "error": "Something went wrong",
        }
        
        assert success["success"] is True
        assert failure["success"] is False


# =============================================================================
# Test Protocol Definitions
# =============================================================================

class TestProtocols:
    """Test Protocol definitions from truth_forge.core.protocols."""

    def test_heartbeatable_protocol(self):
        """Classes implementing Heartbeatable should work."""
        from truth_forge.core.protocols import Heartbeatable
        
        class MyService:
            def handle_heartbeat(self, organism_id: str, load: float) -> dict[str, Any]:
                return {"status": "alive", "load": load}
            
            def get_state(self) -> dict[str, Any]:
                return {"status": "on"}
        
        service = MyService()
        assert isinstance(service, Heartbeatable)

    def test_validatable_protocol(self):
        """Classes implementing Validatable should work."""
        from truth_forge.core.protocols import Validatable
        
        class MyValidator:
            def validate(self) -> bool:
                return True
            
            def get_validation_errors(self) -> list[str]:
                return []
        
        validator = MyValidator()
        assert isinstance(validator, Validatable)

    def test_cost_aware_protocol(self):
        """Classes implementing CostAware should work."""
        from truth_forge.core.protocols import CostAware
        
        class MyExpensiveService:
            def estimate_cost(self, *args: Any, **kwargs: Any) -> float:
                return 0.01
            
            def get_cost_history(self) -> list[dict[str, Any]]:
                return []
        
        service = MyExpensiveService()
        assert isinstance(service, CostAware)


# =============================================================================
# Test Context Managers
# =============================================================================

class TestContextManagers:
    """Test context managers from truth_forge.core.contexts."""

    def test_locked_operation(self):
        """locked_operation should acquire and release lock."""
        from truth_forge.core.contexts import locked_operation
        
        lock = threading.Lock()
        
        with locked_operation(lock, timeout=1.0):
            # Lock should be held
            assert lock.locked()
        
        # Lock should be released
        assert not lock.locked()

    def test_timed_lock_timeout(self):
        """timed_lock should raise on timeout."""
        from truth_forge.core.contexts import timed_lock
        
        lock = threading.Lock()
        lock.acquire()  # Hold the lock
        
        try:
            with pytest.raises(TimeoutError):
                with timed_lock(lock, timeout=0.1):
                    pass
        finally:
            lock.release()

    def test_cleanup_on_error(self):
        """cleanup_on_error should call cleanup on exception."""
        from truth_forge.core.contexts import cleanup_on_error
        
        cleanup_called = False
        
        def my_cleanup():
            nonlocal cleanup_called
            cleanup_called = True
        
        with pytest.raises(ValueError):
            with cleanup_on_error(my_cleanup):
                raise ValueError("Test error")
        
        assert cleanup_called


# =============================================================================
# Test Callable Classes
# =============================================================================

class TestCallables:
    """Test callable classes from truth_forge.core.callables."""

    def test_retryable_operation_success(self):
        """RetryableOperation should succeed on first try."""
        from truth_forge.core.callables import RetryableOperation
        
        call_count = 0
        
        def my_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        retry = RetryableOperation(max_retries=3, delay=0.01)
        result = retry(my_func)
        
        assert result == "success"
        assert call_count == 1

    def test_retryable_operation_retry(self):
        """RetryableOperation should retry on failure."""
        from truth_forge.core.callables import RetryableOperation, RetryExhausted
        
        call_count = 0
        
        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Not yet")
            return "success"
        
        retry = RetryableOperation(max_retries=3, delay=0.01)
        result = retry(failing_func)
        
        assert result == "success"
        assert call_count == 3

    def test_cost_bounded_operation(self):
        """CostBoundedOperation should block expensive operations."""
        from truth_forge.core.callables import CostBoundedOperation, CostLimitExceeded
        
        def estimate_cost(data: str) -> float:
            return len(data) * 0.01
        
        bounded = CostBoundedOperation(
            max_cost_usd=0.05,
            cost_estimator=estimate_cost,
        )
        
        # Should succeed for small data
        result = bounded(lambda x: x.upper(), "hi")
        assert result == "HI"
        
        # Should fail for large data
        with pytest.raises(CostLimitExceeded):
            bounded(lambda x: x.upper(), "this is a much longer string")

    def test_operation_chain(self):
        """OperationChain should execute operations in sequence."""
        from truth_forge.core.callables import OperationChain
        
        chain = OperationChain([
            lambda x: x + 1,
            lambda x: x * 2,
            lambda x: x - 3,
        ])
        
        result = chain(5)
        assert result == 9  # (5 + 1) * 2 - 3 = 9


# =============================================================================
# Test Result Type with Pattern Matching
# =============================================================================

class TestResultPatternMatching:
    """Test Result type with structural pattern matching."""

    def test_ok_pattern_match(self):
        """Ok should match in pattern matching."""
        from truth_forge.core.result import Ok, Err, handle_result
        
        result = Ok(42)
        
        value = handle_result(
            result,
            on_ok=lambda v: v * 2,
            on_err=lambda e: 0,
        )
        
        assert value == 84

    def test_err_pattern_match(self):
        """Err should match in pattern matching."""
        from truth_forge.core.result import Ok, Err, handle_result
        
        result = Err("something went wrong")
        
        value = handle_result(
            result,
            on_ok=lambda v: v * 2,
            on_err=lambda e: -1,
        )
        
        assert value == -1

    def test_result_to_optional(self):
        """result_to_optional should convert Result to Optional."""
        from truth_forge.core.result import Ok, Err, result_to_optional
        
        assert result_to_optional(Ok(42)) == 42
        assert result_to_optional(Err("error")) is None


# =============================================================================
# Test Dataclass Slots
# =============================================================================

class TestDataclassSlots:
    """Test that dataclasses use slots=True."""

    def test_service_endpoint_has_slots(self):
        """ServiceEndpoint should use slots."""
        from truth_forge.governance.service_api.base import ServiceEndpoint
        
        # Classes with slots don't have __dict__
        endpoint = ServiceEndpoint(
            name="test",
            description="Test endpoint",
            endpoint_type=None,  # Will use default
        )
        
        # Slots classes have __slots__ attribute
        assert hasattr(ServiceEndpoint, "__slots__")

    def test_anomaly_has_slots(self):
        """Anomaly should use slots."""
        from truth_forge.vitals.pulse import Anomaly
        
        assert hasattr(Anomaly, "__slots__")

    def test_pulse_result_has_slots(self):
        """PulseResult should use slots."""
        from truth_forge.vitals.pulse import PulseResult
        
        assert hasattr(PulseResult, "__slots__")


# =============================================================================
# Test __all__ Exports
# =============================================================================

class TestAllExports:
    """Test that modules have __all__ exports."""

    def test_core_has_all(self):
        """Primitive.core should have __all__."""
        import truth_forge.core as core
        
        assert hasattr(core, "__all__")
        assert len(core.__all__) > 0

    def test_typed_dicts_has_all(self):
        """typed_dicts should have __all__."""
        import truth_forge.core.typed_dicts as typed_dicts
        
        assert hasattr(typed_dicts, "__all__")
        assert "SparkResult" in typed_dicts.__all__

    def test_protocols_has_all(self):
        """protocols should have __all__."""
        import truth_forge.core.protocols as protocols
        
        assert hasattr(protocols, "__all__")
        assert "Heartbeatable" in protocols.__all__

    def test_contexts_has_all(self):
        """contexts should have __all__."""
        import truth_forge.core.contexts as contexts
        
        assert hasattr(contexts, "__all__")
        assert "locked_operation" in contexts.__all__

    def test_callables_has_all(self):
        """callables should have __all__."""
        import truth_forge.core.callables as callables
        
        assert hasattr(callables, "__all__")
        assert "RetryableOperation" in callables.__all__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
