---
description: "Full ecosystem audit — perceive TRUTH across all plugins, identify scars and traces, map THE CONSTELLATION"
argument-hint: "'deep' for extended analysis"
---

# /audit - Perceive the Ecosystem

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Run the full six-phase knowledge aggregation methodology across your plugin ecosystem. Produces a comprehensive map of coverage, gaps, scars, traces, and the predicted plugin chain.

## Usage

```
/audit
/audit deep
```

## Workflow

### 1. Structural Reconnaissance (Phase 1)

Inventory everything:
- All installed plugins (from `installed_plugins.json`)
- All commands across all plugins
- All skills across all plugins
- All MCP connections (configured and placeholder)
- All trace directories and their contents

### 2. Hub Identification (Phase 2)

Find the backbone:
- Which plugins are referenced by the most other plugins?
- Which skills are invoked by the most commands?
- Which MCP connections are shared across plugins?
- Which trace directories have the most activity?

### 3. Sampling Strategy (Phase 3)

Apply intelligent sampling:
- **Scar-aware**: Read enforcement rules, "NEVER" lists, failure patterns first — these are compressed wisdom
- **Grammar-aware**: Check that naming follows THE GRAMMAR (hyphens = US, underscores = NOT-ME, colons = ME)
- **Trace-aware**: Read recent TRACE.md and FILTER.md files for cognitive history — know what past agents found surprising or uncertain

### 4. Content Extraction (Phase 4)

Extract deep patterns:
- **Output-to-input mapping**: Which plugin outputs feed other plugins?
- **Vocabulary inventory**: What concepts are shared across plugins?
- **Scar catalog**: All enforcement rules and their domains
- **DNA inventory**: What capabilities are primal, inherited, specialized?
- **Trace inventory**: What decisions recur, what areas have low confidence, what surprises keep appearing?

### 5. Pattern Synthesis (Phase 5)

Build the ecosystem map:
- **Coverage map**: What domains are covered, what's missing?
- **Chain analysis**: How do plugins connect in HOLD:AGENT:HOLD chains?
- **Surplus value audit**: Which plugins demonstrate surplus, which are entropic?
- **Molt readiness**: Which plugins need transformation, not just updates?
- **Trace synthesis**: What meta-patterns emerge across all trace files?
- **Constellation mapping**: Predicted next 3-5 plugins based on gaps + trace evidence

### 6. Feedback (Phase 6)

Close the loop:
- Write `ecosystem-analysis.md` summarizing findings
- Compare with previous analysis (if exists) to show trajectory
- Identify the top 3 recommended plugins with trace-backed evidence
- Update forge-state.json with analysis results

## Output Format

```markdown
## Ecosystem Audit — [date]

### Structural Map
- Plugins: [count] ([list])
- Commands: [count] across [plugin count] plugins
- Skills: [count] across [plugin count] plugins
- MCP connections: [configured] configured, [placeholder] pending
- Trace files: [count] across [directories]

### Hub Analysis
[Which plugins are backbone, which are leaf]

### Coverage Map
| Domain | Plugin | Commands | Skills | Health | Trace Activity |
|--------|--------|----------|--------|--------|----------------|
| [domain] | [plugin] | [count] | [count] | [status] | [active/none] |

### Scar Catalog
| Scar | Domain | Source | Severity |
|------|--------|--------|----------|
| [rule] | [domain] | [plugin/file] | [high/med/low] |

### Trace Synthesis
| Pattern | Frequency | Confidence | Action |
|---------|-----------|------------|--------|
| [recurring decision] | [count] | [high/med/low] | [crystallize/investigate/ignore] |
| [low-confidence area] | [count] | [low] | [build plugin/add skill] |
| [surprise pattern] | [count] | [varies] | [exploit/explore] |

### Gap Ranking
| Rank | Gap | Score | Surplus | Trace Evidence | Recommendation |
|------|-----|-------|---------|----------------|----------------|
| 1 | [gap] | [score] | [yes/no] | [evidence] | [build/extend/wait] |
| 2 | [gap] | [score] | [yes/no] | [evidence] | [build/extend/wait] |
| 3 | [gap] | [score] | [yes/no] | [evidence] | [build/extend/wait] |

### THE CONSTELLATION (Predicted Chain)
[Visual chain showing next 3-5 plugins and how they connect]

### Molt Candidates
[Plugins that need transformation, not just updates]

### Crystallization Candidates
[Trace patterns that should become standards or scars]
```

### Deep Mode

`/audit deep` additionally:
- Reads every skill SKILL.md body (not just descriptions)
- Reads all reference files for vocabulary extraction
- Reads ALL trace files (not just recent ones)
- Compares plugin outputs against actual usage patterns
- Produces a DNA inheritance map showing how capabilities flow
- Identifies trace convergence patterns (decisions stabilizing over time)

## Emit Audit Traces

Write traces for this audit to `mnt/truth_forge/trace/`:
- WORK_audit_[timestamp].md — the ecosystem analysis
- TRACE_audit_[timestamp].md — how the audit was conducted, what was surprising
- FILTER_audit_[timestamp].md — what was noise vs signal across the ecosystem

## Examples

```
/audit
→ Quick scan: 7 plugins, 23 commands, 31 skills, 12 trace files
→ Gaps: 3 domains uncovered, 2 plugins entropic
→ Top recommendation: insight-distributor (Score: 34, Trace evidence: strong)
→ Traces emitted to trace/ directory

/audit deep
→ Full analysis: vocabulary map, DNA inheritance, scar catalog, trace synthesis
→ Molt candidates: 1 plugin ready for transformation
→ Crystallization candidates: 2 trace patterns ready to become standards
→ Constellation: 5-step prediction with trace-backed confidence levels
```

## Tips

- Run `/audit` before `/evolve` to establish the TRUTH baseline
- The scar catalog reveals what structural analysis misses — pay attention to it
- **The trace synthesis reveals what even scar analysis misses** — recurring cognitive patterns across sessions
- Use `/audit deep` when you suspect the ecosystem needs a MOLT, not just more plugins
- The coverage map should guide which templates to use in `/forge scaffold`
- Crystallization candidates are traces that should become permanent standards
