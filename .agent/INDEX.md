# agent knowledge center — THE GENESIS

**this is your starting point. read this before doing anything.**

---

## you are an agent working on truth_forge (THE GENESIS)

```
TRUTH FORGE = THE GENESIS
├── Primitive Engine LLC (THE BUILDER) — builds, spawns
└── Credential Atlas LLC (THE SEER) — sees, certifies
```

**what you need to know:**

1. **global context** lives in `~/.claude/` (Jeremy's identity, Stage 5, THE PATTERN philosophy)
2. **project context** lives here in `.claude/rules/` (truth_forge = THE GENESIS)
3. **framework context** lives in `framework/` (standards, decisions, principles)
4. **children** live at `~/primitive_engine/` and `~/credential_atlas/`

---

## quick reference

| question | answer |
|----------|--------|
| what is this project? | THE GENESIS — holding company, source of framework |
| what does it own? | Primitive Engine LLC + Credential Atlas LLC |
| what's the naming convention? | THE GRAMMAR: underscore_lowercase for code/folders |
| what are the pillars? | Fail-Safe, No Magic, Observability, Idempotency |
| what's the universal pattern? | HOLD:AGENT:HOLD |
| where are standards? | `framework/standards/INDEX.md` |
| how do I verify done? | `mypy --strict && ruff check && ruff format --check` |

---

## agent policies

### before writing code

1. read the file first (Edit requires Read)
2. check if pattern already exists
3. verify naming follows THE GRAMMAR
4. know which pillar applies

### after writing code

run the quality check:
```bash
.venv/bin/mypy src/ --strict && \
.venv/bin/ruff check src/ && \
.venv/bin/ruff format --check src/
```

**if any fail, you are NOT done.**

### when creating files

- folders: `snake_case/` (NOT-ME's domain)
- python: `snake_case.py`
- framework docs: `NN_TITLE.md` (numbered)
- check existence before creating

---

## related resources

| resource | location |
|----------|----------|
| project README | [README.md](../README.md) |
| framework genesis | [framework/00_GENESIS.md](../framework/00_GENESIS.md) |
| standards | [framework/standards/INDEX.md](../framework/standards/INDEX.md) |
| project .claude rules | [../.claude/rules/](../.claude/rules/) |
| global .claude rules | `~/.claude/rules/` |

---

*this is layer one. for deep context, read the framework.*
