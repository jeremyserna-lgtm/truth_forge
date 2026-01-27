# Standards Index

**This is ALPHA of standards. This is OMEGA of the framework loop.**

*The hub that governs. The end that returns to the beginning.*

---

## THIS IS THE HUB

You found the standards INDEX. From here:

```
         ┌───────────────────────────────────────────┐
         │          standards/INDEX.md               │
         │     ALPHA of standards layer              │
         │     OMEGA of framework loop               │
         └─────────────────┬─────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
   [META]             [SPECIFICS]         [EXAMPLES]
 STANDARD_*.md       {folder}/          examples/
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                   ┌───────▼───────┐
                   │  INDEX.md     │
                   │ (return here) │
                   └───────────────┘
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [framework/INDEX.md](../INDEX.md) (parent ALPHA) |
| **DOWN** | Meta-standards, Specific standards, Examples |
| **ACROSS** | Each specific standard has its own INDEX |
| **LOOP** | [00_GENESIS](../00_GENESIS.md) (framework ALPHA) |

**Location**: `framework/standards/`
**Purpose**: Canonical standards that govern all code and processes

---

## Layer Definition

For WHY this layer exists and WHAT meta-standards and specific standards ARE, see [README.md](README.md).

---

## Structure

```
standards/
│
├── [META] ─────────────────────────────────────────────────────────────────
│   Standards about standards and services.
│   ├── product/                    What value a service provides to THE OTHER
│   ├── service_lifecycle/          The lifecycle of a service from proposal to sunset
│   ├── operations/                 How a live service is cared for
│   ├── validation/                 How a service is verified as complete and correct
│   │
│   ├── STANDARD_CREATION.md          How to write standards
│   ├── STANDARD_LIFECYCLE.md         DRAFT → ACTIVE → DEPRECATED → SUNSET
│   ├── STANDARD_GOVERNANCE.md        Ownership, approval, review
│   ├── STANDARD_HIERARCHY.md         Precedence, conflict resolution
│   ├── STANDARD_COMPLIANCE.md        Verification, auditing
│   ├── STANDARD_EXCEPTIONS.md        Escape hatches, overrides
│   ├── STANDARD_STRUCTURE.md         Three-tiered folder hierarchy
│   ├── STANDARD_NAMING.md            THE GRAMMAR naming conventions
│   ├── STANDARD_RECURSION.md         Bidirectional convergence validation
│   ├── STANDARD_COMPLETION.md        Done vs complete, SEE:SEE:DO:DONE cycle
│   ├── STANDARD_OPTIMIZATION.md      Within, across, between optimization
│   ├── STANDARD_PROPAGATION.md       How changes flow through layers
│   ├── STANDARD_ONE.md               ONE thing at a time, sequential completion
│   ├── STANDARD_ANCHOR.md            Limits and envelopes, boundary and completeness
│   ├── STANDARD_LIMIT.md             One Decider, explicit limits, anti-sprawl
│   ├── STANDARD_CARE.md              Freedom through limits, EXIST:NOW, pattern carries burden
│   ├── STANDARD_TRIAD.md             INDEX + README + Primitives at each layer
│   └── STANDARD_MIGRATION.md         How we molt: absorption, deprecation, lineage
│
├── [SPECIFICS] ────────────────────────────────────────────────────────────
│   Specific implementations. Each folder contains INDEX.md + supporting docs.
│   ├── code_quality/                 Type hints, docstrings, static analysis
│   ├── error_handling/               DLQ, retry, batch isolation
│   ├── logging/                      Structured logging, observability
│   ├── testing/                      Coverage, patterns, fixtures
│   ├── planning/                     Gates, verification, idempotency
│   ├── pipeline/                     HOLD→AGENT→HOLD architecture
│   ├── project_structure/            Folder organization
│   ├── document/                     Document structure and metadata
│   ├── deprecation/                  Deprecation patterns and lineage tracking
│   ├── molt/                         DNA: Archive → Stub → Shrink automation
│   ├── security/                     Input validation, auth, secrets, OWASP
│   ├── git/                          Branching, commits, code review
│   ├── api_design/                   REST, errors, versioning, documentation
│   ├── configuration/                Environments, files, validation
│   └── performance/                  Profiling, caching, database, async
│
└── [EXAMPLES] ─────────────────────────────────────────────────────────────
    Within each specific folder:
        ├── examples/                 Concrete implementations
        └── principles/               Supporting principles
