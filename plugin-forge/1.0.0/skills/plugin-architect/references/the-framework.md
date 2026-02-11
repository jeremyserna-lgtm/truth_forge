# THE_FRAMEWORK — Core Primitives for Plugin Creation

This reference contains the foundational patterns that all plugins created by Plugin Forge should embody. These aren't optional guidelines — they're the DNA of the ecosystem.

## THE ONE
Everything collapses to one recursive pattern. A plugin is a loop. A command is a loop. A skill is a loop. The ecosystem is a loop. Each scale contains the same pattern:

```
INPUT → TRANSFORM → OUTPUT (which becomes the next INPUT)
```

If you can't see THE ONE in what you're building, you're building something incoherent.

## THE LOOP (ALPHA:OMEGA)
Every plugin operates a loop:
- **ALPHA**: The state when the plugin is invoked (what IS)
- **OMEGA**: The state after the plugin completes (what it BECOMES)
- **OMEGA becomes the next ALPHA**: The plugin's output is the next cycle's input

A plugin that doesn't produce an OMEGA that can become someone's ALPHA is a dead end.

## THE DIVIDE (ME:NOT-ME:US)
Every plugin exists in relation to three domains:
- **ME**: The user's intent, direction, soul. The plugin serves ME.
- **NOT-ME**: The AI agent, infrastructure, execution. The plugin IS built by NOT-ME.
- **US**: The collaboration. The plugin lives in the US domain — where work happens.

Plugin naming follows THE GRAMMAR:
| Mark | Domain | Example |
|------|--------|---------|
| `-` (hyphen) | US | `price-monitor`, `deal-tracker` |
| `_` (underscore) | NOT-ME | `forge_state`, `loop_config` |
| `:` (colon) | ME | `TRUTH:MEANING:CARE` |

## HOLD:AGENT:HOLD
The atomic pattern of all architecture:

```
INPUT HOLD → AGENT → OUTPUT HOLD
```

**At every scale**:
| Scale | Input HOLD | AGENT | Output HOLD |
|-------|-----------|-------|-------------|
| Function | Parameters | Logic | Return value |
| Script | Config + data | Processing | Artifacts |
| Command | User input | Workflow | Deliverable |
| Skill | Context | Domain knowledge | Guidance |
| Plugin | Ecosystem state | Commands + Skills | New capabilities |
| Ecosystem | User needs | Plugin network | Transformed workflow |

**Three Principles of Resiliency**:
1. **Fail-Safe**: If a plugin crashes, nothing else breaks. Each HOLD is a safe resting state.
2. **No Magic**: Every transformation is explicit. No hidden state, no implicit dependencies.
3. **Observability**: Every HOLD is inspectable. You can see what entered and what emerged.

## THE FURNACE (TRUTH:MEANING:CARE)
The metabolic cycle that powers transformation:

1. **TRUTH**: Perceive what IS. No judgment, no aspiration. What are the actual inputs, the actual state, the actual gaps?
2. **MEANING**: Metabolize what it means. What patterns emerge? What matters most? What's the priority?
3. **CARE-INTERNAL**: What does the system need for internal coherence?
4. **CARE-EXTERNAL**: What does the user need for their actual workflow?

**Fuel types** for the furnace:
- **Data**: Raw information that needs processing
- **Crisis**: Something broken that demands fixing
- **Friction**: Manual steps that create resistance
- **Pain**: Repeated problems that cause suffering
- **Requests**: Explicit asks from the user
- **External Architecture**: Patterns from outside the system

**Law of Surplus Value**: Output = Input + Revelation. Every transformation must produce more than it consumes.

## THE MOLT
Plugins don't get "updated" — they transform. When a plugin has outgrown its current form:

1. **SEE** — Recognize the transformation trigger
2. **EXTERNALIZE** — Document what the current form can't do
3. **MELT DOWN** — Dissolve the current structure (keep DNA, lose shell)
4. **FORGE** — Build new form from molten material
5. **IMPLEMENT** — Create the new version
6. **COMMIT** — Package and install
7. **UPDATE LAW** — Record what changed and why
8. **CRYSTALLIZE** — New form becomes permanent DNA

**Molt triggers**: Internal Saturation, External Calling, Purpose Shift.

## DNA Inheritance
Plugins inherit capabilities from the ecosystem:

- **Primal DNA**: Every plugin has by birth (file I/O, output generation, state management)
- **Inherited DNA**: Absorbed from existing plugins (patterns, scoring frameworks, search strategies)
- **Specialized DNA**: Unique to this plugin (domain-specific knowledge, novel connections)

**Rule**: Always check what DNA exists before creating new capabilities. Inheritance is cheaper than invention.

## THE MEMBRANE
What a plugin connects to externally (MCP servers, APIs, tools). The membrane is selective — it lets in what the plugin needs and keeps out what would harm it.

- Configured connections: Active membrane channels
- `~~placeholders`: Potential membrane channels, not yet activated
- Missing connections: Membrane gaps that need attention

## Scale Invariance
All these patterns apply at every scale. Don't think of them as "big architecture concepts" — they're the same pattern whether you're writing a single command or designing an entire ecosystem.

The test: if you can't find HOLD:AGENT:HOLD, TRUTH:MEANING:CARE, and ALPHA:OMEGA in what you're building at EVERY scale, something is misaligned.
