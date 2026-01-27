# project locations — THE GENESIS

**one pattern, one place. know where things live.**

## universal structure (industry-standard)

per ADR-0001 and PROJECT_STRUCTURE.md:

```
truth_forge/
├── .agent/                   # agent knowledge center
├── .claude/                  # claude code config
│   ├── commands/             # slash commands
│   ├── rules/                # project-specific rules
│   └── skills/               # project-specific skills
├── .seed/                    # federation identity
│
├── src/                      # source code (src layout)
│   └── truth_forge/          # importable package
│       ├── services/
│       ├── models/
│       └── utils/
│
├── pipelines/                # HOLD→AGENT→HOLD processing
│   ├── core/                 # universal pipeline engine
│   │   └── stages/
│   └── adapters/             # project-specific configs
│       └── {project_name}/
│           ├── config.yaml
│           └── COMPLIANCE_REPORT.md    # colocated with code
│
├── apps/                     # deployable software
│   ├── web/
│   ├── cli/
│   └── api/
│
├── projects/                 # work items / initiatives
│   └── {project_name}/
│       ├── data/             # project-specific data
│       ├── docs/             # project documentation
│       └── README.md
│
├── config/                   # configuration files
│   ├── base/                 # shared config (committed)
│   └── local/                # personal/secrets (gitignored)
│
├── data/                     # data storage (mostly gitignored)
│   ├── local/
│   ├── staging/              # HOLD₁ (input)
│   └── output/               # HOLD₂ (output)
│
├── docs/                     # documentation (numbered subfolders)
│   ├── 01_core/              # core concepts
│   ├── 02_framework/         # framework explanations
│   ├── 03_business/          # business documents
│   ├── 04_technical/         # technical documentation
│   ├── 05_personal/          # personal context
│   ├── 06_research/          # research and analysis
│   ├── 07_governance/        # governance and compliance
│   └── archive/              # deprecated docs
│
├── tests/                    # test suite
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── scripts/                  # utility scripts
│
├── framework/                # ★ ONLY GENESIS HAS THIS
│   ├── 00_GENESIS.md         # axiomatic - what IS true
│   ├── 01_IDENTITY.md
│   ├── ...
│   ├── standards/            # normative - what MUST be done
│   │   ├── INDEX.md
│   │   ├── STANDARD_*.md     # meta-standards (L2)
│   │   ├── code_quality/     # specific standards (L3)
│   │   ├── error_handling/
│   │   ├── logging/
│   │   ├── testing/
│   │   ├── planning/
│   │   ├── pipeline/
│   │   └── project_structure/
│   ├── decisions/            # ADRs - why we decided
│   │   ├── INDEX.md
│   │   └── 0001-folder-structure-architecture.md
│   └── archive/              # deprecated framework docs
│
├── Truth_Engine/             # molt archive (genesis source)
│
├── CLAUDE.md
├── README.md
├── pyproject.toml
└── .gitignore
```

## key principles (from ADR-0001)

### 1. framework governs, not describes

```
framework/  ← GOVERNS everything below
src/        ← GOVERNED BY framework
pipelines/  ← GOVERNED BY framework
docs/       ← DESCRIBES framework and code
```

### 2. standards central, compliance colocated

- **standards** live in `framework/standards/` (one canonical source)
- **compliance reports** live alongside the code they audit

```
pipelines/
└── claude_code/
    ├── COMPLIANCE_INDEX.md         # summary of all audits
    └── scripts/
        └── stage_0/
            ├── main.py
            └── COMPLIANCE_REPORT.md    # colocated with code
```

### 3. docs use numbered subfolders

```
docs/
├── 01_core/
├── 02_framework/
├── 03_business/
├── 04_technical/
├── 05_personal/
├── 06_research/
├── 07_governance/
└── archive/
```

## children inherit from here

| child | inherits | does NOT have |
|-------|----------|---------------|
| credential_atlas | `~/truth_forge/framework/` | framework/ |
| primitive_engine | `~/truth_forge/framework/` | framework/ |

**daughters reference genesis via federation. they do NOT duplicate framework/.**
