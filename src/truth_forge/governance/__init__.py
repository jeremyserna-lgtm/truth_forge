"""Governance - The Membrane.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/governance/__init__.py
- Version: 2.0.0
- Date: 2026-01-26

This module enforces boundaries, records actions, and gates operations.
It is the immune system of the cell - protecting integrity while allowing
legitimate operations to proceed.

BIOLOGICAL METAPHOR:
- Governance = Cell membrane + immune system
- HoldIsolation = Selective permeability
- AuditTrail = Cellular memory (epigenetics)
- CostEnforcer = Metabolic regulation

Components:
- UnifiedGovernance: Main orchestrator
- HoldIsolation: HOLD1/HOLD2 boundary enforcement
- AuditTrail: Operation recording and compliance
- CostEnforcer: Budget gate enforcement

Example:
    from truth_forge.governance import get_governance

    gov = get_governance()
    if gov.gate_operation("write", source="agent", target="hold2"):
        # Operation allowed
        pass

    # Record costs
    if gov.check_cost("openai", "completion", estimated_cost=0.05):
        result = call_llm(...)
        gov.record_cost("openai", "completion", actual_cost=0.04)
"""

from __future__ import annotations

from truth_forge.governance.audit_trail import (
    AuditCategory,
    AuditLevel,
    AuditRecord,
    AuditTrail,
    get_current_run_id,
)
from truth_forge.governance.cost_enforcer import (
    BudgetConfig,
    CostAction,
    CostEnforcer,
    CostRecord,
)
from truth_forge.governance.hold_isolation import (
    HoldIsolation,
    HoldLayer,
    IsolationViolation,
    OperationType,
)
from truth_forge.governance.unified_governance import (
    GovernanceConfig,
    UnifiedGovernance,
    get_governance,
    governed,
    reset_governance,
)


__all__ = [
    # Unified Governance
    "UnifiedGovernance",
    "GovernanceConfig",
    "get_governance",
    "reset_governance",
    "governed",
    # Hold Isolation
    "HoldIsolation",
    "HoldLayer",
    "OperationType",
    "IsolationViolation",
    # Audit Trail
    "AuditTrail",
    "AuditRecord",
    "AuditLevel",
    "AuditCategory",
    "get_current_run_id",
    # Cost Enforcer
    "CostEnforcer",
    "CostRecord",
    "CostAction",
    "BudgetConfig",
]
