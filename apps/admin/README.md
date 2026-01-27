# Admin Dashboard

MOLT LINEAGE:
- Source: Truth_Engine/apps/admin/
- Version: 2.0.0
- Date: 2026-01-26

## Purpose

Administration dashboard for monitoring and managing truth_forge operations.
Provides visibility into system health, costs, and governance.

## Architecture

```
apps/admin/
├── backend/              # Python FastAPI backend
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   └── routes/          # API routes
├── frontend/            # React/Next.js frontend
│   ├── components/
│   ├── pages/
│   └── styles/
└── shared/              # Shared types
```

## Features

- **System Health**: Real-time monitoring of all services
- **Cost Dashboard**: Track API costs and budget usage
- **Governance**: View audit trails and policy violations
- **Pipeline Status**: Monitor pipeline executions
- **Service Registry**: View registered services and their health

## THE PATTERN

```
Admin Request (HOLD1) → Admin Agent (AGENT) → Dashboard Data (HOLD2)
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/status` - System status
- `GET /api/costs` - Cost summary
- `GET /api/services` - Service registry
- `GET /api/governance` - Governance summary

## Running

```bash
# Backend
cd apps/admin/backend
uvicorn main:app --reload --port 8001

# Frontend
cd apps/admin/frontend
npm run dev
```
