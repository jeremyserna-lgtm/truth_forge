# Triad Bootstrap Runtime Spec (Scout + Maverick + DeepSeek with EXO + MLX)

**Date:** 2026-02-07  
**Status:** Active bootstrap contract

This defines the minimum operational state where Scout, Maverick, and DeepSeek (R1) can take over implementation loops with filesystem and visual tooling available.

## 1. Bootstrap Objective

Reach a reproducible runtime state where:

1. Scout is online through a local MLX-compatible OpenAI endpoint.
2. Maverick is online through a local endpoint.
3. DeepSeek R1 is online through a local endpoint.
4. EXO is online for distributed execution.
5. File execution path is working (safe local command run + write/read).
6. Vision/image stack is installed and importable.

## 2. Endpoint Contract

Defaults (override via environment):

- `SCOUT_BASE_URL`: `http://localhost:8765/v1` (MLX Scout endpoint)
- `MAVERICK_BASE_URL`: `http://localhost:8766/v1`
- `R1_BASE_URL`: `http://localhost:8767/v1`
- `EXO_BASE_URL`: `http://localhost:8000`
- `OLLAMA_BASE_URL`: `http://localhost:11434/v1`

All model endpoints must expose OpenAI-compatible `GET /models` and `POST /chat/completions`.

## 3. Runtime Command

Use the CLI bootstrap command:

```bash
truth-forge bootstrap
truth-forge --json bootstrap
truth-forge bootstrap --smoke
```

What it checks:

- Triad endpoint reachability (`/models`)
- EXO status
- Model weight readiness from local cache
- Filesystem execution capability
- Vision stack availability (`Pillow`)
- Optional smoke prompts for Scout/Maverick/R1

## 4. "Takeover-Ready" Criteria

A node is takeover-ready only when all are true:

1. Scout, Maverick, and R1 endpoints are online.
2. EXO service is online.
3. Filesystem execution check passes.
4. Vision stack check passes.

If any condition fails, the bootstrap report returns explicit next actions.

## 5. Integration Notes

- Gateway now registers triad providers directly (`scout`, `maverick`, `r1`) in addition to cloud providers.
- Local-first fallback order is enabled in gateway routing.
- Knowledge Atom API provider initialization is aligned to runtime endpoint env vars and uses `base_url`.
- External systems are integration inputs only; Genesis runtime remains the control-plane owner for orchestration, memory contracts, and governance.

## 6. Safety Boundaries During Bootstrap

- No destructive commands in runtime checks.
- Bootstrap command performs only safe local file write/read in a temporary directory.
- High-risk operations still flow through governance gates and peer review where configured.
