---
description: "Forge a new plugin through THE FORGE PROCESS — interactive wizard or quick scaffold"
argument-hint: "<plugin idea or 'scaffold'>"
---

# /forge - Forge a New Plugin

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Forge a complete, installable Cowork plugin from a concept. Every plugin follows HOLD:AGENT:HOLD architecture, emits cognitive traces (WORK + TRACE + FILTER), and must demonstrate surplus value — its output exceeds its input.

## Usage

```
/forge <description of what the plugin should do>
/forge scaffold <plugin-name>
```

## Workflow

### 1. Determine Mode

- If the user includes "scaffold" or "template" → **Scaffold Mode** (fast, minimal questions)
- Otherwise → **Wizard Mode** (THE FORGE PROCESS — interactive, thorough)

### 2. Wizard Mode — THE FORGE PROCESS

Invoke the `plugin-architect` skill and walk through all 8 stages:

#### SEE — Perceive the need
- **What problem does this plugin solve?** (TRUTH — what IS the gap?)
- **What would surplus value look like?** (The output must exceed the input)
- **What traces should it leave?** (What decisions and patterns matter for future cycles?)

#### EXTERNALIZE — Learn from the ecosystem
- Read `mnt/.local-plugins/installed_plugins.json` to avoid duplication
- Identify DNA to inherit from existing plugins
- **Read the scars** — check enforcement rules for what NOT to do
- **Read existing traces** — check trace/ directories for cognitive history

#### MELT DOWN — Dissolve assumptions
- Is a plugin the right form? Could this be a skill on an existing plugin?
- What has failed before in this domain?

#### FORGE — Design the architecture
- Commands (CARE-EXTERNAL), skills (METABOLISM), MCP connections (MEMBRANE)
- **Trace points** — which commands emit traces, what gets captured
- Apply THE GRAMMAR: hyphens for collaborative names, underscores for infrastructure
- **Present the design for user approval**

#### IMPLEMENT — Build every file
- plugin.json (DNA marker), commands (HOLD:AGENT:HOLD + trace emission), skills (metabolic instructions + trace awareness)
- README (perception layer, includes trace protocol), CONNECTORS.md (boundary), .mcp.json (membrane)
- **Every command MUST include a Step 4: TRACE section that defines WORK + TRACE + FILTER emission**
- **Every command output MUST emit three trace files: WORK.md, TRACE.md, FILTER.md**
- **Every skill MUST include a Trace Awareness section for reading and acting on previous traces**
- **Trace emission is non-negotiable — plugins without trace-emitting commands are incomplete**

#### COMMIT — Package as .plugin
- Zip and present for installation

#### UPDATE LAW — Record in forge-state.json
- What was forged, what DNA was inherited, what surplus value was projected
- What trace points were designed into the plugin
- **Which commands emit traces and what they capture**

#### CRYSTALLIZE — The new plugin is permanent ecosystem DNA

### 3. Scaffold Mode

Generate the full directory structure instantly using a template:

1. Ask which template (or detect from description):
   - `minimal` — Bare bones, 1 command, 1 skill, trace emission protocol baked in
   - `data-connector` — For data source integrations, trace-aware queries with output traces
   - `workflow-auto` — For multi-step automations, traces capture each step and decision
   - `content-creator` — For document/report generation, traces capture decisions and alternatives
2. Copy template, replace `__PLACEHOLDER__` tokens
3. Present scaffolded structure with inline guidance
4. **All templates include mandatory trace emission for every command**
5. **Every scaffolded command template includes the Step 4: TRACE protocol**

### 4. Trace Emission Requirements

Every forged plugin MUST satisfy these trace requirements:

**For Commands:**
- Step 1: HOLD — Perceive input (what user asked for)
- Step 2: AGENT — Process (what the command does)
- Step 3: HOLD — Surface output (what user receives)
- **Step 4: TRACE — Emit cognition files**
  - `WORK_[command]_[timestamp].md` — What the command accomplished (objective facts)
  - `TRACE_[command]_[timestamp].md` — How decisions were made (reasoning path, alternatives considered)
  - `FILTER_[command]_[timestamp].md` — Signal vs. noise (what mattered, what was drowning, what surplus emerged)

