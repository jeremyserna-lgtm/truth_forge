"""Admin Dashboard FastAPI Application.

MOLT LINEAGE:
- Source: Truth_Engine/apps/admin/backend/main.py
- Version: 2.0.0
- Date: 2026-01-26

FastAPI backend for Admin Dashboard with monitoring endpoints.

THE PATTERN:
- HOLD1: Admin request
- AGENT: Data aggregation
- HOLD2: Dashboard response

Example:
    uvicorn apps.admin.backend.main:app --reload --port 8001
"""

from __future__ import annotations

import logging
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


# Add src to path for truth_forge imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel  # noqa: E402


logger = logging.getLogger(__name__)


class ServiceStatus(BaseModel):
    """Service status model.

    Attributes:
        name: Service name.
        healthy: Whether service is healthy.
        last_check: Last health check time.
    """

    name: str
    healthy: bool
    last_check: str


class CostSummary(BaseModel):
    """Cost summary model.

    Attributes:
        daily_total: Total cost today.
        daily_limit: Daily budget limit.
        monthly_total: Total cost this month.
        monthly_limit: Monthly budget limit.
    """

    daily_total: float
    daily_limit: float
    monthly_total: float
    monthly_limit: float


class SystemStatus(BaseModel):
    """System status model.

    Attributes:
        status: Overall status.
        services_healthy: Number of healthy services.
        services_total: Total number of services.
        uptime_seconds: System uptime.
    """

    status: str
    services_healthy: int
    services_total: int
    uptime_seconds: float


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Args:
        app: FastAPI application.

    Yields:
        None during application lifetime.
    """
    logger.info("Admin Dashboard backend starting")
    yield
    logger.info("Admin Dashboard backend shutting down")


app = FastAPI(
    title="Admin Dashboard",
    description="Administration interface for truth_forge",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Health status.
    """
    return {"status": "healthy", "service": "admin"}


@app.get("/api/status")
async def get_status() -> SystemStatus:
    """Get system status.

    Returns:
        System status summary.
    """
    # TODO: Integrate with actual service monitoring
    return SystemStatus(
        status="healthy",
        services_healthy=9,
        services_total=9,
        uptime_seconds=3600.0,
    )


@app.get("/api/costs")
async def get_costs() -> CostSummary:
    """Get cost summary.

    Returns:
        Cost summary for budgeting.
    """
    # TODO: Integrate with cost_enforcer
    return CostSummary(
        daily_total=2.50,
        daily_limit=10.00,
        monthly_total=45.00,
        monthly_limit=100.00,
    )


@app.get("/api/services")
async def get_services() -> list[ServiceStatus]:
    """Get service registry status.

    Returns:
        List of service statuses.
    """
    services = [
        "secret",
        "mediator",
        "governance",
        "knowledge",
        "cognition",
        "perception",
        "action",
        "relationship",
        "logging",
    ]

    now = datetime.now(UTC).isoformat()

    return [ServiceStatus(name=s, healthy=True, last_check=now) for s in services]


@app.get("/api/governance")
async def get_governance() -> dict[str, Any]:
    """Get governance summary.

    Returns:
        Governance metrics and recent events.
    """
    # TODO: Integrate with audit_trail
    return {
        "violations_today": 0,
        "events_today": 150,
        "hold_isolation_status": "enforced",
        "cost_enforcement_status": "active",
        "recent_events": [],
    }


@app.get("/api/pipelines")
async def get_pipelines() -> list[dict[str, Any]]:
    """Get pipeline status.

    Returns:
        List of recent pipeline runs.
    """
    # TODO: Integrate with pipeline runner
    return [
        {
            "name": "test_pipeline",
            "status": "success",
            "last_run": datetime.now(UTC).isoformat(),
            "duration_seconds": 1.5,
        }
    ]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
