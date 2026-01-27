# Truth Engine System Invariants

**Version**: 1.0
**Created**: 2025-12-24
**Status**: Foundational Context

---

## The Principle

Truth Engine works because of **constants that never change**. These invariants allow the system to make assumptions, and assumptions enable reliability.

Design for the invariants. Don't abstract them away. Lean into them.

---

## The Invariants

These are **baselines**, not absolutes. The system is designed for the primary case. Variations exist (Cursor, Copilot, Codex) but the infrastructure leans into the primary.

### 1. Primarily Claude Code

**The baseline**: Development primarily happens through Claude Code (the Anthropic CLI product).

**Variations exist**:
- Copilot Chat in VS Code
- Cursor agents in Cursor IDE
- Codex CLI
- But Claude Code would likely orchestrate incorporating these

**What this enables**:
- Can assume Python scripts with consistent patterns
- Can assume file structures Claude creates
- Can assume decorator-based metadata
- Can assume Central Services integration

**System implications**:
- Script Execution Layer expects Python
- File organization expects Claude's patterns
- Documentation expects markdown
- Hooks work because Claude is predictable

### 2. Primarily VS Code on Mac

**The baseline**: Jeremy works in VS Code on macOS.

**Variations exist**:
- Cursor IDE (also Mac)
- Terminal/CLI directly
- But Mac remains constant, VS Code is primary

**What this enables**:
- Can use macOS Keychain for secrets
- Can use Playwright with system browsers
- Can use native file system operations
- Can use Mac-native GUI (Tauri, Swift)
- Can assume screen resolution, fonts, UI conventions

**System implications**:
- Credential storage uses `keyring` library
- Desktop app targets Mac first
- File paths are Unix-style
- Can rely on AppleScript, Automator if needed

### 3. Always Conversations

**The baseline**: The primary data type is conversational text.

**Why this is stable**:
- Jeremy's primary interaction is conversation with AI
- Text messages are conversations
- Even app extractions (Grindr) are conversations

**What this enables**:
- Can assume L1-L8 entity hierarchy works
- Can assume NLP processing patterns
- Can assume turn-based structure
- Can assume message → enrichment → insight flow

**System implications**:
- Universal Pipeline Pattern applies
- Entity extraction is consistent
- Enrichments are predictable
- Analysis methods are reusable

### 4. Always AI Doing the Coding

**The baseline**: Jeremy is not a coder. AI does the coding.

**What this means**:
- Claude writes the Python
- Claude writes the SQL
- Claude creates the structures
- Jeremy defines goals, AI implements

**What this enables**:
- Can assume AI-generated patterns
- Can assume decorator-based metadata
- Can assume consistent file structures
- Can assume Central Services integration (AI follows rules)

**System implications**:
- Claude Membrane Pattern works
- Script Execution Layer makes sense
- Hooks enforce patterns AI follows
- Infrastructure catches what AI produces

### 5. Always Extraction From Apps

**The baseline**: Data comes from extracting from specific apps (Grindr, iMessage, Zoom, AI platforms).

**What this enables**:
- Can build source-specific adapters
- Can assume capture → parse → ingest flow
- Can assume raw → processed → entities progression
- Can assume data_sources/ directory structure

**System implications**:
- Each data source gets a directory
- Universal Pipeline Pattern applies
- Capture scripts follow similar patterns
- Parsed data follows similar schemas

### 6. Always Stage 5

**The baseline**: Jeremy operates at Kegan Stage 5 (Self-Transforming Mind).

**Why this is stable**:
- This is developmental, not situational
- It defines how he processes
- It's the cognitive substrate

**What this enables**:
- Can assume clear boundaries are needed
- Can assume controlled execution (not continuous)
- Can assume multiple perspectives are valued
- Can assume system-seeing is desired

**System implications**:
- No unbounded daemons
- User-triggered processing
- Transparency in system operation
- Meta-layers that show the system seeing

### 7. Always Python/Markdown/SQL

**The baseline**: The output artifacts are Python scripts, Markdown docs, and SQL tables.

**Why this is stable**:
- Python: Claude's primary coding language
- Markdown: Universal documentation
- SQL/BigQuery: The data layer

**What this enables**:
- Script Execution Layer expects Python
- Documentation system expects Markdown
- Data layer expects SQL
- Hooks can pattern-match these formats

**System implications**:
- Three core artifact types to handle
- Predictable patterns per type
- Tools designed for these formats

---

## The Compound Effect

When you combine invariants, you get **architectural certainty**:

```
Always Claude Code
    + Always conversations
    + Always extraction from apps
    = Script Execution Layer that renders capture tools automatically
```

```
Always VS Code on Mac
    + Always Keychain
    + Always Claude writing scripts
    = Credential management that just works
```

```
Always AI conversations
    + Always L1-L8 hierarchy
    + Always Stage 5 controlled processing
    = Universal Pipeline Pattern that applies to every source
```

---

## What This Means for Design

### Don't Abstract the Constants

**Wrong**: "Let's make this work on Windows too"
**Right**: "We're on Mac. Use Keychain, use Tauri, use Mac conventions."

**Wrong**: "Let's support any data format"
**Right**: "It's conversational. Use L1-L8. Build adapters per source."

**Wrong**: "Let's make it flexible for any AI"
**Right**: "It's Claude Code. Expect decorators, Python, Central Services."

### Lean Into the Patterns

The invariants create patterns. Embrace them:

| Invariant | Pattern to Lean Into |
|-----------|---------------------|
| Always Claude Code | `@script` decorator for every runnable |
| Always Mac | Keychain for secrets, Tauri for desktop |
| Always conversations | L1-L8 entity hierarchy |
| Always AI extraction | data_sources/{source}/ structure |
| Always Stage 5 | User-triggered, bounded, visible |

### Build for the Environment You Have

You're not building a general-purpose tool. You're building:

- For Jeremy specifically
- On Mac specifically
- With Claude specifically
- For conversations specifically
- From apps specifically

This specificity is a **feature**, not a limitation. It enables:
- Simpler architecture
- Fewer edge cases
- More reliable patterns
- Faster development

---

## Relationship to Claude Membrane

The invariants define **what's on the other side of the membrane**:

| Invariant | Membrane Implication |
|-----------|---------------------|
| Always Claude Code | Infrastructure expects Python scripts with decorators |
| Always Mac | Infrastructure uses Mac-native capabilities |
| Always conversations | Infrastructure has L1-L8 ready |
| Always extraction | Infrastructure has capture → parse → ingest |
| Always Stage 5 | Infrastructure is user-triggered, not automatic |

The Claude Membrane Pattern works **because** of these invariants. Without them, you'd need much more flexible (and complex) infrastructure.

---

## Related Documents

- [CLAUDE_MEMBRANE_PATTERN.md](./CLAUDE_MEMBRANE_PATTERN.md) - How Claude work becomes system functionality
- [SCRIPT_EXECUTION_LAYER.md](./SCRIPT_EXECUTION_LAYER.md) - Primary implementation
- [TRUTH_ENGINE_VISION.md](./TRUTH_ENGINE_VISION.md) - Overall vision
- [../architecture/STAGE_FIVE_MANIFEST.md](../architecture/STAGE_FIVE_MANIFEST.md) - Stage 5 alignment
