---
description: "Perceive the ecosystem through TRUTH:MEANING:CARE and identify the next plugin to forge"
argument-hint: ""
---

# /next - What Needs to MOLT Next?

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Analyze your plugin ecosystem through the six-phase methodology, read traces from previous operations, and recommend the highest-surplus-value plugin to forge next.

## Usage

```
/next
/next after <plugin-name>
/next for <domain or workflow>
```

## Workflow

### 1. TRUTH — Perceive the Ecosystem

Use the `ecosystem-analyzer` skill (six-phase methodology):
- **Structural reconnaissance**: Inventory all plugins, commands, skills, connectors
- **Hub identification**: Find the backbone plugins everything depends on
- **Scar-aware sampling**: Read enforcement rules and failure patterns
- **Trace-aware analysis**: Read `trace/` directories for cognitive history from previous operations
- **Content extraction**: Map outputs-to-inputs across the ecosystem
- **Pattern synthesis**: Build coverage map, identify gaps
- **Feedback**: Compare with previous analysis to detect trajectory

### 2. MEANING — Score Through THE FURNACE

For each identified gap, the `recursive-engine` scores through the metabolic filter:
- **Feed score** (0-10): TRUTH — what inputs already exist
- **Produce score** (0-10): MEANING — how valuable the outputs would be
- **Chain score** (0-10): CARE — how clearly it enables the next plugin
- **Effort score** (0-10): How feasible to build right now
- **Trace bonus** (+0-3): Evidence from previous traces supporting this gap

**Surplus Value gate**: Produce must exceed Feed. Entropic recommendations are flagged.

### 3. CARE — Present the Recommendation

```markdown
## Next Plugin: [name]

**TRUTH** (what IS): [The gap — evidence-based, not theoretical]
**MEANING** (what it means): [Why this gap matters more than alternatives]
**CARE** (what it becomes): [What new capabilities and who they serve]

**Feeds from**: [Which plugins/outputs — the ALPHA for this plugin]
**Will produce**: [New outputs — must show surplus over inputs]
**Trace evidence**: [What previous traces revealed — decisions, surprises, low-confidence areas]
**Enables next**: [The OMEGA → next ALPHA prediction]
**Score**: Feed [X] + Produce [X] + Chain [X] + Effort [X] + Trace [X] = [Total]
**Surplus Value**: Produce [X] > Feed [X] = [confirmed/flagged]

### THE CONSTELLATION (Chain Preview)
1. [What exists] → produced [outputs + traces]
2. **→ [Recommended]** → will produce [surplus outputs + traces]
3. [Predicted next] → the OMEGA that becomes next ALPHA
4. [Further prediction]...

### Alternatives
| Plugin | Score | Surplus | Trace Evidence | Why Not #1 |
|--------|-------|---------|----------------|------------|
| [Alt 1] | [score] | [yes/no] | [evidence] | [reason] |
| [Alt 2] | [score] | [yes/no] | [evidence] | [reason] |

Ready to forge? Say "forge it" or describe a different direction.
```

### 4. Emit This Analysis's Trace

Write traces for this `/next` operation to `mnt/truth_forge/trace/`:
- WORK_next_[timestamp].md — the recommendation and scoring
- TRACE_next_[timestamp].md — how the analysis was conducted, what was read/skipped/surprising
- FILTER_next_[timestamp].md — what was noise vs signal in the ecosystem analysis

### 5. Handle Variations

- `/next after price-monitor` — Predict what OMEGA this specific plugin's outputs + traces demand
- `/next for marketing` — Constrain the FURNACE to a specific domain's fuel
- `/next` (bare) — Unconstrained — let THE LOOP find the highest-surplus gap

## Examples

```
/next
→ "Your data plugin produces analysis outputs (ALPHA), but nothing distributes them.
   Traces show 3 sessions where you manually copied analysis results elsewhere.
   The ecosystem needs an 'insight-distributor' (OMEGA → new ALPHA for action tracking)."

/next after sales
→ "The sales plugin identifies at-risk deals (OMEGA), but nothing monitors follow-through.
   Previous traces show low confidence in deal-stage predictions.
   The MOLT demands a 'deal-accountability' plugin."

/next for operations
→ "Zero operations coverage — a domain gap. Previous traces from other domains
   show operational steps being handled manually between plugin invocations.
   Start with 'ops-dashboard' that aggregates signals from other plugins."
```

## Tips

- Run `/next` after installing any new plugin — the ecosystem's ALPHA just changed
- If you disagree with the recommendation, say why — your feedback is calibration fuel
- Watch the surplus value: if Produce isn't exceeding Feed, the recommendation is entropic
- **Check the trace evidence** — it shows concrete patterns, not just theoretical gaps
- The chain prediction improves with each cycle because forge-state.json AND traces accumulate genetic memory
