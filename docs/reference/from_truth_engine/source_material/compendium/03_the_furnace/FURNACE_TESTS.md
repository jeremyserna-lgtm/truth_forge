---
document_id: doc:2b0b9f131c39
---
# Furnace — Stress Tests For Integrity And Resilience

Purpose
- Apply “heat and pressure” to validate the system’s integrity (truth, privacy, cost, reliability) under realistic stress.

Philosophy
- “I take truth, forge it into meaning, and deliver it with care.” The Furnace is both a mindset and a method: we turn raw evidence into tempered insight without warping it. Heat comes from contradiction, cost, drift, and load. Tempering comes from governance, redaction, and reproducibility.

Furnace Suite (Run monthly or before major releases)
- Truth Furnace: contradiction candidates, triangulation across sources, provenance gaps.
- Privacy Furnace: red‑team PII/consent across Tier‑3/4 pipelines; verify redaction defaults.
- Cost Furnace: preflight estimates vs actuals; circuit breakers; off‑peak scheduling efficacy.
- Drift Furnace: weekly eval deltas; model pinning checks; rollback to fallback companion.
- Resilience Furnace: kill‑switch drill; rollback SOP dry‑run; unattended mode limits verification.
- Load Furnace: batch volume tests (e.g., +2× recent week) for ingest/enrich, observe SLOs.

Outputs
- Short memo with findings, pass/fail per furnace, deltas applied (APP/ADR), fragments with policy tags.

Care Delivery Checklist (before sharing any insight)
- Truth fidelity verified (triangulation + reproducible query/figure)
- Privacy posture checked (no Tier‑3/4 raw content; redaction defaults on)
- Cost posture acceptable (preflight estimates within bounds)
- Audience fit and tone (professional, respectful, purpose‑aligned)
- Evidence/Inference separation clear in artifact

Runbook (per furnace run)
- Inputs: scope, sources, time window, budgets, companions/models
- Heat: which stressors to apply (truth/privacy/cost/drift/resilience/load)
- Methods: queries, scripts, configs; links to policies and contracts
- Findings: pass/fail, figures, fragments (C/L/T) with policy tags
- Actions: APP/ADR updates, backlog items, next review date

Links
- Truth: docs/coordination/TRUTH_FIDELITY_PROTOCOL.md
- Rollback: docs/ops/ROLLBACK_PROCEDURES.md
- SLOs: docs/coordination/policies/SLO_POLICY.md
- Cost: tools/shared/cost_estimator.py
 - Conversation mining (Furnace themes): docs/bq/queries/ai/furnace_mentions.sql, docs/bq/queries/ai/truth_meaning_pairs.sql
