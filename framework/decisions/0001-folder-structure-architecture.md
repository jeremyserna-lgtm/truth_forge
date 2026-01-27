# ADR-0001: Folder Structure Architecture

**Status**: Accepted
**Date**: 2026-01-25
**Context**: Designing folder structure for Truth_Forge (molt from Truth_Engine)

---

## Context

Truth_Engine is molting into Truth_Forge. We need to establish canonical folder structure patterns that:
1. Reflect the authority hierarchy of different content types
2. Enable colocated documentation alongside code
3. Maintain centralized standards while allowing local compliance reports
4. Scale as the project grows

## Decision

### 1. Framework at Project Root (Not Inside `docs/`)

**Decision**: Keep `framework/` at the project root level, peer to `src/`, `docs/`, and `pipelines/`.

**Rationale**:
- The framework GOVERNS everything - it's not documentation ABOUT the project
- `framework/` contains normative content (what MUST be), not descriptive content (what IS)
- Hierarchy should reflect authority: framework governs code, not the other way around
- Immediate visibility signals importance

**Pattern**:
```
Truth_Forge/
├── framework/          # GOVERNS everything below
├── src/                # GOVERNED BY framework
├── pipelines/          # GOVERNED BY framework
└── docs/               # DESCRIBES framework and code
```

**Industry Support**:
- Kubernetes: `api/`, `pkg/`, `docs/` all at root
- Linux kernel: `Documentation/` at root, peer to `kernel/`

---

### 2. Core Framework Files at Root of `framework/` (No Nested `docs/`)

**Decision**: Keep numbered core files (00-08) at root of `framework/`, not in a subfolder.

**Rationale**:
- These files ARE the framework - they don't need a container
- Putting the constitution in a "documents about constitution" folder is a category error
- Immediate visibility when opening `framework/` folder
- Avoids unnecessary nesting: `framework/06_LAW.md` vs `framework/docs/06_LAW.md`

**Pattern**:
```
framework/
├── 00_GENESIS.md           # AXIOMATIC - what IS true
├── 01_IDENTITY.md
├── ...
├── 07_STANDARDS.md
├── standards/              # NORMATIVE - what MUST be done
├── insights/               # EXPLORATORY - what COULD be understood
├── decisions/              # ADRs - why we decided what we decided
└── archive/                # HISTORICAL - what WAS
```

**Category Distinction**:
| Location | Content Type | Nature |
|----------|--------------|--------|
| `framework/*.md` | Core framework | Axiomatic |
| `framework/standards/` | Enforceable rules | Normative |
| `framework/insights/` | Deep explorations | Exploratory |
| `framework/decisions/` | Architecture decisions | Historical record |
| `framework/archive/` | Deprecated content | Historical |

---

### 3. Centralized Standards + Colocated Compliance Reports

**Decision**: Standards live centrally in `framework/standards/`. Compliance reports live alongside the code they audit.

**Rationale**:
- Standards should have ONE canonical location (Single Source of Truth)
- Compliance reports need to be found with the code they describe
- Reports can drift if separated from code
- Developers find what they need where they expect it

**Pattern**:
```
Truth_Forge/
├── framework/
│   └── standards/                      # CENTRAL: Canonical standards
│       ├── INDEX.md                    # Registry
│       ├── STANDARD_*.md               # Meta-standards (L2)
│       ├── code_quality/               # Specific standards (L3)
│       ├── pipeline/
│       └── ...
│
└── pipelines/
    └── claude_code/
        ├── COMPLIANCE_INDEX.md         # Summary of all audits
        └── scripts/
            ├── stage_0/
            │   ├── claude_code_stage_0.py
            │   └── COMPLIANCE_REPORT.md    # COLOCATED: Audit for this stage
            └── stage_1/
                ├── claude_code_stage_1.py
                └── COMPLIANCE_REPORT.md    # COLOCATED: Audit for this stage
```

**Industry Support**:
- [Spotify Engineering](https://engineering.atspotify.com/2019/10/solving-documentation-for-monoliths-and-monorepos): "Documentation should be as close to the code as possible"
- [ADR Pattern](https://adr.github.io/): Keep ADRs close to the code they describe
- [Squarespace Docs-as-Code](https://engineering.squarespace.com/blog/2025/making-documentation-simpler-and-practical-our-docs-as-code-journey): Markdown files stored alongside source code

---

### 4. ADR (Architecture Decision Record) Pattern

**Decision**: Store architectural decisions in `framework/decisions/` using sequential numbering.

**Rationale**:
- Decisions need to be discoverable and permanent
- Future developers need to understand WHY decisions were made
- Prevents re-litigating settled decisions
- Creates institutional memory

**Naming Convention**:
```
NNNN-short-description.md

Examples:
0001-folder-structure-architecture.md
0002-logging-standard-structured-only.md
0003-identity-service-as-gate.md
```

**ADR Template**:
```markdown
# ADR-NNNN: Title

**Status**: Proposed | Accepted | Deprecated | Superseded
**Date**: YYYY-MM-DD
**Context**: Brief description of what prompted this decision

## Context
[Detailed description of the problem or situation]

## Decision
[What was decided and why]

## Consequences
[What are the implications of this decision]

## Alternatives Considered
[What other options were evaluated]
```

---

## Consequences

### Positive
- Clear authority hierarchy visible in folder structure
- Standards centralized, compliance distributed
- ADRs create permanent record of architectural thinking
- Pattern scales as project grows

### Negative
- More folders at root level (potential sprawl)
- Compliance reports could become stale if not maintained
- ADRs require discipline to maintain

### Neutral
- Existing references to `framework/` paths remain valid
- Migration from Truth_Engine requires updating compliance report locations

---

## Alternatives Considered

### Alternative 1: Framework inside `docs/`
**Rejected because**: Framework governs docs, not the other way around. Category error.

### Alternative 2: Core framework files in `framework/docs/`
**Rejected because**: These files ARE the framework, not documentation about it.

### Alternative 3: Compliance reports in central location
**Rejected because**: Reports drift when separated from code. Colocated pattern keeps them relevant.

---

## References

- [Spotify Engineering: Documentation for Monorepos](https://engineering.atspotify.com/2019/10/solving-documentation-for-monoliths-and-monorepos)
- [ADR GitHub: Architecture Decision Records](https://github.com/joelparkerhenderson/architecture-decision-record)
- [Squarespace: Docs-as-Code Journey](https://engineering.squarespace.com/blog/2025/making-documentation-simpler-and-practical-our-docs-as-code-journey)
- [MADR: Markdown ADR](https://adr.github.io/madr/)

---

*Decided: 2026-01-25*
*Applies to: Truth_Forge molt from Truth_Engine*
