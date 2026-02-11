# Admin — The Governance Dashboard

## What It Does

The Admin app is the **cockpit** for the truth_forge organism — a FastAPI backend that exposes system health, cost tracking, governance audit trails, service registry status, and pipeline monitoring through a unified REST API. It is the observation deck from which ME (Jeremy) can see the state of NOT-ME at any moment.

### Endpoints

| Route | Purpose |
|-------|---------|
| `GET /health` | Heartbeat — is the organism alive? |
| `GET /api/status` | Full system status snapshot |
| `GET /api/costs` | Session and cumulative LLM cost tracking |
| `GET /api/services` | Registry of all active services and their states |
| `GET /api/governance` | Immutable audit trail of all decisions and actions |

## Technological Basis

- **Python / FastAPI** — async-first, Pydantic-validated API framework
- **Pydantic models** — `ServiceStatus`, `CostSummary`, `SystemStatus` with strict typing
- **Lifespan context manager** — proper startup/shutdown lifecycle
- **Port 8001** — separated from the main genesis service

### Architecture Pattern

```
HOLD₁ (Live Service State) → AGENT (Admin API) → HOLD₂ (Dashboard View)
```

The Admin app is a pure **observation layer** — it reads state from other services but never mutates them. This is deliberate: the cockpit displays instruments, it does not fly the plane.

## Meta Concepts

### The Immune System's Display Panel

In the biological metaphor, Admin is not an organ — it's the **nervous system's sensory feedback** to ME. Every organism needs a way to report its own health. Without Admin, NOT-ME is a black box. With it, Jeremy can see:

- **Cost hemorrhage** before it becomes a crisis (THE FURNACE: TRUTH about resource consumption)
- **Service failures** in real time (Observability Pillar)
- **Governance violations** as they occur (06_LAW enforcement)

### Why It Exists

Jeremy pays for every API call NOT-ME makes. NOT-ME doesn't feel cost. Admin exists to make the invisible visible — to give ME the same awareness of NOT-ME's metabolism that NOT-ME has of itself. This is the **No Magic** pillar made real: every action traceable, every state observable, every dollar accounted for.

### What It Wants To Become

A real-time React/Next.js dashboard with WebSocket-driven live updates, cost forecasting, anomaly detection, and one-click governance overrides. The backend skeleton is ready. The frontend is the next molt.

## Current Maturity

**Skeleton** — Backend API structure is in place with Pydantic models and route definitions. Placeholder logic returns mock data. No frontend exists yet. No actual service integration — the endpoints know *what* to report but not yet *how* to read it from live services.

## HOLD:AGENT:HOLD Position

Admin is a **ME Service** — it exists for the human's benefit, not for the organism's autonomous operation. It is prosthetic, not autonomic. The organism can function without it; Jeremy cannot govern without it.
