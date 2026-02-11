"""Explorer Service - Autonomous data exploration with cognitive architecture.

Provides autonomous exploration of the spine dataset (11.8M entities) with:
- Full cognitive architecture tagging (Stage 5 baseline)
- Total Resonance tracking for ontological alignment
- Struggle Filter (keep swimming, discard drowning)
- Integration with 36 MCP spine-analysis tools
- Service ecosystem integration (Knowledge, Relationship, Cognition)

Usage:
    from truth_forge.services.factory import get_service

    explorer = get_service("explorer")
    report = explorer.explore(ExplorationConfig(
        iterations=5,
        focus_area="Stage 5 patterns",
        depth=ExplorationDepth.MEDIUM,
    ))

    print(f"Findings: {len(report.findings)}")
    print(f"Total Resonance: {report.total_resonance_score:.2f}")

THE PATTERN:
- HOLD₁: ExplorationConfig
- AGENT: Exploration Loop (tool invocation → classification → filtering)
- HOLD₂: ExplorationReport with InsightAtoms

MOLT LINEAGE:
- Source: New creation for autonomous data exploration
- Version: 1.0.0
- Date: 2026-02-01
"""

from __future__ import annotations

# Context management
from truth_forge.services.explorer.context import (
    EXPLORER_CONTEXT_LIMIT,
    EXPLORER_FALLBACK_ORDER,
    EXPLORER_MODEL,
    EXPLORER_MODEL_TIERS,
    ContextManager,
    SessionMemory,
    apply_struggle_filter,
    classify_struggle_state,
    get_explorer_context,
)

# Models - cognitive architecture types
from truth_forge.services.explorer.models import (
    ExplorationConfig,
    ExplorationDepth,
    ExplorationReport,
    Finding,
    IterationBudget,
    Pattern,
    ResonanceMetrics,
    Significance,
    StruggleState,
    ToolResult,
)

# Main service (auto-registered via @register_service decorator)
from truth_forge.services.explorer.service import (
    MAX_CALLS_PER_SESSION,
    MAX_COST_PER_SESSION,
    ExplorerService,
)

# Session management
from truth_forge.services.explorer.session import ExplorationSession

# Tool bridge
from truth_forge.services.explorer.tool_bridge import (
    TOOL_CATEGORIES,
    ToolBridge,
)


__all__ = [
    # Service
    "ExplorerService",
    "MAX_COST_PER_SESSION",
    "MAX_CALLS_PER_SESSION",
    # Models
    "ExplorationConfig",
    "ExplorationDepth",
    "ExplorationReport",
    "Finding",
    "IterationBudget",
    "Pattern",
    "ResonanceMetrics",
    "Significance",
    "StruggleState",
    "ToolResult",
    # Context
    "ContextManager",
    "SessionMemory",
    "EXPLORER_MODEL",
    "EXPLORER_CONTEXT_LIMIT",
    "EXPLORER_MODEL_TIERS",
    "EXPLORER_FALLBACK_ORDER",
    "get_explorer_context",
    "classify_struggle_state",
    "apply_struggle_filter",
    # Tool bridge
    "ToolBridge",
    "TOOL_CATEGORIES",
    # Session
    "ExplorationSession",
]
