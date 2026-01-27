"""Cost Enforcer - Budget Gate Enforcement.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/governance/cost_enforcer.py
- Version: 2.0.0
- Date: 2026-01-26

Every operation that consumes resources must pass through the cost gate.
This protects against:
- Runaway AI costs
- Unexpected resource consumption
- Budget overruns

The cost enforcer is the metabolic regulator - it ensures the cell
doesn't consume more than it can sustain.

BIOLOGICAL METAPHOR:
- CostEnforcer = Metabolic regulation
- BudgetConfig = Energy reserves
- CostAction = Metabolic response (conserve, spend, deny)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

from truth_forge.core.paths import DATA_ROOT
from truth_forge.governance.audit_trail import get_current_run_id


logger = logging.getLogger(__name__)


class CostAction(Enum):
    """What to do when budget is exceeded."""

    ALLOW = "allow"  # Log but allow (soft limit)
    WARN = "warn"  # Warn and allow
    DENY = "deny"  # Deny the operation
    THROTTLE = "throttle"  # Slow down operations


@dataclass
class CostRecord:
    """Record of a cost event."""

    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    run_id: str = field(default_factory=get_current_run_id)
    service: str = ""
    operation: str = ""
    cost_usd: Decimal = field(default_factory=lambda: Decimal("0"))
    tokens_in: int = 0
    tokens_out: int = 0
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "run_id": self.run_id,
            "service": self.service,
            "operation": self.operation,
            "cost_usd": str(self.cost_usd),
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "context": self.context,
        }


@dataclass
class BudgetConfig:
    """Budget configuration."""

    # Global limits
    daily_budget_usd: Decimal = field(default_factory=lambda: Decimal("10.00"))
    monthly_budget_usd: Decimal = field(default_factory=lambda: Decimal("100.00"))
    per_run_budget_usd: Decimal = field(default_factory=lambda: Decimal("1.00"))

    # Per-service limits
    service_budgets: dict[str, Decimal] = field(default_factory=dict)

    # Actions
    soft_limit_action: CostAction = CostAction.WARN
    hard_limit_action: CostAction = CostAction.DENY

    # Thresholds (percentage of budget)
    soft_limit_threshold: float = 0.8  # Warn at 80%
    hard_limit_threshold: float = 1.0  # Deny at 100%


class CostEnforcer:
    """Enforces cost budgets and tracks spending.

    The cost enforcer gates operations based on budget:
    1. Check if operation would exceed budget
    2. Either allow, warn, or deny based on threshold
    3. Record the cost for tracking

    BIOLOGICAL METAPHOR:
    - CostEnforcer = Metabolic regulator
    - Budget = Energy reserves
    - Check = ATP availability check
    - Record = Energy expenditure tracking

    Example:
        enforcer = CostEnforcer()

        # Check before expensive operation
        if enforcer.check("openai", "completion", estimated_cost=0.05):
            # Proceed with operation
            result = call_llm(...)

            # Record actual cost
            enforcer.record("openai", "completion", actual_cost=0.04)
        else:
            # Handle denial
            logger.warning("Operation denied due to budget")
    """

    def __init__(
        self,
        config: BudgetConfig | None = None,
        storage_path: Path | None = None,
    ) -> None:
        """Initialize cost enforcer.

        Args:
            config: Budget configuration
            storage_path: Path to cost records file
        """
        self.config = config or BudgetConfig()

        if storage_path is None:
            storage_path = DATA_ROOT / "local" / "cost" / "cost_records.jsonl"

        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # In-memory tracking
        self._records: list[CostRecord] = []
        self._daily_total: Decimal = Decimal("0")
        self._monthly_total: Decimal = Decimal("0")
        self._run_totals: dict[str, Decimal] = {}
        self._service_totals: dict[str, Decimal] = {}

        # Load existing records for today/month
        self._load_recent_costs()

        logger.info(
            "CostEnforcer initialized",
            extra={
                "daily_budget": str(self.config.daily_budget_usd),
                "monthly_budget": str(self.config.monthly_budget_usd),
            },
        )

    def _load_recent_costs(self) -> None:
        """Load costs from current day/month."""
        if not self.storage_path.exists():
            return

        now = datetime.now(UTC)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        try:
            with open(self.storage_path, encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue

                    data = json.loads(line)
                    timestamp = datetime.fromisoformat(data["timestamp"])
                    cost = Decimal(data["cost_usd"])
                    service = data.get("service", "unknown")
                    run_id = data.get("run_id", "unknown")

                    # Add to monthly total
                    if timestamp >= start_of_month:
                        self._monthly_total += cost

                    # Add to daily total
                    if timestamp >= start_of_day:
                        self._daily_total += cost
                        self._service_totals[service] = (
                            self._service_totals.get(service, Decimal("0")) + cost
                        )
                        self._run_totals[run_id] = self._run_totals.get(run_id, Decimal("0")) + cost
        except Exception as e:
            logger.warning("Failed to load cost history", extra={"error": str(e)})

    def check(
        self,
        service: str,
        operation: str,
        estimated_cost: float | Decimal,
        run_id: str | None = None,
    ) -> bool:
        """Check if operation should be allowed based on budget.

        Args:
            service: Service making the request
            operation: Type of operation
            estimated_cost: Estimated cost in USD
            run_id: Optional run ID (uses current if not provided)

        Returns:
            True if allowed, False if denied
        """
        allowed, _action, _reason = self.check_with_details(
            service, operation, estimated_cost, run_id
        )
        return allowed

    def check_with_details(
        self,
        service: str,
        operation: str,
        estimated_cost: float | Decimal,
        run_id: str | None = None,
    ) -> tuple[bool, CostAction, str]:
        """Check operation with detailed response.

        Args:
            service: Service making the request
            operation: Type of operation
            estimated_cost: Estimated cost in USD
            run_id: Optional run ID

        Returns:
            Tuple of (allowed, action, reason)
        """
        cost = Decimal(str(estimated_cost))
        run_id = run_id or get_current_run_id()

        # Check daily budget
        daily_after = self._daily_total + cost
        daily_ratio = float(daily_after / self.config.daily_budget_usd)

        if daily_ratio >= self.config.hard_limit_threshold:
            action = self.config.hard_limit_action
            reason = f"Daily budget exceeded: ${daily_after:.2f} / ${self.config.daily_budget_usd}"
            if action == CostAction.DENY:
                logger.warning("Cost denied", extra={"reason": reason})
                return False, action, reason
        elif daily_ratio >= self.config.soft_limit_threshold:
            action = self.config.soft_limit_action
            reason = f"Daily budget warning: ${daily_after:.2f} / ${self.config.daily_budget_usd}"
            logger.warning("Cost warning", extra={"reason": reason})

        # Check monthly budget
        monthly_after = self._monthly_total + cost
        monthly_ratio = float(monthly_after / self.config.monthly_budget_usd)

        if monthly_ratio >= self.config.hard_limit_threshold:
            action = self.config.hard_limit_action
            reason = (
                f"Monthly budget exceeded: ${monthly_after:.2f} / ${self.config.monthly_budget_usd}"
            )
            if action == CostAction.DENY:
                logger.warning("Cost denied", extra={"reason": reason})
                return False, action, reason

        # Check per-run budget
        run_total = self._run_totals.get(run_id, Decimal("0"))
        run_after = run_total + cost

        if run_after > self.config.per_run_budget_usd:
            action = self.config.hard_limit_action
            reason = (
                f"Per-run budget exceeded: ${run_after:.2f} / ${self.config.per_run_budget_usd}"
            )
            if action == CostAction.DENY:
                logger.warning("Cost denied", extra={"reason": reason})
                return False, action, reason

        # Check service-specific budget
        if service in self.config.service_budgets:
            service_budget = self.config.service_budgets[service]
            service_total = self._service_totals.get(service, Decimal("0"))
            service_after = service_total + cost

            if service_after > service_budget:
                action = self.config.hard_limit_action
                reason = f"Service budget exceeded for {service}: ${service_after:.2f} / ${service_budget}"
                if action == CostAction.DENY:
                    logger.warning("Cost denied", extra={"reason": reason})
                    return False, action, reason

        return True, CostAction.ALLOW, "within_budget"

    def record(
        self,
        service: str,
        operation: str,
        cost_usd: float | Decimal,
        tokens_in: int = 0,
        tokens_out: int = 0,
        run_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> CostRecord:
        """Record an actual cost.

        Args:
            service: Service that incurred the cost
            operation: Type of operation
            cost_usd: Actual cost in USD
            tokens_in: Input tokens (for LLM calls)
            tokens_out: Output tokens (for LLM calls)
            run_id: Optional run ID
            context: Additional context

        Returns:
            The cost record
        """
        cost = Decimal(str(cost_usd))
        run_id = run_id or get_current_run_id()

        record = CostRecord(
            run_id=run_id,
            service=service,
            operation=operation,
            cost_usd=cost,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            context=context or {},
        )

        # Update totals
        self._daily_total += cost
        self._monthly_total += cost
        self._run_totals[run_id] = self._run_totals.get(run_id, Decimal("0")) + cost
        self._service_totals[service] = self._service_totals.get(service, Decimal("0")) + cost

        # Store record
        self._records.append(record)

        # Persist to disk
        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict()) + "\n")

        logger.debug(
            "Cost recorded",
            extra={
                "service": service,
                "operation": operation,
                "cost": str(cost),
                "run_id": run_id,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
            },
        )

        return record

    def get_daily_total(self) -> Decimal:
        """Get today's total spending.

        Returns:
            Today's total in USD.
        """
        return self._daily_total

    def get_monthly_total(self) -> Decimal:
        """Get this month's total spending.

        Returns:
            This month's total in USD.
        """
        return self._monthly_total

    def get_run_total(self, run_id: str | None = None) -> Decimal:
        """Get total for a specific run.

        Args:
            run_id: The run ID (uses current if not provided)

        Returns:
            Run total in USD.
        """
        run_id = run_id or get_current_run_id()
        return self._run_totals.get(run_id, Decimal("0"))

    def get_service_total(self, service: str) -> Decimal:
        """Get total for a specific service today.

        Args:
            service: The service name

        Returns:
            Service total for today in USD.
        """
        return self._service_totals.get(service, Decimal("0"))

    def get_budget_status(self) -> dict[str, Any]:
        """Get current budget status.

        Returns:
            Dictionary with budget status.
        """
        return {
            "daily": {
                "spent": str(self._daily_total),
                "budget": str(self.config.daily_budget_usd),
                "remaining": str(self.config.daily_budget_usd - self._daily_total),
                "utilization": float(self._daily_total / self.config.daily_budget_usd),
            },
            "monthly": {
                "spent": str(self._monthly_total),
                "budget": str(self.config.monthly_budget_usd),
                "remaining": str(self.config.monthly_budget_usd - self._monthly_total),
                "utilization": float(self._monthly_total / self.config.monthly_budget_usd),
            },
            "services": {service: str(total) for service, total in self._service_totals.items()},
        }

    def get_stats(self) -> dict[str, Any]:
        """Get cost statistics for vitals/pulse.

        Returns:
            Dict with total_cost_usd and total_operations
        """
        return {
            "total_cost_usd": float(self._daily_total),
            "total_operations": len(self._records),
            "daily_total": float(self._daily_total),
            "monthly_total": float(self._monthly_total),
            "daily_budget": float(self.config.daily_budget_usd),
            "monthly_budget": float(self.config.monthly_budget_usd),
        }

    def within_budget(self) -> bool:
        """Check if currently within budget.

        Returns:
            True if within all budget limits
        """
        # Check daily budget
        daily_ratio = float(self._daily_total / self.config.daily_budget_usd)
        if daily_ratio >= self.config.hard_limit_threshold:
            return False

        # Check monthly budget
        monthly_ratio = float(self._monthly_total / self.config.monthly_budget_usd)
        return monthly_ratio < self.config.hard_limit_threshold


__all__ = [
    "BudgetConfig",
    "CostAction",
    "CostEnforcer",
    "CostRecord",
]
