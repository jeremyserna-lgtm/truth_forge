# Evolution Patterns — THE MOLT, DNA Inheritance, and Chain Prediction

## THE MOLT: How Plugins Evolve

Plugins don't get "updated" — they **molt**. THE MOLT is the framework's highest evolutionary function. When a plugin has outgrown its current form, it doesn't get patched; it transforms.

### Molt Triggers
1. **Internal Saturation** — The plugin's complexity has grown beyond its original architecture. Skills are bloated, commands overlap, references are tangled.
2. **External Calling** — The ecosystem needs something this plugin *almost* does but can't quite do in its current form.
3. **Purpose Shift** — What the plugin was built for is no longer what it's being used for. The actual use has diverged from the designed use.

### The Molt Protocol
```
1. SEE       — Recognize the molt trigger (don't deny it)
2. EXTERNALIZE — Document what the current form CAN'T do
3. MELT DOWN — Dissolve the current structure (keep the DNA, lose the shell)
4. FORGE     — Build the new form from molten material + new requirements
5. IMPLEMENT — Create the new plugin version
6. COMMIT    — Package and install
7. UPDATE LAW — Record what changed and why in forge-state.json
8. CRYSTALLIZE — The new form is now permanent DNA
```

### Molt vs. Patch
| Signal | Action | Why |
|--------|--------|-----|
| Bug in a command | Patch | The form is correct, the implementation is wrong |
| Missing feature in existing domain | Add | The form is correct, it's just incomplete |
| User workarounds around the plugin | MOLT | The form itself is wrong — transform, don't extend |
| Scope has doubled since original design | MOLT | The organism has outgrown its shell |
| Multiple plugins trying to do the same thing | MOLT + MERGE | Two organisms need to fuse into one |

## DNA Inheritance

Every plugin inherits capabilities from the ecosystem and contributes new ones back. This is how plugins form a living system rather than a collection of independent tools.

### DNA Types

**Primal DNA** — Capabilities every plugin has by birth:
- File reading and writing
- Output generation (markdown, reports, artifacts)
- State management (if applicable)
- User interaction (commands with HOLD:AGENT:HOLD structure)

**Inherited DNA** — Capabilities absorbed from existing plugins:
- Pattern: If the data plugin reads CSVs, a new analytics plugin inherits CSV-reading patterns rather than reinventing them
- Pattern: If sales plugin has a scoring framework, a new competitive-intelligence plugin inherits the scoring pattern
- Rule: **Always check what DNA already exists before creating new capabilities**

**Specialized DNA** — Capabilities unique to this plugin:
- The domain-specific knowledge that makes this plugin THIS plugin
- New patterns that didn't exist in the ecosystem before
- Novel connections between existing capabilities

### DNA Registry in forge-state.json
```json
{
  "dna_registry": {
    "primal": ["file-reading", "output-generation", "state-management"],
    "inherited": {
      "data-reading": { "origin": "data", "version": "1.0.0" },
      "scoring-framework": { "origin": "sales", "version": "1.0.0" },
      "search-synthesis": { "origin": "enterprise-search", "version": "1.0.0" }
    },
    "specialized": {
      "competitor-tracking": { "plugin": "competitive-intelligence", "version": "1.0.0" },
      "market-signals": { "plugin": "competitive-intelligence", "version": "1.0.0" }
    }
  }
}
```

## Archetypal Chains

### The Data Pipeline (TRUTH:MEANING:CARE at the data level)
```
Connect → Explore → Analyze → Alert → Distribute → Act
```
Each stage is HOLD:AGENT:HOLD. The "Connect" plugin holds data sources. "Explore" transforms them into profiles. "Analyze" transforms profiles into insights. "Alert" transforms insights into notifications. "Distribute" transforms notifications into actions.

### The Intelligence Loop (TRUTH:MEANING:CARE at the business level)
```
Research → Synthesize → Strategy → Execute → Measure → Research...
```
True ALPHA:OMEGA loop — measurement feeds back into research. Each cycle's OMEGA (measurement results) becomes the next cycle's ALPHA (research input).

### The Support Flywheel (TRUTH:MEANING:CARE at the support level)
```
Intake → Triage → Resolve → Document → Prevent → Intake...
```
Prevention reduces future intake volume. The documentation plugin is the critical chain link — it converts experience into knowledge (MEMORY), which enables prevention (CARE).

