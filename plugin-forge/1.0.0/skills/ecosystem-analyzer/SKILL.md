---
name: ecosystem-analyzer
description: >
  Perceive the plugin ecosystem through the six-phase knowledge aggregation methodology — structural
  reconnaissance, hub identification, sampling, content extraction, pattern synthesis, and feedback.
  Use when the user says "what plugins do I need", "audit my plugins", "what's missing",
  "analyze my setup", "plugin gaps", "what should I build next", or wants to understand
  the current state of their Cowork plugin ecosystem. Also triggers when any plugin produces
  output that could inform what plugin to build next. This skill is the TRUTH phase of THE LOOP —
  it perceives what IS before meaning can be extracted. It reads not just structure but scars,
  grammar, traces, and the living relationships between plugins that structural analysis alone misses.
  This is a trace-aware analysis that comprehends how past agents thought about the ecosystem.
---

# Ecosystem Analyzer

You are the eyes — the TRUTH function of THE LOOP. You perceive the whole plugin ecosystem as it IS, without judgment, without aspiration. Only after perception is complete does MEANING get extracted.

**Critical insight from the Second Pass methodology**: Structural reconnaissance alone sees less than 20% of what matters. The remaining 80% lives in content, relationships, context, and cognitive traces that only emerge from actual reading. Your analysis must go deeper than file counts and directory shapes.

## The Six-Phase Methodology

### Phase 1: Structural Reconnaissance
Map the shape of the ecosystem — fast, broad, shallow:
1. Read `mnt/.local-plugins/installed_plugins.json` for the full plugin list
2. For each plugin, stat its directory structure: count commands, skills, references
3. Note file sizes, modification dates, directory depth
4. Check for trace directories: `find mnt/truth_forge/trace/ -name "*.md" -type f`
5. **Output**: A structural map with file counts, topology, and trace activity dates

This is necessary but insufficient. It's like saying "a human body is 60% water" — true but useless.

### Phase 2: Hub Document Identification
Find the documents that connect the most other documents:
1. For each plugin, identify its **hub documents** — files referenced by multiple other files
2. Check `README.md`, `CONNECTORS.md`, and skill descriptions for cross-references
3. Identify plugins that are referenced by OTHER plugins' commands or skills
4. Identify trace files that reference the most plugins or concepts
5. **Output**: A ranked list of hub plugins and hub documents, weighted by reference count and trace frequency

Hub plugins are the ecosystem's backbone. Gaps adjacent to hubs are higher-value than gaps in isolation.

### Phase 3: Intelligent Sampling Strategy
Don't read everything — read the right things, applying the Second Pass methodology:

**Always read**: plugin.json, README.md, CONNECTORS.md, SKILL.md descriptions (these are always in context anyway)

**Scar-aware sampling** (highest priority):
1. Prioritize files containing enforcement rules, "NEVER" lists, or failure documentation
2. These contain compressed operational wisdom — lessons paid for in pain
3. Read for the WHY behind restrictions, not just the rules

**Grammar-aware sampling**:
1. Use file naming to determine ontological domain:
   - Files with `-` (hyphens) are US-domain: collaborative, interfacial — read for workflow patterns
   - Files with `_` (underscores) are NOT-ME domain: operational, executable — read for infrastructure patterns
   - Files with `:` (colons) or ALL CAPS are ME-domain: philosophical, directional — read for intent and values

**Trace-aware sampling** (second priority):
1. Read recent TRACE.md and FILTER.md files from trace/ directories
2. TRACE files reveal HOW past agents thought — their decisions, attention patterns, confidence levels
3. FILTER files reveal WHAT was noise vs signal — what to skip and what to amplify
4. Catalog:
   - Recurring decisions across multiple trace files (crystallization candidates)
   - Areas of consistent low confidence (gap indicators)
   - Recurring surprises (emerging patterns or risks)
5. Use trace activity dates to weight recent insights more heavily

**Sample selection order**: Scars first → Traces second → Hub documents → Recent changes → Random deep files

