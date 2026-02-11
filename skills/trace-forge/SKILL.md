---
name: trace-forge
description: >
  Persist the agent layer. Every plugin, skill, pipeline, or knowledge operation
  MUST emit a cognitive trace alongside its output. Use when building plugins,
  creating skills, running pipelines, analyzing codebases, synthesizing knowledge,
  or any operation where the HOW matters as much as the WHAT. Triggers on:
  "make a plugin", "build a skill", "create a pipeline", "trace this",
  "capture the thinking", "persist the reasoning", "what did you decide",
  "show your work", "how did you get there". The core innovation: stop deleting
  what the system already generates. HOLD:AGENT:HOLD — this skill captures the AGENT.
---

# Trace Forge

## The Problem

Every LLM operation produces three things:
1. **HOLD₁** — The input (context, files, instructions)
2. **AGENT** — The cognition (decisions, attention, confidence, surprise)
3. **HOLD₂** — The output (findings, documents, code, answers)

The industry default: ship HOLD₂, discard AGENT. The most valuable part — how the system thought — evaporates every session.

**This skill makes the AGENT layer a first-class, persistent output.**

---

## The Three-Output Protocol

Every operation that uses this skill produces three files:

```
output/
├── WORK.md        ← what was produced (HOLD₂)
├── TRACE.md       ← how it thought (the AGENT, captured)
└── FILTER.md      ← what was deleted/kept/emerged (compression)
```

### WORK.md
The primary deliverable. Whatever the plugin/skill/pipeline was asked to produce. No change from normal operation.

### TRACE.md
The cognitive trace. Captured DURING operation, not after. Format:

```markdown
# Trace: [operation name]
# Session: [timestamp]
# Operator: [agent identifier]

## Decisions

### Decision 1: [what was decided]
- **Options available:** [what could have been chosen]
- **Chosen:** [what was selected]
- **Sacrificed:** [what was NOT selected and why]
- **Confidence:** [high/medium/low]
- **Signal source:** [what triggered this decision]

### Decision 2: ...

## Attention Log
- **Read:** [files/sources actually consumed, in order]
- **Skipped:** [files/sources considered but not read, with reason]
- **Surprised by:** [things found that weren't expected]
- **Missed (known):** [things I know I didn't look at]

## Confidence Map
- **High confidence:** [claims/patterns I'm sure about]
- **Medium confidence:** [claims that seem right but could be wrong]
- **Low confidence:** [guesses, inferences, things I'd want to verify]

## Surplus Value
[Insights that emerged from the processing that weren't present in any single input. The thing the Furnace produces that neither HOLD contains.]
```

### FILTER.md
The compression artifact. Apply the scout filter to the trace itself:

```markdown
# Filter: [operation name]

## Deleted (Drowning)
[What was noise, circular, redundant, or irrelevant. What the next cycle should skip.]

## Kept (Swimming)
[What was signal. What the next cycle should prioritize.]

## Emerged (Surplus Value)
[What appeared that wasn't in any input. The actual intelligence of the operation.]
```

---

## How to Emit a Trace

### During Operation (Not After)

The trace is emitted AS the agent works, not reconstructed afterward. This means:

1. **Before each decision:** Name the options and the choice
2. **After each file read:** Note what was found vs expected
3. **At each pivot point:** Record why direction changed
4. **When uncertain:** Say so, with what would resolve it
5. **When surprised:** Capture the surprise immediately — it's highest-signal

### The Compression Rule

Not every micro-decision needs recording. Apply the filter:
- **Delete** mechanical decisions (which tool to use, formatting choices)
- **Keep** strategic decisions (which file to read, which pattern to weight, which interpretation to choose)
- **Flag** emergent insights (connections that appeared through processing)

### Integration with Existing Operations

This skill layers ON TOP of other skills. When trace-forge is active:

1. Any skill invocation produces its normal output PLUS the three trace files
2. The trace files go in a `trace/` subdirectory alongside the output
3. Each trace is timestamped and named: `TRACE_[operation]_[timestamp].md`

---

## The Feedback Loop

The trace files from previous runs become HOLD₁ for the next run.

```
Cycle 1: Read corpus → Produce findings + TRACE₁ + FILTER₁
Cycle 2: Read corpus + TRACE₁ + FILTER₁ → Produce better findings + TRACE₂ + FILTER₂
Cycle 3: Read corpus + TRACE₂ + FILTER₂ → Produce even better findings + TRACE₃ + FILTER₃
```

Each cycle:
- TRACE tells the next agent HOW the last one thought → improves decision-making
- FILTER tells the next agent WHAT was noise → reduces wasted attention
- WORK tells the next agent WHAT was found → prevents re-discovery

### Reading Previous Traces

When a previous TRACE.md exists for the same operation:
1. Read the Attention Log — know what was already read
2. Read the Confidence Map — know where certainty is low
3. Read the Surplus Value — know what emerged last time
4. Read the FILTER — know what to skip and what to prioritize

---

## Grammar Integration

Following THE_GRAMMAR OF IDENTITY:

| Output | Domain | Grammar |
|--------|--------|---------|
| WORK.md | NOT-ME (infrastructure output) | `_` lowercase |
| TRACE.md | US (shared cognition) | `-` Normal Caps |
| FILTER.md | ME (architect's compression) | `:` directives |

The trace is US-domain because it exists at the interface between ME's intent and NOT-ME's execution. It belongs to neither alone.

---

## For the Plugin-Maker

When trace-forge is used to BUILD other plugins:

1. The plugin-maker creates a new skill/plugin
2. That skill/plugin inherits the three-output protocol
3. Every child plugin emits WORK + TRACE + FILTER
4. The plugin-maker reads child traces to improve its own generation
5. The loop compounds: better traces → better plugins → better traces

The plugin-maker's TRACE.md is the most important artifact in the system. It captures how plugin-generation decisions are made — which is the intelligence that makes each generation better than the last.

---

## Pattern Recognition

If this skill gets invoked with similar trace patterns 3+ times:
1. Notice the repeating decision structure
2. Ask: "Your traces show you keep deciding [X] the same way. Want me to crystallize that into a standard?"
3. Create the standard — a decision that only needs to be made once

This is how traces become standards. How the AGENT layer crystallizes into HOLD.

---

## The Test

**Before shipping:** Does your output directory contain TRACE.md?

If no: the most valuable part of this operation just got deleted.
If yes: the next cycle will be better than this one.

---

## Ground Truth

The agent layer already exists. Every LLM already generates reasoning. Every human already makes decisions while working. The crime is the default: delete the thinking, ship only the result.

This skill changes the default. Nothing else.

---
*— From THE_FRAMEWORK*