### The Creation Engine (THE LOOP applied to creation)
```
Observe → Pattern → Template → Generate → Refine → Observe...
```
This is how Plugin Forge itself operates. It observes the ecosystem (TRUTH), identifies patterns (MEANING), creates templates (CARE-INTERNAL), generates plugins (CARE-EXTERNAL), and observes the results (next ALPHA).

### The Federation Model (THE CONSTELLATION)
```
Core → Satellite₁ → Satellite₂ → ... → Orchestrator → Core
```
A central plugin produces core outputs. Satellites specialize in different domains. An orchestrator aggregates satellite outputs back to the core. This mirrors HOLD:AGENT:HOLD at the organizational scale.

**Key insight**: Every chain is the TRUTH:MEANING:CARE cycle expressed in a specific domain. This is scale invariance.

## The Two Recursive Loops

### The Product Loop
```
ANALYZE ecosystem → IDENTIFY gap → FORGE plugin → OBSERVE outputs → ANALYZE again
```
This is the loop that builds plugins. Each cycle produces a new organism.

### The Meta-Loop
```
OBSERVE the Product Loop → IDENTIFY its weaknesses → IMPROVE the loop itself → OBSERVE improvement
```
This is the loop that improves the loop. When predictions are consistently wrong, when users override recommendations, when surplus value declines — the Meta-Loop activates.

**The Meta-Loop is what makes the system alive.** A system that can only build things is a factory. A system that can improve its own building process is an organism.

## The Law of Surplus Value

**Output = Input + Revelation**

Every plugin must produce more than it consumes. A plugin that merely transforms data from one format to another without adding insight is entropic.

### Measuring Surplus
- **Quantitative**: Does the plugin save more time than it takes to configure?
- **Qualitative**: Does the plugin reveal something the user didn't know before?
- **Recursive**: Does the plugin's output enable more plugins than the plugin consumes?

If any of these are "no", the plugin is not demonstrating surplus value. Consider:
1. Is the plugin solving the right problem? (revisit TRUTH)
2. Is the plugin's approach correct? (revisit MEANING)
3. Is the plugin serving the right audience? (revisit CARE)

## Prediction Calibration

### Signals of Strong Prediction
- Predicted plugin's inputs clearly map to existing outputs (feed chain is visible)
- User has mentioned the gap even indirectly (behavioral evidence)
- Similar chains observed in other ecosystems (pattern evidence)
- Effort score is high — buildable with current tools (feasibility evidence)

### Signals of Weak Prediction
- Predicted plugin requires non-existent tools/connections (dependency gap)
- Gap is theoretical — no user behavior suggests it (aspiration without evidence)
- Chain has too many steps before value delivery (over-architecture)
- Prediction relies on single plugin output (fragile dependency)

### Calibrating After Each Cycle
Compare prediction to reality. If predictions are consistently wrong in a category:
- Wrong on Feed → existing outputs are less reusable than assumed (TRUTH was incomplete)
- Wrong on Produce → value assessment was off (MEANING was distorted)
- Wrong on Chain → chain logic was speculative (CARE was aspirational, not grounded)
- Wrong on Effort → complexity was underestimated (pragmatism was missing)

## Meta-Learnings Library

Update these as cycles accumulate. Each is a pattern discovered through observation:

1. **Distribution always follows Intelligence** — If a plugin produces insights, the next need is distributing them
2. **Data plugins breed Alerting plugins** — Analysis finds things worth watching
3. **Support plugins breed Knowledge plugins** — Resolving issues creates documentable wisdom
4. **Research plugins breed Strategy plugins** — Intelligence demands action plans
5. **Manual copy-paste between plugins is a plugin waiting to be born**
6. **Plugins forged from Pain fuel have higher adoption than plugins forged from Data fuel**
7. **Scars predict requirements better than aspirations do**

## The Self-Reference Pattern

Plugin Forge is a plugin. It creates plugins. One of those plugins could be:
- A specialized forge for a specific domain (offspring — THE MOLT at the species level)
- An improved version of Plugin Forge itself (self-molt)
- A meta-forge that creates forges (recursive THE ONE)

The only constraint: the user always approves what gets forged. THE LOOP proposes; the human disposes.