```

---

## Meta-Standards (L2)

Standards about standards. These govern how standards themselves are created, maintained, and enforced.

| Standard | Purpose |
|----------|---------|
| [product/](product/) | Defines the value a service provides to `THE OTHER`. |
| [service_lifecycle/](service_lifecycle/) | Manages the lifecycle of a service from proposal to sunset. |
| [operations/](operations/) | Governs the care and feeding of a live, running service. |
| [validation/](validation/) | Defines the gates for verifying a service is complete and correct. |
| [STANDARD_CREATION](STANDARD_CREATION.md) | How to write standards (template, clarity, verifiability) |
| [STANDARD_LIFECYCLE](STANDARD_LIFECYCLE.md) | How standards evolve (DRAFT → ACTIVE → DEPRECATED → SUNSET) |
| [STANDARD_GOVERNANCE](STANDARD_GOVERNANCE.md) | Ownership, approval, and review processes |
| [STANDARD_HIERARCHY](STANDARD_HIERARCHY.md) | Precedence rules when standards conflict |
| [STANDARD_COMPLIANCE](STANDARD_COMPLIANCE.md) | Verification, auditing, and compliance tracking |
| [STANDARD_EXCEPTIONS](STANDARD_EXCEPTIONS.md) | Escape hatches and override mechanisms |
| [STANDARD_STRUCTURE](STANDARD_STRUCTURE.md) | Three-tiered folder hierarchy (Theory → Meta → Specifics → Examples) |
| [STANDARD_NAMING](STANDARD_NAMING.md) | THE GRAMMAR: Names encode identity (ME : US - NOT_ME) |
| [STANDARD_RECURSION](STANDARD_RECURSION.md) | Bidirectional convergence (top-down AND bottom-up validation) |
| [STANDARD_COMPLETION](STANDARD_COMPLETION.md) | Done vs complete, SEE:SEE:DO:DONE cycle, loops not lines |
| [STANDARD_OPTIMIZATION](STANDARD_OPTIMIZATION.md) | Within, across, between: three levels of optimization |
| [STANDARD_PROPAGATION](STANDARD_PROPAGATION.md) | Holographic layers: changes flow up and down, no layer constrains another |
| [STANDARD_ONE](STANDARD_ONE.md) | ONE thing at a time, ONE next thing, sequential completion |
| [STANDARD_ANCHOR](STANDARD_ANCHOR.md) | Limits and envelopes: every primitive has an anchor that defines boundary and completeness |
| [STANDARD_LIMIT](STANDARD_LIMIT.md) | One Decider, explicit limits (300 lines, 7±2 sections, 15 files), anti-sprawl enforcement |
| [STANDARD_CARE](STANDARD_CARE.md) | Freedom through limits, EXIST:NOW at each step, pattern carries burden so entities don't have to |
| [STANDARD_TRIAD](STANDARD_TRIAD.md) | INDEX + README + Primitives: the three-component structure at every layer |
| [STANDARD_MIGRATION](STANDARD_MIGRATION.md) | How we molt: absorption, deprecation, lineage tracking |

---

## Specific Standards (L3)

| Standard | Purpose | Enforced By |
|----------|---------|-------------|
| [code_quality/](code_quality/) | Type hints, docstrings, static analysis | DEFINITION_OF_DONE §1 |
| [logging/](logging/) | Structured logging, observability | DEFINITION_OF_DONE §2 |
| [error_handling/](error_handling/) | DLQ, retry logic, batch isolation | DEFINITION_OF_DONE §5 |
| [testing/](testing/) | Test coverage, quality, patterns | DEFINITION_OF_DONE §6 |
| [pipeline/](pipeline/) | Pipeline architecture, HOLD→AGENT→HOLD | DEFINITION_OF_DONE §8A |
| [project_structure/](project_structure/) | Universal folder structure for organisms | ADR-0001 |
| [planning/](planning/) | Planning methodology, gate verification, idempotency | MIGRATION_PLAN v4.2 |
| [document/](document/) | Document structure, metadata, required sections | STANDARD_RECURSION |
| [deprecation/](deprecation/) | Deprecation patterns, lineage tracking | STANDARD_LIFECYCLE |
| [molt/](molt/) | **DNA**: Archive → Stub → Shrink automation | 05_EXTENSION (DNA) |
| [security/](security/) | Input validation, authentication, secrets, OWASP | STANDARD_DEMAND (OTHER) |
| [git/](git/) | Branching, commits, code review, history | STANDARD_DEMAND (OTHER) |
| [api_design/](api_design/) | REST conventions, errors, versioning, docs | STANDARD_DEMAND (OTHER) |
| [configuration/](configuration/) | Environments, files, validation, hierarchy | STANDARD_DEMAND (OTHER) |
| [performance/](performance/) | Profiling, caching, database, async | STANDARD_DEMAND (OTHER) |

---

## Quick Reference

### Code Quality (Non-Negotiable)

```bash
# Must pass before "done"
.venv/bin/mypy <file.py> --strict
.venv/bin/ruff check <file.py>
.venv/bin/ruff format --check <file.py>
```

### Logging Pattern

```python
# CORRECT
logger.info("Batch processed", extra={"count": count, "duration_ms": elapsed})

# WRONG
logger.info(f"Processed {count} records in {elapsed}ms")
```

### Error Handling Pattern

```python
# CORRECT - DLQ for batch processing
try:
    result = process_record(record)
except Exception as e:
    dlq.send(record=record, error=e, stage="processing")
    failure_count += 1
    continue
