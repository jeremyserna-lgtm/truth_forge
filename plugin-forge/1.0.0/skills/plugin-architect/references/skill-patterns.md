# Skill Patterns — Structured Through HOLD:AGENT:HOLD

Common patterns observed across production Cowork plugins, now understood through the framework.

## Pattern 1: Domain Expert (METABOLISM)
A skill that encodes deep knowledge about a specific domain. This is the METABOLISM pattern — the skill IS the metabolic knowledge that powers commands.

**Examples**: `sql-queries`, `statistical-analysis`, `data-visualization`

**HOLD:AGENT:HOLD structure**:
- INPUT HOLD: Domain question or task
- AGENT: Expert knowledge patterns and decision trees
- OUTPUT HOLD: Domain-specific guidance or artifact

**References hold**: Dialect-specific or framework-specific depth (MEMORY)

**When to use**: The plugin needs expert-level decisions in a specialized area.

## Pattern 2: Workflow Orchestrator (CARE-EXTERNAL)
A skill that coordinates a multi-step HOLD:AGENT:HOLD chain.

**Examples**: `ticket-triage`, `call-prep`, `daily-briefing`

**HOLD:AGENT:HOLD structure**:
- INPUT HOLD: Workflow trigger with context
- AGENT: Step-by-step process with branching logic (each step is its own HOLD:AGENT:HOLD)
- OUTPUT HOLD: Completed workflow result

**References hold**: Templates, checklists, and example outputs (MEMORY)

**When to use**: The plugin guides a complex process from start to finish.

## Pattern 3: Research Synthesizer (TRUTH → MEANING)
A skill that gathers TRUTH from multiple sources and synthesizes MEANING.

**Examples**: `customer-research`, `account-research`, `knowledge-synthesis`

**HOLD:AGENT:HOLD structure**:
- INPUT HOLD: Research question or topic
- AGENT: Multi-source search, prioritization, and synthesis (THE FURNACE applied to information)
- OUTPUT HOLD: Synthesized view with sources and confidence

**References hold**: Source-specific query patterns and scar history (MEMORY)

**When to use**: The plugin needs to pull from multiple data sources and create unified insight.

## Pattern 4: Output Generator (CARE → CRYSTALLIZE)
A skill that produces a specific artifact. This is THE FORGE process applied to content creation.

**Examples**: `response-drafting`, `feature-spec`, `stakeholder-comms`

**HOLD:AGENT:HOLD structure**:
- INPUT HOLD: Content requirements and context
- AGENT: Template application, tone calibration, quality checking
- OUTPUT HOLD: Polished deliverable (must demonstrate surplus value — the output exceeds what any single input provided)

**References hold**: Example outputs and audience-specific variations (MEMORY)

**When to use**: The plugin needs to create polished deliverables.

## Pattern 5: Analyzer (TRUTH → MEANING with scoring)
A skill that examines inputs and produces structured assessments. This is the TRUTH:MEANING cycle with explicit scoring.

**Examples**: `data-validation`, `competitive-analysis`, `ecosystem-analyzer`

**HOLD:AGENT:HOLD structure**:
- INPUT HOLD: Subject to be analyzed
- AGENT: Analysis framework with scoring criteria (THE FURNACE: burn away noise, keep signal)
- OUTPUT HOLD: Structured assessment with scores and recommendations

**References hold**: Calibration data, benchmarks, and scar catalog (MEMORY)

**When to use**: The plugin needs to evaluate something and produce structured judgment.

## Pattern 6: Connector Bridge (THE MEMBRANE)
A skill that translates between tools or data formats. This IS the membrane function — selectively filtering what crosses between systems.

**Examples**: `data-context-extractor`, `source-management`

**HOLD:AGENT:HOLD structure**:
- INPUT HOLD: Data from source system (in source format)
- AGENT: Mapping logic and transformation rules (THE MEMBRANE's filter)
- OUTPUT HOLD: Data in target format (ready for consumption)

**References hold**: Tool-specific API patterns and data schemas (MEMORY)

**When to use**: The plugin needs to move data between systems or translate formats.

## Pattern 7: Recursive Engine (THE LOOP)
A skill that powers a self-feeding loop where outputs become inputs to the next cycle.

**Examples**: `recursive-engine` (Plugin Forge's own engine)

**HOLD:AGENT:HOLD structure**:
- INPUT HOLD (ALPHA): Current ecosystem state + loop memory
- AGENT: THE FURNACE (TRUTH:MEANING:CARE) metabolizing gaps into recommendations
- OUTPUT HOLD (OMEGA): New plugin + predictions (becomes next cycle's ALPHA)

**References hold**: Evolution patterns, DNA registry, meta-learnings (GENETIC MEMORY)

**When to use**: The plugin needs to improve itself or its context with each use.

## Combining Patterns

Most effective plugins combine 2-3 patterns. The framework reveals WHY certain combinations work:

- **Research + Output** (TRUTH + CARE): Perceive reality, then serve the user. Natural metabolic flow.
- **Analyzer + Orchestrator** (MEANING + CARE): Extract significance, then act on it. THE FURNACE in action.
- **Domain Expert + Output** (METABOLISM + CRYSTALLIZE): Apply deep knowledge to produce lasting artifacts.
- **Connector + Analyzer** (MEMBRANE + FURNACE): Bridge data sources, then metabolize the combined view.
- **Research + Recursive** (TRUTH + THE LOOP): Each research cycle informs the next. ALPHA:OMEGA.

## THE GRAMMAR for Skill Naming

Apply the ontological grammar to skill names:
- **Hyphen-case** for all skill names (US-domain — collaborative work): `data-exploration`, `competitive-analysis`
- **Underscore_case** for internal state files: `forge_state.json`, `loop_config.json`
- **COLON:CASE** only for framework concept references: `TRUTH:MEANING:CARE`, `HOLD:AGENT:HOLD`

Never name a skill with underscores (that's infrastructure domain) or colons (that's philosophy domain).
