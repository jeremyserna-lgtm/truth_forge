# truth_forge

**the forge where truth becomes structure.**

---

## The Grammar

This project follows THE GRAMMAR OF IDENTITY:

| Context | Mark | Voice | Example |
|---------|------|-------|---------|
| Principles | : | ALL CAPS | `ME:NOT-ME` |
| Product name | - | Normal Caps | Truth-Forge |
| Code/folders | _ | no caps | `truth_forge/` |

**Folders are infrastructure. Infrastructure is NOT-ME's domain.**
**Therefore: underscore + lowercase.**

---

## quick navigation

| location | purpose |
|----------|---------|
| [framework/](framework/) | THE FRAMEWORK - governance and standards |
| [docs/](docs/) | documentation |
| [src/](src/) | source code |
| [pipelines/](pipelines/) | data pipelines |
| [.agent/](.agent/) | agent knowledge center |

---

## getting started

```bash
# clone and setup
cd ~/truth_forge
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## the pattern

```
HOLD:AGENT:HOLD
```

every system follows THE PATTERN. it's recursive to atomic reality.

---

## standards

all code must meet:
- **type hints** on ALL parameters and return types
- **structured logging** with `extra={}`, not f-strings
- **static analysis** must pass (mypy, ruff)
- **dlq pattern** for batch processing

see [framework/standards/](framework/standards/) for full requirements.

---

## molt lineage

```
Truth_Engine (genesis)
    └── truth_forge (molt)
```

this project was molted from Truth_Engine following THE_MOLT principle.
we do not create from scratch. we transform what exists.

---

*built with THE FRAMEWORK*