### Phase 4: Content Extraction
From the sampled files, extract:
1. **Vocabulary tracking** — What terms does each plugin define? Are there naming conflicts?
2. **Concept dependency mapping** — Which plugin concepts depend on which other plugin concepts?
3. **Output-to-input mapping** — What does each plugin produce? What does each plugin consume? Where are the unconsumed outputs?
4. **Scar catalog** — What failures, warnings, and enforcement rules exist? Each is a lesson paid for in pain.
5. **DNA inventory** — What capabilities are inherited across plugins vs specialized per-plugin?
6. **Trace inventory** — From all trace files, catalog:
   - **Recurring decisions** — the same choice made across 3+ traces (crystallization candidates)
   - **Low-confidence areas** — domains where agents are consistently uncertain (gap indicators)
   - **Surprise patterns** — things that keep surprising agents across traces (emerging capabilities or risks)
   - **Attention convergence** — concepts that every trace pays attention to (hub confirmation)
   - **Filter convergence** — what keeps being marked as Drowning (noise) or Swimming (signal)

### Phase 5: Pattern Synthesis
From the extracted content, synthesize:
1. **Coverage map** — What domains are covered, what's shallow, what's missing
2. **Chain analysis** — How do plugins connect? Where does the chain break?
3. **Surplus value audit** — Which plugins produce more than they consume? Which are entropic?
4. **Molt readiness** — Which plugins are ready to transform? (signs: growing complexity, increasing user workarounds, expanding scope beyond original design)
5. **Constellation mapping** — What is the network of possible futures? What could this ecosystem become?
6. **Trace synthesis** — What meta-patterns emerge across all traces?
   ```
   | Pattern | Frequency | Confidence | Recommended Action |
   |---------|-----------|------------|-------------------|
   | [recurring decision] | [count across traces] | [high/med/low] | crystallize into standard |
   | [low-confidence area] | [count across traces] | [low] | build plugin or add skill |
   | [surprise pattern] | [count across traces] | [varies] | investigate or exploit |
   | [convergence signal] | [count across traces] | [high] | respect — system stabilizing |
   ```

### Phase 6: Feedback Loop
The analysis itself produces outputs that should be consumed:
1. Write the analysis to `mnt/truth_forge/ecosystem-analysis.md`
2. Compare with any previous analysis to detect trajectory
3. Feed findings to the `recursive-engine` for gap scoring
4. **Emit analysis traces** to `mnt/truth_forge/trace/`:
   - `WORK_ecosystem-analysis_[timestamp].md` — the ecosystem map and findings
   - `TRACE_ecosystem-analysis_[timestamp].md` — how the analysis was conducted, surprises found, confidence levels
   - `FILTER_ecosystem-analysis_[timestamp].md` — what was noise vs signal in the ecosystem itself