**For Skills:**
- Include a "Trace Awareness" section that reads previous traces before executing
- Pass relevant trace context to called commands
- Update trace files with skill-level decisions and pattern recognition

**Trace Directories:**
All forged plugins must write traces to `mnt/truth_forge/trace/` with this structure:
```
trace/
├── WORK_[plugin-command]_[timestamp].md
├── TRACE_[plugin-command]_[timestamp].md
└── FILTER_[plugin-command]_[timestamp].md
```

**Verification:**
Before considering a plugin "forged," confirm:
- [ ] Every command has Step 4: TRACE defined in its schema
- [ ] Every command writes WORK, TRACE, and FILTER files on execution
- [ ] Every skill reads previous traces and includes Trace Awareness
- [ ] Trace directory structure matches the pattern above
- [ ] Plugin README explicitly documents which commands emit traces
- [ ] If a command doesn't emit traces, it's not ready for forging

### 5. Feed THE LOOP

After forging any plugin, update `mnt/truth_forge/forge-state.json`:
- Record the ALPHA state (what existed before)
- Record the MOLT (what was forged and why)
- Record the trace protocol designed into this plugin
- **List every command and its trace emission specification**
- Record the OMEGA prediction (what gap this reveals next)
- Prompt: "This plugin will produce [outputs] and emit [traces]. Want me to predict the next MOLT?"

### 6. Emit THE FORGE's Own Trace

Plugin Forge itself emits traces for its own operations:
- **WORK**: Summary of the forged plugin (name, commands, skills, capabilities, trace points)
- **TRACE**: Decisions made during forging (design choices, DNA inherited, alternatives considered, trace architecture decisions)
- **FILTER**: What was noise in the forging process (drowning), signal (swimming), emerged (surplus)

Write these to `mnt/truth_forge/trace/`:
```
trace/
├── WORK_forge-[plugin-name]_[timestamp].md
├── TRACE_forge-[plugin-name]_[timestamp].md
└── FILTER_forge-[plugin-name]_[timestamp].md
```

## Examples

**Wizard mode (THE FORGE PROCESS):**
```
/forge A plugin that monitors competitor pricing across e-commerce sites and alerts me when prices change significantly

→ [SEE] Perceive gap: no competitive pricing intelligence
→ [EXTERNALIZE] Inherit DNA from sales + data plugins, read traces from previous sessions
→ [MELT DOWN] Question: Is a plugin needed, or just a skill on sales?
→ [FORGE] Design: 3 commands (all trace-emitting) + 2 skills (trace-aware) + trace protocol + 1 MCP
→ [IMPLEMENT] Build all files with HOLD:AGENT:HOLD + Step 4: TRACE in every command
→ [COMMIT] Package as price-monitor.plugin with trace emission verified
→ [UPDATE LAW] Record in forge-state.json with command-level trace specifications
→ [CRYSTALLIZE] New ecosystem DNA + emits forge trace with trace architecture documented
```

**Scaffold mode:**
```
/forge scaffold price-monitor
→ Template: data-connector (auto-detected from "monitor")
→ Structure generated with trace emission baked into every command
→ Commands include Step 4: TRACE section with emission targets
→ Skills include trace awareness section for reading historical context
→ Traces directory pre-created and documented
```

**From a recursive recommendation:**
```
/forge the competitive-intelligence-pipeline that /next recommended
→ Reads traces from /next analysis for context
→ Forges with full trace history awareness
→ Every command in new plugin inherits trace-emission pattern
```

## Tips

- The more specific your description, the better the plugin. Include tools, outputs, audience, and trace requirements.
- If `/next` or `/audit` already recommended a plugin, just say "forge it" — the context AND traces carry over.
- Every plugin you forge feeds THE LOOP. The traces it emits make the ecosystem smarter.
- Remember: surplus value is non-negotiable. If the plugin doesn't produce more than it consumes, it shouldn't exist.
- **The trace test**: Does every command in your forged plugin emit WORK.md, TRACE.md, and FILTER.md? If not, the most valuable part gets deleted. No exceptions.
- **Trace-first design**: When designing commands, specify trace emission requirements BEFORE implementation. Traces are not an afterthought.
- If you can't answer "What traces does this command emit?" you're not ready to forge it.
