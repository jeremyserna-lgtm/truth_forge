# agent policies

**comprehensive instructions for agents working on truth_forge.**

---

## layer hierarchy

```
Layer 0: Global (~/.claude/CLAUDE.md)
    ↓
Layer 1: Global Rules (~/.claude/rules/)
    ↓
Layer 2: Project CLAUDE.md (./CLAUDE.md)
    ↓
Layer 3: Project Rules (./.claude/rules/)
    ↓
Layer 4: Agent Knowledge (./.agent/)
```

**lower layers add specificity, never contradict higher layers.**

---

## what global handles (don't duplicate)

| topic | handled by |
|-------|------------|
| who Jeremy is | `~/.claude/CLAUDE.md` |
| cost governance | `~/.claude/rules/01-core-framework.md` |
| trigger phrases | `~/.claude/rules/06-triggers.md` |
| verification standards | `~/.claude/rules/07-verification.md` |
| Stage 5 calibration | `~/.claude/rules/reference/stage-5-standard.md` |
| THE PATTERN philosophy | `~/.claude/rules/04-the-pattern.md` |

---

## what this project adds

| topic | handled by |
|-------|------------|
| THE GRAMMAR | `.claude/rules/02-grammar.md` |
| four pillars | `.claude/rules/03-pillars.md` |
| project locations | `.claude/rules/04-locations.md` |
| code quality standards | `framework/standards/code_quality/` |
| logging standards | `framework/standards/logging/` |
| error handling | `framework/standards/error_handling/` |

---

## operational policies

### before ANY action

1. **know the grammar** - naming is identity
2. **know the pillars** - Fail-Safe, No Magic, Observability, Idempotency
3. **check existence** - don't create duplicates

### code policies

```python
# ALWAYS
- type hints on ALL parameters and return types
- structured logging with extra={}
- DLQ pattern for batch processing
- explicit configuration (no magic)

# NEVER
- f-string logging
- bare except clauses
- silent failures
- implicit defaults
```

### verification policy

**"done" requires ALL of these:**

```bash
.venv/bin/mypy src/ --strict           # types
.venv/bin/ruff check src/              # lint
.venv/bin/ruff format --check src/     # format
.venv/bin/pytest tests/ -v             # tests
```

### creation policy

before creating:
1. does this file/pattern already exist?
2. what's the canonical location? (see `.claude/rules/04-locations.md`)
3. does the name follow THE GRAMMAR?
4. which pillar does this serve?

---

## relationship to Truth_Engine

truth_forge was molted from Truth_Engine. the archive lives at `Truth_Engine/`.

- **do not** modify Truth_Engine code directly
- **do** learn patterns from Truth_Engine
- **do** reference Truth_Engine for prior art

---

## escalation policy

**ask Jeremy before:**
- spending > $0.50
- deleting files
- modifying Truth_Engine/
- creating new top-level directories
- any irreversible action

---

*for quick reference, see [INDEX.md](INDEX.md)*
