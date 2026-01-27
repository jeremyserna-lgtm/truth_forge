# The Claude Membrane Pattern

**Version**: 1.0
**Created**: 2025-12-24
**Status**: Foundational Design Pattern

---

## The Insight

Claude sessions are stateless. Claude instances don't communicate with each other.

But Claude is **consistent**. Claude produces **predictable artifacts**. You can design systems that **know what Claude will do** and wait for it.

No Claude tells another Claude. The systems are in place. When one Claude does something, another system was waiting for it—because they know how Claude works.

---

## The Membrane

There's a boundary between:

| Inside the Membrane | Outside the Membrane |
|---------------------|----------------------|
| Claude writes scripts | System discovers scripts |
| Claude creates files | System organizes files |
| Claude produces output | System renders output |
| Claude follows patterns | System expects patterns |

**The membrane is the interface between Claude's work and the infrastructure that consumes it.**

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   CLAUDE SESSION 1              THE MEMBRANE           INFRASTRUCTURE        │
│   ┌─────────────────┐          ┌───────────┐          ┌─────────────────┐   │
│   │                 │          │           │          │                 │   │
│   │ Writes script   │─────────▶│ @script   │─────────▶│ Script Runner   │   │
│   │ with decorator  │          │ pattern   │          │ discovers it    │   │
│   │                 │          │           │          │                 │   │
│   └─────────────────┘          └───────────┘          └─────────────────┘   │
│                                                                              │
│   CLAUDE SESSION 2                                                           │
│   ┌─────────────────┐          ┌───────────┐          ┌─────────────────┐   │
│   │                 │          │           │          │                 │   │
│   │ Creates doc     │─────────▶│ docs/     │─────────▶│ Documentation   │   │
│   │ in docs/product │          │ structure │          │ system indexes  │   │
│   │                 │          │           │          │                 │   │
│   └─────────────────┘          └───────────┘          └─────────────────┘   │
│                                                                              │
│   CLAUDE SESSION 3                                                           │
│   ┌─────────────────┐          ┌───────────┐          ┌─────────────────┘   │
│   │                 │          │           │          │                 │   │
│   │ Logs event with │─────────▶│ Central   │─────────▶│ Observability   │   │
│   │ log_event()     │          │ Services  │          │ sees everything │   │
│   │                 │          │           │          │                 │   │
│   └─────────────────┘          └───────────┘          └─────────────────┘   │
│                                                                              │
│   No Claude talks to another Claude.                                         │
│   The membrane catches what each Claude produces.                            │
│   The infrastructure was waiting.                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Designing for the Membrane

### 1. Define What Claude Produces

Claude will produce:
- Python scripts (with predictable structure)
- Markdown documentation
- SQL queries
- JSON/YAML configuration
- Log events via Central Services

### 2. Create Listeners for Each Type

| Claude Output | Listener | What It Does |
|---------------|----------|--------------|
| `@script` decorated function | Script Runner | Discovers, renders UI, executes |
| File in `docs/` | Documentation system | Indexes, links, searches |
| `log_event()` call | Observability | Aggregates, alerts, dashboards |
| File in root | Sweep system | Moves to correct location |
| BigQuery table creation | Schema discovery | Updates interface registry |

### 3. Make Patterns Obvious

Claude follows patterns when they're:
- **Documented** in CLAUDE.md
- **Enforced** by hooks
- **Easy** (less friction than alternatives)
- **Consistent** (same pattern everywhere)

When patterns are obvious, Claude produces predictable output. Predictable output is catchable by infrastructure.

---

## Examples

### Script Execution Layer

**Claude does**: Writes `capture.py` with `@script(name="Grindr Capture", params=[...])`

**System does**:
- Discovers the decorator
- Parses the metadata
- Renders a UI with sliders/buttons
- Runs the script when user clicks
- Streams logs to display
- Shows results

**No Claude told the system to do this.** The system was waiting for any file matching the `@script` pattern.

### File Organization

**Claude does**: Creates `analysis_results.json` in project root

**System does**:
- Sweep hook detects new file
- Pattern matcher identifies it as data output
- Moves to `data/analysis/`
- Logs the move

**No Claude told the system where to put it.** The system knows Claude makes files and organizes them.

### Central Services Logging

**Claude does**: Calls `log_event(component="capture", action="started")`

**System does**:
- Ingests into BigQuery
- Links to run_id
- Surfaces in dashboards
- Triggers alerts if needed

**No Claude told the system to monitor.** The system was listening to all log_event calls.

---

## The Meta-Pattern

This is **reactive architecture for AI agents**:

1. **Define the artifacts** agents will produce
2. **Create watchers** for each artifact type
3. **Build infrastructure** that reacts to artifacts
4. **Let agents work** without coordination

The agents don't know about each other. They just follow patterns. The infrastructure does the rest.

---

## Why This Works for Claude

Claude is:
- **Stateless**: Each session starts fresh
- **Consistent**: Follows documented patterns
- **Predictable**: Given the same instructions, produces similar output
- **Pattern-following**: Will use decorators, structure, conventions when shown

This means you can:
- **Design for Claude's outputs** not Claude's coordination
- **Build listeners** instead of orchestrators
- **Create membranes** that catch and process Claude's work
- **Trust the patterns** because Claude follows them

---

## Implementation Principles

### 1. Pattern First, Enforcement Second

Define what you want Claude to produce:
```python
@script(name="...", params=[...])
def main(): ...
```

Then build infrastructure that finds it:
```python
scripts = discover_files_with_decorator("@script")
```

### 2. Convention Over Configuration

Don't make Claude configure watchers. The watchers know the conventions:
- Scripts go in `code/` or `scripts/`
- Docs go in `docs/`
- Data goes in `data/`
- The watchers find them automatically

### 3. Graceful Discovery

Infrastructure discovers what exists rather than requiring registration:
```python
# Good: discover what's there
available_scripts = glob("**/*.py") |> has_decorator("@script")

# Bad: require Claude to register
REGISTRY.append({"name": "my_script", "path": "..."})
```

### 4. Fail Open

If Claude produces something unexpected, don't break. Catch it generically:
- Unknown file? → `_holding/` for triage
- Unknown decorator? → Log and skip
- Missing metadata? → Use defaults

---

## Relationship to Other Patterns

| Pattern | How It Uses the Membrane |
|---------|-------------------------|
| Script Execution Layer | Watches for `@script` decorated files |
| File Organization | Watches for new files, applies rules |
| Central Services | Provides the logging/identity membrane |
| Substrate Fluidity | Watches BigQuery INFORMATION_SCHEMA |
| Definition of Done | Defines what patterns Claude should follow |

---

## The Bottom Line

**Design for what Claude produces, not what Claude communicates.**

Claude sessions don't talk to each other. But they all produce similar artifacts. Build infrastructure that:
- Knows the patterns
- Waits for them
- Reacts when they appear
- Requires no coordination

This is the Claude Membrane Pattern: the boundary where Claude's work becomes system functionality, automatically.

---

## Related Documents

- [SCRIPT_EXECUTION_LAYER.md](./SCRIPT_EXECUTION_LAYER.md) - Primary implementation
- [DESIGN_PRINCIPLES.md](./DESIGN_PRINCIPLES.md) - Core design philosophy
- [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) - Overall architecture
