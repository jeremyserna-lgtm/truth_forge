"""Unified Governance - The Membrane Orchestrator.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/governance/unified_governance.py
- Version: 2.0.0
- Date: 2026-01-26

This is the central governance system that coordinates:
- HoldIsolation: HOLD1/HOLD2 boundary enforcement
- AuditTrail: Operation recording
- CostEnforcer: Budget gates

Together they form the cell membrane - protecting integrity while
allowing legitimate operations to proceed.

BIOLOGICAL METAPHOR:
- UnifiedGovernance = Cell membrane (complete)
- HoldIsolation = Selective permeability
- AuditTrail = Cellular memory
- CostEnforcer = Metabolic regulation

Example:
    from truth_forge.governance import get_governance

    gov = get_governance()

    # Gate an operation
    if gov.gate_operation("write", source="agent", target="hold2"):
        # Proceed
        pass

    # Check cost before expensive operation
    if gov.check_cost("openai", "completion", estimated_cost=0.05):
        result = call_llm(...)
        gov.record_cost("openai", "completion", actual_cost=0.04)
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any, TypeVar

from truth_forge.core.paths import DATA_ROOT
from truth_forge.governance.audit_trail import (
    AuditCategory,
    AuditLevel,
    AuditTrail,
    get_current_run_id,
)
from truth_forge.governance.cost_enforcer import (
    BudgetConfig,
    CostEnforcer,
)
from truth_forge.governance.hold_isolation import HoldIsolation


logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class GovernanceConfig:
    """Configuration for unified governance."""

    # Enforcement levels
    enforce_hold_isolation: bool = True
    enforce_cost_limits: bool = True
    audit_all_operations: bool = True

    # Strictness
    strict_mode: bool = True  # Deny unknown flows

    # Budget config
    budget_config: BudgetConfig | None = None

    # Storage
    data_path: Path | None = None


class UnifiedGovernance:
    """The unified governance system - the cell membrane.

    This orchestrates all governance components:
    - HoldIsolation: Ensures data flows correctly through THE_PATTERN
    - AuditTrail: Records all operations for compliance
    - CostEnforcer: Gates operations based on budget

    The membrane protects the cell while allowing legitimate operations:
    - External sources can write to HOLD1
    - AGENT can read HOLD1 and write HOLD2
    - Consumers can read HOLD2
    - All operations are audited
    - Costs are tracked and limited

    BIOLOGICAL METAPHOR:
    - UnifiedGovernance = Complete cell membrane
    - gate_operation = Receptor-mediated transport
    - check_cost = ATP availability check
    - record_agent_action = Cellular activity logging

    Example:
        gov = get_governance()

        # Gate an operation
        if gov.gate_operation("write", source="agent", target="hold2"):
            # Proceed with operation
            pass

        # Check and record costs
        if gov.check_cost("openai", "completion", estimated_cost=0.05):
            result = call_llm(...)
            gov.record_cost("openai", "completion", actual_cost=0.04)
    """

    def __init__(self, config: GovernanceConfig | None = None) -> None:
        """Initialize unified governance.

        Args:
            config: Governance configuration
        """
        self.config = config or GovernanceConfig()

        # Initialize components
        data_path = self.config.data_path or (DATA_ROOT / "local")

        self.hold_isolation = HoldIsolation(strict_mode=self.config.strict_mode)

        self.audit_trail = AuditTrail(
            storage_path=data_path / "audit" / "audit_trail.jsonl",
            auto_flush=True,
        )

        self.cost_enforcer = CostEnforcer(
            config=self.config.budget_config,
            storage_path=data_path / "cost" / "cost_records.jsonl",
        )

        logger.info(
            "UnifiedGovernance initialized",
            extra={
                "enforce_hold_isolation": self.config.enforce_hold_isolation,
                "enforce_cost_limits": self.config.enforce_cost_limits,
                "strict_mode": self.config.strict_mode,
            },
        )

    def gate_operation(
        self,
        operation: str,
        source: str,
        target: str,
        path: Path | None = None,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """Gate an operation through governance checks.

        This is the main entry point for governance. It:
        1. Checks HOLD isolation
        2. Records the operation in audit trail
        3. Returns whether operation should proceed

        Args:
            operation: What is being done (read, write, append, etc.)
            source: Where it originates (external, agent, consumer)
            target: What it targets (hold1, hold2)
            path: Optional path for context
            context: Additional context for audit

        Returns:
            True if operation is allowed, False if denied
        """
        run_id = get_current_run_id()
        full_context = context or {}
        full_context["run_id"] = run_id
        full_context["path"] = str(path) if path else None

        # Check HOLD isolation
        if self.config.enforce_hold_isolation:
            allowed, reason = self.hold_isolation.check_with_reason(
                operation, source, target, path, full_context
            )

            if not allowed:
                # Record violation
                self.audit_trail.record_violation(
                    operation=f"{source}_{operation}_{target}",
                    reason=reason,
                    component="hold_isolation",
                    context=full_context,
                )
                return False

        # Record successful operation
        if self.config.audit_all_operations:
            self.audit_trail.record_hold_operation(
                operation=operation,
                hold_layer=target,
                component=source,
                success=True,
                context=full_context,
            )

        return True

    def check_cost(
        self,
        service: str,
        operation: str,
        estimated_cost: float | Decimal,
    ) -> bool:
        """Check if a cost-incurring operation should proceed.

        Args:
            service: Service making the request
            operation: Type of operation
            estimated_cost: Estimated cost in USD

        Returns:
            True if within budget, False if would exceed
        """
        if not self.config.enforce_cost_limits:
            return True

        allowed, action, reason = self.cost_enforcer.check_with_details(
            service, operation, estimated_cost
        )

        if not allowed:
            self.audit_trail.record(
                operation=f"{service}_{operation}",
                component="cost_enforcer",
                level=AuditLevel.WARNING,
                category=AuditCategory.COST,
                success=False,
                error_message=reason,
                context={"estimated_cost": str(estimated_cost), "action": action.value},
            )

        return allowed

    def record_cost(
        self,
        service: str,
        operation: str,
        cost_usd: float | Decimal,
        tokens_in: int = 0,
        tokens_out: int = 0,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Record an actual cost.

        Args:
            service: Service that incurred the cost
            operation: Type of operation
            cost_usd: Actual cost in USD
            tokens_in: Input tokens
            tokens_out: Output tokens
            context: Additional context
        """
        self.cost_enforcer.record(
            service=service,
            operation=operation,
            cost_usd=cost_usd,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            context=context,
        )

        self.audit_trail.record_cost(
            service=service,
            operation=operation,
            cost_usd=float(cost_usd),
            context={"tokens_in": tokens_in, "tokens_out": tokens_out},
        )

    def record_agent_action(
        self,
        action: str,
        component: str,
        input_records: int = 0,
        output_records: int = 0,
        success: bool = True,
        error_message: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Record an AGENT transformation action.

        Args:
            action: What the agent did
            component: Which agent/component
            input_records: Records read from HOLD1
            output_records: Records written to HOLD2
            success: Whether transformation succeeded
            error_message: Error if failed
            context: Additional context
        """
        ctx = context or {}
        ctx["input_records"] = input_records
        ctx["output_records"] = output_records

        self.audit_trail.record(
            operation=action,
            component=component,
            category=AuditCategory.AGENT_ACTION,
            success=success,
            error_message=error_message,
            context=ctx,
        )

    def get_status(self) -> dict[str, Any]:
        """Get governance system status.

        Returns:
            Dictionary with status information.
        """
        return {
            "config": {
                "enforce_hold_isolation": self.config.enforce_hold_isolation,
                "enforce_cost_limits": self.config.enforce_cost_limits,
                "audit_all_operations": self.config.audit_all_operations,
                "strict_mode": self.config.strict_mode,
            },
            "hold_isolation": {
                "violations_count": len(self.hold_isolation.violations),
            },
            "audit_trail": {
                "buffer_size": len(self.audit_trail._buffer),
                "violations": len(self.audit_trail.get_violations()),
            },
            "cost": self.cost_enforcer.get_budget_status(),
        }

    def flush(self) -> None:
        """Flush all buffers to disk."""
        self.audit_trail.flush()

    def __enter__(self) -> UnifiedGovernance:
        """Context manager entry.

        Returns:
            Self for context manager use.
        """
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit - flush buffers."""
        self.flush()


# Singleton instance
_governance_instance: UnifiedGovernance | None = None


@lru_cache(maxsize=1)
def get_governance(config: GovernanceConfig | None = None) -> UnifiedGovernance:
    """Get the singleton governance instance.

    This is the primary way to access governance. The instance is
    created lazily and cached.

    Args:
        config: Optional configuration (only used on first call)

    Returns:
        The unified governance instance
    """
    global _governance_instance

    if _governance_instance is None:
        _governance_instance = UnifiedGovernance(config)

    return _governance_instance


def reset_governance() -> None:
    """Reset the governance singleton (for testing)."""
    global _governance_instance
    if _governance_instance:
        _governance_instance.flush()
    _governance_instance = None
    get_governance.cache_clear()


def governed(
    operation: str = "execute",
    source: str = "agent",
    target: str = "hold2",
) -> Callable[[F], F]:
    """Decorator to add governance to a function.

    Args:
        operation: The operation type
        source: The source context
        target: The target HOLD layer

    Returns:
        Decorator function

    Example:
        @governed(operation="write", source="agent", target="hold2")
        def my_function():
            ...
    """

    def decorator(func: F) -> F:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            gov = get_governance()

            if not gov.gate_operation(operation, source, target):
                raise PermissionError(f"Governance denied: {source} cannot {operation} {target}")

            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


__all__ = [
    "GovernanceConfig",
    "UnifiedGovernance",
    "get_governance",
    "governed",
    "reset_governance",
]
