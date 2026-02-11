# PROJECT_STRUCTURE

**The canonical folder structure for all organisms in the Truth Engine colony.**

| Attribute | Value |
|-----------|-------|
| Status | **CANONICAL** |
| Scope | All organisms (genesis + daughters) |
| Created | 2026-01-26 |
| Validated | Industry-aligned (src layout, Kedro patterns, monorepo standards) |

---

## Principle

**Compete at architecture and theory, not code structure.**

All organisms use industry-standard folder structures. The differentiation is in THE FRAMEWORK, not in folder naming. This enables:
- Familiarity for new contributors
- Tool compatibility (linters, CI/CD, IDEs)
- Focus on what matters: the thinking, not the scaffolding

---

## Universal Structure (All Organisms)

```
{organism}/
├── .claude/                  # Claude Code configuration
│   ├── commands/             # Slash commands
│   ├── rules/                # Project-specific rules
│   └── skills/               # Project-specific skills
│
├── .seed/                    # Federation identity
│   ├── identity.json         # WHO this organism is
│   └── sync.py               # HOW it talks to genesis
│
├── src/                      # Source code (src layout)
│   └── {package_name}/       # Importable package
│       ├── __init__.py
│       ├── services/         # Service modules
│       ├── models/           # Data models
│       └── utils/            # Utilities
│
├── pipelines/                # Universal pipeline + adapters
│   ├── core/                 # THE universal pipeline
│   │   ├── stages/
│   │   │   ├── __init__.py
│   │   │   ├── stage_0_ingest.py
│   │   │   ├── stage_1_transform.py
│   │   │   ├── stage_2_enrich.py
│   │   │   └── stage_3_output.py
│   │   ├── runner.py
│   │   └── base_config.py
│   └── adapters/             # Project-specific configurations
│       └── {project_name}/
│           ├── config.yaml
│           └── hooks.py      # Optional custom hooks
│
├── apps/                     # Deployable software
│   ├── web/                  # Web applications
│   ├── cli/                  # Command-line tools
│   └── api/                  # API services
│
├── projects/                 # Work items / initiatives
│   └── {project_name}/
│       ├── data/             # Project-specific data
│       ├── docs/             # Project documentation
│       └── README.md
│
├── config/                   # Configuration files
│   ├── base/                 # Shared config (committed)
│   └── local/                # Personal/secrets (gitignored)
│
├── data/                     # Data storage (mostly gitignored)
│   ├── local/                # Local working data
│   ├── staging/              # HOLD₁ (input)
│   └── output/               # HOLD₂ (output)
│
├── docs/                     # Documentation
│   ├── technical/
│   ├── business/
│   └── archive/
│
├── tests/                    # Test suite
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── scripts/                  # Utility scripts
│
├── CLAUDE.md                 # Project config for Claude
├── README.md                 # Project overview
├── pyproject.toml            # Python project config
├── .gitignore
└── .pre-commit-config.yaml   # Pre-commit hooks
```

---

## Genesis-Only Addition

Genesis (truth_forge) contains the canonical framework:

```
truth_forge/
├── [all universal folders above]
│
└── framework/                # ONLY IN GENESIS
    ├── 00_THE_FRAMEWORK.md   # Theory
    ├── 06_LAW.md             # Inviolable rules
    ├── standards/            # Canonical standards
    │   ├── INDEX.md          # Standards registry
    │   ├── CODE_QUALITY.md
    │   ├── ERROR_HANDLING.md
    │   ├── PROJECT_STRUCTURE.md  # This document
    │   └── ...
    ├── decisions/            # Architecture Decision Records
    └── archive/              # Deprecated framework docs
```

**Daughters do NOT have `/framework/`.** They reference genesis via federation.

---

## Pipeline Architecture

### The Pattern

```
ADAPTER (config) → HOLD₁ (source) → UNIVERSAL PIPELINE → HOLD₂ (destination)
```

### Core Pipeline (One to Maintain)

```python
# pipelines/core/runner.py
def run_pipeline(adapter: str):
    config = load_adapter(f"adapters/{adapter}/config.yaml")

    data = stage_0.ingest(config.source)
    data = stage_1.transform(data, config)
    data = stage_2.enrich(data, config)
    stage_3.output(data, config.destination)
```

### Adapter Configuration

```yaml
# pipelines/adapters/claude_code/config.yaml
name: claude_code
source:
  type: jsonl
  path: projects/claude_code/data/raw/
destination:
  type: duckdb
  path: data/output/knowledge.duckdb
  table: claude_code_atoms
stages:
  transform:
    extract_fields: [content, metadata, timestamp]
  enrich:
    embedding_model: text-embedding-3-small
```

### Running Pipelines

```bash
# Run pipeline for a specific project
python -m pipelines.core.runner --adapter claude_code
```

---

## Folder Purposes

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

## Industry Alignment

| Pattern | Standard | Source |
|---------|----------|--------|
| src layout | Python Packaging Guide | packaging.python.org |
| Modular pipelines | Kedro, Dagster | kedro.org |
| Config-driven adapters | Kedro parameters | kedro.org |
| projects/ + lib/ split | Monorepo pattern | Opendoor, Tweag |
| conf/base + conf/local | Environment separation | Kedro |

---

## Enforcement

### Pre-Commit Hook

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: structure-check
      name: Project Structure Check
      entry: python scripts/check_structure.py
      language: python
      pass_filenames: false
```

### Required Files

Every organism MUST have:
- `CLAUDE.md` - Claude Code configuration
- `README.md` - Project overview
- `pyproject.toml` - Python project config
- `.gitignore` - Git ignore rules
- `src/{package}/` - Source code
- `tests/` - Test suite

---

## NEVER

```
✗ Create unique folder structures per organism
✗ Put framework/ in daughter organisms
✗ Duplicate pipeline code (use adapters)
✗ Commit secrets to config/local/
✗ Put data in committed folders without .gitignore
```

## ALWAYS

```
✓ Use src/ layout for importable code
✓ Put pipeline configs in adapters/
✓ Reference genesis framework via federation
✓ Separate base/ and local/ config
✓ Follow THE_PATTERN: HOLD₁ → AGENT → HOLD₂
```

---

*Industry-standard structure, unique thinking. Compete at architecture, not scaffolding.*

— Enshrined 2026-01-26
