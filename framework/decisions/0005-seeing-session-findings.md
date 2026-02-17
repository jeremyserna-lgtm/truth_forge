# ADR-0005: Seeing Session Findings — Agent Architecture Component Harvest

**Status**: Accepted
**Date**: 2026-02-17
**Context**: Recording the component patterns harvested from seven agent architecture codebases

---

## Context

Seven codebases were analyzed through paired seeing sessions:

| Entity | System | Builder | Age |
|--------|--------|---------|-----|
| e908 | ACE Framework | David Shapiro | 2023-2024 (archived) |
| e909 | Soar | Laird/Newell | 1983-present |
| e910 | AIlice | Steven Lu | 2023-present |
| e911 | AIOS | Rutgers team | 2024-present |
| e912 | Letta | Berkeley team | 2023-present |
| e913 | Strix | Tim Kellogg | 2025-present |
| e914 | Strix Research | Tim Kellogg | 2025-present |

The analysis identified implementable patterns, three convergences across the field, and three open gaps.

## Decision

### Tier 1: Adopt These Patterns Now

| Pattern | Source | Adoption Rationale |
|---------|--------|-------------------|
| **Journal-as-VERIFY** | Strix | `user_wanted`/`agent_did`/`predictions` triad. Cheapest verification loop. Zero infrastructure cost. Every pipeline stage should journal. |
| **Memory compile()** | Letta | Re-render entire memory state into system prompt every turn. Ensures reserved memory is always fresh and complete. |
| **Self-editing memory tools** | Letta | `core_memory_replace`, `memory_rethink`, `memory_apply_patch`. Agents must curate their own state. |

### Tier 2: Adopt These Patterns Soon

| Pattern | Source | Adoption Rationale |
|---------|--------|-------------------|
| **GDS dependency tracking** | Soar | Track which inputs a result depends on. If inputs change, invalidate the result. Prevents stale reasoning. |
| **Impasse type taxonomy** | Soar | CONSTRAINT_FAILURE, CONFLICT, TIE, NO_CHANGE. Four canonical failure modes. Named failures are diagnosable. |
| **Bidirectional variable passing** | AIlice | Parent passes named variables to child, child returns named variables. HOLD:AGENT:HOLD communication through named variables, not raw dumps. |
| **Perch time scheduling** | Strix | Scheduled autonomous processing. Agents that only respond to stimuli are not autonomous. |

### Tier 3: Study and Adapt

| Pattern | Source | Research Rationale |
|---------|--------|-------------------|
| **Anti-identity paradox** | Strix Research | Contradictory instructions + thinking mode = 0% collapse. Consistent values = 67% collapse. Challenges the assumption that identity scaffolding is always optimal. |
| **Preference semantics** | Soar | REQUIRE > ACCEPTABLE > REJECT > BETTER/WORSE > INDIFFERENT. Formal conflict resolution for multi-source reconciliation. |
| **Negentropy flux model** | Strix Research | Agent as dissipative structure. Flow maintains form. Theoretical grounding for why HOLD:AGENT:HOLD works. |

### Three Convergences (Field-Wide)

1. **State over processing.** Build for the HOLDs, not the AGENT. Every surviving system prioritizes persistent state over computation quality.
2. **Loops must close.** Open loops die. Closed loops survive. The closure mechanism varies but the requirement is universal.
3. **Nobody has the full stack.** No system has even half the required capabilities. The closest is Soar (closed loop + structural hierarchy + prevention).

### Three Open Gaps (Unsolved)

1. **Reserved memory that survives context pressure.** No system structurally guarantees identity memory persists. Letta's `read_only` flag is convention, not architecture.
2. **The ME/NOT-ME boundary.** Not one of seven systems distinguishes between self-generated state and externally-injected state.
3. **Self-restructuring (the Molt).** No system can deliberately shed an old architecture and adopt a new one while maintaining continuity.

## Consequences

- Tier 1 patterns should be implemented in the next pipeline iteration
- The anti-identity paradox (Tier 3) must be tested before committing to heavy identity scaffolding in extended agent runs
- The three open gaps validate the framework's architecture — Jeremy's design is the only one that addresses all three

## References

- `credential_atlas/registry/seeing_reports/CROSS_DOMAIN_SYNTHESIS.md`
- `credential_atlas/registry/seeing_reports/PAIR_A_ACE_STRIX.md`
- `credential_atlas/registry/seeing_reports/PAIR_B_SOAR_AILICE.md`
- `credential_atlas/registry/seeing_reports/PAIR_C_AIOS_LETTA.md`
