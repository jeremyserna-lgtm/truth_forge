# Folder Purposes

**What each folder is for and its git status.**

---

## Folder Reference

| Folder | Purpose | Git Status |
|--------|---------|------------|
| `src/` | Importable Python package | Committed |
| `pipelines/core/` | Universal pipeline engine | Committed |
| `pipelines/adapters/` | Project-specific configs | Committed |
| `apps/` | Deployable software | Committed |
| `projects/` | Work items with their data | Selective |
| `config/base/` | Shared configuration | Committed |
| `config/local/` | Personal/secrets | **Gitignored** |
| `data/` | Data storage | **Gitignored** |
| `docs/` | Documentation | Committed |
| `tests/` | Test suite | Committed |
| `framework/` | Standards & theory (genesis only) | Committed |

---

## HOLD:AGENT:HOLD Mapping

```
data/staging/         → pipelines/core/        → data/output/
(HOLD₁ - input)         (AGENT - process)        (HOLD₂ - output)
```

| Folder | Role |
|--------|------|
| `data/staging/` | HOLD₁ - input data |
| `pipelines/` | AGENT - processing code |
| `data/output/` | HOLD₂ - output data |
| `src/` | AGENT - service code |
| `config/` | Configuration for AGENT |

---

## THE GRAMMAR for Folders

| Mark | Application | Example |
|------|-------------|---------|
| `-` (hyphen) | Project names, branches | `feature-auth`, `claude-code` |
| `_` (underscore) | Folder names (infrastructure) | `code_quality/`, `data_models/` |

**Why underscore for folders?** Folders are infrastructure. Infrastructure is NOT-ME's domain. Therefore: underscore + lowercase.

---

## NEVER

```
✗ Create unique folder structures per organism
✗ Commit secrets to config/local/
✗ Put data in committed folders without .gitignore
✗ Use CamelCase or PascalCase for folder names
```

## ALWAYS

```
✓ Use src/ layout for importable code
✓ Separate base/ and local/ config
✓ Gitignore data/ and config/local/
✓ Use snake_case for folder names
```

---

## UP

[INDEX.md](INDEX.md)
