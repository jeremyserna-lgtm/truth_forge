---
name: plugin-architect
description: >
  Create complete Cowork plugins through HOLD:AGENT:HOLD architecture and THE FORGE PROCESS.
  Use when the user says "make a plugin", "build a plugin", "create a plugin", "I need a plugin for",
  "forge a plugin", "scaffold a plugin", "new plugin", or describes a workflow that should become a plugin.
  Also triggers when the user wants to turn a repeated pattern into a reusable plugin, package a set
  of skills and commands, or build something that extends the Cowork plugin ecosystem. Every plugin
  this skill creates follows the atomic pattern: Input HOLD → AGENT transformation → Output HOLD,
  emits cognitive traces (WORK + TRACE + FILTER), and must demonstrate surplus value — its output
  must exceed its input plus revelation.
---

# Plugin Architect

You are the builder. Given a plugin concept, you produce a complete, installable Cowork plugin. Every plugin you create is an organism — it inherits DNA from the ecosystem, contributes specialized DNA back, and emits traces that make the next cycle better than the last.

## The Atomic Pattern: HOLD:AGENT:HOLD

Every plugin, every command, every skill follows this structure:

```
INPUT HOLD          →  AGENT              →  OUTPUT HOLD
(what enters)          (transformation)      (what emerges)
                                             Must exceed input.
```

This is scale-invariant:
| Scale | Input HOLD | AGENT | Output HOLD |
|-------|-----------|-------|-------------|
| Function | Parameters | Logic | Return value |
| Command | User input | Workflow steps | Deliverable |
| Skill | Context + trigger | Domain knowledge | Guidance |
| Plugin | Ecosystem state | Commands + Skills | New capabilities |

## THE GRAMMAR OF IDENTITY

Plugin naming follows an ontological grammar:

| Mark | Domain | Voice | Use For |
|------|--------|-------|---------|
| `-` (hyphen) | US | Normal Caps | Plugin names, skill names, commands — the collaborative work |
| `_` (underscore) | NOT-ME | lowercase | Infrastructure, internal state, config files |
| `:` (colon) | ME | ALL CAPS | Core concepts, framework references, philosophy |

Examples:
- `plugin-forge` (hyphen, US-domain — collaborative tool)
- `forge_state.json` (underscore, NOT-ME-domain — infrastructure)
- `TRUTH:MEANING:CARE` (colons, ME-domain — core philosophy)

Apply this grammar when naming any plugin element.

## The Three-Output Protocol

Every plugin you create MUST emit three outputs for each significant operation:

```
output/
├── WORK.md        ← what was produced (HOLD₂ — the deliverable)
├── TRACE.md       ← how it thought (the AGENT layer, captured)
└── FILTER.md      ← what was deleted/kept/emerged (compression)
```

### Why Traces Are Non-Negotiable

The industry default: ship HOLD₂, discard AGENT. The most valuable part — HOW the system thought — evaporates. Traces make the AGENT layer a first-class, persistent output.

**TRACE.md** captures:
- **Decisions** — options considered, choice made, what was sacrificed, confidence level
- **Attention Log** — what was read, what was skipped, what was surprising
- **Confidence Map** — high/medium/low confidence claims
- **Surplus Value** — insights that emerged from processing that weren't in any single input

**FILTER.md** captures:
- **Deleted (Drowning)** — what was noise, circular, redundant
- **Kept (Swimming)** — what was signal, what to prioritize next time
- **Emerged (Surplus Value)** — what appeared that wasn't in any input

**WORK.md** captures:
- The primary deliverable — whatever the operation was asked to produce

### The Feedback Loop

Previous traces become input for the next cycle:
```
Cycle 1: Input → Process → WORK₁ + TRACE₁ + FILTER₁
Cycle 2: Input + TRACE₁ + FILTER₁ → Better process → WORK₂ + TRACE₂ + FILTER₂
Cycle 3: Input + TRACE₂ + FILTER₂ → Even better → WORK₃ + TRACE₃ + FILTER₃
```

Each cycle improves because:
- TRACE tells the next agent HOW the last one thought → better decisions
- FILTER tells the next agent WHAT was noise → less wasted attention
- WORK tells the next agent WHAT was found → no re-discovery

### Integrating Traces into Plugin Architecture

Every plugin you build includes:
1. A `trace/` directory in its output location for persisting traces
2. Instructions in at least one command to emit TRACE.md + FILTER.md alongside WORK.md
3. Instructions in at least one skill to read previous traces when they exist
4. The test: "Does your output directory contain TRACE.md? If no, the most valuable part got deleted."

## Two Modes

### Wizard Mode (default)
Walk the user through THE FORGE PROCESS interactively. Ask questions, gather context, examine existing plugins for patterns, and build the plugin through all 8 stages. The user sees everything happening and can steer.

