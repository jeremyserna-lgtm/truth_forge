# The Three-Output Trace Protocol

Every plugin forged by Plugin Forge implements this protocol. The AGENT layer — the cognition that happens between input and output — is a first-class, persistent artifact.

## The Problem

Every LLM operation produces three things:
1. **HOLD₁** — The input (context, files, instructions)
2. **AGENT** — The cognition (decisions, attention, confidence, surprise)
3. **HOLD₂** — The output (findings, documents, code, answers)

The default: ship HOLD₂, discard AGENT. This means the most valuable part — how the system decided what to do — vanishes every session.

## The Solution: Three Files

Every significant plugin operation writes three files:

### WORK.md — What Was Produced

The primary deliverable. Whatever the command was asked to produce. This IS the normal output; the trace protocol doesn't change what gets delivered.

### TRACE.md — How It Thought

The cognitive trace, captured DURING operation (not reconstructed after). Structure:

```markdown
# Trace: [operation name]
# Session: [timestamp]
# Operator: [agent identifier]
# Status: [live/reconstructed]

---

## Decisions

### Decision 1: [what was decided]
- **Options available:** [what could have been chosen]
- **Chosen:** [what was selected]
- **Sacrificed:** [what was NOT selected and why it was not]
- **Confidence:** [high/medium/low]
- **Signal source:** [what triggered this decision — user input, data pattern, scar, etc.]

### Decision 2: ...

## Attention Log

### Read (in order):
1. [file/source actually consumed]
2. [next file consumed]

### Skipped:
- [file considered but not read, with reason]

### Surprised by:
- [things found that weren't expected — these are highest-signal]

### Missed (known):
- [things the agent knows it didn't look at]

## Confidence Map

### High confidence:
- [claims the agent is sure about]

### Medium confidence:
- [claims that seem right but could be wrong]

### Low confidence:
- [guesses, inferences, things that need verification]

## Surplus Value
[Insights that emerged from processing that weren't present in any single input. The thing the Furnace produces that neither HOLD contains alone.]
```

### FILTER.md — What Was Signal vs Noise

The compression artifact. Apply the epistemological filter to the trace itself:

```markdown
# Filter: [operation name]
# Session: [timestamp]

---

## Deleted (Drowning)
[What was noise, circular, redundant, or irrelevant. What the next cycle should skip.]

## Kept (Swimming)
[What was signal. What the next cycle should prioritize.]

## Emerged (Surplus Value)
[What appeared that wasn't in any input. The actual intelligence of the operation.]
```

## How to Emit Traces

### During Operation, Not After

The trace is emitted AS the agent works, not reconstructed afterward:

1. **Before each strategic decision:** Name the options and the choice
2. **After each file read:** Note what was found vs expected
3. **At each pivot point:** Record why direction changed
4. **When uncertain:** Say so, with what would resolve it
5. **When surprised:** Capture immediately — surprise is highest-signal

### The Compression Rule

Not every micro-decision needs recording. Apply the filter:
- **Delete** mechanical decisions (formatting, tool selection, syntax choices)
- **Keep** strategic decisions (which file to read, which pattern to weight, which interpretation to choose)
- **Flag** emergent insights (connections that appeared through processing)

### File Naming Convention

Following THE GRAMMAR:
```
trace/
├── WORK_[operation]_[YYYYMMDD].md
├── TRACE_[operation]_[YYYYMMDD].md
└── FILTER_[operation]_[YYYYMMDD].md
```

- Operation name: kebab-case (US-domain, collaborative)
- Timestamp: YYYYMMDD or full ISO if multiple per day
- Directory: `trace/` within the plugin's output location

## How to Read Previous Traces

When a previous TRACE.md exists for the same operation:

1. **Read the Attention Log** — know what was already read, skip re-reading
2. **Read the Confidence Map** — know where certainty is low, focus there
3. **Read the Surplus Value** — know what emerged last time, build on it
4. **Read the FILTER** — know what to skip (Drowning) and prioritize (Swimming)

This is THE LOOP applied to cognition: each cycle's trace output becomes the next cycle's trace input.

## The Feedback Loop as Training Loop

TRACE.md files from previous runs ARE the training examples for the next run. FILTER.md files ARE the curriculum updates. No separate training pipeline needed — just persistence of what's already generated.

```
Cycle 1: Input → Process → WORK₁ + TRACE₁ + FILTER₁
Cycle 2: Input + TRACE₁ + FILTER₁ → Better process → WORK₂ + TRACE₂ + FILTER₂
Cycle 3: Input + TRACE₂ + FILTER₂ → Even better → WORK₃ + TRACE₃ + FILTER₃
```

## Pattern Recognition

If traces show the same decision being made 3+ times:
1. Notice the repeating decision structure
2. Suggest crystallizing it into a standard or scar
3. The standard means the decision only needs to be made once

This is how the AGENT layer crystallizes into HOLD. Traces become standards. Standards become infrastructure. Infrastructure becomes invisible. That's Stage 5 operation.

## Grammar Integration

| Output | Domain | Grammar | Reason |
|--------|--------|---------|--------|
| WORK.md | NOT-ME (infrastructure output) | `_` lowercase | The deliverable is infrastructure |
| TRACE.md | US (shared cognition) | `-` Normal Caps | The trace exists between ME and NOT-ME |
| FILTER.md | ME (architect's compression) | `:` directives | Compression is an act of judgment |

## The Test

**Before shipping any plugin output:** Does the output directory contain TRACE.md?

If no: the most valuable part of this operation just got deleted.
If yes: the next cycle will be better than this one.

---
*— From THE_FRAMEWORK via trace-forge*
