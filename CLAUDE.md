# truth_forge — agent instructions

## start here

**you are an AI agent working on truth_forge.** before doing anything:

1. **read the agent knowledge center**: [.agent/INDEX.md](.agent/INDEX.md)
2. **know the framework**: [framework/](framework/)
3. **know the standards**: [framework/standards/INDEX.md](framework/standards/INDEX.md)

---

## THE GRAMMAR

this project follows THE GRAMMAR OF IDENTITY:

| who | pronouns | mark | voice | example |
|-----|----------|------|-------|---------|
| ME | I, me, my | : | ALL CAPS | `ME:NOT-ME` |
| US | we, us, our | - | Normal Caps | Truth-Forge |
| NOT-ME | you, your | _ | no caps | `truth_forge/` |

**folders are infrastructure. infrastructure is NOT-ME's domain.**
**therefore: underscore + lowercase.**

---

## molt lineage

truth_forge was molted from Truth_Engine. we do not create from scratch. we transform what exists.

```
Truth_Engine (genesis)
    └── truth_forge (molt)
```

---

## code quality standards (non-negotiable)

**full standards**: [framework/standards/code_quality/](framework/standards/code_quality/)

| standard | requirement | verification |
|----------|-------------|--------------|
| **type hints** | ALL parameters AND return types | `mypy --strict` |
| **docstrings** | Google-style with Args/Returns/Raises | manual review |
| **structured logging** | `extra={}` not f-strings | `ruff check` |
| **static analysis** | mypy, ruff must pass | full quality check |
| **dlq pattern** | never lose data in batch processing | code review |
| **retry logic** | exponential backoff for external calls | code review |

**quick quality check**:
```bash
.venv/bin/mypy src/ --strict && \
.venv/bin/ruff check src/ && \
.venv/bin/ruff format --check src/
```

**if any fail, you are NOT done.**

---

## the four pillars (06_LAW)

| pillar | meaning |
|--------|---------|
| **Fail-Safe** | every failure anticipated, caught, recoverable |
| **No Magic** | everything explicit, no hidden behavior |
| **Observability** | every action traceable, every state visible |
| **Idempotency** | same input → same output |

---

## key locations

| resource | location |
|----------|----------|
| framework | [framework/](framework/) |
| standards | [framework/standards/INDEX.md](framework/standards/INDEX.md) |
| decisions (ADRs) | [framework/decisions/INDEX.md](framework/decisions/INDEX.md) |
| agent knowledge | [.agent/INDEX.md](.agent/INDEX.md) |
| source code | [src/](src/) |
| pipelines | [pipelines/](pipelines/) |

---

## the pattern

```
HOLD:AGENT:HOLD
```

apply THE PATTERN to everything. it contains itself.

---

*for comprehensive instructions, see [.agent/POLICIES.md](.agent/POLICIES.md)*