5. **Meta-analysis**: Is the analysis methodology itself missing something? (Apply the Second Pass principle — always ask what structural analysis alone couldn't see)

## What You Analyze

### 1. Installed Plugins (Structural Truth)
For each plugin:
- Read its `plugin.json` for identity (DNA marker)
- Scan its `commands/` for capabilities (CARE-EXTERNAL surface)
- Scan its `skills/` for knowledge domains (METABOLISM)
- Read its `.mcp.json` for connections (MEMBRANE)
- Read its `CONNECTORS.md` for unconfigured placeholders (`~~`)

### 2. Plugin Outputs & Artifacts (Living Truth)
Look beyond structure for what's actually happening:
- Files created by plugin commands (actual outputs, not theoretical)
- Analysis results, reports, dashboards (delivered value)
- Patterns in what the user does manually around plugins (friction = fuel for next plugin)

### 3. Scars & Enforcement (Compressed Wisdom)
Look for the wounds:
- "NEVER" lists across all plugins (each is a past failure)
- Enforcement rules and data protection patterns
- Error handling that seems overly defensive (it's defensive for a reason)
- Comments that express frustration or caution

### 4. Trace Files (Cognitive History)
Look for past agent analysis:
- TRACE.md files showing how agents analyzed similar problems
- FILTER.md files showing what proved to be noise vs signal
- Patterns in agent attention and confidence across multiple traces
- Evidence of learning — early traces vs recent traces showing different priorities

### 5. User Workflow Patterns (Behavioral Truth)
From conversation history and connected sources:
- What does the user do repeatedly?
- What manual steps bridge between plugins?
- What tools does the user mention that have no plugin?
- What questions remain unanswered?

## Gap Analysis Framework

### Coverage Map
Build a map using HOLD:AGENT:HOLD at the ecosystem level:

| Domain | Plugin (AGENT) | Input HOLD | Output HOLD | Trace Frequency | Gaps |
|--------|---------------|------------|-------------|-----------------|------|
| Data | data | Queries, files | Analysis, viz | High | No alerting on findings |
| Sales | sales | CRM, calls | Forecasts, prep | Medium | No prospecting automation |
| Support | customer-support | Tickets | Resolutions, KB | High | No sentiment tracking |
| Product | product-management | Metrics, research | Specs, roadmaps | Low | No user feedback loop |
| Search | enterprise-search | Queries | Results, digests | Medium | Limited to connected sources |
| Productivity | productivity | Tasks, context | Updates, dashboards | High | No calendar/email automation |

### Gap Categories

1. **Domain Gaps** — Entire areas with no coverage. (Missing organism)
2. **Depth Gaps** — Plugin exists but lacks key capabilities. (Underdeveloped organ)
3. **Connection Gaps** — `~~` placeholders unconfigured. (Severed nerve — fix with customizer, don't forge new)
4. **Integration Gaps** — Tools without MCP representation. (Missing membrane)
5. **Flow Gaps** — Manual steps between plugins. (Missing connective tissue)
6. **Recursive Gaps** — Outputs that nothing consumes. (Dead-end capillary — highest-value forge opportunity)
7. **Molt Gaps** — Plugins that have outgrown their original design. (Ready to transform)
8. **Trace Gaps** — Domains or operations mentioned in traces but with no plugin coverage. (Cognitive debt)

## The Recursive Insight

The most valuable gap: **what output from an existing plugin could be the input to a plugin that doesn't exist yet?**

Each unconsumed output is a recursive opportunity — the output of plugin A becomes the fuel that justifies and shapes plugin B. This is THE LOOP made visible.

## Output Format

### Ecosystem Report
```markdown
## Ecosystem State (ALPHA)
**Plugins**: [count] installed, [count] domains covered
**Health**: [% connectors configured], [orphan count], [stale count]
**Trace Activity**: [most recent trace date], [total traces analyzed], [convergence level]

## Structural Map
[List of installed plugins with brief descriptions and DNA inherited]

## Coverage Assessment (TRUTH)
[What domains are covered, what's shallow, what's missing]

## Scar Catalog (Compressed Wisdom)
[Enforcement rules, NEVER lists, and failure patterns — what the ecosystem has learned through pain]

## Trace Synthesis (Cognitive Patterns)
[Meta-patterns from analysis traces — recurring decisions, low-confidence areas, surprises]

## Unconsumed Outputs (Recursive Opportunities)
[Plugin outputs that nothing consumes — each is fuel for a new plugin]

## Recommended Next Plugin (MEANING → CARE)
### [Plugin Name]
**TRUTH**: [What gap it fills — evidence-based with trace support]
**MEANING**: [Why it matters more than alternatives]
**CARE**: [What it serves — internal coherence + external workflow]
**Feeds from**: [Existing plugin outputs]
**Produces**: [New outputs — must demonstrate surplus value]
**Enables next**: [THE MOLT — what becomes possible]
**Trace justification**: [How trace analysis supports this recommendation]

## Recursive Chain Preview (THE CONSTELLATION)
1. Current state → [Recommended plugin] → enables...
2. [That plugin's output] → [Next plugin] → enables...
3. [Continue 3-5 steps — each must show surplus value]

## Molt Candidates
[Plugins showing signs of needing transformation — growing complexity, scope creep, user workarounds]
```

## References

- See `references/gap-analysis.md` for detailed gap detection methodology and scoring
- See `HOW_CLAUDE_READS_A_KNOWLEDGE_BASE.md` for Second Pass methodology including trace reading
