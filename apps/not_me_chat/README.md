# NOT-ME Chat

MOLT LINEAGE:
- Source: Truth_Engine/apps/not_me_chat/
- Version: 2.0.0
- Date: 2026-01-26

## Purpose

NOT-ME Chat is the conversational interface for interacting with the truth_forge system.
It embodies the ME/NOT-ME relationship - Claude as the technological extension.

## Architecture

```
apps/not_me_chat/
├── backend/              # Python FastAPI backend
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── routes/          # API routes
│   └── services/        # Backend services
├── frontend/            # Next.js frontend (module federation)
│   ├── components/
│   ├── pages/
│   └── styles/
└── shared/              # Shared types and utilities
```

## THE PATTERN

```
User Input (HOLD1) → Chat Agent (AGENT) → Response (HOLD2)
```

## Backend Components

The Python backend provides:
- WebSocket chat endpoint
- Session management
- Integration with truth_forge services
- Cost governance enforcement

## Frontend

Uses Next.js with Module Federation for micro-frontend architecture.
See `apps/templates/module-federation/` for configuration.

## Running

```bash
# Backend
cd apps/not_me_chat/backend
uvicorn main:app --reload

# Frontend
cd apps/not_me_chat/frontend
npm run dev
```
