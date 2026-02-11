# Plugin Anatomy Reference

Complete specification for every file in a Cowork plugin, including the three-output trace protocol.

## Directory Structure

```
plugin-name/VERSION/
├── .claude-plugin/
│   └── plugin.json              # REQUIRED: Plugin metadata (DNA marker)
├── .mcp.json                    # REQUIRED: MCP server configs (MEMBRANE)
├── README.md                    # REQUIRED: Documentation (PERCEPTION)
├── CONNECTORS.md                # REQUIRED: Tool connection status (BOUNDARY)
├── LICENSE                      # Optional: License file
├── commands/                    # At least 1 command (CARE-EXTERNAL)
│   ├── command-one.md
│   ├── command-two.md
│   └── ...
├── skills/                      # At least 1 skill (METABOLISM)
│   ├── skill-one/
│   │   ├── SKILL.md             # REQUIRED per skill
│   │   └── references/          # Optional: depth content (MEMORY)
│   │       └── topic.md
│   └── skill-two/
│       └── ...
└── trace/                       # COGNITIVE TRACE — the AGENT layer persisted
    ├── WORK_[operation]_[ts].md # What was produced (HOLD₂)
    ├── TRACE_[operation]_[ts].md # How it thought (the AGENT, captured)
    └── FILTER_[operation]_[ts].md # What was noise vs signal (compression)
```

## File Specifications

### plugin.json
```json
{
  "name": "kebab-case-name",
  "version": "MAJOR.MINOR.PATCH",
  "description": "1-2 sentence description of what the plugin does",
  "author": {
    "name": "Author or Organization"
  }
}
```

Rules:
- `name` must be kebab-case, match the directory name
- `version` follows semantic versioning
- `description` should be actionable ("Write SQL queries and build dashboards" not "A data tool")

### .mcp.json
```json
{
  "mcpServers": {
    "server-name": {
      "type": "http|sse",
      "url": "https://mcp.service.com/mcp",
      "headers": {
        "Authorization": "Bearer ${ENV_VARIABLE}"
      }
    }
  }
}
```

Rules:
- Always include this file, even if `mcpServers` is empty `{}`
- Use `${VARIABLE}` syntax for secrets
- `type` is either `"http"` or `"sse"` (Server-Sent Events)
- Common MCP endpoints end in `/mcp` or `/sse`

### Command Files (commands/*.md)
```markdown
---
description: "Imperative description of what this command does"
argument-hint: "<what the user provides>"
---

# /command-name - Human-Readable Title

> If you see unfamiliar placeholders, see [CONNECTORS.md](../CONNECTORS.md).

Brief description.

## Usage
\`\`\`
/command-name <argument>
\`\`\`

## Workflow
### 1. INPUT HOLD — Receive and validate
[What enters the command]

### 2. AGENT — Transform through skill knowledge
[The processing steps — reference skills by name]

### 3. OUTPUT HOLD — Deliver surplus value
[What emerges — must exceed what entered]

### 4. TRACE — Persist the AGENT layer
Emit three files to the trace/ directory:
- WORK_[command]_[timestamp].md — summary of what was produced
- TRACE_[command]_[timestamp].md — decisions made, attention patterns, confidence levels, surprises
- FILTER_[command]_[timestamp].md — what was drowning (noise) vs swimming (signal) vs emerged (surplus)

## Examples
\`\`\`
/command-name example input
\`\`\`

## Tips
- [Helpful hints for users]
```

Rules:
- `description` in frontmatter is always shown in command lists
- `argument-hint` shows the expected input format
- Workflow should reference skills by name where appropriate
- Always include the CONNECTORS.md link at the top
- **Every command MUST include a Step 4: TRACE for emitting cognitive traces**

### SKILL.md
```markdown
---
name: skill-identifier
description: >
  ~100 words. Action verbs + file types + user phrases + scenarios.
  This is ALWAYS in context. Err on the side of being slightly pushy
  about when to trigger. Include "Use when..." phrases.
---

# Skill Title

Core instructions, under 500 lines.
Point to references/ for anything deeper.

## Trace Awareness
When previous TRACE.md or FILTER.md files exist for this operation:
1. Read the Attention Log — know what was already read
2. Read the Confidence Map — know where certainty is low
3. Read the Surplus Value — know what emerged last time
4. Read the Filter — know what to skip (Drowning) and prioritize (Swimming)

## References
- See `references/topic.md` for [specific depth content]
```

Rules:
- `name` must be kebab-case
- `description` is the single most important field — it determines triggering
- Body should be actionable instructions, not documentation
- Use references/ for anything that would push the body over 500 lines
- **Every skill MUST include a Trace Awareness section**

### README.md
```markdown
# Plugin Name

Brief description and purpose.

## Installation
\`\`\`
claude plugins add marketplace/plugin-name
\`\`\`

## What It Does
[2-3 paragraphs explaining the value]

## Commands
| Command | Description |
|---------|-------------|
| `/cmd` | What it does |

## Skills
| Skill | Description |
|-------|-------------|
| `name` | What it provides |

## Trace Protocol
This plugin emits cognitive traces alongside every operation:
- **WORK.md** — what was produced
- **TRACE.md** — decisions, attention, confidence, surprises
- **FILTER.md** — signal vs noise vs emerged insights

Previous traces feed the next cycle. Each run is better than the last.

## Example Workflows
[3-4 concrete usage examples with expected outputs]

## Connecting Your Tools
[How to configure MCP servers and customize connectors]
```

### CONNECTORS.md
```markdown
# Connectors

## How tool references work
[Brief explanation of configured vs placeholder tools]

## Connectors for this plugin
| Category | Tool | Status |
|----------|------|--------|
| Category | Tool Name | Configured |
| Category | `~~placeholder` | Not yet configured |
```

### Trace Files (emitted at runtime)

```markdown
# TRACE_[operation]_[YYYYMMDD].md

## Decisions
### Decision 1: [what was decided]
- **Options available:** [alternatives]
- **Chosen:** [selection]
- **Sacrificed:** [what wasn't picked]
- **Confidence:** [high/medium/low]
- **Signal source:** [what triggered the decision]

## Attention Log
- **Read:** [files consumed, in order]
- **Skipped:** [files skipped, with reason]
- **Surprised by:** [unexpected findings]
- **Missed (known):** [known gaps]

## Confidence Map
- **High confidence:** [sure claims]
- **Medium confidence:** [likely claims]
- **Low confidence:** [guesses]

## Surplus Value
[Emergent insights not in any single input]
```

## Naming Conventions

- Plugin names: `kebab-case` (e.g., `price-monitor`, `deal-tracker`)
- Skill names: `kebab-case` (e.g., `data-exploration`, `competitive-analysis`)
- Command files: `kebab-case.md` (e.g., `analyze.md`, `build-dashboard.md`)
- Trace files: `UPPER_kebab_timestamp.md` (e.g., `TRACE_analyze_20260207.md`)
- Versions: Semantic versioning starting at `1.0.0`

## Packaging

To package a plugin as an installable `.plugin` file:
```bash
cd /path/to/plugin-name/VERSION/
zip -r /tmp/plugin-name.plugin . -x "*.DS_Store"
cp /tmp/plugin-name.plugin /path/to/outputs/
```

The `.plugin` extension triggers rich preview in the Cowork UI.
