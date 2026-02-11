# Gap Analysis Framework — Six-Phase Detection with Scar-Aware and Grammar-Aware Methodology

## The Principle

Structural reconnaissance alone sees less than 20% of what matters. This framework goes deeper by incorporating:
- **Scar-aware analysis**: Reading enforcement rules, "NEVER" lists, and failure patterns as compressed operational wisdom
- **Grammar-aware sampling**: Using file naming conventions to determine ontological domain
- **Second Pass methodology**: Always asking what the first structural scan missed

## Gap Categories

### 1. Domain Gaps (Missing Organism)
Entire areas of work with zero plugin coverage.

**Detection**: List all domains the user works in (from conversation history, connected tools, file types). Compare against installed plugin domains.

**Framework signal**: If the user's workflow has a TRUTH:MEANING:CARE cycle in a domain and no plugin covers it, that's a domain gap.

**Scoring boost**: +3 to Produce score if the domain is actively used.

### 2. Depth Gaps (Underdeveloped Organ)
A plugin covers a domain but lacks critical capabilities.

**Detection**: For each installed plugin, compare its commands against the full HOLD:AGENT:HOLD lifecycle for that domain. If a plugin has "analyze" (AGENT) but not "alert" (OUTPUT HOLD → next INPUT HOLD), that's a depth gap.

**Scar-aware detection**: Check the plugin's enforcement rules. If it has "NEVER do X" rules, ask: is there a missing command that would do X safely?

**Scoring boost**: +2 to Feed score since the existing plugin already produces relevant context.

### 3. Connection Gaps (Severed Nerve)
Plugins exist but their `~~` placeholders haven't been configured.

**Detection**: `grep -rn '~~\w' /path/to/plugins --include='*.md' --include='*.json'`

**Resolution**: These don't need new plugins — they need the `cowork-plugin-customizer` skill. Flag them but don't score them as forge candidates. A severed nerve needs reconnection, not a new organ.

### 4. Integration Gaps (Missing Membrane)
The user's tools aren't represented by any MCP connection.

**Detection**: Check what tools the user mentions in conversation vs what's in `.mcp.json` files across all plugins.

**Grammar-aware detection**: If the user references tools using US-domain grammar (hyphens, collaborative language), they consider those tools part of their working identity. Missing MCP connections for those tools are higher-priority.

**Scoring boost**: +2 to Effort score if an MCP server exists for the tool (just needs connecting).

### 5. Flow Gaps (Missing Connective Tissue)
Multi-step workflows that span plugins but have no orchestration.

**Detection**: Look for patterns where the user manually copies output from one plugin command and feeds it into another. That manual step IS the gap — it's friction fuel for the next plugin.

**HOLD:AGENT:HOLD detection**: If the OUTPUT HOLD of plugin A doesn't naturally flow into the INPUT HOLD of plugin B, there's a flow gap between them.

**Scoring boost**: +3 to Chain score since flow gaps are inherently about connecting plugins.

### 6. Output Gaps / Recursive Gaps (Dead-End Capillary)
Plugins produce outputs that nothing consumes.

**Detection**: For each plugin, list its outputs. For each output, check if any other plugin or command consumes it. Unconsumed outputs are THE LOOP's most valuable fuel — they're recursive opportunities waiting to ignite.

**Surplus Value detection**: If a plugin's outputs aren't being consumed, the plugin isn't achieving surplus value in the ecosystem context (even if it's valuable to the user individually).

**Scoring boost**: +3 to Feed score (the input already exists) and +2 to Chain score (consuming it enables more).

### 7. Molt Gaps (Shell That's Been Outgrown)
Plugins that have outgrown their original design.

**Detection**: Look for these molt triggers:
- **Internal Saturation**: Skills over 400 lines, commands with branching complexity > 5 paths
- **External Calling**: Users requesting capabilities adjacent to but outside the plugin's domain
- **Purpose Shift**: The plugin's actual use has diverged from its README description
- **Scar Accumulation**: Many enforcement rules and "NEVER" lists (the organism is constraining itself rather than transforming)

**Resolution**: Recommend THE MOLT — transform the plugin, don't just extend it.

## Scoring Formula

```
Total = Feed(0-10) + Produce(0-10) + Chain(0-10) + Effort(0-10)

Max possible: 40
Threshold for recommendation: 20+
Strong recommendation: 30+
```

### Feed Score (0-10) — TRUTH: What Exists
How well can existing plugin outputs serve as inputs?
- 0: No existing plugins produce relevant data
- 5: Some plugins produce partially relevant outputs
- 10: Multiple plugins produce exactly what this needs
- **Scar bonus**: +1 if existing plugins have enforcement rules that document the exact input format

### Produce Score (0-10) — MEANING: What Matters
How valuable are the outputs this new plugin would create?
- 0: Outputs are nice-to-have but not actionable
- 5: Outputs save time on a regular task
- 10: Outputs are critical for decision-making
- **Surplus Value requirement**: Produce MUST be > Feed, or the cycle is entropic

### Chain Score (0-10) — CARE: What It Serves
How clearly does this enable the NEXT plugin?
- 0: Dead-end — outputs don't feed anything (no OMEGA → ALPHA transition)
- 5: Outputs could potentially feed something
- 10: Outputs obviously demand a consumer plugin (strong OMEGA → ALPHA)
- **Constellation bonus**: +1 if the chain prediction extends 3+ steps with confidence

### Effort Score (0-10) — Pragmatism
How feasible is it to build this right now?
- 0: Requires tools/access we don't have
- 5: Buildable but needs some new MCP connections
- 10: Everything needed already exists, just needs assembly
- **DNA bonus**: +1 if significant DNA can be inherited from existing plugins

## Priority Matrix

| Feed | Chain | Priority | Framework Reasoning |
|------|-------|----------|-------------------|
| High | High | **BUILD NOW** | Rich inputs + clear OMEGA → ALPHA = the loop is pulling this into existence |
| High | Low | Build soon | Rich inputs but terminal — CARE-EXTERNAL value without CARE-INTERNAL chain |
| Low | High | Plan ahead | Great chain position but needs prerequisites — the ALPHA isn't ready yet |
| Low | Low | Backlog | Neither urgent nor chain-enabling — not yet in THE LOOP's path |

## Second Pass Checklist

After completing the gap analysis, apply the Second Pass principle — always ask what was missed:

1. **Did I read actual content, or just structure?** (File counts are not analysis)
2. **Did I check the scars?** (Enforcement rules contain compressed wisdom)
3. **Did I follow the grammar?** (File naming reveals ontological domain)
4. **Did I find the living system, or just the shapes?** (Plugins are organisms, not folders)
5. **Did I detect predecessor projects?** (Numbered subsystems may be absorbed predecessors with their own internal logic)
6. **Am I seeing Stage 5?** (Don't find the recursion fascinating. Find it unremarkable. Then look for what's actually interesting.)
