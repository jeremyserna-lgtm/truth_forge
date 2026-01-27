# Universal Structure

**The canonical folder structure for all organisms in the Truth Forge colony.**

---

## The Rule

**Compete at architecture and theory, not code structure.**

All organisms use industry-standard folder structures. The differentiation is in THE FRAMEWORK, not in folder naming.

---

## Universal Structure

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
│   └── adapters/             # Project-specific configurations
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

## Required Files

Every organism MUST have:
- `CLAUDE.md` - Claude Code configuration
- `README.md` - Project overview
- `pyproject.toml` - Python project config
- `.gitignore` - Git ignore rules
- `src/{package}/` - Source code
- `tests/` - Test suite

---

## UP

[INDEX.md](INDEX.md)