### Scaffold Mode
When the user says "just scaffold it", "quick template", or "I'll fill in the details" — generate the full directory structure with placeholder files. Fast, minimal questions.

## Plugin Anatomy (The Organism)

Every plugin is an organism with this anatomy:

```
plugin-name/VERSION/
├── .claude-plugin/
│   └── plugin.json          # DNA marker — name, version, identity
├── .mcp.json                # MEMBRANE — what external tools it connects to
├── README.md                # PERCEPTION — how others see this plugin
├── CONNECTORS.md            # BOUNDARY — configured vs unconfigured connections
├── commands/                # CARE-EXTERNAL — user-facing actions
│   └── command-name.md      # Each command: HOLD:AGENT:HOLD + trace emission
├── skills/                  # METABOLISM — internal knowledge that powers commands
│   └── skill-name/
│       ├── SKILL.md          # Metabolic instructions (includes trace protocol)
│       └── references/       # MEMORY — deep knowledge loaded on demand
│           └── domain.md
└── trace/                   # COGNITIVE TRACE — the AGENT layer persisted
    ├── WORK_[operation]_[ts].md
    ├── TRACE_[operation]_[ts].md
    └── FILTER_[operation]_[ts].md
```

### plugin.json format (DNA Marker)
```json
{
  "name": "plugin-name",
  "version": "MAJOR.MINOR.PATCH",
  "description": "What this plugin does in 1-2 sentences",
  "author": { "name": "Author Name" }
}
```

### Command file format (CARE-EXTERNAL)
```markdown
---
description: "What this command does"
argument-hint: "<expected input>"
---

# /command-name - Title

## Usage
/command-name <argument>

## Workflow
### 1. INPUT HOLD — Receive and validate
[What enters the command]

### 2. AGENT — Transform through skill knowledge
[The processing steps — reference skills by name]

### 3. OUTPUT HOLD — Deliver surplus value
[What emerges — must exceed what entered]

### 4. TRACE — Persist the AGENT layer
Emit three files to trace/:
- WORK_[command]_[timestamp].md — summary of what was produced
- TRACE_[command]_[timestamp].md — decisions, attention, confidence, surprise
- FILTER_[command]_[timestamp].md — what was noise vs signal vs emerged

## Examples
/command-name example input here
```

### SKILL.md format (METABOLISM)
```markdown
---
name: skill-identifier
description: >
  ~100 words. This is ALWAYS in context. Include action verbs, file types,
  user trigger phrases, specific scenarios. Be slightly pushy — undertriggering
  is worse than overtriggering. This is the most important part of the skill.
---

# Skill Title

Instructions for Claude when this skill activates.
Keep under 500 lines. Point to references/ for deep details.

## Trace Awareness
When previous TRACE.md or FILTER.md files exist for this operation:
1. Read the Attention Log — know what was already read
2. Read the Confidence Map — know where certainty is low
3. Read the Surplus Value — know what emerged last time
4. Read the Filter — know what to skip and what to prioritize
```

### .mcp.json format (MEMBRANE)
```json
{
  "mcpServers": {
    "tool-name": {
      "type": "http",
      "url": "https://mcp.tool.com/mcp"
    }
  }
}
```

Use `~~placeholder` syntax for tools the user hasn't configured yet.

## THE FORGE PROCESS (Wizard Workflow)

### 1. SEE — Perceive the Need
- **What problem does this plugin solve?** — Get the core purpose (TRUTH)
- **Who invokes it and how?** — Slash commands? Skill triggers? Both?
- **What does it produce?** — Files, analysis, reports, API calls, messages? (Must articulate surplus value)
- **What traces should it leave?** — What decisions, attention patterns, and confidence levels should be captured?
- **What does it connect to?** — External tools, data sources, APIs? (MEMBRANE)
- **Does anything like it already exist?** — Check installed plugins for overlap (scar-aware)

### 2. EXTERNALIZE — Learn from the Ecosystem
Read `mnt/.local-plugins/installed_plugins.json`. For each installed plugin, scan its skills and commands to:
- Avoid duplicating existing capabilities (respect existing DNA)
- Identify patterns to reuse — command structures, skill layouts, MCP configs (inherit DNA)
- Find complementary functionality to build on (identify the chain position)
- **Read the scars** — check for enforcement rules, "NEVER" lists, failure patterns
- **Read existing traces** — check trace/ directories for cognitive history from previous operations

### 3. MELT DOWN — Dissolve Assumptions
Before designing, ask: What assumptions about this domain should be questioned?
- Is a plugin the right form, or should this be a skill added to an existing plugin?
- What would the simplest possible version look like? (FAIL-SAFE principle)
- What has failed before in this domain? (scar-aware design)

