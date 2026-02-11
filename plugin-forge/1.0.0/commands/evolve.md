---
description: "Run THE LOOP (ALPHA:OMEGA) — analyze, metabolize, forge, observe, repeat — with traces"
argument-hint: "<number of cycles or 'auto'>"
---

# /evolve - Run THE LOOP

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

The full recursive loop. Metabolize your ecosystem through TRUTH:MEANING:CARE, forge the next plugin, observe the surplus value, emit traces, and let this cycle's OMEGA become the next ALPHA.

## Usage

```
/evolve
/evolve 3
/evolve auto
```

## Workflow

### 1. Initialize

- Read `mnt/truth_forge/forge-state.json` (create if missing — this is the organism's genetic memory)
- **Read previous traces** from `mnt/truth_forge/trace/` — know how past cycles thought
- Determine cycle count:
  - `/evolve` — Single ALPHA:OMEGA cycle
  - `/evolve 3` — Three cycles, each OMEGA + traces becoming the next ALPHA
  - `/evolve auto` — Keep looping until saturation or user stop

### 2. For Each Cycle: THE FURNACE Protocol

Invoke the `recursive-engine` skill which runs:

#### TRUTH — Perceive What IS
- Run the `ecosystem-analyzer` on current state (six-phase methodology)
- Read outputs from plugins forged in previous cycles
- **Read traces from previous cycles** — TRACE.md tells you how last agent thought, FILTER.md tells you what was noise
- Check forge-state.json for prediction accuracy (calibrate genetic memory)
- **Read the scars** — enforcement rules and failure patterns contain compressed wisdom

#### MEANING — Metabolize Through THE FURNACE
- Score all gaps: Feed (TRUTH) + Produce (MEANING) + Chain (CARE) + Effort + **Trace bonus**
- **Surplus Value check**: Produce must exceed Feed, or the cycle is entropic
- Select the highest-scoring gap
- Generate chain prediction (THE CONSTELLATION — next 3-5 steps)

#### CARE — Present the Recommendation
```markdown
## Cycle [N]: Recommended Plugin

**[Plugin Name]**: [Description]
**TRUTH**: [The gap — what IS missing]
**MEANING**: [Why it matters — what the gap MEANS]
**CARE**: [What it BECOMES — how it serves]
**Trace evidence**: [What previous traces revealed about this gap]
**Score**: Feed [X] + Produce [X] + Chain [X] + Effort [X] + Trace [X] = [Total]
**Surplus Value**: Produce [X] > Feed [X] = [yes/no]
**Chain position**: [Where this sits in THE CONSTELLATION]

Forge this plugin? (yes / skip / modify / stop)
```

#### FORGE — THE MOLT (if approved)
- Invoke `plugin-architect` following THE FORGE PROCESS
- Build the complete plugin with HOLD:AGENT:HOLD architecture + trace protocol
- Every command emits WORK + TRACE + FILTER
- Every skill reads previous traces
- Package as .plugin file
- Record DNA inherited and specialized

#### OBSERVE — Validate Surplus Value and Emit Traces
- Record what was built in forge-state.json (genetic memory)
- Measure: Did Output exceed Input? Was there Revelation?
- Score prediction accuracy against previous cycle
- Update meta_learnings if patterns emerge
- **Emit cycle traces** to `mnt/truth_forge/trace/`:
  - WORK_cycle-[N]_[timestamp].md — what was forged
  - TRACE_cycle-[N]_[timestamp].md — how decisions were made
  - FILTER_cycle-[N]_[timestamp].md — signal vs noise vs emerged
- **This OMEGA + traces become next cycle's ALPHA**

### 3. Between Cycles

After each MOLT:
- Show the chain so far (ALPHA → OMEGA → new ALPHA → ...)
- Show surplus value trend (is the loop negentropic?)
- Show prediction accuracy (is genetic memory improving?)
- Show meta-learnings accumulated
- **Show trace compression trend** (if traces are getting shorter, the system is converging)
- Ask: "Continue to next ALPHA?"

### 4. Loop Summary

After all cycles complete:

```markdown
## Evolution Summary

### THE LOOP Trajectory
| Cycle | ALPHA | MOLT (Plugin) | OMEGA | Surplus | Traces |
|-------|-------|---------------|-------|---------|--------|
| 1 | [initial state] | [plugin name] | [new state] | [yes/no] | [emitted] |
| 2 | [from cycle 1 + traces] | [plugin name] | [new state] | [yes/no] | [emitted] |
| 3 | [from cycle 2 + traces] | [plugin name] | [new state] | [yes/no] | [emitted] |

### THE CONSTELLATION (Chain Built)
[Visual chain showing how plugins connect as HOLD:AGENT:HOLD]

### Genetic Memory Update
- Prediction accuracy: [X/Y correct]
- New meta-learnings: [patterns discovered]
- DNA registry changes: [new inherited/specialized capabilities]
- Trace compression: [trend across cycles]

### Trace Summary
- Total traces emitted: [count]
- Recurring decisions: [patterns that appeared 3+ times]
- Low-confidence areas: [domains needing more data]
- Crystallization candidates: [decisions ready to become standards]

### Next ALPHA
[What the loop predicts comes next, even though we're stopping]
[The OMEGA + traces are always ready to become the next ALPHA]
```

## The Auto Mode

`/evolve auto` keeps THE LOOP running until:
- All gap scores fall below 15 (ecosystem approaching saturation)
- Surplus value becomes negative (the loop is becoming entropic)
- The user says "stop"
- 5 cycles complete (safety limit, overridable)
- A gap requires tools/access not currently available
- **Traces show convergence** (decreasing verbosity across cycles = system stabilizing)

In auto mode, the engine still pauses at each CARE phase for user approval. THE LOOP proposes; the human disposes.

## Examples

```
/evolve
→ Single ALPHA:OMEGA cycle with trace emission

/evolve 3
→ Three linked cycles: each OMEGA + traces become the next ALPHA

/evolve auto
→ THE LOOP runs until saturation: builds plugins until surplus value plateaus
→ Traces from each cycle feed the next, improving decisions automatically
```

## Tips

- Start with `/audit` to see the TRUTH, then `/evolve` to begin THE LOOP
- The first cycle fills the biggest gap — each subsequent cycle gets more nuanced
- **Check the traces between cycles** — they show you WHY decisions were made
- If a forged plugin isn't right, say so — your feedback is Crisis fuel for the Meta-Loop
- The meta-learnings from `/evolve auto` reveal the deep structure of your workflow
- Watch the surplus value trend — if it's declining, the ecosystem may need a MOLT rather than more plugins
- **Watch the trace compression** — if traces are getting shorter, you're approaching convergence
