# ADR-0004: Loop-Pyramid Architecture

**Status**: Accepted
**Date**: 2026-02-17
**Context**: Formalizing the 4-sovereign-layer architecture and SENSE-DECIDE-ACT-VERIFY loop

---

## Context

The system needed a formal architectural model that specifies:
1. How many sovereign layers exist and what each layer governs
2. How information flows between layers
3. How memory is partitioned (reserved vs available)
4. How the verification loop closes

Previous framework documents (00-06) established principles but did not specify the architectural topology. The Loop-Pyramid theory emerged from synthesis of the framework principles with empirical findings from seven agent architecture codebases (e908-e914).

## Decision

### 1. Four Sovereign Layers (Not Five, Not Three)

| Layer | Name | Governs | Memory |
|-------|------|---------|--------|
| L1 | GENESIS | Framework itself | Reserved (immutable) |
| L2 | IDENTITY | Who we are, standards | Reserved (protected) |
| L3 | STRATEGY | Planning, adaptation | Available (curated) |
| L4 | EXECUTION | Tool use, API calls, builds | Available (working) |

**Rationale**: Cloud is NOT a layer — cloud is an advisor. The cloud provides capability but does not make decisions. Sovereignty requires that all four layers operate locally.

### 2. Reserved vs Available Memory

Memory splits into two classes:

- **Reserved** (L1 + L2): Cannot be compressed, evicted, or modified by working-level agents. This is identity.
- **Available** (L3 + L4): Actively managed, compressed under pressure, used for working operations.

**Rationale**: No existing system (Soar, Letta, Strix, ACE, AIlice, AIOS) has structural protection for identity memory. Letta's `read_only` flag is enforcement by convention, not architecture. This is an open gap in the field.

### 3. SENSE-DECIDE-ACT-VERIFY Loop

Every processing cycle follows:

```
SENSE → DECIDE → ACT → VERIFY → (loop)
```

VERIFY is the survival filter. Systems that close the loop survive. Systems with open loops die. Empirical evidence:

| System | Loop | Status |
|--------|------|--------|
| ACE Framework | Open (northbound execute commented out) | Archived |
| AIOS | Open (scheduler blind to outcomes) | Stagnating |
| Soar | Closed (GDS consistency checking) | 40 years active |
| Letta | Closed (memory edits visible next turn) | 21K stars, active |
| Strix | Closed (journal records user_wanted/agent_did) | Active |

### 4. Layer 4 Is a Spectrum

L4 (Execution) is not monolithic. It is a spectrum from careful to autonomous:

```
L4 = [Manual ←──────────────────→ Fully Autonomous]
         Human confirms each step    Agent runs independently
```

The position on this spectrum is governed by trust, which is earned through successful VERIFY cycles.

## Consequences

- Framework document `12_LOOPS_AND_PYRAMIDS.md` formalizes this theory
- All pipeline stages must implement VERIFY (not just SENSE-DECIDE-ACT)
- Memory architecture must structurally protect L1+L2 (reserved pocket)
- Cloud services are advisors, never sovereign layers

## References

- `framework/12_LOOPS_AND_PYRAMIDS.md` — Full theory document
- `credential_atlas/registry/seeing_reports/CROSS_DOMAIN_SYNTHESIS.md` — Empirical basis
- Seeing reports for Pairs A, B, C — Individual codebase analyses