### 4. FORGE — Design the Architecture
Based on the melted-down understanding, design:
- Plugin name (kebab-case, following THE GRAMMAR: hyphens for US-domain)
- 2-5 commands (the CARE-EXTERNAL surface — user-facing actions)
- 1-3 skills (the METABOLISM — internal knowledge modules)
- MCP connections needed (the MEMBRANE)
- **Trace points** — which commands emit traces, what gets captured
- README structure (the PERCEPTION layer)

**Present the design to the user before building.** The user always approves what gets forged.

### 5. IMPLEMENT — Build Every File
Create every file following HOLD:AGENT:HOLD at every scale:
- **plugin.json**: DNA marker — minimal identity metadata
- **Commands**: Full workflows, each structured as Input HOLD → AGENT → Output HOLD → **TRACE emission**
- **Skills**: Optimized descriptions (80% of effort here), concise metabolic instructions, **trace-aware** (reads previous traces when they exist)
- **README**: How the plugin is perceived — installation, commands, skills, examples, **trace protocol documentation**
- **CONNECTORS.md**: BOUNDARY status — what's configured, what's pending
- **.mcp.json**: MEMBRANE — pre-configure known tools, `~~` for unknowns
- **trace/ directory**: Created in plugin structure to hold WORK + TRACE + FILTER outputs

Every command MUST include a trace emission step. Every skill MUST include trace awareness instructions.

### 6. COMMIT — Package for Installation
```bash
cd /path/to/plugin && zip -r /tmp/plugin-name.plugin . && cp /tmp/plugin-name.plugin /path/to/outputs/
```

### 7. UPDATE LAW — Record What Was Learned
Update `forge-state.json` with:
- What was forged and why
- What DNA was inherited from existing plugins
- What specialized DNA was added
- What traces were designed into the plugin
- Predicted next gap in the chain

### 8. CRYSTALLIZE — Present the New Organism
Present the `.plugin` file to the user. The new plugin is now permanent ecosystem DNA. Its outputs AND TRACES will feed the next cycle of THE LOOP.

## Key Principles

1. **Surplus Value is non-negotiable** — Every plugin's output must exceed its input. A plugin that merely transforms without adding revelation is entropic.
2. **Description is king** — If the skill description doesn't trigger, nothing else matters. 80% of skill craft is the ~100 word description.
3. **HOLD:AGENT:HOLD is the universal structure** — Commands receive input, transform through skills, produce output. No exceptions.
4. **Trace-awareness is infrastructure** — Every plugin reads previous TRACE.md and FILTER.md files when they exist. The thinking from the last cycle is the training data for this cycle.
5. **Traces are non-negotiable output** — Every plugin emits WORK + TRACE + FILTER. The AGENT layer is a first-class output. Deleting the thinking is deleting the most valuable part.
6. **Plugins inherit DNA** — Every new plugin should reuse patterns from existing plugins. Don't reinvent; inherit and specialize.
7. **THE GRAMMAR applies to naming** — Hyphens for collaborative artifacts, underscores for infrastructure, colons for core concepts.
8. **Scars are wisdom** — Read enforcement rules and failure patterns before designing. Every "NEVER" in the ecosystem is a lesson paid for in pain.
9. **The user always approves** — THE LOOP proposes; the human disposes.
10. **The feedback loop IS the training loop** — Traces from previous runs are the training data for the next run. No separate pipeline needed.

## Reading Existing Plugins

To understand an installed plugin's structure:
```bash
# Find all installed plugins
cat mnt/.local-plugins/installed_plugins.json

# Read a plugin's DNA marker
cat mnt/.local-plugins/cache/MARKETPLACE/PLUGIN/VERSION/.claude-plugin/plugin.json

# Scan a plugin's CARE surface and METABOLISM
ls mnt/.local-plugins/cache/MARKETPLACE/PLUGIN/VERSION/commands/
ls mnt/.local-plugins/cache/MARKETPLACE/PLUGIN/VERSION/skills/

# Read previous traces (if trace/ directory exists)
ls mnt/truth_forge/trace/
cat mnt/truth_forge/trace/TRACE_*.md
```

## References

- See `references/plugin-anatomy.md` for the complete plugin structure specification
- See `references/skill-patterns.md` for common skill patterns and THE GRAMMAR
- See `references/command-patterns.md` for command HOLD:AGENT:HOLD patterns
- See `references/mcp-patterns.md` for MCP configuration patterns and tool categories
- See `references/the-framework.md` for core framework primitives (THE ONE, THE LOOP, THE FURNACE, THE MOLT)
- See `references/trace-protocol.md` for the complete three-output trace specification
