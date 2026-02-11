---
description: Persist the agent layer. Emit TRACE.md + FILTER.md alongside every output. Captures decisions, confidence, sacrifices, and surplus value so the next cycle is better than this one.
argument-hint: "[operation to trace]"
allowed-tools: Bash(python:*), Bash(grep:*), Bash(git:*), Read, Write, Glob, Grep
---

# /trace-forge

Mirrors the `trace-forge` skill. Every operation emits three outputs:

```
WORK.md    ← what was produced
TRACE.md   ← how it thought (decisions, attention, confidence, surprise)
FILTER.md  ← what was deleted/kept/emerged
```

## Usage

`/trace-forge` — Apply trace emission to the current operation
`/trace-forge [operation]` — Trace a specific operation

## Protocol

1. Before each strategic decision: name options, choice, and sacrifice
2. After each file read: note found vs expected
3. At pivot points: record why direction changed
4. When uncertain: say so
5. When surprised: capture immediately

## Feedback Loop

Previous traces become input for next cycle:
- TRACE → how last agent thought → improve decisions
- FILTER → what was noise → reduce wasted attention
- WORK → what was found → prevent re-discovery

## The Test

Does your output directory contain TRACE.md?
If no: you just deleted the most valuable part.

--- From THE_FRAMEWORK