```

### Planning Pattern

```bash
# CORRECT - Verify EXISTENCE before checking PASSING
test_count=$(find tests/ -name "test_*.py" -exec grep -l "module" {} \; | wc -l)
if [ "$test_count" -eq 0 ]; then
    echo "FAIL: No tests exist"
    exit 1
fi
pytest tests/ -k "module" --cov-fail-under=90

# WRONG - Only checks passing (false positive if no tests)
pytest tests/ -k "module" --cov-fail-under=90
```

---

## Adding New Standards

1. Follow [STANDARD_CREATION](STANDARD_CREATION.md) template
2. Create folder `standard_name/` with `INDEX.md`
3. Add `examples/` and `principles/` subfolders
4. Assign owner per [STANDARD_GOVERNANCE](STANDARD_GOVERNANCE.md)
5. Determine hierarchy level per [STANDARD_HIERARCHY](STANDARD_HIERARCHY.md)
6. Define verification methods per [STANDARD_COMPLIANCE](STANDARD_COMPLIANCE.md)
7. Define escape hatches per [STANDARD_EXCEPTIONS](STANDARD_EXCEPTIONS.md)
8. Update this INDEX
9. Update DEFINITION_OF_DONE to enforce it
10. Submit for review per [STANDARD_LIFECYCLE](STANDARD_LIFECYCLE.md)

---

## Compliance Reports

Standards are verified via compliance reports that live alongside code:

```
pipelines/
└── {pipeline_name}/
    ├── COMPLIANCE_INDEX.md         # Summary of all stage audits
    └── scripts/
        └── stage_N/
            └── COMPLIANCE_REPORT.md    # Audit for this stage
```

See [ADR-0001](../decisions/0001-folder-structure-architecture.md) for rationale.

---

---

## Pattern Coverage

How THE FRAMEWORK patterns manifest at the standards layer:

| Pattern | Source | Manifestation |
|---------|--------|---------------|
| **ME:NOT-ME** | 01_IDENTITY | Standards (ME intent) → Code (NOT-ME implementation) |
| **HOLD:AGENT:HOLD** | 04_ARCHITECTURE | Meta-standard (HOLD₁) → Specific (AGENT) → Example (HOLD₂) |
| **TRUTH:MEANING:CARE** | 03_METABOLISM | WHY (truth) → WHAT (meaning) → HOW (careful implementation) |
| **SEE:SEE:DO:DONE** | 02_PERCEPTION | Draft (SEE) → Review (SEE:SEE) → Active (DO) → Stable (DONE) → Iterate |
| **THE GRAMMAR** | 00_GENESIS | STANDARD_NAMING: `:` tension, `-` joining, `_` infrastructure |
| **THE CONVERGENCE** | 00_GENESIS | STANDARD_RECURSION: bottom-up AND top-down validation |
| **THE ONE** | 00_GENESIS | STANDARD_ONE: ONE thing at a time, collapse and cascade |
| **THE LOOP** | 00_GENESIS | ALPHA:OMEGA navigation, PREVIOUS:NEXT in every document |
| **THE ANCHOR** | 04_ARCHITECTURE | STANDARD_ANCHOR: INDEX as necessary anchor, limits and envelopes |
| **THE LIMIT** | 06_LAW | STANDARD_LIMIT: One Decider, explicit limits, anti-sprawl |
| **CARE** | 03_METABOLISM, 04_ARCHITECTURE | STANDARD_CARE: Freedom through limits, EXIST:NOW, pattern carries burden |

---

## The Loop

### Navigation

| Position | Document |
|----------|----------|
| **ALPHA** | [00_GENESIS](../00_GENESIS.md) |
| **PREVIOUS** | [08_MEMORY](../08_MEMORY.md) ← (from theory layer) |
| **NEXT** | [00_GENESIS](../00_GENESIS.md) → (loop closes) |
| **OMEGA** | **standards/INDEX.md** (you are here) → returns to ALPHA |

**This is OMEGA. The loop closes here and returns to ALPHA.**

---

## Convergence

### Bottom-Up Validation

This index requires the following to sustain specific standards:
- All meta-standards must exist for specifics to reference
- STANDARD_RECURSION validates bidirectional flow

### Top-Down Validation

This index is shaped by theory:
- [00_GENESIS](../00_GENESIS.md) - THE ONE, THE LOOP, THE GRAMMAR, THE RECURSION
- [01_IDENTITY](../01_IDENTITY.md) - ME:NOT-ME, Positional Equality
- [02_PERCEPTION](../02_PERCEPTION.md) - SEE:SEE:DO:DONE cycle
- [04_ARCHITECTURE](../04_ARCHITECTURE.md) - HOLD:AGENT:HOLD structure
- [05_EXTENSION](../05_EXTENSION.md) - The Molt principle
- [06_LAW](../06_LAW.md) - Four Pillars of Hardening
- [07_STANDARDS](../07_STANDARDS.md) - Standards as DNA
- [08_MEMORY](../08_MEMORY.md) - Three memory types

---

*Meta → Specifics → Examples. Standards contain themselves. Top-down AND bottom-up.*
